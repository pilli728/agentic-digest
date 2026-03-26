---
title: "AGENTS.md Masterclass: Why the Tech Stack Mini-Map Approach Fails"
description: "Most AGENTS.md files are useless. Here's the structure that actually makes AI agents productive in your codebase."
date: "2026-03-26"
tier: "founding"
category: "guide"
---

Your AGENTS.md is probably bad. Not because you're lazy — because nobody taught you what it's actually for.

## What AGENTS.md Is

It's a file in your repo root that gives AI coding agents context about your project. Claude Code reads it. Cursor reads it. Windsurf reads it. When an agent opens your project, this file tells it how to behave.

Think of it as onboarding docs — but for robots.

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

## Good vs Bad: Side by Side

**Bad:** "We use Tailwind for styling."

**Good:** "Use Tailwind utility classes. Never use `@apply` in component files — it breaks our CSS extraction. Custom colors are in `tailwind.config.ts` under `theme.extend.colors`. If you need a new color, add it there — don't use arbitrary values like `bg-[#ff0000]`."

**Bad:** "PostgreSQL database."

**Good:** "All database queries go through Drizzle ORM in `/lib/db/`. Never write raw SQL outside of migration files. The connection pool max is 10 — don't create new connections in request handlers."

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

Keep it under 500 lines. Agents lose focus on long context. Trim ruthlessly.
