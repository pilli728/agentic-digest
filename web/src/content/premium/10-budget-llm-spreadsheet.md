---
title: "The Budget LLM Spreadsheet: One Model Switch. 87% Cost Reduction."
description: "The exact spreadsheet I use to compare LLM costs per task. Which models to use where, when to switch, and how I cut my API bill from $340/mo to $44/mo."
date: "2026-03-26"
tier: "founding"
category: "tool-drop"
---

I was spending $340 a month on API calls. Most of it was waste. I was routing every single request through Claude Sonnet because it was "good enough" and I didn't want to think about it.

That laziness cost me $296 every month.

## The Core Idea: Task Routing

Not every task needs a smart model. Classification? Summarization? Extracting structured data from a known format? A cheap model handles those just fine.

The expensive models — Opus, GPT-4o, Gemini Pro — should only touch the hard stuff. Agent orchestration. Complex code generation. Multi-step reasoning.

Everything else goes to the budget tier.

## The Actual Numbers

Here's what I'm paying per 1K tokens (input/output) as of March 2026:

**Budget Tier:**
- Claude Haiku: $0.25 / $1.25
- GPT-4o-mini: $0.15 / $0.60
- Gemini Flash: $0.075 / $0.30

**Mid Tier:**
- Claude Sonnet: $3.00 / $15.00
- GPT-4o: $2.50 / $10.00
- Gemini Pro: $1.25 / $5.00

**Heavy Tier:**
- Claude Opus: $15.00 / $75.00

The gap between tiers is massive. Haiku is 60x cheaper than Opus on output tokens. That matters when you're processing thousands of requests.

## My Task Routing Setup

This isn't complicated. It's an if/else.

```python
def route_model(task_type: str) -> str:
    budget_tasks = ["classify", "summarize", "extract", "format", "translate"]
    mid_tasks = ["code_gen", "analysis", "draft_writing", "code_review"]
    heavy_tasks = ["agent_orchestration", "complex_reasoning", "architecture"]

    if task_type in budget_tasks:
        return "claude-haiku"
    elif task_type in mid_tasks:
        return "claude-sonnet"
    elif task_type in heavy_tasks:
        return "claude-opus"
    return "claude-sonnet"  # default to mid
```

That's it. No fancy routing model. No classifier deciding which classifier to use. Just a map.

## The $340 → $44 Breakdown

Here's where my money was going before and after:

| Task | Before (Sonnet for all) | After (Routed) |
|------|------------------------|----------------|
| Email classification (2K/day) | $180/mo | $12/mo |
| Content summarization (500/day) | $75/mo | $8/mo |
| Code generation (50/day) | $45/mo | $45/mo (kept on Sonnet) |
| Agent tasks (20/day) | $40/mo | $40/mo (moved to Opus, fewer retries) |
| **Total** | **$340/mo** | **$44/mo** (after optimizing prompt lengths too) |

The classification work was the killer. Two thousand requests a day through Sonnet when Haiku handles it at 99.2% the same accuracy. I tested this. Ran 500 classification tasks through both models. Haiku got 496 right. Sonnet got 498. That two-request difference was costing me $168 a month.

## The Part Nobody Talks About

Prompt length matters more than model choice for cost. I was sending 800-token system prompts for simple classification tasks. Cut those to 120 tokens. That alone saved 30%.

Also: cache your system prompts. Anthropic and OpenAI both support prompt caching now. If you're sending the same system prompt repeatedly, you're paying full price for tokens the API has already processed.

## The Spreadsheet

I keep a live spreadsheet with three columns per task: model, avg tokens per request, monthly cost. I update it weekly. Takes five minutes. Saves hundreds.

The template is in the member resources. Duplicate it, plug in your own numbers, and watch where the money actually goes.

Stop paying Opus prices for Haiku work.
