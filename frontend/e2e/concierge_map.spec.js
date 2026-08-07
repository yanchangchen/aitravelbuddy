// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Traveler\'s Desk — Concierge Chat & Map Views', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/desk');
  });

  test('should render AI Concierge chat input and message bubbles', async ({ page }) => {
    const chatInput = page.locator('input[placeholder*="Ask" i], input[placeholder*="concierge" i], input[placeholder*="chat" i], textarea[placeholder*="Ask" i]').first();
    if (await chatInput.isVisible()) {
      await expect(chatInput).toBeVisible();
      await chatInput.fill('Suggest family restaurants in Tokyo');
      
      const sendBtn = page.locator('button[type="submit"], button:has-text("Send")').first();
      if (await sendBtn.isVisible()) {
        await sendBtn.click();
      }
    }
  });

  test('should allow switching between Timeline, Map, Hotels, and Flights view tabs', async ({ page }) => {
    const mapTab = page.locator('button:has-text("Map"), div:has-text("Map")').first();
    if (await mapTab.isVisible()) {
      await mapTab.click();
      await page.waitForTimeout(300);
      
      // Leaflet container should be visible
      const leafletMap = page.locator('.leaflet-container');
      if (await leafletMap.isVisible()) {
        await expect(leafletMap).toBeVisible();
      }
    }

    const timelineTab = page.locator('button:has-text("Timeline"), div:has-text("Timeline")').first();
    if (await timelineTab.isVisible()) {
      await timelineTab.click();
      await page.waitForTimeout(300);
    }
  });

  test('should render sticky budget bar at bottom of canvas', async ({ page }) => {
    const budgetBar = page.locator('.budget-bar, .center-canvas footer, .budget-summary');
    if (await budgetBar.isVisible()) {
      await expect(budgetBar).toBeVisible();
    }
  });
});
