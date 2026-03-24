# Getting Started with Agentic Edge Daily Digest

## What This Project Does

A **personal intelligence feed** for founders building agentic AI products. It:
- Fetches 50+ RSS feeds (blogs, newsletters, news)
- Uses Claude to filter for "would a builder need to know this TODAY?"
- Delivers a 15-article daily digest + 25-article weekly digest
- Sends via email or publishes to a website archive
- Tracks what you like/dislike to improve recommendations

## Architecture at a Glance

```
RSS Feeds (50+)
    ↓
Fetcher (src/core/fetcher.py)
    ↓
Filter & Rank (Claude) (src/core/filter.py)
    ↓
Generator (Markdown) (src/core/generator.py)
    ↓
Outputs: Email + Website (src/outputs/)
    ↓
SQLite DB (dedup, archive, feedback)
```

### Key Files

| File | Purpose |
|------|---------|
| `src/core/fetcher.py` | Pulls articles from RSS feeds |
| `src/core/filter.py` | Claude-powered filtering (builder relevance) |
| `src/core/generator.py` | Renders digest as markdown |
| `src/core/models.py` | Article, Digest dataclasses |
| `src/database.py` | SQLite: dedup, archive, feedback tracking |
| `src/orchestrator.py` | Main pipeline (run this) |
| `src/source_manager.py` | Interactive CLI to approve/reject sources |
| `web/` | Astro website for browsing archive |

## Setup (5 minutes)

### 1. Activate Python Virtual Environment

```bash
cd /Users/pilli/agentic-digest
source venv/bin/activate
```

### 2. Set Your API Keys

Copy `.env.template` to `.env` and fill in:

```bash
# Get from console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-...
```

Optional (for email delivery):
```bash
DIGEST_EMAIL_FROM=your@gmail.com
DIGEST_EMAIL_TO=your@gmail.com
DIGEST_EMAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Gmail app password
```

Get Gmail app password: https://myaccount.google.com/apppasswords

### 3. Test the Pipeline

```bash
python3 src/orchestrator.py --dry-run
```

You'll see:
- Articles fetched from each feed
- Claude filtering them by relevance
- Top 15 ranked articles with scores and "why it matters"
- Final digest preview

**Output**: Check `output/` folder for generated `.md` files

## Commands You'll Use

### Run Daily Digest
```bash
python3 src/orchestrator.py --mode daily
```

### Run Weekly Digest
```bash
python3 src/orchestrator.py --mode weekly
```

### Test Without Email
```bash
python3 src/orchestrator.py --dry-run
```

### Email Only (No Website)
```bash
python3 src/orchestrator.py --mode daily --email-only
```

### Website Only (No Website)
```bash
python3 src/orchestrator.py --mode daily --website-only
```

### Review Sources Interactively
```bash
python3 src/source_manager.py
```

## View the Website Locally

### 1. Install Dependencies
```bash
cd web
npm install
```

### 2. Start Dev Server
```bash
npm run dev
```

Visit: **http://localhost:3000**

You'll see:
- Latest digest with all articles
- 3-sentence summaries for quick skimming
- Relevance scores (1-10)
- Tier badges (1-4)
- Link to full article

### 3. Build for Production
```bash
npm run build
```

## Data Flows

### How Deduplication Works

Every article is hashed on its URL. Once stored in SQLite, it won't appear again — preventing duplicates across days.

### How Feedback Works

When you click 👍/👎 in the email, it updates the database. (Phase 2 feature)

### How Archive Works

Each digest is saved as `.md` in `web/src/content/digests/` and rendered by Astro.

## What's Next (Roadmap)

### Phase 1 ✅ (Done)
- RSS fetching from 50+ sources
- Claude filtering by builder relevance
- Daily/weekly email delivery
- SQLite dedup & archive

### Phase 2 (In Progress)
- [x] Astro website with digest archive
- [ ] **3-sentence summaries** for faster skimming
- [ ] Interactive article cards with relevance badges
- [ ] Author filtering (see only from builder-focused sources)

### Phase 3 (Future)
- Feedback loop (track which summaries you like)
- Weekly digest drafts to Substack
- Custom source addition UI
- Full-text search across archive

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
→ Make sure `.env` has your key and you activated the venv

### "No articles found"
→ Check internet connection or verify feed URLs in `src/core/fetcher.py`

### Website won't start
→ Make sure you ran `npm install` in the `web/` folder

### Articles not showing in digest
→ Check `logs/digest.log` for errors

## Cost

Each daily run: ~3,000-5,000 tokens on Claude Haiku = **$0.0005/day** (negligible)

## Want to Customize?

- **Add/remove RSS feeds**: Edit `FEEDS` dict in `src/core/fetcher.py`
- **Change digest format**: Edit template in `src/core/generator.py`
- **Adjust relevance criteria**: Modify system prompt in `src/core/filter.py`
- **Change summary length**: Update Claude prompt in `src/core/filter.py`

---

**Next step**: Run `python3 src/orchestrator.py --dry-run` to see it in action!
