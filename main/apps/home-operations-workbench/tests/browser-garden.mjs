import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { chromium } from '../../../tools/playwright-smoke/node_modules/playwright/index.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const output = process.env.SCREENSHOT_DIR ?? path.join(os.tmpdir(), 'workbench-garden-review');
await mkdir(output, { recursive: true });
const server = createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const target = path.resolve(root, '.' + (pathname === '/' ? '/index.html' : pathname));
    if (!target.startsWith(root)) { response.writeHead(403).end(); return; }
    const content = await readFile(target);
    response.writeHead(200, { 'Content-Type': { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' }[path.extname(target)] ?? 'application/octet-stream' });
    response.end(content);
  } catch { response.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const browser = await chromium.launch({ headless: true });
const errors = [];
const upload = async (page, value, bom = false) => {
  await page.locator('#evidence-file').setInputFiles({
    name: 'saved-garden.json', mimeType: 'application/json', buffer: Buffer.from((bom ? '\uFEFF' : '') + JSON.stringify(value)),
  });
  await page.waitForFunction(() => document.querySelector('#evidence-file').files.length === 0);
};
const fixture = () => ({ schemaVersion: 'garden-tasks/1.0', status: 'available', observedAt: new Date().toISOString(),
  ownerUrl: 'https://garden.example.invalid/tasks', tasks: [{ title: 'Water herbs', status: 'pending', due_at: '2026-10-04T13:00:00+01:00', notes: 'PRIVATE-NOTE' }, { title: 'Hidden completed task', status: 'completed' }] });
try {
  for (const width of [1440, 320]) {
    const page = await browser.newPage({ viewport: { width, height: 1000 } });
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    const requests = [];
    page.on('request', request => requests.push(request.url()));
    await page.goto(`http://127.0.0.1:${server.address().port}/`, { waitUntil: 'networkidle' });
    await upload(page, fixture(), true);
    await page.getByText('Water herbs', { exact: true }).waitFor();
    assert.match(await page.locator('#evidence-source').textContent(), /GardenKeeper.*saved tasks/);
    assert.doesNotMatch(await page.locator('#panel').textContent(), /PRIVATE|Hidden completed task/);
    assert.match(await page.locator('#panel').textContent(), /2026-10-04T12:00:00.000Z/);
    assert.match(await page.locator('#panel').textContent(), /No complete-garden or overdue inference/);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    assert.equal(await page.locator('.item-list').first().evaluate(node => getComputedStyle(node).paddingLeft), '0px');
    await page.locator('#live-message').evaluate(node => node.classList.remove('visible'));
    await page.waitForFunction(() => getComputedStyle(document.querySelector('#live-message')).opacity === '0');
    await page.screenshot({ path: path.join(output, `garden-fresh-${width}.png`), fullPage: true });
    await upload(page, { ...fixture(), observedAt: '2020-01-01T00:00:00Z' });
    assert.match(await page.locator('#panel').textContent(), /Stale evidence/);
    await upload(page, { ...fixture(), observedAt: '2099-01-01T00:00:00Z' });
    assert.match(await page.locator('#panel').textContent(), /Needs evidence/);
    await upload(page, { ...fixture(), tasks: [] });
    assert.equal(await page.getByText('Water herbs', { exact: true }).count(), 0);
    assert.match(await page.locator('#panel').textContent(), /0 of 0 pending/);
    await upload(page, { ...fixture(), status: 'unavailable' });
    assert.match(await page.locator('#panel').textContent(), /GardenKeeper source unavailable/);
    await upload(page, { ...fixture(), tasks: [{ status: 'unknown' }] });
    await page.getByText('The evidence file could not be imported.', { exact: true }).waitFor();
    assert.match(await page.locator('#panel').textContent(), /GardenKeeper source unavailable/);
    await page.locator('#evidence-file').setInputFiles({ name: 'oversize.json', mimeType: 'application/json', buffer: Buffer.alloc(512 * 1024 + 1, 32) });
    await page.getByText('Evidence imports are limited to 512 KB.', { exact: true }).waitFor();
    assert.match(await page.locator('#panel').textContent(), /GardenKeeper source unavailable/);
    const mealPlan = () => ({ schemaVersion: 'mealie-plan/1.0', status: 'available', observedAt: new Date().toISOString(),
      planDate: '2026-10-04', ownerUrl: 'https://mealie.example.invalid/', plan: { items: [
        { date: '2026-10-04', entryType: 'dinner', title: '', text: 'PRIVATE-MEAL-NOTE', recipe: { name: 'Bean stew', slug: 'PRIVATE-SLUG' } },
        { date: '2026-10-05', entryType: 'lunch', title: 'Other date meal' }] } });
    await upload(page, mealPlan(), true);
    assert.match(await page.locator('#evidence-source').textContent(), /Mealie.*saved meal plan/);
    assert.equal(await page.getByText('Bean stew', { exact: true }).count(), 1);
    assert.match(await page.locator('#panel').textContent(), /Planned: 2026-10-04/);
    assert.match(await page.locator('#panel').textContent(), /ingredient availability and food safety unknown/);
    assert.match(await page.locator('#panel').textContent(), /Selected date is explicit, not inferred as today/);
    assert.doesNotMatch(await page.locator('#panel').textContent(), /PRIVATE|Other date meal/);
    assert.equal(await page.locator('.area-card').filter({ has: page.getByRole('heading', { name: 'Meals', exact: true }) }).getByRole('link').getAttribute('href'), 'https://mealie.example.invalid/');
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.locator('#live-message').evaluate(node => { node.classList.remove('visible', 'error'); node.textContent = ''; });
    await page.waitForFunction(() => getComputedStyle(document.querySelector('#live-message')).opacity === '0');
    await page.screenshot({ path: path.join(output, `mealie-fresh-${width}.png`), fullPage: true });
    await upload(page, { ...mealPlan(), observedAt: '2020-01-01T00:00:00Z' });
    assert.match(await page.locator('#panel').textContent(), /Stale evidence/);
    await upload(page, { ...mealPlan(), observedAt: '2099-01-01T00:00:00Z' });
    assert.match(await page.locator('#panel').textContent(), /Needs evidence/);
    await upload(page, { ...mealPlan(), planDate: '2026-10-06' });
    assert.equal(await page.getByText('Bean stew', { exact: true }).count(), 0);
    assert.match(await page.locator('#panel').textContent(), /0 of 0 matching entries/);
    await upload(page, { ...mealPlan(), status: 'unavailable' });
    assert.match(await page.locator('#panel').textContent(), /Mealie source unavailable/);
    await upload(page, { ...mealPlan(), planDate: '2026-02-29' });
    assert.match(await page.locator('#live-message').textContent(), /could not be imported/);
    assert.match(await page.locator('#panel').textContent(), /Mealie source unavailable/);
    const household = () => ({ schemaVersion: 'household-sources/1.0', sources: [fixture(),
      { schemaVersion: 'grocy-overview/1.0', status: 'available', observedAt: '2020-01-01T00:00:00Z',
        overview: { stock: [{ name: 'Beans', amount: 2, best_before_date: '2026-10-10' }], shopping_list: [{ name: 'Rice', amount: 1, note: 'PRIVATE-SHOPPING' }] } }, mealPlan()] });
    await upload(page, household(), true);
    assert.match(await page.locator('#evidence-source').textContent(), /Household.*three saved sources/);
    for (const name of ['Water herbs', 'Beans', 'Bean stew', 'Shopping: Rice']) assert.equal(await page.getByText(name, { exact: true }).count(), 1);
    const area = name => page.locator('.area-card').filter({ has: page.getByRole('heading', { name, exact: true }) });
    assert.match(await area('Food to use').textContent(), /Stale evidence/);
    assert.match(await area('Garden').textContent(), /Needs review/);
    assert.match(await area('Meals').textContent(), /Needs review/);
    assert.match(await area('Operations').textContent(), /GardenKeeper saved task selection/);
    assert.match(await area('Operations').textContent(), /Grocy saved overview/);
    assert.match(await area('Operations').textContent(), /Mealie saved selection/);
    assert.doesNotMatch(await page.locator('#panel').textContent(), /PRIVATE/);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.locator('#live-message').evaluate(node => { node.classList.remove('visible', 'error'); node.textContent = ''; });
    await page.waitForFunction(() => getComputedStyle(document.querySelector('#live-message')).opacity === '0');
    await page.screenshot({ path: path.join(output, `household-mixed-${width}.png`), fullPage: true });
    const unavailableBundle = household();
    unavailableBundle.sources[0].status = 'unavailable';
    await upload(page, unavailableBundle);
    assert.equal(await page.getByText('Water herbs', { exact: true }).count(), 0);
    assert.match(await area('Operations').textContent(), /GardenKeeper source unavailable/);
    assert.equal(await page.getByText('Bean stew', { exact: true }).count(), 1);
    const brokenBundle = household();
    brokenBundle.sources[1].overview.stock = [null];
    await upload(page, brokenBundle);
    assert.match(await page.locator('#live-message').textContent(), /could not be imported/);
    assert.match(await area('Operations').textContent(), /GardenKeeper source unavailable/);
    assert.equal(await page.getByText('Water herbs', { exact: true }).count(), 0);
    const cappedBundle = household();
    cappedBundle.sources[1].overview.shopping_list = Array.from({ length: 60 }, (_, index) => ({ name: `Item ${index}`, amount: 1 }));
    await upload(page, cappedBundle);
    assert.equal(await area('Operations').locator('.item-row').count(), 50);
    assert.match(await area('Operations').textContent(), /47 of 50 selected rows/);
    assert.match(await area('Operations').textContent(), /Mealie saved selection/);
    const training = () => ({ schemaVersion: 'recomp-plan/1.0', status: 'available', observedAt: new Date().toISOString(), planDate: '2026-10-04',
      ownerUrl: 'https://recomp.example.invalid/', routines: { items: [
        { id: 'private-id', name: 'Sunday routine', scheduleDays: [6], exercises: [{ discomfort: 'PRIVATE-HEALTH' }] },
        { id: 'monday', name: 'Monday routine', scheduleDays: [0] }], scheduleOverrides: {} } });
    await upload(page, training(), true);
    assert.match(await page.locator('#evidence-source').textContent(), /Recomp.*saved routine plan/);
    assert.equal(await page.getByText('Sunday routine', { exact: true }).count(), 1);
    assert.match(await area('Training').textContent(), /completion and readiness unknown/);
    assert.doesNotMatch(await page.locator('#panel').textContent(), /PRIVATE|Monday routine/);
    const moved = training();
    moved.routines.scheduleOverrides = { '2026-10-04|private-id': '2026-10-05', '2026-10-05|monday': '2026-10-04' };
    await upload(page, moved);
    assert.equal(await page.getByText('Sunday routine', { exact: true }).count(), 0);
    assert.equal(await page.getByText('Monday routine', { exact: true }).count(), 1);
    assert.match(await area('Training').textContent(), /Moved from 2026-10-05/);
    await upload(page, { ...training(), status: 'unavailable' });
    assert.equal(await page.getByText('Sunday routine', { exact: true }).count(), 0);
    assert.match(await area('Operations').textContent(), /Recomp source unavailable/);
    await upload(page, { ...training(), observedAt: '2099-01-01T00:00:00Z' });
    assert.match(await area('Training').textContent(), /Needs evidence/);
    const four = { schemaVersion: 'household-sources/1.1', sources: [...household().sources, { ...training(), observedAt: '2020-01-01T00:00:00Z' }] };
    await upload(page, four);
    assert.match(await page.locator('#evidence-source').textContent(), /four saved sources/);
    for (const name of ['Water herbs', 'Beans', 'Bean stew', 'Sunday routine']) assert.equal(await page.getByText(name, { exact: true }).count(), 1);
    assert.match(await area('Training').textContent(), /Stale evidence/);
    assert.match(await area('Meals').textContent(), /Needs review/);
    assert.doesNotMatch(await page.locator('#panel').textContent(), /PRIVATE/);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.locator('#live-message').evaluate(node => { node.classList.remove('visible', 'error'); node.textContent = ''; });
    await page.waitForFunction(() => getComputedStyle(document.querySelector('#live-message')).opacity === '0');
    await page.screenshot({ path: path.join(output, `household-four-${width}.png`), fullPage: true });
    await upload(page, { ...four, sources: four.sources.slice(0, 3) });
    assert.match(await page.locator('#live-message').textContent(), /could not be imported/);
    assert.equal(await page.getByText('Sunday routine', { exact: true }).count(), 1);
    // Hold file reads until after competing user actions, without timing races.
    await page.evaluate(() => {
      const original = File.prototype.text;
      File.prototype.text = function () {
        if (!this.name.startsWith('delayed-')) return original.call(this);
        const file = this;
        return new Promise((resolve, reject) => {
          window.delayedRead = { release: async (fail = false) => {
            if (fail) reject(new Error('Obsolete read failure'));
            else resolve(await original.call(file));
          } };
        });
      };
    });
    const delayed = async () => {
      await page.evaluate(() => { window.delayedRead = null; });
      await page.locator('#evidence-file').setInputFiles({ name: 'delayed-old.json', mimeType: 'application/json',
        buffer: Buffer.from(JSON.stringify({ ...fixture(), tasks: [{ title: 'Obsolete task', status: 'pending' }] })) });
      await page.waitForFunction(() => Boolean(window.delayedRead));
    };
    const release = async (fail = false) => page.evaluate(async fail => {
      await window.delayedRead.release(fail);
      await new Promise(resolve => setTimeout(resolve, 0));
    }, fail);
    await delayed();
    await page.getByRole('button', { name: 'Clear', exact: true }).click();
    await release();
    assert.match(await page.locator('#panel').textContent(), /Load operational evidence/);
    assert.match(await page.locator('#live-message').textContent(), /cleared/);
    await delayed();
    await page.locator('#load-demo').click();
    const demoSource = await page.locator('#evidence-source').textContent();
    await release(true);
    assert.equal(await page.locator('#evidence-source').textContent(), demoSource);
    assert.match(await page.locator('#live-message').textContent(), /Demonstration evidence loaded/);
    await delayed();
    await upload(page, fixture());
    await release();
    assert.match(await page.locator('#panel').textContent(), /Water herbs/);
    assert.doesNotMatch(await page.locator('#panel').textContent(), /Obsolete task/);
    await delayed();
    await upload(page, { ...fixture(), tasks: [null] });
    await release();
    assert.match(await page.locator('#panel').textContent(), /Water herbs/);
    assert.match(await page.locator('#live-message').textContent(), /could not be imported/);
    await delayed();
    await page.locator('#evidence-file').setInputFiles({ name: 'oversize.json', mimeType: 'application/json', buffer: Buffer.alloc(512 * 1024 + 1, 32) });
    await release();
    assert.match(await page.locator('#panel').textContent(), /Water herbs/);
    assert.match(await page.locator('#live-message').textContent(), /limited to 512 KB/);
    // Strict health times must remain unknown through the real picker and recovery UI.
    for (const timestamp of ['2026-10-03T24:00:00Z', new Date(Date.now() + 60000).toISOString(), '2026-10-04T12:00:00+15:00']) {
      await upload(page, { collector: 'Proxmox host', timestamp, checks: { ct111_root: 'pass', backup_vm100: 'pass' } });
      assert.equal(await page.locator('#healthy-count').textContent(), '0');
      assert.equal(await page.locator('#unknown-count').textContent(), '8');
      assert.match(await page.locator('#panel').textContent(), /Observation time is missing, ambiguous or in the future/);
      await page.getByRole('tab', { name: 'Recovery', exact: true }).click();
      assert.doesNotMatch(await page.locator('#panel').textContent(), /Backed up, not restore-proven/);
      await page.getByRole('tab', { name: 'Today', exact: true }).click();
    }
    const timestamp = new Date(Date.now() - 1000).toISOString().replace(/Z$/, '456Z');
    await upload(page, { collector: 'Windows management workstation', timestamp, checks: { router: 'pass' } });
    assert.equal(await page.locator('#healthy-count').textContent(), '1');
    assert.equal(await page.locator('#unknown-count').textContent(), '12');
    assert.equal(await page.locator('[aria-label="Dependency evidence summary"]').count(), 1);
    assert.match(await page.locator('#healthy-count').locator('..').textContent(), /Healthy dependencies/);
    await page.locator('#live-message').evaluate(node => node.classList.remove('visible'));
    await page.waitForFunction(() => getComputedStyle(document.querySelector('#live-message')).opacity === '0');
    await page.screenshot({ path: path.join(output, `import-state-${width}.png`), fullPage: true });
    await page.getByRole('button', { name: 'Clear', exact: true }).click();
    assert.match(await page.locator('#panel').textContent(), /Load operational evidence/);
    assert.ok(requests.every(url => url.startsWith(`http://127.0.0.1:${server.address().port}/`)), 'no external source requests');
    await page.close();
  }
  assert.deepEqual(errors, []);
  if (process.argv.includes('--regression')) {
    for (const script of ['browser-smoke.mjs', 'browser-recovery.mjs']) {
      await new Promise((resolve, reject) => {
        const child = spawn(process.execPath, [path.join(root, 'tests', script)], {
          env: { ...process.env, POC_URL: `http://127.0.0.1:${server.address().port}` }, stdio: 'inherit',
        });
        child.on('error', reject);
        child.on('exit', code => code === 0 ? resolve() : reject(new Error(`${script} failed (${code})`)));
      });
    }
  }
  console.log('Household/Recomp/Garden/Mealie imports pass at1440/320px: BOM, fresh/stale/future, empty/unavailable, errors, oversize, Clear, overlapping reads, strict health/recovery times and no external requests.');
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
}
