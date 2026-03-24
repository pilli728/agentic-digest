---
title: "The Scoring Algorithm: How We Rank 700+ Articles Without AI"
description: "The exact keyword lists, multipliers, and penalty system we use to score articles locally. No API key needed. Copy this for your own newsletter."
date: "2026-03-24"
tier: "founding"
category: "technical"
---

# The Scoring Algorithm

We score 700+ articles per batch without a single API call. Here's the exact system.

## How It Works

Every article gets a 0-10 score based on four keyword tiers, source multipliers, trending boosts, and penalty patterns. The whole thing runs in under 1 second on a laptop.

## Tier 1: Paradigm Shift Keywords (+2.0 each, max 8 points)

These signal fundamental changes in how AI work gets done:

```python
PARADIGM_SHIFT_SIGNAL = [
    "ai first", "ai-first", "before human", "replaces", "replacing",
    "fundamentally", "paradigm", "game changer", "disrupt",
    "transform", "revolution", "reimagin", "rethink", "new era",
    "without devops", "without engineers", "no-code", "zero-code",
    "autonomous", "self-driving", "self-healing", "self-improving",
    "solo founder", "one-person", "small team", "lean team",
    "without hiring", "replacing team", "ai employee",
    "6 engineers", "10 engineers", "no devops", "no ops",
    "competitor", "competes with", "alternative to", "vs ",
    "openclaw", "defenseclaw", "new player", "just launched",
    "stealth", "backed by", "raised", "funding round",
]
```

## Tier 2: Actionable Keywords (+1.0 each, max 6 points)

Things you can use or implement today:

```python
ACTIONABLE_SIGNAL = [
    "claude", "computer use", "claude code", "anthropic",
    "openai", "gpt-4", "gpt-5", "codex", "gemini",
    "openclaw", "mcp server", "model context protocol",
    "just released", "now available", "launching", "announces",
    "use case", "real-world", "in production", "case study",
    "we built", "how we", "how i", "our experience",
    "framework", "methodology", "playbook",
    "vibe coding", "coding agent", "pr review",
    "scale", "scaling", "growth", "revenue", "customers",
    "startup", "founder", "entrepreneur",
    "pricing", "cost", "cheaper", "faster", "efficient",
]
```

## Tier 3: Infrastructure Keywords (+0.3 each, max 2 points)

Important context but less immediately actionable:

```python
INFRA_SIGNAL = [
    "agent", "agentic", "langchain", "llamaindex", "crewai",
    "llm", "prompt engineer", "rag", "api", "sdk",
    "open source", "hugging face", "mistral", "llama",
    "deploy", "ship", "launch", "release", "production",
    "template", "tutorial", "guide", "how to",
]
```

## Penalties

### Research Paper Penalty
```python
RESEARCH_INDICATORS = [
    "arxiv", "we propose", "we present", "ablation study",
    "empirical", "theoretical", "in this paper",
    "markov", "bayesian", "stochastic",
]
# 3+ matches = 0.2x multiplier (80% reduction)
# 2 matches = 0.4x
# 1 match = 0.7x
```

### Skip Patterns (user-trained)
```python
SKIP_PATTERNS = [
    r"\bvllm\b", r"\bconcurrent request",
    r"\bbeginner\b", r"\bintroduction to\b",
    r"\bspeed up.*python\b",
]
# Matched articles score 0.5/10
```

## Source Multipliers

### Boosted Sources (user's preferred)
```python
SOURCE_BOOST = {
    "Vercel": 1.6, "SaaStr": 1.5, "Product Hunt": 1.5,
    "Anthropic": 1.5, "OpenAI": 1.5, "Claude": 1.5,
    "LangChain": 1.4, "Cursor": 1.5, "Latent Space": 1.4,
}
```

### Penalized Sources
```python
SOURCE_PENALTY = {
    "ArXiv": 0.4, "IEEE": 0.5, "ACM": 0.5,
    "KDnuggets": 0.7,
}
```

## Trending Boost

```python
# HN engagement
if points >= 500: score *= 1.8
elif points >= 200: score *= 1.5
elif points >= 100: score *= 1.3

# Tier bonus
tier_bonus = {0: 3.0, 1: 2.0, 2: 1.0, 3: 0.0, 4: 0.0}
```

## Tier 0 (curated newsletters) get +3.0 base bonus because they're already filtered by smart humans.

## Results

From 700+ articles per batch:
- ~200 filtered as noise (score 0)
- ~400 scored low (1-3)
- ~70 scored medium (4-6)
- ~30 scored high (7-10)
- **Top 20 shown to you**

The whole thing costs $0 to run.
