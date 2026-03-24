"""
Automated trending news fetcher.
Pulls breaking AI stories from HN API, Reddit JSON, and key RSS feeds.
No API keys needed — uses free public APIs.
Scores by engagement (upvotes, points, comments) to surface what's actually hot.
"""

import json
import re
import urllib.request
from datetime import datetime, timedelta
from .models import Article

# AI keywords to filter HN/Reddit for relevant stories
AI_KEYWORDS = re.compile(
    r'\b(ai|artificial intelligence|llm|gpt|claude|openai|anthropic|gemini|'
    r'agent|agentic|mcp|model context protocol|langchain|llamaindex|'
    r'machine learning|deep learning|neural|transformer|diffusion|'
    r'hugging face|open.?source.+model|fine.?tun|rag|vector|embedding|'
    r'copilot|cursor|codex|computer use|tool.?use|multi.?agent|'
    r'inference|token|context window|prompt|reasoning|'
    r'startup.+ai|ai.+startup|funding.+ai|ai.+funding|'
    r'openclaw|automation|automat|autonomous|robot|'
    r'regulation|policy|governance|safety|alignment)\b',
    re.IGNORECASE
)


def fetch_hn_trending(min_points: int = 50, max_stories: int = 15) -> list[Article]:
    """Fetch top AI-related stories from Hacker News API."""
    articles = []
    try:
        # HN top stories API
        req = urllib.request.Request(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            headers={"User-Agent": "AgenticDigest/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            story_ids = json.loads(resp.read())[:100]  # Top 100 stories

        for story_id in story_ids:
            try:
                req = urllib.request.Request(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                    headers={"User-Agent": "AgenticDigest/1.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    story = json.loads(resp.read())

                if not story or story.get("type") != "story":
                    continue

                title = story.get("title", "")
                points = story.get("score", 0)
                comments = story.get("descendants", 0)
                url = story.get("url", f"https://news.ycombinator.com/item?id={story_id}")

                # Filter for AI-related stories
                if not AI_KEYWORDS.search(title):
                    continue

                if points < min_points:
                    continue

                article = Article(
                    source="Hacker News (Trending)",
                    tier=1 if points >= 200 else 4,
                    title=title,
                    link=url,
                    summary=f"Points: {points}. Comments: {comments}. Trending on Hacker News front page.",
                    published=datetime.fromtimestamp(story.get("time", 0)).isoformat(),
                    fetched_at=datetime.now().isoformat(),
                )

                articles.append(article)
                if len(articles) >= max_stories:
                    break

            except Exception:
                continue

    except Exception as e:
        print(f"  [WARN] HN trending fetch failed: {e}")

    print(f"  [HN] Found {len(articles)} trending AI stories")
    return articles


def fetch_reddit_trending(subreddits: list[str] = None, min_upvotes: int = 20, max_per_sub: int = 5) -> list[Article]:
    """Fetch trending AI posts from Reddit JSON API (no auth needed)."""
    if subreddits is None:
        subreddits = [
            # Core AI agent communities
            "AI_Agents", "AgentsOfAI", "MachineLearning", "LocalLLaMA",
            "ClaudeAI", "ChatGPT", "artificial", "LangChain",
            # OpenClaw & Claude ecosystem
            "openclaw", "clawdbot",
            # Builder & startup communities
            "Startup_Ideas", "vibecoding", "singularity",
        ]

    articles = []
    for sub in subreddits:
        try:
            req = urllib.request.Request(
                f"https://www.reddit.com/r/{sub}/hot.json?limit=15",
                headers={"User-Agent": "AgenticDigest/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())

            count = 0
            for post in data.get("data", {}).get("children", []):
                pd = post.get("data", {})
                title = pd.get("title", "")
                upvotes = pd.get("ups", 0)
                comments = pd.get("num_comments", 0)
                url = pd.get("url", "")
                permalink = f"https://reddit.com{pd.get('permalink', '')}"

                if pd.get("stickied"):
                    continue

                if upvotes < min_upvotes:
                    continue

                # For non-AI subreddits, filter by keywords
                if sub in ["singularity", "artificial"] and not AI_KEYWORDS.search(title):
                    continue

                article = Article(
                    source=f"Reddit r/{sub} (Trending)",
                    tier=4,
                    title=title,
                    link=permalink if not url.startswith("https://www.reddit.com") else permalink,
                    summary=f"Upvotes: {upvotes}. Comments: {comments}. Trending on r/{sub}.",
                    published=datetime.fromtimestamp(pd.get("created_utc", 0)).isoformat(),
                    fetched_at=datetime.now().isoformat(),
                )

                articles.append(article)
                count += 1
                if count >= max_per_sub:
                    break

        except Exception as e:
            print(f"  [WARN] Reddit r/{sub} fetch failed: {e}")

    print(f"  [Reddit] Found {len(articles)} trending posts across {len(subreddits)} subreddits")
    return articles


def fetch_all_trending() -> list[Article]:
    """Fetch all trending AI content from HN + Reddit."""
    articles = []

    print("  Fetching trending from Hacker News...")
    articles.extend(fetch_hn_trending())

    print("  Fetching trending from Reddit...")
    articles.extend(fetch_reddit_trending())

    print(f"  [TOTAL] {len(articles)} trending articles found")
    return articles
