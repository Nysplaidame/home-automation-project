import assert from 'node:assert/strict';
import { symptoms } from '../diagnostic-model.js';
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
  await desktop.clock.install({ time: new Date('2026-09-10T12:00:00Z') });
  await desktop.goto(baseUrl, { waitUntil: 'networkidle' });
  assert.equal(await desktop.title(), 'Home Operations Troubleshooting');
  assert.equal(await desktop.locator('.symptom-button').count(), symptoms.length);
  assert.match(await desktop.locator('#snapshot-time').textContent(), /Not loaded/);
  const unlabeledControls = await desktop.evaluate(() => [...document.querySelectorAll('button, input, select, textarea')]
    .filter((element) => {
      const labels = element.labels ? [...element.labels].map((label) => label.textContent).join(' ') : '';
      return !(element.getAttribute('aria-label') || labels || element.textContent || element.getAttribute('placeholder'));
    })
    .map((element) => element.outerHTML));
  assert.deepEqual(unlabeledControls, []);

  assert.match(await desktop.locator('#symptom-heading').textContent(), /1. Choose a problem/);
  await desktop.locator('.collection-help summary').click();
  assert.match(await desktop.locator('.collection-help').textContent(), /health_check.ps1/);
  await desktop.locator('.collection-help summary').click();
  assert.equal(await desktop.locator('.step-body[open]').count(), 1);
  await desktop.locator('.step-heading').nth(1).click();
  assert.equal(await desktop.locator('.step-body[open]').count(), 2);
  assert.ok(await desktop.locator('.interpretation dd').first().evaluate(el => parseFloat(getComputedStyle(el).fontSize)) >= 18);
  assert.ok(await desktop.locator('.evidence-detail').count() === 0);
  if (snapshotPath) {
    await desktop.clock.setSystemTime(new Date());
    await desktop.locator('#snapshot-file').setInputFiles(snapshotPath);
    assert.doesNotMatch(await desktop.locator('#snapshot-time').textContent(), /Not loaded/);
    assert.doesNotMatch(await desktop.locator('#snapshot-source').textContent(), /not supplied/i);
    assert.match(await desktop.locator('#snapshot-age').textContent(), /Recent/);
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

  await desktop.clock.setSystemTime(new Date('2026-09-10T12:00:00Z'));
  await desktop.locator('#snapshot-file').setInputFiles({
    name: 'stale.json', mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify({ timestamp: '2020-01-01T00:00:00Z', checks: { router: 'pass', docker_host: 'pass', homepage: 'pass' } })),
  });
  assert.match(await desktop.locator('#snapshot-age').textContent(), /Stale/);
  assert.match(await desktop.locator('#active-status').textContent(), /Needs evidence/);
  assert.match(await desktop.locator('#evidence-list').textContent(), /Recorded: pass/);
  assert.equal(await desktop.locator('#evidence-list .status-pass').count(), 0);
  await desktop.locator('#snapshot-file').setInputFiles({
    name: 'recent.json', mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify({ timestamp: '2026-09-09T00:00:30Z', checks: { router: 'pass', docker_host: 'pass', homepage: 'pass' } })),
  });
  assert.match(await desktop.locator('#active-status').textContent(), /Healthy/);
  await desktop.locator('#notes').fill('Keep these operator notes');
  await desktop.locator('#notes').focus();
  await desktop.clock.fastForward(61000);
  assert.match(await desktop.locator('#snapshot-age').textContent(), /Stale/);
  assert.match(await desktop.locator('#active-status').textContent(), /Needs evidence/);
  assert.equal(await desktop.locator('#notes').inputValue(), 'Keep these operator notes');
  assert.equal(await desktop.locator('#notes').evaluate(element => element === document.activeElement), true);
  assert.equal(await desktop.locator('.symptom-topline .status-label').count(), 0);
  await desktop.selectOption('#sample-select', 'p1s');
  assert.match(await desktop.locator('#snapshot-age').textContent(), /Example only/);
  await desktop.locator('#route-search').fill('P1S');
  await desktop.getByRole('button', { name: /P1S telemetry/ }).click();
  assert.match(await desktop.locator('#active-status').textContent(), /Action needed/);
  assert.match(await desktop.locator('#expected-state').textContent(), /P1S not commissioned/);
  assert.match(await desktop.locator('#evidence-list').textContent(), /P1S reachable/);
  assert.equal(await desktop.locator('#evidence-list .status-fail').count(), 1);
  assert.equal(await desktop.locator('#dependency-path .status-border-fail').count(), 2);
  assert.equal(await desktop.locator('#dependency-path .status-border-pass').count(), 3);
  assert.match(await desktop.locator('#focus-label').textContent(), /P1S reachable/);
  assert.match(await desktop.locator('.step-context').first().textContent(), /VM 103/);
  await desktop.waitForTimeout(2800);
  await desktop.locator('#load-evidence').scrollIntoViewIfNeeded();
  await desktop.screenshot({ path: path.join(outputDir, 'desktop-top.png') });
  await desktop.locator('.sequence-section').screenshot({ path: path.join(outputDir, 'desktop-checks.png') });
  await desktop.screenshot({ path: path.join(outputDir, 'desktop.png'), fullPage: true });

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  mobile.on('console', (message) => {
    if (message.type() === 'error') errors.push(message.text());
  });
  mobile.on('pageerror', (error) => errors.push(error.message));
  await mobile.goto(baseUrl, { waitUntil: 'networkidle' });
  await mobile.selectOption('#sample-select', 'backups');
  await mobile.locator('#route-search').fill('Backup freshness');
  await mobile.getByRole('button', { name: /Backup freshness/ }).click();
  assert.match(await mobile.locator('#active-status').textContent(), /Action needed/);
  await mobile.waitForTimeout(2800);
  const overflow = await mobile.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  assert.ok(overflow <= 1, `mobile page overflows by ${overflow}px`);
  await mobile.locator('.load-evidence').screenshot({ path: path.join(outputDir, 'mobile-evidence.png') });
  await mobile.locator('.sequence-section').screenshot({ path: path.join(outputDir, 'mobile-checks.png') });
  await mobile.screenshot({ path: path.join(outputDir, 'mobile.png'), fullPage: true });

  await desktop.locator('#route-search').fill('does-not-exist');
  assert.equal(await desktop.locator('.symptom-button').count(), 0);
  assert.match(await desktop.locator('#symptom-list').textContent(), /No matching routes/);
  await desktop.locator('#route-search').fill('');
  await desktop.locator('#route-category').selectOption('Applications and data');
  assert.ok(await desktop.locator('.symptom-button').count() > 3);
  await desktop.locator('#route-category').selectOption('');
  // Every route is selectable, has evidence/steps, and retains readable layout.
  for (const symptom of symptoms) {
    await desktop.locator('#route-search').fill(symptom.title);
    await desktop.locator(`[data-route-id="${symptom.id}"]`).click();
    assert.equal(await desktop.locator('#active-title').textContent(), symptom.title);
    assert.equal(await desktop.locator('.diagnostic-step').count(), symptom.steps.length);
    assert.equal(await desktop.locator('.evidence-row').count(), symptom.checks.length);
  }
  await mobile.locator('#route-search').fill('Downloads');
  await mobile.locator('[data-route-id="downloads"]').click();
  assert.match(await mobile.locator('#active-status').textContent(), /Needs evidence/);
  assert.ok(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await mobile.locator('.sequence-section').screenshot({ path: path.join(outputDir, 'mobile-downloads.png') });
  assert.deepEqual(errors, []);
  console.log(`Browser smoke: PASS (${outputDir})`);
} finally {
  await browser.close();
}
