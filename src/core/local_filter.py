"""
Local article filter — no API key needed.
Scores articles by keyword relevance and filters out noise.
Used as a pre-filter before Claude ranking, or standalone when no API key is available.
"""

import re
from .models import Article


# === LEARNED FROM USER FEEDBACK ===
# User likes: paradigm shifts, competitive intel, major disruptions,
#             unique agent use cases, scaling stories, new protocols,
#             frameworks that change how engineers work
# User skips: low-level infra details, beginner tutorials

# HIGHEST SIGNAL — paradigm shifts and disruptions (user's top interest)
PARADIGM_SHIFT_SIGNAL = [
    # Fundamentally new ways of working
    "ai first", "ai-first", "before human", "replaces", "replacing",
    "fundamentally", "paradigm", "game changer", "game-changer", "disrupt",
    "transform", "revolution", "reimagin", "rethink", "new era",
    "without devops", "without engineers", "no-code", "zero-code",
    "autonomous", "self-driving", "self-healing", "self-improving",
    # Company structure changes
    "solo founder", "one-person", "small team", "lean team",
    "without hiring", "replacing team", "ai employee", "ai worker",
    "ai intern", "ai assistant", "ai cofounder", "co-founder",
    "6 engineers", "10 engineers", "no devops", "no ops",
    # Competitive intelligence
    "competitor", "competes with", "alternative to", "vs ", "versus",
    "openclaw", "defenseclaw", "new player", "just launched",
    "stealth", "backed by", "raised", "funding round",
]

# HIGH SIGNAL — concrete tools, major announcements, unique use cases
ACTIONABLE_SIGNAL = [
    # Major platform changes (Claude, OpenAI, OpenClaw)
    "claude", "computer use", "claude code", "anthropic",
    "openai", "gpt-4", "gpt-5", "o1", "o3", "o4", "codex",
    "gemini", "deepmind", "google ai",
    "openclaw", "open claw", "clawdbot", "clawd",
    "vibe coding", "vibecoding", "vibe-coding",
    # New tools, plugins, protocols you can use TODAY
    "mcp server", "mcp plugin", "model context protocol", "mpp",
    "tool use", "tool call", "plugin", "extension",
    "just released", "now available", "launching", "announces",
    "new feature", "new version", "update", "upgrade",
    # Unique/novel agent use cases (user loves these)
    "use case", "real-world", "in production", "case study",
    "we built", "how we", "how i", "our experience",
    "agent for", "ai for", "automat", "built an agent",
    "beating", "beats", "outperforms", "disrupting",
    # Frameworks for better engineering
    "framework", "methodology", "playbook", "system", "approach",
    "vibe coding", "coding agent", "pr review", "code review",
    "workflow", "developer experience", "dx", "devex",
    # Scaling & entrepreneur stories
    "scale", "scaling", "growth", "revenue", "customers",
    "startup", "founder", "entrepreneur", "bootstrapped",
    "series a", "series b", "yc", "y combinator", "raised",
    "pricing", "cost", "cheaper", "faster", "efficient",
]

# MEDIUM SIGNAL — still relevant but less exciting
INFRA_SIGNAL = [
    "agent", "agentic", "langchain", "llamaindex", "crewai", "autogen",
    "multi-agent", "orchestrat", "function calling",
    "llm", "large language model", "prompt engineer", "rag",
    "api", "sdk", "open source", "open-source",
    "hugging face", "huggingface", "mistral", "llama", "cohere",
    "token", "context window", "multimodal",
    "deploy", "ship", "launch", "release", "production",
    "template", "tutorial", "guide", "how to", "step-by-step",
]

# LOW SIGNAL — general AI stuff
LOW_SIGNAL = [
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "generative", "nlp",
    "python", "javascript", "developer", "engineer",
    "enterprise", "saas", "platform",
]

# NEGATIVE SIGNAL — user explicitly skips these
SKIP_PATTERNS = [
    # Low-level infra the user doesn't care about
    r"\bvllm\b", r"\bconcurrent request", r"\bserving\b.*\bmodel\b",
    r"\bbatch.?size\b", r"\bthroughput\b", r"\blatency\b.*\boptimiz",
    r"\bkubernetes\b", r"\bdocker\b.*\bcontainer\b",
    r"\bload balanc", r"\brate limit",
    # Beginner content
    r"\bbeginner\b", r"\bintroduction to\b", r"\bwhat is\b.*\b(ai|ml)\b",
    r"\bfor dummies\b", r"\bstart learning\b",
    r"\bspeed up.*python\b", r"\bpython tips\b",
    # Generic listicles
    r"\b\d+ (best|top|ways|tips|tools)\b.*\b(for beginners|you should know)\b",
]

# RESEARCH PENALTY — academic papers, not builder content
RESEARCH_INDICATORS = [
    "arxiv", "we propose", "we present", "our method", "our approach",
    "ablation study", "empirical", "theoretical", "theorem", "proof",
    "in this paper", "contributions of this", "related work",
    "markov", "bayesian", "stochastic", "convergence",
    "benchmark results", "evaluation metrics", "f1 score",
    "dataset", "baseline", "novel approach",
]

# Noise keywords — articles containing these are likely irrelevant
NOISE_PATTERNS = [
    r"\bnixos\b", r"\bfpga\b", r"\bwayland\b", r"\bibook\b", r"\bclamshell\b",
    r"\bcable\b.+\btv\b", r"\brefresh rate\b", r"\bgaming\b.+\bbrowser\b",
    r"\bpassword manager\b", r"\bvpn\b(?!.*\bai\b)", r"\bgan adapter\b",
    r"\biphone.+secret\b", r"\bsamsung.+fold\b", r"\bopera gx\b",
    r"\bhorror novel\b", r"\bshy girl\b", r"\bonline betting\b",
    r"\bcricket\b", r"\bsports\b(?!.*\bai\b)", r"\brecipe\b(?!.*\bai\b)",
    r"\bfashion\b(?!.*\bai\b)", r"\bcelebrit\b", r"\bgossip\b",
    r"\breal estate\b(?!.*\bai\b)", r"\bhoroscope\b", r"\bweather\b(?!.*\bai\b)",
    r"\bdogfood\b", r"\bfart\b",
    r"\blinux desktop\b(?!.*\bai\b)", r"\bwindow manager\b",
    r"\bkernel\b(?!.*\bai\b)", r"\bfilesystem\b",
]

# Source quality multipliers — based on user's actual preferences
SOURCE_BOOST = {
    # User loved these sources (gave thumbs up)
    "Vercel": 1.6, "SaaStr": 1.5, "Product Hunt": 1.5,
    "Towards AI": 1.4, "Dev.to": 1.3,
    # Core builder sources
    "Anthropic": 1.5, "OpenAI": 1.5, "Claude": 1.5,
    "LangChain": 1.4, "Cursor": 1.5, "Latent Space": 1.4,
    "Simon Willison": 1.3, "Hugging Face": 1.3,
    "LlamaIndex": 1.3, "CrewAI": 1.3,
    # Competitive intel sources
    "ZDNet": 1.3, "TechCrunch": 1.2,
}

# Source penalties — user skipped these or research sources
SOURCE_PENALTY = {
    "ArXiv": 0.4, "arxiv": 0.4,
    "IEEE": 0.5, "ACM": 0.5,
    "Nature": 0.6, "PNAS": 0.5,
    "KDnuggets": 0.7,  # user thumbs-downed beginner content from here
}

# TRENDING SIGNAL — engagement/virality indicators that boost score
TRENDING_INDICATORS = [
    "viral", "trending", "blowing up", "everyone talking",
    "million", "billion", "10x", "100x",
    "just announced", "breaking", "just launched", "just released",
    "goes viral", "taking over", "internet is", "twitter is",
    "points:", "comments:",  # HN engagement
    "upvotes", "likes", "shares", "retweets",
]


def compute_local_score(title: str, summary: str, source: str, tier: int) -> tuple[float, str]:
    """
    Compute a relevance score (0-10) for an article based on keywords.
    Prioritizes ACTIONABLE content (tools, templates, tutorials, releases).
    Penalizes research papers and academic content.
    Returns (score, reason).
    """
    text = f"{title} {summary}".lower()

    # Check for noise — auto-reject
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return 0.0, _noise_summary(source)

    # Check for skip patterns (user explicitly dislikes these)
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return 0.5, _skip_summary(source)

    score = 0.0
    matches = []

    # PARADIGM SHIFTS — user's #1 interest (+2.0 each, max 8 points)
    paradigm_hits = 0
    for kw in PARADIGM_SHIFT_SIGNAL:
        if kw.lower() in text:
            paradigm_hits += 1
            if len(matches) < 5:
                matches.append(kw)
    score += min(paradigm_hits * 2.0, 8.0)

    # ACTIONABLE content — tools, announcements, use cases (+1.0 each, max 6 points)
    action_hits = 0
    for kw in ACTIONABLE_SIGNAL:
        if kw.lower() in text:
            action_hits += 1
            if len(matches) < 5:
                matches.append(kw)
    score += min(action_hits * 1.0, 6.0)

    # Infrastructure signal (+0.3 each, max 2 points)
    infra_hits = 0
    for kw in INFRA_SIGNAL:
        if kw.lower() in text:
            infra_hits += 1
    score += min(infra_hits * 0.3, 2.0)

    # Low signal (+0.1 each, max 0.5 points)
    low_hits = 0
    for kw in LOW_SIGNAL:
        if kw.lower() in text:
            low_hits += 1
    score += min(low_hits * 0.1, 0.5)

    # RESEARCH PENALTY — academic papers get heavily downranked
    research_hits = 0
    for kw in RESEARCH_INDICATORS:
        if kw.lower() in text:
            research_hits += 1
    if research_hits >= 3:
        score *= 0.2  # Very heavy penalty
    elif research_hits >= 2:
        score *= 0.4
    elif research_hits == 1:
        score *= 0.7

    # Tier bonus
    tier_bonus = {1: 2.0, 2: 1.0, 3: 0.0, 4: 0.0}
    score += tier_bonus.get(tier, 0)

    # Source boost — user's preferred sources
    for source_key, mult in SOURCE_BOOST.items():
        if source_key.lower() in source.lower():
            score *= mult
            break

    # Source penalty — research/beginner sources
    for source_key, mult in SOURCE_PENALTY.items():
        if source_key.lower() in source.lower():
            score *= mult
            break

    # TRENDING BOOST — viral/high-engagement content gets a big bump
    trending_hits = 0
    for kw in TRENDING_INDICATORS:
        if kw.lower() in text:
            trending_hits += 1
    if trending_hits >= 2:
        score *= 1.5  # Big boost for clearly trending content
    elif trending_hits >= 1:
        score *= 1.2

    # HN engagement boost — extract points if available
    import re as _re
    points_match = _re.search(r'points:\s*(\d+)', text)
    if points_match:
        points = int(points_match.group(1))
        if points >= 500:
            score *= 1.8  # Massively viral on HN
        elif points >= 200:
            score *= 1.5
        elif points >= 100:
            score *= 1.3
        elif points >= 50:
            score *= 1.1

    # Cap at 10
    score = min(round(score, 1), 10.0)

    # Tag what type of content this is
    is_research = research_hits >= 2
    is_paradigm = paradigm_hits >= 2
    is_actionable = action_hits >= 3

    # Generate 5-sentence summary — human voice, no AI slop
    kw_list = ', '.join(matches[:3]) if matches else 'general tech'

    if score >= 7 and is_paradigm:
        reason = (
            f"The rules are changing. This is about {kw_list} — and it's the kind of shift that makes last month's playbook obsolete. "
            f"{source} is reporting something that affects how you hire, build, and sell. "
            f"The companies that see this early get a 6-month head start. The rest scramble. "
            f"This isn't a \"nice to know\" — it changes your roadmap. "
            f"Read it, then ask your team: what do we do differently starting Monday?"
        )
    elif score >= 7 and is_actionable:
        reason = (
            f"You can use this right now. Covers {kw_list} — not theory, not a research paper, an actual thing you can ship with. "
            f"From {source}, which consistently puts out stuff builders actually use. "
            f"The gap between knowing about this and your competitors knowing about it is your advantage. "
            f"Takes 5 minutes to read, could save you a week of building the wrong thing. "
            f"Open it, try it, decide if it belongs in your stack."
        )
    elif score >= 7:
        reason = (
            f"This one matters. Covers {kw_list} — directly affects what you're building. "
            f"From {source}. Could be a new model drop, a funding signal, or competitive intel. "
            f"The kind of thing that shows up in your investor's questions next week. "
            f"Better to know it now than hear about it from someone else. "
            f"Worth the 3-minute read."
        )
    elif score >= 4 and not is_research:
        reason = (
            f"Good context. Touches on {kw_list}. "
            f"From {source} — not urgent but the kind of thing that makes you smarter in the next meeting. "
            f"Might surface a competitor move, a funding trend, or a weird use case worth stealing. "
            f"Skim it in 2 minutes. Bookmark if it connects to something you're working on. "
            f"Skip if your plate is already full today."
        )
    elif score >= 4 and is_research:
        reason = (
            f"Academic paper on {kw_list}. Interesting but you can't ship with it today. "
            f"From {source}. Someone will turn this into an open-source tool in 6-12 months. "
            f"Now you'll recognize it when they do. "
            f"Skip unless this is exactly the problem you're solving right now. "
            f"Check back when there's a GitHub repo."
        )
    elif score > 0:
        reason = (
            f"Not really builder-focused. General tech content from {source}. "
            f"No tools to try, no moves to make, no opinions to form. "
            f"Your time is better spent on the articles above this one. "
            f"Skip it. "
            f"Only read if the headline genuinely surprises you."
        )
    else:
        reason = (
            f"Filtered out — nothing here about AI agents or builder tools. "
            f"From {source}. Auto-removed to keep your feed focused. "
            f"No action needed. "
            f"The filter is doing its job. "
            f"If this was wrong, hit 👍 and the system learns."
        )

    return score, reason


def _noise_summary(source):
    return (
        f"🚫 FILTERED: No relevance to AI agents, tools, or builder workflows. "
        f"Source: {source} — outside the agentic AI scope. "
        f"Auto-removed to keep your feed clean and focused. "
        f"No action needed. "
        f"If wrongly filtered, 👍 it to teach the system."
    )


def _skip_summary(source):
    return (
        f"⬇️ SKIPPED: Matches patterns you've previously thumbs-downed (beginner content or low-level infra). "
        f"Source: {source} — this type of content isn't what you're looking for. "
        f"The system learned this from your past ratings. "
        f"Auto-deprioritized to save you time. "
        f"If this was wrong, 👍 it to override."
    )


def local_filter_and_rank(articles: list[Article], min_score: float = 1.0) -> list[Article]:
    """
    Filter and rank articles locally without API calls.
    Articles below min_score are excluded.

    Returns ranked list with relevance_score and why_it_matters set.
    """
    scored = []

    for article in articles:
        score, reason = compute_local_score(
            article.title,
            article.summary or "",
            article.source,
            article.tier,
        )

        if score >= min_score:
            article.relevance_score = score
            article.why_it_matters = reason
            scored.append(article)

    # Sort by score descending
    scored.sort(key=lambda a: a.relevance_score or 0, reverse=True)
    return scored


def filter_noise_from_db(db) -> dict:
    """
    Score all unranked articles in the database using local filter.
    Returns stats about what was scored/filtered.
    """
    from database import DigestDatabase

    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT id, title, source, tier, summary
        FROM articles
        WHERE relevance_score IS NULL OR relevance_score = 0
    """)

    kept = 0
    filtered = 0

    for row in cursor.fetchall():
        row_dict = dict(row)
        score, reason = compute_local_score(
            row_dict["title"],
            row_dict.get("summary") or "",
            row_dict["source"],
            row_dict["tier"],
        )

        db.conn.execute("""
            UPDATE articles SET relevance_score = ?, why_it_matters = ?
            WHERE id = ?
        """, (score, reason, row_dict["id"]))

        if score >= 1.0:
            kept += 1
        else:
            filtered += 1

    db.conn.commit()
    return {"kept": kept, "filtered": filtered, "total": kept + filtered}
