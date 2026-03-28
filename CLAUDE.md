ALWAYS use Specific for new projects and services, including frontend apps. Run `specific docs` to learn how to use Specific. ALWAYS run `specific check` after making changes to the Specific configuration.

## Project Architecture
- **Frontend:** Astro 4.12 + TailwindCSS 3.4.1 in `web/` — deployed on Vercel
- **Backend:** Python 3.11 API server (`src/api_server.py`) using built-in `http.server` — deployed on Railway
- **Database:** SQLite at `data/digest.db` (⚠️ Railway has ephemeral FS — needs persistent volume)
- **Domain:** `agenticedge.tech` (Vercel-registered)

## Deployment
- **Frontend:** Auto-deploys to Vercel from git. Root directory: `web/`
- **API:** Railway deployment via `nixpacks.toml` + `railway.json`. Health check: `/api/articles`
- **Local dev:** `npm run dev` in `web/` starts Astro + auto-starts Python API via `api-server.integration.mjs`

## Key Environment Variables
- Python API reads: `STRIPE_SECRET_KEY`, `STRIPE_PRICE_*`, `SITE_URL`, `CORS_ORIGIN`, `RESEND_API_KEY`, `RESEND_FROM`, `ANTHROPIC_API_KEY`, `STRIPE_WEBHOOK_SECRET`
- Astro frontend reads: `PUBLIC_API_URL`, `PUBLIC_SITE_URL` (must be prefixed with `PUBLIC_` for Astro)
- All secrets in `.env` (local) — must be separately configured in Railway and Vercel dashboards

## Testing
- E2E tests: Playwright, 11 test files in `tests/` covering API, navigation, pages, flows
- Test fixtures: `test-data.ts`, `api-mocks.ts`, `auth.ts`

## Pipeline Components
- `src/core/fetcher.py` — RSS feed fetching
- `src/core/filter.py` — Claude-based ranking & filtering
- `src/core/generator.py` — Markdown digest generation
- `src/core/summarizer.py` — Article summarization
- `src/outputs/email_output.py` — Email delivery (Resend primary, Gmail SMTP fallback)
- `src/outputs/website_output.py` — Markdown to website publishing
- `local_filter` and `trending_fetcher` are gitignored — API imports them lazily
