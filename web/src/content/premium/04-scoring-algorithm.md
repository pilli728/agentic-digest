---
title: "The Scoring Algorithm: How We Rank 700+ Articles Without AI"
description: "The exact keyword lists, multipliers, and penalty system we use to score articles locally. No API key needed. Copy this for your own newsletter."
date: "2026-03-24"
tier: "founding"
category: "technical"
---

# The Scoring Algorithm

We score 700+ articles per batch without a single API call. Here's the exact system, from keyword matching to semantic embeddings to freshness decay.

## How It Works

Every article gets a 0-10 score based on six signals: keyword tiers, source multipliers, trending boosts, category tagging, freshness decay, and (optionally) semantic embedding similarity. The keyword-only pipeline runs in under 1 second on a laptop. Adding embeddings bumps that to about 4 seconds on a MacBook M-series with no GPU.

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

Tier 0 (curated newsletters) get +3.0 base bonus because they're already filtered by smart humans.

## Category-Based Scoring

Not all articles compete in the same pool. We tag each article into a category and apply per-category score adjustments. This prevents "startup funding" articles from always beating "open source tool release" articles just because funding stories have splashier keywords.

```python
CATEGORY_RULES = {
    "product_launch": {
        "signals": ["just launched", "now available", "announcing", "introduces"],
        "boost": 1.3,
        "min_per_digest": 2,   # always include at least 2
        "max_per_digest": 5,
    },
    "founder_story": {
        "signals": ["we built", "how we", "our experience", "solo founder", "bootstrapped"],
        "boost": 1.2,
        "min_per_digest": 1,
        "max_per_digest": 3,
    },
    "funding_news": {
        "signals": ["raised", "series a", "series b", "funding round", "backed by"],
        "boost": 1.0,          # no boost, just capped
        "min_per_digest": 0,
        "max_per_digest": 2,   # don't let funding stories dominate
    },
    "tutorial": {
        "signals": ["how to", "tutorial", "step by step", "guide", "walkthrough"],
        "boost": 1.1,
        "min_per_digest": 2,
        "max_per_digest": 4,
    },
    "opinion": {
        "signals": ["i think", "unpopular opinion", "hot take", "controversial"],
        "boost": 1.15,
        "min_per_digest": 1,
        "max_per_digest": 3,
    },
}

def categorize_article(title: str, summary: str) -> str:
    text = f"{title} {summary}".lower()
    best_cat, best_count = "general", 0
    for cat, rules in CATEGORY_RULES.items():
        hits = sum(1 for s in rules["signals"] if s in text)
        if hits > best_count:
            best_cat, best_count = cat, hits
    return best_cat
```

After scoring, we sort within categories and enforce the min/max constraints. This keeps your digest balanced. Nobody wants 15 funding announcements and zero tutorials.

## Freshness Decay

Older articles get scored down. Simple exponential decay:

```python
import math
from datetime import datetime, timezone

def freshness_multiplier(published_at: datetime, half_life_hours: float = 36.0) -> float:
    """
    Returns a multiplier between 0.1 and 1.0.
    At half_life_hours, the multiplier is 0.5.
    Articles older than 7 days floor at 0.1.
    """
    now = datetime.now(timezone.utc)
    age_hours = (now - published_at).total_seconds() / 3600
    if age_hours < 0:
        return 1.0  # future-dated, treat as fresh
    decay = math.exp(-0.693 * age_hours / half_life_hours)  # ln(2) ≈ 0.693
    return max(0.1, decay)
```

Why 36 hours? We tested a few values. At 24 hours, good articles from yesterday afternoon got buried. At 48 hours, stale stuff hung around too long. 36 is the sweet spot for a daily digest.

The decay curve looks like this:
- 0 hours old: 1.0x (full score)
- 12 hours: 0.79x
- 24 hours: 0.63x
- 36 hours: 0.50x
- 48 hours: 0.40x
- 72 hours: 0.25x
- 168 hours (7 days): 0.1x (floor)

## Semantic Scoring with Embeddings

Keywords work. But they miss stuff. An article titled "Why Cursor Won the IDE War" has zero keyword matches for "coding agent" or "vibe coding" but it's clearly relevant. Semantic scoring catches these.

### Setup (5 minutes)

```bash
pip install sentence-transformers
```

First run downloads the model (~80MB). After that, it loads from cache.

### Pick Your Model

We tested three options. Here's what we found:

| Model | Size | Speed (700 articles) | Quality |
|---|---|---|---|
| `all-MiniLM-L6-v2` | 22M params, 384 dims | 1.8s | Good enough |
| `all-mpnet-base-v2` | 109M params, 768 dims | 3.4s | Noticeably better |
| `BAAI/bge-small-en-v1.5` | 33M params, 384 dims | 2.1s | Best bang for buck |

We use `all-MiniLM-L6-v2` in production. It's tiny, fast, and 90% as good as the bigger models for our use case. If you're scoring fewer than 200 articles per batch, `all-mpnet-base-v2` is worth the extra 1.6 seconds.

### How It Works

You define a set of "ideal article" descriptions. The system encodes those into vectors once. Then for each incoming article, it encodes the title + summary and computes cosine similarity against your ideal set. High similarity = high relevance.

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticScorer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

        # Define what a "perfect article" looks like for YOUR newsletter.
        # Be specific. These aren't keywords, they're descriptions.
        self.ideal_articles = [
            "A startup built an AI agent that replaces a specific job function and shows real revenue numbers",
            "New developer tool for AI-assisted coding ships today with benchmarks against competitors",
            "Founder shares exact growth playbook with specific numbers and what actually worked",
            "Company migrates from traditional architecture to AI-first and shares the results",
            "Open source project launches that lets you run AI models locally without cloud dependency",
            "Practical guide showing how to build something with Claude or GPT with working code",
            "Analysis of why a specific AI company is winning or losing with concrete evidence",
        ]

        # Encode once, reuse forever
        self.ideal_embeddings = self.model.encode(self.ideal_articles, normalize_embeddings=True)

    def score(self, title: str, summary: str) -> float:
        """
        Returns 0.0-1.0 semantic similarity to ideal articles.
        """
        text = f"{title}. {summary}"
        embedding = self.model.encode([text], normalize_embeddings=True)

        # Cosine similarity against each ideal article
        similarities = np.dot(embedding, self.ideal_embeddings.T)[0]

        # Take the max similarity (best match to any ideal)
        best_match = float(np.max(similarities))

        # Also factor in average of top 3 (rewards broad relevance)
        top_3_avg = float(np.mean(np.sort(similarities)[-3:]))

        # Weighted: 70% best match, 30% top-3 average
        return 0.7 * best_match + 0.3 * top_3_avg
```

### Converting Semantic Score to Points

Raw cosine similarity ranges from about 0.15 (totally irrelevant) to 0.75 (perfect match). We map this to 0-3 bonus points:

```python
def semantic_bonus(similarity: float) -> float:
    """Map cosine similarity to 0-3 point bonus."""
    if similarity < 0.30:
        return 0.0       # not relevant
    elif similarity < 0.40:
        return 0.5       # slightly relevant
    elif similarity < 0.50:
        return 1.0       # relevant
    elif similarity < 0.60:
        return 2.0       # very relevant
    else:
        return 3.0       # perfect match
```

## The Full Scoring Pipeline

Here's the complete implementation that ties everything together:

```python
import math
import re
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional

@dataclass
class Article:
    title: str
    summary: str
    source: str
    url: str
    published_at: datetime
    hn_points: int = 0
    tier: int = 3  # 0=curated newsletter, 1-4=other sources

@dataclass
class ScoredArticle:
    article: Article
    raw_score: float
    keyword_score: float
    semantic_score: float
    freshness: float
    source_mult: float
    trending_mult: float
    category: str
    final_score: float

def score_article(
    article: Article,
    semantic_scorer: Optional['SemanticScorer'] = None,
) -> ScoredArticle:
    text = f"{article.title} {article.summary}".lower()

    # 1. Keyword scoring
    kw_score = 0.0

    # Tier 1: paradigm shift
    t1_hits = sum(1 for kw in PARADIGM_SHIFT_SIGNAL if kw in text)
    kw_score += min(t1_hits * 2.0, 8.0)

    # Tier 2: actionable
    t2_hits = sum(1 for kw in ACTIONABLE_SIGNAL if kw in text)
    kw_score += min(t2_hits * 1.0, 6.0)

    # Tier 3: infrastructure
    t3_hits = sum(1 for kw in INFRA_SIGNAL if kw in text)
    kw_score += min(t3_hits * 0.3, 2.0)

    # Tier bonus (curated sources)
    kw_score += tier_bonus.get(article.tier, 0.0)

    # 2. Penalties
    # Research paper penalty
    research_hits = sum(1 for kw in RESEARCH_INDICATORS if kw in text)
    if research_hits >= 3:
        kw_score *= 0.2
    elif research_hits == 2:
        kw_score *= 0.4
    elif research_hits == 1:
        kw_score *= 0.7

    # Skip patterns (instant kill)
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, text):
            return ScoredArticle(
                article=article, raw_score=0.5, keyword_score=0.5,
                semantic_score=0.0, freshness=1.0, source_mult=1.0,
                trending_mult=1.0, category="skipped", final_score=0.5,
            )

    # 3. Source multiplier
    source_mult = SOURCE_BOOST.get(article.source, 1.0)
    source_mult = SOURCE_PENALTY.get(article.source, source_mult)

    # 4. Trending boost
    trending_mult = 1.0
    if article.hn_points >= 500:
        trending_mult = 1.8
    elif article.hn_points >= 200:
        trending_mult = 1.5
    elif article.hn_points >= 100:
        trending_mult = 1.3

    # 5. Freshness decay
    freshness = freshness_multiplier(article.published_at)

    # 6. Semantic scoring (optional)
    sem_score = 0.0
    sem_bonus = 0.0
    if semantic_scorer:
        sem_score = semantic_scorer.score(article.title, article.summary)
        sem_bonus = semantic_bonus(sem_score)

    # 7. Category
    category = categorize_article(article.title, article.summary)
    cat_boost = CATEGORY_RULES.get(category, {}).get("boost", 1.0)

    # 8. Combine everything
    raw = kw_score + sem_bonus
    final = raw * source_mult * trending_mult * freshness * cat_boost
    final = min(final, 10.0)  # cap at 10

    return ScoredArticle(
        article=article,
        raw_score=raw,
        keyword_score=kw_score,
        semantic_score=sem_score,
        freshness=freshness,
        source_mult=source_mult,
        trending_mult=trending_mult,
        category=category,
        final_score=round(final, 2),
    )


def score_batch(
    articles: list[Article],
    semantic_scorer: Optional['SemanticScorer'] = None,
    top_n: int = 20,
) -> list[ScoredArticle]:
    """Score all articles, enforce category constraints, return top N."""
    scored = [score_article(a, semantic_scorer) for a in articles]

    # Sort by final score
    scored.sort(key=lambda x: x.final_score, reverse=True)

    # Enforce category min/max constraints
    result = []
    cat_counts = {}

    # First pass: guarantee minimums
    for cat, rules in CATEGORY_RULES.items():
        min_count = rules.get("min_per_digest", 0)
        cat_articles = [s for s in scored if s.category == cat]
        for a in cat_articles[:min_count]:
            if a not in result:
                result.append(a)
                cat_counts[cat] = cat_counts.get(cat, 0) + 1

    # Second pass: fill remaining slots by score, respecting max
    for s in scored:
        if len(result) >= top_n:
            break
        if s in result:
            continue
        cat = s.category
        max_count = CATEGORY_RULES.get(cat, {}).get("max_per_digest", top_n)
        if cat_counts.get(cat, 0) < max_count:
            result.append(s)
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

    # Sort final result by score
    result.sort(key=lambda x: x.final_score, reverse=True)
    return result[:top_n]
```

## Calibrating Thresholds

The numbers above (keyword weights, similarity cutoffs, decay half-life) aren't magic. Here's how to find yours.

### Step 1: Build a Labeled Set

Take 100 articles you've already rated. You need at least 30 "good" (would include in newsletter) and 30 "bad" (would skip). Export them as JSON:

```python
labeled = [
    {"title": "...", "summary": "...", "source": "...", "good": True},
    # ... 100 articles
]
```

### Step 2: Score With Current Weights

Run your scoring pipeline on the labeled set. Then check precision and recall:

```python
def evaluate(scored_articles, threshold=5.0):
    tp = sum(1 for a in scored_articles if a.final_score >= threshold and a.article.good)
    fp = sum(1 for a in scored_articles if a.final_score >= threshold and not a.article.good)
    fn = sum(1 for a in scored_articles if a.final_score < threshold and a.article.good)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    print(f"Threshold: {threshold}")
    print(f"Precision: {precision:.1%} (of articles above threshold, how many are good?)")
    print(f"Recall: {recall:.1%} (of good articles, how many scored above threshold?)")
    return precision, recall
```

### Step 3: Find the Sweet Spot

Run evaluate at thresholds from 3.0 to 7.0 in 0.5 increments. You want:
- **Precision > 80%**: you're not drowning in noise
- **Recall > 70%**: you're not missing good stuff

If precision is low, raise keyword weights or add more penalty patterns. If recall is low, lower your threshold or add more signal keywords.

### Step 4: Iterate Weekly

Every time you manually override the system (promote a low-scored article, skip a high-scored one), that's a calibration signal. Log those overrides. After 2 weeks, re-run the evaluation. Your numbers will improve.

## Keyword-Only vs Keyword+Embedding: Benchmarks

We ran both pipelines on 4 weeks of real data (2,800 articles, 80 manually curated digests). Here's what we found:

| Metric | Keywords Only | Keywords + Embeddings |
|---|---|---|
| Precision @ top 20 | 72% | 84% |
| Recall @ top 20 | 68% | 79% |
| "Surprise" catches (good articles with 0 keyword hits) | 0 | 14 per week avg |
| Processing time (700 articles) | 0.8s | 4.2s |
| Setup complexity | Zero dependencies | pip install + 80MB model |

The big win isn't the precision bump. It's the 14 articles per week that keywords completely miss. These tend to be the most interesting ones because they use unexpected language. An article titled "The $0 Stack That Prints Money" scores zero on keywords but the semantic scorer nails it because it's about bootstrapped AI automation.

### When to Skip Embeddings

- You have fewer than 200 articles per batch (keywords are enough)
- You can't install Python dependencies (serverless with tight size limits)
- You're still in the first 2 weeks (get your keyword lists right first)

### When Embeddings Are Worth It

- Your newsletter covers a niche topic where vocabulary is unpredictable
- You keep finding great articles that your keyword scorer missed
- You have the 4 seconds to spare (you do)

## Results

From 700+ articles per batch:
- ~200 filtered as noise (score 0)
- ~400 scored low (1-3)
- ~70 scored medium (4-6)
- ~30 scored high (7-10)
- **Top 20 shown to you**

The whole thing costs $0 to run.
