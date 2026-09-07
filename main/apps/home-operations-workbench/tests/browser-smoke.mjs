import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { chromium } from '../../../tools/playwright-smoke/node_modules/playwright/index.mjs';

const baseUrl = process.env.POC_URL ?? 'http://127.0.0.1:8129';
const outputDir = process.env.SCREENSHOT_DIR ?? path.join(os.tmpdir(), 'home-operations-workbench');
await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const errors = [];

function collectErrors(page) {
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(message.text());
  });
  page.on('pageerror', (error) => errors.push(error.message));
}

try {
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  collectErrors(desktop);
  await desktop.goto(baseUrl, { waitUntil: 'networkidle' });
  assert.equal(await desktop.title(), 'Home Operations Workbench');
  assert.match(await desktop.locator('#panel').textContent(), /Load operational evidence/);
  assert.equal(await desktop.getByRole('tab').count(), 5);
  const unlabeledControls = await desktop.evaluate(() => [...document.querySelectorAll('button, input, select, textarea')]
    .filter((control) => {
      const labels = control.labels ? [...control.labels].map((label) => label.textContent).join(' ') : '';
      return !(control.getAttribute('aria-label') || labels || control.textContent || control.getAttribute('placeholder'));
    })
    .map((control) => control.outerHTML));
  assert.deepEqual(unlabeledControls, []);

  await desktop.locator('#evidence-file').setInputFiles({
    name: 'invalid-evidence.json',
    mimeType: 'application/json',
    buffer: Buffer.from('{not valid JSON'),
  });
  await desktop.getByText('The selected file is not valid JSON.').waitFor({ state: 'visible' });

  await desktop.locator('#evidence-file').setInputFiles({
    name: 'windows-health.json', mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify({ collector: 'Windows management workstation', timestamp: new Date().toISOString(), checks: { router: 'pass', homepage: 'fail' } })),
  });
  assert.match(await desktop.locator('#evidence-source').textContent(), /Windows management workstation/);
  assert.match(await desktop.locator('#panel').textContent(), /Homepage HTTPS/);
  await desktop.getByRole('tab', { name: 'Recovery' }).click();
  assert.match(await desktop.locator('#panel').textContent(), /Needs evidence/);
  await desktop.getByRole('tab', { name: 'Today' }).click();

  await desktop.getByRole('button', { name: 'Load demonstration' }).first().click();
  assert.match(await desktop.locator('#evidence-time').textContent(), /2026-09-05/);
  assert.match(await desktop.locator('#panel').textContent(), /Check herb bed moisture/);

  await desktop.getByRole('tab', { name: 'Incidents' }).click();
  assert.match(await desktop.locator('#panel').textContent(), /Possible shared dependencies/);
  assert.match(await desktop.locator('#panel').textContent(), /VM 103/);
  await desktop.getByRole('tab', { name: 'Recovery' }).click();
  assert.match(await desktop.locator('#panel').textContent(), /Backed up, not restore-proven/);
  const emergencyPack = desktop.waitForEvent('download');
  await desktop.getByRole('button', { name: 'Download emergency pack' }).click();
  await emergencyPack;
  await desktop.getByRole('tab', { name: 'Cook' }).click();
  assert.match(await desktop.locator('#panel').textContent(), /Vegetable traybake/);
  await desktop.getByRole('tab', { name: 'Commissioning' }).click();
  assert.match(await desktop.locator('#panel').textContent(), /Visual-only scenarios/);
  await desktop.getByRole('tab', { name: 'Commissioning' }).press('Home');
  assert.equal(await desktop.getByRole('tab', { name: 'Today' }).getAttribute('aria-selected'), 'true');
  await desktop.getByRole('tab', { name: 'Commissioning' }).click();
  await desktop.screenshot({ path: path.join(outputDir, 'desktop.png'), fullPage: true });

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  collectErrors(mobile);
  await mobile.goto(baseUrl, { waitUntil: 'networkidle' });
  await mobile.getByRole('button', { name: 'Load demonstration' }).first().click();
  await mobile.getByRole('tab', { name: 'Recovery' }).click();
  assert.match(await mobile.locator('#panel').textContent(), /Recovery readiness/);
  const overflow = await mobile.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  assert.ok(overflow <= 1, `mobile page overflows by ${overflow}px`);
  await mobile.screenshot({ path: path.join(outputDir, 'mobile.png'), fullPage: true });

  const narrow = await browser.newPage({ viewport: { width: 320, height: 844 } });
  collectErrors(narrow);
  await narrow.goto(baseUrl, { waitUntil: 'networkidle' });
  await narrow.getByRole('button', { name: 'Load demonstration' }).first().click();
  await narrow.getByRole('tab', { name: 'Today' }).click();
  const narrowOverflow = await narrow.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  assert.ok(narrowOverflow <= 1, `320px page overflows by ${narrowOverflow}px`);

  assert.deepEqual(errors, []);
  console.log(`Browser smoke: PASS (${outputDir})`);
} finally {
  await browser.close();
}
