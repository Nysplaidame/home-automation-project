import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { chromium } from '../../../tools/playwright-smoke/node_modules/playwright/index.mjs';
import { diagrams } from '../dist/diagram-data.js';

const root = fileURLToPath(new URL('../dist/', import.meta.url));
const diagramRoot = fileURLToPath(new URL('../../../docs/diagrams/', import.meta.url));
const output = process.env.DIAGRAM_SCREENSHOTS || path.join(os.tmpdir(), 'mermaid-diagram-review');
await mkdir(output, { recursive: true });
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };
const server = createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const target = path.resolve(root, '.' + (pathname === '/' ? '/index.html' : pathname));
    if (!target.startsWith(root)) { response.writeHead(403).end(); return; }
    const body = await readFile(target);
    response.writeHead(200, { 'Content-Type': mime[path.extname(target)] || 'application/octet-stream' });
    response.end(body);
  } catch { response.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const browser = await chromium.launch({ headless: true });
const results = [];
try {
  const page = await browser.newPage({ viewport: { width: 1600, height: 1100 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  for (const diagram of diagrams) {
    const source = await readFile(path.join(diagramRoot, diagram.path), 'utf8');
    assert.equal(source.replaceAll('\r\n', '\n').trim(), diagram.source.replaceAll('\r\n', '\n').trim(), `Generated source differs: ${diagram.id}`);
    await page.goto(`http://127.0.0.1:${server.address().port}/?diagram=${diagram.id}`);
    await page.waitForFunction(() => document.querySelector('#diagram-canvas svg') && document.querySelector('#render-status').hidden);
    await page.screenshot({ path: path.join(output, `${diagram.id}.png`), fullPage: true });
    results.push(await page.evaluate(id => {
      const svg = document.querySelector('#diagram-canvas svg');
      const viewBox = svg.viewBox.baseVal;
      return { id, width: Math.round(viewBox.width), height: Math.round(viewBox.height), zoom: document.querySelector('#zoom-level').textContent, nodes: svg.querySelectorAll('.node').length, edges: svg.querySelectorAll('.edgePath, .flowchart-link').length };
    }, diagram.id));
  }
  await page.setViewportSize({ width: 390, height: 844 });
  for (const id of ['current-master-architecture', 'vlan_architecture_clean', 'docker-host-service-placement']) {
    await page.goto(`http://127.0.0.1:${server.address().port}/?diagram=${id}`);
    await page.waitForFunction(() => document.querySelector('#diagram-canvas svg') && document.querySelector('#render-status').hidden);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Mobile page overflow: ${id}`);
    await page.locator('[data-view-action="actual"]').click();
    assert.equal(await page.locator('#zoom-level').textContent(), '100%');
    await page.locator('[data-view-action="zoom-in"]').click();
    assert.ok(parseInt(await page.locator('#zoom-level').textContent()) > 100);
    await page.locator('[data-view-action="fit"]').click();
    assert.ok(parseInt(await page.locator('#zoom-level').textContent()) < 100);
    await page.screenshot({ path: path.join(output, `${id}-mobile.png`), fullPage: true });
  }
  assert.deepEqual(errors, []);
  await writeFile(path.join(output, 'dimensions.json'), JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results));
  console.log(`Screenshots: ${output}`);
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
}
