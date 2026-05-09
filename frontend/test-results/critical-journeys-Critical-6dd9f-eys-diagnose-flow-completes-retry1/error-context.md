# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: critical-journeys.spec.ts >> Critical User Journeys >> diagnose flow completes
- Location: e2e\critical-journeys.spec.ts:19:3

# Error details

```
TimeoutError: locator.waitFor: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button:has-text("下一题"), button:has-text("完成诊断")').first() to be visible

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - main [ref=e4]:
    - generic [ref=e5]:
      - generic [ref=e6]:
        - heading "知识诊断" [level=1] [ref=e7]
        - generic [ref=e8]: 第 1 题
      - generic [ref=e9]:
        - paragraph [ref=e10]: 解方程：3(x + 2) - 5 = 2x + 7
        - textbox "输入答案" [ref=e11]:
          - /placeholder: 输入答案...
          - text: "0"
      - button "提交答案" [ref=e12] [cursor=pointer]
  - navigation [ref=e13]:
    - generic [ref=e14]:
      - button "📚 学习" [ref=e15] [cursor=pointer]:
        - generic [ref=e16]: 📚
        - generic [ref=e17]: 学习
      - button "🔍 诊断" [ref=e18] [cursor=pointer]:
        - generic [ref=e19]: 🔍
        - generic [ref=e20]: 诊断
      - button "⭐ 精灵" [ref=e21] [cursor=pointer]:
        - generic [ref=e22]: ⭐
        - generic [ref=e23]: 精灵
      - button "👤 我的" [ref=e24] [cursor=pointer]:
        - generic [ref=e25]: 👤
        - generic [ref=e26]: 我的
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test'
  2  | 
  3  | test.describe('Critical User Journeys', () => {
  4  | 
  5  |   test.beforeEach(async ({ page }) => {
  6  |     // Dismiss onboarding so other pages render their content
  7  |     await page.goto('/')
  8  |     await page.evaluate(() => localStorage.setItem('onboarding_done', '1'))
  9  |   })
  10 | 
  11 |   test('homepage loads and shows onboarding', async ({ page }) => {
  12 |     await page.evaluate(() => localStorage.clear())
  13 |     await page.goto('/')
  14 |     await expect(page.locator('text=欢迎来到数学启明星')).toBeVisible({ timeout: 10000 })
  15 |     await page.click('text=跳过引导')
  16 |     await expect(page.locator('text=数学启明星')).toBeVisible({ timeout: 10000 })
  17 |   })
  18 | 
  19 |   test('diagnose flow completes', async ({ page }) => {
  20 |     await page.goto('/diagnose')
  21 |     await expect(page.locator('text=知识诊断')).toBeVisible({ timeout: 10000 })
  22 |     await page.locator('button:has-text("开始诊断")').click({ force: true })
  23 |     await expect(page.locator('text=提交答案')).toBeVisible({ timeout: 20000 })
  24 |     for (let i = 0; i < 3; i++) {
  25 |       // Check if multiple-choice options exist
  26 |       const options = page.locator('button[class*="rounded-xl"]')
  27 |       const count = await options.count()
  28 |       if (count > 0) {
  29 |         await options.first().click({ force: true })
  30 |       } else {
  31 |         await page.fill('input[type="text"]', '0')
  32 |       }
  33 |       await page.locator('button:has-text("提交答案")').click({ force: true })
  34 |       // Wait for post-submit buttons
  35 |       const postBtn = page.locator('button:has-text("下一题"), button:has-text("完成诊断")').first()
> 36 |       await postBtn.waitFor({ timeout: 15000 })
     |                     ^ TimeoutError: locator.waitFor: Timeout 15000ms exceeded.
  37 |       if (await postBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
  38 |         await postBtn.click({ force: true })
  39 |       }
  40 |     }
  41 |     await expect(page.locator('text=诊断报告')).toBeVisible({ timeout: 20000 })
  42 |   })
  43 | 
  44 |   test('parent dashboard PIN auth and renders', async ({ page }) => {
  45 |     await page.goto('/parent')
  46 |     await expect(page.locator('text=家长看板')).toBeVisible({ timeout: 10000 })
  47 |     await page.fill('input[type="password"]', '1234')
  48 |     await page.click('text=进入看板')
  49 |     await expect(page.locator('text=每周统计')).toBeVisible({ timeout: 15000 })
  50 |     await expect(page.locator('.grid.grid-cols-3 .card').first()).toBeVisible({ timeout: 10000 })
  51 |   })
  52 | 
  53 |   test('quiz page flow with hearts', async ({ page }) => {
  54 |     await page.goto('/quiz')
  55 |     await page.waitForSelector('button:has-text("开始")', { timeout: 15000 })
  56 |     await page.click('button:has-text("开始")')
  57 |     await page.waitForSelector('text=第', { timeout: 20000 })
  58 |     const options = page.locator('button[class*="rounded-xl"]')
  59 |     const count = await options.count()
  60 |     if (count > 0) {
  61 |       await options.first().click()
  62 |     } else {
  63 |       await page.fill('input[type="text"]', '0')
  64 |     }
  65 |     await page.click('text=提交答案')
  66 |     // Wait for post-submit UI: either next/retry/summary button
  67 |     const postSubmitBtn = page.locator('button:has-text("下一题"), button:has-text("再试一次"), button:has-text("查看总结")').first()
  68 |     await postSubmitBtn.waitFor({ timeout: 15000 })
  69 |     await expect(postSubmitBtn).toBeVisible()
  70 |   })
  71 | 
  72 |   test('daily summary page renders from navigation', async ({ page }) => {
  73 |     await page.goto('/daily-summary')
  74 |     await expect(page.locator('text=今日学习总结').or(page.locator('text=数学启明星'))).toBeVisible({ timeout: 3000 })
  75 |   })
  76 | 
  77 | })
  78 | 
```