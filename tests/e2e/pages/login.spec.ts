import { test, expect } from '@playwright/test';

test.describe('Login Page (/login)', () => {
  test('page loads and login form is visible', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('#login-card')).toBeVisible();
    await expect(page.locator('#login-form')).toBeVisible();
  });

  test('check-email and error states are hidden by default', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('#check-email')).toBeHidden();
    await expect(page.locator('#login-error')).toBeHidden();
  });

  test('login form has email input and submit button', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('#login-email')).toBeVisible();
    await expect(page.locator('#login-btn')).toHaveText('Send magic link');
  });

  test('successful login shows check-email state with email', async ({ page }) => {
    await page.route('**/api/auth/login', (route) =>
      route.fulfill({
        json: { success: true, message: 'Magic link sent' },
      })
    );
    await page.goto('/login');
    await page.locator('#login-email').fill('test@example.com');
    await page.locator('#login-btn').click();
    await expect(page.locator('#check-email')).toBeVisible();
    await expect(page.locator('#sent-to-email')).toHaveText('test@example.com');
    await expect(page.locator('#login-card')).toBeHidden();
  });

  test('failed login shows error state', async ({ page }) => {
    await page.route('**/api/auth/login', (route) =>
      route.fulfill({
        json: { success: false, message: 'Not found' },
      })
    );
    await page.goto('/login');
    await page.locator('#login-email').fill('unknown@example.com');
    await page.locator('#login-btn').click();
    await expect(page.locator('#login-error')).toBeVisible();
    await expect(page.locator('#login-card')).toBeHidden();
  });

  test('error state has "Not found" heading', async ({ page }) => {
    await page.route('**/api/auth/login', (route) =>
      route.fulfill({
        json: { success: false },
      })
    );
    await page.goto('/login');
    await page.locator('#login-email').fill('unknown@example.com');
    await page.locator('#login-btn').click();
    await expect(page.locator('#login-error')).toBeVisible();
    await expect(page.locator('#login-error h1')).toHaveText('Not found');
  });

  test('try-again button returns to login form from error', async ({ page }) => {
    await page.route('**/api/auth/login', (route) =>
      route.fulfill({
        json: { success: false },
      })
    );
    await page.goto('/login');
    await page.locator('#login-email').fill('unknown@example.com');
    await page.locator('#login-btn').click();
    await expect(page.locator('#login-error')).toBeVisible();
    await page.locator('#login-error .try-again').click();
    await expect(page.locator('#login-card')).toBeVisible();
    await expect(page.locator('#login-error')).toBeHidden();
  });

  test('try-again button returns to login form from check-email', async ({ page }) => {
    await page.route('**/api/auth/login', (route) =>
      route.fulfill({
        json: { success: true },
      })
    );
    await page.goto('/login');
    await page.locator('#login-email').fill('test@example.com');
    await page.locator('#login-btn').click();
    await expect(page.locator('#check-email')).toBeVisible();
    await page.locator('#check-email .try-again').click();
    await expect(page.locator('#login-card')).toBeVisible();
    await expect(page.locator('#check-email')).toBeHidden();
  });

  test('already logged in redirects to /pro', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('ae_session', 'test-session-id');
      localStorage.setItem('ae_email', 'user@test.com');
      localStorage.setItem('ae_tier', 'pro');
    });
    await page.route('**/api/auth/session', (route) =>
      route.fulfill({
        json: { success: true, email: 'user@test.com', tier: 'pro' },
      })
    );
    await page.goto('/login');
    await page.waitForURL('**/pro');
    expect(page.url()).toContain('/pro');
  });

  test('"Not a subscriber" link points to /', async ({ page }) => {
    await page.goto('/login');
    const link = page.locator('.login-note a');
    await expect(link).toHaveAttribute('href', '/');
    await expect(link).toHaveText('Join for free');
  });
});
