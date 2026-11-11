// Re-renders the PDF and PNG from alef-investor-one-pager.html.
// Run from this folder: node render.js   (needs Playwright with Chromium)
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const html = 'file://' + path.join(__dirname, 'alef-investor-one-pager.html');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 900, height: 1200 }, deviceScaleFactor: 2 });
  await page.goto(html);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(__dirname, 'alef-investor-one-pager.png'), fullPage: true });
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: path.join(__dirname, 'alef-investor-one-pager.pdf'), width: '8.5in', height: '11in', printBackground: true, preferCSSPageSize: true });
  await browser.close();
})();
