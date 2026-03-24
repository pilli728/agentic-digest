# Agentic Edge Website

Astro-based website for the Agentic Edge Daily Digest. Shows digest archive, individual digests, and feedback UI.

## Quick Start

```bash
npm install
npm run dev
```

Then visit `http://localhost:3000`

## Structure

- **pages/**: Website pages (home, archive, individual digests)
- **layouts/**: Shared layouts
- **components/**: Reusable components (StoryCard, FeedbackWidget, etc.)
- **content/digests/**: Generated digest markdown files
- **src/content/config.ts**: Content collection configuration

## How It Works

### Digest Generation

The Python pipeline in the parent directory (`src/orchestrator.py`) automatically writes digest files to `src/content/digests/YYYY-MM-DD-digest.md`.

Each digest file has YAML frontmatter:
```yaml
---
title: "Agentic Edge Digest - 2026-03-22"
date: 2026-03-22
layout: ../../layouts/DigestLayout.astro
---
```

Followed by markdown content (story cards).

### Content Collection

Astro's content collection (`src/content/config.ts`) automatically discovers these markdown files and makes them available to pages via `getCollection('digests')`.

### Story Cards

Each story in the digest is rendered as a `StoryCard` component with:
- 👍 **Relevant** button
- 👎 **Not for me** button
- 💭 **Tell me more** with comment field

### Feedback Flow

1. User clicks reaction button
2. JavaScript sends POST to `/api/feedback`
3. Server stores in `feedback` table
4. (Optional) Homepage shows feedback stats

## Deployment

### Local Testing

```bash
npm run dev
```

### Vercel Deployment

```bash
npm run build
vercel deploy
```

The site is static, so any hosting works (Netlify, GitHub Pages, etc.)

## Environment

No environment variables needed for the website. It reads from the Python pipeline's digest files and database.

## API Endpoints (Phase 2)

- `POST /api/feedback` - Store user feedback
  - Body: `{ articleId, reaction: "thumbs_up"|"thumbs_down", comment?: string }`

These are currently stubbed. Implement when wiring feedback infrastructure.

## Styling

- Uses Tailwind CSS for responsive design
- Dark mode support via CSS variables
- Serif headings (Merriweather), sans body (Inter)
- 4-tier color scheme for story sources

## Notes

- Digests are auto-written by the Python pipeline
- This site is **read-only** for viewing and feedback
- Content lives in the parent project's database
