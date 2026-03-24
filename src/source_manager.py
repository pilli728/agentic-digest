"""Source discovery and curation for the Agentic Digest."""

import sys
from pathlib import Path

_src_path = Path(__file__).parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from database import DigestDatabase


class SourceManager:
    """Manage source discovery, review, and approval."""

    def __init__(self, db: DigestDatabase = None):
        self.db = db or DigestDatabase()

    def add_source_candidate(
        self,
        name: str,
        url: str,
        category: str,
        signal_strength: float = None,
        update_frequency: str = None,
        comment: str = None,
    ) -> bool:
        """
        Add a source to the review queue.

        Args:
            name: Source name
            url: Feed URL or website
            category: 'builder', 'entrepreneur', 'agentic'
            signal_strength: 1-10 relevance rating
            update_frequency: 'daily', 'weekly', 'sporadic'
            comment: Why consider this source

        Returns:
            True if added successfully
        """
        return self.db.add_source_review(
            source_name=name,
            url=url,
            category=category,
            signal_strength=signal_strength,
            update_frequency=update_frequency,
            relevance_comment=comment,
            approved=False,
        )

    def approve_source(self, source_name: str) -> bool:
        """Approve a source for inclusion in feeds."""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "UPDATE source_reviews SET approved = 1 WHERE source_name = ?",
                (source_name,)
            )
            self.db.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error approving source: {e}")
            return False

    def reject_source(self, source_name: str) -> bool:
        """Reject a source (delete from queue)."""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "DELETE FROM source_reviews WHERE source_name = ?",
                (source_name,)
            )
            self.db.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error rejecting source: {e}")
            return False

    def get_candidates(self, category: str = None) -> list[dict]:
        """
        Get all unapproved sources for review.

        Args:
            category: Optional filter by category

        Returns:
            List of source candidate dicts
        """
        try:
            cursor = self.db.conn.cursor()
            if category:
                query = """
                    SELECT * FROM source_reviews
                    WHERE approved = 0 AND category = ?
                    ORDER BY signal_strength DESC, added_date DESC
                """
                cursor.execute(query, (category,))
            else:
                query = """
                    SELECT * FROM source_reviews
                    WHERE approved = 0
                    ORDER BY signal_strength DESC, added_date DESC
                """
                cursor.execute(query)

            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching candidates: {e}")
            return []

    def get_approved_sources(self) -> list[dict]:
        """Get all approved sources."""
        return self.db.get_approved_sources()

    def print_review_queue(self, category: str = None):
        """Pretty-print the review queue."""
        candidates = self.get_candidates(category)

        if not candidates:
            print(f"  No candidates to review{f' in {category}' if category else ''}.")
            return

        print(f"\n  Source Review Queue ({len(candidates)} sources)\n")
        for i, src in enumerate(candidates, 1):
            print(f"  {i}. {src['source_name']}")
            print(f"     URL: {src['url']}")
            print(f"     Category: {src['category']} | Signal: {src['signal_strength']}/10")
            if src['update_frequency']:
                print(f"     Updates: {src['update_frequency']}")
            if src['relevance_comment']:
                print(f"     Why: {src['relevance_comment']}")
            print()


if __name__ == "__main__":
    # Example: Add sources from research
    manager = SourceManager()

    # Example candidates
    candidates = [
        {
            "name": "Simon Willison's Blog",
            "url": "https://simonwillison.net/atom/everything/",
            "category": "builder",
            "signal": 9,
            "frequency": "daily",
            "comment": "Deep dives into LLMs and tools"
        },
    ]

    for c in candidates:
        manager.add_source_candidate(
            c["name"], c["url"], c["category"],
            signal_strength=c["signal"],
            update_frequency=c["frequency"],
            comment=c["comment"]
        )

    manager.print_review_queue()
