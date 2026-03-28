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

Separation of concerns. Your messy curation process stays private. Your readers see polished output. Netflix doesn't show you their recommendation algorithm. They show you movies.

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
3. Scan summaries. Each is 5 sentences
4. 📰 Add 8-12 articles to newsletter
5. Check preview on the right
6. Click Publish
7. Done. Total time: 5 minutes.

## The Feedback Collection API

Here's the actual API that handles rating events from the dashboard. Three endpoints, each does one thing.

### Endpoints

```python
# POST /api/feedback
# Records a single rating event

from http.server import BaseHTTPRequestHandler
import json
import sqlite3
from datetime import datetime, timezone

class FeedbackHandler:
    def handle_feedback(self, body: dict) -> dict:
        article_id = body["article_id"]
        action = body["action"]  # "like", "skip", or "add"
        digest_date = body.get("digest_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))

        if action not in ("like", "skip", "add"):
            return {"error": "action must be like, skip, or add"}, 400

        conn = sqlite3.connect("data/digest.db")
        conn.execute("""
            INSERT INTO feedback (article_id, action, digest_date, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(article_id, digest_date) DO UPDATE SET
                action = excluded.action,
                created_at = excluded.created_at
        """, (article_id, action, digest_date, datetime.now(timezone.utc).isoformat()))
        conn.commit()

        # Trigger async preference update
        self._update_preferences(conn, article_id, action)
        conn.close()

        return {"status": "ok", "article_id": article_id, "action": action}, 200

    def _update_preferences(self, conn, article_id: str, action: str):
        """Pull keywords and source from article, update preference weights."""
        row = conn.execute(
            "SELECT title, summary, source FROM articles WHERE id = ?",
            (article_id,)
        ).fetchone()
        if not row:
            return

        title, summary, source = row
        text = f"{title} {summary}".lower()

        # Update source preference
        delta = {"like": 0.05, "add": 0.1, "skip": -0.05}[action]
        conn.execute("""
            INSERT INTO source_preferences (source, weight, updated_at)
            VALUES (?, 1.0 + ?, ?)
            ON CONFLICT(source) DO UPDATE SET
                weight = MAX(0.1, MIN(3.0, weight + ?)),
                updated_at = ?
        """, (source, delta, datetime.now(timezone.utc).isoformat(),
              delta, datetime.now(timezone.utc).isoformat()))

        # Extract and update keyword signals
        words = set(text.split())
        signal = 1 if action in ("like", "add") else -1
        for word in words:
            if len(word) < 4:  # skip short words
                continue
            conn.execute("""
                INSERT INTO keyword_signals (keyword, score, hits, updated_at)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(keyword) DO UPDATE SET
                    score = score + ?,
                    hits = hits + 1,
                    updated_at = ?
            """, (word, signal, datetime.now(timezone.utc).isoformat(),
                  signal, datetime.now(timezone.utc).isoformat()))
        conn.commit()
```

```python
# GET /api/feedback/stats
# Returns aggregated feedback stats for the current digest

def handle_stats(self, digest_date: str) -> dict:
    conn = sqlite3.connect("data/digest.db")
    rows = conn.execute("""
        SELECT action, COUNT(*) FROM feedback
        WHERE digest_date = ?
        GROUP BY action
    """, (digest_date,)).fetchall()
    conn.close()

    stats = {r[0]: r[1] for r in rows}
    return {
        "digest_date": digest_date,
        "liked": stats.get("like", 0),
        "skipped": stats.get("skip", 0),
        "added": stats.get("add", 0),
        "total_rated": sum(stats.values()),
    }, 200
```

```python
# GET /api/preferences
# Returns current learned preferences (for debugging and transparency)

def handle_preferences(self) -> dict:
    conn = sqlite3.connect("data/digest.db")

    sources = conn.execute("""
        SELECT source, weight FROM source_preferences
        ORDER BY weight DESC LIMIT 20
    """).fetchall()

    top_keywords = conn.execute("""
        SELECT keyword, score FROM keyword_signals
        WHERE hits >= 3
        ORDER BY score DESC LIMIT 30
    """).fetchall()

    bottom_keywords = conn.execute("""
        SELECT keyword, score FROM keyword_signals
        WHERE hits >= 3
        ORDER BY score ASC LIMIT 20
    """).fetchall()

    conn.close()
    return {
        "boosted_sources": [{"source": s, "weight": round(w, 2)} for s, w in sources],
        "liked_topics": [{"keyword": k, "score": s} for k, s in top_keywords],
        "disliked_topics": [{"keyword": k, "score": s} for k, s in bottom_keywords],
    }, 200
```

## Data Model: SQLite Schema

Here's the full schema for the feedback and preference system. Five tables. No ORM. Just SQL.

```sql
-- Articles (populated by the fetcher)
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,              -- SHA256 of URL
    title TEXT NOT NULL,
    summary TEXT,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    published_at TEXT,
    hn_points INTEGER DEFAULT 0,
    tier INTEGER DEFAULT 3,
    score REAL DEFAULT 0.0,
    created_at TEXT NOT NULL
);

-- Feedback events from the dashboard
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT NOT NULL REFERENCES articles(id),
    action TEXT NOT NULL CHECK(action IN ('like', 'skip', 'add')),
    digest_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(article_id, digest_date)
);
CREATE INDEX idx_feedback_date ON feedback(digest_date);
CREATE INDEX idx_feedback_article ON feedback(article_id);

-- Learned source preferences
CREATE TABLE IF NOT EXISTS source_preferences (
    source TEXT PRIMARY KEY,
    weight REAL NOT NULL DEFAULT 1.0,  -- multiplier: 0.1 to 3.0
    updated_at TEXT NOT NULL
);

-- Learned keyword signals
CREATE TABLE IF NOT EXISTS keyword_signals (
    keyword TEXT PRIMARY KEY,
    score REAL NOT NULL DEFAULT 0.0,   -- positive = liked, negative = disliked
    hits INTEGER NOT NULL DEFAULT 0,   -- how many times we've seen this keyword rated
    updated_at TEXT NOT NULL
);

-- Published digests
CREATE TABLE IF NOT EXISTS digests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    digest_date TEXT NOT NULL UNIQUE,
    article_ids TEXT NOT NULL,          -- JSON array of article IDs
    markdown TEXT,                      -- generated newsletter content
    sent_at TEXT,                       -- null until email sent
    subscriber_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);
```

Why SQLite? It's a single file. Zero config. Handles 10,000+ articles without breaking a sweat. And you can copy the entire database to a new machine with `cp`. If you eventually need Postgres, the migration is straightforward because the schema is simple.

## The Preference Engine: Recency Weighting

Not all feedback is equal. Your tastes change. What you liked 3 months ago might bore you now. The preference engine weights recent ratings higher using exponential decay.

```python
import math
from datetime import datetime, timezone

def weighted_source_preference(conn, source: str, half_life_days: float = 21.0) -> float:
    """
    Calculate source preference weighted by recency.
    Ratings from 21 days ago count half as much as today's.
    """
    rows = conn.execute("""
        SELECT action, created_at FROM feedback f
        JOIN articles a ON f.article_id = a.id
        WHERE a.source = ?
        ORDER BY f.created_at DESC
        LIMIT 100
    """, (source,)).fetchall()

    if not rows:
        return 1.0  # neutral default

    now = datetime.now(timezone.utc)
    weighted_sum = 0.0
    weight_total = 0.0

    for action, created_at in rows:
        created = datetime.fromisoformat(created_at)
        age_days = (now - created).total_seconds() / 86400
        recency_weight = math.exp(-0.693 * age_days / half_life_days)

        action_value = {"like": 1.0, "add": 2.0, "skip": -1.0}[action]
        weighted_sum += action_value * recency_weight
        weight_total += recency_weight

    if weight_total == 0:
        return 1.0

    # Map weighted average (-2 to +2) to multiplier (0.3 to 2.0)
    avg = weighted_sum / weight_total
    multiplier = 1.0 + (avg * 0.5)  # -2 -> 0.0, 0 -> 1.0, +2 -> 2.0
    return max(0.3, min(2.0, multiplier))
```

Why 21-day half-life? Two reasons. First, newsletter topics shift fast. AI moves in weeks, not months. Second, if you start covering a new beat (say, you pivot from general AI to AI-in-healthcare), the system should adapt within a month, not six months.

The effect:

| Rating age | Weight |
|---|---|
| Today | 1.00 |
| 1 week ago | 0.78 |
| 2 weeks ago | 0.61 |
| 3 weeks (21 days) | 0.50 |
| 6 weeks | 0.25 |
| 3 months | 0.06 |

After 3 months, old ratings barely matter. This is intentional. If your taste was frozen in time, you wouldn't need a preference engine. You'd just use static keyword lists.

## Analytics: What to Track

Running a newsletter blind is like driving without a dashboard. Here's what to measure and what the numbers actually tell you.

### Tier 1: Must-Track (check daily)

| Metric | What It Tells You | Target |
|---|---|---|
| Open rate | Is your subject line working? | 40%+ (niche newsletters avg 41%) |
| Click rate | Is the content compelling? | 5-8% of opens |
| Unsubscribe rate | Are you annoying people? | Below 0.3% per send |
| Bounce rate | Is your list clean? | Below 2% |

### Tier 2: Growth Metrics (check weekly)

| Metric | What It Tells You | Target |
|---|---|---|
| New subscribers/week | Is your acquisition working? | Steady upward trend |
| Free-to-paid conversion | Is the paywall working? | 5-10% of free list |
| Paid churn/month | Are paid readers sticking? | Below 4% monthly |
| Revenue per subscriber | What's a subscriber worth? | $0.50-1.50/month blended |

### Tier 3: Content Intelligence (check after each issue)

| Metric | What It Tells You | Action |
|---|---|---|
| Click rate per article | Which stories resonate? | Boost similar content |
| Feedback rate (likes + skips) | Reader engagement depth | If < 5%, simplify the UI |
| Article-level open time | Deep reads vs skims | Long reads = topic interest |
| Category distribution of clicks | What topics win? | Adjust category min/max in scorer |

### Tracking Implementation

```python
# Store analytics events alongside feedback

CREATE TABLE IF NOT EXISTS analytics_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,  -- 'open', 'click', 'unsubscribe'
    subscriber_id TEXT,
    article_id TEXT,
    digest_date TEXT NOT NULL,
    metadata TEXT,             -- JSON blob for extra context
    created_at TEXT NOT NULL
);
CREATE INDEX idx_analytics_date ON analytics_events(digest_date);
CREATE INDEX idx_analytics_type ON analytics_events(event_type, digest_date);
```

```python
def weekly_report(conn, digest_date: str) -> dict:
    """Generate weekly analytics summary."""
    opens = conn.execute(
        "SELECT COUNT(DISTINCT subscriber_id) FROM analytics_events "
        "WHERE event_type = 'open' AND digest_date = ?", (digest_date,)
    ).fetchone()[0]

    total_sent = conn.execute(
        "SELECT subscriber_count FROM digests WHERE digest_date = ?", (digest_date,)
    ).fetchone()[0]

    clicks = conn.execute(
        "SELECT article_id, COUNT(*) as click_count FROM analytics_events "
        "WHERE event_type = 'click' AND digest_date = ? "
        "GROUP BY article_id ORDER BY click_count DESC", (digest_date,)
    ).fetchall()

    unsubs = conn.execute(
        "SELECT COUNT(*) FROM analytics_events "
        "WHERE event_type = 'unsubscribe' AND digest_date = ?", (digest_date,)
    ).fetchone()[0]

    open_rate = opens / total_sent if total_sent > 0 else 0
    unsub_rate = unsubs / total_sent if total_sent > 0 else 0

    return {
        "digest_date": digest_date,
        "sent": total_sent,
        "opens": opens,
        "open_rate": f"{open_rate:.1%}",
        "unsub_rate": f"{unsub_rate:.2%}",
        "top_articles": [{"id": a, "clicks": c} for a, c in clicks[:5]],
    }
```

### Feedback-to-Score Correlation

The most useful metric nobody tracks: do your feedback ratings predict reader clicks?

```python
def feedback_correlation(conn) -> float:
    """
    How well does your dashboard rating predict reader engagement?
    Returns Pearson correlation between article score and click count.
    Anything above 0.5 means the system is working.
    """
    rows = conn.execute("""
        SELECT a.score, COUNT(ae.id) as clicks
        FROM articles a
        JOIN analytics_events ae ON ae.article_id = a.id AND ae.event_type = 'click'
        GROUP BY a.id
        HAVING clicks > 0
    """).fetchall()

    if len(rows) < 10:
        return 0.0  # not enough data

    scores = [r[0] for r in rows]
    clicks = [r[1] for r in rows]
    # numpy-free Pearson correlation
    n = len(scores)
    mean_s = sum(scores) / n
    mean_c = sum(clicks) / n
    cov = sum((s - mean_s) * (c - mean_c) for s, c in zip(scores, clicks))
    std_s = (sum((s - mean_s)**2 for s in scores))**0.5
    std_c = (sum((c - mean_c)**2 for c in clicks))**0.5
    if std_s == 0 or std_c == 0:
        return 0.0
    return round(cov / (std_s * std_c), 3)
```

If the correlation is below 0.3, your scoring system and your readers disagree. Time to recalibrate.

## A/B Testing Newsletter Formats

You think you know what your readers want. You don't. Test it.

### What to Test

| Test | Variant A | Variant B | What You Learn |
|---|---|---|---|
| Article count | 10 articles | 20 articles | Do people prefer concise or comprehensive? |
| Summary length | 2 sentences | 5 sentences | How much context do readers need? |
| Subject line style | Descriptive ("AI News #47") | Curiosity ("The tool that killed Jira") | Open rate comparison |
| Send time | Friday 5pm | Monday 8am | When do people actually read? |
| Format | Bullet points | Paragraphs | Click-through differences |

### How to A/B Test with a Small List

You don't need 50,000 subscribers for meaningful tests. With 500 subscribers, you can detect a 5-percentage-point difference in open rates at 95% confidence. Here's how:

```python
import random
import hashlib

def assign_variant(subscriber_email: str, test_name: str) -> str:
    """
    Deterministic A/B assignment. Same email always gets same variant
    for the same test. No database needed.
    """
    hash_input = f"{subscriber_email}:{test_name}"
    hash_val = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
    return "A" if hash_val % 2 == 0 else "B"

def evaluate_test(conn, test_name: str, digest_date: str) -> dict:
    """Compare open/click rates between variants."""
    results = {}
    for variant in ("A", "B"):
        opens = conn.execute("""
            SELECT COUNT(DISTINCT subscriber_id) FROM analytics_events
            WHERE event_type = 'open' AND digest_date = ?
            AND subscriber_id IN (
                SELECT email FROM subscribers WHERE variant = ?
            )
        """, (digest_date, variant)).fetchone()[0]

        total = conn.execute("""
            SELECT COUNT(*) FROM subscribers WHERE variant = ?
        """, (variant,)).fetchone()[0]

        clicks = conn.execute("""
            SELECT COUNT(*) FROM analytics_events
            WHERE event_type = 'click' AND digest_date = ?
            AND subscriber_id IN (
                SELECT email FROM subscribers WHERE variant = ?
            )
        """, (digest_date, variant)).fetchone()[0]

        results[variant] = {
            "sent": total,
            "opens": opens,
            "open_rate": f"{opens/total:.1%}" if total > 0 else "0%",
            "clicks": clicks,
            "ctr": f"{clicks/opens:.1%}" if opens > 0 else "0%",
        }

    return {"test": test_name, "digest_date": digest_date, "results": results}
```

### Rules for Testing

1. **One variable at a time.** Don't change the subject line AND the article count in the same test.
2. **Run for 4 issues minimum.** One send is noise. Four sends is a pattern.
3. **50/50 split.** Don't get clever with 90/10 splits unless you have 10,000+ subscribers.
4. **Pick your winner metric before the test.** "Open rate" or "click rate" or "paid conversion." Not all three.
5. **Ship the winner.** Don't keep testing after you have a clear result. Move on to the next test.

## Progressive Automation

| Week | Manual Work | System Capability |
|---|---|---|
| 1-2 | Rate everything manually | Learning your preferences |
| 3-4 | Rate half, auto-skip obvious noise | Knows your source preferences |
| 5-8 | Spot-check top 20, publish | Can auto-curate 80% of content |
| 9+ | Review auto-generated newsletter | Full autonomous mode possible |

The goal: the system gets good enough that you just review and publish. No manual curation needed.
