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
┌─────────────────────────────────────────────────────────┐
│                    FETCH LAYER                          │
│                                                         │
│  Layer 0: Curator Newsletters ──┐                      │
│    17 feeds, 15 articles each   │                      │
│    (80% of final content)       │                      │
│                                 ├──→ Raw Article Pool   │
│  Layer 1: Primary Sources ──────┤    (~200/day)        │
│    8 company blogs              │                      │
│    HN top 100 + 13 subreddits   │                      │
│    (15% of final content)       │                      │
│                                 │                      │
│  Layer 2: Background Sources ───┘                      │
│    21 niche feeds (weekly only)                        │
│    (5% of final content)                               │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                   FILTER LAYER                          │
│                                                         │
│  Step 1: Deduplication                                 │
│    URL normalization → SHA-256 hash → SQLite check     │
│                                                         │
│  Step 2: Blocklist (94 patterns)                       │
│    Kill: NixOS, FPGA, VPNs, beginner tutorials         │
│                                                         │
│  Step 3: Keyword Scoring (0-10)                        │
│    Paradigm shift +2.0 | Actionable +1.0               │
│    Infrastructure +0.3 | Research penalty 0.2x         │
│                                                         │
│  Step 4: Trending Boost                                │
│    HN 500+ pts = 1.8x | 200+ = 1.5x | 100+ = 1.3x   │
│                                                         │
│  Output: ~30 scored articles/day                       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                   OUTPUT LAYER                          │
│                                                         │
│  Claude API → Summaries (5 sentences each)             │
│  Markdown → Astro static site                          │
│  Resend API → Email delivery                           │
│  SQLite → Archive + dedup store                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Why This Works Better Than ChatGPT

ChatGPT can summarize articles you give it. Our system finds the articles worth summarizing. The difference is curation, not generation.

## The RSS Fetching Architecture

The fetcher uses a 3-layer system. Each layer has different fetch frequency and article limits.

### The Feed Parser

Here's the core fetching logic (simplified from our actual `fetcher.py`):

```python
import feedparser
from datetime import datetime, timedelta
from dateutil import parser as dateparser

MAX_ARTICLES_PER_FEED = 10
MAX_ARTICLES_TIER_ZERO = 15  # More from top curators

def _fetch_feeds(feeds: dict, lookback_hours: int, max_per_feed: int = 10):
    """Fetch articles from a set of feeds."""
    cutoff = datetime.now() - timedelta(hours=lookback_hours)
    all_articles = []

    for source_name, config in feeds.items():
        try:
            feed = feedparser.parse(config["url"])
            count = 0
            for entry in feed.entries:
                if count >= max_per_feed:
                    break

                # Parse date — feeds are inconsistent, so try multiple fields
                published = None
                for date_field in ["published_parsed", "updated_parsed"]:
                    if hasattr(entry, date_field) and getattr(entry, date_field):
                        published = datetime(*getattr(entry, date_field)[:6])
                        break

                # Fallback: parse date strings directly
                if not published:
                    for date_str_field in ["published", "updated"]:
                        if hasattr(entry, date_str_field):
                            try:
                                published = dateparser.parse(
                                    getattr(entry, date_str_field)
                                )
                                if published and published.tzinfo:
                                    published = published.replace(tzinfo=None)
                            except:
                                pass
                            break

                if published and published < cutoff:
                    continue

                title = entry.get("title", "Untitled")
                link = entry.get("link", "")
                summary = entry.get("summary", "")[:500]

                all_articles.append({
                    "source": source_name,
                    "tier": config["tier"],
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "published": published.isoformat() if published else "unknown",
                })
                count += 1

        except Exception as e:
            print(f"  [WARN] Failed to fetch {source_name}: {e}")

    return all_articles
```

Key decisions in this code:

1. **feedparser handles format hell for you.** RSS 0.9x, 1.0, 2.0, Atom 0.3, Atom 1.0, RDF. All normalized into the same structure. Don't try to parse XML yourself.
2. **Date parsing is a nightmare.** Feeds publish dates in dozens of formats. We try `published_parsed` first (feedparser's pre-parsed struct), then fall back to raw string parsing with `dateutil`. Some feeds have no dates at all.
3. **Truncate summaries to 500 chars.** Some RSS feeds dump the entire article body into `<description>`. You don't want 50KB entries clogging your pipeline.
4. **Fail silently per-feed.** One broken feed shouldn't kill the whole batch. Log the warning, move on.

### Making It Faster With Async

feedparser itself is synchronous. For 376 feeds, that's slow. The fix: use `aiohttp` for the HTTP fetch, then hand the response to feedparser for parsing.

```python
import aiohttp
import asyncio
import feedparser

async def fetch_feed_async(session, name, url):
    """Fetch one feed asynchronously, parse with feedparser."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            raw = await resp.text()
            return name, feedparser.parse(raw)
    except Exception as e:
        print(f"  [WARN] {name}: {e}")
        return name, None

async def fetch_all_feeds(feeds: dict):
    """Fetch all feeds concurrently. 376 feeds in ~8 seconds instead of ~90."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_feed_async(session, name, config["url"])
            for name, config in feeds.items()
        ]
        results = await asyncio.gather(*tasks)
        return {name: parsed for name, parsed in results if parsed}
```

This drops fetch time from ~90 seconds (sequential) to ~8 seconds (concurrent). We cap the timeout at 15 seconds per feed because some RSS endpoints are slow or dead.

## Deduplication Strategies

When you're pulling from 376 sources, the same story shows up 5-10 times. Here's how we handle it.

### Layer 1: URL Normalization

Before anything else, normalize the URL. Strip tracking params, force lowercase, remove trailing slashes.

```python
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Tracking params to strip
TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_content",
                   "utm_term", "ref", "source", "via"}

def normalize_url(url: str) -> str:
    """Strip tracking params, lowercase, remove trailing slash."""
    parsed = urlparse(url.lower().rstrip("/"))
    params = {k: v for k, v in parse_qs(parsed.query).items()
              if k not in TRACKING_PARAMS}
    clean = parsed._replace(query=urlencode(params, doseq=True))
    return urlunparse(clean)
```

### Layer 2: Content Hashing

Same article, different URL? Happens constantly with syndicated content. We hash the title + first 200 chars of the summary.

```python
import hashlib

def content_hash(title: str, summary: str) -> str:
    """SHA-256 of normalized title + summary prefix."""
    normalized = (title.lower().strip() + summary[:200].lower().strip())
    return hashlib.sha256(normalized.encode()).hexdigest()
```

### Layer 3: SQLite Dedup Store

Check both URL hash and content hash against the database before adding any article.

```python
# In SQLite: CREATE TABLE seen_articles (
#   url_hash TEXT PRIMARY KEY,
#   content_hash TEXT,
#   first_seen TEXT,
#   source TEXT
# );

def is_duplicate(db, url: str, title: str, summary: str) -> bool:
    url_h = hashlib.sha256(normalize_url(url).encode()).hexdigest()
    content_h = content_hash(title, summary)
    cursor = db.execute(
        "SELECT 1 FROM seen_articles WHERE url_hash = ? OR content_hash = ?",
        (url_h, content_h)
    )
    return cursor.fetchone() is not None
```

This three-layer approach catches 95%+ of duplicates. The remaining edge cases (same story, completely different headline, different source) get caught by the Claude scoring step later.

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

## Email Delivery: Resend vs SES vs SendGrid (2026)

We use Resend. Here's why, and what we considered.

### Resend (What We Use)

- **Free tier:** 3,000 emails/month, capped at 100/day
- **Paid:** ~$20/month for 50K emails
- **Overage:** $0.90 per 1,000 emails
- **Why we picked it:** API is dead simple. Three lines of Python. React Email templates if you want them. Built by ex-Vercel engineers who understand developer UX.
- **The catch:** Overage pricing is 9x more expensive than SES. Fine at newsletter scale (sub-50K). Bad if you're sending millions.

```python
import resend
resend.api_key = "re_xxxxx"

resend.Emails.send({
    "from": "digest@agenticedge.tech",
    "to": subscriber_email,
    "subject": subject_line,
    "html": html_content,
})
```

### Amazon SES

- **Free tier:** 3,000 emails/month for first 12 months (from EC2 only)
- **Paid:** $0.10 per 1,000 emails. Cheapest at scale by far.
- **Why we didn't pick it:** Setup takes 30+ minutes. You need to verify domains, request production access, handle bounce/complaint notifications via SNS. The API works but it's not fun.
- **When to switch:** If you pass 50K subscribers, SES saves you serious money. At 100K emails/month: ~$10 with SES vs ~$70 with Resend.

### SendGrid

- **Free tier:** Gone. SendGrid killed their free plan in May 2025. New accounts get a 60-day trial (100 emails/day), then it's $19.95/month minimum.
- **Why we didn't pick it:** The free tier removal burned a lot of indie developers. Documentation is bloated. The API has legacy cruft from 15 years of features.
- **Still good for:** Enterprise shops that need advanced analytics, A/B testing, and dedicated IP addresses.

### Our recommendation

Start with Resend. Switch to SES when you hit 50K subscribers. Don't bother with SendGrid unless you need marketing campaign features.

## Monitoring and Alerting

A newsletter that silently fails is worse than no newsletter. Here's what we monitor.

### Feed Health

- **Dead feeds:** Track HTTP status codes per feed. Three consecutive 4xx/5xx = flag for review. Some feeds die quietly (domain expires, blog moves).
- **Empty feeds:** A feed that returns 200 OK but zero new entries for 7+ days gets flagged.
- **Parse failures:** feedparser returns a `bozo` flag when it encounters malformed XML. Log these. Some feeds are permanently broken; some have temporary issues.

```python
feed = feedparser.parse(url)
if feed.bozo:
    log_warning(f"{source_name}: parse error - {feed.bozo_exception}")
```

### Delivery Monitoring

- **Bounce rate:** Keep it under 2%. Above that, email providers start throttling you. Resend's dashboard shows this in real time.
- **Complaint rate:** Gmail and Yahoo enforce strict compliance rules as of 2026. Stay under 0.1% complaint rate or you'll get blocklisted.
- **Open rate tracking:** Average newsletter open rate is ~35-45%. If yours drops below 20%, something is wrong (subject lines, send time, or deliverability issues).

### Pipeline Alerts

Set up basic alerting for:
1. **Fetch returned 0 articles** (feed infrastructure broken)
2. **Bounce rate > 2%** (email list hygiene problem)
3. **Score distribution shifted** (all articles scoring < 3 means your keywords need updating)
4. **Delivery latency > 5 minutes** (server overloaded or API rate-limited)

We use a simple Python script that runs after each pipeline execution and posts to a private Slack channel. No need for Datadog or PagerDuty at newsletter scale.

### Authentication (Non-Negotiable in 2026)

Gmail and Yahoo made these mandatory:
- **SPF record** on your domain
- **DKIM signing** for all outbound email
- **DMARC policy** set to at least `p=none` (monitoring mode)

Resend handles DKIM automatically. SPF and DMARC you configure in your DNS. Skip this and your emails go straight to spam.

## Cost (Updated March 2026)

**Zero-cost tier (what we run on):**
- RSS fetching: $0 (feedparser, free forever)
- HN API: $0 (public, no auth needed)
- Reddit RSS: $0 (public .rss endpoints, rate-limited)
- Keyword scoring: $0 (local Python, no API calls)
- Hosting: $0 (Vercel Hobby tier, non-commercial only)
- Email: $0 (Resend free tier, 3K emails/month)
- **Total: $0/month**

**With AI summaries:**
- Claude Haiku 3.5: ~$0.15/day for 30 article summaries
- Claude Sonnet 4.6: ~$0.50/day for 30 article summaries
- Prompt caching drops this 90% if you reuse system prompts

**With paid hosting (commercial use):**
- Vercel Pro: $20/month (required if you monetize)
- Railway Hobby: $5/month for the Python API (billed by actual CPU/memory usage, idle = near zero)
- Resend: $0-20/month depending on subscriber count
- **Total: $25-45/month**

**At scale (10K+ subscribers):**
- Vercel Pro: $20/month
- Railway Pro: $20/month
- SES: ~$1/month per 10K emails
- Claude API: ~$15/month with caching
- **Total: ~$60/month to run a real newsletter business**

## The Stack

- Python 3.11 + feedparser + aiohttp + SQLite
- Astro 4.12 (static site) on Vercel
- Resend for email delivery
- Stripe for paid tiers
- Railway for the Python API server
- No Docker, no Kubernetes, no message queues

One person can run this. That's the point.
