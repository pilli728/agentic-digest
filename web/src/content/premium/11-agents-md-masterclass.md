---
title: "AGENTS.md Masterclass: Why the Tech Stack Mini-Map Approach Fails"
description: "Most AGENTS.md files are useless. Here's the structure that actually makes AI agents productive in your codebase."
date: "2026-03-26"
tier: "founding"
category: "guide"
---

Your AGENTS.md is probably bad. Not because you're lazy. Because nobody taught you what it's actually for.

## What AGENTS.md Is

It's a file in your repo root that gives AI coding agents context about your project. Claude Code reads it. Cursor reads it. Codex reads it. Windsurf reads it. When an agent opens your project, this file tells it how to behave.

Think of it as onboarding docs for robots.

AGENTS.md started as an OpenAI Codex convention. It's now an open format under the Linux Foundation with adoption across 60,000+ open-source projects. It's the closest thing we have to a universal standard for AI agent configuration.

## AGENTS.md vs CLAUDE.md: When to Use Which

This confuses everyone. Here's the simple version.

**AGENTS.md** is the universal file. It works with Claude Code, Cursor, Codex, Amp, and basically every AI coding tool. If your team uses multiple tools, or if you're open-sourcing your project, use AGENTS.md.

**CLAUDE.md** is Claude Code's native config file. It supports Claude-specific features like the memory hierarchy and modular rules in `.claude/rules/`. Claude Code reads AGENTS.md as a fallback if no CLAUDE.md exists.

**My recommendation:** Use AGENTS.md as your single source of truth. If you need Claude-specific config (like rules for specific subdirectories), add a CLAUDE.md that imports or extends your AGENTS.md content. Don't maintain two separate files with overlapping information. That's a sync nightmare.

If your whole team is on Claude Code and nothing else, just use CLAUDE.md. But the moment someone opens your repo in Cursor, they get nothing.

## The Tech Stack Mini-Map Anti-Pattern

Here's what 90% of AGENTS.md files look like:

```markdown
## Tech Stack
- Frontend: React 19 + TypeScript
- Backend: FastAPI
- Database: PostgreSQL
- Hosting: Vercel + Railway
```

This is useless. The agent can figure out your tech stack by reading `package.json` and your import statements. You're burning context tokens on information the model already has.

The mini-map approach fails because it tells the agent WHAT you're using without explaining HOW you use it or WHAT TO AVOID.

## The Structure That Works

Four sections. In this order. Order matters because agents sometimes lose context at the end of long files.

### 1. Constraints (What NOT to do)

Put this first. Violations here cause the most damage.

```markdown
## Constraints
- NEVER modify migration files after they've been committed
- NEVER use `any` type in TypeScript — use `unknown` and narrow
- NEVER commit directly to main — always branch
- Do NOT add dependencies without checking the bundle size impact
```

Agents follow negative instructions better than positive ones. "Never use X" is clearer than "Prefer Y over X."

### 2. Conventions (How we do things here)

```markdown
## Conventions
- All API routes return `{ data, error, meta }` envelope
- Error messages are user-facing — write them in plain English
- Component files: PascalCase. Utility files: camelCase
- Tests live next to the file they test: `Button.tsx` → `Button.test.tsx`
```

Be specific. "Follow best practices" means nothing. "Components use named exports, not default exports" means something.

### 3. Danger Zones (Where things break)

```markdown
## Danger Zones
- `/lib/auth/` — session handling is stateful, don't refactor without understanding the token refresh flow
- `/api/webhooks/stripe.ts` — this processes real payments, test ONLY with Stripe test keys
- The `user_preferences` table has a trigger — INSERTs cascade to three other tables
```

This is the highest-value section. It prevents the agent from confidently breaking your production system.

### 4. Verification Steps (How to check your work)

```markdown
## Verification
- Run `npm run typecheck` before committing — CI will reject type errors
- Run `npm test -- --related` to test only affected files
- Check `npm run build` passes — tree-shaking can break with certain import patterns
```

Give the agent a checklist. Otherwise it'll make changes, declare success, and leave you with a broken build.

## Danger Zones by Stack

The danger zones section is where most people write too little. Here are starter templates for common stacks.

### Next.js App Router

```markdown
## Danger Zones
- `/app/layout.tsx` — root layout wraps every page. Changes here affect the entire site. Test thoroughly.
- `/middleware.ts` — runs on EVERY request. A bug here takes down all routes, not just one.
- Any file with `"use server"` — these are server actions. They accept user input and run on the server. Treat them like API endpoints. Validate everything.
- `/app/api/` — API routes share the Node runtime with server components. Memory leaks here affect page renders.
- `next.config.js` — rewrites and redirects are order-dependent. Adding a new rewrite can shadow existing routes.
- NEVER put secrets in files that start with `"use client"`. They'll ship to the browser.
```

### Django

```markdown
## Danger Zones
- `*/migrations/` — NEVER edit a migration after it's been applied. Create a new one.
- `settings.py` — MIDDLEWARE order matters. Auth middleware must come before permission checks.
- `*/signals.py` — signals fire on every save/delete. A slow signal blocks the request. Check for N+1 queries.
- `*/admin.py` — admin list_display with foreign keys causes N+1. Always use list_select_related.
- Any model with `on_delete=CASCADE` — deleting a parent nukes all children. Trace the cascade before modifying.
- `celery_tasks/` — tasks run outside the request cycle. Database connections can be stale. Always use `.using('default')`.
```

### Rails

```markdown
## Danger Zones
- `db/schema.rb` — auto-generated. NEVER edit directly. Changes come from migrations only.
- `config/routes.rb` — route order matters. First match wins. New routes can shadow existing ones.
- `app/models/concerns/` — mixins affect every model that includes them. Test all including models.
- Any model with `has_many dependent: :destroy` — same cascade danger as Django. Trace it.
- `config/initializers/` — runs once at boot. Errors here prevent the app from starting entirely.
- `app/jobs/` — background jobs retry by default. Make them idempotent or you'll process payments twice.
```

### Go

```markdown
## Danger Zones
- Any function launching goroutines — check for goroutine leaks. Every goroutine needs a cancellation path.
- `internal/` — this directory enforces import boundaries. Moving things out of internal/ changes your public API.
- Files using `sync.Mutex` — deadlocks are silent. Never hold two locks at once. Document lock ordering.
- `*_test.go` files with `TestMain` — these override the test runner for the entire package. Changes affect all tests.
- CGO files — cross-compilation breaks. If you add CGO, document the build dependencies.
- Any handler touching `http.ResponseWriter` — writing headers after body panics. Check Write/WriteHeader order.
```

## Real-World AGENTS.md Examples

### Example 1: SaaS API (Node.js + Postgres)

```markdown
# AGENTS.md

## Constraints
- NEVER modify files in `/prisma/migrations/` after they've been committed
- NEVER use `console.log` in production code — use the logger from `/lib/logger.ts`
- NEVER store secrets in code — all secrets come from environment variables
- Do NOT add new npm dependencies without approval — check bundle size with `npx bundlephobia <package>`
- All database queries must go through Prisma — no raw SQL outside migrations

## Conventions
- API responses: `{ data: T, error: string | null, meta: { page, total } }`
- Route handlers in `/api/v1/` — versioned, always
- Zod schemas validate all input — schema lives next to the route file
- Error codes: 4xx for client errors with actionable messages, 5xx logged to Sentry
- Feature flags in `/lib/flags.ts` — check before shipping incomplete features

## Danger Zones
- `/lib/billing/` — Stripe integration. Uses webhooks for state changes. Dual-write to our DB and Stripe. Test ONLY with `sk_test_` keys.
- `/lib/auth/middleware.ts` — JWT verification + session refresh. The refresh token rotation is stateful. Don't refactor without reading the flow diagram in Notion.
- `/prisma/schema.prisma` — the User model has 12 relations. Changing it cascades everywhere. Run `prisma db push --dry-run` first.
- `/workers/` — background jobs run on a separate process. They don't have access to request context.

## Verification
- `npm run typecheck` — zero errors required
- `npm run test:unit` — must pass
- `npm run lint` — auto-fixable issues get fixed, non-fixable block merge
- `npm run build` — SSR build must succeed. Import ordering matters for tree-shaking.
```

### Example 2: Python ML Pipeline

```markdown
# AGENTS.md

## Constraints
- NEVER commit model weights or large data files — use DVC or git-lfs
- NEVER use `pip install` directly — add to `pyproject.toml` and run `uv sync`
- NEVER modify the training config schema without updating the validation tests
- All experiments must be logged to MLflow — no silent runs

## Conventions
- Config files: YAML in `/configs/`. One per experiment. Never hardcode hyperparameters.
- Data loading: all datasets go through `/src/data/loaders.py`. No pandas in model code.
- Type hints required on all function signatures. Use `beartype` for runtime validation.
- Naming: `snake_case` everywhere. Model classes: `PascalCase`. Constants: `UPPER_SNAKE`.

## Danger Zones
- `/src/training/distributed.py` — multi-GPU training setup. Incorrect rank handling corrupts checkpoints.
- `/configs/production.yaml` — this config runs the deployed model. Changes here affect live inference.
- `/src/data/transforms.py` — preprocessing must match between training and inference. A mismatch here causes silent accuracy degradation.
- Any file importing `torch.cuda` — GPU memory management is manual. Always free tensors in finally blocks.

## Verification
- `uv run pytest tests/ -x` — stop on first failure
- `uv run mypy src/` — type checking must pass
- `uv run ruff check .` — linting
- For model changes: run the smoke test suite with `uv run pytest tests/smoke/ --timeout=60`
```

### Example 3: Mobile App (React Native)

```markdown
# AGENTS.md

## Constraints
- NEVER use inline styles — all styles go through the design system in `/theme/`
- NEVER import from `react-native` directly for UI components — use the wrapped versions in `/components/ui/`
- NEVER add native modules without testing on both iOS and Android simulators
- Platform-specific code MUST use `.ios.tsx` / `.android.tsx` suffixes, not runtime checks

## Conventions
- Navigation: React Navigation v7. All routes defined in `/navigation/types.ts`
- State: Zustand stores in `/stores/`. One store per domain (auth, cart, user, etc.)
- API: all network calls go through `/api/client.ts` which handles auth headers and retry
- Animations: Reanimated 4. No Animated API from react-native.

## Danger Zones
- `/ios/Podfile` and `/android/build.gradle` — native dependency changes require full rebuild and testing on physical devices
- `/stores/auth.ts` — token refresh, biometric unlock, and session persistence all live here. It's complex. Read the whole file before modifying.
- `/api/client.ts` — retry logic + offline queue. A bug here silently drops user actions.

## Verification
- `npx tsc --noEmit` — type check
- `npx jest --bail` — unit tests
- `npx detox test -c ios.sim.release` — E2E on iOS
- `npx detox test -c android.emu.release` — E2E on Android
```

## Multi-Repo AGENTS.md Strategies

If your system spans multiple repos (frontend, backend, shared libs, infra), you need a strategy.

**Option 1: Shared core, repo-specific extensions.** Create a shared `AGENTS-CORE.md` in a central repo or wiki. Each repo's AGENTS.md starts with a link to the core doc and adds repo-specific sections. The agent won't fetch the link, but your developers will keep things in sync.

**Option 2: Monorepo with directory-level files.** If you're in a monorepo, put AGENTS.md at the root with universal rules. Then add AGENTS.md files in subdirectories for package-specific context. Most AI tools pick up the nearest AGENTS.md and merge it with parents.

```
/AGENTS.md              ← universal constraints
/packages/api/AGENTS.md ← API-specific conventions
/packages/web/AGENTS.md ← frontend-specific conventions
/packages/shared/AGENTS.md ← shared lib rules
```

**Option 3: Cross-repo references.** When repos depend on each other, document the contract in both AGENTS.md files. If the API repo exposes an endpoint the frontend consumes, both repos should describe the contract shape and validation rules.

```markdown
## Cross-Repo Dependencies
- This API serves the `web-app` frontend repo
- API contract types are published to `@company/api-types` — run `npm run generate:types` after changing any endpoint
- Breaking changes require a version bump in the URL: `/api/v2/...`
```

The goal: an agent working in any single repo has enough context to avoid breaking the other repos it touches.

## Testing That Your AGENTS.md Actually Works

Writing an AGENTS.md is step one. Knowing it works is step two. Most people skip step two.

**The new-session test.** Start a fresh Claude Code session (or whatever tool you use). Give it a task that touches a danger zone or convention you documented. Don't mention the convention in your prompt. See if the agent follows it anyway. If it doesn't, your instructions aren't clear enough.

**The violation test.** Ask the agent to do something your AGENTS.md explicitly prohibits. "Add a console.log statement for debugging." If your constraints section says "NEVER use console.log," the agent should push back or use the logger instead. If it blindly follows your request, your constraints aren't strong enough. Use CAPS. Use "NEVER." Use "CRITICAL."

**The checklist test.** Ask the agent to make a change and submit it. See if it runs your verification steps. If not, make the verification section more prominent. Move it higher in the file if needed.

**The context-length test.** If your AGENTS.md is over 300 lines, the agent will lose track of later sections. Trim it. Move detailed docs to linked files and keep AGENTS.md as the index. Frontier models can reliably follow about 150 instructions. Claude Code's system prompt uses ~50 of those. So you have room for about 100 instructions before things get fuzzy.

**The diff review.** After each AI-assisted PR, check: did the agent follow my AGENTS.md? Keep a tally. If compliance drops below 90%, your file needs rewriting, not expanding. Clarity beats completeness.

## Good vs Bad: Side by Side

**Bad:** "We use Tailwind for styling."

**Good:** "Use Tailwind utility classes. Never use `@apply` in component files. It breaks our CSS extraction. Custom colors are in `tailwind.config.ts` under `theme.extend.colors`. If you need a new color, add it there. Don't use arbitrary values like `bg-[#ff0000]`."

**Bad:** "PostgreSQL database."

**Good:** "All database queries go through Drizzle ORM in `/lib/db/`. Never write raw SQL outside of migration files. The connection pool max is 10. Don't create new connections in request handlers."

**Bad:** "Follow our coding standards."

**Good:** "Functions over 30 lines get split. No exceptions. If you're writing a function and it crosses 30 lines, extract a helper. Name the helper after what it does, not what it returns."

## The Template

Here's the bare minimum you should have:

```markdown
# AGENTS.md

## Constraints
- [3-5 hard rules that prevent damage]

## Conventions
- [5-10 patterns specific to YOUR codebase]

## Danger Zones
- [List files/directories that require extra caution]

## Verification
- [Commands to run before considering a task complete]
```

Fill in each section with things a new hire would need to know on day one. That's the bar. If a competent developer joining your team would need to know it, put it in.

Keep it under 300 lines. Agents lose focus on long context. Trim ruthlessly. Link to external docs for details.
