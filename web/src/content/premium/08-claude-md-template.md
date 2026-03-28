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
- Do not use placeholder comments — write the full implementation or say you can't

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

Every extra line dilutes the important stuff. If your CLAUDE.md is 200 lines, Claude treats none of it as important. Move detailed documentation to a `docs/` folder where Claude can read it on demand.

---

## The Three-Tier Setup

### Tier 1: Global (`~/.claude/CLAUDE.md`)

```markdown
# Global rules
- Always run tests before declaring a task done
- Never commit without checking git diff
- When unsure, say "I don't know" instead of guessing
- A careful question beats a confident wrong answer
- Never use placeholder comments — write the real implementation
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

## The Memory System (`~/.claude/projects/`)

Claude has an auto-memory system that most people don't know about. Here's how it works.

When you see "Writing memory" in the Claude Code interface, Claude is saving notes to `~/.claude/projects/<project-hash>/memory/`. It stores things it learned during the session: build commands that worked, debugging insights, architecture patterns, your preferences.

**How to use it:**
- Run `/memory` inside a session to browse all loaded memory files
- Toggle auto memory on/off from the `/memory` menu
- Claude reads these files at the start of every session automatically

**Auto Dream** is the newer feature. Claude periodically reviews its memory files, prunes stale info, resolves contradictions, and reorganizes everything into clean indexed topic files. Think of it as Claude defragging its own brain.

**What to know:**
- Auto memory requires Claude Code v2.1.59+
- It's on by default. You don't need to configure anything.
- Memory files are per-project, stored by project path hash
- You can manually edit these files. They're just markdown.
- CLAUDE.md files are instructions you write. Memory files are notes Claude writes for itself. Both get loaded at session start.

**The practical distinction:** CLAUDE.md is your playbook. Memory files are Claude's notebook. Don't try to merge them. Let each do its job.

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

## The settings.json Configuration

Your `.claude/settings.json` controls hooks, permissions, and MCP servers. Here's a production-ready example:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $CLAUDE_FILE_PATH"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "CI=true npm test 2>&1 | tail -20"
          }
        ]
      }
    ]
  }
}
```

**Where settings files live:**
- `~/.claude/settings.json` — Global (your personal defaults)
- `.claude/settings.json` — Project (committed, shared with team)
- `.claude/settings.local.json` — Local project (not committed, your overrides)

**Common hooks people actually use:**
- Auto-format after every file edit (PostToolUse with prettier/black)
- Block dangerous bash commands (PreToolUse with exit code 2)
- Run tests automatically when Claude says it's done (Stop)
- Notify Slack when a long task completes (Stop with HTTP hook)

---

## CLAUDE.md vs AGENTS.md

This question comes up constantly. Here's the clear answer.

**CLAUDE.md** is Anthropic's format. Claude Code reads it natively. It supports the three-tier hierarchy (global, project, local), scoped subdirectory files, and the lessons learned pattern. If you use Claude Code, this is your primary file.

**AGENTS.md** is an open standard backed by the Linux Foundation. Most AI coding tools read it: Cursor, Windsurf, Copilot, and others. It's becoming the README.md of AI configuration. One file, many tools.

**When to use each:**

| Scenario | Use |
|---|---|
| Solo dev, Claude Code only | CLAUDE.md |
| Team uses mixed tools | AGENTS.md + CLAUDE.md |
| Open source project | AGENTS.md (widest compatibility) |
| Claude-specific hooks/skills | CLAUDE.md (AGENTS.md can't do these) |

**The practical setup for teams:** Put shared context in AGENTS.md. Put Claude-specific stuff (hooks, skills, the "what NOT to do" section) in CLAUDE.md. Some teams symlink AGENTS.md to CLAUDE.md so they maintain one source of truth for the basics.

The bottom line: AGENTS.md is for portability across tools. CLAUDE.md is for Claude-specific power features. They complement each other.

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

## Real-World Examples (Filled In)

### Example 1: REST API Service (Node.js)

```markdown
# CLAUDE.md — project context

## what this project is
A REST API for a SaaS billing system. Handles subscriptions, invoices, and payment webhooks for ~2,000 customers.

## tech stack
- Language: TypeScript 5.4
- Framework: Express 4.18 + tRPC
- Database: PostgreSQL 16 via Drizzle ORM
- Testing: Vitest + Supertest
- Package manager: pnpm

## essential commands
\`\`\`bash
pnpm install
pnpm dev                    # starts on port 3001
CI=true pnpm test           # runs all tests
pnpm db:migrate             # apply pending migrations
pnpm db:generate            # regenerate Drizzle types after schema changes
\`\`\`

## architecture
Routes in src/routes/, business logic in src/services/, DB layer in src/db/.
All routes validate input with zod schemas in src/schemas/.
Webhook handlers in src/webhooks/ — these are idempotent by design.

## what NOT to do
- Do not write raw SQL — use Drizzle query builder
- Do not handle Stripe webhooks without verifying the signature
- Do not return 200 for failed operations — use proper HTTP status codes
- Do not skip the service layer — routes call services, services call db
```

### Example 2: Mobile App (React Native)

```markdown
# CLAUDE.md — project context

## what this project is
A fitness tracking app for iOS and Android. Users log workouts, track progress, and follow training plans. ~15K monthly active users.

## tech stack
- Language: TypeScript 5.3
- Framework: React Native 0.74 + Expo 51
- State: Zustand + React Query
- Backend: Supabase (auth, database, storage)
- Testing: Jest + Detox for E2E

## essential commands
\`\`\`bash
npx expo start              # dev server
npx expo run:ios            # native iOS build
npm test                    # unit tests
npx detox test -c ios.sim   # E2E tests on simulator
\`\`\`

## architecture
Screens in src/screens/, reusable components in src/components/.
Navigation defined in src/navigation/ using React Navigation 6.
API calls go through src/api/ hooks — never call Supabase directly from components.
Offline-first: workouts saved locally first, synced when online.

## what NOT to do
- Do not call Supabase from components — go through src/api/ hooks
- Do not use inline styles — use the theme system in src/theme/
- Do not store sensitive data in AsyncStorage — use SecureStore
- Do not skip the offline sync queue — all writes go through src/sync/
```

### Example 3: Data Pipeline (Python)

```markdown
# CLAUDE.md — project context

## what this project is
An ETL pipeline that processes 2M+ daily events from Kafka, transforms them, and loads into BigQuery for analytics dashboards.

## tech stack
- Language: Python 3.12
- Framework: Apache Beam (Dataflow runner)
- Queue: Kafka via confluent-kafka
- Storage: BigQuery + GCS for staging
- Testing: pytest + testcontainers
- Package manager: uv

## essential commands
\`\`\`bash
uv sync                       # install deps
uv run pytest                 # run all tests
uv run python -m pipeline.main --runner DirectRunner  # local test run
uv run beam_deploy staging    # deploy to staging Dataflow
\`\`\`

## architecture
Pipeline stages in src/pipeline/transforms/. Each transform is a standalone DoFn.
Schemas defined in src/schemas/ as Pydantic models.
Config in src/config/ — environment-specific YAML files.
Dead letter queue for failed records in src/pipeline/dlq/.

## what NOT to do
- Do not process records without schema validation first
- Do not write to BigQuery without going through the batch writer in src/pipeline/io/
- Do not use print() for logging — use the structured logger in src/utils/log.py
- Do not hardcode project IDs — read from config
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
- [ ] Set up `.claude/settings.json` with at least one hook (auto-format is a good start)
- [ ] Check if your team uses other AI tools. If yes, add an AGENTS.md too.
- [ ] Tell Claude: "Read CLAUDE.md and confirm you understand the project before we start"

That last step is critical. It forces Claude to actually load the context instead of charging ahead.
