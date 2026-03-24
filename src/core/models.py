"""Data models for the Agentic Digest pipeline."""

from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class Article:
    """Represents a single article from an RSS feed."""
    source: str
    tier: int
    title: str
    link: str
    summary: str
    published: str
    id: Optional[str] = None  # SHA256 hash of URL
    relevance_score: Optional[float] = None
    why_it_matters: Optional[str] = None
    fetched_at: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Digest:
    """Represents a generated digest."""
    date: str  # YYYY-MM-DD
    mode: str  # 'daily' or 'weekly'
    content: str  # Markdown content
    articles: list[Article]
    filename: Optional[str] = None
    email_sent: bool = False
    website_published: bool = False
    substack_draft_id: Optional[str] = None
    created_at: Optional[str] = None
