"""Website output for the Agentic Digest (Astro integration)."""

from pathlib import Path


def write_digest_to_website(
    digest_content: str,
    date: str,
    content_dir: str = "web/src/content/digests"
) -> bool:
    """
    Write digest markdown to the Astro website content directory.

    Args:
        digest_content: Markdown content of the digest
        date: Date string (YYYY-MM-DD)
        content_dir: Path to Astro content/digests directory

    Returns:
        True if written successfully, False otherwise
    """
    try:
        content_path = Path(content_dir)
        content_path.mkdir(parents=True, exist_ok=True)

        filename = f"{date}-digest.md"
        filepath = content_path / filename

        # Add Astro frontmatter
        frontmatter = f"""---
title: "Agentic Edge Digest - {date}"
date: {date}
layout: ../../layouts/DigestLayout.astro
---

"""
        full_content = frontmatter + digest_content

        filepath.write_text(full_content)
        print(f"  ✓ Website digest written to {filepath}")
        return True

    except Exception as e:
        print(f"  ✗ Failed to write website digest: {e}")
        return False
