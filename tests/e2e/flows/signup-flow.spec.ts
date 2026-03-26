import { test, expect } from '@playwright/test';

test.describe('Signup Flow', () => {
  test('signup then click Pro upgrade navigates to /upgrade', async ({ page }) => {
    await page.route('**/api/subscribe', (route) =>
      route.fulfill({
        json: { success: true, message: 'Subscribed', total_subscribers: 42 },
      })
    );
    await page.goto('/');
    await page.locator('#signup-email').fill('flow-test@example.com');
    await page.locator('#signup-btn').click();
    await expect(page.locator('#welcome-modal')).toHaveClass(/active/);

    // Click the Pro upgrade link in the modal (now .modal-pro-btn instead of .modal-upgrade-card)
    const proUpgradeLink = page.locator('.modal-pro-btn');
    await proUpgradeLink.click();
    await page.waitForURL('**/upgrade');
    expect(page.url()).toContain('/upgrade');
  });

  test('signup then click "Start with free" closes modal, stays on /', async ({ page }) => {
    await page.route('**/api/subscribe', (route) =>
      route.fulfill({
        json: { success: true, message: 'Subscribed', total_subscribers: 42 },
      })
    );
    await page.goto('/');
    await page.locator('#signup-email').fill('flow-test@example.com');
    await page.locator('#signup-btn').click();
    await expect(page.locator('#welcome-modal')).toHaveClass(/active/);

    // Click "Start with free" close button
    await page.locator('#modal-close').click();
    await expect(page.locator('#welcome-modal')).not.toHaveClass(/active/);
    expect(page.url()).toMatch(/\/$/);
  });

  test.skip('signup then click Inner Circle upgrade navigates to /upgrade?tier=inner', async ({
    page,
  }) => {
    // Skipped: current modal design has a single Pro upgrade link (.modal-pro-btn)
    // not separate .modal-upgrade-card / .modal-upgrade-card.gold cards.
    await page.route('**/api/subscribe', (route) =>
      route.fulfill({
        json: { success: true, message: 'Subscribed', total_subscribers: 42 },
      })
    );
    await page.goto('/');
    await page.locator('#signup-email').fill('flow-test@example.com');
    await page.locator('#signup-btn').click();
    await expect(page.locator('#welcome-modal')).toHaveClass(/active/);

    // Click the Inner Circle (gold) upgrade card
    const innerCard = page.locator('.modal-upgrade-card.gold');
    await innerCard.click();
    await page.waitForURL('**/upgrade?tier=inner');
    expect(page.url()).toContain('/upgrade?tier=inner');
  });
});
