# CLAUDE.md — project context

## what this project is
[One sentence: what does this app/service do and who uses it]

## tech stack
- Language: [e.g. TypeScript / Python 3.11]
- Framework: [e.g. Next.js 15 / FastAPI]
- Database: [e.g. PostgreSQL via Prisma]
- Testing: [e.g. Vitest + Playwright]
- Package manager: [e.g. pnpm]

## essential commands
```bash
# install
pnpm install

# dev server
pnpm dev

# run all tests (always use CI=true)
CI=true pnpm test

# lint + typecheck
pnpm lint && pnpm typecheck

# build
pnpm build
```

## architecture
[2-3 sentences. e.g. "API routes in src/api/, shared types in src/types/,
database layer in src/db/. Frontend in src/app/ using server components
by default."]

## coding conventions
- [e.g. Use named exports only, no default exports]
- [e.g. All async functions must handle errors explicitly]
- [e.g. Database queries go through the repository layer]
- [e.g. Co-locate tests with source files as *.test.ts]

## what NOT to do
- Do not make up dependencies — check package.json before importing
- Do not guess API signatures — read the source file or ask first
- Do not assume a function exists — grep for it or confirm
- Do not use `any` in TypeScript
- Do not regenerate entire files for a small change — use targeted edits
- Do not declare something done without running the tests
- Do not add polyfills or shims without checking if the runtime already supports it
- Do not create new utility files when a similar one already exists — search first
- Do not re-implement logic that already exists elsewhere in the codebase
- Do not modify generated files (prisma client, compiled output, lock files) by hand
- Do not introduce circular dependencies between modules
- Do not add environment variables without updating .env.example
- Do not write barrel files (index.ts re-exports) unless the project already uses them
- Do not change test fixtures or snapshots without understanding why they exist
- Do not ignore TypeScript errors with @ts-ignore — fix the actual type issue

## current session context
<!-- Update this section at the start of each session with what you're working on -->
- **Current task:** [e.g. "Adding user profile page with avatar upload"]
- **Branch:** [e.g. feature/user-profile]
- **Blocked on:** [e.g. "Waiting for design spec for mobile layout" or "None"]
- **Files in progress:** [list files currently being modified]
- **Key decisions made:** [any architecture/approach decisions made this session]

## known issues
<!-- Track bugs, tech debt, and gotchas that affect current work -->
- [e.g. "Auth session refresh has a race condition on slow connections — see #142"]
- [e.g. "CI flakes on Playwright tests ~5% of the time due to timeout on DB seed"]
- [e.g. "The search index is stale in dev mode — run `pnpm reindex` after schema changes"]

## MCP server configuration
<!-- Notes on any MCP (Model Context Protocol) servers this project uses or exposes -->
- **MCP servers used:** [e.g. filesystem, database, custom API tools]
- **Config location:** [e.g. `.claude/mcp.json` or `mcp-config.json`]
- **Available tools:** [list key tools exposed by MCP servers]
- **Auth/setup notes:** [e.g. "Requires DATABASE_URL set before starting MCP server"]
- **Testing MCP tools:** [e.g. "Use `claude mcp serve` to test locally"]

## before writing code
1. Verify the function/module you need actually exists in this codebase
2. Check for an existing pattern and follow it
3. If unsure about architecture, stop and ask — do not invent

## before finishing a task
1. Run `CI=true pnpm test` — all tests must pass
2. Run `pnpm lint` — zero errors
3. Check git diff — no unintended file changes
4. If you added behavior, add or update a test for it

## lessons learned
<!-- Claude appends here when mistakes are corrected -->
