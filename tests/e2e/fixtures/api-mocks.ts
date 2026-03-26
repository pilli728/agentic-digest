import { Page } from '@playwright/test';

/**
 * Mock POST /api/subscribe to return a success response.
 */
export async function mockSubscribeSuccess(page: Page) {
  await page.route('**/api/subscribe', async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Subscribed successfully' }),
      });
    } else {
      await route.fallback();
    }
  });
}

/**
 * Mock POST /api/subscribe to return a 400 error.
 */
export async function mockSubscribeError(page: Page, errorMessage = 'Invalid email') {
  await page.route('**/api/subscribe', async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ success: false, error: errorMessage }),
      });
    } else {
      await route.fallback();
    }
  });
}

/**
 * Mock POST /api/auth/login to return success.
 */
export async function mockLoginSuccess(page: Page, email: string) {
  await page.route('**/api/auth/login', async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, email }),
      });
    } else {
      await route.fallback();
    }
  });
}

/**
 * Mock POST /api/auth/login to return 404 (email not found).
 */
export async function mockLoginNotFound(page: Page) {
  await page.route('**/api/auth/login', async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ success: false, error: 'Email not found' }),
      });
    } else {
      await route.fallback();
    }
  });
}

/**
 * Mock POST /api/checkout to return success with a fake session URL.
 */
export async function mockCheckoutSuccess(page: Page) {
  await page.route('**/api/checkout', async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          url: 'https://checkout.stripe.com/test_session',
        }),
      });
    } else {
      await route.fallback();
    }
  });
}

/**
 * Mock POST /api/feedback to return success.
 */
export async function mockFeedbackSuccess(page: Page) {
  await page.route('**/api/feedback', async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Feedback recorded' }),
      });
    } else {
      await route.fallback();
    }
  });
}

/**
 * Mock POST /api/unsubscribe to return success.
 */
export async function mockUnsubscribeSuccess(page: Page) {
  await page.route('**/api/unsubscribe', async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Unsubscribed successfully' }),
      });
    } else {
      await route.fallback();
    }
  });
}

/**
 * Mock all API routes to simulate a server outage (503).
 */
export async function mockApiDown(page: Page) {
  await page.route('**/api/**', async (route) => {
    await route.fulfill({
      status: 503,
      contentType: 'application/json',
      body: JSON.stringify({ success: false, error: 'Service unavailable' }),
    });
  });
}
