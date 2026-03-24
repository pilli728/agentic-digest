---
title: "The Training Dashboard: How We Built a Feed That Learns From You"
description: "The two-website architecture, feedback loop, and preference engine that makes each newsletter better than the last."
date: "2026-03-24"
tier: "pro"
category: "playbook"
---

# The Training Dashboard

Most newsletters have one website. We have two.

## The Two-Site Architecture

### Site 1: Training Dashboard (Private — Just You)
- Shows ALL articles (not just the top 20)
- Rate them: 👍 Like, 👎 Skip, 📰 Add to Newsletter
- See live newsletter preview as you curate
- Click "Publish" when satisfied

### Site 2: Customer Website (Public — Your Readers)
- Only shows the published newsletter
- Free tier: top 5 stories
- Pro tier: all 20 stories + full analysis
- Founding tier: everything + 1:1 access

### Why Two Sites?

Separation of concerns. Your messy curation process stays private. Your readers see polished output. Netflix doesn't show you their recommendation algorithm — they show you movies.

## The Feedback Loop

```
Day 1: You rate 20 articles
  ↓
System learns: "User likes Vercel scaling stories, skips vLLM details"
  ↓
Day 2: Similar articles score higher automatically
  ↓
Day 7: Top 20 is 80% stuff you'd pick yourself
  ↓
Day 30: System can auto-generate newsletter without manual review
```

### What It Tracks

From your ratings:
- **Source preferences**: Which newsletters you trust (Vercel 1.6x, ArXiv 0.4x)
- **Topic signals**: Keywords from liked vs disliked articles
- **Tier preferences**: Approval rate per source category
- **Skip patterns**: vLLM, beginner content, academic papers

### Three Buttons, Three Purposes

| Button | Means | Affects Newsletter? |
|---|---|---|
| 👍 Like | "I find this relevant" — trains the scoring system | No |
| 👎 Skip | "Not for me" — penalizes similar content | No |
| 📰 Add to Newsletter | "Publish this one" — explicitly includes it | **Yes** |

Liking ≠ publishing. You might find an article interesting but not newsletter-worthy. The 📰 button is your editorial decision.

## The Newsletter Preview

The right panel of the dashboard shows a live preview of what your newsletter will look like. As you click 📰, articles appear in the preview. Remove them by clicking 📰 again.

When you're satisfied, click **Publish**. It:
1. Writes the digest to the Astro website
2. Sends email to all subscribers
3. Stores the digest in the database
4. Done. One click.

## The Daily Workflow

1. Open dashboard (5 min late in the week)
2. See top 20 articles (auto-fetched, auto-scored)
3. Scan summaries — each is 5 sentences
4. 📰 Add 8-12 articles to newsletter
5. Check preview on the right
6. Click Publish
7. Done. Total time: 5 minutes.

## Progressive Automation

| Week | Manual Work | System Capability |
|---|---|---|
| 1-2 | Rate everything manually | Learning your preferences |
| 3-4 | Rate half, auto-skip obvious noise | Knows your source preferences |
| 5-8 | Spot-check top 20, publish | Can auto-curate 80% of content |
| 9+ | Review auto-generated newsletter | Full autonomous mode possible |

The goal: the system gets good enough that you just review and publish. No manual curation needed.
