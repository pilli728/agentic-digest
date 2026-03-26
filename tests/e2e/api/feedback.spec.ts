import { test, expect } from '@playwright/test';
import { API_BASE } from '../fixtures/test-data';

test.describe('Feedback API', () => {
  let ctx: Awaited<ReturnType<typeof import('@playwright/test')['request']['newContext']>>;

  test.beforeAll(async ({ playwright }) => {
    ctx = await playwright.request.newContext({ baseURL: API_BASE });
  });

  test.afterAll(async () => {
    await ctx.dispose();
  });

  test('POST /api/feedback with articleId and reaction returns success', async () => {
    const res = await ctx.post('/api/feedback', {
      data: {
        articleId: `article-${Date.now()}`,
        reaction: 'thumbs_up',
      },
    });
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.success).toBe(true);
  });

  test('POST /api/feedback without articleId returns 400', async () => {
    const res = await ctx.post('/api/feedback', {
      data: { reaction: 'thumbs_up' },
    });
    expect(res.status()).toBe(400);

    const body = await res.json();
    expect(body.success).toBe(false);
  });

  test('POST /api/feedback with comment returns success', async () => {
    const res = await ctx.post('/api/feedback', {
      data: {
        articleId: `article-${Date.now()}`,
        reaction: 'thumbs_up',
        comment: 'Great article, very informative!',
      },
    });
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.success).toBe(true);
  });
});
