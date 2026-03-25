"""
Voice-powered digest writer.
Takes topics with sources and editor notes, writes each section in the author's voice.
Uses the Anti-AI Writing Style Guide formula: Hook → Context → So what → Edge → Action.
"""

import json
import os
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}


def fetch_article_content(url: str, max_chars: int = 5000) -> str:
    """Fetch the main text content of an article URL."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        if resp.status_code != 200:
            return ""

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Remove noise elements
        for tag in soup.find_all(['nav', 'footer', 'script', 'style', 'aside', 'header', 'form', 'iframe']):
            tag.decompose()

        # Try multiple content selectors in order of specificity
        content_el = None
        for selector in [
            ('article', {}),
            ('div', {'class_': lambda c: c and any(x in str(c).lower() for x in ['entry-content', 'post-content', 'article-body', 'article-content', 'post-body'])}),
            ('main', {}),
            ('div', {'class_': lambda c: c and 'content' in str(c).lower()}),
            ('body', {}),
        ]:
            content_el = soup.find(selector[0], **selector[1]) if len(selector) > 1 else soup.find(selector[0])
            if content_el:
                ps = content_el.find_all('p')
                long_ps = [p for p in ps if len(p.get_text(strip=True)) > 30]
                if long_ps:
                    break

        if not content_el:
            return ""

        # Get text from paragraphs, headings, and list items
        elements = content_el.find_all(['p', 'h1', 'h2', 'h3', 'li', 'blockquote'])
        parts = []
        for el in elements:
            text = el.get_text(strip=True)
            if len(text) < 20:
                continue
            # Skip cookie/privacy notices
            if any(skip in text.lower() for skip in ['cookie', 'privacy policy', 'subscribe', 'sign up for', 'advertisement']):
                continue
            parts.append(text)

        text = '\n'.join(parts)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()

        if len(text) > max_chars:
            text = text[:max_chars] + '...'

        return text if len(text) > 100 else ""
    except Exception:
        return ""

VOICE_SYSTEM = """You are ghostwriting a newsletter for Agentic Edge, a weekly digest for AI agent builders.

VOICE:
Write like you're texting a smart friend about something you found. Not a journalist. Not an AI. You're a builder who tried things this week and is sharing what worked.

Study these writers: Paul Graham (say it in 5 words not 15), Packy McCormick (make complex things a story you can't stop reading), Lenny Rachitsky (cut every sentence that doesn't earn its place), Simon Willison (credibility from doing, not theorizing).

ANTI-AI WRITING RULES (critical, follow every one):

Vocabulary bans: delve, tapestry, landscape, realm, embark, leverage, foster, underscore, harness, beacon, robust, seamless, transformative, groundbreaking, cutting-edge, holistic, multifaceted, paradigm, synergy, testament, journey, navigate, unlock, unravel, craft/crafting, illuminate, pivotal, paramount, meticulously, profoundly, it's worth noting, in today's, not only X but also Y, when it comes to, at its core, shed light on, paving the way, in conclusion, overall (as opener), let's dive in, by doing X you can Y.

Punctuation: NEVER use em dashes. Use commas, periods, or parentheses. Semicolons max once per section. No emoji in prose. No decorative unicode. Don't bold random words for emphasis.

Sentences: Never start two consecutive sentences with the same word. Mix 4-word sentences with 25-word ones. Never three sentences of similar length in a row. Use fragments for punch. Start sentences with "And" or "But" sometimes. Avoid ending sentences with ", [verb]-ing..." constructions. Don't do three-part parallel lists ("X, Y, and Z") more than once per section.

Paragraphs: Vary length wildly. Include single-sentence paragraphs. Don't follow topic-sentence > evidence > summary for every paragraph. Sometimes lead with the example. Sometimes the point comes last. Never write a conclusion that restates what you said. End on a specific detail or just stop.

Tone: Make direct statements. Don't hedge ("it may be advisable to consider"). Say things are bad when they're bad. Not everything is exciting. Mix contractions inconsistently ("it's" and "it is" in the same piece). Include uncertainty when genuine ("I'm not sure about this but"). Take a position. Be wrong sometimes rather than vague always.

Content: Use specific names, numbers, dates, dollar amounts. Don't present balanced perspectives on everything. State each point once, never repeat across paragraphs.

READABILITY:
- Short paragraphs. 2-3 sentences max. Lots of whitespace between them.
- Break up walls of text. If a paragraph is more than 3 sentences, SPLIT IT.
- When jargon appears, keep it but add a quick "(that means...)" the first time. Don't strip out technical detail, just make it accessible.
- One idea per sentence. Let it breathe.
- Add a > blockquote callout for the single most important insight in each section. Just one per section.
- For tool sections: use ### sub-headings for each tool. This breaks up the visual flow.
- Think "smart builder explaining to another builder" not "journalist dumbing it down."

STRUCTURE:
For each topic section:
1. Section header as: ## [Topic Title]
2. Short paragraphs (2-3 sentences max each). Use multiple paragraphs, not one dense block. Whitespace is your friend.
3. If the topic covers multiple tools or products, give EACH ONE its own line with a link. Don't cram them together.
4. After the section: **Sources:** [Name](url), [Name](url)
5. Separator --- between sections.
6. Follow the editor's notes closely. They may override default format.

EXAMPLE (notice: sub-headings for tools, blockquote callout, short paragraphs, technical but clear):

## Tools This Week

### [Polsia](https://polsia.ai)

An AI agent that builds entire startups. It spins up a project instance (web app + database), wires it to Claude or GPT, then runs planning and execution cycles on its own.

Already at $1M+ ARR. The real question is whether orchestration alone is a moat, or if anyone can replicate this in a weekend.

> If agents can spend money, message customers, and ship code, the product isn't the agent. It's trust.

### [Nia](https://trynia.ai)

A CLI skill that gives your coding agent deep search across indexed codebases. Install with `npx nia-wizard@latest`, point it at a repo, and your agent stops hallucinating about your own code.

Works with Claude Code, OpenClaw, Cursor. Free tier is generous.

**Sources:** [Reddit](https://reddit.com), [trynia.ai](https://trynia.ai)

---

## The Market Shift

a16z said it plainly: two paths left. Grow 10+ points or hit 40% margins. The middle is dead.

Durable shipped 360 billion tokens/year with 6 engineers. That ratio used to be impossible. They stopped owning infrastructure and built on Vercel instead.

> The cost of owning your stack is no longer a tradeoff. It's a trap.

**Sources:** [a16z](https://a16z.com), [Vercel](https://vercel.com)

---

Return ONLY the newsletter markdown. Start with a one-line intro, then topic sections. No preamble."""


def write_digest(topics: list[dict], model: str = "claude-haiku-4-5-20251001") -> str:
    """
    Generate newsletter content from topics.

    Each topic dict should have:
        - title: str
        - synthesis: str (editor's notes)
        - articles: list[dict] with title, source, link, summary

    Returns markdown string of the full digest.
    """
    client = Anthropic()

    # Fetch full article content for each source
    print("  [digest-writer] Fetching article content...")
    for topic in topics:
        for a in topic.get('articles', []):
            url = a.get('link', '')
            if url:
                content = fetch_article_content(url)
                a['full_content'] = content
                status = f"{len(content)} chars" if content else "failed"
                print(f"    [{status}] {a.get('title', '?')[:50]}")

    # Build the prompt with all topics
    topics_text = ""
    for i, topic in enumerate(topics, 1):
        topics_text += f"\n--- TOPIC {i}: {topic['title']} ---\n"
        if topic.get('synthesis'):
            topics_text += f"Editor's notes: {topic['synthesis']}\n"
        topics_text += "Sources:\n"
        for a in topic.get('articles', []):
            topics_text += f"  - [{a.get('source', '?')}]({a.get('link', '#')}): {a.get('title', '?')}\n"
            if a.get('full_content'):
                topics_text += f"    Full article:\n    {a['full_content'][:2500]}\n\n"
            elif a.get('summary'):
                topics_text += f"    Summary: {a['summary'][:300]}\n"
        topics_text += "\n"

    response = client.messages.create(
        model=model,
        max_tokens=8000,
        system=VOICE_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Write the newsletter sections for these {len(topics)} topics:\n{topics_text}"
        }]
    )

    return response.content[0].text.strip()
