# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: critical-journeys.spec.ts >> Critical User Journeys >> quiz page flow with hearts
- Location: e2e\critical-journeys.spec.ts:53:3

# Error details

```
TimeoutError: locator.waitFor: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button:has-text("下一题"), button:has-text("再试一次"), button:has-text("查看总结")').first() to be visible

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - main [ref=e4]:
    - generic [ref=e5]:
      - generic [ref=e6]:
        - button "← 返回" [ref=e7] [cursor=pointer]
        - generic [ref=e8]:
          - 'generic "Sprite: 星尘" [ref=e9]':
            - img [ref=e11]
          - generic [ref=e15]: 星尘
        - generic [ref=e17]:
          - generic [ref=e18]: ❤️
          - generic [ref=e19]: ❤️
          - generic [ref=e20]: ❤️
      - generic [ref=e22]: 第 1 题 · Pythagoras Theorem
      - generic [ref=e23]:
        - generic [ref=e24]:
          - generic [ref=e25]: Lv.1
          - generic [ref=e26]: 提示 0/3
        - paragraph [ref=e27]: In a right triangle, hypotenuse = 13, one leg = 5. Find the other leg.
        - textbox "输入答案" [ref=e28]:
          - /placeholder: 输入答案...
          - text: "0"
      - button "提交答案" [ref=e29] [cursor=pointer]
  - navigation [ref=e30]:
    - generic [ref=e31]:
      - button "📚 学习" [ref=e32] [cursor=pointer]:
        - generic [ref=e33]: 📚
        - generic [ref=e34]: 学习
      - button "🔍 诊断" [ref=e35] [cursor=pointer]:
        - generic [ref=e36]: 🔍
        - generic [ref=e37]: 诊断
      - button "⭐ 精灵" [ref=e38] [cursor=pointer]:
        - generic [ref=e39]: ⭐
        - generic [ref=e40]: 精灵
      - button "👤 我的" [ref=e41] [cursor=pointer]:
        - generic [ref=e42]: 👤
        - generic [ref=e43]: 我的
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
  36 |       await postBtn.waitFor({ timeout: 15000 })
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
> 68 |     await postSubmitBtn.waitFor({ timeout: 15000 })
     |                         ^ TimeoutError: locator.waitFor: Timeout 15000ms exceeded.
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