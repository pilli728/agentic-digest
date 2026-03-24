"""Main orchestration pipeline for the Agentic Digest.

Pipeline steps are exposed as importable functions so the API server can call them individually.
The CLI entry point still works as before.
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add src directory to path for imports
_src_path = Path(__file__).parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

import yaml
from core.fetcher import fetch_articles
from core.filter import filter_and_rank
from core.generator import generate_digest
from database import DigestDatabase
from outputs.email_output import send_digest_email
from outputs.website_output import write_digest_to_website


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}


# --- Decomposed pipeline steps (used by API server) ---

def pipeline_fetch(lookback_hours: int = 24) -> list:
    """Step 1: Fetch articles from RSS feeds."""
    return fetch_articles(lookback_hours=lookback_hours)


def pipeline_store(db: DigestDatabase, articles: list) -> list:
    """Step 2: Store articles and deduplicate. Returns only new articles."""
    return db.store_articles(articles)


def pipeline_rank(articles: list, top_n: int = 999, model: str = "claude-haiku-4-5-20251001", preference_context: str = "") -> list:
    """Step 3: Filter and rank with Claude. Default top_n=999 ranks ALL articles."""
    return filter_and_rank(articles, top_n=top_n, model=model, preference_context=preference_context)


def pipeline_generate(articles: list, mode: str = "daily", date: str = None):
    """Step 4: Generate digest markdown from ranked articles."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    return generate_digest(articles, mode=mode, date=date)


def pipeline_publish(db: DigestDatabase, digest, config: dict = None):
    """Step 5: Publish digest to website and/or email."""
    if config is None:
        config = load_config()
    outputs_config = config.get("outputs", {})
    today = digest.date

    # Store digest in database
    digest_id = db.store_digest(digest)

    # Save to output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    filename = f"{today}_digest_{digest.mode}.md"
    output_path = output_dir / filename
    output_path.write_text(digest.content)

    results = {"digest_id": digest_id, "email_sent": False, "website_published": False}

    # Email output
    email_enabled = outputs_config.get("email", {}).get("enabled", False)
    if email_enabled:
        email_to = outputs_config.get("email", {}).get("to")
        if send_digest_email(digest.content, email_to=email_to):
            db.mark_email_sent(digest_id)
            results["email_sent"] = True

    # Website output
    website_enabled = outputs_config.get("website", {}).get("enabled", False)
    if website_enabled:
        content_dir = outputs_config.get("website", {}).get("content_dir", "web/src/content/digests")
        if write_digest_to_website(digest.content, today, content_dir):
            db.mark_website_published(digest_id)
            results["website_published"] = True

    return results


# --- Full pipeline (CLI and backward compat) ---

def run_pipeline(
    mode: str = "daily",
    dry_run: bool = False,
    email_only: bool = False,
    website_only: bool = False,
) -> bool:
    """Run the complete digest pipeline."""
    print(f"\n=== Agentic Edge {mode.title()} Digest ===\n")

    config = load_config()
    digest_config = config.get("digest", {})
    model = config.get("model", "claude-haiku-4-5-20251001")

    if mode == "weekly":
        lookback_hours = digest_config.get("lookback_hours_weekly", 168)
        top_stories = digest_config.get("weekly_top_stories", 25)
    else:
        lookback_hours = digest_config.get("lookback_hours_daily", 24)
        top_stories = digest_config.get("daily_top_stories", 15)

    db = DigestDatabase()

    # Step 1: Fetch
    print("  [1/5] Fetching articles from RSS feeds...")
    articles = pipeline_fetch(lookback_hours=lookback_hours)
    if not articles:
        print("  ✗ No articles found.")
        db.close()
        return False

    # Step 2: Deduplicate
    print("  [2/5] Deduplicating articles...")
    new_articles = pipeline_store(db, articles)
    if not new_articles:
        print("  ⚠ All articles were duplicates.")
        db.close()
        return False

    # Step 3: Rank
    print(f"  [3/5] Filtering and ranking with Claude ({model})...")
    ranked_articles = pipeline_rank(new_articles, top_n=top_stories, model=model)
    if not ranked_articles:
        print("  ✗ Claude filtering produced no results.")
        db.close()
        return False

    # Persist scores back to DB
    db.update_article_scores(ranked_articles)

    # Step 4: Generate
    print("  [4/5] Generating digest...")
    today = datetime.now().strftime("%Y-%m-%d")
    if db.digest_exists(today):
        print(f"  ⚠ Digest for {today} already exists. Skipping.")
        db.close()
        return False

    digest = pipeline_generate(ranked_articles, mode=mode, date=today)

    # Step 5: Deliver
    print("  [5/5] Delivering digest...")
    if dry_run:
        print("  [DRY RUN] Skipping email and website output.")
        print("\n--- DIGEST PREVIEW ---\n")
        print(digest.content)
        print("\n--- END PREVIEW ---\n")
        db.close()
        return True

    # Build outputs config based on flags
    publish_config = load_config()
    if email_only:
        publish_config.setdefault("outputs", {}).setdefault("website", {})["enabled"] = False
    if website_only:
        publish_config.setdefault("outputs", {}).setdefault("email", {})["enabled"] = False

    results = pipeline_publish(db, digest, publish_config)
    db.close()

    print(f"\n✓ Pipeline complete. Digest for {today} ready.\n")
    return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Agentic Edge Daily Digest Pipeline")
    parser.add_argument("--mode", choices=["daily", "weekly"], default="daily")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--email-only", action="store_true")
    parser.add_argument("--website-only", action="store_true")
    args = parser.parse_args()

    success = run_pipeline(
        mode=args.mode,
        dry_run=args.dry_run,
        email_only=args.email_only,
        website_only=args.website_only,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
