# AGENTS.md — agent operating context

## purpose
This file tells AI agents how to work in this codebase. It is NOT a tech
stack list. It defines constraints, danger zones, and verification steps.

## constraints
- Never modify files outside src/ without explicit approval
- Never add dependencies without checking if an existing one covers the need
- Never bypass TypeScript strict mode
- All database mutations go through the service layer, never direct SQL in routes
- Rate limits exist on all public endpoints — do not remove them
- Never disable ESLint rules inline without a comment explaining why
- Never introduce breaking changes to public API endpoints without versioning
- Never commit code with TODO/FIXME without creating a corresponding issue
- Never modify CI/CD pipeline files without explicit approval
- Never change database column types on tables with production data — add new columns instead
- All inter-service calls must have timeout and retry configuration
- Never store user-generated content unescaped — sanitize at the boundary
- Feature flags must wrap any incomplete or experimental functionality
- All new endpoints must have request validation (zod/joi) at the boundary

## danger zones
These areas break things if touched carelessly:
- `src/auth/` — session handling, token validation. Changes here affect every logged-in user.
- `src/db/migrations/` — never edit an existing migration. Create a new one.
- `src/payments/` — Stripe webhook handlers. Test with `stripe trigger` before deploying.
- `.env` / `.env.production` — secrets. Never commit. Never log.
- `src/middleware/` — request pipeline. A bug here breaks every endpoint. Always test the full chain.
- `package.json` / `pnpm-lock.yaml` — changing dependencies can break downstream builds. Run full test suite after.
- `src/db/schema.ts` (or `prisma/schema.prisma`) — schema changes trigger migrations. Always check backward compatibility.
- `next.config.js` / `vite.config.ts` — build configuration. A wrong setting can break production but pass in dev.
- `Dockerfile` / `docker-compose.yml` — container changes affect all environments. Test locally first.
- `src/jobs/` / `src/workers/` — background jobs run without user context. Failures are silent. Always add dead-letter handling.
- `src/email/templates/` — email rendering differs across clients. Test with Litmus or similar before deploying.

## verification steps
Before declaring any task complete:
1. `CI=true pnpm test` — all tests pass
2. `pnpm lint` — zero errors
3. `pnpm typecheck` — zero errors
4. If you touched auth: test login, logout, and protected route access
5. If you touched payments: run `stripe trigger checkout.session.completed`
6. If you touched the database: verify migration runs cleanly on empty DB
7. If you touched API routes: test with curl/httpie, check response shapes match types
8. If you touched background jobs: verify retry behavior and failure handling

## testing strategy
- **Unit tests:** All business logic in services/ and utils/. Mock external dependencies.
- **Integration tests:** API routes with a real test database. Use transactions for cleanup.
- **E2E tests:** Critical user flows (signup, purchase, core features). Run with Playwright.
- **Test data:** Use factories/fixtures, never hardcode IDs or emails that exist in production.
- **Coverage target:** New code must have ≥80% line coverage. Do not game coverage with trivial assertions.
- **When to skip tests:** Never. If something is "too simple to test," it is simple enough to test quickly.
- **Flaky tests:** Fix immediately or quarantine with `it.skip` + a linked issue. Never ignore.

## deployment checklist
Before merging to main / triggering a deploy:
1. [ ] All CI checks pass (tests, lint, typecheck, build)
2. [ ] Database migrations are backward-compatible (old code can still run during rollout)
3. [ ] Environment variables are set in the target environment (check .env.example)
4. [ ] Feature flags are configured for any incomplete functionality
5. [ ] No console.log or debug statements in production code
6. [ ] API changes are backward-compatible or versioned
7. [ ] If adding a new service dependency: verify it is available in the target environment
8. [ ] Performance: no new N+1 queries, no unbounded list fetches, pagination in place
9. [ ] Monitoring: new endpoints have health checks, errors are logged with context
10. [ ] Rollback plan: know how to revert if something goes wrong (revert commit, feature flag off)

## how to add a new feature
1. Write the test first
2. Implement to pass the test
3. Run full test suite
4. Check git diff — nothing unintended
5. If it touches multiple files, explain why in the commit message

## patterns to follow
- Error handling: throw typed errors from service layer, catch in route handler
- Validation: zod schemas at API boundary, trust internal code
- Logging: structured JSON via pino, never console.log in production
- Tests: co-located with source, AAA pattern (Arrange, Act, Assert)

## patterns to avoid
- God functions that do 5 things
- Shared mutable state between requests
- String concatenation for SQL (use parameterized queries)
- Catching errors silently (always log or rethrow)
- Adding "helper" abstractions for one-time operations
