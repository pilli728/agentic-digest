# Two-Website Architecture

## 🏗️ The Setup

```
Your Ranking System
├── Internal Dashboard (http://localhost:3001) ← JUST FOR YOU
│   ├── ALL articles (filtered + unfiltered)
│   ├── Training interface (rate articles)
│   ├── Feedback patterns
│   ├── System statistics
│   └── Debugging tools
│
├── Feedback Server (http://localhost:8000)
│   └── Stores ratings in SQLite
│
└── External Website (http://localhost:4321) ← FOR CUSTOMERS
    ├── Top 15 curated articles only
    ├── Professional design
    ├── Article links & summaries
    ├── Maybe feedback from readers
    └── Maybe analytics
```

## 📊 Data Flow

```
RSS Feeds (50+)
    ↓
Fetcher
    ↓
Claude Filter & Rank
    ↓
SQLite (all articles + your ratings)
    ├─→ Internal Dashboard (show ALL articles)
    │   └─→ You rate them 👍👎💭
    │   └─→ Ratings go back to SQLite
    │
    └─→ External Website (show TOP 15 only)
        └─→ What customers see
        └─→ Maybe customer feedback too
```

## 🎯 Internal Dashboard

**Purpose**: Train the system, see what's working

**Features**:
- ✅ Show 50+ articles fetched today
- ✅ Sort by: relevance score, source, tier
- ✅ Rate articles 👍👎💭
- ✅ See YOUR feedback patterns (what you like)
- ✅ See Claude's scores vs your scores
- ✅ Debug: why did Claude rank this high/low?
- ✅ Statistics: which sources you trust most
- ✅ Bulk actions: "Mark all from TechCrunch as low-quality"

**Who sees it**: Just you (localhost only, no auth needed yet)

**Design**: Functional, data-heavy, lots of tables and stats

## 🌐 External Website

**Purpose**: Share the best articles with your audience

**Features**:
- ✅ Only show top 15 articles (you already curated)
- ✅ Beautiful card design
- ✅ Article summaries (the 3-sentence ones)
- ✅ Relevance scores + tier badges
- ✅ Links to full articles
- ✅ Maybe: reader feedback (optional)
- ✅ Maybe: subscribe to email digest
- ✅ Archive page (browse past digests)

**Who sees it**: Everyone (public website, deployed)

**Design**: Clean, professional, reader-friendly

## 🚀 Implementation Plan

### Option A: Use Current Astro Website + Create Internal Dashboard

**Current setup:**
```
/web → Astro website (EXTERNAL - customer facing)
/internal → New React/Vue dashboard (INTERNAL - just for you)
```

**Steps:**
1. Keep `/web` as external customer site
2. Create `/internal` with a new tech stack (React/Vue/Svelte)
3. Internal dashboard talks to feedback API
4. Share the same SQLite database

### Option B: Separate Everything

**Setup:**
```
/web-external → Astro (what customers see)
/web-internal → React (just for you)
```

**Same data:**
- Both read from `data/digest.db`
- Both use `src/feedback_server.py`
- Both show same articles, but different layouts

## 📋 Comparison

| Aspect | Internal Dashboard | External Website |
|--------|-------------------|------------------|
| **URL** | localhost:3001 | localhost:4321 |
| **Audience** | Just you | Everyone |
| **Articles shown** | All 50+ fetched | Top 15 curated |
| **Purpose** | Train the system | Share the digest |
| **Design** | Data-heavy, functional | Clean, professional |
| **Feedback** | You rate to train | Customers maybe rate |
| **Complexity** | Medium (lots of filters) | High (polished design) |
| **Data shown** | Raw scores, Claude's reasoning | Clean summaries |
| **Buttons** | Rate, debug, bulk actions | Read, share, maybe feedback |

## 🎨 What Goes Where

### Internal Dashboard Shows
```
Article #1
┌─────────────────────────────────┐
│ Source: Anthropic Blog          │
│ Tier: 1 (Builder Signal)        │
│ Published: 2026-03-23           │
│ Claude Score: 9/10              │
│ Your Rating: 👍                 │
│ Summary: [3 sentences]          │
│ Your Comment: "Great, exactly..." │
│                                 │
│ [👍] [👎] [💭] [Debug] [Hide]  │
└─────────────────────────────────┘
```

### External Website Shows
```
Article #1
┌─────────────────────────────────┐
│ Claude 3.5 Achieves New...      │
│ Anthropic Blog                  │
│ Signal Strength: 9/10           │
│                                 │
│ Why it matters: [3 sentences]   │
│                                 │
│ [Read →] [Share] [Save]        │
└─────────────────────────────────┘
```

## 🔄 Training Loop

```
1. Run: python3 src/orchestrator.py --mode daily
   └─→ Creates digest with 50 articles

2. Open Internal Dashboard (localhost:3001)
   └─→ See all 50 articles
   └─→ Claude has ranked them 1-50

3. You rate articles 👍👎💭
   └─→ Feedback API saves your ratings
   └─→ Now SQLite has: Claude scores + Your scores

4. Open External Website (localhost:4321)
   └─→ Shows top 15 (what customers see)
   └─→ You can see if you agree with Claude's top 15

5. Next run: python3 src/orchestrator.py
   └─→ System considers your previous feedback
   └─→ Adjusts rankings (Phase 3)
   └─→ Repeat

6. Over time:
   └─→ You've trained Claude on YOUR preferences
   └─→ External site improves
   └─→ Customers see better digests
```

## 💰 Why Two Sites?

**You're essentially building a feedback loop:**

1. **Internal**: You curate + train the AI
2. **External**: Customers enjoy the results

**Benefits:**
- ✅ Messy training data stays private
- ✅ Customers see polished output
- ✅ You can experiment internally without affecting the feed
- ✅ Clear separation of concerns
- ✅ Can scale to multiple users later

**Analogy:**
- Netflix's internal: "Rate movies to train recommendations" ← employees only
- Netflix's external: "Watch movies, see recommendations" ← public
- Both feed the same algorithm

## 🛠️ Technical Details

### Database (Shared)
```
SQLite (data/digest.db)
├── articles (all fetched)
├── digests (each day's digest)
├── feedback (your ratings)
└── digest_articles (which articles in which digests)
```

### APIs (Shared)
```
Feedback Server (port 8000)
├── POST /api/feedback (save rating)
├── GET /api/feedback/summary (stats)
└── GET /api/feedback/article/<id> (article's feedback)
```

### Websites (Separate)
```
Internal Dashboard (port 3001)
└── React/Vue app
    └── Shows all articles
    └── Calls feedback API
    └── Shows Claude scores vs your scores

External Website (port 4321)
└── Astro app
    └── Shows top 15
    └── Beautiful design
    └── Maybe calls feedback API for reader ratings
```

## 📱 Real-World Example

**Day 1:**
- You run the digest pipeline
- Internal dashboard shows 50 articles, Claude ranked them
- You think: "Hmm, Claude put #8 (a TechCrunch article) above #3 (Anthropic blog)"
- You rate them: TechCrunch = 👎, Anthropic = 👍
- Feedback saved

**Day 2:**
- You run the pipeline again
- Claude now considers: "This user really likes Anthropic, downranks general tech news"
- Internal dashboard shows better ranking
- External website shows better top 15
- Customers are happier!

---

## 🎯 Which Option?

I recommend: **Keep Astro external, create React internal dashboard**

Why:
- Astro is optimized for static content (clean, fast)
- React is better for interactive dashboards (filters, real-time feedback)
- Both can run on localhost simultaneously
- Clear tech separation

---

## Next Steps

Choose:
1. **Start with internal dashboard** (let me build it for you)
2. **Keep current Astro site as is** (no changes needed)
3. **Connect them via shared SQLite + feedback API** (already done)

Then you'll have:
- ✅ Internal training site (full control, all articles, debugging)
- ✅ External customer site (polished, curated, professional)
- ✅ Shared feedback system (trains the AI)

Sound good?
