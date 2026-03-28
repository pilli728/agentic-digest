---
title: "15 Claude Code Skills and GitHub Repos Worth Installing This Week"
description: "The skills, plugins, and repos that real developers are using with Claude Code right now. Tested, ranked, with install commands."
date: "2026-03-30"
tier: "pro"
category: "tool-drop"
---

The Claude Code skills ecosystem exploded this month. There are now thousands of skills floating around GitHub, and most of them are junk. Copy-paste prompt files with fancy READMEs.

I spent a week testing the ones people actually talk about. Here are 15 that are worth your time, sorted by how much they changed my workflow.

## The Big Three

These are the repos everyone should know about. If you install nothing else, install these.

### 1. obra/superpowers (93k+ stars)

This is the biggest Claude Code plugin by a mile. Jesse Vincent built a full development methodology as a skill. You don't just get code completion. You get a process: brainstorming, spec writing, planning, TDD, parallel sub-agents, code review. It asks you what you're trying to build before writing a single line.

I was skeptical. "A process framework? Just let me code." But after a week, my code reviews had 60% fewer issues. The spec step alone saves hours of rework.

It got accepted into the official Anthropic marketplace in January. Still gaining ~2,000 stars a day.

```bash
/plugin marketplace add obra/superpowers
/plugin install superpowers
```

### 2. thedotmack/claude-mem (38k+ stars)

Claude Code has built-in memory with CLAUDE.md files and auto-memory. But claude-mem goes further. It captures everything Claude does during your session, compresses it with AI, and injects relevant context into future sessions.

The difference is subtle at first. Then you realize Claude remembers that weird edge case from three days ago. It remembers that your auth service returns 403s instead of 401s. It remembers that you hate ternaries.

The search is the killer feature. It uses a 3-layer system: search, timeline, and get_observations. You can ask "what did we decide about the database schema?" and get an actual answer.

```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

Don't use `npm install -g claude-mem`. That installs the SDK only, not the plugin hooks.

### 3. nextlevelbuilder/ui-ux-pro-max-skill (52k+ stars)

This one surprised me. It's a searchable database of UI styles, color palettes, font pairings, and UX guidelines that Claude queries while building your frontend.

The numbers: 57 UI styles, 95 color palettes, 56 font combinations, 98 UX best practice guidelines, 25 chart types across 9 tech stacks. It covers glassmorphism, brutalism, neumorphism, bento grid, dark mode, you name it.

Before this skill, I'd tell Claude "make it look good" and get generic Bootstrap vibes. Now I say "glassmorphism with the Stripe color palette" and get something I'd actually ship.

```bash
uipro init --ai claude
```

Or clone it directly:

```bash
git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git
```

## The Website Cloner

### 4. JCodesMore/ai-website-cloner-template (1.3k stars)

Everyone tries to clone websites by screenshotting them and feeding the image to an AI. That gets you maybe 50% of the way there. Wrong fonts, wrong spacing, fake animations.

This skill does it differently. It directs Claude Code's Chrome MCP to the actual live site. It reads the DOM. Grabs design tokens. Pulls assets. Writes component specs. Then it spins up parallel builder agents to rebuild every section in isolated git worktrees that auto-merge when done.

Point it at any URL. Type `/clone-website`. Walk away. Come back to a pixel-perfect Next.js clone with TypeScript, shadcn/ui, and Tailwind v4.

```bash
git clone https://github.com/JCodesMore/ai-website-cloner-template.git my-clone
cd my-clone && npm install
```

Not the most starred repo on this list, but the one that made my jaw drop.

## The Content Machine

### 5. mvanhorn/last30days-skill (3.8k stars)

This skill scans Reddit, X, YouTube, Hacker News, Polymarket, and the broader web from the last 30 days on any topic you give it. Then it synthesizes everything into a grounded summary with real citations.

I've been using it for newsletter research. Instead of spending 3 hours scrolling Reddit and X for what people actually think about a topic, I type:

```
/last30days Claude Code skills and plugins March 2026
```

And get a structured brief with real quotes, real upvote counts, real engagement data. It finds what communities are actually sharing, betting on, and arguing about.

No API keys needed. No npm install. Just clone and go.

```bash
git clone https://github.com/mvanhorn/last30days-skill.git ~/.claude/skills/last30days
```

## Not a Skill, But You Need to Know About It

### 6. paperclipai/paperclip (30k+ stars)

Greg Isenberg sat down with Dotta (the pseudonymous founder) and walked through a live demo. They spun up an AI-agent company in real time. CEO agent. Founding engineer agent. QA agent. Content strategist. All coordinated.

Paperclip is a Node.js server and React dashboard that orchestrates AI agents like employees. You give them roles, goals, and budgets. They report progress. It has org charts, governance, goal alignment, and cost tracking.

It's not a Claude Code skill. It's an orchestration layer. But it hit 30k stars in under three weeks, and the overlap between "people who use Claude Code" and "people experimenting with Paperclip" is basically a circle.

Self-hosted. MIT license. No account needed.

```bash
npx paperclipai onboard --yes
```

Needs Node.js 20+ and pnpm 9.15+. PostgreSQL spins up automatically.

## The Curated Collections

If you want to browse skills instead of installing specific ones, these are your starting points.

### 7. ComposioHQ/awesome-claude-skills (44k+ stars)

The biggest curated list. This is where you go when you need Claude to actually do things: automate workflows, connect to external services, handle multi-step processes. Good categorization. Active community.

### 8. travisvn/awesome-claude-skills (9k+ stars)

Smaller but more curated. Travis focuses on battle-tested skills only. 20+ skills covering TDD, debugging, and collaboration patterns. Less noise than the bigger lists.

### 9. VoltAgent/awesome-agent-skills (11k+ stars)

This one stands out because it includes official skills from Anthropic, Google Labs, Vercel, Stripe, Cloudflare, Netlify, Sentry, Figma, and others. If you want to know what the platform teams themselves are publishing, start here.

### 10. alirezarezvani/claude-skills (5.2k stars)

192+ skills across 9 domains. The twist: every skill works with Claude Code, Codex, Gemini CLI, Cursor, and 8 other coding agents. 268 Python automation tools. No external dependencies. All standard library.

If you use multiple AI coding tools, this is the only cross-compatible collection I've found.

```bash
git clone https://github.com/alirezarezvani/claude-skills.git ~/.claude/skills/alireza
```

## The Official Stuff

### 11. anthropics/skills

Anthropic's own public skills repo. Not the flashiest. Not the most starred. But it's the reference implementation for how skills should be built.

Includes the document creation skills (docx, pdf, pptx, xlsx) that power Claude's built-in document features. These are source-available, not fully open source, but you can read them to understand how production skills work.

```bash
/plugin install document-skills@anthropic-agent-skills
```

## The Specialists

### 12. xBenJamminx/x-research-skill

X/Twitter research skill. Agentic search, thread following, deep-dives, sourced briefings. If you're building content around what's happening on X, this is more targeted than the last30days skill.

### 13. daymade/claude-code-skills (twitter-reader)

A focused Twitter/X reader skill. Less ambitious than the research skill above, but faster for quick scans. Good for pulling specific threads into your context.

### 14. yusufkaraaslan/Skill_Seekers

This one converts documentation websites, GitHub repos, and PDFs into Claude AI skills with automatic conflict detection. Instead of manually writing SKILL.md files, point it at a docs site and get a working skill back.

If you're building your own skills, this cuts the setup time in half.

### 15. sickn33/antigravity-awesome-skills

1,326+ agentic skills. The biggest single library. Includes an installer CLI, bundles, and workflows. Covers Claude Code, Cursor, Codex CLI, Gemini CLI, and Antigravity.

Honestly, the volume is overwhelming. But if you need a skill for something obscure (HIPAA compliance review? Financial analyst reports? Cold email writing?), it's probably in here somewhere.

## How to Actually Install Skills

If you're new to this, here's the quick version.

**Method 1: Plugin marketplace (easiest)**

```bash
/plugin marketplace add [owner/repo]
/plugin install [skill-name]
```

**Method 2: Clone to your skills directory**

```bash
git clone https://github.com/[owner/repo].git ~/.claude/skills/[name]
```

**Method 3: Copy the SKILL.md directly**

Find the SKILL.md file in any repo. Copy its contents into `.claude/skills/[name]/SKILL.md` in your project. Claude discovers it automatically.

## My Current Stack

After testing all of these, here's what I actually kept installed:

1. **superpowers** for the development methodology
2. **claude-mem** for session memory
3. **ui-ux-pro-max** for frontend work
4. **last30days** for research
5. **ai-website-cloner** for reference implementations

Everything else I install on a per-project basis. The curated lists (ComposioHQ, VoltAgent) are bookmarked for when I need something specific.

The skills ecosystem is moving fast. Three months ago, most of these repos didn't exist. By next month, half of them will be outdated. That's the game right now. Install what works, drop what doesn't, keep moving.
