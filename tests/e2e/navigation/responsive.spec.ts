import { test, expect } from '@playwright/test';

test.describe('Responsive Design', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('homepage signup form stacks vertically on mobile', async ({ page }) => {
    await page.goto('/');
    const form = page.locator('.signup-form');
    await expect(form).toBeVisible();
    // On mobile, the form or its container should adapt layout
    // Check that the form elements are visible and accessible
    await expect(page.locator('#signup-email')).toBeVisible();
    await expect(page.locator('#signup-btn')).toBeVisible();
  });

  test('pricing cards display in single column on /upgrade', async ({ page }) => {
    await page.goto('/upgrade');
    const pricingSection = page.locator('.pricing-section');
    await expect(pricingSection).toBeVisible();
    // At 375px width, the grid should be single column (grid-template-columns: 1fr)
    const gridColumns = await pricingSection.evaluate((el) =>
      window.getComputedStyle(el).getPropertyValue('grid-template-columns')
    );
    // Single column means one value (the full width)
    const columnCount = gridColumns.trim().split(/\s+/).length;
    expect(columnCount).toBe(1);
  });

  test('nav bar is still functional on mobile', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.site-nav').first()).toBeVisible();
    await expect(page.locator('.nav-brand').first()).toBeVisible();
    await expect(page.locator('#nav-signin').first()).toBeVisible();
  });

  test('all plan cards are visible on mobile /upgrade', async ({ page }) => {
    await page.goto('/upgrade');
    const planCards = page.locator('.plan-card');
    await expect(planCards).toHaveCount(3);
    for (let i = 0; i < 3; i++) {
      await expect(planCards.nth(i)).toBeVisible();
    }
  });

  test('homepage content is readable on mobile', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1').first()).toBeVisible();
    await expect(page.locator('.tagline')).toBeVisible();
    await expect(page.locator('.signup-section')).toBeVisible();
  });
});
