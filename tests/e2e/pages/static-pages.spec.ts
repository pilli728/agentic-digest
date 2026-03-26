import { test, expect } from '@playwright/test';

test.describe('Static Pages', () => {
  test('/pro loads and shows "Pro Library" heading', async ({ page }) => {
    await page.goto('/pro');
    await expect(page.locator('.pro-header h1')).toHaveText('Pro Library');
  });

  test('/pro has content cards', async ({ page }) => {
    await page.goto('/pro');
    const contentCards = page.locator('.content-card');
    const count = await contentCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('/pro/01-building-ai-newsletter-from-scratch loads and shows article content', async ({
    page,
  }) => {
    await page.goto('/pro/01-building-ai-newsletter-from-scratch');
    await expect(page).toHaveTitle(/Agentic Edge/);
    // Article should have main content
    const body = page.locator('body');
    await expect(body).toContainText('newsletter');
  });

  test('/privacy loads and shows "Privacy Policy" heading', async ({ page }) => {
    await page.goto('/privacy');
    await expect(page.locator('.legal-page h1')).toHaveText('Privacy Policy');
  });

  test('/terms loads and shows "Terms of Service" heading', async ({ page }) => {
    await page.goto('/terms');
    await expect(page.locator('.legal-page h1')).toHaveText('Terms of Service');
  });

  test('/archive loads and shows past digests', async ({ page }) => {
    await page.goto('/archive');
    await expect(page.locator('.archive-header h1')).toHaveText('Digest Archive');
    const digestItems = page.locator('.digest-item');
    const count = await digestItems.count();
    expect(count).toBeGreaterThan(0);
  });

  test('all pages have navigation bar - /pro', async ({ page }) => {
    await page.goto('/pro');
    await expect(page.locator('.site-nav')).toBeVisible();
    await expect(page.locator('.nav-brand')).toBeVisible();
  });

  test('all pages have navigation bar - /privacy', async ({ page }) => {
    await page.goto('/privacy');
    await expect(page.locator('.site-nav')).toBeVisible();
    await expect(page.locator('.nav-brand')).toBeVisible();
  });
});
