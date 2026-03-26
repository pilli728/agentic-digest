import { test, expect } from '@playwright/test';
import { API_BASE } from '../fixtures/test-data';

test.describe('Articles API', () => {
  let ctx: Awaited<ReturnType<typeof import('@playwright/test')['request']['newContext']>>;

  test.beforeAll(async ({ playwright }) => {
    ctx = await playwright.request.newContext({ baseURL: API_BASE });
  });

  test.afterAll(async () => {
    await ctx.dispose();
  });

  test('GET /api/articles returns articles list', async () => {
    const res = await ctx.get('/api/articles');
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.success).toBe(true);
    expect(typeof body.total).toBe('number');
    expect(Array.isArray(body.articles)).toBe(true);
  });

  test('GET /api/articles/by-tier returns articles grouped by tier', async () => {
    const res = await ctx.get('/api/articles/by-tier');
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.success).toBe(true);
    expect(body.articles_by_tier).toBeDefined();
  });

  test('GET /api/articles/stats returns article statistics', async () => {
    const res = await ctx.get('/api/articles/stats');
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.success).toBe(true);
    expect(typeof body.total_articles).toBe('number');
    expect(body.ranked).toBeDefined();
  });

  test('GET /api/pipeline/status returns pipeline state', async () => {
    const res = await ctx.get('/api/pipeline/status');
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.state).toBeDefined();
    expect(body.message).toBeDefined();
  });

  test.skip('GET /api/digest/preview returns digest markdown', async () => {
    // Skipped: digest/preview calls Claude API to generate the digest via write_digest(),
    // which blocks the single-threaded Python HTTP server indefinitely when the API key
    // is missing or the call is slow, causing all subsequent API tests to fail.
    const res = await ctx.get('/api/digest/preview');
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.success).toBe(true);
    expect(typeof body.markdown).toBe('string');
    expect(typeof body.article_count).toBe('number');
  });

  test('GET /api/feedback/summary returns feedback counts', async () => {
    const res = await ctx.get('/api/feedback/summary');
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(typeof body.thumbs_up).toBe('number');
    expect(typeof body.thumbs_down).toBe('number');
  });

  test('GET /api/nonexistent returns 404', async () => {
    const res = await ctx.get('/api/nonexistent');
    expect(res.status()).toBe(404);
  });
});
