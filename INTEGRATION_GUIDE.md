# Integration Guide: New Sources + Feedback Infrastructure

## Current Status

### ✓ Phase 1: Complete
- Core pipeline (fetch → filter → generate → deliver)
- SQLite database with deduplication
- Email delivery via Gmail
- launchd scheduling

### ✓ Phase 2A: Complete
- Astro website with digest archive
- Story cards with feedback buttons
- Database schema for feedback + source reviews
- Source manager infrastructure

### 🔄 Phase 2B: In Progress
- **Research agents** finding 30+ new sources across 3 categories
- **Source scorecard** template ready
- **Integration pipeline** being built

### ⏳ Phase 2: Next
- Wire email feedback links
- Wire web feedback API
- Integrate new sources into pipeline
- Test end-to-end

---

## How Research Results Will Be Integrated

### Step 1: Receive Research Agent Results

Three agents are researching in parallel:
1. **Builder sources** (engineers shipping agents)
2. **Entrepreneur sources** (SMB AI leverage)
3. **Agentic sources** (agent-obsessed communities)

Each returns a list like:

```
1. **Simon Willison's Blog**
   - URL: https://simonwillison.net/atom/everything/
   - Update frequency: Daily
   - Signal strength: 9/10
   - Why: Deep dives into LLMs, hands-on experiments
   - Example: "Building multi-agent systems with Claude"
```

### Step 2: Add to Source Review Queue

Use the source manager to add candidates:

```python
from src.source_manager import SourceManager

manager = SourceManager()
manager.add_source_candidate(
    name="Simon Willison's Blog",
    url="https://simonwillison.net/atom/everything/",
    category="builder",
    signal_strength=9,
    update_frequency="daily",
    comment="Deep dives into LLMs, hands-on experiments"
)
```

Or bulk import from research results:

```bash
python scripts/import_sources.py research_results.json
```

### Step 3: Manual Review

Review candidates in the web UI or CLI:

```bash
python src/source_manager.py
```

Output shows:
```
  Source Review Queue (42 sources)

  1. Simon Willison's Blog
     URL: https://simonwillison.net/atom/everything/
     Category: builder | Signal: 9/10
     Updates: daily
     Why: Deep dives into LLMs and tools

  2. The Neuron (AI newsletter)
     ...
```

Approve via CLI (coming):
```bash
python scripts/approve_source.py "Simon Willison's Blog"
```

Or via web UI (when ready).

### Step 4: Activate New Sources

Once approved, sources are added to the active feed list:

```python
from src.source_manager import SourceManager
manager = SourceManager()
approved = manager.get_approved_sources()
# Now 30+ sources instead of 20
```

Update `src/core/fetcher.py` to include approved sources dynamically:

```python
def fetch_articles(lookback_hours=24):
    # Start with hardcoded FEEDS
    feeds = dict(FEEDS)

    # Add approved sources from DB
    manager = SourceManager()
    for source in manager.get_approved_sources():
        feeds[source['source_name']] = {
            "url": source['url'],
            "tier": category_to_tier(source['category']),
            "focus": source['relevance_comment']
        }

    # Fetch from combined list
    ...
```

### Step 5: Feedback Loop Training

User feedback trains the system to tune:
- Which sources matter most
- What content resonates
- Whether to keep/drop sources

Pattern detection: "This story appeared in 5 approved sources" → high signal

---

## Email Feedback Integration

### Current Setup

Email sent via `src/outputs/email_output.py` with:
- HTML + plain text MIME
- Clean template with story cards
- **NOT YET** feedback buttons (next step)

### How to Wire It

#### 1. Modify Email Template

Update `src/outputs/email_output.py` to include feedback buttons:

```python
from src.email_feedback import EmailFeedbackTemplate

html_for_story = f"""
<div>
  <h3>{story['title']}</h3>
  <p>{story['why_it_matters']}</p>
  <a href="{story['link']}">Read more</a>

  {EmailFeedbackTemplate.reaction_html(story['article_id'])}
</div>
"""
```

#### 2. Add API Endpoint

Create `src/api/feedback.py` to handle email clicks:

```python
# Pseudo-code for FastAPI/Flask endpoint
@app.get("/api/feedback")
def feedback(article_id: str, reaction: str):
    db = DigestDatabase()
    db.add_feedback(article_id, reaction=reaction)
    db.close()

    # Return 1x1 pixel (email tracking)
    return redirect("https://tracking-pixel.com/1x1.gif")
```

#### 3. Host API

Options:
- **Vercel Functions** (free, serverless)
- **Heroku/Railway** (free tier)
- **AWS Lambda** (free tier)
- **Your own server**

#### 4. Update Base URL

Change `base_url` in feedback links to match your domain:

```python
feedback_link = generate_feedback_link(
    article_id,
    "thumbs_up",
    base_url="https://agentic-digest-api.vercel.app"
)
```

---

## Web UI Feedback (Already Built)

Story cards in `/archive` pages already have:
- 👍 Relevant button
- 👎 Not for me button
- 💭 Comment field

JavaScript sends POST to `/api/feedback`:

```javascript
const response = await fetch('/api/feedback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    articleId: 'abc123',
    reaction: 'thumbs_up',
    comment: 'Very relevant to my work'
  })
});
```

This is **already wired**, just needs backend API.

---

## Sentiment Aggregation

Once feedback flows in, query patterns:

```python
db = DigestDatabase()

# Overall stats
stats = db.get_feedback_summary()
# { thumbs_up: 42, thumbs_down: 5, comments: 12 }

# Feedback for one article
feedback = db.get_article_feedback(article_id)
# [
#   { reaction: 'thumbs_up', comment: 'Very relevant' },
#   { reaction: 'thumbs_down', comment: 'Not for my use case' }
# ]

# Source performance (from feedback patterns)
# If stories from "Simon Willison's Blog" get 8/10 thumbs up
# But stories from "Generic AI News" get 2/10
# → Adjust tier or drop weak sources
```

---

## Timeline

### Now (Today)
- ✓ Research agents running
- ✓ Website + feedback UI built
- ✓ Source manager ready

### Next 2-4 hours
- Receive research results
- Import 30+ new sources
- Manual review (you approve/reject)
- Update `src/core/fetcher.py` to use approved sources

### Next 24 hours
- Wire email feedback links
- Deploy API endpoint (Vercel)
- Test email → click → DB flow
- Run digest with new sources

### Week 2
- Aggregate feedback patterns
- Update Claude prompts based on what you like
- Gradually remove human-in-loop for source approval
- Measure which sources drive engagement

---

## Checklist for Integration

### Research Results
- [ ] Receive research agent outputs
- [ ] Extract source list from each agent
- [ ] Validate URLs are real RSS feeds

### Source Management
- [ ] Import sources into database
- [ ] Review & approve candidates
- [ ] Update `src/core/fetcher.py` dynamically

### Email Feedback
- [ ] Add feedback buttons to email template
- [ ] Deploy API endpoint
- [ ] Update base URLs in feedback links
- [ ] Test email click → tracking

### Web Feedback
- [ ] Test story card buttons (already wired)
- [ ] Verify feedback stores in DB
- [ ] Check feedback shows on article detail page

### Integration Testing
- [ ] Run pipeline with new sources
- [ ] Verify deduplication still works
- [ ] Send email with feedback buttons
- [ ] Click email button → verify DB entry
- [ ] Click web button → verify DB entry
- [ ] Test comment collection

### Sentiment Tuning
- [ ] Query feedback stats
- [ ] Identify high/low signal sources
- [ ] Adjust source weights or tiers
- [ ] Rerun digest, compare quality

---

## File Structure Added

```
src/
├── source_manager.py           # NEW: Manage source curation
├── email_feedback.py           # NEW: Email feedback link generation
├── api/                        # NEW (next): API endpoints
│   └── feedback.py
└── scripts/
    ├── import_sources.py       # NEW: Bulk import from research
    └── approve_source.py       # NEW: Approve/reject candidates
```

---

## Questions & Decisions

**Q: How often should I manually review sources?**
A: Probably weekly. As you get feedback data, patterns will emerge and you can auto-approve high-signal sources.

**Q: Should I test with just web feedback first?**
A: Yes. Test the full flow locally: click button → feedback stores → appears in stats. Then wire email when confident.

**Q: How do I measure if a source is good?**
A: Click-through rate + feedback ratio. If stories from "Source X" get 7/10 thumbs up vs 2/10 for "Source Y", source Y is weak.

**Q: What if a source publishes spam?**
A: Remove from approved list. Your feedback data will show it quickly (low thumbs up ratio).

---

**Next: Wait for research agent results, then execute integration steps above.**
