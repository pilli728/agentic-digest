import { test, expect } from '@playwright/test';

test.describe('Navigation Bar', () => {
  test('logged out: "Sign in" visible on /', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#nav-signin').first()).toBeVisible();
    await expect(page.locator('#nav-user').first()).toBeHidden();
  });

  test('logged out: "Sign in" visible on /pro', async ({ page }) => {
    await page.goto('/pro');
    await expect(page.locator('#nav-signin').first()).toBeVisible();
  });

  test('logged out: "Sign in" visible on /upgrade', async ({ page }) => {
    await page.goto('/upgrade');
    await expect(page.locator('#nav-signin').first()).toBeVisible();
  });

  test('logged in: email shown, "Sign in" hidden', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('ae_session', 'test-session');
      localStorage.setItem('ae_email', 'nav@test.com');
      localStorage.setItem('ae_tier', 'pro');
    });
    await page.goto('/');
    await expect(page.locator('#nav-signin').first()).toBeHidden();
    await expect(page.locator('#nav-user').first()).toBeVisible();
    await expect(page.locator('#nav-user').first()).toHaveText('nav@test.com');
  });

  test('brand link goes to /', async ({ page }) => {
    await page.goto('/pro');
    const brandLink = page.locator('.nav-brand').first();
    await expect(brandLink).toHaveAttribute('href', '/');
  });

  test('nav links: Archive goes to /archive, Pro goes to /pro', async ({ page }) => {
    await page.goto('/');
    const navLinks = page.locator('.nav-links').first().locator('a');
    const archiveLink = navLinks.filter({ hasText: 'Archive' });
    await expect(archiveLink).toHaveAttribute('href', '/archive');
    const proLink = navLinks.filter({ hasText: 'Pro' });
    await expect(proLink).toHaveAttribute('href', '/pro');
  });
});
