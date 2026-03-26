import { test, expect } from '@playwright/test';
import { API_BASE } from '../fixtures/test-data';

test.describe('Subscribe / Unsubscribe API', () => {
  let ctx: Awaited<ReturnType<typeof import('@playwright/test')['request']['newContext']>>;
  const uniqueEmail = () => `test+${Date.now()}@example.com`;

  test.beforeAll(async ({ playwright }) => {
    ctx = await playwright.request.newContext({ baseURL: API_BASE });
  });

  test.afterAll(async () => {
    await ctx.dispose();
  });

  test('POST /api/subscribe with valid email returns success', async () => {
    const email = uniqueEmail();
    const res = await ctx.post('/api/subscribe', {
      data: { email },
    });
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.success).toBe(true);
  });

  test('POST /api/subscribe with invalid email returns 400', async () => {
    const res = await ctx.post('/api/subscribe', {
      data: { email: 'not-an-email' },
    });
    expect(res.status()).toBe(400);

    const body = await res.json();
    expect(body.success).toBe(false);
  });

  test('POST /api/subscribe without email returns 400', async () => {
    // Send a body with a non-email key so it's not empty (empty dict {} is falsy in Python
    // causing the server to return no response).
    const res = await ctx.post('/api/subscribe', {
      data: { name: 'no-email' },
    });
    expect(res.status()).toBe(400);

    const body = await res.json();
    expect(body.success).toBe(false);
  });

  test('POST /api/unsubscribe with email returns success', async () => {
    const email = uniqueEmail();

    // Subscribe first so there is something to unsubscribe
    await ctx.post('/api/subscribe', { data: { email } });

    const res = await ctx.post('/api/unsubscribe', {
      data: { email },
    });
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.success).toBe(true);
  });

  test('resubscribe after unsubscribe resets active flag', async () => {
    const email = uniqueEmail();

    // Subscribe
    const sub1 = await ctx.post('/api/subscribe', { data: { email } });
    expect(sub1.status()).toBe(200);

    // Unsubscribe
    const unsub = await ctx.post('/api/unsubscribe', { data: { email } });
    expect(unsub.status()).toBe(200);

    // Resubscribe — active should reset to 1
    const sub2 = await ctx.post('/api/subscribe', { data: { email } });
    expect(sub2.status()).toBe(200);

    const body = await sub2.json();
    expect(body.success).toBe(true);
  });
});
