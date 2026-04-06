---
title: "The Boris Cherny Method: How Claude Code's Creator Runs 15 Sessions in Parallel"
description: "The guy who built Claude Code shared his actual workflow. 10-15 parallel sessions, self-evolving CLAUDE.md, zero SQL in 6 months. Here's exactly what he does."
date: "2026-03-30"
tier: "free"
category: "playbook"
---

# The Boris Cherny Method

Boris Cherny is a Staff Engineer at Anthropic and the creator of Claude Code. In January 2026, he posted a Threads series walking through his exact daily setup. Then he did a deep dive on Lenny's Podcast and another on The Pragmatic Engineer Podcast with Gergely Orosz. The internet lost its mind.

Here's the thing: his setup is surprisingly vanilla. His words, not mine. But the *way* he uses it is not vanilla at all.

Let me break down what he actually does.

---

## The Parallel Session Setup

Boris runs 10-15 Claude Code sessions at the same time. Every single day.

The split:

- **5 sessions in terminal.** Each one gets its own git checkout (or git worktree). Tabs numbered 1 through 5. He uses system notifications so he knows when Claude needs input.
- **5-10 sessions on claude.ai/code.** Running in the browser, working on separate tasks simultaneously.

He uses Opus with extended thinking for everything. Not Sonnet. His reasoning: yes, Opus is slower per session. But you steer it less. It's better at tool use. When you're running 10+ sessions in parallel, the per-session speed barely matters. What matters is how often you have to babysit.

The team's motto: "Don't babysit."

He even kicks off sessions from his iPhone using the Claude iOS app every morning. Start something on your phone at breakfast. Pick it up on your laptop 20 minutes later.

This is the single biggest tip from the entire Claude Code team: run parallel sessions with separate git worktrees. It's the #1 productivity unlock they've found. Everyone on the team does it differently, but everyone does *this*.

---

## The CLAUDE.md System (This Is the Real Weapon)

Every Anthropic team maintains a CLAUDE.md file checked into their repo. Boris's is about 100 lines, roughly 2,500 tokens. Not huge. But every line is earned.

Here's how it works:

1. Claude makes a mistake on your codebase.
2. You correct it.
3. You end with: **"Update your CLAUDE.md so you don't make that mistake again."**
4. Claude writes a rule for itself.
5. That rule lives in the repo forever.

Boris's exact quote from Threads: *"Invest in your CLAUDE.md. After every correction, end with: Update your CLAUDE.md so you don't make that mistake again."*

He says Claude is "eerily good at writing rules for itself." And here's where it compounds: the whole team contributes. Multiple updates per week. During code review, Boris tags @.claude on teammates' PRs to add learnings to CLAUDE.md as part of the PR itself, using the Claude Code GitHub Action.

He calls this "Compounding Engineering." Every correction makes every future session smarter. Not just for you. For everyone on the team.

### What's Actually In His CLAUDE.md

Three core principles:

1. **Simplicity first.** Prefer deleting code over adding it. Minimal changes.
2. **No laziness.** Find root causes. No temporary hacks.
3. **Minimal impact.** Only touch what the task requires. No side effects.

Then there are six task management rules:

1. Plan first. Write the plan to `tasks/todo.md`.
2. Verify the plan before starting.
3. Track progress continuously.
4. Explain changes at each step.
5. Document results in `todo.md`.
6. Capture lessons. Update `lessons.md`.

And five workflow rules:

- **Plan mode is default** for anything with 3+ steps.
- **Use subagents** for parallel subtasks to preserve context.
- **Self-improvement loop.** Update rules after corrections.
- **Verify before marking done.** Prove the work works.
- **Balanced elegance.** Ask "is there a better way?" but don't over-engineer.

That's 33 rules total. Zero hand-holding. The file teaches Claude how to think about *your* codebase specifically.

---

## Plan Mode, Then Auto-Accept

Boris's actual coding flow:

1. Hit Shift+Tab twice to enter **Plan mode**.
2. Go back and forth with Claude until the plan looks right.
3. Switch to **auto-accept mode**.
4. Claude one-shots the implementation.

His take: "A good plan is really important." When the plan is solid, Claude can usually execute the whole thing without further input. That's how you run 10+ sessions. You spend your time reviewing plans and checking outputs, not writing code.

He challenges Claude too. Prompts like:

- *"Grill me on these changes and don't make a PR until I pass your test."*
- *"Prove to me this works."*
- Just the word *"Fix."* with a bug report pasted in.

Short prompts. High expectations.

---

## Zero SQL in 6+ Months

This one surprised people. Boris hasn't written a single line of SQL in over six months.

From his Threads post: *"Ask Claude Code to use the 'bq' CLI to pull and analyze metrics on the fly. We have a BigQuery skill checked into the codebase, and everyone on the team uses it for analytics queries directly in Claude Code. Personally, I haven't written a line of SQL in 6+ months."*

The setup: the team has a BigQuery "skill" (a structured prompt template) checked into their repo. When Boris needs data, he tells Claude what he wants. Claude writes the SQL, runs it through the `bq` CLI, and interprets the results. All in one context window.

He added: "This works for any database that has a CLI, MCP, or API."

Beyond BigQuery, Claude handles his Slack searches and posts (via MCP server), pulls error logs from Sentry, and reads Docker logs for distributed system debugging. His Threads post about it: *"Claude Code uses all my tools for me. It often searches and posts to Slack (via the MCP server), runs BigQuery queries to answer analytics questions (using bq CLI), grabs error logs from Sentry."*

All the MCP configs are checked into `.mcp.json` and shared with the whole team.

---

## Slash Commands and Subagents

Boris stores reusable workflows in `.claude/commands/` and `.claude/agents/`, both checked into git:

**Commands he uses daily:**
- `/commit-push-pr` for the obvious workflow
- `/techdebt` to find and eliminate duplicated code
- Custom commands with inline bash that pre-computes info (like git status) so Claude doesn't waste tokens on it

**Subagents:**
- `code-simplifier` that cleans up code after a task is done
- `verify-app` that runs end-to-end testing

He also runs a PostToolUse hook that auto-formats code after every write/edit:

```json
"PostToolUse": [{
  "matcher": "Write|Edit",
  "hooks": [{"type": "command", "command": "bun run format || true"}]
}]
```

For permissions, he uses `/permissions` with wildcard syntax like `"Bash(bun run *)"` or `"Edit(/docs/**)"` stored in `settings.json`. Never `--dangerously-skip-permissions`.

---

## The Verification Insight

If you take one thing from Boris's workflow, take this:

**Give Claude a way to verify its work.**

His claim: verification feedback loops improve output quality 2-3x. Not a small number.

For frontend changes on claude.ai/code, his team uses the Claude Chrome extension. Claude opens a browser, navigates the UI, checks if the feature works, iterates until it's right. For backend work, it's test suites. For data work, it's re-running queries and sanity-checking numbers.

The pattern: Claude does the work, then Claude checks the work, then Claude fixes what's wrong. You just watch.

---

## The 4% Number

SemiAnalysis (Dylan Patel's research firm) published a report in February 2026: Claude Code accounts for 4% of all public GitHub commits. Their projection: 20%+ of daily commits by end of 2026.

To put that in perspective: Claude Code launched as a research preview in February 2025. One year later, it's responsible for a measurable chunk of all public code on Earth.

A few caveats. Winbuzzer reported that roughly 90% of Claude Code's output lands in repos with fewer than 2 stars. Most of it is personal projects, experiments, and prototyping. Not production code at Fortune 500 companies. But still: 4% of all public commits from a single tool that's barely a year old is wild.

Boris himself says his team writes "pretty much 100% of our code" with Claude Code. The Anthropic team building Claude Code uses Claude Code to build Claude Code. It's recursive at this point.

---

## What This Actually Means for You

You don't need 15 parallel sessions. Start with 2 or 3. The real takeaways:

**1. Your CLAUDE.md is the most important file in your repo.** Every time you correct Claude, make it write a rule so it never makes that mistake again. This compounds. In a month, Claude will know your codebase's quirks better than a new hire.

**2. Plan before you execute.** Shift+Tab twice. Agree on the approach. Then let Claude run. You'll interrupt less and ship more.

**3. Git worktrees unlock parallelism.** One checkout per session. No merge conflicts. No context switching. Just multiple streams of work flowing at the same time.

**4. Give Claude your tools.** BigQuery CLI. Slack MCP. Sentry. Whatever you use daily. The less context-switching you do, the more you can run in parallel.

**5. Verification is not optional.** If Claude can check its own work, the quality roughly triples. Build that loop in.

Boris's workflow isn't magic. It's architecture. He's not a better prompter than you. He just set up a system where Claude gets smarter every day, runs on 15 tracks simultaneously, and checks its own homework.

That's the gap. Not talent. Infrastructure.

---

*Sources: Boris Cherny's [Threads series](https://www.threads.com/@boris_cherny) (January-February 2026), [Lenny's Podcast interview](https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens) (February 2026), [The Pragmatic Engineer Podcast](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny), [SemiAnalysis report](https://newsletter.semianalysis.com/p/claude-code-is-the-inflection-point) on GitHub commit data (February 2026), and the community-compiled [howborisusesclaudecode.com](https://howborisusesclaudecode.com).*
