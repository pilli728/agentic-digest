import { Page } from '@playwright/test';

/**
 * Inject an authenticated session into localStorage before the page loads.
 * Call this *before* page.goto().
 */
export async function setAuthState(
  page: Page,
  opts: { email: string; token: string; tier?: string },
) {
  const { email, token, tier = 'free' } = opts;

  await page.addInitScript(
    ({ email, token, tier }) => {
      window.localStorage.setItem('auth_email', email);
      window.localStorage.setItem('auth_token', token);
      window.localStorage.setItem('auth_tier', tier);
    },
    { email, token, tier },
  );
}

/**
 * Remove all auth-related keys from localStorage before the page loads.
 * Call this *before* page.goto().
 */
export async function clearAuthState(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.removeItem('auth_email');
    window.localStorage.removeItem('auth_token');
    window.localStorage.removeItem('auth_tier');
  });
}

/**
 * Mock the POST /api/auth/login endpoint to return a successful response.
 */
export async function mockAuthLoginSuccess(page: Page, email: string) {
  await page.route('**/api/auth/login', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, email }),
    });
  });
}

/**
 * Mock the POST /api/auth/login endpoint to return a not-found response.
 */
export async function mockAuthLoginNotFound(page: Page) {
  await page.route('**/api/auth/login', async (route) => {
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ success: false, error: 'Email not found' }),
    });
  });
}

/**
 * Mock the POST /api/auth/logout endpoint to return success.
 */
export async function mockAuthLogoutSuccess(page: Page) {
  await page.route('**/api/auth/logout', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true }),
    });
  });
}

/**
 * Mock the GET /api/auth/session endpoint to return an active session.
 */
export async function mockAuthSessionActive(page: Page, email: string) {
  await page.route('**/api/auth/session', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, authenticated: true, email }),
    });
  });
}
