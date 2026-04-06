#!/usr/bin/env python3
"""
Agentic Edge — Weekly Digest Generator
Runs every Sunday night. Pulls Twitter bookmarks, scores them with Claude,
writes vault articles, builds the digest markdown, commits, and sends test email.

Usage:
    python scripts/weekly_digest_generator.py

Environment variables:
    ANTHROPIC_API_KEY       - Required
    TWITTER_ACCESS_TOKEN    - OAuth 2.0 user token (required unless BOOKMARKS_JSON_PATH set)
    TWITTER_USER_ID         - Numeric Twitter user ID
    RESEND_API_KEY          - Required for test email
    RESEND_FROM             - Sender address (e.g. "Agentic Edge <digest@agenticedge.tech>")
    BOOKMARKS_JSON_PATH     - Path to local JSON file (optional, overrides Twitter API)
    REPO_PATH               - Repo root (defaults to parent of scripts/)
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Bootstrap — detect repo root
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = Path(os.environ.get("REPO_PATH", str(SCRIPT_DIR.parent))).resolve()
DIGESTS_DIR = REPO_ROOT / "web/src/content/digests"
PREMIUM_DIR = REPO_ROOT / "web/src/content/premium"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def slugify(text: str) -> str:
    """Lowercase, spaces to hyphens, strip non-alphanumeric except hyphens."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-")[:60]


def get_next_article_number() -> int:
    """Scan premium/ for files matching NNN-*.md, return max+1."""
    max_num = 0
    for f in PREMIUM_DIR.glob("*.md"):
        m = re.match(r"^(\d+)-", f.name)
        if m:
            max_num = max(max_num, int(m.group(1)))
    return max_num + 1


def markdown_to_simple_html(md: str) -> str:
    """Minimal markdown-to-HTML for email. No external deps."""
    lines = md.split("\n")
    html_lines = []
    in_frontmatter = False
    frontmatter_done = False
    fm_count = 0

    for line in lines:
        # Strip frontmatter
        if line.strip() == "---":
            fm_count += 1
            if fm_count <= 2:
                continue
        if fm_count < 2:
            continue

        # Headings
        if line.startswith("### "):
            content = line[4:]
            # Convert [text](url) inside heading
            content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', content)
            html_lines.append(f"<h3>{content}</h3>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        # Horizontal rule
        elif line.strip() == "---":
            html_lines.append("<hr>")
        # Italics-only line (taglines)
        elif re.match(r"^\*[^*]+\*$", line.strip()):
            html_lines.append(f"<p><em>{line.strip()[1:-1]}</em></p>")
        # Empty line
        elif line.strip() == "":
            html_lines.append("")
        else:
            # Inline links and bold
            processed = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', line)
            processed = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", processed)
            processed = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", processed)
            html_lines.append(f"<p>{processed}</p>")

    inner = "\n".join(html_lines)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{
    font-family: Georgia, 'Times New Roman', serif;
    max-width: 620px;
    margin: 0 auto;
    padding: 24px 16px;
    color: #1a1a1a;
    line-height: 1.7;
    background: #ffffff;
  }}
  h1, h2 {{ font-weight: 700; line-height: 1.3; }}
  h2 {{ font-size: 22px; margin: 32px 0 4px 0; border-bottom: 2px solid #7c3aed; padding-bottom: 4px; }}
  h3 {{ font-size: 17px; margin: 20px 0 6px 0; line-height: 1.4; }}
  p {{ margin: 6px 0 14px 0; }}
  a {{ color: #7c3aed; text-decoration: none; }}
  hr {{ border: none; border-top: 1px solid #eee; margin: 24px 0; }}
  em {{ font-style: italic; color: #555; }}
  .notice {{
    background: #fff8e1;
    border-left: 4px solid #f59e0b;
    padding: 12px 16px;
    margin-bottom: 24px;
    font-family: monospace;
    font-size: 13px;
    line-height: 1.5;
  }}
</style>
</head>
<body>
<div class="notice">
  &#9888; Review and edit by 6am PT. Articles are live at agenticedge.tech/digest<br>
  This test email was sent automatically. Cron fires at 6am PT Monday.
</div>
{inner}
</body>
</html>"""


# ---------------------------------------------------------------------------
# Twitter bookmarks
# ---------------------------------------------------------------------------

def _parse_bookmarks_json(raw: list, since_date: datetime) -> list[dict]:
    """Parse raw bookmark JSON (from file or Playwright scraper) into normalized dicts."""
    bookmarks = []
    for item in raw:
        tweeted_at_str = item.get("tweeted_at") or item.get("bookmark_date", "")
        try:
            tweeted_at = datetime.fromisoformat(tweeted_at_str.replace("Z", "+00:00"))
        except Exception:
            tweeted_at = since_date  # default: include it
        if tweeted_at >= since_date:
            bookmarks.append({
                "tweet_url": item.get("tweet_url", ""),
                "full_text": item.get("full_text", ""),
                "screen_name": item.get("screen_name", ""),
                "tweeted_at": tweeted_at.isoformat(),
            })
    return bookmarks


def fetch_twitter_bookmarks(since_date: datetime) -> list[dict]:
    """
    Fetch bookmarks via (in priority order):
    1. BOOKMARKS_JSON_PATH env var — local JSON file
    2. Playwright browser scraper (scripts/fetch_bookmarks.js) — uses Chrome login session
    3. Twitter API v2 — requires TWITTER_ACCESS_TOKEN + TWITTER_USER_ID

    Returns list of dicts with keys: tweet_url, full_text, screen_name, tweeted_at.
    """
    # 1. Local JSON file
    local_path = os.environ.get("BOOKMARKS_JSON_PATH", "")
    if local_path and Path(local_path).exists():
        log(f"Loading bookmarks from local file: {local_path}")
        with open(local_path) as f:
            raw = json.load(f)
        bookmarks = _parse_bookmarks_json(raw, since_date)
        log(f"Loaded {len(bookmarks)} bookmarks since {since_date.date()} from local file")
        return bookmarks

    # 2. Playwright browser scraper
    scraper_path = SCRIPT_DIR / "fetch_bookmarks.js"
    if scraper_path.exists():
        log("Running Playwright bookmark scraper...")
        try:
            result = subprocess.run(
                ["node", str(scraper_path), "--max", "200"],
                capture_output=True, text=True, timeout=120,
                cwd=str(REPO_ROOT)
            )
            if result.returncode == 0 and result.stdout.strip():
                raw = json.loads(result.stdout)
                bookmarks = _parse_bookmarks_json(raw, since_date)
                log(f"Playwright scraped {len(bookmarks)} bookmarks since {since_date.date()}")
                return bookmarks
            else:
                log(f"Playwright scraper failed (exit {result.returncode}): {result.stderr[:200]}")
                log("Falling back to Twitter API...")
        except subprocess.TimeoutExpired:
            log("Playwright scraper timed out. Falling back to Twitter API...")
        except json.JSONDecodeError as e:
            log(f"Playwright scraper returned invalid JSON: {e}. Falling back to Twitter API...")

    # 3. Twitter API v2
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    user_id = os.environ.get("TWITTER_USER_ID")
    if not access_token or not user_id:
        log("ERROR: TWITTER_ACCESS_TOKEN and TWITTER_USER_ID required (or set BOOKMARKS_JSON_PATH)")
        sys.exit(1)

    import urllib.request
    import urllib.parse

    url = f"https://api.twitter.com/2/users/{user_id}/bookmarks"
    params = {
        "max_results": "100",
        "tweet.fields": "text,author_id,created_at",
        "expansions": "author_id",
        "user.fields": "username,name",
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "AgenticEdgeDigest/1.0",
    }

    all_bookmarks = []
    next_token = None
    page = 0

    while True:
        page += 1
        p = dict(params)
        if next_token:
            p["pagination_token"] = next_token

        full_url = url + "?" + urllib.parse.urlencode(p)
        req = urllib.request.Request(full_url, headers=headers)

        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read())
                break
            except Exception as e:
                if attempt == 2:
                    log(f"Twitter API error after 3 attempts: {e}")
                    sys.exit(1)
                log(f"Twitter API attempt {attempt + 1} failed: {e}. Retrying in 5s...")
                time.sleep(5)

        # Build author map
        author_map = {}
        for user in data.get("includes", {}).get("users", []):
            author_map[user["id"]] = user.get("username", "unknown")

        tweets = data.get("data", [])
        if not tweets:
            break

        stop = False
        for tweet in tweets:
            created_at_str = tweet.get("created_at", "")
            try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            except Exception:
                created_at = datetime.now(timezone.utc)

            if created_at < since_date:
                stop = True
                break

            author_id = tweet.get("author_id", "")
            screen_name = author_map.get(author_id, "unknown")
            tweet_id = tweet.get("id", "")
            tweet_url = f"https://x.com/{screen_name}/status/{tweet_id}"

            all_bookmarks.append({
                "tweet_url": tweet_url,
                "full_text": tweet.get("text", ""),
                "screen_name": screen_name,
                "tweeted_at": created_at.isoformat(),
            })

        if stop:
            break

        next_token = data.get("meta", {}).get("next_token")
        if not next_token:
            break

        # Respect rate limits
        time.sleep(1)

    log(f"Fetched {len(all_bookmarks)} bookmarks from Twitter API (page {page})")
    return all_bookmarks


# ---------------------------------------------------------------------------
# Already-published URL extraction
# ---------------------------------------------------------------------------

def get_already_published_urls() -> set[str]:
    """
    Scan all digest and premium files.
    Extract tweet URLs (x.com/...) and vault article URLs.
    Returns a set of normalized URLs.
    """
    urls: set[str] = set()
    url_pattern = re.compile(r"https?://(?:x\.com|twitter\.com)/[^\s)\]\"']+")

    # Scan digests
    for f in DIGESTS_DIR.glob("*.md"):
        text = f.read_text(encoding="utf-8")
        for m in url_pattern.finditer(text):
            urls.add(m.group(0).rstrip(".,)"))

    # Scan premium articles — look for [Source: ...](url) lines
    source_pattern = re.compile(r"\[Source:[^\]]*\]\(([^)]+)\)")
    for f in PREMIUM_DIR.glob("*.md"):
        text = f.read_text(encoding="utf-8")
        for m in source_pattern.finditer(text):
            urls.add(m.group(1).rstrip(".,)"))
        # Also any x.com links anywhere in the file
        for m in url_pattern.finditer(text):
            urls.add(m.group(0).rstrip(".,)"))

    log(f"Found {len(urls)} already-published URLs")
    return urls


# ---------------------------------------------------------------------------
# Scoring with Claude
# ---------------------------------------------------------------------------

def score_and_filter_bookmarks(bookmarks: list[dict], min_score: int = 7) -> list[dict]:
    """Score each bookmark with Claude. Return those scoring >= min_score, sorted desc."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Batch into chunks of 20 to stay within context limits
    BATCH_SIZE = 20
    scored: list[dict] = []

    for i in range(0, len(bookmarks), BATCH_SIZE):
        batch = bookmarks[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        log(f"Scoring batch {batch_num} ({len(batch)} bookmarks)...")

        items_json = json.dumps(
            [
                {
                    "index": j,
                    "url": b["tweet_url"],
                    "text": b["full_text"][:500],
                    "author": b["screen_name"],
                }
                for j, b in enumerate(batch)
            ],
            indent=2,
        )

        prompt = f"""You are scoring Twitter bookmarks for the Agentic Edge newsletter.
Agentic Edge readers are senior engineers building AI agents in production.

Score each tweet 1-10 based on:
- Is it about agentic AI, agent frameworks, Claude/Claude Code, LLM tooling, or AI builder workflows?
- Is it actionable for an engineer building agents in production?
- Does it have a specific insight, number, or tool vs. generic hype?
- Is the source credible (known engineer, Anthropic, major lab, primary source)?

Scoring bands:
- 9-10: Major release, architectural insight, or primary source (Karpathy, Anthropic, major lab)
- 7-8: Solid tool drop, useful framework, good case study with specifics
- 5-6: Interesting but not essential for builders
- 1-4: Generic hype, not technical enough, or already widely known
- Hard skip (score 1): funding announcements, job posts, generic "AI will change everything"

Tweets to score:
{items_json}

Return ONLY a JSON array with exactly {len(batch)} objects, one per tweet, in the same order:
[
  {{
    "index": 0,
    "url": "...",
    "score": 8,
    "reason": "One sentence why.",
    "suggested_title": "Punchy title under 80 chars — specific, no hype words",
    "category": "tools"
  }},
  ...
]

Categories: tools, frameworks, benchmarks, workflow, analysis, release, news
"""

        for attempt in range(3):
            try:
                resp = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}],
                )
                raw = resp.content[0].text.strip()
                # Extract JSON array from response
                json_match = re.search(r"\[.*\]", raw, re.DOTALL)
                if not json_match:
                    raise ValueError("No JSON array in response")
                results = json.loads(json_match.group(0))
                break
            except Exception as e:
                if attempt == 2:
                    log(f"Scoring batch {batch_num} failed after 3 attempts: {e}")
                    # Give every item score 0 so they're skipped
                    results = [{"index": j, "url": b["tweet_url"], "score": 0, "reason": "error", "suggested_title": "", "category": ""} for j, b in enumerate(batch)]
                else:
                    log(f"Scoring attempt {attempt + 1} failed: {e}. Retrying in 10s...")
                    time.sleep(10)

        for r in results:
            idx = r.get("index", 0)
            if idx < len(batch):
                merged = dict(batch[idx])
                merged["score"] = r.get("score", 0)
                merged["reason"] = r.get("reason", "")
                merged["suggested_title"] = r.get("suggested_title", "")
                merged["category"] = r.get("category", "")
                scored.append(merged)

        time.sleep(2)  # Rate limit courtesy

    # Filter and sort
    filtered = [b for b in scored if b["score"] >= min_score]
    filtered.sort(key=lambda x: x["score"], reverse=True)
    log(f"Scored {len(scored)} bookmarks. {len(filtered)} scored >= {min_score}.")
    return filtered


# ---------------------------------------------------------------------------
# Digest planning
# ---------------------------------------------------------------------------

def plan_digest_structure(top_bookmarks: list[dict]) -> dict:
    """
    Given the top-scored bookmarks, ask Claude to:
    - Split into free (top 8) and pro (remaining) tiers
    - Group the top 8 into 3 sections with names and taglines
    - Return structured JSON
    """
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    free_items = top_bookmarks[:8]
    pro_items = top_bookmarks[8:]

    items_json = json.dumps(
        [
            {
                "index": i,
                "url": b["tweet_url"],
                "suggested_title": b["suggested_title"],
                "text": b["full_text"][:300],
                "score": b["score"],
                "category": b["category"],
                "reason": b["reason"],
            }
            for i, b in enumerate(free_items)
        ],
        indent=2,
    )

    prompt = f"""You are the editor of Agentic Edge, a newsletter for senior AI engineers.

You have 8 articles for this week's digest. Group them into exactly 3 sections.
Each section should have 2-4 articles. Order sections by importance (biggest news first).

Good section names from past issues: "The Leak", "Cognition", "Builder Tools", "Agent Ops",
"Working Smarter". Invent new names when the content calls for it.
Each section gets a short tagline in italics (one punchy sentence, max 10 words).

Articles:
{items_json}

Return ONLY JSON in this exact structure:
{{
  "sections": [
    {{
      "name": "Section Name",
      "tagline": "Punchy tagline here.",
      "article_indices": [0, 1, 2]
    }},
    {{
      "name": "Section Two",
      "tagline": "Tagline for section two.",
      "article_indices": [3, 4]
    }},
    {{
      "name": "Section Three",
      "tagline": "Tagline for section three.",
      "article_indices": [5, 6, 7]
    }}
  ]
}}

Every article index 0-7 must appear exactly once. Total must equal 8.
"""

    for attempt in range(3):
        try:
            resp = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.content[0].text.strip()
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object in response")
            plan = json.loads(json_match.group(0))

            # Validate: all indices 0-7 present
            all_indices = []
            for section in plan.get("sections", []):
                all_indices.extend(section.get("article_indices", []))
            if sorted(all_indices) != list(range(len(free_items))):
                raise ValueError(f"Article indices don't cover 0-{len(free_items)-1}: {sorted(all_indices)}")

            log(f"Digest plan: {[s['name'] for s in plan['sections']]}")
            return {
                "sections": plan["sections"],
                "free_bookmarks": free_items,
                "pro_bookmarks": pro_items,
            }
        except Exception as e:
            if attempt == 2:
                log(f"Planning failed after 3 attempts: {e}")
                raise
            log(f"Planning attempt {attempt + 1} failed: {e}. Retrying in 10s...")
            time.sleep(10)


# ---------------------------------------------------------------------------
# Vault article writing
# ---------------------------------------------------------------------------

ARTICLE_SYSTEM_PROMPT = """Write like a sharp senior engineer talking to a peer. Direct, opinionated, no fluff.
NEVER use: "delve", "landscape", "tapestry", "it's worth noting", "in conclusion", "game-changer", "revolutionize", "unlock", "empower", "leverage"
Short paragraphs (2-4 sentences max). Specific numbers when available. Named sources. Second person ("you", "your").
Start with the key insight — no preamble, no "In this article" throat-clearing.
Include at least 2 H2 sections (## Header).
End with the source line: [Source: @handle](tweet_url)
No em-dashes. Use periods and short sentences instead."""


def write_vault_article(
    bookmark: dict,
    suggested_title: str,
    tier: str,
    article_number: int,
    is_featured_free: bool = False,
    date_str: str = "",
) -> tuple[str, str]:
    """
    Write a full vault article for a bookmark.
    Returns (filename, content).
    """
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    slug = slugify(suggested_title)
    filename = f"{article_number}-{slug}.md"

    prompt = f"""Write a vault article for Agentic Edge newsletter about this tweet.

Tweet URL: {bookmark['tweet_url']}
Author: @{bookmark['screen_name']}
Tweet text: {bookmark['full_text']}

Suggested title: {suggested_title}
Score/reason: {bookmark.get('score', '')}/10 — {bookmark.get('reason', '')}
Category: {bookmark.get('category', '')}

Write a 300-500 word article. Requirements:
- Title: use the suggested title or improve it (must be specific, no hype)
- Description: one punchy sentence that makes someone click (under 20 words)
- At least 2 H2 sections
- Specific numbers, named tools, named people where relevant
- Tell the reader what to DO with this information
- End with: [Source: @{bookmark['screen_name']}]({bookmark['tweet_url']})

Return ONLY the article body (NO frontmatter). Start directly with the first paragraph.
"""

    description = ""
    title = suggested_title
    body = ""

    for attempt in range(3):
        try:
            resp = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=ARTICLE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            body = resp.content[0].text.strip()

            # Try to extract a better title from the first line if it looks like a heading
            first_line = body.split("\n")[0].strip()
            if first_line.startswith("# "):
                title = first_line[2:].strip()
                body = "\n".join(body.split("\n")[1:]).strip()
            break
        except Exception as e:
            if attempt == 2:
                log(f"Article writing failed for {suggested_title}: {e}")
                body = f"Article generation failed: {e}\n\n[Source: @{bookmark['screen_name']}]({bookmark['tweet_url']})"
            else:
                log(f"Article attempt {attempt + 1} failed: {e}. Retrying in 10s...")
                time.sleep(10)

    # Build description from first non-empty paragraph
    for line in body.split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("["):
            # Strip markdown links and bold for description
            desc_clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
            desc_clean = re.sub(r"\*+([^*]+)\*+", r"\1", desc_clean)
            description = desc_clean[:160]
            break

    # Category from bookmark
    category = bookmark.get("category", "analysis")
    if not category:
        category = "analysis"

    # Build frontmatter
    frontmatter_lines = [
        "---",
        f'title: "{title}"',
        f'description: "{description}"',
        f'date: "{date_str}"',
        f'tier: "{tier}"',
        f'category: "{category}"',
    ]
    if is_featured_free:
        frontmatter_lines.append("featured_free: true")
    frontmatter_lines.append("---")

    content = "\n".join(frontmatter_lines) + "\n\n" + body + "\n"
    return filename, content


# ---------------------------------------------------------------------------
# Digest markdown builder
# ---------------------------------------------------------------------------

def build_digest_markdown(plan: dict, article_files: dict, date_str: str) -> str:
    """
    Assemble the digest markdown.
    article_files: {bookmark_index: (filename, title)} for free articles
    """
    lines = [
        "---",
        f'title: "Agentic Edge Digest - {date_str}"',
        f'date: "{date_str}"',
        "---",
        "",
    ]

    free_bookmarks = plan["free_bookmarks"]

    for section_idx, section in enumerate(plan["sections"]):
        if section_idx > 0:
            lines.append("")
            lines.append("---")
            lines.append("")

        lines.append(f"## {section['name']}")
        lines.append("")
        lines.append(f"*{section['tagline']}*")
        lines.append("")

        for article_idx in section["article_indices"]:
            bookmark = free_bookmarks[article_idx]
            if article_idx in article_files:
                filename, title, article_number = article_files[article_idx]
                # Build slug from filename (strip .md)
                slug = filename.replace(".md", "")
                url = f"https://agenticedge.tech/pro/{slug}"

                # Build summary from reason + text
                summary = bookmark.get("reason", "")
                if not summary:
                    # Trim tweet text
                    summary = bookmark["full_text"][:200].replace("\n", " ")
                if len(summary) < 80:
                    # Pad with tweet text
                    extra = bookmark["full_text"][:300].replace("\n", " ")
                    summary = f"{summary} {extra}"[:280]

                lines.append(f"### [{title}]({url})")
                lines.append(summary.strip())
                lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Git operations
# ---------------------------------------------------------------------------

def commit_and_push(date_str: str):
    """Stage digest and premium files, commit, push."""
    def run_git(cmd: list[str]):
        result = subprocess.run(
            ["git"] + cmd,
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    # Set identity for CI
    run_git(["config", "user.email", "bot@agenticedge.tech"])
    run_git(["config", "user.name", "Agentic Edge Bot"])

    # Stage files
    run_git(["add", "web/src/content/digests/", "web/src/content/premium/"])

    # Check if there's anything to commit
    status = run_git(["status", "--porcelain"])
    if not status:
        log("Nothing to commit — skipping git commit")
        return

    run_git(["commit", "-m", f"Weekly digest {date_str}"])
    log(f"Committed: Weekly digest {date_str}")

    run_git(["push"])
    log("Pushed to remote")


# ---------------------------------------------------------------------------
# Test email
# ---------------------------------------------------------------------------

def send_test_email(digest_content: str, date_str: str):
    """Send test email to pillicdj@gmail.com via Resend."""
    import urllib.request

    api_key = os.environ.get("RESEND_API_KEY")
    from_addr = os.environ.get("RESEND_FROM", "Agentic Edge <digest@agenticedge.tech>")

    if not api_key:
        log("RESEND_API_KEY not set — skipping test email")
        return

    html_body = markdown_to_simple_html(digest_content)

    payload = json.dumps({
        "from": from_addr,
        "to": ["pillicdj@gmail.com"],
        "subject": f"[REVIEW] Agentic Edge — {date_str} (sends 6am PT)",
        "html": html_body,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            log(f"Test email sent. ID: {result.get('id', 'unknown')}")
            return
        except Exception as e:
            if attempt == 2:
                log(f"Test email failed after 3 attempts: {e}")
            else:
                log(f"Email attempt {attempt + 1} failed: {e}. Retrying in 5s...")
                time.sleep(5)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    log("=== Agentic Edge Weekly Digest Generator ===")
    log(f"Repo root: {REPO_ROOT}")

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Last Sunday = 7 days ago
    since_date = datetime.now(timezone.utc) - timedelta(days=7)
    log(f"Fetching bookmarks since {since_date.date()}")

    # 1. Fetch bookmarks
    bookmarks = fetch_twitter_bookmarks(since_date)
    if not bookmarks:
        log("No bookmarks found since last Sunday. Exiting cleanly.")
        return

    # 2. Diff against already-published
    published_urls = get_already_published_urls()
    new_bookmarks = [
        b for b in bookmarks
        if b["tweet_url"] not in published_urls
    ]
    log(f"{len(new_bookmarks)} new bookmarks (filtered {len(bookmarks) - len(new_bookmarks)} already published)")

    if not new_bookmarks:
        log("No new bookmarks after deduplication. Exiting cleanly.")
        return

    # 3. Score and filter
    scored = score_and_filter_bookmarks(new_bookmarks, min_score=7)
    if not scored:
        log("No bookmarks scored >= 7. Exiting cleanly.")
        return

    if len(scored) < 8:
        log(f"WARNING: Only {len(scored)} bookmarks scored >= 7. Need at least 8 for a full digest.")
        log("Proceeding with what we have...")

    # Cap at 18 total (8 free + up to 10 pro)
    scored = scored[:18]
    log(f"Using top {len(scored)} bookmarks (free: {min(8, len(scored))}, pro: {max(0, len(scored) - 8)})")

    # 4. Plan structure
    plan = plan_digest_structure(scored)

    # 5. Write vault articles
    next_num = get_next_article_number()
    log(f"Starting article numbering at {next_num}")

    article_files: dict = {}  # {free_bookmark_index: (filename, title, article_number)}
    files_written: list[str] = []

    # Free articles (top 8, in the digest)
    for i, bookmark in enumerate(plan["free_bookmarks"]):
        is_featured = i == 0  # highest score = first item
        tier = "free"
        article_num = next_num + i

        log(f"Writing free article {article_num}: {bookmark['suggested_title'][:60]}...")
        filename, content = write_vault_article(
            bookmark=bookmark,
            suggested_title=bookmark["suggested_title"],
            tier=tier,
            article_number=article_num,
            is_featured_free=is_featured,
            date_str=date_str,
        )

        out_path = PREMIUM_DIR / filename
        out_path.write_text(content, encoding="utf-8")
        files_written.append(str(out_path))
        log(f"  Wrote {filename}")

        # Extract title from frontmatter for digest links
        title_match = re.search(r'^title:\s+"([^"]+)"', content, re.MULTILINE)
        title = title_match.group(1) if title_match else bookmark["suggested_title"]
        article_files[i] = (filename, title, article_num)

        time.sleep(1)  # Courteous pacing

    # Pro-only articles (vault only, not in homepage digest)
    pro_start_num = next_num + len(plan["free_bookmarks"])
    for j, bookmark in enumerate(plan["pro_bookmarks"]):
        article_num = pro_start_num + j
        log(f"Writing pro article {article_num}: {bookmark['suggested_title'][:60]}...")
        filename, content = write_vault_article(
            bookmark=bookmark,
            suggested_title=bookmark["suggested_title"],
            tier="pro",
            article_number=article_num,
            date_str=date_str,
        )

        out_path = PREMIUM_DIR / filename
        out_path.write_text(content, encoding="utf-8")
        files_written.append(str(out_path))
        log(f"  Wrote {filename} (pro vault only)")

        time.sleep(1)

    # 6. Build digest markdown
    digest_content = build_digest_markdown(plan, article_files, date_str)
    digest_filename = f"{date_str}-digest.md"
    digest_path = DIGESTS_DIR / digest_filename
    digest_path.write_text(digest_content, encoding="utf-8")
    files_written.append(str(digest_path))
    log(f"Wrote digest: {digest_filename}")

    # Preview
    log("--- Digest preview ---")
    for line in digest_content.split("\n")[:30]:
        print(line)
    log("--- End preview ---")

    # 7. Commit and push
    try:
        commit_and_push(date_str)
    except subprocess.CalledProcessError as e:
        log(f"Git error: {e.stderr}")
        log("Files were written locally. Manual push required.")

    # 8. Send test email
    send_test_email(digest_content, date_str)

    log(f"=== Done. {len(files_written)} files written. ===")
    for f in files_written:
        log(f"  {f}")


if __name__ == "__main__":
    main()
