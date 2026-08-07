// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
  test('should load with hero section and animated title', async ({ page }) => {
    await page.goto('/');
    
    // Check page title
    await expect(page).toHaveTitle(/Travel Buddy/);
    
    // Check main title text
    const title = page.locator('h1').first();
    await expect(title).toBeVisible();
    await expect(title).toContainText('Travel Buddy');
    
    // Check subtitle
    const subtitle = page.locator('header p').first();
    await expect(subtitle).toBeVisible();
    await expect(subtitle).toContainText('AI-Powered Multi-Agent Travel Planning');
    
    // Check CTA button exists
    const ctaButton = page.locator('button:has-text("Start Planning")');
    await expect(ctaButton).toBeVisible();
  });

  test('should display seasonal inspiration cards', async ({ page }) => {
    await page.goto('/');
    
    // Check seasonal header exists
    const seasonalHeader = page.locator('h2:has-text("Seasonal Inspiration")');
    await expect(seasonalHeader).toBeVisible();
    
    // Check at least one destination card is rendered (Kyoto, Swiss Alps, Santorini)
    const cards = page.locator('h3:has-text("Kyoto"), h3:has-text("Swiss Alps"), h3:has-text("Santorini")');
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('should display feature highlight cards', async ({ page }) => {
    await page.goto('/');
    
    // Check features cards exist
    const agentCard = page.locator('h3:has-text("4 AI Agents")');
    await expect(agentCard).toBeVisible();
    
    const budgetCard = page.locator('h3:has-text("Smart Budget Guard")');
    await expect(budgetCard).toBeVisible();
  });

  test('should navigate to Desk page when Start Planning is clicked', async ({ page }) => {
    await page.goto('/');
    
    const ctaButton = page.locator('button:has-text("Start Planning")');
    await ctaButton.click();
    
    // Should navigate to /desk
    await expect(page).toHaveURL(/\/desk/);
  });
});
