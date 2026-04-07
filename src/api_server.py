"""
Unified API server for the Agentic Digest platform.

Handles:
- Article retrieval (by tier, flat list, stats)
- Feedback (thumbs up/down, comments)
- Pipeline control (fetch, rank)
- Digest preview and publish

Run: python3 src/api_server.py
All endpoints on: http://localhost:8000
"""

import json
import os
import re
import threading
import time
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime
import sys
from pathlib import Path

# --- In-memory rate limiter (sliding window) ---
_rate_limit_store: dict[str, list[float]] = defaultdict(list)

# Load .env file
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent.parent / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
    else:
        load_dotenv()  # Try CWD
except ImportError:
    pass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from database import DigestDatabase

# Pipeline imports — optional, only needed for /api/pipeline/* endpoints
# These may not be present in production deployments
try:
    from orchestrator import (
        load_config, pipeline_fetch, pipeline_store, pipeline_rank, pipeline_publish
    )
    from core.generator import generate_digest
    from core.local_filter import filter_noise_from_db
    from core.trending_fetcher import fetch_all_trending
    _HAS_PIPELINE = True
except ImportError:
    _HAS_PIPELINE = False
    print("  [WARN] Pipeline modules not available — pipeline endpoints disabled")


# --- Stripe checkout ---
def create_stripe_checkout(price_key: str, customer_email: str = None) -> str:
    """Create a Stripe Checkout session. Returns checkout URL or None."""
    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        print("  [Stripe] No STRIPE_SECRET_KEY in env")
        return None

    try:
        import stripe
        stripe.api_key = stripe_key

        # Price IDs from Stripe Dashboard
        price_ids = {
            "pro_monthly": os.environ.get("STRIPE_PRICE_PRO_MONTHLY", ""),
            "pro_annual": os.environ.get("STRIPE_PRICE_PRO_ANNUAL", ""),
            "founding_monthly": os.environ.get("STRIPE_PRICE_FOUNDING", ""),
            "inner_monthly": os.environ.get("STRIPE_PRICE_FOUNDING", ""),  # alias
            "inner_annual": os.environ.get("STRIPE_PRICE_INNER_ANNUAL", ""),
        }

        price_id = price_ids.get(price_key)
        if not price_id:
            return None

        site_url = os.environ.get("SITE_URL", "http://localhost:4321")
        inner_prices = {
            os.environ.get("STRIPE_PRICE_FOUNDING", ""),
            os.environ.get("STRIPE_PRICE_INNER_ANNUAL", ""),
        }
        tier = "inner" if price_id in inner_prices else "pro"

        session_params = {
            "mode": "subscription",
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": f"{site_url}/?upgraded=true&session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{site_url}/upgrade",
            "allow_promotion_codes": True,
        }
        if customer_email:
            session_params["customer_email"] = customer_email
        session = stripe.checkout.Session.create(**session_params)
        return session.url

    except Exception as e:
        print(f"Stripe error: {e}")
        return None


# --- Global state ---
pipeline_status = {"state": "idle", "message": "", "last_fetch": None}
pipeline_lock = threading.Lock()


def run_background_fetch():
    """Run the fetch+dedupe+rank pipeline in a background thread."""
    global pipeline_status

    with pipeline_lock:
        if pipeline_status["state"] == "fetching":
            return  # Already running
        pipeline_status = {"state": "fetching", "message": "Fetching articles from RSS feeds..."}

    try:
        config = load_config()
        model = config.get("model", "claude-haiku-4-5-20251001")
        lookback_hours = config.get("digest", {}).get("lookback_hours_daily", 24)

        db = DigestDatabase()

        # Step 1: Fetch Layer 0 (newsletters) + Layer 1 (primary sources)
        pipeline_status["message"] = "Fetching from top newsletters and builder sources..."
        articles = pipeline_fetch(lookback_hours=lookback_hours)

        # Step 1b: Fetch trending from HN + Reddit (Layer 1 supplement)
        pipeline_status["message"] = "Fetching trending from HN and Reddit..."
        try:
            trending = fetch_all_trending()
            articles.extend(trending)
        except Exception as e:
            print(f"  [WARN] Trending fetch failed: {e}")

        if not articles:
            pipeline_status = {"state": "idle", "message": "No articles found", "last_fetch": datetime.now().isoformat()}
            db.close()
            return

        # Step 2: Deduplicate
        pipeline_status["message"] = f"Deduplicating {len(articles)} articles..."
        new_articles = pipeline_store(db, articles)

        if not new_articles:
            pipeline_status = {"state": "idle", "message": "All articles were duplicates", "last_fetch": datetime.now().isoformat()}
            db.close()
            return

        # Step 3: Score articles — local keyword filter (no API key needed)
        pipeline_status["message"] = f"Scoring and filtering {len(new_articles)} articles..."
        stats = filter_noise_from_db(db)

        # Step 4: Try Claude ranking for top articles if API key is available
        try:
            import os
            if os.environ.get("ANTHROPIC_API_KEY"):
                pipeline_status["message"] = "Enhancing rankings with Claude..."
                # Get high-scoring articles for Claude to refine
                from core.models import Article as ArticleModel
                cursor = db.conn.cursor()
                cursor.execute("""
                    SELECT id, source, tier, title, link, summary, published_at, relevance_score
                    FROM articles WHERE relevance_score >= 4
                    ORDER BY relevance_score DESC LIMIT 50
                """)
                top_articles = []
                for row in cursor.fetchall():
                    r = dict(row)
                    top_articles.append(ArticleModel(
                        source=r["source"], tier=r["tier"], title=r["title"],
                        link=r["link"], summary=r.get("summary") or "",
                        published=r.get("published_at") or "", id=r["id"],
                        relevance_score=r.get("relevance_score"),
                    ))
                if top_articles:
                    ranked = pipeline_rank(top_articles, top_n=999, model=model)
                    if ranked:
                        db.update_article_scores(ranked)
        except Exception:
            pass  # Claude ranking is optional — local filter is sufficient

        pipeline_status = {
            "state": "idle",
            "message": f"Done! {stats['kept']} relevant articles, {stats['filtered']} noise filtered out.",
            "last_fetch": datetime.now().isoformat(),
            "new_articles": len(new_articles),
            "kept": stats["kept"],
            "filtered": stats["filtered"],
        }

        db.close()

    except Exception as e:
        pipeline_status = {"state": "error", "message": str(e)[:200], "last_fetch": datetime.now().isoformat()}


class APIHandler(BaseHTTPRequestHandler):
    """Unified HTTP request handler for all API endpoints."""

    def _check_rate_limit(self, key, max_requests=5, window_seconds=60):
        """Return True if rate limited (too many requests). Sliding window."""
        now = time.time()
        timestamps = _rate_limit_store[key]
        # Purge old entries outside the window
        _rate_limit_store[key] = [t for t in timestamps if now - t < window_seconds]
        if len(_rate_limit_store[key]) >= max_requests:
            return True
        _rate_limit_store[key].append(now)
        return False

    def _check_admin_auth(self, body=None):
        """Check ADMIN_API_KEY from body or Authorization header. Returns True if authorized."""
        admin_key = os.environ.get("ADMIN_API_KEY", "")
        if not admin_key:
            # No key configured — reject all admin requests in production
            if os.environ.get("RAILWAY_ENVIRONMENT"):
                self.send_json({"success": False, "message": "Admin auth not configured"}, status=401)
                return False
            # Allow in local dev if no key is set
            return True

        # Check body field
        if body and body.get("api_key") == admin_key:
            return True

        # Check Authorization header
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer ") and auth_header[7:] == admin_key:
            return True

        self.send_json({"success": False, "message": "Unauthorized"}, status=401)
        return False

    def _get_client_ip(self):
        """Get the client IP, respecting X-Forwarded-For behind a proxy."""
        forwarded = self.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.client_address[0]

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/debug":
            import os
            db_path = os.environ.get("DATABASE_PATH", "data/digest.db")
            db_abs = os.path.abspath(db_path)
            db_exists = os.path.exists(db_abs)
            db_size = os.path.getsize(db_abs) if db_exists else 0
            try:
                db = DigestDatabase()
                cursor = db.conn.cursor()
                cursor.execute("SELECT tier, COUNT(*) FROM subscribers GROUP BY tier")
                subs = dict(cursor.fetchall())
                cursor.execute("SELECT COUNT(*) FROM subscribers")
                total = cursor.fetchone()[0]
                db.close()
            except Exception as e:
                subs = {}
                total = f"error: {e}"
            self.send_json({
                "cwd": os.getcwd(),
                "database_path_env": db_path,
                "database_path_abs": db_abs,
                "db_file_exists": db_exists,
                "db_file_size_bytes": db_size,
                "subscribers_total": total,
                "subscribers_by_tier": subs,
            })

        elif path == "/api/articles":
            db = DigestDatabase()
            articles = db.get_all_articles()
            db.close()
            self.send_json({"success": True, "total": len(articles), "articles": articles})

        elif path == "/api/articles/by-tier":
            db = DigestDatabase()
            by_tier = db.get_articles_by_tier()
            db.close()
            self.send_json({"success": True, "articles_by_tier": by_tier})

        elif path == "/api/articles/stats":
            db = DigestDatabase()
            stats = db.get_stats()
            db.close()
            self.send_json({"success": True, **stats})

        elif path == "/api/feedback/summary":
            db = DigestDatabase()
            summary = db.get_feedback_summary()
            db.close()
            self.send_json(summary)

        elif path.startswith("/api/feedback/article/"):
            article_id = path.split("/")[-1]
            db = DigestDatabase()
            feedback = db.get_article_feedback(article_id)
            db.close()
            self.send_json(feedback)

        elif path == "/api/curate/state":
            db = DigestDatabase()
            articles = db.get_all_articles()

            # Get latest curation feedback for each article
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT article_id, reaction, MAX(created_at) as latest
                FROM feedback
                WHERE reaction IN ('newsletter_include', 'newsletter_skip', 'newsletter_maybe', 'newsletter_remove')
                GROUP BY article_id
                HAVING created_at = MAX(created_at)
            """)
            # Map article_id to latest curation state
            states = {}
            for row in cursor.fetchall():
                r = dict(row)
                reaction = r["reaction"]
                if reaction == "newsletter_include":
                    states[r["article_id"]] = "accepted"
                elif reaction == "newsletter_skip":
                    states[r["article_id"]] = "skipped"
                elif reaction == "newsletter_maybe":
                    states[r["article_id"]] = "maybe"
                elif reaction == "newsletter_remove":
                    states[r["article_id"]] = "candidate"

            # Also get rank order for accepted articles
            cursor.execute("""
                SELECT article_id, created_at
                FROM feedback
                WHERE reaction = 'newsletter_include'
                ORDER BY created_at ASC
            """)
            accept_order = {}
            for i, row in enumerate(cursor.fetchall()):
                aid = dict(row)["article_id"]
                if states.get(aid) == "accepted":
                    accept_order[aid] = i

            # Get latest editor notes
            cursor.execute("""
                SELECT article_id, comment
                FROM feedback
                WHERE reaction = 'editor_note' AND comment IS NOT NULL
                AND created_at = (
                    SELECT MAX(f2.created_at) FROM feedback f2
                    WHERE f2.article_id = feedback.article_id AND f2.reaction = 'editor_note'
                )
            """)
            editor_notes = {dict(r)["article_id"]: dict(r)["comment"] for r in cursor.fetchall()}

            # Auto-summarize articles with bad/missing summaries using Claude
            try:
                from core.summarizer import batch_summarize, needs_summary
                articles_needing_summary = [
                    a for a in articles if needs_summary(a.get("summary") or a.get("why_it_matters") or "")
                ]
                if articles_needing_summary:
                    summaries = batch_summarize(articles_needing_summary)
                    if summaries:
                        cursor = db.conn.cursor()
                        for aid, summary in summaries.items():
                            cursor.execute("UPDATE articles SET summary = ? WHERE id = ?", (summary, aid))
                            # Also update in-memory
                            for a in articles:
                                if a["id"] == aid:
                                    a["summary"] = summary
                        db.conn.commit()
            except Exception as e:
                print(f"  [WARN] Auto-summarize failed: {e}")

            db.close()

            # Surface only what's worth your time:
            # - Tier 0/1 trusted sources — but cap noisy ones to top 5 by score
            # - Trending (HN/Reddit) — only score >= 5
            TRUSTED_TIERS = {0, 1}
            MAX_PER_SOURCE = 5

            # Pre-sort: group candidates by source, pick top N per source
            source_buckets = {}
            acted_on = []
            for a in articles:
                state = states.get(a["id"], "candidate")
                a["curation_state"] = state
                a["accept_order"] = accept_order.get(a["id"], 999999)
                a["editor_note"] = editor_notes.get(a["id"], "")

                if state != "candidate":
                    acted_on.append(a)
                    continue

                source_buckets.setdefault(a.get("source", ""), []).append(a)

            curated = list(acted_on)

            for source, items in source_buckets.items():
                # Sort by score descending within each source
                items.sort(key=lambda x: x.get("relevance_score") or 0, reverse=True)
                tier = items[0].get("tier", 99) if items else 99
                is_trending = "(Trending)" in source

                if tier in TRUSTED_TIERS:
                    # Trusted sources — top N per source
                    curated.extend(items[:MAX_PER_SOURCE])
                elif is_trending and (items[0].get("relevance_score") or 0) >= 5:
                    # Trending — only the best ones
                    curated.extend([a for a in items[:MAX_PER_SOURCE]
                                    if (a.get("relevance_score") or 0) >= 5])

            self.send_json({"success": True, "articles": curated})

        elif path == "/api/topics":
            if not self._check_admin_auth():
                return
            db = DigestDatabase()
            cursor = db.conn.cursor()
            cursor.execute("SELECT id, title, synthesis, sort_order, created_at FROM digest_topics ORDER BY sort_order")
            topics = []
            for row in cursor.fetchall():
                t = dict(row)
                cursor.execute("""
                    SELECT a.id, a.title, a.source, a.link, a.summary, a.relevance_score
                    FROM articles a JOIN topic_articles ta ON a.id = ta.article_id
                    WHERE ta.topic_id = ?
                """, (t["id"],))
                t["articles"] = [dict(r) for r in cursor.fetchall()]
                topics.append(t)
            db.close()
            self.send_json({"success": True, "topics": topics})

        elif path == "/api/pipeline/status":
            self.send_json(pipeline_status)

        elif path == "/api/digest/preview":
            db = DigestDatabase()
            cursor = db.conn.cursor()

            # Load topics with their articles
            cursor.execute("SELECT id, title, synthesis FROM digest_topics ORDER BY sort_order")
            topic_rows = cursor.fetchall()

            if not topic_rows:
                db.close()
                self.send_json({"success": True, "markdown": "*No topics yet. Accept articles into topics to build your digest.*", "article_count": 0})
            else:
                topics_data = []
                premium_topics = []
                total_articles = 0
                for trow in topic_rows:
                    t = dict(trow)
                    cursor.execute("""
                        SELECT a.title, a.source, a.link, a.summary
                        FROM articles a JOIN topic_articles ta ON a.id = ta.article_id
                        WHERE ta.topic_id = ?
                    """, (t["id"],))
                    t_articles = [dict(r) for r in cursor.fetchall()]
                    total_articles += len(t_articles)
                    topic_entry = {
                        "title": t["title"],
                        "synthesis": t.get("synthesis") or "",
                        "articles": t_articles,
                    }
                    # Premium/locked topics go last
                    if "unlock" in t["title"].lower() or "playbook" in t["title"].lower() or "premium" in t["title"].lower():
                        premium_topics.append(topic_entry)
                    else:
                        topics_data.append(topic_entry)
                # Append premium at the end
                topics_data.extend(premium_topics)

                db.close()

                # Generate using voice-powered writer
                try:
                    from core.digest_writer import write_digest
                    markdown = write_digest(topics_data)
                    self.send_json({"success": True, "markdown": markdown, "article_count": total_articles})
                except Exception as e:
                    self.send_json({"success": True, "markdown": f"*Error generating digest: {e}*", "article_count": total_articles})

        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/digest/iterate":
            body = self.read_body()
            if not body:
                return
            if not self._check_admin_auth(body):
                return
            # Rate limit: max 10 per minute per IP
            client_ip = self._get_client_ip()
            if self._check_rate_limit(f"iterate:{client_ip}", max_requests=10, window_seconds=60):
                self.send_json({"success": False, "message": "Rate limited. Try again shortly."}, status=429)
                return
            current_draft = body.get("current_draft", "")
            feedback = body.get("feedback", "")

            if not current_draft:
                self.send_json({"success": False, "message": "No draft to iterate on"}, status=400)
                return

            try:
                from dotenv import load_dotenv
                load_dotenv()
                from anthropic import Anthropic
                client = Anthropic()

                # Use Haiku for iterations (fast + cheap)
                # Switch to claude-sonnet-4-6-20250514 when available on your plan
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=8000,
                    system="You are editing a newsletter draft. Apply the feedback and return the FULL updated newsletter. Keep the same voice, structure, and style. Only change what the feedback asks for. Return ONLY the updated markdown, no preamble.",
                    messages=[{
                        "role": "user",
                        "content": f"Current draft:\n\n{current_draft}\n\nFeedback:\n{feedback}\n\nReturn the full updated newsletter with the feedback applied."
                    }]
                )
                new_markdown = response.content[0].text.strip()
                self.send_json({"success": True, "markdown": new_markdown})
            except Exception as e:
                self.send_json({"success": False, "message": str(e)[:200]}, status=500)

        elif path == "/api/feedback":
            body = self.read_body()
            if not body:
                return
            article_id = body.get("articleId")
            reaction = body.get("reaction")
            comment = body.get("comment")

            if not article_id:
                self.send_json({"success": False, "message": "Missing articleId"}, status=400)
                return

            db = DigestDatabase()
            success = db.add_feedback(article_id, reaction, comment)
            db.close()

            self.send_json({
                "success": success,
                "message": "Feedback saved!" if success else "Error saving feedback",
                "preview_changed": True,
            })

        elif path == "/api/topics":
            body = self.read_body()
            if not body:
                return
            if not self._check_admin_auth(body):
                return
            action = body.get("action", "create")
            db = DigestDatabase()
            cursor = db.conn.cursor()

            if action == "create":
                import hashlib
                topic_id = body.get("id") or hashlib.sha256(
                    f"{body.get('title', '')}{datetime.now().isoformat()}".encode()
                ).hexdigest()[:16]
                title = body.get("title", "Untitled Topic")
                synthesis = body.get("synthesis", "")
                article_ids = body.get("article_ids", [])
                # Get next sort order
                cursor.execute("SELECT COALESCE(MAX(sort_order), -1) + 1 FROM digest_topics")
                sort_order = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT OR REPLACE INTO digest_topics (id, title, synthesis, sort_order, created_at) VALUES (?, ?, ?, ?, ?)",
                    (topic_id, title, synthesis, sort_order, datetime.now().isoformat())
                )
                for aid in article_ids:
                    cursor.execute("INSERT OR IGNORE INTO topic_articles (topic_id, article_id) VALUES (?, ?)", (topic_id, aid))
                db.conn.commit()
                self.send_json({"success": True, "topic_id": topic_id})

            elif action == "update":
                topic_id = body.get("id")
                if not topic_id:
                    self.send_json({"success": False, "message": "Missing topic id"}, status=400)
                    db.close()
                    return
                if "title" in body:
                    cursor.execute("UPDATE digest_topics SET title = ? WHERE id = ?", (body["title"], topic_id))
                if "synthesis" in body:
                    cursor.execute("UPDATE digest_topics SET synthesis = ? WHERE id = ?", (body["synthesis"], topic_id))
                db.conn.commit()
                self.send_json({"success": True})

            elif action == "add_article":
                topic_id = body.get("id")
                article_id = body.get("article_id")
                cursor.execute("INSERT OR IGNORE INTO topic_articles (topic_id, article_id) VALUES (?, ?)", (topic_id, article_id))
                db.conn.commit()
                self.send_json({"success": True})

            elif action == "remove_article":
                topic_id = body.get("id")
                article_id = body.get("article_id")
                cursor.execute("DELETE FROM topic_articles WHERE topic_id = ? AND article_id = ?", (topic_id, article_id))
                db.conn.commit()
                self.send_json({"success": True})

            elif action == "delete":
                topic_id = body.get("id")
                cursor.execute("DELETE FROM topic_articles WHERE topic_id = ?", (topic_id,))
                cursor.execute("DELETE FROM digest_topics WHERE id = ?", (topic_id,))
                db.conn.commit()
                self.send_json({"success": True})

            elif action == "reorder":
                order = body.get("order", [])
                for i, tid in enumerate(order):
                    cursor.execute("UPDATE digest_topics SET sort_order = ? WHERE id = ?", (i, tid))
                db.conn.commit()
                self.send_json({"success": True})

            else:
                self.send_json({"success": False, "message": f"Unknown action: {action}"}, status=400)

            db.close()

        elif path == "/api/pipeline/fetch":
            if not self._check_admin_auth():
                return
            if not _HAS_PIPELINE:
                self.send_json({"success": False, "message": "Pipeline not available in this deployment"}, status=501)
                return
            # Start background fetch
            if pipeline_status.get("state") == "fetching":
                self.send_json({"success": True, "message": "Already fetching", "status": pipeline_status})
                return

            thread = threading.Thread(target=run_background_fetch, daemon=True)
            thread.start()
            self.send_json({"success": True, "message": "Fetch started in background", "status": pipeline_status})

        elif path == "/api/digest/publish":
            body = self.read_body() or {}
            if not self._check_admin_auth(body):
                return
            markdown = body.get("markdown", "")

            if not markdown:
                self.send_json({"success": False, "message": "No content to publish. Preview first, then publish."})
                return

            today = datetime.now().strftime("%Y-%m-%d")

            # Write to website
            try:
                from outputs.website_output import write_digest_to_website
                write_digest_to_website(markdown, today)

                # Store in DB
                db = DigestDatabase()
                try:
                    from core.models import Digest
                    digest = Digest(date=today, mode="daily", content=markdown, articles=[])
                    digest_id = db.store_digest(digest, f"{today}-digest.md")
                    db.mark_website_published(digest_id)
                except Exception:
                    # Already published today, just update the file
                    pass
                db.close()

                # Email to all subscribers
                email_results = {"sent": 0, "failed": 0}
                try:
                    from outputs.email_output import send_to_all_subscribers
                    db2 = DigestDatabase()
                    email_results = send_to_all_subscribers(markdown, db2)
                    db2.close()
                except Exception as e:
                    print(f"  Email sending failed: {e}")

                self.send_json({
                    "success": True,
                    "message": f"Published! {email_results.get('sent', 0)} emails sent.",
                    "date": today,
                    "emails_sent": email_results.get("sent", 0),
                    "emails_failed": email_results.get("failed", 0),
                })
            except Exception as e:
                self.send_json({"success": False, "message": str(e)[:200]})

        elif path == "/api/digest/send-latest":
            # Auto-send: reads today's digest file and emails all subscribers
            body = self.read_body() or {}
            api_key = body.get("api_key", "")
            expected_key = os.environ.get("DIGEST_SEND_KEY", "")
            if not expected_key or api_key != expected_key:
                self.send_json({"success": False, "message": "Unauthorized"}, status=401)
                return

            try:
                from datetime import datetime as dt
                today = dt.now().strftime("%Y-%m-%d")

                # Accept digest content passed directly in request body (preferred)
                # Falls back to reading from filesystem (legacy)
                raw_content = body.get("content", "")
                if raw_content:
                    parts = raw_content.split("---", 2)
                    md = parts[2].strip() if len(parts) >= 3 else raw_content
                else:
                    # Filesystem fallback — find most recent digest within last 2 days
                    base = os.path.dirname(os.path.abspath(__file__))
                    possible_paths = [
                        os.path.join(base, "..", "web", "src", "content", "digests"),
                        os.path.join(base, "web", "src", "content", "digests"),
                        "/app/web/src/content/digests",
                    ]
                    from datetime import timedelta
                    digest_file = None
                    for check_date in [today, (dt.now() - timedelta(days=1)).strftime("%Y-%m-%d")]:
                        for digest_path in possible_paths:
                            if not os.path.isdir(digest_path):
                                continue
                            for f in os.listdir(digest_path):
                                if f.startswith(check_date) and f.endswith(".md"):
                                    digest_file = os.path.join(digest_path, f)
                                    break
                            if digest_file:
                                break
                        if digest_file:
                            break
                    if not digest_file:
                        tried = [p for p in possible_paths if os.path.isdir(p)]
                        self.send_json({"success": False, "message": f"No digest for {today} or yesterday. Paths: {tried}"})
                        return
                    with open(digest_file, "r") as f:
                        content = f.read()
                        parts = content.split("---", 2)
                        md = parts[2].strip() if len(parts) >= 3 else content

                # Find featured_free article and prepend to digest
                site_url = os.environ.get("SITE_URL", "https://agenticedge.tech")
                featured_title = body.get("featured_title", "")
                featured_slug = body.get("featured_slug", "")
                if featured_title and featured_slug:
                    featured_url = f"{site_url}/pro/{featured_slug}"
                    md = f"**This week's free Pro article:** [{featured_title}]({featured_url}) — read the full piece, no login needed.\n\n---\n\n{md}"
                else:
                    # Filesystem fallback for featured article
                    base = os.path.dirname(os.path.abspath(__file__))
                    premium_path = os.path.join(base, "..", "web", "src", "content", "premium")
                    if not os.path.isdir(premium_path):
                        premium_path = os.path.join(base, "web", "src", "content", "premium")
                    if os.path.isdir(premium_path):
                        for pf in os.listdir(premium_path):
                            if pf.endswith(".md"):
                                with open(os.path.join(premium_path, pf), "r") as pfile:
                                    pcontent = pfile.read()
                                    if "featured_free: true" in pcontent:
                                        import re as _re
                                        title_match = _re.search(r'title:\s*"([^"]+)"', pcontent)
                                        slug = pf.replace(".md", "")
                                        if title_match:
                                            ft = title_match.group(1)
                                            fu = f"{site_url}/pro/{slug}"
                                            md = f"**This week's free Pro article:** [{ft}]({fu}) — read the full piece, no login needed.\n\n---\n\n{md}"
                                        break

                test_mode = body.get("test_mode", False)
                from outputs.email_output import send_to_all_subscribers, send_digest_email
                if test_mode:
                    test_email = os.environ.get("DIGEST_TEST_EMAIL", "pillicdj@gmail.com")
                    success = send_digest_email(md, email_to=test_email, is_test=True)
                    self.send_json({
                        "success": True,
                        "message": f"TEST MODE: sent to {test_email} only",
                        "emails_sent": 1 if success else 0,
                        "emails_failed": 0 if success else 1,
                        "test_mode": True,
                    })
                else:
                    db = DigestDatabase()
                    email_results = send_to_all_subscribers(md, db)
                    db.close()
                    self.send_json({
                        "success": True,
                        "message": f"Sent {email_results.get('sent', 0)} emails for {today}",
                        "emails_sent": email_results.get("sent", 0),
                        "emails_failed": email_results.get("failed", 0),
                    })
            except Exception as e:
                self.send_json({"success": False, "message": f"Error: {str(e)[:300]}"})

        elif path == "/api/checkout":
            body = self.read_body()
            if not body:
                return
            price_key = body.get("price_key", "pro_monthly")
            # Pre-fill email from session if available
            customer_email = None
            session_id = body.get("session_id")
            if session_id:
                from auth import get_session
                sess = get_session(session_id)
                if sess:
                    customer_email = sess["email"]
            checkout_url = create_stripe_checkout(price_key, customer_email)
            if checkout_url:
                self.send_json({"success": True, "checkout_url": checkout_url})
            else:
                self.send_json({"success": False, "message": "Stripe not configured. Add STRIPE_SECRET_KEY to .env and create products in Stripe Dashboard."})

        elif path == "/api/checkout/verify":
            # Called after Stripe redirect — verifies session and upgrades subscriber
            body = self.read_body()
            if not body:
                return
            session_id = body.get("session_id")
            if not session_id:
                self.send_json({"success": False, "message": "Missing session_id"})
                return

            try:
                import stripe
                stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
                if not stripe.api_key:
                    self.send_json({"success": False, "message": "Stripe not configured"})
                    return

                session = stripe.checkout.Session.retrieve(session_id)
                if session.payment_status != "paid":
                    self.send_json({"success": False, "message": "Payment not completed"})
                    return

                customer_email = session.customer_email or (session.customer_details or {}).get("email")
                customer_id = session.customer

                if not customer_email:
                    self.send_json({"success": False, "message": "No email found in checkout"})
                    return

                # Determine tier from price
                line_items = stripe.checkout.Session.list_line_items(session_id)
                price_id = line_items.data[0].price.id if line_items.data else ""
                inner_prices = {
                    os.environ.get("STRIPE_PRICE_FOUNDING", ""),
                    os.environ.get("STRIPE_PRICE_INNER_ANNUAL", ""),
                }
                tier = "inner" if price_id in inner_prices else "pro"

                # Upgrade subscriber
                db = DigestDatabase()
                db.conn.execute(
                    "UPDATE subscribers SET tier = ?, stripe_customer_id = ? WHERE email = ?",
                    (tier, customer_id, customer_email)
                )
                # Also update any auth sessions
                db.conn.execute(
                    "UPDATE auth_sessions SET tier = ? WHERE email = ?",
                    (tier, customer_email)
                )
                db.conn.commit()
                db.close()

                print(f"  Checkout verified: {customer_email[:3]}*** → {tier}")
                self.send_json({"success": True, "email": customer_email, "tier": tier})

            except Exception as e:
                print(f"  Checkout verify error: {e}")
                self.send_json({"success": False, "message": str(e)[:200]})

        elif path == "/api/subscribe":
            body = self.read_body()
            if not body:
                return
            email = body.get("email")
            if not email:
                self.send_json({"success": False, "message": "Email required"}, status=400)
                return
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                self.send_json({"success": False, "message": "Invalid email format"}, status=400)
                return
            # Rate limit: max 5 per minute per IP
            client_ip = self._get_client_ip()
            if self._check_rate_limit(f"subscribe:{client_ip}", max_requests=5, window_seconds=60):
                self.send_json({"success": False, "message": "Too many requests. Try again in a minute."}, status=429)
                return
            db = DigestDatabase()

            # Check if email already exists as an active subscriber
            cursor = db.conn.cursor()
            cursor.execute("SELECT active FROM subscribers WHERE email = ?", (email,))
            existing = cursor.fetchone()
            is_existing = existing and dict(existing)["active"] == 1

            if is_existing:
                db.close()
                self.send_json({"success": True, "existing": True, "message": "You're already subscribed! Sign in to access your account."})
                return

            db.add_subscriber(email)
            total = len(db.get_subscribers())
            db.close()

            # Send welcome email in background
            try:
                from outputs.welcome_email import send_welcome_email
                threading.Thread(target=send_welcome_email, args=(email,), daemon=True).start()
            except Exception:
                pass
            self.send_json({"success": True, "existing": False, "message": f"Subscribed: {email}", "total_subscribers": total})

        elif path == "/api/unsubscribe":
            body = self.read_body()
            if not body:
                self.send_json({"success": False, "message": "Email required"}, status=400)
                return
            email = body.get("email")
            if not email:
                self.send_json({"success": False, "message": "Email required"}, status=400)
                return
            db = DigestDatabase()
            db.conn.execute("UPDATE subscribers SET active = 0 WHERE email = ?", (email,))
            db.conn.commit()
            db.close()
            self.send_json({"success": True, "message": f"Unsubscribed: {email}"})

        elif path == "/api/cancel-subscription":
            body = self.read_body()
            if not body:
                return
            session_id = body.get("session_id")
            if not session_id:
                self.send_json({"success": False, "message": "Not logged in"}, status=400)
                return

            from auth import get_session
            session = get_session(session_id)
            if not session:
                self.send_json({"success": False, "message": "Invalid session"}, status=401)
                return

            email = session["email"]
            db = DigestDatabase()
            cursor = db.conn.cursor()
            cursor.execute("SELECT stripe_customer_id FROM subscribers WHERE email = ?", (email,))
            row = cursor.fetchone()
            customer_id = dict(row)["stripe_customer_id"] if row else None

            if customer_id:
                try:
                    import stripe
                    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
                    # Cancel all active subscriptions for this customer
                    subs = stripe.Subscription.list(customer=customer_id, status="active")
                    cancelled = 0
                    for sub in subs.data:
                        stripe.Subscription.modify(sub.id, cancel_at_period_end=True)
                        cancelled += 1

                    db.close()
                    self.send_json({"success": True, "message": f"Subscription set to cancel at end of billing period. {cancelled} subscription(s) scheduled for cancellation.", "cancelled": cancelled})
                except Exception as e:
                    db.close()
                    print(f"  Cancel error: {e}")
                    self.send_json({"success": False, "message": str(e)[:200]})
            else:
                # No Stripe customer, just downgrade
                db.conn.execute(
                    "UPDATE subscribers SET tier = 'free' WHERE email = ?",
                    (email,)
                )
                db.conn.execute(
                    "UPDATE auth_sessions SET tier = 'free' WHERE email = ?",
                    (email,)
                )
                db.conn.commit()
                db.close()
                self.send_json({"success": True, "message": "Downgraded to free.", "cancelled": 0})

        elif path == "/api/auth/login":
            body = self.read_body()
            if not body:
                return
            email = body.get("email")
            if not email:
                self.send_json({"success": False, "message": "Email required"}, status=400)
                return
            # Email validation (#11)
            if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
                self.send_json({"success": False, "message": "Invalid email format"}, status=400)
                return
            # Rate limit: max 5 per minute per IP
            client_ip = self._get_client_ip()
            if self._check_rate_limit(f"login:{client_ip}", max_requests=5, window_seconds=60):
                self.send_json({"success": False, "message": "Too many login attempts. Try again in a minute."}, status=429)
                return

            from auth import create_magic_link, send_magic_link_email, cleanup_expired
            # Opportunistic cleanup of expired tokens/sessions (cheap)
            try:
                cleanup_expired()
            except Exception:
                pass
            db = DigestDatabase()
            token, is_new = create_magic_link(email, db)
            db.close()

            site_url = os.environ.get("SITE_URL", "http://localhost:4321")
            magic_url = f"{site_url}/auth/verify?token={token}"
            is_local = "localhost" in site_url

            if is_new:
                # New subscriber: send welcome email with magic link embedded
                try:
                    from outputs.welcome_email import send_welcome_email
                    threading.Thread(
                        target=send_welcome_email, args=(email, magic_url), daemon=True
                    ).start()
                    if not os.environ.get("RAILWAY_ENVIRONMENT"):
                        print(f"  [NEW SUBSCRIBER] {email}")
                    else:
                        print(f"  [NEW SUBSCRIBER] {email[:3]}***")
                except Exception:
                    pass
            else:
                # Returning user: send standard magic link email
                send_magic_link_email(email, token)

            resp = {"success": True, "message": f"Check your inbox — we sent a link to {email}."}
            if is_local:
                resp["dev_link"] = magic_url
                resp["message"] = "Dev mode: use dev_link to sign in."
            self.send_json(resp)

        elif path == "/api/auth/verify":
            body = self.read_body()
            if not body:
                return
            token = body.get("token")
            if not token:
                self.send_json({"success": False, "message": "Token required"}, status=400)
                return

            from auth import verify_token
            session = verify_token(token)

            if not session:
                self.send_json({"success": False, "message": "Invalid or expired link. Request a new one."})
                return

            self.send_json({
                "success": True,
                "session_id": session["session_id"],
                "email": session["email"],
                "tier": session["tier"],
            })

        elif path == "/api/auth/session":
            body = self.read_body()
            if not body:
                return
            session_id = body.get("session_id")

            from auth import get_session
            session = get_session(session_id) if session_id else None

            if session:
                self.send_json({"success": True, "email": session["email"], "tier": session["tier"]})
            else:
                self.send_json({"success": False, "message": "Not logged in"})

        elif path == "/api/auth/logout":
            body = self.read_body()
            if not body:
                return
            session_id = body.get("session_id")
            if session_id:
                from auth import logout
                logout(session_id)
            self.send_json({"success": True, "message": "Logged out"})

        elif path == "/api/stripe/webhook":
            # Stripe webhook — handles subscription events
            body_raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            try:
                import stripe
                stripe_key = os.environ.get("STRIPE_SECRET_KEY")
                webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

                if not stripe_key:
                    self.send_json({"success": False, "message": "Stripe not configured"})
                    return

                stripe.api_key = stripe_key
                sig_header = self.headers.get("Stripe-Signature", "")
                if webhook_secret:
                    event = stripe.Webhook.construct_event(body_raw, sig_header, webhook_secret)
                else:
                    event = json.loads(body_raw)  # Dev mode fallback

                if event.get("type") == "checkout.session.completed":
                    session = event["data"]["object"]
                    customer_email = session.get("customer_email") or session.get("customer_details", {}).get("email")
                    customer_id = session.get("customer")

                    if customer_email:
                        # Get the price ID from the subscription
                        line_items = stripe.checkout.Session.list_line_items(session["id"])
                        price_id = line_items.data[0].price.id if line_items.data else ""
                        inner_prices = [p for p in [
                            os.environ.get("STRIPE_PRICE_FOUNDING", ""),
                            os.environ.get("STRIPE_PRICE_INNER_ANNUAL", ""),
                        ] if p]
                        tier = "inner" if price_id in inner_prices else "pro"

                        db = DigestDatabase()
                        db.conn.execute(
                            "UPDATE subscribers SET tier = ?, stripe_customer_id = ? WHERE email = ?",
                            (tier, customer_id, customer_email)
                        )
                        db.conn.execute(
                            "UPDATE auth_sessions SET tier = ? WHERE email = ?",
                            (tier, customer_email)
                        )
                        db.conn.commit()
                        db.close()
                        print(f"  Upgraded {customer_email[:3]}*** to {tier}")

                elif event.get("type") == "customer.subscription.deleted":
                    customer_id = event["data"]["object"].get("customer")
                    if customer_id:
                        db = DigestDatabase()
                        db.conn.execute(
                            "UPDATE subscribers SET tier = 'free' WHERE stripe_customer_id = ?",
                            (customer_id,)
                        )
                        # Also downgrade any active auth sessions for this customer
                        db.conn.execute(
                            "UPDATE auth_sessions SET tier = 'free' WHERE email IN "
                            "(SELECT email FROM subscribers WHERE stripe_customer_id = ?)",
                            (customer_id,)
                        )
                        db.conn.commit()
                        db.close()
                        print(f"  Downgraded customer {customer_id} to free")

                elif event.get("type") == "invoice.payment_failed":
                    invoice = event["data"]["object"]
                    customer_id = invoice.get("customer")
                    customer_email = invoice.get("customer_email", "unknown")
                    attempt_count = invoice.get("attempt_count", 0)
                    print(f"  Payment failed for {customer_email[:3]}*** (customer {customer_id}), attempt #{attempt_count}")
                    # Optionally send notification email
                    try:
                        resend_key = os.environ.get("RESEND_API_KEY")
                        resend_from = os.environ.get("RESEND_FROM")
                        if resend_key and resend_from and customer_email and customer_email != "unknown":
                            import requests
                            requests.post("https://api.resend.com/emails", headers={
                                "Authorization": f"Bearer {resend_key}",
                                "Content-Type": "application/json"
                            }, json={
                                "from": resend_from,
                                "to": [customer_email],
                                "subject": "Payment failed — please update your billing info",
                                "html": "<p>Your recent payment for Agentic Edge failed. "
                                        "Please update your payment method to keep your subscription active.</p>"
                                        "<p>You can manage your billing at any time from your account.</p>"
                            })
                    except Exception as notify_err:
                        print(f"  Failed to send payment failure notification: {notify_err}")

                elif event.get("type") == "customer.subscription.updated":
                    subscription = event["data"]["object"]
                    customer_id = subscription.get("customer")
                    status = subscription.get("status")
                    if customer_id and status == "active":
                        # Determine new tier from the subscription's current plan
                        items = subscription.get("items", {}).get("data", [])
                        price_id = items[0]["price"]["id"] if items else ""
                        inner_prices = [p for p in [
                            os.environ.get("STRIPE_PRICE_FOUNDING", ""),
                            os.environ.get("STRIPE_PRICE_INNER_ANNUAL", ""),
                        ] if p]
                        tier = "inner" if price_id in inner_prices else "pro"

                        db = DigestDatabase()
                        db.conn.execute(
                            "UPDATE subscribers SET tier = ? WHERE stripe_customer_id = ?",
                            (tier, customer_id)
                        )
                        db.conn.execute(
                            "UPDATE auth_sessions SET tier = ? WHERE email IN "
                            "(SELECT email FROM subscribers WHERE stripe_customer_id = ?)",
                            (tier, customer_id)
                        )
                        db.conn.commit()
                        db.close()
                        print(f"  Subscription updated for customer {customer_id} → {tier}")

                self.send_json({"success": True})

            except Exception as e:
                print(f"  Stripe webhook error: {e}")
                self.send_json({"success": True})  # Always 200 to Stripe

        elif path == "/api/quick-add":
            # Quick-add an article via URL — from Telegram bot, Discord, or direct API call
            body = self.read_body()
            if not body:
                return

            url = body.get("url", "").strip()
            note = body.get("note", "").strip()
            secret = body.get("secret", "")

            # Auth: check secret token (set QUICK_ADD_SECRET in .env)
            expected_secret = os.environ.get("QUICK_ADD_SECRET", "")
            if expected_secret and secret != expected_secret:
                self.send_json({"success": False, "message": "Unauthorized"}, status=401)
                return

            if not url:
                self.send_json({"success": False, "message": "URL required"}, status=400)
                return

            # Fetch article title and summary from URL
            import hashlib
            import urllib.request

            try:
                req = urllib.request.Request(url, headers={"User-Agent": "AgenticDigest/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    html = resp.read().decode("utf-8", errors="ignore")

                # Extract title
                import re as _re
                title_match = _re.search(r"<title[^>]*>(.*?)</title>", html, _re.IGNORECASE | _re.DOTALL)
                title = title_match.group(1).strip() if title_match else url

                # Extract meta description
                desc_match = _re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html, _re.IGNORECASE)
                summary = desc_match.group(1).strip() if desc_match else ""

                # Clean HTML entities
                title = title.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"').replace("&#x27;", "'")
                summary = summary.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')

            except Exception as e:
                title = url
                summary = ""

            # Store in database
            article_id = hashlib.sha256(url.encode()).hexdigest()
            db = DigestDatabase()
            try:
                from datetime import datetime
                db.conn.execute("""
                    INSERT OR IGNORE INTO articles (id, source, tier, title, link, summary, published_at, fetched_at, relevance_score, why_it_matters)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_id, "Quick Add", 1, title, url, summary,
                    datetime.now().isoformat(), datetime.now().isoformat(),
                    8.0, note or "Manually added via quick-add."
                ))
                db.conn.commit()
                added = db.conn.total_changes > 0
            except Exception:
                added = False
            db.close()

            self.send_json({
                "success": True,
                "added": added,
                "title": title,
                "url": url,
                "note": note,
                "message": f"Added: {title[:60]}" if added else f"Already exists: {title[:60]}"
            })

        else:
            self.send_error(404)

    def _get_cors_origin(self):
        return os.environ.get('CORS_ORIGIN', '*')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", self._get_cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def read_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            content_length = 0
        if content_length == 0:
            self.send_json({"success": False, "message": "Request body is empty"}, status=400)
            return None
        try:
            body = self.rfile.read(content_length)
            return json.loads(body.decode("utf-8"))
        except Exception:
            self.send_json({"success": False, "message": "Invalid JSON"}, status=400)
            return None

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", self._get_cors_origin())
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        # Only log non-200 requests
        if args and len(args) >= 2 and "200" not in str(args[1]):
            super().log_message(format, *args)


def main():
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    server = HTTPServer((host, port), APIHandler)

    # Clean up expired auth tokens/sessions at startup
    try:
        from auth import cleanup_expired
        cleanup_expired()
        print("  [STARTUP] Expired auth tokens/sessions cleaned up")
    except Exception as e:
        print(f"  [STARTUP] Auth cleanup skipped: {e}")

    print()
    print("=" * 60)
    print("  Agentic Digest API Server")
    print("=" * 60)
    print(f"  http://{host}:{port}")
    print()
    print("  Endpoints:")
    print(f"    GET  /api/articles           All articles")
    print(f"    GET  /api/articles/by-tier   Articles by tier")
    print(f"    GET  /api/articles/stats     Statistics")
    print(f"    POST /api/feedback           Save feedback")
    print(f"    GET  /api/feedback/summary   Feedback stats")
    print(f"    POST /api/pipeline/fetch     Trigger background fetch")
    print(f"    GET  /api/pipeline/status    Fetch status")
    print(f"    GET  /api/digest/preview     Newsletter preview")
    print(f"    POST /api/digest/publish     Publish newsletter")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 60)
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
