import assert from 'node:assert/strict';
import test from 'node:test';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { adaptGrocyOverview } from '../grocy-adapter.js';
import { normalizeWorkbook } from '../models.js';

const now = '2026-10-02T12:00:00Z';
function fixture() {
  return { schemaVersion: 'grocy-overview/1.0', status: 'available', observedAt: now,
    ownerUrl: 'https://grocy.example.test/', overview: {
      stock: [{ name: 'Synthetic oats', amount: 2, location: 'Demo pantry', best_before_date: '2026-10-05' }],
      shopping_list: [{ name: 'Synthetic apples', amount: 1, note: 'PRIVATE-NOTE-MARKER' }],
    }, token: 'PRIVATE-TOKEN-MARKER' };
}
test('saved rows retain quantities, scope and best-before without use-by or private payload', () => {
  const raw = adaptGrocyOverview(fixture(), { now });
  const book = normalizeWorkbook(raw);
  assert.equal(book.today.food[0].status, 'healthy');
  assert.equal(book.today.food[0].quantity, '2 (source units)');
  assert.equal(book.today.food[0].expires, '');
  assert.match(book.today.food[0].detail, /Best before: 2026-10-05/);
  assert.match(raw.today.operations[0].detail, /do not establish complete inventory/);
  assert.doesNotMatch(JSON.stringify(raw), /PRIVATE-|token|note/);
  assert.equal(book.today.operations[1].title, 'Shopping: Synthetic apples');
});
test('empty, unavailable and malformed observations never invent inventory', () => {
  const empty = fixture(); empty.overview.stock = []; empty.overview.shopping_list = [];
  assert.equal(adaptGrocyOverview(empty, { now }).today.food.length, 0);
  const unavailable = { ...fixture(), status: 'unavailable' };
  assert.equal(adaptGrocyOverview(unavailable, { now }).today.food.length, 0);
  assert.equal(adaptGrocyOverview(unavailable, { now }).today.operations[0].status, 'unknown');
  for (const observedAt of [undefined, '2026-10-02T12:00:00', '2026-02-30T12:00:00Z', '2026-10-02T12:00:01Z', '2026-10-01T24:00:00Z', '2026-10-02T12:00:00+15:00']) {
    assert.equal(adaptGrocyOverview({ ...fixture(), observedAt }, { now }).today.food[0].status, 'unknown');
  }
  assert.equal(adaptGrocyOverview({ ...fixture(), observedAt: '2026-09-01T12:00:00Z' }, { now }).today.food[0].status, 'stale');
});
test('bounds, sensitive labels, unsafe links and malformed values are handled at import', () => {
  const value = fixture(); value.overview.stock[0] = { name: 'api key PRIVATE', amount: Infinity, location: 'password PRIVATE', best_before_date: '2026-02-30' };
  for (const ownerUrl of ['javascript:alert(1)', 'https://user:pass@example.test/', 'https://example.test/?token=PRIVATE']) {
    const item = adaptGrocyOverview({ ...value, ownerUrl }, { now }).today.food[0];
    assert.equal(item.ownerUrl, ''); assert.equal(item.quantity, 'Quantity unknown');
    assert.doesNotMatch(JSON.stringify(item), /PRIVATE/);
  }
  value.overview.stock = Array.from({ length: 80 }, () => ({ name: 'Synthetic item' }));
  assert.equal(adaptGrocyOverview(value, { now }).today.food.length, 50);
  for (const stock of [null, {}, [null], Array(5001).fill({})]) {
    assert.throws(() => adaptGrocyOverview({ ...fixture(), overview: { stock, shopping_list: [] } }, { now }));
  }
  assert.throws(() => adaptGrocyOverview({ ...fixture(), schemaVersion: 'wrong' }, { now }));
});
test('CLI refuses overwrite and malformed input without printing private payload', async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), 'grocy-adapter-'));
  try {
    const input = path.join(root, 'input.json'), output = path.join(root, 'output.json');
    const cli = new URL('../import-grocy.mjs', import.meta.url);
    await writeFile(input, JSON.stringify(fixture()));
    const run = () => spawnSync(process.execPath, [fileURLToPath(cli), input, output], { encoding: 'utf8' });
    assert.equal(run().status, 0);
    const saved = await readFile(output, 'utf8');
    assert.notEqual(run().status, 0); assert.equal(await readFile(output, 'utf8'), saved);
    await writeFile(input, '{ PRIVATE-MALFORMED');
    const invalid = run(); assert.notEqual(invalid.status, 0); assert.doesNotMatch(invalid.stderr, /PRIVATE/);
    await writeFile(input, ' '.repeat(512 * 1024 + 1));
    assert.match(run().stderr, /limited to 512 KB/);
  } finally { await rm(root, { recursive: true, force: true }); }
});
