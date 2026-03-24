#!/usr/bin/env python3
"""
Import sources from research results into the database.

Usage:
    python scripts/import_sources.py RESEARCH_RESULTS.md
    python scripts/import_sources.py ../RESEARCH_RESULTS.json
"""

import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.source_manager import SourceManager


def parse_markdown_sources(filepath):
    """Parse sources from RESEARCH_RESULTS.md"""
    sources = []
    current_category = None

    with open(filepath, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect category headers
        if line.startswith('## Category'):
            if 'Builders' in line:
                current_category = 'builder'
            elif 'Entrepreneurs' in line:
                current_category = 'entrepreneur'
            elif 'Agentic' in line:
                current_category = 'agentic'

        # Detect source entries (numbered)
        if line and line[0].isdigit() and '.' in line and '*' in line:
            # Extract name from "1. **Name**"
            name_start = line.find('**') + 2
            name_end = line.find('**', name_start)
            if name_start > 1 and name_end > name_start:
                source = {
                    'name': line[name_start:name_end],
                    'category': current_category,
                    'url': None,
                    'update_frequency': None,
                    'signal_strength': None,
                    'comment': None,
                }

                # Look ahead for URL, signal strength, etc.
                j = i + 1
                while j < min(i + 10, len(lines)):
                    next_line = lines[j].strip()

                    if next_line.startswith('- URL:'):
                        source['url'] = next_line.replace('- URL:', '').strip()
                    elif next_line.startswith('- Update frequency:'):
                        freq = next_line.replace('- Update frequency:', '').strip()
                        source['update_frequency'] = freq.split()[0]  # Just get first word
                    elif next_line.startswith('- Signal strength:'):
                        strength = next_line.replace('- Signal strength:', '').strip()
                        try:
                            source['signal_strength'] = float(strength.split('/')[0])
                        except:
                            pass
                    elif next_line.startswith('- Why'):
                        # Get the why comment
                        source['comment'] = next_line.split(':', 1)[1].strip()

                    j += 1

                if source['url']:
                    sources.append(source)

        i += 1

    return sources


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_sources.py RESEARCH_RESULTS.md")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    print(f"\nImporting sources from {filepath}...\n")

    # Parse sources
    if filepath.suffix == '.md':
        sources = parse_markdown_sources(filepath)
    elif filepath.suffix == '.json':
        with open(filepath, 'r') as f:
            sources = json.load(f)
    else:
        print("Unsupported format. Use .md or .json")
        sys.exit(1)

    # Import to database
    manager = SourceManager()
    imported = 0

    for source in sources:
        success = manager.add_source_candidate(
            name=source['name'],
            url=source['url'],
            category=source['category'],
            signal_strength=source.get('signal_strength'),
            update_frequency=source.get('update_frequency'),
            comment=source.get('comment'),
        )
        if success:
            imported += 1
            print(f"  ✓ {source['name']}")
        else:
            print(f"  ✗ {source['name']} (duplicate or error)")

    print(f"\n{imported}/{len(sources)} sources imported\n")

    # Show review queue
    print("Next: Review and approve sources\n")
    manager.print_review_queue()

    print("\nApprove sources with:")
    print("  python scripts/approve_source.py \"Source Name\"\n")


if __name__ == "__main__":
    main()
