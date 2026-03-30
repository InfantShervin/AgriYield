const { test, expect } = require('@playwright/test');

test.describe('AgriYield AI - End-to-End User Flow', () => {
  test('should successfully predict yield when form is submitted', async ({ page }) => {
    // 1. Visit the application
    await page.goto('http://127.0.0.1:3000');
    
    // 2. Wait for the API status to be "API Online"
    await expect(page.locator('#statusText')).toHaveText('API Online', { timeout: 10000 });

    // 3. Fill the prediction form
    await page.fill('#temperature', '28.5');
    await page.fill('#humidity', '70');
    await page.fill('#precipitation', '125');
    await page.fill('#soil_ph', '6.5');
    await page.fill('#soil_nutrients', '140');
    
    // Set map coordinates manually (or via clicking map, but direct fill is faster for CI)
    await page.fill('#latitude', '11.1271');
    await page.fill('#longitude', '78.6569');
    
    // Select crop
    await page.selectOption('#crop_type', 'rice');

    // 4. Click the Predict Yield button
    await page.click('#predictBtn');

    // 5. Verify the result
    const resultCard = page.locator('#resultCard');
    await expect(resultCard).toBeVisible({ timeout: 10000 });
    
    const yieldVal = page.locator('#yieldValue');
    await expect(yieldVal).not.toBeEmpty();
    
    const statusVal = page.locator('#statusVal');
    await expect(statusVal).toHaveText('SUCCESS');
  });

  test('should update history after prediction', async ({ page }) => {
    await page.goto('http://127.0.0.1:3000');
    
    // Mocking prediction and submitting (repeat previous flow)
    await page.fill('#temperature', '25');
    await page.fill('#humidity', '60');
    await page.fill('#precipitation', '100');
    await page.fill('#soil_ph', '6.0');
    await page.fill('#soil_nutrients', '120');
    
    // Set map coordinates manually
    await page.fill('#latitude', '22');
    await page.fill('#longitude', '78');
    
    // Select crop (Crucial: Required for form submission)
    await page.selectOption('#crop_type', 'maize');

    await page.click('#predictBtn');

    // ⚡ Step 1: Wait for resultCard to appear (Ensures async fetch is done)
    await expect(page.locator('#resultCard')).toBeVisible({ timeout: 10000 });

    // ⚡ Step 2: Check if history table body has rows
    await expect(page.locator('#historyBody tr')).toHaveCount(1);
    
    // Check if global statistic updated
    await expect(page.locator('#totalPredsStat')).toHaveText('1');
  });
});
