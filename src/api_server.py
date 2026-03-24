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
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from database import DigestDatabase
from orchestrator import (
    load_config, pipeline_fetch, pipeline_store, pipeline_rank, pipeline_publish
)
from core.generator import generate_digest
from core.local_filter import filter_noise_from_db
from core.trending_fetcher import fetch_all_trending


# --- Stripe checkout ---
def create_stripe_checkout(price_key: str) -> str:
    """Create a Stripe Checkout session. Returns checkout URL or None."""
    import os
    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        return None

    try:
        import stripe
        stripe.api_key = stripe_key

        # Price IDs from Stripe Dashboard
        price_ids = {
            "pro_monthly": os.environ.get("STRIPE_PRICE_PRO_MONTHLY", ""),
            "pro_annual": os.environ.get("STRIPE_PRICE_PRO_ANNUAL", ""),
            "founding_monthly": os.environ.get("STRIPE_PRICE_FOUNDING", ""),
        }

        price_id = price_ids.get(price_key)
        if not price_id:
            return None

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url="http://localhost:4321/?upgraded=true",
            cancel_url="http://localhost:4321/upgrade",
        )
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

        # Step 1: Fetch RSS feeds + trending
        pipeline_status["message"] = "Fetching articles from RSS feeds..."
        articles = pipeline_fetch(lookback_hours=lookback_hours)

        # Step 1b: Fetch trending from HN + Reddit
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

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/articles":
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

        elif path == "/api/pipeline/status":
            self.send_json(pipeline_status)

        elif path == "/api/digest/preview":
            db = DigestDatabase()
            preview_articles = db.get_articles_for_preview()
            db.close()
            if preview_articles:
                digest = generate_digest(preview_articles, mode="daily")
                self.send_json({"success": True, "markdown": digest.content, "article_count": len(preview_articles)})
            else:
                self.send_json({"success": True, "markdown": "*No articles selected yet. Rate some articles to build your newsletter!*", "article_count": 0})

        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/feedback":
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

        elif path == "/api/pipeline/fetch":
            # Start background fetch
            if pipeline_status.get("state") == "fetching":
                self.send_json({"success": True, "message": "Already fetching", "status": pipeline_status})
                return

            thread = threading.Thread(target=run_background_fetch, daemon=True)
            thread.start()
            self.send_json({"success": True, "message": "Fetch started in background", "status": pipeline_status})

        elif path == "/api/digest/publish":
            db = DigestDatabase()
            preview_articles = db.get_articles_for_preview()

            if not preview_articles:
                db.close()
                self.send_json({"success": False, "message": "No articles to publish. Rate some articles first."})
                return

            today = datetime.now().strftime("%Y-%m-%d")
            digest = generate_digest(preview_articles, mode="daily", date=today)
            config = load_config()
            results = pipeline_publish(db, digest, config)
            db.close()

            self.send_json({
                "success": True,
                "message": "Newsletter published!",
                "date": today,
                "article_count": len(preview_articles),
                **results,
            })

        elif path == "/api/checkout":
            body = self.read_body()
            if not body:
                return
            price_key = body.get("price_key", "pro_monthly")
            checkout_url = create_stripe_checkout(price_key)
            if checkout_url:
                self.send_json({"success": True, "checkout_url": checkout_url})
            else:
                self.send_json({"success": False, "message": "Stripe not configured. Add STRIPE_SECRET_KEY to .env and create products in Stripe Dashboard."})

        elif path == "/api/subscribe":
            body = self.read_body()
            if not body:
                return
            email = body.get("email")
            if not email:
                self.send_json({"success": False, "message": "Email required"}, status=400)
                return
            db = DigestDatabase()
            db.add_subscriber(email)
            db.close()
            self.send_json({"success": True, "message": f"Subscribed: {email}"})

        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def read_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode("utf-8"))
        except:
            self.send_json({"success": False, "message": "Invalid JSON"}, status=400)
            return None

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        # Only log non-200 requests
        if args and len(args) >= 2 and "200" not in str(args[1]):
            super().log_message(format, *args)


def main():
    port = 8000
    server = HTTPServer(("localhost", port), APIHandler)

    print()
    print("=" * 60)
    print("  Agentic Digest API Server")
    print("=" * 60)
    print(f"  http://localhost:{port}")
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
