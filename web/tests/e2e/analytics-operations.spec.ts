import { test, expect } from '@playwright/test'

const WEB = process.env.WEB_URL || 'http://localhost:3000'

test.describe('Analytics and Operations dashboards', () => {
  test('Analytics summary shows key KPIs', async ({ page }) => {
    await page.goto(`${WEB}/analytics`)
    await expect(page.getByText('Analytics & Business Intelligence')).toBeVisible()
    await expect(page.getByText('Risk Model Accuracy')).toBeVisible()
    await expect(page.getByText('Beneficiaries')).toBeVisible()
  })

  test('Operations shows live service status and stats', async ({ page }) => {
    await page.goto(`${WEB}/operations`)
    await expect(page.getByText('DSRS Operations Center')).toBeVisible()
    await expect(page.getByText('SERVICE STATUS')).toBeVisible()
  })
})

