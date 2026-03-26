---
title: "Claude Code Cheat Sheet: Keybindings, Hooks, and Syntax Not in the Docs"
description: "Everything I've learned using Claude Code 8 hours a day that isn't in the official documentation. Keyboard shortcuts, hook patterns, and undocumented features."
date: "2026-03-26"
tier: "founding"
category: "tool-drop"
---

I've been using Claude Code as my primary development tool for four months. The official docs cover maybe 40% of what you need to know. Here's the rest.

## Keybindings That Matter

The basics you already know — Tab to accept a suggestion, Escape to cancel. Here are the ones that actually speed things up:

- **Shift+Tab**: Reject current suggestion and request an alternative
- **Ctrl+C**: Cancel a running generation without losing your prompt history
- **/** (slash): Open the command menu. This is where the power lives.
- **/compact**: Summarize the conversation and free up context. Use this constantly.
- **/clear**: Nuclear option. Wipe the conversation and start fresh.
- **/cost**: Check how much you've spent this session. Keeps you honest.
- **/model**: Switch models mid-conversation without restarting

The one nobody uses: **/init**. It auto-generates a CLAUDE.md for your project by scanning the codebase. The output needs editing, but it's a solid starting point.

## Hook Patterns

Hooks run commands automatically when Claude Code performs certain actions. They live in your `.claude/settings.json` file.

**Pre-commit hook — run tests before any commit:**

```json
{
  "hooks": {
    "PreCommit": ["npm test -- --bail"]
  }
}
```

If the tests fail, Claude Code won't commit. Simple. Saves you from pushing broken code.

**Post-file-edit — auto-lint on save:**

```json
{
  "hooks": {
    "PostFileEdit": ["npx eslint --fix $FILE"]
  }
}
```

The `$FILE` variable gets replaced with whatever file was just modified. Your code stays clean without thinking about it.

**Post-tool-use — log every tool call:**

Useful for debugging agent behavior. Log what tools Claude Code used and in what order. Helps you understand why it made the choices it did.

## The Skills Directory

This one flies under the radar. Create `.claude/skills/` in your project root. Each markdown file in there becomes a reusable workflow.

Example: `.claude/skills/add-api-endpoint.md`

```markdown
# Add API Endpoint

When asked to create a new API endpoint:
1. Create route file in `/api/routes/`
2. Add input validation using Zod schema
3. Add corresponding test file
4. Register route in `/api/index.ts`
5. Run `npm run typecheck`
```

Now when you tell Claude Code to "add an API endpoint," it follows your playbook instead of guessing. This is the single biggest productivity unlock I've found.

## Subagent Patterns

You can spin up focused subagents for specific tasks. Instead of asking your main conversation to handle everything, break it up.

The pattern: use your main session for orchestration. Kick off subagents for isolated tasks — "write the tests for this module," "refactor this function," "update the docs."

Each subagent gets clean context. No bleeding between tasks. The main session stays focused.

In practice, I do this with the `/clear` command between major tasks, but structured subagents through the SDK give you even more control.

## Context Management

This is where most people fail. They start a session, work for an hour, and wonder why Claude Code is giving worse answers.

**The context is full.** You stuffed it with 200 back-and-forth messages and now the model is losing track.

Rules I follow:

1. Start fresh for every new task. Not every new question — every new *task*.
2. Run `/compact` every 15-20 messages.
3. Put persistent context in CLAUDE.md, not in conversation. Conversations die. CLAUDE.md persists.
4. If you're copy-pasting previous responses back into the chat, your workflow is broken.

## Undocumented Tricks

**Multi-file edits**: Ask Claude Code to "edit these three files together" and it'll plan the changes as a batch. Way better than one-at-a-time.

**Checkpoint trick**: Before a risky refactor, tell Claude Code "remember the current state of these files as a checkpoint." It'll track what they look like now and can revert if things go sideways.

**The @ mention**: Use `@filename` in your prompt to explicitly pull a file into context. Better than hoping the agent finds it on its own.

**Permission bundles**: Set `allowedTools` in your project settings to pre-approve specific tools. Stops the constant "allow this tool?" prompts.

Use these daily. They compound.
