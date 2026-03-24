---
title: "The Production CLAUDE.md Template (Copy-Paste Ready)"
description: "The exact CLAUDE.md file structure used by top developers. Three tiers, negative constraints, lessons learned section. Just fill in your stack."
date: "2026-03-24"
tier: "founding"
category: "template"
---

# The Production CLAUDE.md Template

Copy everything below. Fill in the brackets. Drop it in your project root.

This template is built from analyzing what the best developers on Reddit are actually using in March 2026. Every section exists because skipping it causes real problems.

---

## The Template

```markdown
# CLAUDE.md — project context

## what this project is
[One sentence: what does this app/service do and who uses it]

## tech stack
- Language: [e.g. TypeScript / Python 3.11]
- Framework: [e.g. Next.js 14 / FastAPI]
- Database: [e.g. PostgreSQL via Prisma]
- Testing: [e.g. Vitest + Playwright]
- Package manager: [e.g. pnpm]

## essential commands
\`\`\`bash
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
\`\`\`

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
```

---

## Why Each Section Matters

### "what NOT to do" — This is the highest-leverage section

Negative constraints work 3x better than positive ones with LLMs. "Don't guess API signatures" prevents more bugs than "be accurate."

### "before finishing a task" — The verification wall

Without this, Claude will say "done" when the code compiles. Compiling isn't done. Passing tests is done.

### "lessons learned" — Persistent memory

Leave this blank. When Claude makes a mistake and you correct it, tell it: "Add this to the lessons learned section." Next session, it reads this first. Same mistake doesn't happen twice.

### Keep it under 15 lines per section

Every extra line dilutes the important stuff. If your CLAUDE.md is 200 lines, Claude treats none of it as important.

---

## The Three-Tier Setup

### Tier 1: Global (`~/.claude/CLAUDE.md`)

```markdown
# Global rules
- Always run tests before declaring a task done
- Never commit without checking git diff
- When unsure, say "I don't know" instead of guessing
- A careful question beats a confident wrong answer
```

### Tier 2: Project (`./CLAUDE.md`)

The template above. Committed to git. Shared with your team.

### Tier 3: Local (`./CLAUDE.local.md`)

```markdown
# My local setup (not committed)
- Using iTerm2 with zsh
- MCP servers: Context7, GitHub, PostgreSQL
- Editor: Cursor + Claude Code in parallel
- Preferred test runner: vitest --watch
```

---

## Scoped CLAUDE.md Files

For large projects, add context files in subdirectories:

```
project/
├── CLAUDE.md              # Project-level
├── src/
│   ├── api/
│   │   └── CLAUDE.md      # "All routes return JSON. Use zod for validation."
│   ├── db/
│   │   └── CLAUDE.md      # "Never raw SQL. Use Prisma client. Migrations in prisma/migrations/"
│   └── auth/
│       └── CLAUDE.md      # "JWT tokens. Refresh flow in auth/refresh.ts. Never store tokens in localStorage."
```

Claude only loads the relevant scoped file when working in that directory. Zero wasted context.

---

## The Skills Directory

```
.claude/skills/
├── code-review/
│   └── SKILL.md           # "Review for security, performance, and readability. Flag any direct DB queries outside repository layer."
├── refactor/
│   └── SKILL.md           # "Preserve all existing tests. Run full suite after each change. Never change public API signatures."
├── test-writer/
│   └── SKILL.md           # "Write tests for edge cases first. Use AAA pattern. Mock external services only."
└── release/
    └── SKILL.md           # "Bump version, update CHANGELOG, run full CI, create git tag."
```

---

## Fill-In Checklist

Before your first session with this template:

- [ ] Fill in "what this project is" (one sentence only)
- [ ] List your actual tech stack
- [ ] Paste your real commands (not generic ones)
- [ ] Write 2-3 sentences about your architecture
- [ ] Add 3-5 project-specific coding conventions
- [ ] Customize "what NOT to do" for your stack's common mistakes
- [ ] Tell Claude: "Read CLAUDE.md and confirm you understand the project before we start"

That last step is critical. It forces Claude to actually load the context instead of charging ahead.
