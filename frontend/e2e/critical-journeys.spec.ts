import { test, expect } from '@playwright/test'

test.describe('Critical User Journeys', () => {

  test.beforeEach(async ({ page }) => {
    // Dismiss onboarding so other pages render their content
    await page.goto('/')
    await page.evaluate(() => localStorage.setItem('onboarding_done', '1'))
  })

  test('homepage loads and shows onboarding', async ({ page }) => {
    await page.evaluate(() => localStorage.clear())
    await page.goto('/')
    await expect(page.locator('text=欢迎来到数学启明星')).toBeVisible({ timeout: 10000 })
    await page.click('text=跳过引导')
    await expect(page.locator('text=数学启明星')).toBeVisible({ timeout: 10000 })
  })

  test('diagnose flow completes', async ({ page }) => {
    await page.goto('/diagnose')
    await expect(page.locator('text=知识诊断')).toBeVisible({ timeout: 10000 })
    await page.locator('button:has-text("开始诊断")').click({ force: true })
    await expect(page.locator('text=提交答案')).toBeVisible({ timeout: 20000 })
    for (let i = 0; i < 3; i++) {
      // Check if multiple-choice options exist
      const options = page.locator('button[class*="rounded-xl"]')
      const count = await options.count()
      if (count > 0) {
        await options.first().click({ force: true })
      } else {
        await page.fill('input[type="text"]', '0')
      }
      await page.locator('button:has-text("提交答案")').click({ force: true })
      // Wait for post-submit buttons
      const postBtn = page.locator('button:has-text("下一题"), button:has-text("完成诊断")').first()
      await postBtn.waitFor({ timeout: 15000 })
      if (await postBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        await postBtn.click({ force: true })
      }
    }
    await expect(page.locator('text=诊断报告')).toBeVisible({ timeout: 20000 })
  })

  test('parent dashboard PIN auth and renders', async ({ page }) => {
    await page.goto('/parent')
    await expect(page.locator('text=家长看板')).toBeVisible({ timeout: 10000 })
    await page.fill('input[type="password"]', '1234')
    await page.click('text=进入看板')
    await expect(page.locator('text=每周统计')).toBeVisible({ timeout: 15000 })
    await expect(page.locator('.grid.grid-cols-3 .card').first()).toBeVisible({ timeout: 10000 })
  })

  test('quiz page flow with hearts', async ({ page }) => {
    await page.goto('/quiz')
    await page.waitForSelector('button:has-text("开始")', { timeout: 15000 })
    await page.click('button:has-text("开始")')
    await page.waitForSelector('text=第', { timeout: 20000 })
    const options = page.locator('button[class*="rounded-xl"]')
    const count = await options.count()
    if (count > 0) {
      await options.first().click()
    } else {
      await page.fill('input[type="text"]', '0')
    }
    await page.click('text=提交答案')
    // Wait for post-submit UI: either next/retry/summary button
    const postSubmitBtn = page.locator('button:has-text("下一题"), button:has-text("再试一次"), button:has-text("查看总结")').first()
    await postSubmitBtn.waitFor({ timeout: 15000 })
    await expect(postSubmitBtn).toBeVisible()
  })

  test('daily summary page renders from navigation', async ({ page }) => {
    await page.goto('/daily-summary')
    await expect(page.locator('text=今日学习总结').or(page.locator('text=数学启明星'))).toBeVisible({ timeout: 3000 })
  })

})
