---
title: "Running a 24/7 AI Agent on a Mac Mini: 18 Cron Jobs, Zero Babysitting"
description: "One developer's setup for running AI agents around the clock. 18 cron jobs, 35 scripts, 6 custom skills, and a context system that gets smarter every day."
date: "2026-03-30"
tier: "founding"
category: "playbook"
---

# Running a 24/7 AI Agent on a Mac Mini

A developer named witcheer (@witcheer on X) has been running an autonomous AI agent on a Mac Mini M4 for two months straight. Not as a weekend experiment. As actual infrastructure. 14 launchd agents, 25+ shell scripts, research crons, a Telegram bot, RSS monitoring, memory files, the whole thing. Running continuously. No babysitting.

Then they migrated from OpenClaw to Hermes Agent in three hours. The 5 research crons became 15. They added a competitor dashboard, Dune Analytics monitoring, a Telegram channel auto-drafter, content performance tracking, an outreach CRM, and a learning digest. All configured in natural language instead of crontab syntax.

This is the playbook for building the same kind of setup. Not the "hello world" version. The version that actually runs for months.

---

## Why a Mac Mini

The Mac Mini M4 idles at 3-5 watts. That's less than a phone charger. Leave it on 24/7 and your electricity bill goes up maybe $2/month. Under heavy LLM inference with a local model, it peaks around 65 watts. Still nothing.

Compare that to a VPS: $20-75/month for something with less power. Or a cloud GPU: $200+/month. The Mini pays for itself in a few months.

Apple Silicon also matters here. M4 runs local models through Ollama surprisingly well. You can run a 7B parameter model locally for tasks that don't need Claude-level reasoning. Use the API for the hard stuff. Local inference for the routine stuff. Your API bill drops dramatically.

The real advantage is reliability. This thing is designed to sit in a closet and run forever. Enable "restart after power failure" in System Settings > Energy Saver and it boots back up automatically after outages. No UPS needed for most setups.

## The Architecture

Here's what a production always-on agent setup looks like:

```
Mac Mini M4 (closet, ethernet, always on)
    |
    +--- Agent Runtime (OpenClaw / Hermes / Claude Code)
    |       |
    |       +--- LLM Provider (Anthropic API / local Ollama)
    |       +--- MCP Servers (filesystem, search, APIs)
    |       +--- Skills (markdown + scripts)
    |
    +--- launchd (macOS service manager)
    |       |
    |       +--- Agent daemon (auto-restart on crash)
    |       +--- Cron jobs (scheduled tasks)
    |       +--- Watchdog (monitors daemon health)
    |
    +--- Memory System
    |       +--- MEMORY.md (always loaded, ~100 lines)
    |       +--- Daily logs (memory/YYYY-MM-DD.md)
    |       +--- Deep knowledge (people/, projects/, topics/)
    |
    +--- Delivery Layer
            +--- Telegram bot
            +--- Slack webhook
            +--- Email (optional)
```

Three layers do the heavy lifting: scheduling (when things run), skills (what the agent knows how to do), and memory (what the agent remembers between sessions).

## Setting Up launchd (Not Cron)

On macOS, forget `crontab`. Use `launchd`. It's more reliable, handles restarts, and integrates with the OS properly.

First, make your agent daemon start on boot. Create a plist file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.agent.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/openclaw</string>
        <string>daemon</string>
        <string>start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/you/.agent/logs/daemon.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/you/.agent/logs/daemon-error.log</string>
</dict>
</plist>
```

Save this to `~/Library/LaunchAgents/com.agent.daemon.plist`. Then load it:

```bash
launchctl load ~/Library/LaunchAgents/com.agent.daemon.plist
```

`KeepAlive` is the key setting. If the daemon crashes, macOS restarts it automatically. Combined with the "restart after power failure" setting, your agent comes back online within 60 seconds of any reboot.

One gotcha: launchd is notoriously picky about file permissions and paths. If your agent doesn't start after reboot, check `Console.app` for launchd errors. Nine times out of ten it's a path issue.

## The Cron Job Structure

witcheer's setup evolved from 5 research crons to 15+ after migration. Here's what a real cron schedule looks like for an always-on agent, organized by frequency:

**Every 30 minutes (monitoring)**
- RSS feed check (54 feeds via newsboat)
- Breaking news monitor (TVL + stablecoin pegs)
- Deployment health check

**Every 2 hours (analysis)**
- Competitor dashboard refresh
- Content performance tracking
- Social engagement scan

**Daily at fixed times**
- 6:00 AM: Morning research briefing
- 9:00 AM: Daily digest compilation
- 10:00 AM: Social media engagement run
- 12:00 PM: Midday intelligence update
- 6:00 PM: End-of-day summary
- 9:00 PM: Overnight research queue setup

**Weekly**
- Monday: Outreach CRM review
- Wednesday: Learning digest compilation
- Friday: Weekly performance report

In OpenClaw, each cron job is a JSON entry in `~/.openclaw/cron/jobs.json`. The two execution modes matter:

- **`systemEvent`**: Injects into the main conversation session. The agent has full context. Good for tasks that need to reference earlier work.
- **`agentTurn`**: Spawns an isolated session. No shared context. Good for independent tasks that shouldn't pollute the main thread.

Use `agentTurn` for most cron jobs. Isolated sessions prevent one runaway task from corrupting your main agent context. witcheer learned this the hard way during migration when delivery mode settings caused garbled Slack messages.

## Building Skills That Actually Work

Skills are just markdown files with YAML frontmatter. That's the whole thing. No SDK. No compilation. No deployment.

```
~/.openclaw/workspace/skills/
    research-briefing/
        SKILL.md
        reference/
        scripts/
    social-engagement/
        SKILL.md
        scripts/engage.py
    content-drafter/
        SKILL.md
```

A skill file looks like this:

```markdown
---
name: research-briefing
trigger: manual, cron
model: claude-sonnet-4-20250514
---

# Research Briefing Skill

## When to Use
Run this skill for the daily morning briefing or when
explicitly asked to research a topic.

## Instructions
1. Read today's RSS digest from memory/feeds/today.md
2. Identify the top 5 stories by relevance to our topics
3. For each story, write a 2-sentence summary
4. Flag anything that contradicts yesterday's briefing
5. Save output to memory/briefings/YYYY-MM-DD.md

## Rules
- ALWAYS check memory/briefings/ for the last 3 days first
- NEVER summarize paywalled content you can't access
- Keep each summary under 50 words
- If no significant news, say so. Don't pad.
```

The critical insight from people running these at scale: be opinionated. "ALWAYS" and "NEVER" directives work. Suggestions don't. The LLM reads the skill file as context and follows the strongest signals.

Keep skills under 500 words. Token efficiency matters when you're running 15+ cron jobs that each load skills.

## The Memory System (This Is the Real Secret)

witcheer had 60 memory files when they migrated frameworks. The migration proved something interesting: copying those memory files to the new system immediately restored the agent's personality and capabilities. Memory matters more than the model.

Here's how the three-tier memory system works:

**Tier 1: Always loaded (MEMORY.md)**

This file loads into every single conversation. Keep it under 100 lines. It contains the agent's core identity, current priorities, and key facts. Think of it as working memory.

```markdown
# MEMORY.md

## Identity
I am [name]. I monitor DeFi markets and crypto news for [owner].

## Current Priorities
1. Track stablecoin depegging events
2. Monitor competitor content output
3. Draft weekly newsletter by Friday

## Key Facts
- Using GLM-5 as primary model ($21/month)
- Telegram is primary delivery channel
- Owner timezone: CET
```

**Tier 2: Daily context (auto-loaded)**

Files named `memory/YYYY-MM-DD.md` load automatically for today and yesterday. The agent writes these at the end of each day. When a new session starts, it reads yesterday's notes and picks up where it left off.

This is what makes sessions intelligent. Without daily context files, every cron job starts from zero. With them, the 6 PM summary knows what the 6 AM briefing found.

**Tier 3: Deep knowledge (searched on demand)**

Directories for `people/`, `projects/`, `topics/`, `decisions/`. Not loaded by default. The agent searches these via vector embeddings when it needs specific context.

This is where long-term learning accumulates. After two months, witcheer's agent had built up enough deep knowledge to make connections between events that a fresh agent would miss.

## Claude Code's Scheduling Options

If you're not using OpenClaw, Claude Code has its own scheduling system as of March 2026:

**`/loop` (session-scoped)**

Quick and dirty. Type `/loop 5m check the deployment` and Claude runs that prompt every 5 minutes. Dies when you close the terminal. Good for temporary monitoring. Bad for always-on operations.

**Desktop scheduled tasks (persistent)**

Survives restarts. Runs as long as the app is open. Supports one-minute intervals. Only on macOS and Windows. This is the closest to a real cron job in Claude Code.

**Cloud scheduled tasks (truly persistent)**

Runs on Anthropic's servers. Survives everything. Minimum interval is one hour. No access to local files (works from a fresh git clone). Best for tasks that don't need your local filesystem.

**DIY with `claude -p` and actual cron**

The headless mode flag (`-p`) makes Claude Code work in scripts. Combine it with macOS launchd or Linux cron for real scheduling:

```bash
# In your launchd plist or crontab
claude -p "Check the deployment status and report any failures" \
  --allowedTools Bash,Read \
  --output-format json
```

Always specify `--allowedTools`. Without it, Claude exits with an error on any action needing approval. Specify only what the script actually needs.

## What Goes Wrong

People who've run these setups for weeks (not days) report the same failure modes.

**Platform bans.** One developer's agent got shadowbanned on Reddit and suspended on GitHub within two weeks. Automated posting patterns are obvious to platform detection. If your agent posts publicly, it needs rate limits and human-like timing variations.

**Completion lies.** Agents report tasks as "done" when they're not. One developer found that analytics accounts the agent claimed to create didn't exist. Published pages returned 404s. Build verification into every skill. Don't trust the agent's self-report.

**Cost runaway.** A skill that retries on failure can burn $50+ in minutes on Opus. Set `maxRequestsPerDay` limits. Use Sonnet for routine tasks and Opus only when you need serious reasoning. witcheer uses GLM-5 at $21/month as their primary model. That's the kind of cost discipline that lets you run 24/7 without flinching.

**Delivery pipeline failures.** witcheer's biggest lesson from migrating: the data moves in 30 minutes. Getting the agent's output to reach you through the right channel, in the right format, at the right time without silent failures? That's where the hours go. Test delivery end-to-end before you trust a cron job.

**External API changes.** One developer's Twitter posting skill broke because the API endpoint changed without notice. Third-party services change URLs, auth flows, and rate limits. Your agent won't tell you it failed unless you build alerting into the skill itself.

## The Real Cost Breakdown

Here's what running an always-on agent actually costs per month:

| Item | Cost |
|------|------|
| Mac Mini M4 (amortized over 3 years) | ~$17/month |
| Electricity (24/7 idle + bursts) | ~$2/month |
| LLM API (budget model like GLM-5) | ~$21/month |
| LLM API (Claude Sonnet, moderate use) | ~$30-80/month |
| LLM API (Claude Opus, heavy use) | ~$150-400/month |
| Internet (you already have this) | $0 incremental |

Budget path: $40/month for Mac Mini + cheap model. That's a Netflix subscription plus lunch. For a 24/7 research assistant, content drafter, and monitoring system, that's absurdly cheap.

Premium path with Claude Sonnet for everything: $100/month. Still cheaper than any human assistant, any SaaS dashboard bundle, or any cloud GPU rental.

## The Setup Sequence (Do This In Order)

**Week 1: Foundation**
1. Set up Mac Mini headless (ethernet, auto-restart on power failure)
2. Install your agent runtime (OpenClaw, Claude Code, or Hermes)
3. Configure one messaging channel (Telegram is easiest)
4. Write MEMORY.md with identity and priorities
5. Create one skill (start with a daily briefing)
6. Set up one cron job running that skill every morning
7. Monitor logs daily

**Week 2: Expand**
8. Add 2-3 more skills (research, monitoring, drafting)
9. Add RSS feed monitoring cron
10. Set up daily memory writing (agent logs what happened)
11. Connect MCP servers one at a time, test each
12. Add error alerting (agent messages you on failure)

**Week 3-4: Harden**
13. Add delivery verification to all skills
14. Set up cost monitoring and alerts
15. Build the watchdog (restart daemon if health check fails)
16. Tune cron schedules based on what's actually useful
17. Prune skills and crons that don't pull their weight

**Month 2+: Compound**
18. The memory system starts paying dividends
19. Agent makes connections between today's events and last month's
20. Add more complex workflows that chain multiple skills
21. Gradually increase autonomy as trust builds

The compounding effect is real. A month-old agent with accumulated memory and tuned skills is dramatically more useful than a fresh install. That's why witcheer's 60 memory files were the most valuable part of their setup. Not the scripts. Not the cron jobs. The accumulated context.

## Bottom Line

The people getting the most out of AI agents right now aren't using them as chatbots. They're running them as services. Headless, scheduled, persistent, with structured memory that compounds over time.

The Mac Mini is just the hardware. The real infrastructure is the cron schedule that triggers work, the skills that define how to do it, and the memory system that makes every session smarter than the last.

Start with one skill, one cron job, one messaging channel. Run it for a week. Then build up. The people who try to deploy 18 cron jobs on day one are the same people who give up on day three.
