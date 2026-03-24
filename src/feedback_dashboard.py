"""
Interactive dashboard to review your feedback and see how articles were ranked.
Shows which articles you liked/disliked and your comments.
"""

import sqlite3
from pathlib import Path
from feedback_api import FeedbackHandler


def print_separator(char="═", length=80):
    """Print a line separator."""
    print(char * length)


def show_feedback_summary():
    """Display overall feedback statistics."""
    handler = FeedbackHandler()
    summary = handler.get_feedback_summary()

    print_separator()
    print("📊 YOUR FEEDBACK SUMMARY")
    print_separator()

    thumbs_up = summary.get("thumbs_up", 0)
    thumbs_down = summary.get("thumbs_down", 0)
    total = thumbs_up + thumbs_down

    if total == 0:
        print("\nNo feedback yet. Start rating articles! 👇\n")
        return

    print(f"\n👍 Thumbs Up:    {thumbs_up}")
    print(f"👎 Thumbs Down: {thumbs_down}")
    print(f"📈 Total:        {total}")

    if total > 0:
        pct_up = (thumbs_up / total) * 100
        print(f"✨ Approval:     {pct_up:.0f}% articles you liked")

    print()


def show_recent_feedback():
    """Display recent feedback entries with article context."""
    handler = FeedbackHandler()

    try:
        conn = sqlite3.connect("data/digest.db")
        cursor = conn.cursor()

        # Get recent feedback with article details
        cursor.execute("""
            SELECT
                f.article_id,
                f.reaction,
                f.comment,
                f.created_at,
                a.title,
                a.source
            FROM feedback f
            JOIN articles a ON f.article_id = a.id
            ORDER BY f.created_at DESC
            LIMIT 20
        """)

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("No feedback entries yet.\n")
            return

        print_separator()
        print("📝 YOUR RECENT FEEDBACK")
        print_separator()
        print()

        for i, row in enumerate(rows, 1):
            article_id, reaction, comment, timestamp, title, source = row

            emoji = "👍" if reaction == "thumbs_up" else "👎"
            reaction_text = "Relevant" if reaction == "thumbs_up" else "Not for me"

            print(f"{i}. {emoji} {reaction_text}")
            print(f"   📰 {title[:70]}")
            print(f"   🔗 {source}")
            if comment:
                print(f"   💬 {comment}")
            print(f"   ⏰ {timestamp}")
            print()

    except Exception as e:
        print(f"Error loading feedback: {e}\n")


def show_liked_articles():
    """Show articles you gave thumbs up to."""
    try:
        conn = sqlite3.connect("data/digest.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT
                a.title,
                a.source,
                a.link,
                a.relevance_score,
                COUNT(f.id) as feedback_count
            FROM articles a
            JOIN feedback f ON a.id = f.article_id
            WHERE f.reaction = 'thumbs_up'
            GROUP BY a.id
            ORDER BY feedback_count DESC, a.relevance_score DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("You haven't thumbed up any articles yet.\n")
            return

        print_separator()
        print("👍 ARTICLES YOU LIKED")
        print_separator()
        print()

        for i, row in enumerate(rows, 1):
            title, source, link, score, count = row
            print(f"{i}. {title}")
            print(f"   Source: {source} | Score: {score}/10")
            print(f"   {link}")
            print()

    except Exception as e:
        print(f"Error loading liked articles: {e}\n")


def show_disliked_articles():
    """Show articles you gave thumbs down to."""
    try:
        conn = sqlite3.connect("data/digest.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT
                a.title,
                a.source,
                a.link,
                a.relevance_score,
                COUNT(f.id) as feedback_count
            FROM articles a
            JOIN feedback f ON a.id = f.article_id
            WHERE f.reaction = 'thumbs_down'
            GROUP BY a.id
            ORDER BY feedback_count DESC, a.relevance_score DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("You haven't thumbed down any articles yet.\n")
            return

        print_separator()
        print("👎 ARTICLES YOU DIDN'T LIKE")
        print_separator()
        print()

        for i, row in enumerate(rows, 1):
            title, source, link, score, count = row
            print(f"{i}. {title}")
            print(f"   Source: {source} | Score: {score}/10")
            print(f"   {link}")
            print()

    except Exception as e:
        print(f"Error loading disliked articles: {e}\n")


def main():
    """Run the feedback dashboard."""
    print()
    show_feedback_summary()
    show_recent_feedback()
    show_liked_articles()
    show_disliked_articles()

    print_separator()
    print("💡 TIP: Your feedback helps improve future rankings!")
    print("   Rate more articles to train the system.")
    print_separator()
    print()


if __name__ == "__main__":
    main()
