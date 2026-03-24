# Testing Guide for Agentic Edge Digest

## Prerequisites

1. **Anthropic API Key** (required for Claude filtering)
   - Get from: https://console.anthropic.com/
   - Add to `.env`: `ANTHROPIC_API_KEY=sk-...`

2. **Gmail Credentials** (required for email delivery)
   - Gmail app password from: https://myaccount.google.com/apppasswords
   - Update `.env` with:
     ```
     DIGEST_EMAIL_FROM=you@gmail.com
     DIGEST_EMAIL_TO=you@gmail.com
     DIGEST_EMAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
     ```

3. **Configuration** (`config.yaml`)
   - Update `outputs.email.to` with your email address

## Test Sequence

### 1. Verify Environment Setup

```bash
cd /Users/pilli/agentic-digest
source venv/bin/activate
echo $ANTHROPIC_API_KEY  # Should show your API key
```

If empty:
```bash
set -a
source .env
set +a
echo $ANTHROPIC_API_KEY  # Should now show your API key
```

### 2. Test Dry Run (no email, no website)

```bash
python3 src/orchestrator.py --dry-run
```

This will:
- Fetch articles from 20+ RSS sources
- Deduplicate against database
- Filter with Claude
- Generate markdown digest
- Print preview to terminal
- **Skip email and website output**

Expected output:
```
=== Agentic Edge Daily Digest ===

  [1/5] Fetching articles from RSS feeds...
  Fetched 23 articles from 20 sources.
  [2/5] Deduplicating articles...
  [3/5] Filtering and ranking with Claude...
  [4/5] Generating digest...
  [5/5] Delivering digest...
  [DRY RUN] Skipping email and website output.

--- DIGEST PREVIEW ---

# Agentic Edge Daily Digest
**[Today's Date]**
...
```

### 3. Test Deduplication

Run dry-run twice in a row:

```bash
python3 src/orchestrator.py --dry-run
python3 src/orchestrator.py --dry-run
```

The second run should show:
```
  [2/5] Deduplicating articles...
  [DEDUP] Skipping: [Article title]...
  ⚠ All articles were duplicates. Skipping digest.
```

This confirms the database is preventing duplicate stories.

### 4. Test Email Delivery

```bash
python3 src/orchestrator.py --mode daily --email-only
```

Expected output:
```
  ✓ Digest emailed to you@gmail.com
```

Check your inbox within 30 seconds. Email should appear with:
- Subject: "Agentic Edge Digest | [Today's Date]"
- HTML formatted digest with story cards
- Links to full articles

### 5. Test Database

```bash
sqlite3 data/digest.db "SELECT COUNT(*) FROM articles;"
```

Should return a non-zero number (total articles ever fetched).

```bash
sqlite3 data/digest.db "SELECT * FROM digests ORDER BY date DESC LIMIT 1;"
```

Should show the most recent digest entry.

### 6. Test Web Output

```bash
python3 src/orchestrator.py --mode daily --website-only
```

Check for created file:
```bash
ls -la web/src/content/digests/
```

Should show: `YYYY-MM-DD-digest.md`

### 7. Full Pipeline Test

```bash
python3 src/orchestrator.py --mode daily
```

This will:
- Fetch and deduplicate articles
- Filter with Claude
- Generate digest
- Send email
- Write to website (if enabled)
- Store in database

### 8. Verify launchd Installation

After running setup.sh:

```bash
launchctl list | grep agentic
```

Should show both jobs:
```
com.agenticedge.dailydigest
com.agenticedge.weeklydigest
```

Check logs:
```bash
tail -f logs/digest.log
```

## Common Issues

### "ANTHROPIC_API_KEY not found"

Add your API key to `.env`:
```bash
echo "ANTHROPIC_API_KEY=sk-..." >> .env
```

Then reload:
```bash
set -a
source .env
set +a
```

### "Email failed: [SMTPAuthenticationError]"

- Verify Gmail app password (not your regular password)
- Confirm password is correct in `.env`
- Check Gmail security settings: https://myaccount.google.com/apppasswords

### "No articles found"

- Check internet connection: `curl https://www.latent.space/feed`
- Feed URLs may be temporarily down
- Try again in a few minutes

### "Claude filtering produced no results"

- API key might be invalid
- Check Anthropic console for rate limits
- Verify articles were fetched in previous step

### Database locked

If you get `database is locked`:
- Ensure no other process is accessing `data/digest.db`
- Close all open digest runs with `Ctrl+C`
- Try again

## Success Criteria

✓ Dry run completes with digest preview
✓ Email arrives in inbox with formatted digest
✓ Database stores articles and prevents duplicates
✓ Website markdown file is created
✓ launchd jobs appear in `launchctl list`
✓ Logs are written to `logs/digest.log`

## Next Steps

Once all tests pass:
1. Set up launchd for automatic daily runs
2. Customize RSS feeds in `src/core/fetcher.py`
3. Build Astro website (Phase 2)
4. Deploy to Vercel
5. Enable Substack integration (when ready)

## Running Manually

For one-time runs:

```bash
cd /Users/pilli/agentic-digest
source venv/bin/activate

# Daily digest
./scripts/run.sh

# Weekly digest
./scripts/run_weekly.sh
```

Check results:
```bash
tail -20 logs/digest.log
```
