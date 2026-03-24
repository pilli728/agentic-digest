"""Substack output for the Agentic Digest (STUBBED)."""

# This module is stubbed and disabled until you're ready to integrate Substack.
# When enabled in config.yaml, it will create weekly digest drafts in your Substack publication.


def create_substack_draft(
    digest_content: str,
    date: str,
    publication_url: str = None,
    substack_cookie: str = None,
) -> str:
    """
    Create a draft post on Substack.

    STUBBED: Uncomment and implement when ready.

    Args:
        digest_content: Markdown content of the digest
        date: Date string (YYYY-MM-DD)
        publication_url: Your Substack publication URL
        substack_cookie: Substack session cookie

    Returns:
        Draft post ID if successful, None otherwise
    """
    # TODO: Implement Substack API integration
    # For now, this is a placeholder
    raise NotImplementedError(
        "Substack integration not yet implemented. "
        "Enable in config.yaml when ready."
    )
