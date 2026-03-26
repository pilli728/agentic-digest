# Launch Checklist

## MUST-FIX Before Go-Live

1. [x] Replace all hardcoded localhost URLs with env-driven config
2. [x] Fix Stripe price key mismatch (inner_monthly vs founding_monthly)
3. [x] Add Stripe webhook signature verification
4. [x] Gate premium content behind auth (client-side check)
5. [ ] Deploy API behind HTTPS (Caddy/nginx or managed service)
6. [x] Persist sessions to SQLite (survive server restarts)
7. [x] Add physical mailing address to email footer
8. [x] Add List-Unsubscribe header to emails
9. [x] Create /privacy and /terms pages
10. [x] Fix unsubscribe link with email pre-fill

## SHOULD-FIX First Week
11. [x] Restrict CORS to actual domain
12. [ ] Add rate limiting on subscribe/login/fetch
13. [x] Add email validation on subscribe
14. [ ] Add OG/Twitter meta tags + sitemap
15. [x] Show error on failed signup (not fake success)
16. [x] Fix resubscribe after unsubscribe
17. [x] Fix Stripe checkout to pass customer_email
18. [x] Map Stripe price to correct tier (pro vs inner)
19. [x] Remove dev_token from production

## Configure Before Launch
- [ ] Get Resend API key (resend.com)
- [ ] Get Stripe keys + create products (dashboard.stripe.com)
- [ ] Set up custom domain
- [ ] Deploy Astro site to Vercel
- [ ] Deploy API server (Railway/Render/VPS)
