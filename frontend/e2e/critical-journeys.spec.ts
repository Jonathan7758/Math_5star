import { test, expect } from '@playwright/test'

test.describe('Critical User Journeys', () => {

  test('homepage loads and shows onboarding', async ({ page }) => {
    await page.evaluate(() => localStorage.clear())
    await page.goto('/')
    await expect(page.locator('text=欢迎来到数学启明星')).toBeVisible()
    await page.click('text=跳过引导')
    await expect(page.locator('text=数学启明星')).toBeVisible()
  })

  test('diagnose flow completes', async ({ page }) => {
    await page.goto('/')
    await page.click('text=开始诊断')
    await expect(page.locator('text=知识诊断')).toBeVisible()
    await page.click('text=开始诊断')
    for (let i = 0; i < 5; i++) {
      await page.waitForSelector('text=第')
      const options = page.locator('button[class*="rounded-xl"]')
      const count = await options.count()
      if (count > 0) {
        await options.first().click()
      } else {
        const input = page.locator('input[type="text"]')
        await input.fill('0')
      }
      await page.click('text=提交答案')
      await page.waitForSelector('button')
      const nextBtn = page.locator('button:has-text("下一题")')
      const finishBtn = page.locator('button:has-text("完成诊断")')
      if (await nextBtn.isVisible()) {
        await nextBtn.click()
      } else if (await finishBtn.isVisible()) {
        await finishBtn.click()
        break
      }
    }
    await expect(page.locator('text=诊断报告')).toBeVisible()
  })

  test('parent dashboard PIN auth and renders', async ({ page }) => {
    await page.goto('/parent')
    await expect(page.locator('text=家长看板')).toBeVisible()
    await page.fill('input[type="password"]', '1234')
    await page.click('text=进入看板')
    await expect(page.locator('text=已掌握')).toBeVisible({ timeout: 5000 })
    await expect(page.locator('text=每周统计')).toBeVisible()
  })

  test('quiz page flow with hearts', async ({ page }) => {
    await page.goto('/quiz')
    await page.click('text=开始')
    await page.waitForSelector('text=第')
    const options = page.locator('button[class*="rounded-xl"]')
    const count = await options.count()
    if (count > 0) {
      await options.first().click()
    } else {
      await page.fill('input[type="text"]', '0')
    }
    await page.click('text=提交答案')
    await page.waitForTimeout(500)
    await expect(page.locator('text=下一题').or(page.locator('text=再试一次')).or(page.locator('text=查看总结'))).toBeVisible()
  })

  test('daily summary page renders from navigation', async ({ page }) => {
    await page.goto('/')
    await page.evaluate(() => {
      localStorage.setItem('onboarding_done', '1')
    })
    await page.goto('/daily-summary')
    await expect(page.locator('text=今日学习总结').or(page.locator('text=数学启明星'))).toBeVisible({ timeout: 3000 })
  })

})
