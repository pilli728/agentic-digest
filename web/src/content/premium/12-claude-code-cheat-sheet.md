---
title: "Claude Code Cheat Sheet: Keybindings, Hooks, and Syntax Not in the Docs"
description: "Everything I've learned using Claude Code 8 hours a day that isn't in the official documentation. Keyboard shortcuts, hook patterns, and undocumented features."
date: "2026-03-26"
tier: "founding"
category: "tool-drop"
---

I've been using Claude Code as my primary development tool for four months. The official docs cover maybe 40% of what you need to know. Here's the rest.

## Slash Commands That Matter

Type `/` in the prompt to see the full list. There are 55+ built-in commands plus any custom skills you've added. Here are the ones I use daily:

- **/compact** - Summarize the conversation and free up context. Takes an optional argument for what to retain: `/compact keep the auth refactor context`. Use this when context exceeds 80%.
- **/clear** - Wipe the conversation and start fresh. Use when switching tasks entirely.
- **/cost** - Check how much you've spent this session. I check this every hour.
- **/model** - Switch models mid-conversation. Great for dropping to Haiku for simple tasks.
- **/init** - Auto-generates a CLAUDE.md by scanning your codebase. The output needs editing, but it's a 10-minute head start on a 2-hour task.
- **/memory** - View and edit your project's memory files directly.
- **/plan** - Enter plan mode. Claude analyzes and suggests but doesn't modify anything. Perfect for reviewing before a big refactor.
- **/vim** - Enable vim keybindings in the prompt input. Supports mode switching, hjkl navigation, w/b/e word motions, d/c/y operators, and text objects. If you're a vim person, this changes everything.
- **/keybindings** - Open the keybindings editor. Changes take effect immediately.

## Keybindings

The basics: Tab to accept, Escape to cancel. Here are the ones that speed things up:

- **Ctrl+C** - Cancel a running generation without losing prompt history
- **Option+T / Alt+T** - Toggle extended thinking on/off
- **Option+P / Alt+P** - Open the model picker
- **Ctrl+G** - Open the current file in your external editor
- **Shift+Tab** - Cycle through permission modes

All keybindings are remappable. Run `/keybindings` to edit `~/.claude/keybindings.json`. Changes apply instantly, no restart needed.

## The Hook System (Correct Format)

Hooks run shell commands automatically when Claude Code performs certain actions. They go in `.claude/settings.json` (project-level, shared with team) or `~/.claude/settings.json` (user-level, personal).

**The format most guides get wrong.** Hooks are NOT simple key-value pairs. Each hook event contains an array of matchers, and each matcher has its own array of hook commands.

Here's the actual structure:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'About to edit a file'"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx eslint --fix $CLAUDE_FILE"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude needs attention\" with title \"Claude Code\"'",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

### Hook Events

There are three hook events:

**PreToolUse** fires before Claude executes any tool. The exit code matters:
- Exit 0 = allow the tool to run
- Exit 2 = block the tool from running

This is your safety net. You can prevent Claude from editing certain files, running dangerous commands, or writing to protected directories.

**PostToolUse** fires after a tool completes. Use it for auto-formatting, linting, running tests, or logging. Exit code doesn't block anything since the action already happened.

**Notification** fires when Claude is waiting for your input or permission. Perfect for desktop notifications, Slack alerts, or sounds so you don't sit there staring at the screen wondering if it's done.

### Matcher Patterns

The `matcher` field is a regex that filters which tool triggers the hook. Common tools to match:

- `Edit|MultiEdit|Write` - file modifications
- `Bash` - shell command execution
- `Read` - file reading
- `Glob|Grep` - file search operations

Leave the matcher as an empty string `""` to match everything.

### Practical Hook Examples

**Auto-lint after every file edit:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $CLAUDE_FILE 2>/dev/null; npx eslint --fix $CLAUDE_FILE 2>/dev/null"
          }
        ]
      }
    ]
  }
}
```

**Block edits to migration files:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo $CLAUDE_FILE | grep -q '/migrations/' && exit 2 || exit 0"
          }
        ]
      }
    ]
  }
}
```

**macOS notification when Claude finishes or needs input:**
```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"$CLAUDE_NOTIFICATION\" with title \"Claude Code\" sound name \"Glass\"'",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

To disable all hooks temporarily: add `"disableAllHooks": true` to your settings file.

## Permission Modes

Permission prompts are the biggest productivity killer in Claude Code. Here's how to tame them.

**Default mode:** Claude asks before every file edit, bash command, and state change. Safe but slow.

**acceptEdits mode:** Auto-approves all file operations (edits, writes, creates). Bash commands still prompt. This is my daily driver. Turn it on with Shift+Tab or configure it in settings.

**Plan mode:** Read-only. Claude can analyze and suggest but can't modify anything. Use this for code review or when you want to understand a codebase before touching it.

**bypassPermissions mode:** Skips all prompts except writes to `.git`, `.claude`, `.vscode`, and `.idea` directories. Only use this in containers or VMs. Not your laptop.

**Auto mode (new, March 2026):** Uses an AI safety classifier to auto-approve or block actions. Less interruptions than default, safer than bypass. It's a good middle ground if you don't want to think about permissions but also don't want to go full YOLO.

### allowedTools Configuration

Instead of using broad permission modes, you can whitelist specific tools in your settings:

```json
{
  "allowedTools": [
    "Read",
    "Glob",
    "Grep",
    "Edit",
    "MultiEdit",
    "Write"
  ]
}
```

This goes in `.claude/settings.json` (project) or `~/.claude/settings.json` (global). Project settings override global. CLI flags override both.

You can also pass it per-session: `claude --allowedTools "Read,Grep,Glob,Edit"`

My setup: I allowlist Read, Glob, Grep, Edit, MultiEdit, and Write in my project settings. Bash stays on prompt. That way Claude can freely navigate and edit code, but I approve every shell command manually. Best of both worlds.

## The Memory System

Claude Code has a four-level memory hierarchy. Understanding it is the difference between re-explaining your project every session and having Claude just know.

### Level 1: Global Memory (~/.claude/CLAUDE.md)

Applies to every project. Put your universal preferences here: commit message style, language, coding philosophy.

```markdown
# ~/.claude/CLAUDE.md
- Always use TypeScript strict mode
- Commit messages: imperative mood, under 72 chars
- Prefer named exports over default exports
```

### Level 2: Project Memory (./CLAUDE.md)

Lives at your repo root. Committed to git, shared with the team. This is your project's AGENTS.md equivalent. Architecture decisions, conventions, build commands.

### Level 3: Modular Rules (.claude/rules/)

Since Claude Code 2.0 (January 2026), you can split rules into separate files:

```
.claude/rules/
  testing.md      ← test conventions
  api.md          ← API patterns
  database.md     ← query rules
```

Claude loads the relevant rule files based on context. More specific rules override general ones. If `.claude/rules/testing.md` says use Jest and `CLAUDE.md` says use Vitest, the rules file wins.

### Level 4: Auto Memory (.claude/memory/)

This is the one most people miss. Claude automatically saves notes as it works: build commands it discovered, debugging insights, architecture observations, code patterns it noticed. It writes to `.claude/memory/MEMORY.md` and creates topic-specific files.

You don't have to do anything. It just accumulates knowledge across sessions. Check the memory directory occasionally to see what Claude has learned about your project. Edit it if something's wrong.

### The Hierarchy Rule

When two levels conflict, the most specific wins. Rules file beats CLAUDE.md. CLAUDE.md beats global. This means your team can set project conventions and individual developers can override them for their own workflow without causing conflicts.

## The Skills System

Create `.claude/skills/` in your project. Each skill gets a directory with a `SKILL.md` file containing YAML frontmatter and markdown instructions.

```markdown
---
name: add-api-endpoint
description: Create a new API endpoint with validation and tests
---

When creating a new API endpoint:
1. Create route file in `/api/routes/`
2. Add input validation using Zod schema in the same file
3. Add corresponding test file at `/api/routes/__tests__/`
4. Register route in `/api/index.ts`
5. Run `npm run typecheck` and `npm test -- --bail`
```

This becomes the `/add-api-endpoint` slash command. The `name` field in frontmatter is the command name. The markdown body is what Claude follows.

Skills and the old `.claude/commands/` system have been unified. Existing commands files still work, but new ones should use the skills format.

Five built-in skills ship with Claude Code: `/btw`, `/claude-api`, `/debug`, `/loop`, and `/simplify`. You can override them by creating skills with the same name.

## Context Management

This is where most people fail. They start a session, work for an hour, and wonder why Claude Code is giving worse answers.

The context is full. You stuffed it with 200 back-and-forth messages and the model is losing track.

Rules I follow:

1. **New task, new session.** Not every new question. Every new task. If you're switching from "fix this bug" to "add this feature," clear or compact first.
2. **Run /compact at 80% context.** Don't wait for degradation. Be proactive. Tell it what to keep: `/compact retain the database schema discussion`.
3. **Put persistent context in CLAUDE.md.** Conversations die. CLAUDE.md persists. If you're repeating yourself across sessions, it belongs in a file.
4. **Use @ mentions.** Type `@filename` in your prompt to pull a specific file into context. Better than hoping Claude finds it on its own.
5. **If you're copy-pasting previous responses back into the chat, your workflow is broken.** That context should be in memory or a rules file.

## Tricks That Compound

**Multi-file edits**: Tell Claude to "edit these three files together" and it plans the changes as a batch. Way better than one-at-a-time because it can reason about cross-file dependencies.

**The @ mention**: `@filename.ts` in your prompt explicitly pulls that file into context. `@directory/` pulls the directory listing. Use these instead of hoping Claude's search finds what you need.

**Subagent pattern**: Use your main session for orchestration. Let Claude spawn focused subagents for isolated tasks. Each subagent gets clean context with no bleed between tasks. The main session stays focused on the big picture.

**Model switching mid-task**: Start complex reasoning on Opus, then `/model` switch to Sonnet for implementation. You get Opus-quality planning with Sonnet-speed execution.

**The plan-then-execute flow**: Start in plan mode (`/plan`). Have Claude analyze the problem and propose a solution. Review the plan. Then switch to normal mode and say "execute the plan." This two-step flow catches bad approaches before they burn tokens.

Use these daily. They compound.
