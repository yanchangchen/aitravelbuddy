# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: desk.spec.js >> Traveler's Desk — 3-Pane Layout >> should have collapsible left drawer
- Location: e2e\desk.spec.js:27:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('.left-drawer')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('.left-drawer')

```

```yaml
- banner:
  - button:
    - img
  - heading "Travel Buddy Desk" [level=1]
  - button "Save":
    - img
    - text: Save
  - button "Export":
    - img
    - text: Export
- complementary:
  - button:
    - img
  - text: Trip Details
  - heading "📍 Trip Logistics" [level=3]
  - img
  - text: Origin City
  - img
  - textbox "e.g. New York"
  - text: Destination City
  - img
  - textbox "e.g. Tokyo"
  - text: Start Date
  - textbox
  - text: End Date
  - textbox
  - text: Travelers Adults
  - spinbutton: "2"
  - text: Children
  - spinbutton: "0"
  - text: Infants
  - spinbutton: "0"
  - checkbox "Self-drive (Rent a car)"
  - text: Self-drive (Rent a car) Budget
  - checkbox "No Budget Limit"
  - text: No Budget Limit
  - spinbutton: "5000"
  - combobox:
    - option "USD" [selected]
    - option "EUR"
    - option "JPY"
    - option "GBP"
  - heading "🎭 Persona & Style" [level=3]
  - img
  - button "Solo"
  - button "Business"
  - button "Couple"
  - button "Family"
  - button "Backpacker"
  - button "Custom"
  - heading "💾 Saved Trips" [level=3]
  - img
- main:
  - button "Timeline"
  - button "Map"
  - button "Split View"
  - button "Hotels"
  - button "Bookings"
  - img
  - paragraph: Start a conversation or fill in your trip details to begin
- complementary:
  - text: Concierge
  - button:
    - img
  - button "Plan Trip":
    - img
    - text: Plan Trip
  - button:
    - img
  - text: Hello! I am your Travel Buddy. How can I help you plan your trip today?
  - textbox "Tell me what you'd like..."
  - button:
    - img
```

# Test source

```ts
  1   | // @ts-check
  2   | import { test, expect } from '@playwright/test';
  3   | 
  4   | test.describe('Traveler\'s Desk — 3-Pane Layout', () => {
  5   |   test.beforeEach(async ({ page }) => {
  6   |     await page.goto('/desk');
  7   |   });
  8   | 
  9   |   test('should render the 3-pane desk layout', async ({ page }) => {
  10  |     // Check the desk container
  11  |     const desk = page.locator('.desk-layout, .desk-container');
  12  |     await expect(desk).toBeVisible();
  13  | 
  14  |     // Left drawer should be visible
  15  |     const leftDrawer = page.locator('.left-drawer');
  16  |     await expect(leftDrawer).toBeVisible();
  17  | 
  18  |     // Center canvas should be visible
  19  |     const center = page.locator('.center-canvas');
  20  |     await expect(center).toBeVisible();
  21  | 
  22  |     // Right panel should be visible
  23  |     const right = page.locator('.right-panel');
  24  |     await expect(right).toBeVisible();
  25  |   });
  26  | 
  27  |   test('should have collapsible left drawer', async ({ page }) => {
  28  |     const leftDrawer = page.locator('.left-drawer');
> 29  |     await expect(leftDrawer).toBeVisible();
      |                              ^ Error: expect(locator).toBeVisible() failed
  30  | 
  31  |     // Find and click the collapse/toggle button
  32  |     const toggleBtn = page.locator('.drawer-toggle, .left-drawer button').first();
  33  |     if (await toggleBtn.isVisible()) {
  34  |       await toggleBtn.click();
  35  |       // Drawer should collapse (hidden or width 0)
  36  |       await page.waitForTimeout(500); // wait for animation
  37  |       
  38  |       // Click again to expand
  39  |       await toggleBtn.click();
  40  |       await page.waitForTimeout(500);
  41  |       await expect(leftDrawer).toBeVisible();
  42  |     }
  43  |   });
  44  | });
  45  | 
  46  | test.describe('Traveler\'s Desk — Trip Logistics Form', () => {
  47  |   test.beforeEach(async ({ page }) => {
  48  |     await page.goto('/desk');
  49  |   });
  50  | 
  51  |   test('should fill in trip logistics fields', async ({ page }) => {
  52  |     // Fill origin
  53  |     const originInput = page.locator('input[placeholder*="origin" i], input[name="origin"], label:has-text("Origin") + input, label:has-text("Origin") ~ input').first();
  54  |     if (await originInput.isVisible()) {
  55  |       await originInput.fill('Singapore');
  56  |       await expect(originInput).toHaveValue('Singapore');
  57  |     }
  58  | 
  59  |     // Fill destination
  60  |     const destInput = page.locator('input[placeholder*="destination" i], input[name="destination"], label:has-text("Destination") + input, label:has-text("Destination") ~ input').first();
  61  |     if (await destInput.isVisible()) {
  62  |       await destInput.fill('Tokyo, Japan');
  63  |       await expect(destInput).toHaveValue('Tokyo, Japan');
  64  |     }
  65  |   });
  66  | 
  67  |   test('should allow adjusting group composition', async ({ page }) => {
  68  |     // Find adults number input
  69  |     const adultsInput = page.locator('input[type="number"]').first();
  70  |     if (await adultsInput.isVisible()) {
  71  |       await adultsInput.fill('3');
  72  |       await expect(adultsInput).toHaveValue('3');
  73  |     }
  74  |   });
  75  | 
  76  |   test('should toggle self-drive checkbox', async ({ page }) => {
  77  |     const selfDriveCheckbox = page.locator('input[type="checkbox"]').first();
  78  |     if (await selfDriveCheckbox.isVisible()) {
  79  |       const initialState = await selfDriveCheckbox.isChecked();
  80  |       await selfDriveCheckbox.click();
  81  |       const newState = await selfDriveCheckbox.isChecked();
  82  |       expect(newState).not.toBe(initialState);
  83  |     }
  84  |   });
  85  | });
  86  | 
  87  | test.describe('Traveler\'s Desk — Persona Selection', () => {
  88  |   test.beforeEach(async ({ page }) => {
  89  |     await page.goto('/desk');
  90  |   });
  91  | 
  92  |   test('should show persona options', async ({ page }) => {
  93  |     // Look for persona buttons or radio options
  94  |     const personaSection = page.locator('text=Persona, text=Style, text=Traveler Type').first();
  95  |     if (await personaSection.isVisible()) {
  96  |       await expect(personaSection).toBeVisible();
  97  |     }
  98  | 
  99  |     // Check for persona option buttons
  100 |     const personaOptions = page.locator('.persona-option, .persona-btn, button:has-text("Family"), button:has-text("Solo"), button:has-text("Business")');
  101 |     const count = await personaOptions.count();
  102 |     expect(count).toBeGreaterThanOrEqual(0); // May be inside an accordion
  103 |   });
  104 | 
  105 |   test('should not change destination when selecting a persona', async ({ page }) => {
  106 |     // Fill in destination first
  107 |     const destInput = page.locator('input[placeholder*="destination" i], input[name="destination"]').first();
  108 |     if (await destInput.isVisible()) {
  109 |       await destInput.fill('Paris, France');
  110 |       
  111 |       // Click a persona option
  112 |       const familyBtn = page.locator('button:has-text("Family"), label:has-text("Family")').first();
  113 |       if (await familyBtn.isVisible()) {
  114 |         await familyBtn.click();
  115 |         
  116 |         // Destination should remain Paris, France (not change to a persona-specific destination)
  117 |         await expect(destInput).toHaveValue('Paris, France');
  118 |       }
  119 |     }
  120 |   });
  121 | });
  122 | 
```