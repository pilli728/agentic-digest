---
title: "Karpathy: Explicit Memory Artifacts Beat Implicit AI Personalization"
description: "Implicit AI personalization is a black box. Karpathy argues your personal wiki beats it every time."
date: "2026-04-06"
tier: "free"
category: "analysis"
featured_free: true
---

**Implicit AI personalization is a black box. Karpathy argues your personal wiki beats it every time.**

Andrej Karpathy called out Farzapedia, a personal Wikipedia built by Farza, as the right model for LLM personalization. The core argument: an explicit, human-readable memory artifact that you own and control is architecturally superior to any "the AI learns you over time" approach that products like ChatGPT or Claude currently hand-wave about.

The distinction matters more than it sounds. Implicit personalization is opaque by design. You have no idea what the model thinks it knows about you, whether it's accurate, or when it's silently influencing your outputs. An explicit artifact solves all three problems at once.

## Why Explicit Memory Artifacts Win

A personal wiki is inspectable. You can read it, edit it, version-control it in Git, and feed it into any model you want. Your context is not locked to one vendor's memory layer. If Anthropic changes how Claude handles memories next quarter, your data doesn't get silently reshuffled.

Farzapedia demonstrates the pattern concretely: structured personal context in plain markdown that gets injected at prompt time. The model gets the same quality signal as implicit memory, but you stay in the loop. You know exactly what you're telling the model about yourself because you wrote it.

## What You Should Actually Build

Start a personal wiki today. Obsidian, Notion, or literally a folder of markdown files works. Structure it around the things you ask LLMs about most: your stack, your current projects, your decision-making defaults, your writing voice, key relationships and context.

Keep entries short and factual. Two to five sentences per topic. LLMs don't need prose, they need dense context. When you start a session, paste the relevant sections directly into your system prompt. This is more reliable than any memory feature any product ships right now, because you control the write path.

The compounding effect is real. A wiki you've been editing for 6 months contains better signal than 6 months of passive usage data, because you've curated it intentionally. Garbage in, garbage out applies to memory systems too. You know what's relevant. The model doesn't.

One practical move: review and update your wiki weekly. Treat it like a living document, not a one-time setup. The 10 minutes you spend pruning stale context pays back every time you start a new conversation without re-explaining your entire situation from scratch.

Karpathy's framing here is a clean architectural principle, not just a productivity tip. Explicit over implicit, portable over locked-in, human-readable over opaque. Apply that lens to every AI tooling decision you make.

[Source: @karpathy](https://x.com/karpathy/status/2040572272944324650)
