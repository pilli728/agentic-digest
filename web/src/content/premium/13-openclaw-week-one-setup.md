---
title: "OpenClaw Week-One Setup: Lock Your Gateway Before You Connect Anything"
description: "The exact setup sequence for OpenClaw that avoids the security mistakes 80% of new users make. Gateway config, plugin vetting, cost controls."
date: "2026-03-26"
tier: "founding"
category: "guide"
---

OpenClaw is an open-source personal AI assistant that went from a side project (originally called Clawdbot, then Moltbot) to 100k+ GitHub stars in a matter of weeks. Created by PSPDFKit founder Peter Steinberger, it runs locally and connects to your chat apps (WhatsApp, Telegram, Discord) while using MCP servers and "skills" from ClawHub to do actual work on your machine.

It's powerful. It's also dangerous if you set it up wrong.

Most people install it, connect a bunch of MCP servers and skills, and start building. That's backwards. You need to lock the gateway down first.

## What OpenClaw Actually Is (And Isn't)

OpenClaw is NOT an agent gateway in the traditional API-proxy sense. It's a local AI assistant that acts as the agent itself. It connects to LLM providers (Anthropic, OpenAI, Google, or local models via Ollama), takes instructions through your messaging apps, and executes tasks using tools.

The architecture looks like this:

```
You (WhatsApp/Telegram/Discord/CLI)
        |
        v
  OpenClaw Daemon (local, port 3000)
        |
        +--- LLM Provider (Anthropic/OpenAI/Google/Ollama)
        |
        +--- MCP Servers (filesystem, Brave Search, Postgres, GitHub, etc.)
        |
        +--- Skills (ClawHub marketplace + custom Python/JS scripts)
        |
        +--- SOUL.md (personality + constraints file)
```

The daemon binds to localhost by default. This matters. Do NOT expose it to the public internet. It is not hardened for that. If you need remote access, use SSH tunnels or Tailscale.

## Step 0: Installation (15 minutes)

You need Node.js 22.16+ (Node 24 recommended).

```bash
# Option A: One-liner (downloads, installs, runs onboarding wizard)
curl -fsSL https://openclaw.ai/install.sh | bash

# Option B: Manual via npm
npm install -g openclaw@latest

# Then run the onboarding wizard
openclaw onboard --install-daemon
```

The onboarding wizard asks for your LLM API key, picks your messaging channels, and starts the daemon. Resist the urge to connect everything during onboarding. Pick one messaging channel. Enter your API key. Stop there.

Verify it worked:

```bash
openclaw --version
```

## Step 1: Lock Down File Permissions (Day 1, First Thing)

OpenClaw stores everything in `~/.openclaw/`. Your API keys, config, credentials, conversation history. All of it.

```bash
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json
chmod 700 ~/.openclaw/credentials
```

If someone (or some process) can read `~/.openclaw/openclaw.json`, they have your API keys. Your LLM credentials. Everything the assistant can access. Lock it immediately.

## Step 2: Gateway Security (Day 1)

The main config lives at `~/.openclaw/openclaw.json`. Here's what a locked-down config looks like:

```json
{
  "daemon": {
    "host": "127.0.0.1",
    "port": 3000,
    "auth": {
      "enabled": true,
      "token": "${OPENCLAW_AUTH_TOKEN}"
    }
  },
  "llm": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514",
    "apiKey": "${ANTHROPIC_API_KEY}"
  },
  "mcpServers": {},
  "skills": [],
  "safety": {
    "confirmDestructive": true,
    "blockedCommands": ["rm -rf", "DROP TABLE", "FORMAT"],
    "maxConcurrentTools": 3
  }
}
```

Key things to notice:

- **host is 127.0.0.1**, not 0.0.0.0. This means it only accepts local connections.
- **auth is enabled**. Every request needs a token.
- **mcpServers is empty**. We haven't connected anything yet. That's intentional.
- **confirmDestructive is true**. OpenClaw will pause before running anything that could cause damage.

Store secrets in environment variables or in `/etc/openclaw/env`, not hardcoded in the JSON file. OpenClaw reads env vars at startup.

## Step 3: MCP Server Vetting (Day 2-3)

MCP servers are how OpenClaw talks to external tools. The config goes in that `mcpServers` block. Start with these five (they're well-maintained and widely used):

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/you/projects"],
      "env": {}
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

Before adding ANY MCP server:

1. **Read the source code.** If it's closed source, skip it.
2. **Check the scope.** A search server shouldn't need filesystem access. If permissions look too broad, skip it.
3. **Check maintenance.** Last commit more than 3 months old? That server isn't getting security patches.
4. **Install one at a time.** Add a server, restart the daemon (`openclaw daemon restart`), test it, check logs. Then add the next one. Debugging five new servers at once is miserable.

## Step 4: Skills Audit (Day 3-4)

Skills are scripts (Python or JavaScript) that teach OpenClaw multi-step workflows. ClawHub is the marketplace. Since February 2026, ClawHub runs VirusTotal scans on uploads. That's a start, but it's not enough.

Treat every third-party skill as untrusted code. Read it before enabling it.

To install a skill from ClawHub:

```bash
openclaw skill install <skill-name>
```

Skills live in `~/.openclaw/skills/`. Open the file and read it. It's usually under 200 lines. If a "calendar integration" skill is making network calls to domains you don't recognize, delete it.

## Step 5: SOUL.md Constraints (Day 4)

SOUL.md is OpenClaw's personality and rules file. It sits at `~/.openclaw/SOUL.md`. Think of it as your CLAUDE.md equivalent. Whatever you put here, OpenClaw reads on every interaction.

Add hard constraints:

```markdown
# SOUL.md

## Safety Rules
- Never execute commands that delete files without explicit confirmation
- Never access or transmit API keys, passwords, or credentials in messages
- Never make purchases or financial transactions
- Rate limit: max 10 LLM calls per task
- If a task requires more than 5 tool calls, pause and summarize progress

## Allowed Domains for Network Access
- github.com
- api.anthropic.com
- your-internal-tools.company.com
```

## Step 6: Cost Monitoring (Day 5)

OpenClaw calls your LLM provider on every interaction. An agent loop can rack up costs fast. A skill that retries on failure can burn $50+ in minutes if you're on Claude Opus or GPT-4.

There's no built-in cost dashboard yet, but you can monitor costs:

**Check your provider dashboards directly.** Anthropic, OpenAI, and Google all have usage pages. Set billing alerts there.

**Set model-level guards in your config:**

```json
{
  "llm": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514",
    "maxTokensPerRequest": 4096,
    "maxRequestsPerMinute": 30,
    "maxRequestsPerDay": 500
  }
}
```

**Use Sonnet for routine tasks.** Only switch to Opus for complex reasoning. Most skills work fine on Sonnet and cost ~10x less.

**Log everything from day one.** Check `~/.openclaw/logs/` daily for the first week. Look for retry loops (the #1 cost killer) and unexpected tool calls.

## Common Mistakes

**Exposing the gateway to the internet.** Don't bind to 0.0.0.0. Don't set up a public reverse proxy. Use SSH tunnels or Tailscale if you need remote access.

**Installing 12 MCP servers on day one.** Start with 2-3. Add more after you understand the interaction patterns.

**Skipping SOUL.md.** Without constraints, OpenClaw will try anything you ask. Including things you didn't mean to ask. Set boundaries.

**Using the same API key for OpenClaw and production apps.** Create a separate API key with its own billing alerts. Isolate the blast radius.

**Not reading skills before installing them.** ClawHub's VirusTotal scanning catches malware. It doesn't catch a skill that "accidentally" sends your file contents to a third-party API. Read the code.

## Week-One Checklist

- [ ] OpenClaw installed and daemon running
- [ ] File permissions locked (chmod 700/600 on ~/.openclaw)
- [ ] Gateway auth enabled with token
- [ ] Daemon bound to 127.0.0.1 only
- [ ] One messaging channel connected
- [ ] Secrets in env vars, not hardcoded in config
- [ ] 1-2 MCP servers added and tested individually
- [ ] Skills audited (source code read before enabling)
- [ ] SOUL.md written with safety constraints
- [ ] LLM provider billing alerts configured
- [ ] Rate limits set in config
- [ ] Logs reviewed daily
- [ ] confirmDestructive set to true

Do this in order. Skip nothing. The people who get burned by OpenClaw are the ones who connected everything on day one and asked questions later.
