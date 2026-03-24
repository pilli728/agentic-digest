# Agentic Edge Daily Digest - Complete Project Summary

## 🎯 What You've Built

A **personal intelligence feed for founders building agentic AI products**. The system:

1. **Fetches** from 50+ RSS feeds daily (blogs, newsletters, news)
2. **Filters** using Claude to find articles relevant to AI agent builders
3. **Ranks** by relevance score (1-10)
4. **Delivers** via email or website archive
5. **Tracks** feedback (👍👎💭) to improve over time

## 📊 Architecture

```
RSS Feeds (50+)
    ↓
[Fetcher] - Pulls articles, deduplicates
    ↓
[Filter] - Claude rates by "builder relevance"
    ↓
[Generator] - Renders as markdown + metadata
    ↓
[Outputs]
├── Email - Gmail delivery with feedback buttons
└── Website - Astro archive with full-text search
    ↓
[Database] - SQLite for dedup, archive, feedback
```

## 📁 Key Files & Responsibilities

| File | What It Does | Key Points |
|------|-------------|-----------|
| **src/core/fetcher.py** | Pulls articles from RSS feeds | FEEDS dict has 50+ sources with tier (1-4) |
| **src/core/filter.py** | Claude-powered ranking | ⭐ NOW GENERATES 3-SENTENCE SUMMARIES |
| **src/core/generator.py** | Renders digest markdown | Controls article count, order, format |
| **src/core/models.py** | Article/Digest dataclasses | Define data structure |
| **src/database.py** | SQLite: dedup + archive | Prevents duplicates, tracks feedback |
| **src/orchestrator.py** | Main pipeline | Run this! `python3 src/orchestrator.py --dry-run` |
| **src/source_manager.py** | Interactive CLI | Approve/reject sources before use |
| **web/** | Astro website | View/browse digests at localhost:4321 |

## 🚀 Getting Started (Right Now)

### 1. Activate Virtual Environment
```bash
cd /Users/pilli/agentic-digest
source venv/bin/activate
```

### 2. Set API Keys in `.env`
```bash
# Required: Get from console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-...

# Optional: For email delivery
DIGEST_EMAIL_FROM=your@gmail.com
DIGEST_EMAIL_TO=your@gmail.com
DIGEST_EMAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### 3. Test the Pipeline
```bash
python3 src/orchestrator.py --dry-run
```

You'll see:
- ✅ Articles fetched from each feed
- ✅ Claude filtering and ranking
- ✅ **Top 15 articles with 3-sentence summaries** ← NEW!
- ✅ Preview digest output

## 🌐 View the Website

The website is **already running at http://localhost:4321**

You'll see:
- ✅ Today's digest with all articles
- ✅ 3-sentence summaries under each article
- ✅ Relevance scores (visual progress bars)
- ✅ Tier badges (Builder Signal, Curated Daily, etc.)
- ✅ Feedback buttons (👍 Relevant, 👎 Not for me, 💭 Tell me more)
- ✅ Full article links

### View Articles in Grid Mode
The `ArticleGrid.astro` component provides:
- **Compact card layout** - 3 columns on desktop
- **Filter by tier** - Show only certain source categories
- **Filter by score** - Show articles 7+/10 or higher
- **Responsive** - Single column on mobile

## ⚙️ Commands You'll Use

### Daily Operations

```bash
# Test without sending email or updating website
python3 src/orchestrator.py --dry-run

# Run full pipeline (fetch → filter → email + website)
python3 src/orchestrator.py --mode daily

# Weekly digest (25 top stories, 7-day lookback)
python3 src/orchestrator.py --mode weekly

# Email only (skip website)
python3 src/orchestrator.py --mode daily --email-only

# Website only (skip email)
python3 src/orchestrator.py --mode daily --website-only
```

### Interactive Management

```bash
# Review & approve sources before using
python3 src/source_manager.py

# View digest log
tail -f logs/digest.log
```

### Website Development

```bash
cd web

# Already running, but to restart:
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📈 How It Works

### Deduplication
Every article URL is hashed and stored in SQLite. Once seen, it never appears again—preventing the same story appearing across multiple daily digests.

### Filtering
Claude evaluates 50+ articles and ranks by:
- **New model capabilities** that enable agent building
- **Infrastructure releases** (frameworks, APIs, protocols)
- **Fundraising** in the agent space
- **Technical breakthroughs** in reasoning, planning, tool use
- **Production lessons** from teams shipping agents
- **Regulatory moves** affecting builders

### Why the 3-Sentence Summary?
You can now **skim 15 articles in 2 minutes**:
1. **Sentence 1**: What is this about?
2. **Sentence 2**: Why does it matter to agent builders?
3. **Sentence 3**: What action should you take?

### Feedback Loop
Click 👍/👎/💭 in the email or website. This trains the system over time (Phase 2).

## 🗺️ What's Done vs. What's Next

### Phase 1: Core Pipeline ✅
- [x] RSS fetching from 50+ sources
- [x] Claude-powered filtering
- [x] Daily/weekly email delivery
- [x] SQLite dedup & archive
- [x] OpenClaw/launchd scheduling

### Phase 2: Website & Skimming (In Progress)
- [x] Astro website with digest archive
- [x] **3-sentence summaries** ← YOU'RE HERE
- [x] Story card UI with tier badges
- [x] Feedback buttons (👍👎💭)
- [ ] Admin dashboard to manage sources
- [ ] Email preference center
- [ ] Full-text search across all digests

### Phase 3: Intelligence (Future)
- [ ] Feedback-driven ranking (learn from your 👍👎)
- [ ] Custom source addition UI
- [ ] Author following (get only from specific people)
- [ ] Slack/Discord integration
- [ ] Weekly Substack drafts
- [ ] Export to Obsidian/Roam

## 🎨 Customization

### Add More RSS Feeds
Edit `src/core/fetcher.py`, add to `FEEDS` dict:

```python
FEEDS = {
    # ... existing feeds ...
    "Your Blog Name": {
        "url": "https://yourblog.com/feed",
        "tier": 2,  # 1-4, higher = more important
        "focus": "AI agents and infrastructure"
    }
}
```

### Change Digest Length
Edit `config.yaml`:
```yaml
digest:
  daily_top_stories: 20  # Instead of 15
  weekly_top_stories: 30  # Instead of 25
```

### Change Summary Style
Edit `src/core/filter.py` system prompt. Change:
```python
"why_it_matters": "3 sentences: What this is about, why it matters, and what you should do."
```

To whatever format you prefer.

### Schedule Automatically
The system works with launchd (macOS). To set up:
```bash
# Already configured, but to modify:
launchctl list | grep agentic
```

Or use standard cron:
```bash
crontab -e
# Add:
0 7 * * * /Users/pilli/agentic-digest/scripts/run.sh
0 7 * * 0 /Users/pilli/agentic-digest/scripts/run_weekly.sh
```

## 💰 Cost

- **Fetching**: ~100 tokens
- **Filtering 50 articles**: ~3,000 tokens
- **Ranking top 15**: ~500 tokens
- **Total per run**: 3,500-5,000 tokens at Haiku rates = **$0.0005/day**

Negligible cost. Run it every hour if you want.

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "ANTHROPIC_API_KEY not found" | Activate venv + check `.env` |
| Website shows no articles | Run `python3 src/orchestrator.py` to generate digest |
| No articles in digest | Check `logs/digest.log`, verify feed URLs |
| Email not sending | Check Gmail app password is correct |
| Website won't start | Run `npm install` in `web/` folder |
| Duplicates in digest | Database corruption? Delete `data/digest.db` and re-run |

## 🎯 Next Steps for You

### Immediate (Today)
1. ✅ Read this summary (you are here)
2. Set `ANTHROPIC_API_KEY` in `.env`
3. Run `python3 src/orchestrator.py --dry-run`
4. Visit http://localhost:4321 to see the UI
5. Try different feeds/sources in `src/core/fetcher.py`

### Short Term (This Week)
- [ ] Set email credentials in `.env` and run `--mode daily --email-only`
- [ ] Review the sample digest, adjust scoring prompts if needed
- [ ] Set up your first automated run (launchd or cron)
- [ ] Add 5-10 custom RSS feeds you follow

### Medium Term (This Month)
- [ ] Deploy website to Vercel (free tier)
- [ ] Implement feedback loop to improve filtering
- [ ] Add author/source filtering UI
- [ ] Set up Slack notification for top stories

## 📚 Learn More

- **RSS feeds**: Check `src/core/fetcher.py` FEEDS dict
- **Filtering logic**: Check `src/core/filter.py` system prompt
- **Output format**: Check `src/core/generator.py`
- **Database schema**: Check `src/database.py`

## 🔗 Resources

- **Anthropic Docs**: https://docs.anthropic.com
- **Astro Docs**: https://docs.astro.build
- **SQLite**: https://www.sqlite.org/docs.html
- **Python Feedparser**: https://pythonhosted.org/feedparser/

---

**You're all set!** The system is running and generating 3-sentence summaries. Start by running:

```bash
python3 src/orchestrator.py --dry-run
```

Then visit **http://localhost:4321** to see your digest.

Questions? Check the logs:
```bash
tail -f logs/digest.log
```
