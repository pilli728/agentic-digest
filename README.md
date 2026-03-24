# Agentic Edge Daily Digest

A personal intelligence feed for founders building agentic AI products. Pulls from 20+ curated RSS sources, filters for builder relevance using Claude, and delivers a clean daily digest to your inbox and a persistent website archive.

## Quick Start

```bash
cd /Users/pilli/agentic-digest
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script will:
- Create a Python virtual environment
- Install dependencies
- Set up `.env` with placeholders
- Make scripts executable
- Register OpenClaw cron jobs for daily (7 AM) and weekly (7 AM Sunday) runs

## Configuration

### 1. Set your credentials in `.env`

```bash
# Get from console.anthropic.com
ANTHROPIC_API_KEY=sk-...

# Gmail credentials
DIGEST_EMAIL_FROM=you@gmail.com
DIGEST_EMAIL_TO=you@gmail.com
DIGEST_EMAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Gmail app password
```

Get a Gmail app password: https://myaccount.google.com/apppasswords

### 2. Edit `config.yaml`

Update these settings:

```yaml
outputs:
  email:
    to: you@gmail.com  # Required for email delivery
  website:
    enabled: true      # Enable website output when ready

digest:
  daily_top_stories: 15    # Number of top stories per day
  weekly_top_stories: 25   # Number of top stories per week
```

## Usage

### Test the pipeline (dry run)

```bash
source venv/bin/activate
python3 src/orchestrator.py --dry-run
```

This runs the full pipeline but skips email and website output. The digest preview will be printed to your terminal.

### Run once manually

```bash
source venv/bin/activate
python3 src/orchestrator.py --mode daily
```

### Email only (no website)

```bash
python3 src/orchestrator.py --mode daily --email-only
```

### Website only (no email)

```bash
python3 src/orchestrator.py --mode daily --website-only
```

### Weekly digest

```bash
python3 src/orchestrator.py --mode weekly
```

## Scheduling

### Option 1: launchd (Recommended for Mac)

The setup script creates launchd agents for automatic scheduling:

- **Daily digest**: 7:00 AM every day
- **Weekly digest**: 7:00 AM every Sunday

View active jobs:

```bash
launchctl list | grep agentic
```

### Option 2: Standard cron

Add to your crontab:

```bash
crontab -e
```

Then add:

```
0 7 * * * /Users/pilli/agentic-digest/scripts/run.sh
0 7 * * 0 /Users/pilli/agentic-digest/scripts/run_weekly.sh
```

### Option 3: OpenClaw cron

If you want to integrate with OpenClaw's agent system, you can create a wrapper agent that calls the scripts.

## Project Structure

```
agentic-digest/
├── README.md
├── config.yaml                    # Configuration (sources, schedule, outputs)
├── requirements.txt
├── .env                           # Secrets (gitignored)
├── .env.template
├── .gitignore
│
├── src/
│   ├── core/
│   │   ├── fetcher.py             # RSS feed fetching
│   │   ├── filter.py              # Claude-based filtering and ranking
│   │   ├── generator.py           # Markdown digest rendering
│   │   └── models.py              # Article, Digest dataclasses
│   │
│   ├── outputs/
│   │   ├── email_output.py        # Email delivery via Gmail
│   │   ├── website_output.py      # Write to Astro website
│   │   └── substack_output.py     # Newsletter integration (stubbed)
│   │
│   ├── database.py                # SQLite: dedup, archive, state
│   └── orchestrator.py            # Main pipeline
│
├── scripts/
│   ├── run.sh                     # Daily digest entry point (cron)
│   ├── run_weekly.sh              # Weekly digest entry point (cron)
│   └── setup.sh                   # One-command setup
│
├── web/                           # Astro website (coming in Phase 2)
│   └── src/
│       └── content/
│           └── digests/           # .md files written here by pipeline
│
├── data/
│   └── digest.db                  # SQLite database (auto-created)
│
├── output/                        # Raw markdown digests
└── logs/                          # Run logs
```

## Sources (20 feeds across 4 tiers)

### Tier 1: Builder Signal

People shipping things. Framework releases, agent breakthroughs, production lessons.

- Latent Space
- Simon Willison
- LangChain Blog
- OpenAI Blog
- Anthropic Blog
- Google AI Blog
- Hugging Face Blog

### Tier 2: Curated Daily

Pattern recognition from the daily news cycle.

- The Rundown AI
- GenAI.works
- AI++ Newsletter
- Superhuman AI

### Tier 3: Weekly Depth

Long-form analysis and research.

- The Batch (Andrew Ng)
- One Useful Thing (Ethan Mollick)
- Turing Post
- Chip Huyen

### Tier 4: Community Signal

Raw, early trends from tech community.

- Hacker News (Front Page)
- TechCrunch AI
- The Verge AI
- Ars Technica
- MIT Technology Review

## Deduplication

The SQLite database (`data/digest.db`) tracks all articles ever fetched. Once an article is stored, it won't appear in future digests — preventing duplicate stories in multiple days' feeds.

## Logging

All pipeline runs are logged to `logs/digest.log`. Check this file if something goes wrong:

```bash
tail -f logs/digest.log
```

## Cost

Each run uses roughly 3,000–5,000 tokens on Claude Haiku, which is negligible cost (well under $0.01 per day).

## Roadmap

### Phase 1: Core Pipeline ✓
- RSS fetching from 20+ sources
- Claude-based filtering and ranking
- Daily email delivery via Gmail
- SQLite deduplication and archival
- OpenClaw cron integration

### Phase 2: Website
- Astro-based website with digest archive
- Story cards with tier badges and "why it matters"
- Archive page with date navigation
- Deploy to Vercel (free tier)

### Phase 3: Substack Integration
- Weekly digest drafts to Substack
- Manual review before publishing
- Uncomment in config when ready

## FAQ

**Q: Can I add or remove RSS feeds?**
A: Yes. Edit the `FEEDS` dictionary in `src/core/fetcher.py`. Each feed needs a URL, tier (1–4), and focus description.

**Q: How often does it run?**
A: Daily at 7:00 AM and weekly on Sundays at 7:00 AM. Edit in `config.yaml` or via `openclaw cron` commands.

**Q: What if my Mac is asleep when it runs?**
A: OpenClaw's cron system catches up. Jobs will fire the next time your Mac is awake.

**Q: How long are digests kept?**
A: Forever in the SQLite database. Raw `.md` files in `output/` are auto-cleaned after 30 days.

**Q: Can I customize the digest format?**
A: Yes. Edit `src/core/generator.py` to change the markdown template.

**Q: When should I set up the website?**
A: Phase 2 of the roadmap. For now, digests are stored as files in `output/`.

## Support

Issues? Check `logs/digest.log` for error messages.

Common problems:
- **"ANTHROPIC_API_KEY not found"** → Set `ANTHROPIC_API_KEY` in `.env`
- **"Email failed"** → Verify Gmail app password and `DIGEST_EMAIL_*` vars in `.env`
- **"No articles found"** → Check internet connection and feed URLs in `src/core/fetcher.py`

---

Built with Claude. Open source. For founders.
