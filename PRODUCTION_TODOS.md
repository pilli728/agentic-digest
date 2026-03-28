# Production Launch TODO Tracker

## CRITICAL
- [x] #2 — Add auth to admin endpoints (publish, iterate, pipeline, topics)
- [ ] #3 — Move premium content to API-based delivery (not in HTML source)
- [x] #4 — Fix double response bug in /api/digest/send-latest
- [x] #5 — Add rate limiting to email-sending endpoints
- [x] #6 — Fix sitemap URL in robots.txt

## HIGH
- [x] #7 — Add og:image meta tag to all pages
- [x] #8 — Add annual pricing checkout button
- [x] #9 — Webhook: update auth_sessions on checkout.session.completed
- [x] #10 — Change cancellation to end-of-period instead of immediate
- [x] #11 — Add email validation on /api/auth/login
- [x] #12 — Fix /api/unsubscribe 502 on empty body
- [x] #13 — Replace Stripe dev error message with user-friendly text
- [x] #14 — Fix duplicate homepage title
- [x] #15 — Add bounce handling (Resend webhook) — deferred; TODO comment added in email_output.py

## MEDIUM
- [x] #16 — Handle invoice.payment_failed and customer.subscription.updated webhooks
- [x] #17 — Pass magic link to welcome email
- [x] #18 — Add List-Unsubscribe header to welcome and magic link emails
- [x] #19 — Add plain text fallback to welcome and magic link emails
- [x] #20 — Add unsubscribe link + physical address to magic link email
- [x] #21 — Add /favicon.ico file
- [x] #22 — Add og:url meta tag
- [x] #23 — Login page: add try/catch on fetch
- [x] #24 — Add database indexes
- [x] #25 — Remove PII from stdout logs
- [x] #26 — Move download templates out of public directory

## LOW
- [x] #27 — Add expired session cleanup
- [ ] #28 — No database migration framework (defer)
- [x] #29 — Verify page: check if already logged in
- [x] #30 — Remove localhost string from production HTML
- [x] #31 — Add initial-scale=1.0 to viewport
- [x] #32 — Unsubscribe page: handle API failure properly

## SKIPPED (manual)
- [ ] #1 — Switch Stripe to live keys (do after all fixes)
