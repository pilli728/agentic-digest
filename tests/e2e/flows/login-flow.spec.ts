import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test('submit email on /login shows check-email state', async ({ page }) => {
    await page.route('**/api/auth/login', (route) =>
      route.fulfill({
        json: { success: true, message: 'Magic link sent' },
      })
    );
    await page.goto('/login');
    await page.locator('#login-email').fill('flow@example.com');
    await page.locator('#login-btn').click();
    await expect(page.locator('#check-email')).toBeVisible();
    await expect(page.locator('#sent-to-email')).toHaveText('flow@example.com');
  });

  test('verify token sets localStorage and shows success', async ({ page }) => {
    await page.route('**/api/auth/verify', (route) =>
      route.fulfill({
        json: {
          success: true,
          session_id: 'sess_flow_123',
          email: 'flow@example.com',
          tier: 'pro',
        },
      })
    );
    await page.goto('/auth/verify?token=mock-token');
    await expect(page.locator('#verify-success')).toBeVisible();
    await expect(page.locator('#verified-email')).toHaveText('flow@example.com');

    const session = await page.evaluate(() => localStorage.getItem('ae_session'));
    const email = await page.evaluate(() => localStorage.getItem('ae_email'));
    const tier = await page.evaluate(() => localStorage.getItem('ae_tier'));
    expect(session).toBe('sess_flow_123');
    expect(email).toBe('flow@example.com');
    expect(tier).toBe('pro');
  });

  test('after login, nav shows email instead of Sign in', async ({ page }) => {
    // Set localStorage as if user just verified
    await page.addInitScript(() => {
      localStorage.setItem('ae_session', 'sess_flow_123');
      localStorage.setItem('ae_email', 'flow@example.com');
      localStorage.setItem('ae_tier', 'pro');
    });
    await page.goto('/');
    await expect(page.locator('#nav-signin').first()).toBeHidden();
    await expect(page.locator('#nav-user').first()).toBeVisible();
    await expect(page.locator('#nav-user').first()).toHaveText('flow@example.com');
  });
});
