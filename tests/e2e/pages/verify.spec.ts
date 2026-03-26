import { test, expect } from '@playwright/test';

test.describe('Verify Page (/auth/verify)', () => {
  test('navigate without token shows fail state', async ({ page }) => {
    await page.goto('/auth/verify');
    await expect(page.locator('#verify-fail')).toBeVisible();
    await expect(page.locator('#verifying')).toBeHidden();
  });

  test('successful verification shows success state', async ({ page }) => {
    await page.route('**/api/auth/verify', (route) =>
      route.fulfill({
        json: {
          success: true,
          session_id: 'sess_123',
          email: 'verified@test.com',
          tier: 'pro',
        },
      })
    );
    await page.goto('/auth/verify?token=test123');
    await expect(page.locator('#verify-success')).toBeVisible();
    await expect(page.locator('#verifying')).toBeHidden();
  });

  test('success state shows verified email', async ({ page }) => {
    await page.route('**/api/auth/verify', (route) =>
      route.fulfill({
        json: {
          success: true,
          session_id: 'sess_123',
          email: 'verified@test.com',
          tier: 'pro',
        },
      })
    );
    await page.goto('/auth/verify?token=test123');
    await expect(page.locator('#verified-email')).toHaveText('verified@test.com');
  });

  test('on success localStorage has session data', async ({ page }) => {
    await page.route('**/api/auth/verify', (route) =>
      route.fulfill({
        json: {
          success: true,
          session_id: 'sess_abc',
          email: 'store@test.com',
          tier: 'inner',
        },
      })
    );
    await page.goto('/auth/verify?token=test123');
    await expect(page.locator('#verify-success')).toBeVisible();

    const session = await page.evaluate(() => localStorage.getItem('ae_session'));
    const email = await page.evaluate(() => localStorage.getItem('ae_email'));
    const tier = await page.evaluate(() => localStorage.getItem('ae_tier'));
    expect(session).toBe('sess_abc');
    expect(email).toBe('store@test.com');
    expect(tier).toBe('inner');
  });

  test('continue link goes to /pro', async ({ page }) => {
    await page.route('**/api/auth/verify', (route) =>
      route.fulfill({
        json: {
          success: true,
          session_id: 'sess_123',
          email: 'verified@test.com',
          tier: 'pro',
        },
      })
    );
    await page.goto('/auth/verify?token=test123');
    await expect(page.locator('#verify-success')).toBeVisible();
    const continueLink = page.locator('.continue-btn').first();
    await expect(continueLink).toHaveAttribute('href', '/pro');
  });

  test('failed verification shows fail state', async ({ page }) => {
    await page.route('**/api/auth/verify', (route) =>
      route.fulfill({
        json: { success: false },
      })
    );
    await page.goto('/auth/verify?token=expired');
    await expect(page.locator('#verify-fail')).toBeVisible();
    await expect(page.locator('#verify-success')).toBeHidden();
  });

  test('fail state shows "Link expired" heading', async ({ page }) => {
    await page.route('**/api/auth/verify', (route) =>
      route.fulfill({
        json: { success: false },
      })
    );
    await page.goto('/auth/verify?token=expired');
    await expect(page.locator('#verify-fail h1')).toHaveText('Link expired');
  });

  test('"Request a new link" button links to /login', async ({ page }) => {
    await page.route('**/api/auth/verify', (route) =>
      route.fulfill({
        json: { success: false },
      })
    );
    await page.goto('/auth/verify?token=expired');
    await expect(page.locator('#verify-fail')).toBeVisible();
    const loginLink = page.locator('#verify-fail .continue-btn');
    await expect(loginLink).toHaveAttribute('href', '/login');
    await expect(loginLink).toHaveText('Request a new link');
  });
});
