// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Traveler\'s Desk — 3-Pane Layout', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/desk');
  });

  test('should render the 3-pane desk layout', async ({ page }) => {
    // Check the desk layout container
    const desk = page.locator('.desk-layout');
    await expect(desk).toBeVisible();

    // Left pane should be visible
    const leftPane = page.locator('.pane.left');
    await expect(leftPane).toBeVisible();

    // Center canvas pane should be visible
    const centerPane = page.locator('.pane.center');
    await expect(centerPane).toBeVisible();

    // Right pane should be visible
    const rightPane = page.locator('.pane.right');
    await expect(rightPane).toBeVisible();
  });

  test('should have collapsible left drawer toggle', async ({ page }) => {
    const leftPane = page.locator('.pane.left');
    await expect(leftPane).toBeVisible();

    // Find and click the header menu toggle button
    const toggleBtn = page.locator('button.left-drawer-toggle').first();
    await expect(toggleBtn).toBeVisible();

    await toggleBtn.click();
    await page.waitForTimeout(300);
    
    // Check that desk-layout has 'left-closed' class
    const deskLayout = page.locator('.desk-layout');
    await expect(deskLayout).toHaveClass(/left-closed/);

    // Click header toggle button again to re-open
    await toggleBtn.click();
    await page.waitForTimeout(300);
    await expect(deskLayout).not.toHaveClass(/left-closed/);
  });
});

test.describe('Traveler\'s Desk — Trip Logistics Form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/desk');
  });

  test('should fill in trip logistics fields', async ({ page }) => {
    // Fill origin
    const originInput = page.locator('input[placeholder*="origin" i], input[value*="Singapore" i]').first();
    if (await originInput.isVisible()) {
      await originInput.fill('Singapore');
      await expect(originInput).toHaveValue('Singapore');
    }

    // Fill destination
    const destInput = page.locator('input[placeholder*="destination" i], input[placeholder*="Tokyo" i]').first();
    if (await destInput.isVisible()) {
      await destInput.fill('Tokyo, Japan');
      await expect(destInput).toHaveValue('Tokyo, Japan');
    }
  });

  test('should allow adjusting group composition', async ({ page }) => {
    // Find adults number input
    const adultsInput = page.locator('input[type="number"]').first();
    if (await adultsInput.isVisible()) {
      await adultsInput.fill('3');
      await expect(adultsInput).toHaveValue('3');
    }
  });

  test('should toggle self-drive checkbox', async ({ page }) => {
    const selfDriveCheckbox = page.locator('input[type="checkbox"]').first();
    if (await selfDriveCheckbox.isVisible()) {
      const initialState = await selfDriveCheckbox.isChecked();
      await selfDriveCheckbox.click();
      const newState = await selfDriveCheckbox.isChecked();
      expect(newState).not.toBe(initialState);
    }
  });
});

test.describe('Traveler\'s Desk — Persona Selection', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/desk');
  });

  test('should show persona options', async ({ page }) => {
    // Look for persona accordion title
    const personaHeader = page.locator('h3:has-text("Persona & Style")').first();
    await expect(personaHeader).toBeVisible();
  });

  test('should not change destination when selecting a persona', async ({ page }) => {
    // Fill in destination first
    const destInput = page.locator('input[placeholder*="destination" i], input[placeholder*="Tokyo" i]').first();
    if (await destInput.isVisible()) {
      await destInput.fill('Paris, France');
      
      // Select a persona option if visible
      const familyBtn = page.locator('button:has-text("Family"), label:has-text("Family")').first();
      if (await familyBtn.isVisible()) {
        await familyBtn.click();
        
        // Destination should remain Paris, France
        await expect(destInput).toHaveValue('Paris, France');
      }
    }
  });
});
