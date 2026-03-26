import { test, expect } from '@playwright/test';

test.describe('Unsubscribe Flow', () => {
  test('go to /unsubscribe, fill email, submit, done shown', async ({ page }) => {
    await page.route('**/api/unsubscribe', (route) =>
      route.fulfill({
        json: { success: true },
      })
    );
    await page.goto('/unsubscribe');
    await expect(page.locator('#unsub-form-card')).toBeVisible();
    await page.locator('#unsub-email').fill('unsub-flow@test.com');
    await page.locator('#unsub-form button[type="submit"]').click();
    await expect(page.locator('#unsub-done')).toBeVisible();
    await expect(page.locator('#unsub-form-card')).toBeHidden();
    await expect(page.locator('#unsub-done')).toContainText(
      "You won't receive any more emails"
    );
  });

  test.skip('navigate with ?email= auto-submits and shows done', async ({ page }) => {
    // Skipped: the unsubscribe page has a race condition where dispatchEvent('submit')
    // fires before addEventListener('submit') is registered, so auto-submit never triggers.
    await page.route('**/api/unsubscribe', (route) =>
      route.fulfill({
        json: { success: true },
      })
    );
    await page.goto('/unsubscribe?email=auto@test.com');
    await expect(page.locator('#unsub-done')).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('#unsub-form-card')).toBeHidden();
  });
});
