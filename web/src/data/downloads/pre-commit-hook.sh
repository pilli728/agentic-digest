#!/bin/bash
# .claude/hooks/pre-commit — runs before every commit

set -e

echo "Running pre-commit checks..."

# Auto-detect package manager
if [ -f "pnpm-lock.yaml" ]; then
  PM="pnpm"
elif [ -f "package-lock.json" ]; then
  PM="npm"
elif [ -f "bun.lockb" ]; then
  PM="bun"
else
  PM="npm"  # fallback
fi

echo "  Using package manager: $PM"

# 1. Run tests
echo "-> Running tests..."
CI=true $PM test -- --passWithNoTests 2>/dev/null || {
  echo "FAIL: Tests failed. Fix them before committing."
  exit 1
}

# 2. Lint
echo "-> Running linter..."
$PM run lint 2>/dev/null || {
  echo "FAIL: Lint errors. Run '$PM run lint --fix' to auto-fix."
  exit 1
}

# 3. Type check
echo "-> Running type check..."
$PM run typecheck 2>/dev/null || {
  echo "FAIL: Type errors. Fix them before committing."
  exit 1
}

# 4. Check for secrets
echo "-> Scanning for secrets..."
SECRET_PATTERNS='sk_live_\|sk_test_\|AKIA[0-9A-Z]\{16\}\|ghp_[a-zA-Z0-9]\{36\}\|password\s*=\s*['\''"][^'\''"][^'\''"]'
if grep -rn "$SECRET_PATTERNS" --include="*.ts" --include="*.js" --include="*.py" --include="*.tsx" --include="*.jsx" --include="*.env.local" src/ 2>/dev/null; then
  echo "FAIL: Possible secret found in source code. Remove it."
  exit 1
fi

# Also check for private keys
if grep -rn "PRIVATE KEY-----" --include="*.ts" --include="*.js" --include="*.py" --include="*.pem" src/ 2>/dev/null; then
  echo "FAIL: Private key found in source code. Remove it."
  exit 1
fi

# 5. Check for console.log in production code
if grep -rn "console\.log" --include="*.ts" --include="*.js" --include="*.tsx" --include="*.jsx" src/ 2>/dev/null | grep -v "test\|spec\|__mocks__\|__tests__"; then
  echo "WARNING: console.log found in production code. Consider removing."
fi

# 6. Dependency audit
echo "-> Auditing dependencies..."
if command -v $PM &>/dev/null; then
  $PM audit --audit-level=high 2>/dev/null || {
    echo "WARNING: High-severity vulnerabilities found in dependencies. Run '$PM audit' for details."
    # Warning only — does not block commit. Promote to exit 1 for strict mode.
  }
fi

# 7. Bundle size check (if build script exists and size-limit is configured)
if [ -f ".size-limit.json" ] || grep -q "size-limit" package.json 2>/dev/null; then
  echo "-> Checking bundle size..."
  $PM run size 2>/dev/null || {
    echo "WARNING: Bundle size limit exceeded. Run '$PM run size' for details."
  }
fi

# 8. Migration safety check
echo "-> Checking migrations..."
# Detect if staged files include migrations
STAGED_MIGRATIONS=$(git diff --cached --name-only | grep -E "(migrations?/|\.sql$)" || true)
if [ -n "$STAGED_MIGRATIONS" ]; then
  echo "  Migration files detected in commit:"
  echo "$STAGED_MIGRATIONS"

  # Check for destructive operations
  for file in $STAGED_MIGRATIONS; do
    if [ -f "$file" ]; then
      if grep -iE "DROP TABLE|DROP COLUMN|TRUNCATE|DELETE FROM" "$file" 2>/dev/null; then
        echo "FAIL: Destructive migration detected in $file. Review carefully before committing."
        echo "  If intentional, use: git commit --no-verify"
        exit 1
      fi
    fi
  done
fi

# 9. Docker image scan (if Dockerfile is staged and trivy is available)
STAGED_DOCKER=$(git diff --cached --name-only | grep -i "dockerfile" || true)
if [ -n "$STAGED_DOCKER" ] && command -v trivy &>/dev/null; then
  echo "-> Scanning Docker image for vulnerabilities..."
  # Build a temporary image and scan it
  TEMP_TAG="pre-commit-scan:latest"
  if docker build -t "$TEMP_TAG" -f "$STAGED_DOCKER" . --quiet 2>/dev/null; then
    trivy image --severity HIGH,CRITICAL --exit-code 1 "$TEMP_TAG" 2>/dev/null || {
      echo "WARNING: Docker image has high/critical vulnerabilities. Run 'trivy image' for details."
    }
    docker rmi "$TEMP_TAG" --force 2>/dev/null || true
  fi
fi

echo "All checks passed."
