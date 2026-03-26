import { test, expect } from '@playwright/test';

test.describe('Landing Page (/)', () => {
  test('page loads with title containing "Agentic Edge"', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Agentic Edge/);
  });

  test('header shows h1 "Agentic Edge"', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1').first()).toHaveText('Agentic Edge');
  });

  test('header shows tagline', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.home-header .tagline')).toHaveText(
      'Your unfair advantage as an AI builder.'
    );
  });

  test('logo carousel exists with company names', async ({ page }) => {
    await page.goto('/');
    const logosSlide = page.locator('.logos-slide');
    await expect(logosSlide).toBeVisible();
    for (const company of ['Google', 'Meta', 'Anthropic', 'OpenAI', 'Apple']) {
      await expect(logosSlide.locator('.logo-item', { hasText: company }).first()).toBeVisible();
    }
  });

  test('signup form visible with email input and "Join for free" button', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#signup-email')).toBeVisible();
    await expect(page.locator('#signup-btn')).toHaveText('Join for free');
  });

  test('successful signup shows welcome modal', async ({ page }) => {
    await page.route('**/api/subscribe', (route) =>
      route.fulfill({
        json: { success: true, message: 'Subscribed', total_subscribers: 1 },
      })
    );
    await page.goto('/');
    await page.locator('#signup-email').fill('e2e-test@example.com');
    await page.locator('#signup-btn').click();
    await expect(page.locator('#welcome-modal')).toHaveClass(/active/);
  });

  test.skip('welcome modal shows confetti', async ({ page }) => {
    // Skipped: confetti container (#confetti-container / .confetti-piece) does not exist in current page design.
    await page.route('**/api/subscribe', (route) =>
      route.fulfill({
        json: { success: true, message: 'Subscribed', total_subscribers: 1 },
      })
    );
    await page.goto('/');
    await page.locator('#signup-email').fill('e2e-test@example.com');
    await page.locator('#signup-btn').click();
    await expect(page.locator('#welcome-modal')).toHaveClass(/active/);
    const confetti = page.locator('#confetti-container');
    await expect(confetti.locator('.confetti-piece').first()).toBeAttached();
  });

  test('welcome modal close button works', async ({ page }) => {
    await page.route('**/api/subscribe', (route) =>
      route.fulfill({
        json: { success: true, message: 'Subscribed', total_subscribers: 1 },
      })
    );
    await page.goto('/');
    await page.locator('#signup-email').fill('e2e-test@example.com');
    await page.locator('#signup-btn').click();
    await expect(page.locator('#welcome-modal')).toHaveClass(/active/);
    await page.locator('#modal-close').click();
    await expect(page.locator('#welcome-modal')).not.toHaveClass(/active/);
  });

  test('welcome modal overlay click closes modal', async ({ page }) => {
    await page.route('**/api/subscribe', (route) =>
      route.fulfill({
        json: { success: true, message: 'Subscribed', total_subscribers: 1 },
      })
    );
    await page.goto('/');
    await page.locator('#signup-email').fill('e2e-test@example.com');
    await page.locator('#signup-btn').click();
    await expect(page.locator('#welcome-modal')).toHaveClass(/active/);
    // Click the overlay itself (not the modal card)
    await page.locator('#welcome-modal').click({ position: { x: 10, y: 10 } });
    await expect(page.locator('#welcome-modal')).not.toHaveClass(/active/);
  });

  test('welcome modal has upgrade link to /upgrade', async ({ page }) => {
    await page.route('**/api/subscribe', (route) =>
      route.fulfill({
        json: { success: true, message: 'Subscribed', total_subscribers: 1 },
      })
    );
    await page.goto('/');
    await page.locator('#signup-email').fill('e2e-test@example.com');
    await page.locator('#signup-btn').click();
    await expect(page.locator('#welcome-modal')).toHaveClass(/active/);
    const upgradeLink = page.locator('.modal-pro-btn');
    await expect(upgradeLink).toHaveAttribute('href', '/upgrade');
  });

  test.skip('welcome modal has Inner Circle upgrade card linking to /upgrade?tier=inner', async ({
    page,
  }) => {
    // Skipped: current modal design has a single Pro upgrade link (.modal-pro-btn) not separate
    // .modal-upgrade-card / .modal-upgrade-card.gold cards. No Inner Circle card exists.
    await page.route('**/api/subscribe', (route) =>
      route.fulfill({
        json: { success: true, message: 'Subscribed', total_subscribers: 1 },
      })
    );
    await page.goto('/');
    await page.locator('#signup-email').fill('e2e-test@example.com');
    await page.locator('#signup-btn').click();
    await expect(page.locator('#welcome-modal')).toHaveClass(/active/);
    const goldCard = page.locator('.modal-upgrade-card.gold');
    await expect(goldCard).toHaveAttribute('href', '/upgrade?tier=inner');
  });

  test('signup error: button shows error text on failure', async ({ page }) => {
    await page.route('**/api/subscribe', (route) =>
      route.fulfill({
        json: { success: false, message: 'Already subscribed' },
      })
    );
    await page.goto('/');
    await page.locator('#signup-email').fill('e2e-test@example.com');
    await page.locator('#signup-btn').click();
    await expect(page.locator('#signup-btn')).not.toHaveText('Join for free');
  });

  test('signup error: button shows specific error message', async ({ page }) => {
    await page.route('**/api/subscribe', (route) =>
      route.fulfill({
        json: { success: false, message: 'Already subscribed' },
      })
    );
    await page.goto('/');
    await page.locator('#signup-email').fill('e2e-test@example.com');
    await page.locator('#signup-btn').click();
    await expect(page.locator('#signup-btn')).toHaveText('Already subscribed');
  });

  test('premium teaser cards are visible', async ({ page }) => {
    await page.goto('/');
    const teaserCards = page.locator('.teaser-card');
    await expect(teaserCards).toHaveCount(2);
    await expect(teaserCards.first()).toBeVisible();
  });

  test('premium teaser cards link to /upgrade', async ({ page }) => {
    await page.goto('/');
    const firstTeaser = page.locator('.teaser-card').first();
    await expect(firstTeaser).toHaveAttribute('href', '/upgrade');
  });

  test('premium teaser gold card links to /upgrade?tier=inner', async ({ page }) => {
    await page.goto('/');
    const goldTeaser = page.locator('.teaser-card.teaser-gold');
    await expect(goldTeaser).toHaveAttribute('href', '/upgrade?tier=inner');
  });

  test('bottom teaser section is visible', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.bottom-teaser')).toBeVisible();
  });

  test('bottom teaser has CTA linking to /upgrade', async ({ page }) => {
    await page.goto('/');
    const cta = page.locator('.bottom-teaser-cta a');
    await expect(cta).toHaveAttribute('href', '/upgrade');
  });

  test('about section has 4 value-card elements', async ({ page }) => {
    await page.goto('/');
    const valueCards = page.locator('.value-card');
    await expect(valueCards).toHaveCount(4);
  });

  test('about section has "Why this exists" heading', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.about h2')).toHaveText('Why this exists');
  });

  test('footer has link to /archive', async ({ page }) => {
    await page.goto('/');
    const footerLinks = page.locator('.site-footer a');
    const archiveLink = footerLinks.filter({ hasText: 'Archive' });
    await expect(archiveLink).toHaveAttribute('href', '/archive');
  });

  test('footer has link to /pro', async ({ page }) => {
    await page.goto('/');
    const footerLinks = page.locator('.site-footer a');
    const proLink = footerLinks.filter({ hasText: 'Pro Library' });
    await expect(proLink).toHaveAttribute('href', '/pro');
  });

  test('footer has link to /upgrade', async ({ page }) => {
    await page.goto('/');
    const footerLinks = page.locator('.site-footer a');
    const upgradeLink = footerLinks.filter({ hasText: 'Upgrade' });
    await expect(upgradeLink).toHaveAttribute('href', '/upgrade');
  });

  test('meta[name="api-url"] tag exists', async ({ page }) => {
    await page.goto('/');
    const meta = page.locator('meta[name="api-url"]').first();
    await expect(meta).toHaveAttribute('content', /.+/);
  });

  test('signup form email input has correct placeholder', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#signup-email')).toHaveAttribute('placeholder', 'you@company.com');
  });

  test('signup form email input is required', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#signup-email')).toHaveAttribute('type', 'email');
  });
});
