"""
API endpoints for retrieving articles and their rankings.
Serves data to the internal training dashboard.
"""

import sqlite3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


class ArticlesAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for articles API."""

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # GET /api/articles - All articles for today
        if path == "/api/articles":
            articles = self.get_all_articles()
            self.send_json(articles)

        # GET /api/articles/by-tier - Articles organized by tier
        elif path == "/api/articles/by-tier":
            articles_by_tier = self.get_articles_by_tier()
            self.send_json(articles_by_tier)

        # GET /api/articles/stats - Statistics
        elif path == "/api/articles/stats":
            stats = self.get_stats()
            self.send_json(stats)

        else:
            self.send_error(404)

    def get_all_articles(self):
        """Fetch all articles from database."""
        try:
            conn = sqlite3.connect("data/digest.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    title,
                    source,
                    tier,
                    link,
                    summary,
                    relevance_score,
                    why_it_matters,
                    published_at,
                    fetched_at
                FROM articles
                ORDER BY relevance_score DESC NULLS LAST
            """)

            articles = []
            for i, row in enumerate(cursor.fetchall(), 1):
                articles.append({
                    "rank": i,
                    "id": row["id"],
                    "title": row["title"],
                    "source": row["source"],
                    "tier": row["tier"],
                    "link": row["link"],
                    "summary": row["summary"],
                    "relevance_score": row["relevance_score"] or 0,
                    "why_it_matters": row["why_it_matters"] or "Not yet ranked",
                    "published_at": row["published_at"],
                    "fetched_at": row["fetched_at"]
                })

            conn.close()
            return {"success": True, "total": len(articles), "articles": articles}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_articles_by_tier(self):
        """Fetch articles organized by tier."""
        try:
            conn = sqlite3.connect("data/digest.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            tier_names = {
                1: "Builder Signal 🚀",
                2: "Curated Daily 📰",
                3: "Weekly Depth 📚",
                4: "Community Signal 💬"
            }

            articles_by_tier = {}

            for tier in [1, 2, 3, 4]:
                cursor.execute("""
                    SELECT
                        id,
                        title,
                        source,
                        tier,
                        link,
                        summary,
                        relevance_score,
                        why_it_matters,
                        published_at
                    FROM articles
                    WHERE tier = ?
                    ORDER BY relevance_score DESC NULLS LAST
                """, (tier,))

                articles = []
                for i, row in enumerate(cursor.fetchall(), 1):
                    articles.append({
                        "rank": i,
                        "id": row["id"],
                        "title": row["title"],
                        "source": row["source"],
                        "tier": row["tier"],
                        "link": row["link"],
                        "summary": row["summary"],
                        "relevance_score": row["relevance_score"] or 0,
                        "why_it_matters": row["why_it_matters"] or "Pending analysis",
                        "published_at": row["published_at"]
                    })

                articles_by_tier[tier_names[tier]] = articles

            conn.close()
            return {"success": True, "articles_by_tier": articles_by_tier}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_stats(self):
        """Get statistics about articles."""
        try:
            conn = sqlite3.connect("data/digest.db")
            cursor = conn.cursor()

            # Total articles
            cursor.execute("SELECT COUNT(*) FROM articles")
            total_articles = cursor.fetchone()[0]

            # Articles by tier
            cursor.execute("""
                SELECT tier, COUNT(*) as count
                FROM articles
                GROUP BY tier
                ORDER BY tier
            """)

            by_tier = {}
            for tier, count in cursor.fetchall():
                by_tier[f"Tier {tier}"] = count

            # Ranked vs unranked
            cursor.execute("""
                SELECT
                    COUNT(CASE WHEN relevance_score IS NOT NULL THEN 1 END) as ranked,
                    COUNT(CASE WHEN relevance_score IS NULL THEN 1 END) as unranked
                FROM articles
            """)

            ranked, unranked = cursor.fetchone()

            # Average score
            cursor.execute("SELECT AVG(relevance_score) FROM articles WHERE relevance_score IS NOT NULL")
            avg_score = cursor.fetchone()[0] or 0

            conn.close()

            return {
                "success": True,
                "total_articles": total_articles,
                "ranked": ranked,
                "unranked": unranked,
                "average_score": round(avg_score, 1),
                "by_tier": by_tier
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_json(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """Suppress logging."""
        pass


def main():
    """Start the articles API server."""
    port = 8001
    server = HTTPServer(("localhost", port), ArticlesAPIHandler)

    print()
    print("=" * 60)
    print("📰 Articles API Server Started")
    print("=" * 60)
    print(f"Listening on: http://localhost:{port}")
    print()
    print("Available endpoints:")
    print(f"  GET {port}/api/articles          - All articles")
    print(f"  GET {port}/api/articles/by-tier  - Articles by tier")
    print(f"  GET {port}/api/articles/stats    - Statistics")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Articles API server stopped")


if __name__ == "__main__":
    main()
