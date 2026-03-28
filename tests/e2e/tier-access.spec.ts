import { test, expect } from '@playwright/test';

const SITE = 'https://agenticedge.tech';

// Helper to set auth state before page load
async function setTier(page, tier: string) {
  await page.addInitScript((t) => {
    localStorage.setItem('ae_session', 'test-session-123');
    localStorage.setItem('ae_email', `${t}@test.com`);
    localStorage.setItem('ae_tier', t);
  }, tier);
  // Mock session validation to return the tier
  await page.route('**/api/auth/session', route =>
    route.fulfill({ json: { success: true, email: `${tier}@test.com`, tier } })
  );
}

test.describe('Tier Access Control — Free User', () => {
  test('homepage shows signup form', async ({ page }) => {
    await page.goto(SITE);
    const form = page.locator('#signup-form');
    await expect(form).toBeVisible();
  });

  test('homepage shows "Unlock with Pro" on top card', async ({ page }) => {
    await page.goto(SITE);
    const card = page.locator('#locked-top-free');
    await expect(card).toBeVisible();
    await expect(card).toContainText('PRO');
    await expect(card).toContainText('Unlock with Pro');
  });

  test('homepage sidebar shows "Premium Content" label', async ({ page }) => {
    await page.goto(SITE);
    const label = page.locator('#sidebar-cards-label');
    await expect(label).toContainText('Premium Content');
  });

  test('homepage shows both pro and founding sidebar cards', async ({ page }) => {
    await page.goto(SITE);
    const proCards = page.locator('.tier-pro-card');
    const foundingCards = page.locator('.tier-founding-card');
    expect(await proCards.count()).toBeGreaterThan(0);
    expect(await foundingCards.count()).toBeGreaterThan(0);
  });

  test('homepage shows "Unlock Pro" upgrade button (not gold)', async ({ page }) => {
    await page.goto(SITE);
    const proUpgrade = page.locator('#sidebar-upgrade');
    await expect(proUpgrade).toBeVisible();
    const goldUpgrade = page.locator('#sidebar-upgrade-gold');
    await expect(goldUpgrade).toBeHidden();
  });

  test('nav shows "Sign in" button', async ({ page }) => {
    await page.goto(SITE);
    await expect(page.locator('#nav-signin').first()).toBeVisible();
  });

  test('vault shows sign-in gate', async ({ page }) => {
    await page.goto(`${SITE}/pro`);
    await page.waitForTimeout(1500);
    const gate = page.locator('#auth-gate-signin');
    await expect(gate).toBeVisible();
  });

  test('vault content is hidden', async ({ page }) => {
    await page.goto(`${SITE}/pro`);
    await page.waitForTimeout(1500);
    await expect(page.locator('#pro-content')).toBeHidden();
  });

  test('upgrade page shows all 3 plans', async ({ page }) => {
    await page.goto(`${SITE}/upgrade`);
    await expect(page.locator('.plan-card')).toHaveCount(3);
  });

  test('upgrade page free plan says "Current plan"', async ({ page }) => {
    await page.goto(`${SITE}/upgrade`);
    await expect(page.locator('#free-btn')).toContainText('Current plan');
  });
});

test.describe('Tier Access Control — Pro User', () => {
  test.beforeEach(async ({ page }) => {
    await setTier(page, 'pro');
  });

  test('homepage hides signup form', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    const form = page.locator('.signup-section');
    // BaseLayout hides signup when logged in
    await expect(form).toBeHidden();
  });

  test('homepage shows founding article as top card (not pro)', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    const freeCard = page.locator('#locked-top-free');
    const proCard = page.locator('#locked-top-pro');
    await expect(freeCard).toBeHidden();
    await expect(proCard).toBeVisible();
    await expect(proCard).toContainText('INNER CIRCLE');
    await expect(proCard).toContainText('Unlock with Inner Circle');
  });

  test('homepage sidebar shows "Inner Circle Only" label', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    await expect(page.locator('#sidebar-cards-label')).toContainText('Inner Circle Only');
  });

  test('homepage hides pro-tier sidebar cards', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    const proCards = page.locator('.tier-pro-card');
    for (let i = 0; i < await proCards.count(); i++) {
      await expect(proCards.nth(i)).toBeHidden();
    }
  });

  test('homepage shows founding sidebar cards linking to /upgrade?tier=inner', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    const foundingCards = page.locator('.tier-founding-card');
    expect(await foundingCards.count()).toBeGreaterThan(0);
    const href = await foundingCards.first().getAttribute('href');
    expect(href).toContain('upgrade');
  });

  test('homepage shows gold upgrade button (not purple)', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    await expect(page.locator('#sidebar-upgrade')).toBeHidden();
    await expect(page.locator('#sidebar-upgrade-gold')).toBeVisible();
  });

  test('nav shows email, hides "Sign in"', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    await expect(page.locator('#nav-signin').first()).toBeHidden();
    await expect(page.locator('#nav-user-wrap').first()).toBeVisible();
  });

  test('vault shows content (not gate)', async ({ page }) => {
    await page.goto(`${SITE}/pro`);
    await page.waitForTimeout(2000);
    await expect(page.locator('#pro-content')).toBeVisible();
  });

  test('vault founding articles are dimmed/gated', async ({ page }) => {
    await page.goto(`${SITE}/pro`);
    await page.waitForTimeout(2000);
    const gated = page.locator('.tier-gated');
    expect(await gated.count()).toBeGreaterThan(0);
  });

  test('vault pro articles are accessible', async ({ page }) => {
    await page.goto(`${SITE}/pro`);
    await page.waitForTimeout(2000);
    // Content cards that are NOT founding-locked should be clickable
    const cards = page.locator('.content-card:not(.founding-locked)');
    if (await cards.count() > 0) {
      const href = await cards.first().getAttribute('href');
      expect(href).toContain('/pro/');
    }
  });
});

test.describe('Tier Access Control — Inner Circle User', () => {
  test.beforeEach(async ({ page }) => {
    await setTier(page, 'inner');
  });

  test('homepage hides signup form', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    await expect(page.locator('.signup-section')).toBeHidden();
  });

  test('homepage shows founding article unlocked as top card', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    const innerCard = page.locator('#locked-top-inner');
    await expect(innerCard).toBeVisible();
    await expect(innerCard).toContainText('Read now');
    // Should link to actual article, not upgrade
    const href = await innerCard.getAttribute('href');
    expect(href).toContain('/pro/');
  });

  test('homepage sidebar shows "Your Inner Circle Content"', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    await expect(page.locator('#sidebar-cards-label')).toContainText('Your Inner Circle Content');
  });

  test('homepage founding cards link to actual articles (not upgrade)', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    const cards = page.locator('.tier-founding-card');
    for (let i = 0; i < await cards.count(); i++) {
      const href = await cards.nth(i).getAttribute('href');
      expect(href).toContain('/pro/');
      expect(href).not.toContain('upgrade');
    }
  });

  test('homepage hides both upgrade buttons', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    await expect(page.locator('#sidebar-upgrade')).toBeHidden();
    await expect(page.locator('#sidebar-upgrade-gold')).toBeHidden();
  });

  test('nav hides upgrade link', async ({ page }) => {
    await page.goto(SITE);
    await page.waitForTimeout(500);
    const upgradeLink = page.locator('.nav-upgrade').first();
    await expect(upgradeLink).toBeHidden();
  });

  test('vault shows all content unlocked (no gated cards)', async ({ page }) => {
    await page.goto(`${SITE}/pro`);
    await page.waitForTimeout(2000);
    await expect(page.locator('#pro-content')).toBeVisible();
    const gated = page.locator('.tier-gated');
    expect(await gated.count()).toBe(0);
  });

  test('vault founding articles are clickable (not blocked)', async ({ page }) => {
    await page.goto(`${SITE}/pro`);
    await page.waitForTimeout(2000);
    const foundingCards = page.locator('.founding-locked');
    for (let i = 0; i < await foundingCards.count(); i++) {
      const classes = await foundingCards.nth(i).getAttribute('class');
      expect(classes).not.toContain('tier-gated');
    }
  });

  test('individual founding article shows content (not gate)', async ({ page }) => {
    await page.goto(`${SITE}/pro/10-budget-llm-spreadsheet`);
    await page.waitForTimeout(2000);
    await expect(page.locator('#pro-content')).toBeVisible();
    await expect(page.locator('#auth-gate')).toBeHidden();
  });
});

test.describe('Tier Access Control — Pro accessing founding content', () => {
  test('pro user sees gate on founding article page', async ({ page }) => {
    await setTier(page, 'pro');
    // Mock session returns pro (not inner)
    await page.goto(`${SITE}/pro/10-budget-llm-spreadsheet`);
    await page.waitForTimeout(2000);
    // Should see gate or redirect — content should NOT be visible
    const content = page.locator('#pro-content');
    const gate = page.locator('#auth-gate');
    // Either gate is visible or content is hidden
    const gateVisible = await gate.isVisible();
    const contentVisible = await content.isVisible();
    expect(gateVisible || !contentVisible).toBeTruthy();
  });

  test('pro user can access pro article page', async ({ page }) => {
    await setTier(page, 'pro');
    await page.goto(`${SITE}/pro/07-vibecoding-masterclass`);
    await page.waitForTimeout(2000);
    await expect(page.locator('#pro-content')).toBeVisible();
  });
});
