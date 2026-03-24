---
title: "Building an AI-Powered Newsletter From Scratch: The Complete Technical Playbook"
description: "How we built Agentic Edge — a newsletter that curates itself. 376 sources, keyword scoring, trending detection, zero API costs. Full architecture and code."
date: "2026-03-24"
tier: "pro"
category: "playbook"
---

# Building an AI-Powered Newsletter From Scratch

Most newsletters are manually curated. One person reads 200 articles, picks 10, writes summaries. That's 4-6 hours per issue.

We built a system that does this in 5 minutes. Here's exactly how.

## The Architecture

```
Layer 0: Top curator newsletters (80% of content)
  → Ben's Bites, Latent Space, a16z, The Leverage, etc.
  → These humans already filter 500+ articles/week for you

Layer 1: HN + Reddit trending (15%)
  → Real-time API scraping for breaking news
  → Engagement-weighted: 500+ HN points = 1.8x boost

Layer 2: 376 RSS sources (5% — weekly background)
  → Niche coverage the big newsletters miss
```

## Why This Works Better Than ChatGPT

ChatGPT can summarize articles you give it. Our system finds the articles worth summarizing. The difference is curation, not generation.

### The Scoring System

Every article gets a 0-10 score based on:

**Paradigm Shift Keywords (+2.0 each):** "without devops", "replaces", "fundamentally", "ai-first", "solo founder"

**Actionable Keywords (+1.0 each):** "mcp server", "just released", "we built", "tutorial", "plugin"

**Infrastructure Keywords (+0.3 each):** "agent", "langchain", "llm", "api", "framework"

**Research Penalty (0.2x multiplier):** "we propose", "ablation study", "in this paper"

**Trending Boost:** HN 500+ points = 1.8x, 200+ = 1.5x, 100+ = 1.3x

### The Noise Filter

94 articles auto-removed per batch. Patterns that kill an article:
- NixOS, FPGA, Wayland, password managers, VPNs
- Beginner tutorials ("speed up Python", "what is AI")
- Low-level infra details ("vLLM concurrent requests", "batch size optimization")
- Generic listicles ("10 best tools for beginners")

### The Writing Voice

Every summary follows these rules:
- No "delve", "landscape", "leverage", "synergy"
- Write like you're texting a smart friend
- Short sentences. Opinions. Specifics.
- 5 sentences: what it is, why it matters, what to do about it

## The Training Loop

You rate articles → system learns preferences → next batch is better.

After 20+ ratings, the system knows:
- Which sources you trust (Vercel 1.6x boost, a16z 1.5x)
- What you skip (vLLM details, beginner content)
- What excites you (paradigm shifts, scaling stories, unique use cases)

## Cost

- RSS fetching: $0 (feedparser, free)
- HN API: $0 (public, no auth)
- Reddit JSON: $0 (public, rate-limited)
- Keyword scoring: $0 (local Python)
- Hosting: $0 (Vercel free tier)
- **Total: $0/month to run**

Optional: Claude API for enhanced summaries = ~$0.50/day

## The Stack

- Python 3.9 + feedparser + SQLite
- Astro (static site) on Vercel
- Stripe for paid tiers
- Gmail for email delivery
- No frameworks, no Docker, no Kubernetes

One person can run this. That's the point.
