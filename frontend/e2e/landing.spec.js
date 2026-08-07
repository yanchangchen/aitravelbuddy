// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
  test('should load with hero section and animated title', async ({ page }) => {
    await page.goto('/');
    
    // Check page title
    await expect(page).toHaveTitle(/Travel Buddy/);
    
    // Check hero section renders
    const hero = page.locator('.landing-hero');
    await expect(hero).toBeVisible();
    
    // Check gradient title text
    const title = page.locator('.landing-hero h1');
    await expect(title).toContainText('Travel Buddy');
    
    // Check subtitle
    const subtitle = page.locator('.landing-hero p');
    await expect(subtitle).toBeVisible();
    
    // Check CTA button exists
    const ctaButton = page.locator('text=Start Planning');
    await expect(ctaButton).toBeVisible();
  });

  test('should display seasonal inspiration cards', async ({ page }) => {
    await page.goto('/');
    
    // Check seasonal section exists
    const seasonalSection = page.locator('.seasonal-section, .landing-seasonal');
    await expect(seasonalSection).toBeVisible({ timeout: 10000 });
    
    // Check at least one destination card is rendered
    const cards = page.locator('.destination-card, .seasonal-card, .glass-card');
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('should display feature highlight cards', async ({ page }) => {
    await page.goto('/');
    
    // Check features section
    const featureCards = page.locator('.feature-card, .features-section .glass-card');
    const count = await featureCards.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('should navigate to Desk page when Start Planning is clicked', async ({ page }) => {
    await page.goto('/');
    
    const ctaButton = page.locator('text=Start Planning');
    await ctaButton.click();
    
    // Should navigate to /desk
    await expect(page).toHaveURL(/\/desk/);
  });
});
