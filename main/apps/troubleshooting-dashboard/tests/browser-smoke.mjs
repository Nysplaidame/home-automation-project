import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { chromium } from '../../../tools/playwright-smoke/node_modules/playwright/index.mjs';

const baseUrl = process.env.POC_URL ?? 'http://127.0.0.1:8099';
const outputDir = process.env.SCREENSHOT_DIR ?? path.join(os.tmpdir(), 'troubleshooting-dashboard-poc');
const snapshotPath = process.env.SNAPSHOT_PATH;
await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const errors = [];

try {
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  desktop.on('console', (message) => {
    if (message.type() === 'error') errors.push(message.text());
  });
  desktop.on('pageerror', (error) => errors.push(error.message));
  await desktop.goto(baseUrl, { waitUntil: 'networkidle' });
  assert.equal(await desktop.title(), 'Home Operations Troubleshooting');
  assert.equal(await desktop.locator('.symptom-button').count(), 5);
  assert.match(await desktop.locator('#snapshot-time').textContent(), /Not loaded/);
  const unlabeledControls = await desktop.evaluate(() => [...document.querySelectorAll('button, input, select, textarea')]
    .filter((element) => {
      const labels = element.labels ? [...element.labels].map((label) => label.textContent).join(' ') : '';
      return !(element.getAttribute('aria-label') || labels || element.textContent || element.getAttribute('placeholder'));
    })
    .map((element) => element.outerHTML));
  assert.deepEqual(unlabeledControls, []);

  if (snapshotPath) {
    await desktop.locator('#snapshot-file').setInputFiles(snapshotPath);
    assert.doesNotMatch(await desktop.locator('#snapshot-time').textContent(), /Not loaded/);
    assert.doesNotMatch(await desktop.locator('#snapshot-source').textContent(), /not supplied/i);
  } else {
    await desktop.locator('#snapshot-file').setInputFiles({
      name: 'health.json',
      mimeType: 'application/json',
      buffer: Buffer.from(JSON.stringify({
        timestamp: 'Imported smoke snapshot',
        collector: 'Browser smoke collector',
        checks: { router: { status: 'pass', detail: '192.168.10.1:22' }, homepage: 'pass' },
      })),
    });
    assert.match(await desktop.locator('#snapshot-time').textContent(), /Imported smoke snapshot/);
    assert.match(await desktop.locator('#snapshot-source').textContent(), /Browser smoke collector/);
  }

  await desktop.selectOption('#sample-select', 'p1s');
  await desktop.getByRole('button', { name: /P1S telemetry/ }).click();
  assert.match(await desktop.locator('#active-status').textContent(), /Action needed/);
  assert.match(await desktop.locator('#evidence-list').textContent(), /P1S reachable/);
  assert.equal(await desktop.locator('#evidence-list .status-fail').count(), 1);
  assert.equal(await desktop.locator('#dependency-path .status-border-fail').count(), 2);
  assert.equal(await desktop.locator('#dependency-path .status-border-pass').count(), 3);
  assert.match(await desktop.locator('#focus-label').textContent(), /P1S reachable/);
  assert.match(await desktop.locator('.step-context').first().textContent(), /VM 103/);
  await desktop.waitForTimeout(2800);
  await desktop.screenshot({ path: path.join(outputDir, 'desktop.png'), fullPage: true });

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  mobile.on('console', (message) => {
    if (message.type() === 'error') errors.push(message.text());
  });
  mobile.on('pageerror', (error) => errors.push(error.message));
  await mobile.goto(baseUrl, { waitUntil: 'networkidle' });
  await mobile.selectOption('#sample-select', 'backups');
  await mobile.getByRole('button', { name: /Backup freshness/ }).click();
  assert.match(await mobile.locator('#active-status').textContent(), /Action needed/);
  await mobile.waitForTimeout(2800);
  const overflow = await mobile.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  assert.ok(overflow <= 1, `mobile page overflows by ${overflow}px`);
  await mobile.screenshot({ path: path.join(outputDir, 'mobile.png'), fullPage: true });

  assert.deepEqual(errors, []);
  console.log(`Browser smoke: PASS (${outputDir})`);
} finally {
  await browser.close();
}
