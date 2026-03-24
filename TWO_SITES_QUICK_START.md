# Two-Website Setup: Quick Start

## 🎯 The Two Sites

### 1. **Internal Training Dashboard** (localhost:3000)
**Just for you** to train the system
- See ALL 50+ articles
- Rate them 👍👎💭
- See Claude's scores vs your scores
- Debug why articles ranked where they did
- See your rating patterns

### 2. **External Customer Website** (localhost:4321)
**For your readers/customers**
- See only the top 15 curated articles
- Beautiful, professional design
- 3-sentence summaries
- Tier badges & relevance scores
- Archive of past digests

---

## 🚀 How to Run Both

### **Terminal 1: Start Feedback API** (required for both sites)
```bash
cd /Users/pilli/agentic-digest
source venv/bin/activate
python3 src/feedback_server.py
```

Output:
```
🚀 Feedback API Server Started
Listening on: http://localhost:8000/api/feedback
```

### **Terminal 2: Start Internal Dashboard**
```bash
# From the root directory, open the HTML file:
open internal_dashboard.html
# Or just open in your browser:
# http://localhost:3000 (if running a local server)
```

**Or**, serve it locally with Python:
```bash
cd /Users/pilli/agentic-digest
python3 -m http.server 3000
```

Then visit: **http://localhost:3000/internal_dashboard.html**

### **Terminal 3: Astro Website (already running)**
The external website is already running at: **http://localhost:4321**

---

## 📊 How They Work Together

```
┌─────────────────────────────────────────────────┐
│ You Generate Daily Digest                      │
│ python3 src/orchestrator.py --mode daily       │
└─────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        ↓                               ↓
┌──────────────────────┐        ┌──────────────────────┐
│ ALL 50 Articles      │        │ TOP 15 Curated       │
│ (Internal)           │        │ (External)           │
│ localhost:3000       │        │ localhost:4321       │
│                      │        │                      │
│ - All articles       │        │ - Best articles only │
│ - Rate 👍👎💭        │        │ - Beautiful design   │
│ - Debug scores       │        │ - For customers      │
│ - See patterns       │        │ - Professional       │
└──────────────────────┘        └──────────────────────┘
        ↓                               ↑
        └─── Both use same database ───┘
            (SQLite + Feedback API)
```

---

## 🎓 Your Workflow

### **Phase 1: Generate Digest**
```bash
python3 src/orchestrator.py --mode daily
```
Creates 50 articles ranked by Claude, stored in database.

### **Phase 2: Train (Internal Dashboard)**
Open: **http://localhost:3000/internal_dashboard.html**

You'll see:
```
🎓 INTERNAL TRAINING DASHBOARD

📊 Stats:
  50 Articles Fetched
  0 Articles Rated
  0 👍 Relevant
  0 👎 Not for me

[Article #1]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rank: #1
Title: Claude 3.5 Achieves New Benchmark
Source: Anthropic Blog (Tier 1)
Claude Score: 10/10

Why: New reasoning capabilities unlock...

[👍 Relevant] [👎 Not for me]
[💭 Tell me why...]
```

Rate articles:
- 👍 if Claude got it right and it's builder-relevant
- 👎 if Claude was wrong or it's not relevant
- 💭 to write why you rated it

### **Phase 3: Check External Site**
Open: **http://localhost:4321**

You'll see:
- Only the top 15 (that you and Claude both like)
- Clean, professional design
- What customers/readers see

### **Phase 4: See Your Patterns**
```bash
python3 src/feedback_dashboard.py
```

Output:
```
📊 YOUR FEEDBACK SUMMARY
════════════════════════
👍 Thumbs Up:    8
👎 Thumbs Down: 2
📈 Total:        10
✨ Approval:     80% articles you liked

📝 YOUR RECENT FEEDBACK
════════════════════════
1. 👍 Relevant - Claude 3.5 Achieves...
   🔗 Anthropic Blog | Score: 10/10
   💬 "Explains core capability..."
```

---

## 💡 Example Day

**Morning:**
1. Run digest: `python3 src/orchestrator.py --mode daily`
2. Open internal dashboard: http://localhost:3000/internal_dashboard.html
3. Rate the 50 articles (takes ~10 minutes)
   - 👍 articles from Anthropic, LangChain (usually good)
   - 👎 articles from general tech news (not builder-focused)
4. Check stats: your 75% approval rate means good signal!

**Check external site:**
- Visit http://localhost:4321
- See the top 15 articles
- Think: "Yes, this is what I'd want to send to my audience"

**Review patterns:**
- Run: `python3 src/feedback_dashboard.py`
- See which sources you trust most
- Realize: "I always like Anthropic and LangChain"

**Next day:**
- Run digest again
- Claude now weighs Anthropic higher
- Internal dashboard shows better top 15
- External site looks even better!

---

## 📁 File Locations

| File | Purpose | Access |
|------|---------|--------|
| `internal_dashboard.html` | Internal training UI | http://localhost:3000/internal_dashboard.html |
| `web/` | External customer site | http://localhost:4321 |
| `src/feedback_server.py` | API backend | http://localhost:8000/api/feedback |
| `src/feedback_dashboard.py` | CLI feedback viewer | Run in terminal |
| `data/digest.db` | Shared database | Both sites use this |

---

## 🔄 The Training Loop (Over Time)

**Week 1:**
- You rate 50 articles/day
- System has 350 ratings
- Can see patterns: "I like X, don't like Y"

**Week 2:**
- Claude sees your patterns
- Rankings adjust based on your feedback
- External site improves
- Customers are happier!

**Week 4:**
- System has learned YOUR preferences
- Top 15 articles are personalized to you
- External site is optimized
- Perfect feedback loop

---

## ⚙️ Technical Breakdown

### Internal Dashboard
- **Tech**: Plain HTML + JavaScript
- **Purpose**: Functional UI for training
- **Data**: Reads from SQLite database
- **Feedback**: Sends to feedback API (port 8000)

### External Website
- **Tech**: Astro (static site generator)
- **Purpose**: Beautiful customer-facing site
- **Data**: Shows only top 15 from database
- **Design**: Professional, clean, optimized

### Shared Infrastructure
- **Database**: SQLite (`data/digest.db`)
- **API**: Feedback server (port 8000)
- **Pipeline**: `src/orchestrator.py`

---

## 🎯 Quick Reference

### Start Everything (in 3 terminals)

```bash
# Terminal 1: Feedback API
python3 src/feedback_server.py

# Terminal 2: Internal Dashboard
python3 -m http.server 3000
# Then open http://localhost:3000/internal_dashboard.html

# Terminal 3: Already running
# External site: http://localhost:4321
```

### URLs

| Site | URL | Purpose |
|------|-----|---------|
| **Internal** | http://localhost:3000/internal_dashboard.html | Train system (just you) |
| **External** | http://localhost:4321 | Customer-facing (public) |
| **API** | http://localhost:8000/api/feedback | Feedback backend |

### Commands

```bash
# Generate new digest with all articles
python3 src/orchestrator.py --mode daily

# Review your feedback patterns
python3 src/feedback_dashboard.py

# Start feedback API
python3 src/feedback_server.py

# Serve internal dashboard locally
python3 -m http.server 3000
```

---

## ✨ Benefits of Two Sites

| Aspect | Internal | External |
|--------|----------|----------|
| **Audience** | Just you | Everyone |
| **Articles shown** | All 50+ | Top 15 only |
| **Purpose** | Train AI | Share digest |
| **Design** | Functional | Beautiful |
| **Data visibility** | Debug data | Polished only |
| **Update frequency** | Every run | Daily/weekly |

---

## 🚀 Next: Deploy External Site

Once you're happy with the internal training:
1. Deploy external site to Vercel (free tier)
2. Share link with your audience
3. They see the top 15 each day
4. Maybe they click feedback buttons too

For now: Keep both local, keep training! 🎓

---

## ❓ FAQ

**Q: Why two sites?**
A: Separate training (messy, all data) from customer experience (clean, curated).

**Q: Can customers train the system too?**
A: Later! First, perfect it yourself. Then add customer feedback.

**Q: How long until the system learns?**
A: After 20-30 ratings per category, you'll see patterns. After 100+ ratings, clear signal.

**Q: Can I run both sites at once?**
A: Yes! Just need 3 terminals (API, Internal, External already running).

**Q: How do I know the training is working?**
A: Compare your feedback vs Claude's scores. If you 👎 articles Claude ranked high, system will adjust.

---

Ready? Start with:

```bash
python3 src/feedback_server.py
python3 -m http.server 3000
```

Then rate some articles! 🎓
