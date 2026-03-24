# Quick Reference Card

## ⚡ Most Common Commands

```bash
# Activate environment
source venv/bin/activate

# Test the system (no email/website output)
python3 src/orchestrator.py --dry-run

# Generate and send email
python3 src/orchestrator.py --mode daily

# Generate and update website
python3 src/orchestrator.py --mode daily --website-only

# View logs in real-time
tail -f logs/digest.log

# Start website (if needed)
cd web && npm run dev
```

## 🌐 URLs

- **Website**: http://localhost:4321
- **View latest digest**: http://localhost:4321
- **Browse archive**: http://localhost:4321/archive

## 📊 What Runs When

| Command | Fetches | Filters | Email | Website | Time |
|---------|---------|---------|-------|---------|------|
| `--dry-run` | ✅ | ✅ | ❌ | ❌ | 30s |
| `--mode daily` | ✅ | ✅ | ✅ | ✅ | 45s |
| `--email-only` | ✅ | ✅ | ✅ | ❌ | 40s |
| `--website-only` | ✅ | ✅ | ❌ | ✅ | 40s |

## 🎛️ Configuration

- **Feeds**: `src/core/fetcher.py` (FEEDS dict)
- **Settings**: `config.yaml`
- **Credentials**: `.env`
- **Formatting**: `src/core/generator.py`
- **Filtering logic**: `src/core/filter.py`

## 📋 File Structure

```
📂 agentic-digest/
  📄 README.md (main docs)
  📄 PROJECT_SUMMARY.md (you are here)
  📄 GETTING_STARTED.md (detailed setup)
  📄 config.yaml (settings)
  📄 .env (secrets, not in git)
  📂 src/
    📂 core/
      📄 fetcher.py (RSS pulling)
      📄 filter.py (Claude ranking) ⭐ 3-sentence summaries
      📄 generator.py (markdown output)
      📄 models.py (data structures)
    📂 outputs/
      📄 email_output.py (Gmail)
      📄 website_output.py (Astro)
    📄 orchestrator.py (main pipeline) ⭐ RUN THIS
    📄 database.py (SQLite)
    📄 source_manager.py (CLI tool)
  📂 web/ (Astro website)
    📂 src/
      📂 content/
        📂 digests/ (generated .md files)
      📂 components/
        📄 StoryCard.astro (article card)
        📄 ArticleGrid.astro ⭐ NEW! Grid view with filters
  📂 data/
    📄 digest.db (SQLite database)
  📂 logs/
    📄 digest.log (debug logs)
  📂 output/
    📄 *.md (raw digests)
```

## 🔍 Debugging

1. **Check logs**: `tail -f logs/digest.log`
2. **Test API key**: `python3 -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"`
3. **Verify environment**: `env | grep -i anthropic`
4. **Check database**: `sqlite3 data/digest.db ".tables"`

## 🎯 Common Tasks

### Add a new RSS feed
```python
# In src/core/fetcher.py, add to FEEDS dict:
"My Blog": {
    "url": "https://myblog.com/feed",
    "tier": 2,
    "focus": "agent infrastructure"
}
```

### Change article count
```yaml
# In config.yaml:
digest:
  daily_top_stories: 20  # was 15
```

### Change Claude model
```yaml
# In config.yaml:
model: claude-opus-4-6  # was haiku
```

### Change summary style
```python
# In src/core/filter.py, change the prompt:
"why_it_matters": "Your custom format here..."
```

## 📊 What's New in This Version

- ✨ **3-sentence summaries** instead of 1-sentence
- ✨ **ArticleGrid component** with filtering by tier/score
- ✨ **Getting Started guide** with step-by-step setup
- ✨ **Project Summary** (this document)

## ⏰ Scheduling

### macOS (launchd) - Already Set Up
```bash
launchctl list | grep agentic
launchctl start com.agentic-digest.daily
```

### Linux/Windows (cron)
```bash
crontab -e
# Add:
0 7 * * * /Users/pilli/agentic-digest/scripts/run.sh
```

## 💡 Tips

1. **Run `--dry-run` first** to see output before emails
2. **Check logs** when something breaks
3. **Use `source_manager.py`** to review sources before running
4. **Visit website** to see how articles are displayed
5. **Leave feedback** (👍👎💭) to train the system

## 🆘 Help

- Stuck? Read: `README.md`
- Setup issues? Read: `GETTING_STARTED.md`
- Want full context? Read: `PROJECT_SUMMARY.md`
- See logs: `tail -f logs/digest.log`

---

**Ready to run?**

```bash
source venv/bin/activate
python3 src/orchestrator.py --dry-run
```

Then visit: http://localhost:4321
