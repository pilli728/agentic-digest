# Current Status - Agentic Digest System

## ✅ **All Systems Running**

```
🌐 EXTERNAL WEBSITE (Customer-facing)
   URL: http://localhost:4321
   Server: Astro dev server
   Status: ✅ RUNNING
   Purpose: Beautiful digest for your audience

🎓 INTERNAL DASHBOARD v2 (Training - NEW!)
   URL: http://localhost:3000/internal_dashboard_v2.html
   Server: Python HTTP server
   Status: ✅ RUNNING
   Purpose: Rate ALL 58+ articles organized by tier

📰 ARTICLES API (Backend - NEW!)
   URL: http://localhost:8001/api/articles
   Server: Python articles_api.py
   Status: ✅ RUNNING
   Purpose: Serves article data to the dashboard

🔗 FEEDBACK API (Ratings Backend)
   URL: http://localhost:8000/api/feedback
   Server: Python feedback_server.py
   Status: ✅ RUNNING
   Purpose: Saves your 👍👎💭 ratings
```

---

## 📊 **Current Data in System**

```
Total Articles:     58
├── Tier 1 (Builder Signal 🚀):  10 articles
└── Tier 4 (Community Signal 💬): 48 articles

Articles Ranked:    0 (need to add API key and run pipeline)
Your Ratings:       0

Database:          data/digest.db (SQLite)
```

---

## 🎯 **What You Have**

### **1. Internal Training Dashboard**
- **Location**: `internal_dashboard_v2.html`
- **Access**: http://localhost:3000/internal_dashboard_v2.html
- **Shows**:
  - All 58 articles organized by tier
  - Claude's scores
  - Beautiful card layout
  - Rate articles 👍👎💭
  - See your feedback patterns

### **2. External Customer Website**
- **Location**: `web/` (Astro site)
- **Access**: http://localhost:4321
- **Shows**:
  - Top 15 curated articles only
  - Professional design
  - What your audience sees

### **3. Feedback System**
- **Internal**: Rate articles to train the AI
- **Storage**: SQLite database
- **API**: http://localhost:8000/api/feedback

### **4. Articles API**
- **Purpose**: Serves all articles to dashboard
- **Endpoints**:
  - `/api/articles` - All articles flat
  - `/api/articles/by-tier` - Organized by tier
  - `/api/articles/stats` - Statistics

---

## 🚀 **Next Steps (Priority Order)**

### **STEP 1: Add Your API Key** ⚠️ REQUIRED
```bash
# Edit .env and add:
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Get key from: https://console.anthropic.com

This is **required** to fetch and rank today's articles.

### **STEP 2: Run Fresh Pipeline**
```bash
source venv/bin/activate
python3 src/orchestrator.py --mode daily
```

This will:
- ✅ Fetch 50+ articles from today's RSS feeds
- ✅ Include breaking news (Claude computer, latest AI news, etc.)
- ✅ Rank everything with Claude (3-sentence summaries)
- ✅ Update the database
- ✅ Organize by builder relevance

**Time**: ~1-2 minutes

### **STEP 3: Open Improved Dashboard**
http://localhost:3000/internal_dashboard_v2.html

You'll see:
- 📊 Stats: Total articles, ranked, avg score
- 🚀 Tier 1: Builder Signal articles (high signal)
- 📰 Tier 2: Curated Daily articles (if any)
- 📚 Tier 3: Weekly Depth articles (if any)
- 💬 Tier 4: Community Signal articles (if any)

### **STEP 4: Train the System**
For each article:
- Click 👍 **Relevant** if it's useful for AI agent builders
- Click 👎 **Skip** if it's off-topic
- Click 💭 **Why?** to explain your rating

Rate 20-30 articles to start. The system learns from your patterns.

### **STEP 5: Check External Website**
http://localhost:4321

See what your customers will view - the top 15 curated articles based on Claude's ranking + your feedback.

---

## 📋 **Dashboard Features**

### **Internal Dashboard v2**

**Organization**
- Articles grouped by tier (Builder Signal, Curated Daily, Weekly Depth, Community Signal)
- Each tier shows count of articles
- Beautiful card layout for each article

**Per-Article Display**
- Rank number (#1, #2, etc.)
- Title with link to original
- Source + Claude score
- Why it matters (Claude's 3-sentence summary)
- Your feedback buttons (👍👎)
- Comment section (💭)

**Filters & Controls**
- Sort by: Score, Unrated First, Most Recent
- Min Score slider (0-10)
- Refresh button
- Reset filters button

**Statistics**
- Total articles in system
- How many are ranked by Claude
- Your rating count
- Average relevance score

---

## 🔄 **The Workflow**

```
DAY 1:
┌─────────────────────────────────┐
│ 1. Add API key to .env          │
│ 2. Run: python3 orchestrator.py │
│    (fetches 50+ articles)       │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│ 3. Open internal dashboard      │
│    (localhost:3000/...)         │
│ 4. Rate 20-30 articles          │
│    (👍 relevant, 👎 skip)       │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│ 5. Check external website       │
│    (localhost:4321)             │
│    See top 15 for customers     │
└─────────────────────────────────┘

WEEK 1:
- You rate 100+ articles
- System learns your patterns
- Next pipeline run uses your feedback
- External site improves

WEEK 4:
- System knows exactly what you like
- Top 15 articles are personalized
- Customers see your best picks
- Perfect feedback loop! 🎓
```

---

## 🎨 **Architecture Overview**

```
┌──────────────────────────────────────────────────┐
│          Your Rating Training                    │
│      (Internal Dashboard v2)                     │
│      localhost:3000                              │
│                                                  │
│  You rate articles 👍👎💭                        │
│  System learns: "user likes X"                   │
└──────────────────────────────────────────────────┘
    ↓ (saves feedback)                ↓ (reads articles)
┌──────────────────────────┐   ┌────────────────────┐
│  Feedback API            │   │  Articles API      │
│  :8000                   │   │  :8001             │
│  Stores ratings          │   │  Serves data       │
└──────────────────────────┘   └────────────────────┘
    ↓ (both write to)
┌──────────────────────────────────────────────────┐
│         SQLite Database                          │
│      (data/digest.db)                            │
│                                                  │
│  ├── articles (all fetched)                      │
│  ├── feedback (your ratings)                     │
│  ├── digests (daily/weekly)                      │
│  └── digest_articles (which articles in digest)  │
└──────────────────────────────────────────────────┘
    ↓ (pulls articles)
┌──────────────────────────────────────────────────┐
│      External Customer Website                   │
│      (Astro - localhost:4321)                    │
│                                                  │
│  Shows: Top 15 articles only                     │
│  Design: Professional, polished                  │
│  For: Your audience/customers                    │
└──────────────────────────────────────────────────┘
```

---

## ✨ **Key Features**

✅ **All 58+ articles visible** (not just 3)
✅ **Organized by tier** (Builder Signal, Curated Daily, etc.)
✅ **Real data from database** (not mock data)
✅ **Your feedback buttons** (👍👎💭)
✅ **Statistics tracking** (total, ranked, avg score)
✅ **Beautiful design** for both internal & external
✅ **Feedback API** saves your ratings
✅ **External website** shows curated top 15

---

## 🆘 **Troubleshooting**

### Dashboard shows "Loading..." forever
- Check articles API is running: `curl http://localhost:8001/api/articles/stats`
- Check articles exist: `sqlite3 data/digest.db "SELECT COUNT(*) FROM articles"`

### Can't rate articles
- Check feedback API: `curl http://localhost:8000/api/feedback/summary`
- Check feedback server is running

### Want to add more articles
- Add API key to `.env`
- Run: `python3 src/orchestrator.py --mode daily`
- This fetches 50+ fresh articles

### Want different article sources
- Edit `src/core/fetcher.py`
- Add new RSS feeds to FEEDS dict
- Run pipeline again

---

## 📞 **Available Commands**

```bash
# Fetch & rank articles
python3 src/orchestrator.py --mode daily

# Fetch only (no Claude ranking)
python3 src/orchestrator.py --dry-run

# See your feedback patterns
python3 src/feedback_dashboard.py

# View logs
tail -f logs/digest.log
```

---

## 🎯 **Right Now**

1. **Open internal dashboard**: http://localhost:3000/internal_dashboard_v2.html
2. **See 58 real articles** organized by tier
3. **Add API key** to `.env` when ready
4. **Run pipeline** to get today's latest articles
5. **Start rating** to train the system!

**Everything is ready to go!** 🚀
