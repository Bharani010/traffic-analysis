import { test, expect } from '@playwright/test'

test.describe('Smoke Tests', () => {
  test('dashboard loads successfully', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/Traffic Analysis/)
    await expect(page.locator('h1')).toContainText('Traffic Analysis')
  })

  test('displays stat cards', async ({ page }) => {
    await page.goto('/')
    // Verify the stat cards are rendered
    await expect(page.getByText('Total Events')).toBeVisible()
    await expect(page.getByText('Anomalies')).toBeVisible()
    await expect(page.getByText('Open Incidents')).toBeVisible()
    await expect(page.getByText('Uptime')).toBeVisible()
  })
})
