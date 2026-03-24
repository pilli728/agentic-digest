#!/bin/bash
# Weekly digest pipeline entry point
# Called by OpenClaw cron at 7:00 AM every Sunday

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/digest.log"

mkdir -p "$PROJECT_DIR/logs"

{
    echo "=========================================="
    echo "Agentic Edge Weekly Digest"
    echo "Started at $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    echo ""

    # Load environment
    if [ -f "$PROJECT_DIR/.env" ]; then
        set -a
        source "$PROJECT_DIR/.env"
        set +a
    fi

    # Run pipeline in weekly mode
    cd "$PROJECT_DIR"
    python3 src/orchestrator.py --mode weekly

    echo ""
    echo "Completed at $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="

} >> "$LOG_FILE" 2>&1

exit 0
