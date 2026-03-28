---
title: "Auto Mode Breakdown: How Memory Consolidation Works and What Gets Pruned"
description: "Claude Code's auto mode is powerful but opaque. Here's what actually happens to your context, what gets pruned, and how to prevent losing important information."
date: "2026-03-26"
tier: "founding"
category: "technical"
---

Auto mode launched on March 24, 2026 as a research preview for Team plans. It lets Claude Code run without asking permission at every step. Reads files, writes code, runs tests, fixes errors. No clicking "approve" sixteen times.

It's great until it forgets what it was doing. Or until it does something you didn't want.

Here's how it all actually works.

## The Permission Model: Four Modes

Claude Code has four permission modes. You cycle through them with Shift+Tab during a session:

1. **Default mode.** Claude asks before every file write and every bash command. Safe. Slow.
2. **acceptEdits mode.** File writes auto-approved. Bash commands still need approval.
3. **Plan mode.** Claude plans but doesn't execute. You review and approve the plan.
4. **Auto mode.** Claude makes permission decisions on its own, with a safety classifier watching.

Auto mode is NOT the same as `--dangerously-skip-permissions`. That flag skips ALL safety checks. Auto mode has a classifier that blocks risky actions.

To enable auto mode from the CLI:

```bash
claude --enable-auto-mode
```

Then in a session, hit Shift+Tab until you see "auto" in the mode indicator. On Team and Enterprise plans, an admin has to enable it in Claude Code admin settings first.

## How the Safety Classifier Works

This is the part most people skip. Auto mode doesn't just approve everything. Before each tool call, a separate classifier model reviews the action.

The classifier runs on Claude Sonnet 4.6 (regardless of what model your main session uses). It checks three things:

1. **Scope escalation.** Is Claude doing something beyond what you asked for? You said "fix the tests" and it's modifying your CI pipeline? Blocked.
2. **Untrusted infrastructure.** Is the action targeting systems the classifier doesn't recognize as part of your project? Blocked.
3. **Prompt injection.** Does the action look like it was driven by hostile content Claude found in a file or web page? Blocked.

The classifier runs in two stages. First, a fast single-token filter (yes/no). If that flags the action, it runs chain-of-thought reasoning. Most actions clear the first stage, so the overhead is minimal.

What it won't catch: ambiguous user intent. If you gave vague instructions and Claude interprets them broadly, the classifier might let it through because it looks like it matches your request. Be specific in your prompts.

## How Context Consolidation Works

Claude Code on standard plans has a 200K token context window. On Max, Team, and Enterprise plans, it's 1M tokens now (went GA in early 2026). Either way, you can fill it up.

When usage hits about 83.5% of the window, Claude Code auto-compacts. It reserves ~33K tokens as a buffer. Here's what happens during compaction:

1. **Recent messages stay intact.** The last 10-15 exchanges are kept word-for-word.
2. **Older messages get summarized.** Tool outputs get condensed hard. A 500-line file read becomes "read src/auth.ts, 245 lines, contains JWT validation logic."
3. **File contents get dropped.** If Claude read a file 30 messages ago, the full content is gone. Only the summary remains.
4. **Your original instructions get partially preserved.** The system prompt and first message have some protection, but long initial instructions can still get trimmed.

The model doesn't know what's important to you. It makes generic decisions about what to keep. Your critical constraint ("never modify the payments table") might look like any other instruction and get compressed into nothing.

## What Gets Lost

The most common casualties:

- **Specific constraints** you mentioned early in the conversation
- **File contents** from earlier reads (the model thinks it remembers but doesn't)
- **Error messages** from failed attempts (it loses track of what it already tried)
- **Your stated preferences** about approach or architecture
- **The distinction between "done" and "in progress"** (I've watched Claude Code refactor a file, lose context, then refactor it again differently)

## The /compact Command

Don't wait for auto-compaction. Run `/compact` yourself every 15-20 messages.

When you run `/compact`, Claude Code summarizes the entire conversation history into a compressed representation. Typically 60-70% reduction in token usage. The difference from auto-compaction: you're in control. You can review the summary and correct it.

After running `/compact`, check the summary. If it missed something critical, tell it: "The summary should also include that we decided to use the adapter pattern for the database layer and that the payments module is off-limits."

You can also pass a focus hint: `/compact focus on the migration plan and the API changes we discussed`. This biases the summary toward what matters.

On the 1M context window (Max/Team/Enterprise), you can go longer before needing to compact. But longer sessions mean more accumulated context drift. Compact proactively even if you have the space.

## Claude Code's Memory System

Context compaction is temporary. It only helps within a single session. For persistence across sessions, Claude Code has a layered memory system:

### CLAUDE.md (Project Memory)

A file at your project root. Claude reads it at the start of every session. It never gets pruned because it's re-injected each time.

```markdown
# CLAUDE.md
## Rules
- Never modify files in /lib/payments/
- Always run tests after changing API routes
- Use Zod for all input validation
- This project uses pnpm, not npm
```

Keep it under 200 lines. Files under 200 lines have a 92%+ rule application rate. Above 400 lines, that drops to 71%. Be concise.

### ~/.claude/CLAUDE.md (User/Global Memory)

Your personal rules that apply to every project. Put your preferences here:

```markdown
# ~/.claude/CLAUDE.md
- Prefer functional style over class-based
- Always add JSDoc comments to exported functions
- Use early returns instead of nested conditionals
```

### Auto-Memory (~/.claude/projects/)

Shipped in v2.1.59 on February 26, 2026. Claude Code automatically synthesizes what it learned during sessions into durable memory files.

The path is `~/.claude/projects/<encoded-path>/memory/MEMORY.md`. The folder names are your project paths with slashes replaced by hyphens. Claude reads this at session start, just like CLAUDE.md.

Auto-memory captures things like: decisions you made, architecture patterns you chose, things you corrected it on. You can edit these files manually too. They're just markdown.

### Memory Hierarchy

When rules conflict, the resolution order is: project CLAUDE.md > user CLAUDE.md > auto-memory. Project-level rules always win.

## Strategies for Long-Running Agentic Workflows

Auto mode shines on focused tasks. It struggles on multi-hour sessions. Here's how to make long workflows work:

### Break Work Into Commit-Sized Chunks

Instead of "rewrite the entire auth system," do:
1. "Refactor the JWT validation into its own module" (commit)
2. "Add refresh token support" (commit)
3. "Update all routes to use the new auth module" (commit)

Each chunk gets full context. Commits create natural checkpoints.

### Use the --name Flag for Session Management

```bash
claude --name "auth-refactor"
```

Named sessions let you resume later with `/resume`. The session history persists, so you can pick up where you left off without re-explaining everything.

### Write Plans to Files, Not Messages

Before a long autonomous run, tell Claude: "Write the implementation plan to PLAN.md." Files persist. Context doesn't. If the session gets compacted, the plan survives because Claude can re-read the file.

### Monitor the Context Indicator

Claude Code shows context usage in the UI. When you see it climbing past 60%, consider compacting or starting a new session. Don't wait for the auto-compaction threshold.

## Git Worktrees for Parallel Work

Claude Code uses git worktrees to isolate parallel sessions. Each background agent gets its own working copy of your repo at `.claude/worktrees/`.

This means you can run multiple Claude Code sessions on the same repo without them stepping on each other's files. Changes only merge when you commit.

Practical use: kick off a background agent to write tests while you work on implementation in your main session. The test agent works in its own worktree. No conflicts until you merge.

```bash
# Start a background task (it gets its own worktree automatically)
claude "write integration tests for the auth module" --background
```

## When to Use Auto Mode vs Other Modes

**Use auto mode for:** Test-fix cycles. Lint-fix-commit workflows. Generating boilerplate across multiple files. Applying a known pattern to many files. Any task where steps are predictable and the blast radius is small.

**Use acceptEdits mode for:** Most day-to-day coding. You skip the file-write approvals but still review bash commands. Good balance of speed and control.

**Use plan mode for:** Architecture decisions. When you want to review the approach before any code gets written.

**Use default mode for:** Anything touching production data. Security-sensitive code. First-time exploration of an unfamiliar codebase. Debugging race conditions.

**Never use auto mode for:** Tasks involving secrets or credentials. Deploying to production. Anything where "just try stuff" could cause real damage. And remember: auto mode is still a research preview. The classifier is good, not perfect.

Auto mode is a power tool. The classifier is your safety net, not your substitute for judgment.
