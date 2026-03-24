# Revised Plan: Agentic Digest Evolution

## Overview

Instead of sequential phases, we're building **in parallel**:

### Phase 2A: Website + Feedback Infrastructure
- Astro website with digest archive & story cards
- **Feedback UI**: Email reaction buttons + 1-sentence explanation
- Database tracking: store all feedback & sentiment
- Manual source review queue
- Ready by end of this session

### Phase 2B: Source Curation Research + Manual Review System
- Research 5-10 new sources each across:
  - **Builders**: What engineers/founders are shipping (GitHub, IndieHackers, Product Hunt)
  - **Entrepreneurs**: SMB AI leverage, concrete case studies
  - **Agentic Specialists**: Reddit r/agents, specialized newsletters, Slack communities
- Create **source scorecard**: signal strength, audience fit, update frequency
- Build manual review UI: "approve this source?"
- Deploy in next 2-3 days

### Phase 3: Feedback Loop Learning (week 2)
- Aggregate user feedback (👍/👎 + comments)
- Detect cross-source patterns: "This story appeared in 5 feeds"
- Auto-surface high-signal content
- Update Claude prompts based on your preferences
- Remove human-in-loop gradually as patterns emerge

---

## Phase 2A Details: Website + Feedback

### Website Structure (Astro)

```
web/
├── src/
│   ├── content/
│   │   ├── config.ts              # Content collection config
│   │   └── digests/               # .md files (auto-written by pipeline)
│   │
│   ├── pages/
│   │   ├── index.astro            # Homepage: latest digest
│   │   ├── archive.astro          # Date-indexed list
│   │   └── [slug].astro           # Individual digest page
│   │
│   ├── components/
│   │   ├── StoryCard.astro        # Story card with feedback
│   │   ├── FeedbackWidget.astro   # 👍/👎 + comment form
│   │   ├── TierBadge.astro        # Colored tier indicator
│   │   ├── Header.astro
│   │   └── Footer.astro
│   │
│   ├── layouts/
│   │   ├── BaseLayout.astro
│   │   └── DigestLayout.astro
│   │
│   └── styles/
│       └── global.css             # Tailwind setup
```

### Feedback Flow

**In Email:**
```
👍 Relevant  |  👎 Not for me  |  💭 Tell me more
```

When clicked (via email tracking link):
```
GET /feedback?article_id=xyz&reaction=thumbs_up&comment=...
```

**In Web UI:**
```
Story card with inline:
  [👍] [👎] [Comment]
  ↓
  Sentiment stored in DB
  Associated with article_id + your response
```

### Database Schema (additions)

```sql
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT NOT NULL,
    reaction TEXT,              -- 'thumbs_up', 'thumbs_down'
    comment TEXT,               -- 1-sentence explanation
    created_at TEXT,
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

CREATE TABLE IF NOT EXISTS source_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT UNIQUE,
    url TEXT,
    category TEXT,              -- 'builder', 'entrepreneur', 'agentic'
    signal_strength REAL,       -- 1-10 manual rating
    update_frequency TEXT,      -- 'daily', 'weekly', 'sporadic'
    relevance_comment TEXT,
    approved INTEGER DEFAULT 0,
    added_date TEXT
);
```

---

## Phase 2B Details: Source Research + Manual Curation

### Research Tracks

#### Track 1: Builders (What people are shipping)
- **Reddit**: r/agents, r/OpenAI, r/LanguageModels, r/LocalLLaMA
- **GitHub Trends**: ML/AI projects, agent frameworks trending
- **IndieHackers**: "Built with AI" launches
- **Product Hunt**: AI tools & agent startups
- **Dev blogs**: Vercel, Supabase, Pinecone, LangChain updates
- **HackerNews**: Filtered for "shipping" + "agent" mentions

#### Track 2: Entrepreneurs (SMB AI use cases)
- **LinkedIn**: #BuildWithAI posts, case studies
- **Twitter/X**: Founder threads on AI implementation
- **Business newsletters**: Packy McCormick, Nabyl Zahy, CL, Lenny's
- **Substack**: AI for business/startups focused
- **YouTube**: Founder interviews (e.g., Fireside Chats on AI)

#### Track 3: Agentic Specialists (Deep signal)
- **Slack communities**: OpenAI forum, LangChain Discord, Agent-building groups
- **Specialized newsletters**: Already have some, need to find niche ones
- **Research papers**: ArXiv + summaries (papers about agents)
- **Conferences**: Upcoming AI/agent events and announcements

### Manual Review Process

Create a **source scorecard template**:

```
Source: [Name]
URL: [URL]
Category: builder | entrepreneur | agentic
Update Frequency: daily / weekly / sporadic
Average Signal Strength: 1-10 (how often useful for your goals?)
Example Articles: [1-2 recent relevant posts]
Why Add It: [1-2 sentences]
Approved: [ ] YES  [ ] NO
```

Store in DB or CSV, review weekly.

---

## Implementation Timeline

### Week 1 (this session)
- **2A**: Website scaffold + story cards + feedback widget
- **2B**: Initial source research (10-15 candidates)
- **Together**: Wire feedback email links
- **Deliverable**: Working website, 30+ new source candidates identified

### Week 2
- **2A**: Refine feedback UI, sentiment aggregation
- **2B**: Expand source list (50+ candidates), start approving
- **Together**: Auto-display approved sources in digest pipeline
- **Deliverable**: Closed feedback loop, expanded source pool

### Week 3+
- **Phase 3**: Pattern detection, Claude prompt tuning, human-in-loop removal
- **Deliverable**: Smart digest that learns your preferences

---

## Success Metrics (Phase 2)

✓ Website shows latest digest + archive
✓ Email has reaction buttons + comment field
✓ Feedback stores in DB and shows in web UI
✓ 50+ new sources identified and rated
✓ Manual review process documented
✓ Trending patterns visible (cross-source duplicates highlighted)

---

## Quick Start

1. Build website (1-2 hours)
2. Wire feedback infrastructure (30 min)
3. Research new sources in parallel (ongoing)
4. Launch with expanded sources next week

Let's go.
