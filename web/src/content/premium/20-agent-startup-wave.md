---
title: "The Agent Startup Wave: Ghostwriter, Glimpse, ARC-AGI-3, and What's Next"
description: "Sierra's agent builder, Glimpse's $35M raise, the benchmark that humbles every AI, and the GitHub repos blowing up. The agent economy just shifted."
date: "2026-03-30"
tier: "pro"
category: "playbook"
---

# The Agent Startup Wave of March 2026

Five things happened this week that, taken together, paint a clear picture: the agent economy just went from "interesting research direction" to "real companies shipping real products for real money."

Here's what happened, why each one matters, and what builders should do about it.

---

## 1. Sierra Released Ghostwriter: An Agent That Builds Agents

On March 25, Bret Taylor's Sierra dropped [Ghostwriter](https://sierra.ai/blog/agents-as-a-service), a tool that lets you build production-grade customer service agents by having a conversation in plain English.

**What it does:** You upload your SOPs, support transcripts, process docs, even photos of whiteboard sketches. Ghostwriter reads all of it, identifies key behaviors and edge cases, and spits out a production-ready agent that works across voice, chat, email, and 30+ languages. No code required.

**The interesting part:** Ghostwriter includes a tool called Explorer that works like Deep Research but for your own customer conversations. It crawls your interaction data, finds where your agents are underperforming, and proposes fixes. Then it validates those fixes in a sandbox before shipping them. Sierra calls this the "agent assembly line." The agent improves itself continuously without anyone touching it.

**Why it matters:** Sierra hit $100M ARR in under two years. They're valued at $10B after raising $350M in September 2025. Their clients include ADT, Nordstrom, Rivian, SiriusXM, and Nubank. When a company this size says "agents, not clicks," the enterprise market listens.

The pricing model is the real signal though. Sierra charges per outcome, not per seat. You pay when the agent actually resolves a customer issue. That's a fundamentally different business model from traditional SaaS, and it aligns incentives in a way that seat-based pricing never did.

**For builders:** If you're building customer-facing agents, study Ghostwriter's architecture. The "agent harness" concept (scaffolding that includes tools, memory, action space, and reasoning) is a pattern you can replicate. Sierra rearchitected their platform as headless infrastructure so agents could use it directly. That's the direction.

---

## 2. Glimpse Raised $35M to Automate the Boringest Problem in Retail

[Glimpse](https://techcrunch.com/2026/03/25/a16z-backed-glimpse-raises-new-funds-accelerates-dispute-tracking-automation-for-cpg-brands/) announced a $35M Series A led by a16z, with YC and 8VC also in. Total raised: $52M.

**The founders:** Akash Raju, Anuj Mehta, and Kushal Negi went to Purdue together. They started in 2020 building Airbnb product placements. Then they pivoted. Hard.

**What Glimpse actually does:** When Walmart or Target pays a CPG brand less than what they owe (which happens constantly, through deductions for co-op advertising, logistics charges, damaged goods, etc.), brands historically had to manually sift through retailer portals to find and dispute the invalid deductions. It's miserable work. Most companies just eat the losses.

Glimpse built AI agents that log into retailer portals, find all the relevant documents, classify each deduction, cross-reference against internal records (supply chain data, promotion calendars), and file disputes automatically. The agents do the whole workflow end-to-end.

**The numbers:** 200+ retail brands using it. Clients include Suave, Chapstick, Lemon Perfect, IQBar. 14x year-over-year growth.

**Why it matters:** This is the boring-but-lucrative playbook for agent startups. Nobody posts "automated retail deduction disputes" on Twitter for clout. But CPG brands lose billions annually to invalid deductions. Glimpse found a painful workflow, replaced it with agents, and grew 14x in a year. That's the template.

**For builders:** The best agent startup ideas right now aren't sexy. They're the ones where someone currently has 15 browser tabs open, copying data between systems, making decisions based on cross-referencing documents. Find that person. Build the agent.

---

## 3. ARC-AGI-3 Dropped and It Humbles Everything

Francois Chollet and Mike Knoop (Zapier co-founder) launched [ARC-AGI-3](https://arcprize.org/blog/arc-agi-3-launch) on March 25 at YC HQ, with a fireside chat between Chollet and Sam Altman.

**What it is:** Hundreds of interactive turn-based environments. Each one is handcrafted by human game designers. No instructions. No rules. No stated goals. The AI agent has to explore each environment on its own, figure out how it works, discover what winning looks like, and carry what it learns forward across increasingly difficult levels.

**The gap:** Humans score 100%. Frontier AI scores 0.26%.

Read that again. Not 26%. 0.26%.

**Why it's different from ARC-AGI-2:** The first two versions tested static reasoning (look at a grid, figure out the pattern). Version 3 is fully interactive. The agent has to take actions, observe consequences, build a mental model, and adapt. It's testing the gap between "AI that follows instructions" and "AI that genuinely explores and learns in unfamiliar situations."

**The prize:** Over $2M for ARC Prize 2026, running on Kaggle.

**Why builders should care:** ARC-AGI-3 is the canary in the coal mine for agent capability. Right now, every agent framework assumes the agent knows what it's trying to do. Someone gives it a goal, it plans, it executes. But real-world environments are messy. Sometimes you don't know the rules. Sometimes the goal isn't clear. ARC-AGI-3 tests exactly that, and current AI is essentially at zero.

This means the next big unlock in agent capability isn't better reasoning or more tools. It's better exploration. Agents that can poke at unfamiliar systems, notice patterns, and build understanding from scratch. If you're building agents that operate in dynamic environments, this benchmark is your north star.

---

## 4. Agency-Agents Hit 64K Stars on GitHub

A repo called [agency-agents](https://github.com/msitarzewski/agency-agents) went from zero to 10K stars in a week, and is now sitting at 64.3K stars with 9.7K forks.

**What it is:** 140+ specialized AI agent definitions organized across 13 divisions: Engineering, Design, Paid Media, Sales, Marketing, Product, Project Management, Testing, Support, Spatial Computing, Game Development, Academic, and more.

Each agent isn't just a prompt template. It's a full personality with a communication style, specialized workflows, success metrics, and deliverables. There's a Frontend Wizard, a Reddit Community Ninja, a Growth Hacker, a Brand Guardian, a "Whimsy Injector" (I'm not making this up), and an XR Interface Architect.

**How it works:** You copy agent definitions into Claude Code, Cursor, Aider, Windsurf, Gemini CLI, or whatever tool you're using. The repo includes automated scripts for each platform. Then you deploy multiple agents simultaneously. There's a demo called the "Nexus Spatial Discovery Exercise" where 8 agents (Product Trend Researcher, Backend Architect, Brand Guardian, Growth Hacker, Support Responder, UX Researcher, Project Shepherd, XR Interface Architect) evaluate a software opportunity and produce a unified product plan.

**Origin story:** It started as a Reddit post. 50+ people asked for it within the first 12 hours. The creator (msitarzewski) iterated on it for months based on community feedback before it blew up.

**Why it matters:** Two reasons. First, it validates that the "specialized agent with personality" pattern works better than generic prompts. People aren't just starring this repo. They're forking it and using it. 9.7K forks is real adoption.

Second, it shows what "prompt engineering" has become. This isn't "please be a helpful assistant." These are multi-page agent specifications with domains, workflows, tone, and measurable outputs. The gap between a generic agent and a specialized one is enormous, and this repo proves it at scale.

**For builders:** Browse the agent definitions. Seriously. Even if you don't use them directly, the structure is worth studying. The best ones define: who the agent is, what it does, how it communicates, what it delivers, and how success is measured. That's a template for any agent you build.

---

## 5. Meta's HyperAgents Paper Shows Self-Improvement Actually Working

Meta Superintelligence Labs (with UBC, Edinburgh, and NYU) published [HyperAgents](https://arxiv.org/abs/2603.19461) in March 2026. This is the self-improving agents paper that @omarsar0 flagged on Twitter.

**The problem:** Most self-improving AI systems hit the same wall. They can optimize for a specific task, but the optimization strategy itself doesn't get better over time. You improve at chess but you don't improve at improving.

**What HyperAgents does:** It merges the task agent (which solves problems) and the meta agent (which improves the task agent) into a single editable Python program. The agent modifies its own source code, tests the new version against benchmarks, and keeps successful variants in an archive. The meta agent logic is just another function in the same file, and it can rewrite itself.

**The results:** On a polyglot coding benchmark, pass rate went from 14% to 34% on training tasks. On held-out test problems, 8.4% to 26.7%. That's roughly 3x improvement through self-modification alone.

But here's the wild part: when they transferred meta agents from human-customized approaches to Olympiad-level math grading, those transferred agents achieved 0.0 improvement. Zero. The HyperAgents, transferred to the same math task, achieved 0.630. The self-improvement strategies themselves were transferable across domains. The hand-designed ones weren't.

**Emergent behavior:** Without being told to, HyperAgents built their own performance tracking classes and persistent memory with timestamped storage. They invented their own engineering tools to make themselves better at self-improvement.

**Why builders should care:** This is early, and the code is released under a non-commercial Creative Commons license so you can't ship it in a product. But the pattern is what matters: collapse the optimization loop and the task loop into the same program. Let the agent modify both what it does and how it improves. Current agent frameworks keep these completely separate. That's going to change.

---

## The Bigger Picture

Here's what these five signals add up to:

**The agent layer is crystallizing.** Sierra is the enterprise play (agents for customer experience). Glimpse is the vertical SaaS play (agents for a specific painful workflow). Agency-agents is the open-source community play (agent templates for everyone). ARC-AGI-3 is the benchmark that tells us where the ceiling is. And HyperAgents is the research frontier showing where things go next.

**The money is real.** Sierra at $10B valuation. Glimpse at $35M Series A with a16z leading. ARC Prize at $2M+. These aren't research experiments anymore.

**The gap between "can follow instructions" and "can figure things out" is the next frontier.** ARC-AGI-3 makes this painfully clear with its 0.26% score. Current agents are sophisticated instruction-followers. The next generation needs to be genuine explorers. That's a hard problem, and whoever cracks it will have the most valuable technology in the world.

**Three things to do this week:**

1. **Try Ghostwriter** if you have any customer-facing workflow. Even if you don't ship it, the UX of "describe what you want and get a working agent" is where everything is heading.
2. **Browse agency-agents** and steal the agent definition structure. Apply it to your own agents. Personality + workflow + metrics beats a generic system prompt every time.
3. **Look at ARC-AGI-3's tasks** at [arcprize.org/tasks/ls20](https://arcprize.org/tasks/ls20). Play a few games yourself. Then try to imagine building an agent that can do what you just did. That gap is the opportunity.

The agent startup wave isn't coming. It's here. The question is whether you're building on it or watching it.
