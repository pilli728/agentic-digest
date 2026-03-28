# .claude/skills/security-audit/SKILL.md

## what this skill does
Audit code for OWASP Top 10 vulnerabilities, supply chain risks, and common security mistakes.

## OWASP Top 10 checklist
1. **Broken Access Control** — missing auth checks on endpoints, IDOR, privilege escalation, CORS misconfiguration, forced browsing to authenticated pages
2. **Cryptographic Failures** — weak algorithms, hardcoded keys, cleartext storage/transmission, missing TLS, weak hashing for passwords (use bcrypt/argon2)
3. **Injection** — SQL, NoSQL, OS command, LDAP, ORM injection. Check every user input path. Includes template injection (SSTI) and header injection.
4. **Insecure Design** — missing rate limiting, no abuse case considerations, business logic flaws, missing trust boundaries
5. **Security Misconfiguration** — debug mode on, default creds, open CORS, overly permissive permissions, unnecessary features enabled, missing security headers
6. **Vulnerable and Outdated Components** — check package versions against CVE databases, unmaintained dependencies, known-vulnerable versions
7. **Identification and Authentication Failures** — session fixation, weak passwords, missing 2FA, credential stuffing exposure, session ID in URL
8. **Software and Data Integrity Failures** — insecure CI/CD pipeline, unsigned updates, untrusted deserialization, missing integrity checks on packages
9. **Security Logging and Monitoring Failures** — auth failures not logged, no audit trail, logs missing context, no alerting on suspicious activity
10. **Server-Side Request Forgery (SSRF)** — user-controlled URLs fetched server-side, missing URL allowlists, internal network access via redirect

## API security checks
- All endpoints require authentication unless explicitly public
- Authorization checked at the resource level, not just the route level
- Rate limiting on all endpoints (stricter on auth endpoints)
- Request body size limits configured
- API keys are scoped (read/write/admin) and rotatable
- CORS is configured with specific origins, never wildcard in production
- Response headers include: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`
- GraphQL: depth limiting, query complexity analysis, introspection disabled in production
- Webhook endpoints validate signatures before processing

## supply chain attack detection
- Check for typosquatted package names (e.g. `lodash` vs `1odash`)
- Audit `postinstall` scripts in dependencies — they run arbitrary code
- Pin dependency versions or use lockfiles (package-lock.json, pnpm-lock.yaml)
- Check for dependency confusion: internal package names that could shadow public ones
- Review any new dependency: who maintains it, how many downloads, when was last update
- Use `npm audit` / `pnpm audit` / `pip audit` to check for known vulnerabilities
- Verify integrity hashes in lockfiles are not tampered with
- Watch for unexplained new dependencies in pull requests

## container security
- Base images pinned to specific SHA digests, not just tags
- Run as non-root user (USER directive in Dockerfile)
- No secrets baked into images (check build args, ENV, COPY)
- Multi-stage builds to minimize attack surface in production image
- Health check endpoints do not expose internal state
- Read-only filesystem where possible
- Network policies restrict inter-container communication to what is needed

## secrets scanning patterns
Scan for these patterns in code, configs, and git history:
- AWS: `AKIA[0-9A-Z]{16}`, `aws_secret_access_key`
- Stripe: `sk_live_`, `sk_test_`, `rk_live_`, `whsec_`
- GitHub: `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`
- Generic API keys: `api[_-]?key`, `api[_-]?secret`, `bearer [a-zA-Z0-9]{20,}`
- Database: connection strings with passwords, `DATABASE_URL` with credentials inline
- JWT: `eyJ` (base64 encoded JSON — may be a hardcoded token)
- Private keys: `-----BEGIN (RSA |EC )?PRIVATE KEY-----`
- Passwords: `password\s*=\s*['"][^'"]+['"]` (not empty or placeholder)
Check: source code, config files, CI/CD configs, Docker files, git history (`git log -p`)

## for each finding
- **Location** — exact file and line
- **Risk** — critical / high / medium / low
- **Attack scenario** — how an attacker would exploit this
- **Fix** — specific code change needed
- **Verification** — how to confirm the fix works

## what to check first
- All API endpoints: are they auth-protected?
- All user inputs: are they validated and sanitized?
- All secrets: are they in .env, not in code?
- All SQL: parameterized queries, not string concatenation?
- All renders: escaped output, no raw HTML injection?
- All dependencies: any known CVEs? Any suspicious packages?
- All containers: running as non-root? No secrets in image?
