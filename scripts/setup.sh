#!/bin/bash
# One-command setup for Agentic Edge Daily Digest
# Creates venv, installs dependencies, configures .env, registers OpenClaw cron jobs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "==========================================="
echo "Agentic Edge Digest - Setup"
echo "==========================================="
echo ""

# Step 1: Create virtual environment
echo "Step 1: Creating Python virtual environment..."
cd "$PROJECT_DIR"
python3 -m venv venv
source venv/bin/activate
echo "✓ Virtual environment created"

# Step 2: Install dependencies
echo ""
echo "Step 2: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Step 3: Set up .env file
echo ""
echo "Step 3: Configuring environment variables..."
if [ -f "$PROJECT_DIR/.env" ]; then
    echo "  .env already exists. Skipping."
else
    cp "$PROJECT_DIR/.env.template" "$PROJECT_DIR/.env"
    chmod 600 "$PROJECT_DIR/.env"
    echo "  Created .env (mode 600)"
fi

echo ""
echo "  Edit $PROJECT_DIR/.env and set:"
echo "    ANTHROPIC_API_KEY="
echo "    DIGEST_EMAIL_FROM="
echo "    DIGEST_EMAIL_TO="
echo "    DIGEST_EMAIL_PASSWORD= (Gmail app password)"
echo ""

# Step 4: Make scripts executable
echo "Step 4: Making scripts executable..."
chmod +x "$PROJECT_DIR/scripts/run.sh"
chmod +x "$PROJECT_DIR/scripts/run_weekly.sh"
echo "✓ Scripts are executable"

# Step 5: Register launchd jobs
echo ""
echo "Step 5: Registering launchd jobs..."
mkdir -p "$HOME/Library/LaunchAgents"

cp "$PROJECT_DIR/com.agenticedge.dailydigest.plist" "$HOME/Library/LaunchAgents/"
cp "$PROJECT_DIR/com.agenticedge.weeklydigest.plist" "$HOME/Library/LaunchAgents/"

launchctl load "$HOME/Library/LaunchAgents/com.agenticedge.dailydigest.plist" 2>/dev/null || true
launchctl load "$HOME/Library/LaunchAgents/com.agenticedge.weeklydigest.plist" 2>/dev/null || true

echo "✓ launchd jobs registered"
echo ""
echo "  View jobs with: launchctl list | grep agentic"
echo "  Remove jobs with: launchctl unload ~/Library/LaunchAgents/com.agenticedge.*.plist"

# Step 6: Configuration
echo ""
echo "Step 6: Checking configuration..."
if [ -f "$PROJECT_DIR/config.yaml" ]; then
    echo "  Edit $PROJECT_DIR/config.yaml to customize:"
    echo "    - outputs.email.to (required for email delivery)"
    echo "    - digest.daily_top_stories / weekly_top_stories"
    echo "    - schedule times"
else
    echo "  ✗ config.yaml not found!"
    exit 1
fi

echo ""
echo "==========================================="
echo "Setup Complete!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env and set your credentials"
echo "  2. Edit config.yaml and set outputs.email.to"
echo "  3. Test with: python3 src/orchestrator.py --dry-run"
echo "  4. View cron jobs: openclaw cron list"
echo ""
