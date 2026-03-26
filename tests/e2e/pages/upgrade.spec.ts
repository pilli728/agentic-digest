import { test, expect } from '@playwright/test';

test.describe('Upgrade Page (/upgrade)', () => {
  test('page loads with "Choose your plan" heading', async ({ page }) => {
    await page.goto('/upgrade');
    await expect(page.locator('.upgrade-header h1')).toHaveText('Choose your plan');
  });

  test('3 plan cards visible (Free, Pro, Inner Circle)', async ({ page }) => {
    await page.goto('/upgrade');
    const planCards = page.locator('.plan-card');
    await expect(planCards).toHaveCount(3);
  });

  test('Free plan card is present', async ({ page }) => {
    await page.goto('/upgrade');
    const freeCard = page.locator('.free-plan');
    await expect(freeCard).toBeVisible();
    await expect(freeCard.locator('h2')).toHaveText('Free');
  });

  test('Free card button links to /', async ({ page }) => {
    await page.goto('/upgrade');
    const freeBtn = page.locator('.free-plan .checkout-btn');
    await expect(freeBtn).toHaveAttribute('href', '/');
  });

  test('Pro card has "Most Popular" badge', async ({ page }) => {
    await page.goto('/upgrade');
    const proPlan = page.locator('.pro-plan');
    const badge = proPlan.locator('.badge');
    await expect(badge).toHaveText('Most Popular');
  });

  test('Pro card shows $12/mo price', async ({ page }) => {
    await page.goto('/upgrade');
    const proPrice = page.locator('.pro-plan .price');
    await expect(proPrice).toContainText('$12');
  });

  test('Inner Circle card shows $39/mo price', async ({ page }) => {
    await page.goto('/upgrade');
    const innerPrice = page.locator('.inner-plan .price');
    await expect(innerPrice).toContainText('$39');
  });

  test('Pro checkout: calls checkout API with correct price key', async ({ page }) => {
    // Verify the checkout button calls the API with the correct price key.
    // We return a non-URL response to prevent navigation away from the page.
    let capturedBody: string | null = null;
    await page.route('**/api/checkout', async (route) => {
      capturedBody = route.request().postData();
      await route.fulfill({
        json: { success: false, message: 'Stripe not configured' },
      });
    });
    page.on('dialog', async (dialog) => {
      await dialog.accept();
    });
    await page.goto('/upgrade');
    await page.locator('#checkout-pro').click();
    // Wait a moment for the request to complete
    await page.waitForTimeout(500);
    expect(capturedBody).toContain('pro_monthly');
  });

  test('Inner Circle checkout: uses inner_monthly price_key', async ({ page }) => {
    let capturedBody: string | null = null;
    await page.route('**/api/checkout', async (route) => {
      capturedBody = route.request().postData();
      await route.fulfill({
        json: { checkout_url: 'https://stripe.com/mock-inner' },
      });
    });
    await page.goto('/upgrade');
    await page.locator('#checkout-inner').click();
    expect(capturedBody).toContain('inner_monthly');
  });

  test('checkout error: shows alert with message', async ({ page }) => {
    await page.route('**/api/checkout', (route) =>
      route.fulfill({
        json: { success: false, message: 'Stripe not configured' },
      })
    );
    page.on('dialog', async (dialog) => {
      expect(dialog.message()).toContain('Stripe not configured');
      await dialog.accept();
    });
    await page.goto('/upgrade');
    await page.locator('#checkout-pro').click();
  });

  test('FAQ section has questions', async ({ page }) => {
    await page.goto('/upgrade');
    const faqItems = page.locator('.faq-item');
    await expect(faqItems).toHaveCount(4);
    await expect(faqItems.first().locator('h3')).toHaveText('Can I cancel anytime?');
  });

  test('back link to / exists', async ({ page }) => {
    await page.goto('/upgrade');
    const backLink = page.locator('.back-link');
    await expect(backLink).toHaveAttribute('href', '/');
  });
});
