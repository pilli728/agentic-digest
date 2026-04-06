#!/usr/bin/env python3
"""
Removes `draft: true` from all premium articles and digests dated today or earlier.
Run by GitHub Actions on Monday before the email send.

Usage:
    python scripts/publish_drafts.py
    python scripts/publish_drafts.py --dry-run
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
DIGESTS_DIR = REPO_ROOT / "web/src/content/digests"
PREMIUM_DIR = REPO_ROOT / "web/src/content/premium"

dry_run = "--dry-run" in sys.argv

def remove_draft(path: Path) -> bool:
    """Remove `draft: true` line from frontmatter. Returns True if changed."""
    text = path.read_text(encoding="utf-8")
    new_text = re.sub(r"^draft: true\n", "", text, flags=re.MULTILINE)
    if new_text == text:
        return False
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return True

def get_date(path: Path) -> datetime | None:
    text = path.read_text(encoding="utf-8")
    m = re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})"?', text, re.MULTILINE)
    if not m:
        return None
    y, mo, d = map(int, m.group(1).split("-"))
    return datetime(y, mo, d, tzinfo=timezone.utc)

now = datetime.now(timezone.utc)
published = []

for directory in [DIGESTS_DIR, PREMIUM_DIR]:
    for f in sorted(directory.glob("*.md")):
        date = get_date(f)
        if date is None or date > now:
            continue
        if remove_draft(f):
            published.append(f.name)
            print(f"{'[dry-run] ' if dry_run else ''}Published: {f.name}")

if not published:
    print("No drafts to publish.")
else:
    print(f"\n{'Would publish' if dry_run else 'Published'} {len(published)} file(s).")
