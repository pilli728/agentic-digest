# Agentic Edge — Launch Guide

Everything you need to do to go live at `agenticedge.tech` with working payments, emails, and auth.

---

## Status

| System | Status | What's Left |
|--------|--------|-------------|
| Website (Vercel) | ✅ Deployed | Set `PUBLIC_API_URL` env var |
| API Server (Railway) | ❌ Not deployed | Steps 1-2 below |
| Database | ⚠️ SQLite | Attach Railway volume so data persists |
| Stripe | ⚠️ Test mode | Switch to live keys + set up webhook |
| Resend (email) | ⚠️ Domain not verified | Verify DNS records |
| Plausible | ⚠️ Not verified | Re-run verification |
| Magic link auth | ❌ Blocked by Resend | Will work once Resend domain is verified |

---

## Step 1: Deploy API to Railway

1. Go to [railway.app](https://railway.app) → sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select `pilli728/agentic-digest`
4. Railway auto-detects `railway.json` and starts building
5. Wait for build to complete (1-2 minutes)

### Add a persistent volume (critical — without this, every redeploy wipes your database)

6. In your Railway service, click **Settings** → scroll to **Volumes**
7. Click **Add Volume**
8. Set mount path to `/app/data`
9. Railway will persist everything in `/app/data` across deploys — this is where `digest.db` lives

### Generate a public URL

10. Go to **Settings** → **Networking**
11. Click **Generate Domain**
12. You'll get a URL like: `agentic-digest-production-xxxx.up.railway.app`
13. **Copy this URL** — you need it for Steps 2 and 5

---

## Step 2: Set Railway environment variables

Go to your Railway service → **Variables** tab → add each of these:

```
RESEND_API_KEY=re_8BtJkYjC_xxxxxxxxxxxx
RESEND_FROM=Agentic Edge <digest@agenticedge.tech>
SITE_URL=https://agenticedge.tech
CORS_ORIGIN=https://agenticedge.tech
STRIPE_SECRET_KEY=sk_test_xxxxx              ← change to sk_live_ in Step 5
STRIPE_PRICE_PRO_MONTHLY=price_1TF8rD0ct4SV2SEKGfAm6LFf
STRIPE_PRICE_PRO_ANNUAL=price_1TF8rD0ct4SV2SEKEvso9Cjf
STRIPE_PRICE_FOUNDING=price_1TF8rE0ct4SV2SEKUCXgaKbg
STRIPE_WEBHOOK_SECRET=whsec_xxxxx            ← get this in Step 5
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

Copy the actual values from your local `.env` file.

Railway auto-redeploys when you save variables.

---

## Step 3: Point Vercel frontend to Railway API

1. Go to [vercel.com](https://vercel.com) → your `agentic-digest` project
2. Click **Settings** → **Environment Variables**
3. Add:

| Key | Value |
|-----|-------|
| `PUBLIC_API_URL` | `https://agentic-digest-production-xxxx.up.railway.app` |

Use the Railway URL from Step 1.

4. Go to **Deployments** tab → click the **⋮** menu on the latest deploy → **Redeploy**

After this, your site at `agenticedge.tech` will call the Railway API instead of localhost.

---

## Step 4: Verify Resend domain (fixes magic link emails)

Your DNS records from the screenshot show you've already added the Resend records. Now verify them:

1. Go to [resend.com/domains](https://resend.com/domains)
2. Find `agenticedge.tech` → click **Verify**
3. If it says "Pending", wait 5-10 minutes and try again — DNS propagation takes time
4. Once verified, status should show ✅ for DKIM and SPF

### Test that emails actually send

After domain is verified, test from your terminal:

```bash
python3 -c "
import resend, os
from dotenv import load_dotenv
load_dotenv()
resend.api_key = os.environ['RESEND_API_KEY']
r = resend.Emails.send({
    'from': 'Agentic Edge <digest@agenticedge.tech>',
    'to': ['YOUR_REAL_EMAIL@gmail.com'],
    'subject': 'Test — magic link email',
    'html': '<p>If you see this, Resend is working.</p>'
})
print('Sent:', r)
"
```

Replace `YOUR_REAL_EMAIL@gmail.com` with your email. Check inbox AND spam.

---

## Step 5: Set up Stripe for live payments

### 5a. Create webhook

1. Go to [dashboard.stripe.com/webhooks](https://dashboard.stripe.com/webhooks)
2. Make sure you're in **Test mode** first (toggle in top right)
3. Click **Add endpoint**
4. Endpoint URL: `https://YOUR_RAILWAY_URL/api/stripe/webhook`
5. Click **Select events** and check:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
6. Click **Add endpoint**
7. On the webhook page, click **Reveal** next to "Signing secret"
8. Copy the `whsec_...` value
9. Add it to Railway env vars: `STRIPE_WEBHOOK_SECRET=whsec_...`

### 5b. Test in test mode first

1. Go to your site → click **Upgrade** → click **Go Pro**
2. Use Stripe test card: `4242 4242 4242 4242`, any future date, any CVC
3. Verify:
   - You're redirected back to the site
   - Your tier updates to Pro
   - You can access The Vault
4. Test cancellation from the upgrade page

### 5c. Switch to live mode

Once test mode works end-to-end:

1. In Stripe Dashboard, toggle **off** Test mode (top right switch)
2. Go to **Developers** → **API keys**
3. Copy the live Secret key (`sk_live_...`)
4. In Stripe live mode, go to **Products** — verify your 3 products exist:
   - Pro Monthly ($12/mo)
   - Pro Annual ($99/yr)
   - Inner Circle ($39/mo)
5. If products don't exist in live mode, create them and copy the new price IDs
6. Update Railway env vars:
   - `STRIPE_SECRET_KEY=sk_live_...`
   - Update price IDs if they changed
7. Create a **new webhook** in live mode (same URL, same events, new signing secret)
8. Update `STRIPE_WEBHOOK_SECRET` with the new live webhook secret

**Important:** Test and live mode have separate webhooks, separate keys, and separate products.

---

## Step 6: Verify Plausible analytics

1. Go to [plausible.io/sites](https://plausible.io/sites)
2. Make sure your site is registered as `agenticedge.tech`
3. Click the gear → **Verify installation**
4. Open `agenticedge.tech` in another tab to generate a pageview
5. Go back to Plausible and click **Verify**

---

## Step 7: Test all 3 tiers end-to-end

Do this AFTER Steps 1-5 are done.

### Test 1: Free tier
- [ ] Go to `agenticedge.tech`
- [ ] Enter a fresh email in the subscribe form
- [ ] Check inbox — welcome email arrives with magic link
- [ ] Click magic link — you're logged in
- [ ] Visit `/pro` — shows "upgrade to Pro" gate
- [ ] Visit `/upgrade` — shows "Current plan" on Free
- [ ] Visit a digest in `/archive` — loads fine (no gate)

### Test 2: Pro tier
- [ ] While logged in, go to `/upgrade`
- [ ] Click "Go Pro — $12/month"
- [ ] Complete Stripe checkout (use test card if still in test mode)
- [ ] Redirected back — tier updates to Pro
- [ ] Visit `/pro` — content grid shows
- [ ] Click a Pro article — content loads
- [ ] Click a Founding/Inner Circle article — shows upgrade gate
- [ ] Visit `/upgrade` — Pro shows "Current plan"
- [ ] Click "Cancel subscription" — confirm — downgrades to Free
- [ ] Visit `/pro` — shows upgrade gate again

### Test 3: Inner Circle tier
- [ ] Subscribe with a new email
- [ ] Click magic link → logged in
- [ ] Go to `/upgrade` → click "Join Inner Circle — $39/month"
- [ ] Complete Stripe checkout
- [ ] Visit `/pro` — ALL content unlocked, including Founding
- [ ] Upgrade button in nav disappears

---

## Step 8: Nice-to-haves (do after launch)

These won't block launch but improve the experience:

- [ ] **OG image** — create a 1200x630px social preview image, save to `web/public/og-image.png`, add `<meta property="og:image">` to BaseLayout
- [ ] **Plausible goals** — set up conversion tracking for Signup, Checkout, Cancel events
- [ ] **Rate limiting** — add rate limits to `/api/auth/login` and `/api/subscribe` to prevent abuse
- [ ] **Error monitoring** — add Sentry or similar for API error alerts
- [ ] **Database backups** — set up periodic SQLite backup from Railway volume
- [ ] **Custom API domain** — point `api.agenticedge.tech` to Railway instead of the `.up.railway.app` URL

---

## Quick reference: all env vars

### Railway (API server)

| Variable | Example | Required |
|----------|---------|----------|
| `RESEND_API_KEY` | `re_xxxx` | Yes |
| `RESEND_FROM` | `Agentic Edge <digest@agenticedge.tech>` | Yes |
| `SITE_URL` | `https://agenticedge.tech` | Yes |
| `CORS_ORIGIN` | `https://agenticedge.tech` | Yes |
| `STRIPE_SECRET_KEY` | `sk_live_xxxx` | Yes |
| `STRIPE_PRICE_PRO_MONTHLY` | `price_xxxx` | Yes |
| `STRIPE_PRICE_PRO_ANNUAL` | `price_xxxx` | Yes |
| `STRIPE_PRICE_FOUNDING` | `price_xxxx` | Yes |
| `STRIPE_WEBHOOK_SECRET` | `whsec_xxxx` | Yes |
| `ANTHROPIC_API_KEY` | `sk-ant-xxxx` | For pipeline only |

### Vercel (frontend)

| Variable | Example | Required |
|----------|---------|----------|
| `PUBLIC_API_URL` | `https://your-railway-url.up.railway.app` | Yes |

---

## Architecture

```
User → agenticedge.tech (Vercel, static HTML/JS)
         ↓ API calls
       Railway (Python API server)
         ↓ reads/writes
       SQLite on persistent volume (/app/data/digest.db)
         ↓ sends emails
       Resend (transactional email)
         ↓ handles payments
       Stripe (subscriptions + webhooks)
```
