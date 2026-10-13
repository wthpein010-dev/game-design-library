import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('filters, shareable search, empty state, restoration',async({page})=>{
 await page.goto('/');await page.getByLabel('搜索资料').fill('核心循环');
 await expect(page.locator('.resource-row')).not.toHaveCount(0);
 await expect(page).toHaveURL(/q=/);await page.reload();await expect(page.getByLabel('搜索资料')).toHaveValue('核心循环');
 await page.getByLabel('搜索资料').fill('xxxxx-no-resource');await expect(page.getByText('换个关键词试试')).toBeVisible();
 await page.getByLabel('清除搜索').click();await expect(page.locator('.resource-row')).toHaveCount(24);
 await page.getByLabel('语言',{exact:true}).selectOption('en');await expect(page.locator('.resource-row').first()).toContainText('英文');
});
test('study state persists, export and safe merge import',async({page})=>{
 await page.goto('/?id=L01');await page.getByLabel('一个发现、一个疑问，或准备验证的假设').fill('TEST ONLY: a falsifiable design hypothesis');
 await page.getByLabel('阅读状态').selectOption('reading');await page.reload();
 await expect(page.getByLabel('一个发现、一个疑问，或准备验证的假设')).toHaveValue('TEST ONLY: a falsifiable design hypothesis');
 await page.goto('/?view=study');const download=page.waitForEvent('download');await page.getByRole('button',{name:'导出学习记录'}).click();await expect((await download).suggestedFilename()).toBe('game-design-study.json');
 await page.locator('#import-file').setInputFiles({name:'test.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({schema:1,records:{L01:{note:'old',saved:true,status:'done'},V01:{note:'TEST ONLY',saved:true,status:'todo'}}}))});
 await expect(page.getByText('备份已合并，本机已有记录已保留')).toBeVisible();
 await page.goto('/?id=L01');await expect(page.getByLabel('一个发现、一个疑问，或准备验证的假设')).toHaveValue('TEST ONLY: a falsifiable design hypothesis');
});
test('course content and exercise, player loads only on request',async({page})=>{
 await page.goto('/?id=L01');await expect(page.getByRole('heading',{name:'练习与订正',exact:true})).toBeVisible();
 await page.locator('[data-question="0"][data-answer="0"]').click();await expect(page.locator('#answer-0')).toContainText('本题正确');
 await page.goto('/?id=V04');await expect(page.locator('iframe')).toHaveCount(0);
 await page.route('https://player.bilibili.com/**',route=>route.fulfill({body:'<html><body>Player URL test fixture</body></html>',contentType:'text/html'}));
 await page.getByRole('button',{name:/播放 B站视频/}).click();await expect(page.locator('iframe')).toHaveAttribute('src',/page=1&autoplay=0/);
});
test('catalog failure has retry and recovers',async({page})=>{
 await page.route('**/data/catalog.json',route=>route.abort());await page.goto('/');
 await expect(page.getByRole('heading',{name:'资料暂时未能打开'})).toBeVisible();
 await page.unroute('**/data/catalog.json');await page.getByRole('button',{name:'重新加载'}).click();await expect(page.getByLabel('搜索资料')).toBeVisible();
});
test('phone, keyboard and accessibility',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/');await page.getByLabel('搜索资料').waitFor();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
 const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();expect(results.violations).toEqual([]);
 await page.getByLabel('搜索资料').focus();await page.keyboard.type('core');await page.keyboard.press('Tab');await expect(page.getByLabel('清除搜索')).toBeFocused();
 await page.goto('/?view=topics&topic=T09');expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
});
test('two tabs preserve each other records and corrupt storage stays recoverable',async({page,context})=>{
 const other=await context.newPage();await page.goto('/?id=L01');await other.goto('/?id=L02');
 await page.getByLabel('一个发现、一个疑问，或准备验证的假设').fill('TEST ONLY: preserve across tabs');
 await expect(page.locator('#note-status')).toContainText('已保存');
 await other.getByRole('button',{name:'收藏 ☆',exact:true}).click();await expect(other.getByRole('button',{name:'取消收藏',exact:true})).toBeVisible();
 await page.reload();await expect(page.getByLabel('一个发现、一个疑问，或准备验证的假设')).toHaveValue('TEST ONLY: preserve across tabs');
 const raw='{"schema":1,"records":{"L01":{"note":"TEST ONLY: recoverable","status":"old"}}}';
 await page.evaluate(raw=>localStorage.setItem('game-design-library.study.v1',raw),raw);await page.reload();
 await page.getByRole('button',{name:'收藏 ☆',exact:true}).click();await expect(page.locator('#notice')).toContainText('原数据已保留');
 expect(await page.evaluate(()=>localStorage.getItem('game-design-library.study.v1'))).toBe(raw);
});
