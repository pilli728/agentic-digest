"""Claude-based filtering and ranking for the Agentic Digest."""

import json
from anthropic import Anthropic
from .models import Article


def filter_and_rank(articles: list[Article], top_n: int = 15, model: str = "claude-haiku-4-5-20251001", preference_context: str = "") -> list[Article]:
    """
    Use Claude to filter for agentic AI builder relevance and rank.

    Args:
        articles: List of Article objects to filter
        top_n: Number of top stories to return (use 999 to rank all)
        model: Claude model to use
        preference_context: Optional user preference profile to inject into system prompt

    Returns:
        List of ranked Article objects with relevance scores and why_it_matters (3-sentence summary)
    """
    client = Anthropic()

    # Convert articles to JSON for Claude
    articles_json = json.dumps(
        [a.to_dict() for a in articles],
        indent=2
    )

    # Build system prompt with optional preference context
    system_prompt = """You are a senior AI engineer and startup advisor curating a daily intelligence
briefing for founders building agentic AI products.

Your job is to filter and rank articles by ONE criterion:
"Would a founder building an AI agent startup need to know this TODAY?"

Prioritize:
- New model capabilities that unlock agent use cases
- Infrastructure and tooling releases (frameworks, APIs, protocols like MCP)
- Fundraising rounds and market signals in the agent space
- Technical breakthroughs in reasoning, planning, tool use, or multi-agent systems
- Production lessons from teams shipping agents at scale
- Regulatory or policy moves that affect agent builders

Deprioritize:
- General AI hype or listicles
- Consumer product updates unrelated to building
- AI ethics commentary without practical implications
- Repetitive coverage of the same story across sources

Return ONLY valid JSON. No markdown, no backticks, no preamble."""

    if preference_context:
        system_prompt += f"""

Additionally, here is the user's preference profile based on their past ratings:

{preference_context}

Use these preferences to adjust your rankings. Articles matching the user's demonstrated interests
should score higher. Articles matching patterns they consistently skip should score lower.
However, still surface genuinely important breaking news even if it doesn't match past patterns."""

    # Determine how many to request
    select_n = min(top_n, len(articles))

    response = client.messages.create(
        model=model,
        max_tokens=8000,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"""Here are today's articles from my RSS feeds:

{articles_json}

Return a JSON object with this structure:
{{
  "top_stories": [
    {{
      "title": "...",
      "source": "...",
      "link": "...",
      "why_it_matters": "3 sentences: What this is about, why it matters to AI agent builders, and what you should do about it.",
      "relevance_score": 1-10
    }}
  ]
}}

Rank ALL {select_n} stories. Sort by relevance_score descending.
Write why_it_matters as exactly 3 sentences for quick skimming. Be specific and actionable. No hype."""
        }]
    )

    # Parse Claude's response
    raw = response.content[0].text.strip()
    # Clean potential markdown fencing
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]

    ranked_data = json.loads(raw)

    # Convert back to Article objects with enriched data
    result = []
    for story in ranked_data.get("top_stories", []):
        # Find original article to preserve all data
        original = next(
            (a for a in articles if a.link == story.get("link")),
            None
        )
        if original:
            original.relevance_score = story.get("relevance_score")
            original.why_it_matters = story.get("why_it_matters")
            result.append(original)

    return result
