import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { chromium } from '../../../tools/playwright-smoke/node_modules/playwright/index.mjs';
import { adaptGrocyOverview } from '../grocy-adapter.js';

const root = fileURLToPath(new URL('../', import.meta.url));
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };
const server = createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const target = path.resolve(root, '.' + (pathname === '/' ? '/index.html' : pathname));
    const relative = path.relative(root, target);
    if (relative.startsWith('..') || path.isAbsolute(relative)) {
      response.writeHead(403).end(); return;
    }
    response.writeHead(200, { 'Content-Type': mime[path.extname(target)] ?? 'application/octet-stream' });
    response.end(await readFile(target));
  } catch { response.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
let browser;
try {
  browser = await chromium.launch({ headless: true });
  const errors = [];
  for (const viewport of [{ width: 1440, height: 1000 }, { width: 320, height: 760 }]) {
    const page = await browser.newPage({ viewport });
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`http://127.0.0.1:${server.address().port}/`);
    await page.locator('#evidence-file').setInputFiles(path.join(root, 'evidence/recovery-2026-10-02.json'));
    await page.locator('#tab-recovery').click();
    assert.equal(await page.locator('.recovery-card').count(), 7);
    assert.match(await page.locator('#evidence-source').textContent(), /historical evidence/);
    assert.match(await page.locator('#panel').textContent(), /NIC-free temporary VM9102 boot/);
    assert.doesNotMatch(await page.locator('#panel').textContent(), /Recovery proved/i);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    const snapshot = { schemaVersion: 'grocy-overview/1.0', status: 'available',
      observedAt: new Date().toISOString(), ownerUrl: 'https://grocy.example.test/',
      overview: { stock: [{ name: 'Synthetic oats', amount: 2, location: 'Demo pantry', best_before_date: '2026-10-05' }],
        shopping_list: [{ name: 'Synthetic apples', amount: 1, note: 'PRIVATE-NOTE-MARKER' }] } };
    for (const [status, observedAt, expected] of [
      ['available', snapshot.observedAt, 'Healthy'],
      ['available', '2026-01-01T00:00:00Z', 'Stale evidence'],
      ['unavailable', snapshot.observedAt, 'Grocy source unavailable'],
    ]) {
      const workbook = adaptGrocyOverview({ ...snapshot, status, observedAt });
      await page.locator('#evidence-file').setInputFiles({ name: 'synthetic-overview.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(workbook)) });
      await page.locator('#tab-today').click();
      const content = await page.locator('#panel').textContent();
      assert.match(content, new RegExp(expected));
      assert.doesNotMatch(content, /PRIVATE-|Use by:/);
      if (status === 'available') {
        assert.match(content, /Synthetic oats/); assert.match(content, /Best before: 2026-10-05/);
        assert.equal(await page.locator('#panel a[href="https://grocy.example.test/"]').count(), 3);
      } else assert.doesNotMatch(content, /Synthetic oats/);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      if (process.env.WORKBENCH_SCREENSHOT && viewport.width === 320 && expected === 'Healthy') {
        await page.screenshot({ path: process.env.WORKBENCH_SCREENSHOT, fullPage: true });
      }
      // The same saved source can go straight through the picker; BOM exports work too.
      await page.locator('#evidence-file').setInputFiles({ name: 'synthetic-source.json', mimeType: 'application/json',
        buffer: Buffer.from('\uFEFF' + JSON.stringify({ ...snapshot, status, observedAt })) });
      assert.match(await page.locator('#panel').textContent(), new RegExp(expected));
      assert.doesNotMatch(await page.locator('#panel').textContent(), /PRIVATE-|Use by:/);
      assert.match(await page.locator('#evidence-source').textContent(), /Grocy.*offline import/);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    }
    const previous = await page.locator('#panel').textContent();
    for (const [buffer, message] of [[Buffer.from('{ PRIVATE-MALFORMED'), 'not valid JSON'],
      [Buffer.from(JSON.stringify({ ...snapshot, overview: { stock: {}, shopping_list: [] } })), 'could not be imported'],
      [Buffer.from(JSON.stringify({ schemaVersion: 'grocy-overview/9.0' })), 'supported Home Operations evidence schema'],
      [Buffer.alloc(512 * 1024 + 1, 32), 'limited to 512 KB']]) {
      await page.locator('#evidence-file').setInputFiles({ name: 'invalid-source.json', mimeType: 'application/json', buffer });
      await page.waitForFunction(expected => document.querySelector('#live-message').textContent.includes(expected), message);
      await page.locator('#live-message.error').waitFor();
      assert.doesNotMatch(await page.locator('#live-message').textContent(), /PRIVATE/);
      assert.equal(await page.locator('#panel').textContent(), previous);
      assert.equal(await page.locator('#evidence-file').inputValue(), '');
    }
    await page.locator('#clear-evidence').click();
    assert.match(await page.locator('#panel').textContent(), /Load operational evidence/);
    assert.doesNotMatch(await page.locator('#evidence-source').textContent(), /Grocy/);
    await page.close();
  }
  assert.deepEqual(errors, []);
  console.log('PASS: recovery scope, converted/direct BOM Grocy imports and safe error/clear behavior on desktop/320px.');
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
