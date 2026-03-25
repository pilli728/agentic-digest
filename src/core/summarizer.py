"""Batch summarize articles using Claude. Replaces keyword-template garbage with real summaries."""

import json
import os
from anthropic import Anthropic


def needs_summary(summary: str) -> bool:
    """Check if an article's summary is useless and needs replacing."""
    if not summary:
        return True
    s = summary.strip()
    if len(s) < 40:
        return True
    # HN/Reddit point counts
    if s.startswith("Points:") or "Trending on Hacker News" in s or "Trending on Reddit" in s:
        return True
    # Our old keyword-match templates
    for prefix in ("High signal", "Actionable", "Worth a look", "Paradigm shift",
                    "Low signal", "Filtered", "Research", "Auto-skipped"):
        if s.startswith(prefix):
            return True
    return False


def batch_summarize(articles: list[dict], model: str = "claude-haiku-4-5-20251001") -> dict:
    """
    Takes a list of article dicts, returns {article_id: summary} for ones that need it.
    Uses a single Claude call to summarize a batch efficiently.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return {}

    # Filter to articles that need summaries
    to_summarize = []
    for a in articles:
        summary = a.get("summary") or a.get("why_it_matters") or ""
        if needs_summary(summary):
            to_summarize.append(a)

    if not to_summarize:
        return {}

    # Cap batch size to avoid token limits
    batch = to_summarize[:30]

    client = Anthropic()

    articles_for_prompt = []
    for a in batch:
        articles_for_prompt.append({
            "id": a["id"],
            "title": a["title"],
            "source": a["source"],
            "link": a["link"],
            "existing_summary": (a.get("summary") or "")[:200],
        })

    response = client.messages.create(
        model=model,
        max_tokens=4000,
        system="""You write 1-2 sentence summaries for a newsletter curator.
Each summary should answer: "What is this and why should an AI agent builder care?"
Be specific and concrete. No hype, no filler. If you don't know enough from the title/source, say what it likely covers based on the source.
Return ONLY valid JSON. No markdown fencing.""",
        messages=[{
            "role": "user",
            "content": f"""Summarize each article in 1-2 sentences. Return JSON array:
[{{"id": "...", "summary": "..."}}]

Articles:
{json.dumps(articles_for_prompt, indent=2)}"""
        }]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]

    try:
        results = json.loads(raw)
        return {r["id"]: r["summary"] for r in results if r.get("summary")}
    except (json.JSONDecodeError, KeyError):
        return {}
