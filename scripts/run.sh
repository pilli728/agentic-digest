#!/bin/bash
# Main entry point for daily digest pipeline
# Called by OpenClaw cron at 7:00 AM daily

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/digest.log"

mkdir -p "$PROJECT_DIR/logs"

{
    echo "=========================================="
    echo "Agentic Edge Daily Digest"
    echo "Started at $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    echo ""

    # Load environment
    if [ -f "$PROJECT_DIR/.env" ]; then
        set -a
        source "$PROJECT_DIR/.env"
        set +a
    fi

    # Run pipeline in daily mode
    cd "$PROJECT_DIR"
    python3 src/orchestrator.py --mode daily

    echo ""
    echo "Completed at $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="

} >> "$LOG_FILE" 2>&1

exit 0
