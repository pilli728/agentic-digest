"""Email feedback integration for the Agentic Digest."""

import sys
from pathlib import Path
from urllib.parse import urlencode

_src_path = Path(__file__).parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from database import DigestDatabase


def generate_feedback_link(
    article_id: str,
    reaction: str,
    base_url: str = "http://localhost:3000"
) -> str:
    """
    Generate a feedback link for email.

    Args:
        article_id: SHA256 hash of article URL
        reaction: 'thumbs_up' or 'thumbs_down'
        base_url: Base URL for feedback endpoint

    Returns:
        Full feedback URL
    """
    params = {
        "article_id": article_id,
        "reaction": reaction,
    }
    return f"{base_url}/api/feedback?{urlencode(params)}"


def enhance_email_with_feedback(
    markdown_digest: str,
    articles: list,
    base_url: str = "http://localhost:3000"
) -> str:
    """
    Add feedback buttons to email digest.

    This modifies the markdown to include email-safe feedback links.

    Args:
        markdown_digest: Original markdown digest
        articles: List of Article objects
        base_url: Base URL for feedback endpoint

    Returns:
        Enhanced markdown with feedback links
    """
    enhanced = markdown_digest

    # For each article, add feedback buttons at the end of the story
    for article in articles:
        if not article.id:
            continue

        link_thumbs_up = generate_feedback_link(
            article.id, "thumbs_up", base_url
        )
        link_thumbs_down = generate_feedback_link(
            article.id, "thumbs_down", base_url
        )

        feedback_section = f"""

**Feedback:**
[👍 Relevant]({link_thumbs_up}) | [👎 Not for me]({link_thumbs_down}) | [💭 Tell me more](mailto:feedback@example.com?subject=Article%20Feedback)
"""
        # Simple string replacement (would be more sophisticated in production)
        # For now, we'll just append feedback links at story level
        # This would be done by the generator, not here

    return enhanced


def record_email_feedback(article_id: str, reaction: str, db: DigestDatabase = None) -> bool:
    """
    Record feedback from email click.

    In production, this would be called via an API endpoint like:
    GET /api/feedback?article_id=xyz&reaction=thumbs_up

    Args:
        article_id: SHA256 hash
        reaction: 'thumbs_up' or 'thumbs_down'
        db: Database instance

    Returns:
        True if recorded successfully
    """
    if db is None:
        db = DigestDatabase()

    try:
        result = db.add_feedback(article_id, reaction=reaction)
        return result
    finally:
        db.close()


class EmailFeedbackTemplate:
    """Helper for adding feedback buttons to email templates."""

    @staticmethod
    def reaction_html(
        article_id: str,
        base_url: str = "http://localhost:3000"
    ) -> str:
        """
        Generate HTML for email feedback buttons.

        Returns HTML that works in email clients.
        """
        thumbs_up_url = generate_feedback_link(
            article_id, "thumbs_up", base_url
        )
        thumbs_down_url = generate_feedback_link(
            article_id, "thumbs_down", base_url
        )

        html = f"""
<div style="margin-top: 1rem; padding: 0.5rem 0; border-top: 1px solid #ddd; font-size: 0.9em;">
  <p style="margin: 0.5rem 0;">
    <a href="{thumbs_up_url}" style="color: #0066cc; text-decoration: none;">👍 Relevant</a>
    &nbsp;|&nbsp;
    <a href="{thumbs_down_url}" style="color: #0066cc; text-decoration: none;">👎 Not for me</a>
  </p>
  <p style="margin: 0.25rem 0; color: #888; font-size: 0.8em;">
    Click to let us know what you think
  </p>
</div>
"""
        return html


if __name__ == "__main__":
    # Test: generate feedback links
    test_article_id = "abc123def456"

    thumbs_up = generate_feedback_link(test_article_id, "thumbs_up")
    thumbs_down = generate_feedback_link(test_article_id, "thumbs_down")

    print(f"Thumbs up link: {thumbs_up}")
    print(f"Thumbs down link: {thumbs_down}")
    print("\nEmail HTML:")
    print(EmailFeedbackTemplate.reaction_html(test_article_id))
