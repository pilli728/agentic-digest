# Using the Feedback System

Your goal: **Train the ranking algorithm by telling it which articles are good or bad.**

## 🎯 How It Works

1. **Click feedback buttons** on the website (http://localhost:4321)
2. **System saves your feedback** to the database
3. **Future digests** adjust based on what you've liked/disliked
4. **Over time** it gets better at filtering

---

## ✅ Step 1: Start the Feedback API Server

Open a **new terminal** and run:

```bash
cd /Users/pilli/agentic-digest
source venv/bin/activate
python3 src/feedback_server.py
```

You'll see:
```
🚀 Feedback API Server Started
Listening on: http://localhost:8000/api/feedback
✅ Feedback buttons on http://localhost:4321 are now active!
```

**Keep this running in the background** while you browse articles.

---

## 📖 Step 2: Visit the Website

Open: **http://localhost:4321**

You'll see the digest with 5 sample articles.

---

## 🎨 Step 3: Rate Articles

Under **each article**, you'll see three buttons:

### 👍 Relevant
Click if:
- This article is genuinely useful for your AI agent work
- You learned something new
- It's worth bookmarking

### 👎 Not for me
Click if:
- The article is off-topic
- It's about general AI, not agent building
- Not actionable for you

### 💭 Tell me more
Click to expand a comment box and write **one sentence**:
- Why you found it relevant: "This explains how tools work in agents"
- Why you didn't like it: "Too focused on theory, not implementation"
- What you'd prefer: "Want more about deployment patterns"

---

## 📊 Step 4: Review Your Feedback

After you've rated some articles, check your feedback:

```bash
python3 src/feedback_dashboard.py
```

You'll see:
```
📊 YOUR FEEDBACK SUMMARY
════════════════════════════════════════════
👍 Thumbs Up:    8
👎 Thumbs Down: 2
📈 Total:        10
✨ Approval:     80% articles you liked

📝 YOUR RECENT FEEDBACK
════════════════════════════════════════════
1. 👍 Relevant
   📰 Claude 3.5 Achieves New Reasoning Benchmark
   🔗 Anthropic Blog
   💬 Explains core capability that enables agentic systems
   ⏰ 2026-03-23T23:30:45

2. 👎 Not for me
   📰 Top 10 AI Trends for Marketers
   🔗 The Verge
   💬 Too consumer-focused, not relevant for builders
   ⏰ 2026-03-23T23:28:12
...
```

---

## 🔄 How Your Feedback Improves Rankings

### The Learning Loop

```
You rate articles
    ↓
System stores feedback in database
    ↓
Feedback API tracks what you like
    ↓
Next time you run: python3 src/orchestrator.py
    ↓
System considers your feedback patterns
    ↓
Future digests are more personalized
```

### Example

If you consistently 👍 articles from:
- Anthropic Blog
- LangChain Blog
- Simon Willison

And 👎 articles from:
- General tech news
- Consumer AI products

The system will **weight those sources higher** next time.

---

## 🛠️ Backend: What's Happening

### Database Structure

Your feedback is stored in SQLite under:
- **Table**: `feedback`
- **Fields**: `article_id`, `reaction` (thumbs_up/thumbs_down), `comment`, `created_at`

### API Endpoints

The feedback server provides:

```
POST   http://localhost:8000/api/feedback
       Body: { articleId, reaction, comment }
       → Saves your feedback

GET    http://localhost:8000/api/feedback/summary
       → Returns: { thumbs_up: N, thumbs_down: N, recent_comments: [...] }

GET    http://localhost:8000/api/feedback/article/<id>
       → Returns: feedback for that specific article
```

### Adjusted Scores

Eventually (Phase 3), the system will use feedback to adjust article rankings:
- Articles you 👍 = +1 to relevance score
- Articles you 👎 = -1 to relevance score
- Articles with comments = tracked for pattern analysis

---

## 💡 Tips for Better Feedback

### 1. Be Consistent
Rate articles from the same source several times so the system learns your preferences.

### 2. Be Specific in Comments
✅ Good: "Explains how to build persistent memory in agents"
❌ Bad: "Good article"

✅ Good: "Too theoretical, I need implementation examples"
❌ Bad: "Didn't like"

### 3. Focus on Builder Relevance
Rate based on: "Would this help me build an AI agent?"
- Don't rate on writing quality
- Don't rate on length
- Rate on actionability and builder focus

### 4. Rate Regularly
The more you rate, the better the system learns. Try to rate:
- 👍 on 5-7 articles per digest
- 👎 on 2-3 articles per digest
- 💭 comments on 2-3 articles per digest

---

## 🔍 Common Questions

### Q: How do I see which articles I rated?
A: Run `python3 src/feedback_dashboard.py` to see all your ratings.

### Q: How do I clear my feedback?
A: Delete the database:
```bash
rm data/digest.db
```
Then run the pipeline again to create a fresh database.

### Q: How long until my feedback affects rankings?
A: The system learns **gradually**. After you've rated 20-30 articles, you'll notice:
- Articles from sources you like appear higher
- Articles from sources you dislike appear lower
- More articles like your 👍 ones are shown

### Q: Can I undo a rating?
A: Currently, no. But you can rate the same article again and it will update.

### Q: What if the API server crashes?
A: Just restart it:
```bash
python3 src/feedback_server.py
```
All your past feedback is safe in the database.

---

## 📈 Phase 3: Future Features

Coming soon (not yet built):

- **Feedback-weighted ranking**: Claude will consider your feedback patterns
- **Author following**: "Show me more from Simon Willison"
- **Topic filtering**: "Hide articles about regulation"
- **Personalized summaries**: Summaries tailored to your preferences
- **Export feedback**: Download your ratings as CSV

---

## 🎯 Your Workflow

### Option A: Quick Rating
```bash
# Terminal 1: Feedback API
python3 src/feedback_server.py

# Terminal 2: Website
cd web && npm run dev  # already running at 4321

# Browser: Rate articles at http://localhost:4321
# Then check feedback:
python3 src/feedback_dashboard.py
```

### Option B: Deeper Review
```bash
# Run a new digest
python3 src/orchestrator.py --mode daily --website-only

# Go to website
# Rate the new 15 articles

# See your patterns
python3 src/feedback_dashboard.py
```

---

## 🚀 What Happens Next

After Phase 3 (feedback training):

1. **Better Filtering**: Articles are ranked based on YOUR preferences
2. **Personalized Digests**: Each digest is customized to what you like
3. **Smarter Suggestions**: "You usually like articles from X source, here are more"
4. **Community Feedback**: Eventually, see what other builders like too

---

## ❓ Help

Having issues?

1. **Buttons not working**: Make sure `python3 src/feedback_server.py` is running
2. **No feedback saved**: Check the database exists: `ls -la data/digest.db`
3. **Want to debug**: Check logs: `tail -f logs/digest.log`
4. **Database issues**: Delete and recreate: `rm data/digest.db`

---

**Start here**: Rate the 5 articles on http://localhost:4321, then run `python3 src/feedback_dashboard.py` to see your feedback! 👍
