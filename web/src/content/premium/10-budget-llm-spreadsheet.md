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

The expensive models should only touch the hard stuff. Agent orchestration. Complex code generation. Multi-step reasoning.

Everything else goes to the budget tier.

## The Actual Numbers (March 2026)

Here's what I'm paying per 1M tokens (input/output):

**Budget Tier:**
| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| Gemini 2.5 Flash-Lite | $0.10 | $0.40 | Cheapest quality option |
| GPT-4o-mini | $0.15 | $0.60 | Solid all-rounder |
| Gemini 2.5 Flash | $0.15 | $0.60 | Best value for reasoning |
| DeepSeek V3.2 | $0.28 | $0.42 | Absurdly cheap, surprisingly good |
| Claude Haiku 4.5 | $1.00 | $5.00 | Best cheap Claude |

**Mid Tier:**
| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| GPT-4o | $2.50 | $10.00 | Reliable workhorse |
| Claude Sonnet 4.6 | $3.00 | $15.00 | My default for code |
| Gemini 3 Flash | $0.50 | $3.00 | Fast and cheap mid-tier |

**Heavy Tier:**
| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| Claude Opus 4.6 | $5.00 | $25.00 | Best reasoning. 66% cheaper than Opus 4 was |
| Gemini 3.1 Pro | $2.00-$4.00 | $12.00-$18.00 | Google's flagship |

Big news since last year: Opus got way cheaper. Opus 4 used to cost $15/$75. Opus 4.6 costs $5/$25. That's a 66% price drop. The heavy tier is actually affordable now.

And DeepSeek is the wild card. At $0.28/$0.42, it's 95% cheaper than GPT-4o. Quality varies by task, but for classification and extraction it's shockingly competent.

## My Task Routing Setup

This isn't complicated. It's an if/else.

```python
def route_model(task_type: str) -> str:
    budget_tasks = ["classify", "summarize", "extract", "format", "translate"]
    mid_tasks = ["code_gen", "analysis", "draft_writing", "code_review"]
    heavy_tasks = ["agent_orchestration", "complex_reasoning", "architecture"]

    if task_type in budget_tasks:
        return "claude-haiku-4.5"
    elif task_type in mid_tasks:
        return "claude-sonnet-4.6"
    elif task_type in heavy_tasks:
        return "claude-opus-4.6"
    return "claude-sonnet-4.6"  # default to mid
```

That's it. No fancy routing model. No classifier deciding which classifier to use. Just a map.

## Decision Tree for Model Selection

When I'm deciding which model to use for a new task, I run through this:

1. **Does it need to be real-time?** If no, use the Batch API (50% off everything). Skip to step 2 with batch pricing.
2. **Does it need reasoning?** If yes, go mid or heavy tier. If no, budget tier.
3. **Is accuracy above 95% critical?** If yes, mid tier minimum. Test budget tier first though. You'll be surprised.
4. **Is it a repeating task with the same system prompt?** If yes, enable prompt caching (90% input savings). This changes the math dramatically.
5. **Volume over 10K requests/day?** Budget tier. Period. Even 1% accuracy loss is worth the 10-50x cost reduction.
6. **Code generation or complex editing?** Claude Sonnet 4.6 or Opus 4.6. They're just better at code than the alternatives right now.
7. **Simple extraction or classification?** DeepSeek V3.2 or Gemini Flash-Lite. Save your money for the hard stuff.

## The $340 to $44 Breakdown

Here's where my money was going before and after:

| Task | Before (Sonnet for all) | After (Routed) |
|------|------------------------|----------------|
| Email classification (2K/day) | $180/mo | $12/mo |
| Content summarization (500/day) | $75/mo | $8/mo |
| Code generation (50/day) | $45/mo | $45/mo (kept on Sonnet) |
| Agent tasks (20/day) | $40/mo | $40/mo (moved to Opus, fewer retries) |
| **Total** | **$340/mo** | **$44/mo** (after optimizing prompt lengths too) |

The classification work was the killer. Two thousand requests a day through Sonnet when Haiku handles it at 99.2% the same accuracy. I tested this. Ran 500 classification tasks through both models. Haiku got 496 right. Sonnet got 498. That two-request difference was costing me $168 a month.

## Prompt Caching: The Biggest Cost Lever Nobody Uses

If you're sending the same system prompt on every request and not caching it, you're lighting money on fire.

**How it works:** The API stores the computed key-value matrices from your prompt for 5-10 minutes. If your next request starts with the same prefix, it reuses those cached computations instead of reprocessing them.

**Anthropic's approach:** You set up to 4 cache breakpoints using the `cache_control` parameter. Writing to the cache costs 25% MORE than normal input tokens. But reading from cache costs 90% LESS. So if you send the same system prompt 10+ times, you save a ton.

```python
# Anthropic prompt caching example
response = client.messages.create(
    model="claude-sonnet-4-6-20260321",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "Your long system prompt here...",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": "Classify this email..."}]
)
```

**OpenAI's approach:** It's automatic. No configuration needed. OpenAI detects matching prefixes and caches them for you. You get 50% off cached input tokens. Less savings than Anthropic, but zero effort.

**The math:** Say your system prompt is 2,000 tokens and you send 1,000 requests/day.
- Without caching: 2M input tokens/day = $6/day on Sonnet
- With Anthropic caching: First request full price, rest at 90% off = $0.63/day
- Savings: ~$160/month just from caching

Minimum prompt length for caching: 1,024 tokens on Anthropic, 128 tokens on OpenAI. If your system prompt is shorter than that, caching won't kick in.

## Batch API: 50% Off for Non-Urgent Work

Every major provider now offers a Batch API. You submit a bunch of requests, they process them within 24 hours, and you pay half price.

- **Anthropic Message Batches:** 50% off all models
- **OpenAI Batch API:** 50% off all models
- **Google Batch:** 50% off

This is perfect for: content generation pipelines, document classification, data extraction, report generation, bulk analysis. Anything where you don't need the answer in 200ms.

**Stacking discounts:** Prompt caching + batch = up to 95% savings. On Anthropic, a cached batch request to Sonnet costs roughly $0.15/$7.50 per million tokens. Compare that to the standard $3/$15. That's real money.

```python
# Anthropic batch example
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"req_{i}",
            "params": {
                "model": "claude-haiku-4-5-20260321",
                "max_tokens": 256,
                "messages": [{"role": "user", "content": text}]
            }
        }
        for i, text in enumerate(texts_to_classify)
    ]
)
# Poll for results or use webhook
```

## Token Counting: Know What You're Spending Before You Spend It

You can't optimize what you don't measure. Here's how to count tokens before sending requests.

**For OpenAI models:**
```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")
token_count = len(enc.encode("your text here"))
```

**For Anthropic models:**
```python
# Use the API's built-in counter (most accurate)
count = client.messages.count_tokens(
    model="claude-sonnet-4-6-20260321",
    messages=[{"role": "user", "content": "your text here"}]
)
print(count.input_tokens)
```

Anthropic's tokenizer is NOT compatible with tiktoken. Don't use tiktoken to estimate Claude costs. Use their API endpoint or their official `anthropic-tokenizer-typescript` package for JS projects.

**For quick estimates across models:** LiteLLM has built-in token counting that works with OpenAI, Anthropic, Cohere, and Llama models. One library, all providers.

**Pro tip:** I log every request's token count and model to a SQLite database. Weekly, I run a query to see cost-per-task. Takes 5 minutes to review. That's how I caught the classification waste in the first place.

## The Spreadsheet

I keep a live spreadsheet with these columns per task: model, avg input tokens, avg output tokens, requests/day, monthly cost, cached (y/n), batched (y/n). I update it weekly.

The template is in the member resources. Duplicate it, plug in your own numbers, and watch where the money actually goes.

Stop paying Opus prices for Haiku work. And for the love of your bank account, turn on prompt caching.
