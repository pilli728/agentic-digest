---
title: "Newsletter Monetization: Custom Stripe Integration vs Platforms"
description: "Why we went custom instead of Buttondown or Substack, the exact pricing tiers, and how to set up Stripe Checkout in 30 minutes."
date: "2026-03-24"
tier: "pro"
category: "playbook"
---

# Newsletter Monetization: The Custom Approach

We chose custom over Substack and Buttondown. Here's why and how.

## The Decision Matrix

| | Custom (Ours) | Substack | Buttondown |
|---|---|---|---|
| **Revenue cut** | 0% (Stripe 2.9%) | 10% | 0% ($9/mo fee) |
| **Subscriber data** | You own it | They own it | You own it |
| **Domain** | Your brand | yourname.substack.com | Custom domain |
| **Design control** | 100% | Template only | Template only |
| **Discovery** | You drive traffic | Substack network | You drive traffic |
| **Email delivery** | You manage | They handle | They handle |
| **Migration risk** | None (it's yours) | High | Medium |

## Our Pricing Tiers

### Free ($0)
- Top 5 stories weekly
- Headlines + sources
- Email delivery

### Pro ($9/mo or $89/year)
- All 20 stories weekly
- Full "why it matters" analysis
- Source links + engagement data
- Early access (Friday PM vs Monday)
- Reply to any issue

### Founding Member ($29/mo)
- Everything in Pro
- Monthly 1:1 call (15 min)
- Private Slack channel
- Shape what the newsletter covers
- Name in credits forever
- Price locked — goes up later

## Why These Numbers

- **$9/mo** is the sweet spot for newsletter subscriptions. Low enough to be impulsive, high enough to filter for serious readers.
- **$89/year** saves 18% — most subscribers switch to annual within 3 months.
- **$29/mo founding** is a commitment that buys you your most engaged readers. These people become your community.
- **50 founding spots** creates urgency. First 50 people who believe in you.

## The Technical Setup

### What You Need
1. Stripe account (free, 2.9% per transaction)
2. Three Products in Stripe Dashboard:
   - Pro Monthly ($9/mo, recurring)
   - Pro Annual ($89/year, recurring)
   - Founding Member ($29/mo, recurring)
3. Four environment variables:
   ```
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PRICE_PRO_MONTHLY=price_...
   STRIPE_PRICE_PRO_ANNUAL=price_...
   STRIPE_PRICE_FOUNDING=price_...
   ```

### The Checkout Flow
1. Reader clicks "Upgrade to Pro" on your site
2. Your API creates a Stripe Checkout Session
3. Reader enters payment on Stripe's hosted page (you never touch card data)
4. Stripe redirects back to your site with `?upgraded=true`
5. Webhook updates subscriber tier in your database
6. Next newsletter sends full content to paid subscribers

### The Paywall

Free readers see top 5 stories. A gradient fade covers stories 6-20 with an upgrade CTA. Simple CSS:

```css
.paywall-fade {
  height: 120px;
  background: linear-gradient(transparent, var(--color-bg));
  margin-top: -120px;
}
```

No JavaScript paywall hacks. No client-side checks. The full content simply isn't in the free email — it's server-side.

## Revenue Projections

| Subscribers | Free | Pro ($9) | Founding ($29) | MRR |
|---|---|---|---|---|
| 100 | 90 | 8 | 2 | $130 |
| 500 | 425 | 60 | 15 | $975 |
| 1,000 | 850 | 120 | 30 | $1,950 |
| 5,000 | 4,250 | 600 | 50* | $6,850 |

*Founding caps at 50 spots

At 1,000 subscribers with 15% paid conversion, you're making ~$2K/month from a newsletter that takes 5 minutes per issue to produce.

## The Real Moat

It's not the content. Anyone can summarize AI news.

It's the **training loop**. Your system gets better every week because you're rating articles. After 3 months, your curation is trained on your specific taste. No competitor can replicate that without starting from scratch.

That's worth $9/month.
