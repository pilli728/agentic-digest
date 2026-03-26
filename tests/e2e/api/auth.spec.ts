import { test, expect } from '@playwright/test';
import { execSync } from 'child_process';
import { API_BASE } from '../fixtures/test-data';

test.describe('Auth API', () => {
  let ctx: Awaited<ReturnType<typeof import('@playwright/test')['request']['newContext']>>;
  const uniqueEmail = () => `auth+${Date.now()}@example.com`;

  test.beforeAll(async ({ playwright }) => {
    ctx = await playwright.request.newContext({ baseURL: API_BASE });
  });

  test.afterAll(async () => {
    await ctx.dispose();
  });

  test('POST /api/auth/login with subscribed email returns success', async () => {
    const email = uniqueEmail();

    // Subscribe the email first
    await ctx.post('/api/subscribe', { data: { email } });

    const res = await ctx.post('/api/auth/login', {
      data: { email },
    });
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.success).toBe(true);
  });

  test('POST /api/auth/login with unknown email returns failure', async () => {
    const res = await ctx.post('/api/auth/login', {
      data: { email: `unknown+${Date.now()}@example.com` },
    });

    const body = await res.json();
    expect(body.success).toBe(false);
  });

  test('POST /api/auth/login without email returns 400', async () => {
    // Send a body with a non-email key so it's not empty (empty dict {} is falsy in Python
    // causing the server to return no response).
    const res = await ctx.post('/api/auth/login', {
      data: { name: 'no-email' },
    });
    expect(res.status()).toBe(400);

    const body = await res.json();
    expect(body.success).toBe(false);
  });

  test('full auth cycle: subscribe → login → verify → session → logout', async () => {
    const email = uniqueEmail();

    // 1. Subscribe
    const subRes = await ctx.post('/api/subscribe', { data: { email } });
    expect(subRes.status()).toBe(200);

    // 2. Login (triggers magic-link / token creation)
    const loginRes = await ctx.post('/api/auth/login', { data: { email } });
    expect(loginRes.status()).toBe(200);
    expect((await loginRes.json()).success).toBe(true);

    // 3. Read the token directly from the SQLite database
    const token = execSync(
      `sqlite3 data/digest.db "SELECT token FROM auth_tokens ORDER BY expires_at DESC LIMIT 1"`,
    )
      .toString()
      .trim();
    expect(token.length).toBeGreaterThan(0);

    // 4. Verify the token (verify endpoint is POST, not GET)
    const verifyRes = await ctx.post('/api/auth/verify', {
      data: { token },
    });
    expect(verifyRes.status()).toBe(200);

    const verifyBody = await verifyRes.json();
    expect(verifyBody.success).toBe(true);

    // 5. Check session (session endpoint is POST with session_id)
    const sessionRes = await ctx.post('/api/auth/session', {
      data: { session_id: verifyBody.session_id },
    });
    expect(sessionRes.status()).toBe(200);

    // 6. Logout
    const logoutRes = await ctx.post('/api/auth/logout', {
      data: { session_id: verifyBody.session_id },
    });
    expect(logoutRes.status()).toBe(200);

    const logoutBody = await logoutRes.json();
    expect(logoutBody.success).toBe(true);
  });
});
