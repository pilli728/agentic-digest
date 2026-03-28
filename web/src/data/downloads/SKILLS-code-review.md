# .claude/skills/code-review/SKILL.md

## what this skill does
Review code changes for security, performance, readability, and correctness.

## how to approach
1. Read the full diff first — understand the intent before critiquing
2. Check for security issues: SQL injection, XSS, auth bypass, secret leaks
3. Check for performance: N+1 queries, unnecessary re-renders, missing indexes
4. Check for correctness: edge cases, error handling, race conditions
5. Check for readability: naming, function length, dead code
6. Check for dependency changes: audit new packages for necessity, size, and maintenance status
7. Check for accessibility: semantic HTML, ARIA attributes, keyboard navigation, color contrast
8. Check for performance regressions: bundle size impact, unnecessary data fetching, missing memoization

## severity definitions
- **Critical:** Must fix before merge. Security vulnerabilities, data loss risk, broken functionality, auth bypass.
- **Warning:** Should fix before merge. Performance regressions, missing error handling, poor patterns that will cause problems later.
- **Nit:** Nice to fix but not blocking. Naming suggestions, minor readability improvements, optional optimizations.

## what to flag
- Any direct database query outside the repository/service layer
- Any `any` type in TypeScript
- Any error swallowed silently (empty catch blocks)
- Any hardcoded secret, URL, or credential
- Any file over 300 lines (suggest splitting)
- Any function over 50 lines (suggest extracting)
- Any test that doesn't assert anything meaningful
- Any new dependency without justification (check if existing deps cover the need)
- Any dependency with <500 weekly downloads or no updates in 12+ months
- Any missing `loading` or `error` state handling in UI components
- Any image without `alt` text or interactive element without accessible label
- Any unbounded list query (missing LIMIT/pagination)
- Any new API endpoint without input validation
- Any async operation without timeout or cancellation handling

## reviewing AI-generated code
AI-generated code has specific failure patterns. Pay extra attention to:
- **Hallucinated imports:** Verify every import path and package name actually exists in the project
- **Plausible but wrong logic:** AI code often looks correct but handles edge cases incorrectly — trace through manually
- **Over-engineering:** AI tends to add unnecessary abstractions. Question whether each layer is needed.
- **Stale patterns:** AI may use deprecated APIs or outdated patterns. Check against current docs.
- **Missing error paths:** AI often handles the happy path well but skips error handling. Check every external call.
- **Copy-paste drift:** If AI generated similar code in multiple places, check for inconsistencies between them.
- **Test quality:** AI-generated tests often test the implementation rather than behavior. Ensure tests would catch regressions.
- **Security blind spots:** AI may not consider auth context, rate limiting, or input sanitization unless explicitly prompted.

## what NOT to flag
- Style preferences (formatting is handled by prettier/eslint)
- Minor naming disagreements
- "I would have done it differently" without a concrete reason
- TODOs that are tracked in issues

## output format
For each issue:
- **File:line** — what's wrong
- **Severity** — critical / warning / nit
- **Fix** — what to do instead (be specific)
