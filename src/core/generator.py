"""Markdown digest generation for the Agentic Digest.

Writing style: Paul Graham's directness meets Trung Phan's comedic timing.
Intersection of Packy McCormick (conversational, analogies), Lenny Rachitsky
(direct, opinionated, no filler), Paul Graham (short sentences, contrarian),
Ben Thompson (connects dots, frameworks), Trung Phan (witty, fun),
Simon Willison (hands-on, "I tried this").

Rules:
- No AI slop: never use "delve", "landscape", "tapestry", "it's worth noting",
  "in conclusion", "let's dive in", "game-changer", "revolutionize", "leverage",
  "synergy", "in today's rapidly evolving"
- Write like you're texting a smart friend
- Short sentences. Opinions. Specifics over vague claims.
- Every sentence earns its place — if it doesn't add value, cut it
- One earned wry observation per section. Not a punchline — a dry aside that
  makes the reader think "yeah, exactly." Humor should land quietly, not perform.
- Sharp takes over safe takes. Contrarian is fine. Smug is not.
- If a take could appear in any newsletter, cut it. Only write what only you'd write.
"""

from datetime import datetime
from .models import Article, Digest

# Banned AI phrases — if any of these slip into why_it_matters, strip them
AI_SLOP = [
    "it's worth noting", "in today's", "let's dive in", "game-changer",
    "revolutionize", "leverage", "synergy", "in conclusion", "furthermore",
    "landscape", "tapestry", "delve", "navigate", "crucial", "paramount",
    "in this rapidly", "at the forefront", "in the realm of", "it is important to",
    "cutting-edge", "groundbreaking", "seamlessly", "robust", "holistic",
    "unlock the power", "harness the potential", "take it to the next level",
]


def clean_ai_slop(text: str) -> str:
    """Remove AI-sounding phrases from text."""
    result = text
    for phrase in AI_SLOP:
        result = result.replace(phrase, "")
        result = result.replace(phrase.title(), "")
        result = result.replace(phrase.upper(), "")
    # Clean up double spaces
    while "  " in result:
        result = result.replace("  ", " ")
    return result.strip()


def generate_digest(
    articles: list[Article],
    mode: str = "daily",
    date: str = None
) -> Digest:
    """Generate a newsletter digest with a human writing voice."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    date_obj = datetime.strptime(date, "%Y-%m-%d")
    display_date = date_obj.strftime("%B %d, %Y")
    day_name = date_obj.strftime("%A")

    lines = []

    # Header — conversational, not corporate
    lines.append("# Agentic Edge")
    lines.append(f"### {day_name}, {display_date}")
    lines.append("")

    if len(articles) <= 5:
        lines.append(f"**{len(articles)} stories.** The ones that actually matter this week.")
    elif len(articles) <= 10:
        lines.append(f"**{len(articles)} things you need to know.** Ranked by how much they'll affect what you're building.")
    else:
        lines.append(f"**{len(articles)} stories.** Filtered from 700+ articles so you don't have to.")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, article in enumerate(articles, 1):
        score = int(article.relevance_score) if article.relevance_score else 0
        why = clean_ai_slop(article.why_it_matters or "")

        # Strip the emoji prefixes from internal scoring (🔥 PARADIGM SHIFT: etc)
        for prefix in ["🔥 PARADIGM SHIFT: ", "🛠️ USE THIS TODAY: ", "⚡ HIGH IMPACT: ",
                       "📌 WORTH KNOWING: ", "📄 RESEARCH: ", "⬇️ LOW PRIORITY: ",
                       "🚫 FILTERED: ", "ACTIONABLE: ", "USEFUL: ", "RESEARCH: "]:
            if why.startswith(prefix):
                why = why[len(prefix):]

        # Format each story — short, punchy, opinionated
        lines.append(f"### {i}. {article.title}")
        lines.append("")
        lines.append(f"**{article.source}** · Signal: {score}/10")
        lines.append("")

        if why:
            lines.append(f"{why}")
            lines.append("")

        lines.append(f"[Read it →]({article.link})")
        lines.append("")

        if i < len(articles):
            lines.append("---")
            lines.append("")

    # Footer — personality, not generic
    lines.append("---")
    lines.append("")
    lines.append("That's the week. If I missed something, reply and tell me — I read every response.")
    lines.append("")
    lines.append("— Agentic Edge")
    lines.append("")
    lines.append("*Curated from 700+ sources. Zero AI slop. Every story earns its spot.*")

    content = "\n".join(lines)

    return Digest(
        date=date,
        mode=mode,
        content=content,
        articles=articles,
        created_at=datetime.now().isoformat(),
    )
