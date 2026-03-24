"""SQLite database for the Agentic Digest pipeline."""

import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
import sys
from pathlib import Path as PathlibPath

# Add src to path for imports
_src_path = PathlibPath(__file__).parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from core.models import Article, Digest


class DigestDatabase:
    """SQLite database for storing articles, digests, and tracking state."""

    def __init__(self, db_path: str = "data/digest.db"):
        """Initialize database connection and create schema if needed."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Articles table: all fetched articles (enables deduplication)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                tier INTEGER NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL UNIQUE,
                summary TEXT,
                published_at TEXT,
                fetched_at TEXT,
                relevance_score REAL,
                why_it_matters TEXT
            )
        """)

        # Digests table: each generated digest run
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                mode TEXT NOT NULL,
                filename TEXT,
                email_sent INTEGER DEFAULT 0,
                website_published INTEGER DEFAULT 0,
                substack_draft_id TEXT,
                created_at TEXT
            )
        """)

        # Digest articles junction table: which articles in which digests
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS digest_articles (
                digest_id INTEGER NOT NULL,
                article_id TEXT NOT NULL,
                rank INTEGER,
                PRIMARY KEY (digest_id, article_id),
                FOREIGN KEY (digest_id) REFERENCES digests(id),
                FOREIGN KEY (article_id) REFERENCES articles(id)
            )
        """)

        # User feedback: reactions and comments on articles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT NOT NULL,
                reaction TEXT,
                comment TEXT,
                created_at TEXT,
                FOREIGN KEY (article_id) REFERENCES articles(id)
            )
        """)

        # Subscribers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                tier TEXT DEFAULT 'free',
                stripe_customer_id TEXT,
                subscribed_at TEXT,
                active INTEGER DEFAULT 1
            )
        """)

        # Source reviews: manual curation of new sources
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL UNIQUE,
                url TEXT,
                category TEXT,
                signal_strength REAL,
                update_frequency TEXT,
                relevance_comment TEXT,
                approved INTEGER DEFAULT 0,
                added_date TEXT
            )
        """)

        self.conn.commit()

    def _article_hash(self, url: str) -> str:
        """Generate SHA256 hash of article URL for deduplication."""
        return hashlib.sha256(url.encode()).hexdigest()

    def store_articles(self, articles: list[Article]) -> list[Article]:
        """
        Store articles in the database, skipping duplicates.
        Returns only the new articles that weren't already stored.
        """
        cursor = self.conn.cursor()
        new_articles = []

        for article in articles:
            article_id = self._article_hash(article.link)
            article.id = article_id

            # Check if article already exists
            cursor.execute("SELECT id FROM articles WHERE link = ?", (article.link,))
            if cursor.fetchone():
                print(f"  [DEDUP] Skipping: {article.title[:50]}...")
                continue

            # Insert new article
            cursor.execute("""
                INSERT INTO articles (
                    id, source, tier, title, link, summary,
                    published_at, fetched_at, relevance_score, why_it_matters
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article_id,
                article.source,
                article.tier,
                article.title,
                article.link,
                article.summary,
                article.published,
                article.fetched_at,
                article.relevance_score,
                article.why_it_matters,
            ))
            new_articles.append(article)

        self.conn.commit()
        return new_articles

    def store_digest(self, digest: Digest, filename: str = None) -> int:
        """
        Store a digest and its associated articles.
        Returns the digest ID.
        """
        cursor = self.conn.cursor()

        # Insert digest
        cursor.execute("""
            INSERT INTO digests (date, mode, filename, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            digest.date,
            digest.mode,
            filename,
            digest.created_at,
        ))
        digest_id = cursor.lastrowid

        # Link articles to digest
        for rank, article in enumerate(digest.articles, 1):
            cursor.execute("""
                INSERT INTO digest_articles (digest_id, article_id, rank)
                VALUES (?, ?, ?)
            """, (digest_id, article.id, rank))

        self.conn.commit()
        return digest_id

    def mark_email_sent(self, digest_id: int):
        """Mark a digest as having been emailed."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE digests SET email_sent = 1 WHERE id = ?",
            (digest_id,)
        )
        self.conn.commit()

    def mark_website_published(self, digest_id: int):
        """Mark a digest as having been published to the website."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE digests SET website_published = 1 WHERE id = ?",
            (digest_id,)
        )
        self.conn.commit()

    def digest_exists(self, date: str) -> bool:
        """Check if a digest for a given date already exists."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM digests WHERE date = ?", (date,))
        return cursor.fetchone() is not None

    def get_digest(self, date: str) -> dict:
        """Get digest metadata for a given date."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, date, mode, filename, email_sent, website_published, created_at
            FROM digests WHERE date = ?
        """, (date,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def add_feedback(self, article_id: str, reaction: str = None, comment: str = None) -> bool:
        """
        Store user feedback on an article.

        Args:
            article_id: SHA256 hash of article URL
            reaction: 'thumbs_up' or 'thumbs_down'
            comment: Optional explanation (1-2 sentences)

        Returns:
            True if stored successfully
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (article_id, reaction, comment, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                article_id,
                reaction,
                comment,
                datetime.now().isoformat(),
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"  ✗ Feedback error: {e}")
            return False

    def add_source_review(
        self,
        source_name: str,
        url: str,
        category: str,
        signal_strength: float = None,
        update_frequency: str = None,
        relevance_comment: str = None,
        approved: bool = False
    ) -> bool:
        """
        Store a source for manual review.

        Args:
            source_name: Name of the source
            url: Feed URL
            category: 'builder', 'entrepreneur', or 'agentic'
            signal_strength: 1-10 rating
            update_frequency: 'daily', 'weekly', 'sporadic'
            relevance_comment: Why consider this source
            approved: Whether to add to feeds

        Returns:
            True if stored successfully
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO source_reviews (
                    source_name, url, category, signal_strength,
                    update_frequency, relevance_comment, approved, added_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source_name,
                url,
                category,
                signal_strength,
                update_frequency,
                relevance_comment,
                1 if approved else 0,
                datetime.now().isoformat(),
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"  ✗ Source review error: {e}")
            return False

    def get_approved_sources(self) -> list[dict]:
        """Get all approved sources."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT source_name, url, category FROM source_reviews
            WHERE approved = 1 ORDER BY added_date DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_article_feedback(self, article_id: str) -> list[dict]:
        """Get all feedback for an article."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT reaction, comment, created_at FROM feedback
            WHERE article_id = ? ORDER BY created_at DESC
        """, (article_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_feedback_summary(self) -> dict:
        """Get feedback statistics."""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM feedback WHERE reaction = 'thumbs_up'")
        thumbs_up = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM feedback WHERE reaction = 'thumbs_down'")
        thumbs_down = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM feedback WHERE comment IS NOT NULL")
        comments = cursor.fetchone()[0]

        return {
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "comments": comments,
            "total": thumbs_up + thumbs_down,
        }

    def update_article_scores(self, articles: list[Article]):
        """Write relevance_score and why_it_matters back to articles table after Claude ranking."""
        cursor = self.conn.cursor()
        for article in articles:
            if article.id and article.relevance_score is not None:
                cursor.execute("""
                    UPDATE articles SET relevance_score = ?, why_it_matters = ?
                    WHERE id = ?
                """, (article.relevance_score, article.why_it_matters, article.id))
        self.conn.commit()

    def get_articles_by_tier(self) -> dict:
        """Get all articles organized by tier."""
        cursor = self.conn.cursor()
        tier_names = {
            1: "Builder Signal",
            2: "Curated Daily",
            3: "Weekly Depth",
            4: "Community Signal",
        }
        result = {}
        for tier, name in tier_names.items():
            cursor.execute("""
                SELECT id, source, tier, title, link, summary, published_at,
                       fetched_at, relevance_score, why_it_matters
                FROM articles WHERE tier = ?
                ORDER BY relevance_score DESC NULLS LAST
            """, (tier,))
            articles = []
            for i, row in enumerate(cursor.fetchall(), 1):
                articles.append({
                    "rank": i,
                    "id": dict(row)["id"],
                    "title": dict(row)["title"],
                    "source": dict(row)["source"],
                    "tier": dict(row)["tier"],
                    "link": dict(row)["link"],
                    "summary": dict(row)["summary"],
                    "relevance_score": dict(row)["relevance_score"] or 0,
                    "why_it_matters": dict(row)["why_it_matters"] or "Pending analysis",
                    "published_at": dict(row)["published_at"],
                })
            result[name] = articles
        return result

    def get_all_articles(self) -> list[dict]:
        """Get all articles as a flat list."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, source, tier, title, link, summary, published_at,
                   fetched_at, relevance_score, why_it_matters
            FROM articles ORDER BY relevance_score DESC NULLS LAST
        """)
        articles = []
        for i, row in enumerate(cursor.fetchall(), 1):
            d = dict(row)
            d["rank"] = i
            if d["relevance_score"] is None:
                d["relevance_score"] = 0
            if d["why_it_matters"] is None:
                d["why_it_matters"] = "Pending analysis"
            articles.append(d)
        return articles

    def get_stats(self) -> dict:
        """Get article and feedback statistics."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM articles WHERE relevance_score IS NOT NULL")
        ranked = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(relevance_score) FROM articles WHERE relevance_score IS NOT NULL")
        avg = cursor.fetchone()[0] or 0
        cursor.execute("SELECT tier, COUNT(*) FROM articles GROUP BY tier ORDER BY tier")
        by_tier = {f"Tier {row[0]}": row[1] for row in cursor.fetchall()}
        feedback = self.get_feedback_summary()
        return {
            "total_articles": total,
            "ranked": ranked,
            "unranked": total - ranked,
            "average_score": round(avg, 1),
            "by_tier": by_tier,
            "feedback": feedback,
        }

    def get_articles_for_preview(self) -> list[Article]:
        """Get articles for newsletter preview.
        ONLY includes articles explicitly added to newsletter (newsletter_include).
        Falls back to high-scoring unrated if no explicit selections yet.
        """
        cursor = self.conn.cursor()

        # First: articles explicitly added to newsletter
        cursor.execute("""
            SELECT DISTINCT a.id, a.source, a.tier, a.title, a.link, a.summary,
                   a.published_at, a.relevance_score, a.why_it_matters
            FROM articles a
            JOIN feedback f ON a.id = f.article_id
            WHERE f.reaction = 'newsletter_include'
              AND a.id NOT IN (
                  SELECT article_id FROM feedback
                  WHERE reaction = 'newsletter_remove'
                  AND created_at > (
                      SELECT MAX(created_at) FROM feedback f2
                      WHERE f2.article_id = feedback.article_id AND f2.reaction = 'newsletter_include'
                  )
              )
            ORDER BY a.relevance_score DESC
        """)
        newsletter = [dict(row) for row in cursor.fetchall()]

        # If user has explicitly selected articles, use ONLY those
        if newsletter:
            result = []
            for row in newsletter:
                result.append(Article(
                    source=row["source"], tier=row["tier"], title=row["title"],
                    link=row["link"], summary=row["summary"] or "",
                    published=row["published_at"] or "", id=row["id"],
                    relevance_score=row["relevance_score"],
                    why_it_matters=row["why_it_matters"],
                ))
            return result

        # Fallback: if no explicit selections, show high-scoring unrated articles
        cursor.execute("""
            SELECT a.id, a.source, a.tier, a.title, a.link, a.summary,
                   a.published_at, a.relevance_score, a.why_it_matters
            FROM articles a
            WHERE a.relevance_score >= 8
              AND a.id NOT IN (
                  SELECT article_id FROM feedback WHERE reaction = 'thumbs_down'
              )
            ORDER BY a.relevance_score DESC
            LIMIT 10
        """)
        fallback = [dict(row) for row in cursor.fetchall()]

        result = []
        for row in fallback:
            result.append(Article(
                source=row["source"], tier=row["tier"], title=row["title"],
                link=row["link"], summary=row["summary"] or "",
                published=row["published_at"] or "", id=row["id"],
                relevance_score=row["relevance_score"],
                why_it_matters=row["why_it_matters"],
            ))
        return result

    def add_subscriber(self, email: str, tier: str = "free") -> bool:
        """Add an email subscriber."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO subscribers (email, tier, subscribed_at)
                VALUES (?, ?, ?)
            """, (email, tier, datetime.now().isoformat()))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"  Subscriber error: {e}")
            return False

    def get_subscribers(self, tier: str = None) -> list[dict]:
        """Get all active subscribers, optionally filtered by tier."""
        cursor = self.conn.cursor()
        if tier:
            cursor.execute("SELECT email, tier FROM subscribers WHERE active = 1 AND tier = ?", (tier,))
        else:
            cursor.execute("SELECT email, tier FROM subscribers WHERE active = 1")
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection."""
        self.conn.close()
