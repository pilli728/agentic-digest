"""RSS feed fetching for the Agentic Digest.

3-layer architecture:
  Layer 0: Top curator newsletters (80% of content) — already filtered by smart humans
  Layer 1: HN + Reddit trending (15%) — breaking news between newsletter cycles
  Layer 2: Background RSS (5%) — weekly deep scan for niche stuff

Daily fetch = Layer 0 + Layer 1 (~30 articles)
Weekly fetch = Layer 0 + Layer 1 + Layer 2 (~100+ articles)
"""

import feedparser
from datetime import datetime, timedelta
from dateutil import parser as dateparser
from .models import Article


# =============================================================================
# LAYER 0: Top Curator Newsletters — the humans who already filter for you
# These are the 8 best AI/builder newsletters. They read 500+ articles/week.
# =============================================================================
TIER_ZERO = {
    # Verified working feeds — these are the curators doing the filtering for you
    "Ben's Bites": {
        "url": "https://bensbites.substack.com/feed",
        "tier": 0,
        "focus": "Best daily AI roundup — builder-focused, no fluff"
    },
    "Latent Space": {
        "url": "https://www.latent.space/feed",
        "tier": 0,
        "focus": "Deep builder content, AI engineering interviews"
    },
    "Simon Willison": {
        "url": "https://simonwillison.net/atom/everything/",
        "tier": 0,
        "focus": "Hands-on builder, tries everything himself"
    },
    "Import AI (Jack Clark)": {
        "url": "https://importai.substack.com/feed",
        "tier": 0,
        "focus": "Weekly deep AI analysis from Anthropic co-founder"
    },
    "The Batch (Andrew Ng)": {
        "url": "https://thebatch.substack.com/feed",
        "tier": 0,
        "focus": "Weekly AI industry analysis from Andrew Ng"
    },
    "Ahead of AI (Sebastian Raschka)": {
        "url": "https://magazine.sebastianraschka.com/feed",
        "tier": 0,
        "focus": "Visual guides to ML/LLM internals, training techniques"
    },
    "Lenny's Newsletter": {
        "url": "https://www.lennysnewsletter.com/feed",
        "tier": 0,
        "focus": "Product strategy, growth, startup operator insights"
    },
    "Not Boring (Packy McCormick)": {
        "url": "https://www.notboring.co/feed",
        "tier": 0,
        "focus": "Business strategy meets tech — makes complex topics fun"
    },
    "Stratechery (Ben Thompson)": {
        "url": "https://stratechery.com/feed/",
        "tier": 0,
        "focus": "Analytical frameworks for tech business, connects dots"
    },
    "ByteByteGo": {
        "url": "https://blog.bytebytego.com/feed",
        "tier": 0,
        "focus": "System design, engineering at scale, visual explainers"
    },

    # --- From your email subscriptions ---
    "a16z": {
        "url": "https://a16z.substack.com/feed",
        "tier": 0,
        "focus": "VC analysis, tech strategy, market trends from Andreessen Horowitz"
    },
    "a16z Speedrun": {
        "url": "https://speedrun.substack.com/feed",
        "tier": 0,
        "focus": "How to build startups fast — from a16z's accelerator"
    },
    "The Generalist": {
        "url": "https://thegeneralist.substack.com/feed",
        "tier": 0,
        "focus": "Deep dives on the most interesting companies in tech"
    },
    "NEW ECONOMIES": {
        "url": "https://neweconomies.substack.com/feed",
        "tier": 0,
        "focus": "Tech trends reshaping industries, weekly digest"
    },
    "OnlyCFO": {
        "url": "https://onlycfo.substack.com/feed",
        "tier": 0,
        "focus": "SaaS metrics, fundraising, financial strategy for founders"
    },
    # Chain of Thought (Teng Yan) — no working RSS feed, uses custom email delivery
    "Bay Area Founders Club": {
        "url": "https://bayareafoundersclub.substack.com/feed",
        "tier": 0,
        "focus": "VC signal, Bay Area founder events, startup networking"
    },
    "The Leverage": {
        "url": "https://theleverage.substack.com/feed",
        "tier": 0,
        "focus": "Startup leverage, AI-first business building"
    },
}

# =============================================================================
# LAYER 1: Primary builder sources — company blogs that announce things
# Only the ones that actually ship and post regularly
# =============================================================================
PRIMARY_SOURCES = {
    # Major AI labs — announcements you can't miss
    "Anthropic Blog": {
        "url": "https://www.anthropic.com/feed",
        "tier": 1,
        "focus": "Claude releases, computer use, safety research"
    },
    "OpenAI Blog": {
        "url": "https://openai.com/blog/rss/",
        "tier": 1,
        "focus": "GPT releases, API updates, product launches"
    },
    "Google AI Blog": {
        "url": "https://blog.google/technology/ai/rss/",
        "tier": 1,
        "focus": "Gemini, DeepMind, research breakthroughs"
    },
    "Hugging Face Blog": {
        "url": "https://huggingface.co/blog/feed.xml",
        "tier": 1,
        "focus": "Open-source models, community benchmarks"
    },
    "Vercel Blog": {
        "url": "https://vercel.com/blog/feed.xml",
        "tier": 1,
        "focus": "AI SDK, agent deployment, scaling stories"
    },
    "LangChain Blog": {
        "url": "https://blog.langchain.dev/rss/",
        "tier": 1,
        "focus": "Agent frameworks, LangGraph, production agents"
    },

    # Builder-focused tech news
    "Product Hunt": {
        "url": "https://www.producthunt.com/feed",
        "tier": 1,
        "focus": "New AI product launches daily"
    },
    "TechCrunch AI": {
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "tier": 1,
        "focus": "Startup funding, launches, acquisitions"
    },
}

# =============================================================================
# LAYER 2: Background sources — weekly deep scan for niche coverage
# Only runs on weekly fetch, not daily
# =============================================================================
BACKGROUND_SOURCES = {
    # Individual builders
    "Chip Huyen": {"url": "https://huyenchip.com/feed", "tier": 3, "focus": "ML engineering, production systems"},
    "Lilian Weng": {"url": "https://lilianweng.github.io/feed.xml", "tier": 3, "focus": "Deep AI research explainers"},
    "Eugene Yan": {"url": "https://eugeneyan.com/rss/", "tier": 3, "focus": "ML systems, RecSys, production AI"},
    "One Useful Thing": {"url": "https://www.oneusefulthing.org/feed", "tier": 3, "focus": "AI implications, experiments"},
    "Turing Post": {"url": "https://www.turingpost.com/feed", "tier": 3, "focus": "AI deep dives, agentic workflows"},

    # More newsletters
    "AI++ Newsletter": {"url": "https://aiplusplus.substack.com/feed", "tier": 2, "focus": "Agents, MCP, dev tools"},
    "GenAI.works": {"url": "https://newsletter.genai.works/feed", "tier": 2, "focus": "Daily generative AI tools"},
    "Ahead of AI": {"url": "https://magazine.sebastianraschka.com/feed", "tier": 3, "focus": "ML research, LLM training"},

    # Community
    "Hacker News (Front Page)": {"url": "https://hnrss.org/frontpage", "tier": 4, "focus": "Tech community signal"},
    "The Verge AI": {"url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "tier": 4, "focus": "AI product news"},
    "Ars Technica AI": {"url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "tier": 4, "focus": "Technical analysis"},
    "MIT Technology Review": {"url": "https://www.technologyreview.com/feed/", "tier": 4, "focus": "Research, policy"},

    # Reddit (RSS — no API key needed)
    "Reddit: r/AI_Agents": {"url": "https://www.reddit.com/r/AI_Agents/.rss", "tier": 4, "focus": "Agent builder community"},
    "Reddit: r/ClaudeAI": {"url": "https://www.reddit.com/r/ClaudeAI/.rss", "tier": 4, "focus": "Claude user community"},
    "Reddit: r/LocalLLaMA": {"url": "https://www.reddit.com/r/LocalLLaMA/.rss", "tier": 4, "focus": "Open-source LLMs"},
    "Reddit: r/LangChain": {"url": "https://www.reddit.com/r/LangChain/.rss", "tier": 4, "focus": "LangChain users"},
    "Reddit: r/MachineLearning": {"url": "https://www.reddit.com/r/MachineLearning/.rss", "tier": 4, "focus": "ML research"},
    "Reddit: r/openclaw": {"url": "https://www.reddit.com/r/openclaw/.rss", "tier": 4, "focus": "OpenClaw community"},
    "Reddit: r/vibecoding": {"url": "https://www.reddit.com/r/vibecoding/.rss", "tier": 4, "focus": "Vibe coding movement"},
    "Reddit: r/AgentsOfAI": {"url": "https://www.reddit.com/r/AgentsOfAI/.rss", "tier": 4, "focus": "AI agents discussion"},
    "Reddit: r/Startup_Ideas": {"url": "https://www.reddit.com/r/Startup_Ideas/.rss", "tier": 4, "focus": "Startup ideas"},
}

MAX_ARTICLES_PER_FEED = 10
MAX_ARTICLES_TIER_ZERO = 15  # Get more from top curators


def _fetch_feeds(feeds: dict, lookback_hours: int, max_per_feed: int = MAX_ARTICLES_PER_FEED) -> list[Article]:
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

                # Parse published date
                published = None
                for date_field in ["published_parsed", "updated_parsed"]:
                    if hasattr(entry, date_field) and getattr(entry, date_field):
                        published = datetime(*getattr(entry, date_field)[:6])
                        break

                if not published:
                    for date_str_field in ["published", "updated"]:
                        if hasattr(entry, date_str_field):
                            try:
                                published = dateparser.parse(getattr(entry, date_str_field))
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

                article = Article(
                    source=source_name,
                    tier=config["tier"],
                    title=title,
                    link=link,
                    summary=summary,
                    published=published.isoformat() if published else "unknown",
                    fetched_at=datetime.now().isoformat(),
                )
                all_articles.append(article)
                count += 1

        except Exception as e:
            print(f"  [WARN] Failed to fetch {source_name}: {e}")

    return all_articles


def fetch_articles(lookback_hours: int = 24, include_background: bool = False) -> list[Article]:
    """
    Fetch articles using the 3-layer system.

    Daily (default): Layer 0 (top newsletters) + Layer 1 (primary sources)
    Weekly (include_background=True): + Layer 2 (background sources)

    Args:
        lookback_hours: How many hours back to look
        include_background: Include Layer 2 background sources

    Returns:
        List of Article objects
    """
    all_articles = []

    # Layer 0: Top curator newsletters (get more articles from these)
    print("  [Layer 0] Fetching from top curator newsletters...")
    tier_zero = _fetch_feeds(TIER_ZERO, lookback_hours, max_per_feed=MAX_ARTICLES_TIER_ZERO)
    all_articles.extend(tier_zero)
    print(f"  [Layer 0] {len(tier_zero)} articles from {len(TIER_ZERO)} curators")

    # Layer 1: Primary builder sources
    print("  [Layer 1] Fetching from primary builder sources...")
    primary = _fetch_feeds(PRIMARY_SOURCES, lookback_hours)
    all_articles.extend(primary)
    print(f"  [Layer 1] {len(primary)} articles from {len(PRIMARY_SOURCES)} sources")

    # Layer 2: Background sources (weekly only)
    if include_background:
        print("  [Layer 2] Fetching from background sources...")
        background = _fetch_feeds(BACKGROUND_SOURCES, lookback_hours)
        all_articles.extend(background)
        print(f"  [Layer 2] {len(background)} articles from {len(BACKGROUND_SOURCES)} sources")

    print(f"\n  Fetched {len(all_articles)} articles total.")
    return all_articles


# Legacy compatibility — expose all feeds as FEEDS dict
FEEDS = {**TIER_ZERO, **PRIMARY_SOURCES, **BACKGROUND_SOURCES}
