"""
Feedback API for capturing user reactions and comments on articles.
This allows the system to learn from user preferences over time.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class FeedbackHandler:
    """Handle article feedback (thumbs up/down, comments)."""

    def __init__(self, db_path: str = "data/digest.db"):
        self.db_path = db_path

    def save_feedback(self, article_id: str, reaction: str = None, comment: str = None):
        """
        Save user feedback on an article.

        Args:
            article_id: Article ID/hash
            reaction: "thumbs_up" or "thumbs_down"
            comment: Optional 1-sentence explanation

        Returns:
            True if saved successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO feedback (article_id, reaction, comment, created_at)
                VALUES (?, ?, ?, ?)
            """, (article_id, reaction, comment, datetime.now().isoformat()))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False

    def get_feedback_summary(self):
        """
        Get summary of all feedback: thumbs up/down counts, top comments.

        Returns:
            Dict with feedback stats
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Count reactions
            cursor.execute("""
                SELECT reaction, COUNT(*) as count
                FROM feedback
                WHERE reaction IS NOT NULL
                GROUP BY reaction
            """)

            reactions = {row[0]: row[1] for row in cursor.fetchall()}

            # Get recent comments
            cursor.execute("""
                SELECT article_id, comment, created_at
                FROM feedback
                WHERE comment IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 20
            """)

            comments = [
                {
                    "article_id": row[0],
                    "comment": row[1],
                    "timestamp": row[2]
                }
                for row in cursor.fetchall()
            ]

            conn.close()

            return {
                "thumbs_up": reactions.get("thumbs_up", 0),
                "thumbs_down": reactions.get("thumbs_down", 0),
                "recent_comments": comments
            }
        except Exception as e:
            print(f"Error getting feedback summary: {e}")
            return {"thumbs_up": 0, "thumbs_down": 0, "recent_comments": []}

    def get_article_feedback(self, article_id: str):
        """
        Get all feedback for a specific article.

        Args:
            article_id: Article ID/hash

        Returns:
            List of feedback entries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT reaction, comment, created_at
                FROM feedback
                WHERE article_id = ?
                ORDER BY created_at DESC
            """, (article_id,))

            feedback = [
                {
                    "reaction": row[0],
                    "comment": row[1],
                    "timestamp": row[2]
                }
                for row in cursor.fetchall()
            ]

            conn.close()
            return feedback
        except Exception as e:
            print(f"Error getting article feedback: {e}")
            return []

    def get_feedback_adjusted_scores(self):
        """
        Get articles with adjusted relevance scores based on user feedback.

        Returns:
            Dict of article_id -> adjusted_score
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Calculate feedback scores
            cursor.execute("""
                SELECT
                    article_id,
                    SUM(CASE WHEN reaction = 'thumbs_up' THEN 1 ELSE 0 END) as up_count,
                    SUM(CASE WHEN reaction = 'thumbs_down' THEN 1 ELSE 0 END) as down_count
                FROM feedback
                WHERE reaction IS NOT NULL
                GROUP BY article_id
            """)

            adjusted_scores = {}
            for article_id, up_count, down_count in cursor.fetchall():
                # Simple adjustment: +1 for thumbs up, -1 for thumbs down
                adjustment = (up_count or 0) - (down_count or 0)
                adjusted_scores[article_id] = adjustment

            conn.close()
            return adjusted_scores
        except Exception as e:
            print(f"Error getting adjusted scores: {e}")
            return {}
