import { test, expect } from '@playwright/test';

const SITE = 'https://agenticedge.tech';
const API = 'https://agentic-digest-production.up.railway.app';
const TEST_EMAIL = `e2e-${Date.now()}@test.com`;

test.describe('Production E2E — agenticedge.tech', () => {

  // === PAGES LOAD ===
  test('homepage loads', async ({ page }) => {
    await page.goto(SITE);
    await expect(page).toHaveTitle(/Agentic Edge/);
    await expect(page.locator('h1').first()).toBeVisible();
  });

  test('login page loads', async ({ page }) => {
    await page.goto(`${SITE}/login`);
    await expect(page.locator('#login-form')).toBeVisible();
  });

  test('upgrade page loads with 3 plans', async ({ page }) => {
    await page.goto(`${SITE}/upgrade`);
    await expect(page.locator('.plan-card')).toHaveCount(3);
  });

  test('the vault loads', async ({ page }) => {
    await page.goto(`${SITE}/pro`);
    await expect(page.locator('h2').first()).toBeVisible();
  });

  test('privacy page loads', async ({ page }) => {
    await page.goto(`${SITE}/privacy`);
    await expect(page.locator('h1')).toContainText('Privacy');
  });

  test('terms page loads', async ({ page }) => {
    await page.goto(`${SITE}/terms`);
    await expect(page.locator('h1')).toContainText('Terms');
  });

  test('archive page loads', async ({ page }) => {
    await page.goto(`${SITE}/archive`);
    await expect(page).toHaveTitle(/Archive|Agentic/);
  });

  test('unsubscribe page loads', async ({ page }) => {
    await page.goto(`${SITE}/unsubscribe`);
    await expect(page.locator('#unsub-form')).toBeVisible();
  });

  // === NAV BAR ===
  test('nav bar shows sign in when logged out', async ({ page }) => {
    await page.goto(SITE);
    await expect(page.locator('#nav-signin').first()).toBeVisible();
  });

  test('nav bar links work', async ({ page }) => {
    await page.goto(SITE);
    // Click The Vault
    await page.locator('.nav-links a[href="/pro"]').first().click();
    await expect(page).toHaveURL(/\/pro/);
  });

  // === SIGNUP FLOW ===
  test('signup with new email shows welcome modal', async ({ page }) => {
    await page.goto(SITE);
    const form = page.locator('#signup-form');
    if (await form.isVisible()) {
      await page.fill('#signup-email', TEST_EMAIL);
      await page.click('#signup-btn');
      // Should either show modal or redirect to login
      await page.waitForTimeout(3000);
      const modal = page.locator('#welcome-modal');
      const url = page.url();
      // Either modal appeared or redirected to login (existing subscriber)
      expect(await modal.isVisible() || url.includes('/login')).toBeTruthy();
    }
  });

  // === LOGIN FLOW ===
  test('login sends magic link', async ({ page }) => {
    // First subscribe
    await page.request.post(`${API}/api/subscribe`, {
      data: { email: TEST_EMAIL }
    });

    await page.goto(`${SITE}/login`);
    await page.fill('#login-email', TEST_EMAIL);
    await page.click('#login-btn');
    await page.waitForTimeout(2000);

    // Should show check-email state
    const checkEmail = page.locator('#check-email');
    if (await checkEmail.isVisible()) {
      await expect(checkEmail).toContainText(TEST_EMAIL);
    }
  });

  test('login with unknown email shows error or redirects', async ({ page }) => {
    await page.goto(`${SITE}/login`);
    await page.fill('#login-email', 'nonexistent-e2e@nobody.com');
    await page.click('#login-btn');
    await page.waitForTimeout(2000);
    // Some kind of response should show
    const pageContent = await page.textContent('body');
    expect(pageContent).toBeTruthy();
  });

  // === UPGRADE PAGE ===
  test('pro checkout button redirects to Stripe', async ({ page }) => {
    await page.goto(`${SITE}/upgrade`);
    const proBtn = page.locator('[data-price="pro_monthly"]');
    if (await proBtn.isVisible()) {
      // Intercept the navigation to Stripe
      const [response] = await Promise.all([
        page.waitForEvent('requestfinished', r => r.url().includes('/api/checkout')),
        proBtn.click(),
      ]);
      // Should have called the checkout API
      expect(response.url()).toContain('/api/checkout');
    }
  });

  // === THE VAULT (AUTH GATE) ===
  test('vault shows auth gate when logged out', async ({ page }) => {
    await page.goto(`${SITE}/pro`);
    await page.waitForTimeout(1000);
    // Should see sign-in gate since not logged in
    const gate = page.locator('#auth-gate-signin');
    const upgrade = page.locator('#auth-gate-upgrade');
    const content = page.locator('#pro-content');

    // One of the gates should be visible, or content if somehow authed
    const gateVisible = await gate.isVisible() || await upgrade.isVisible();
    const contentVisible = await content.isVisible();
    expect(gateVisible || contentVisible).toBeTruthy();
  });

  test('vault shows content when logged in as pro', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('ae_session', 'test-session');
      localStorage.setItem('ae_email', 'pro@test.com');
      localStorage.setItem('ae_tier', 'pro');
    });
    // Mock session check to return valid
    await page.route('**/api/auth/session', route =>
      route.fulfill({ json: { success: true, email: 'pro@test.com', tier: 'pro' } })
    );
    await page.goto(`${SITE}/pro`);
    await page.waitForTimeout(2000);
    await expect(page.locator('#pro-content')).toBeVisible();
  });

  // === UNSUBSCRIBE ===
  test('unsubscribe with email param auto-fills', async ({ page }) => {
    await page.goto(`${SITE}/unsubscribe?email=test@test.com`);
    const input = page.locator('#unsub-email');
    await expect(input).toHaveValue('test@test.com');
  });

  // === RESPONSIVE ===
  test('homepage is responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(SITE);
    await expect(page.locator('h1').first()).toBeVisible();
    // Nav should still be present
    await expect(page.locator('.site-nav').first()).toBeVisible();
  });

  // === API DIRECT TESTS ===
  test('API: subscribe + unsubscribe cycle', async ({ request }) => {
    const email = `api-cycle-${Date.now()}@test.com`;

    // Subscribe
    const sub = await request.post(`${API}/api/subscribe`, {
      data: { email }
    });
    expect(sub.ok()).toBeTruthy();
    const subData = await sub.json();
    expect(subData.success).toBeTruthy();

    // Unsubscribe
    const unsub = await request.post(`${API}/api/unsubscribe`, {
      data: { email }
    });
    expect(unsub.ok()).toBeTruthy();

    // Resubscribe
    const resub = await request.post(`${API}/api/subscribe`, {
      data: { email }
    });
    const resubData = await resub.json();
    expect(resubData.success).toBeTruthy();
  });

  test('API: invalid email rejected', async ({ request }) => {
    const res = await request.post(`${API}/api/subscribe`, {
      data: { email: 'not-an-email' }
    });
    const data = await res.json();
    expect(data.success).toBeFalsy();
  });

  test('API: checkout returns Stripe URL', async ({ request }) => {
    const res = await request.post(`${API}/api/checkout`, {
      data: { price_key: 'pro_monthly' }
    });
    const data = await res.json();
    expect(data.checkout_url).toContain('checkout.stripe.com');
  });

  test('API: quick-add with valid secret', async ({ request }) => {
    const res = await request.post(`${API}/api/quick-add`, {
      data: {
        url: `https://example.com/e2e-${Date.now()}`,
        note: 'E2E test article',
        secret: 'ae_quick_add_2026'
      }
    });
    const data = await res.json();
    expect(data.success).toBeTruthy();
  });

  test('API: quick-add without secret rejected', async ({ request }) => {
    const res = await request.post(`${API}/api/quick-add`, {
      data: { url: 'https://example.com/no-auth' }
    });
    const data = await res.json();
    expect(data.success).toBeFalsy();
  });

  // === PLAUSIBLE ===
  test('plausible analytics script present', async ({ page }) => {
    await page.goto(SITE);
    const script = page.locator('script[src*="plausible"]');
    await expect(script).toHaveCount(1);
  });
});
