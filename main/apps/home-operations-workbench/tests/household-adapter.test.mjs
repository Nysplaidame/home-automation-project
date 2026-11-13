import test from 'node:test';
import assert from 'node:assert/strict';
import { adaptHouseholdSources } from '../household-adapter.js';
import { normalizeWorkbook } from '../models.js';
const now = '2026-10-04T12:00:00Z';
const fixture = () => ({ schemaVersion: 'household-sources/1.0', observedAt: '2099-01-01T00:00:00Z', token: 'PRIVATE-TOKEN', sources: [
  { schemaVersion: 'garden-tasks/1.0', status: 'available', observedAt: now, tasks: [{ title: 'Water herbs', status: 'pending', notes: 'PRIVATE-NOTE' }] },
  { schemaVersion: 'grocy-overview/1.0', status: 'available', observedAt: '2020-01-01T00:00:00Z', overview: { stock: [{ name: 'Beans', amount: 2 }], shopping_list: [] } },
  { schemaVersion: 'mealie-plan/1.0', status: 'unavailable', observedAt: now, planDate: '2026-10-04', plan: { items: [{ date: '2026-10-04', entryType: 'dinner', title: 'Hidden cached meal' }] } },
] });
test('bundle preserves independent observations, unavailable absence and source privacy', () => {
  const value = fixture(), before = JSON.stringify(value);
  const result = normalizeWorkbook(adaptHouseholdSources(value, { now }));
  assert.equal(result.today.gardenTasks[0].status, 'warning');
  assert.equal(result.today.food[0].status, 'stale');
  assert.deepEqual(result.today.meals, []);
  assert.deepEqual(result.today.operations.map(row => row.status), ['healthy', 'stale', 'unknown']);
  assert.match(result.today.operations[1].detail, /2020-01-01/);
  assert.equal(result.generatedAt, now.replace('Z', '.000Z'));
  assert.doesNotMatch(JSON.stringify(result), /PRIVATE|Hidden cached meal|2099/);
  assert.equal(JSON.stringify(value), before);
});
test('input order never changes source allocation or observation priority', () => {
  const value = fixture();
  assert.deepEqual(adaptHouseholdSources({ ...value, sources: [...value.sources].reverse() }, { now }), adaptHouseholdSources(value, { now }));
});
test('missing, duplicate, nested and unsupported sources fail atomically', () => {
  const value = fixture();
  for (const sources of [[], value.sources.slice(0, 2), [value.sources[0], value.sources[0], value.sources[2]], [null, ...value.sources.slice(1)], [{ schemaVersion: 'household-sources/1.0' }, ...value.sources.slice(1)], [{ schemaVersion: '1.0' }, ...value.sources.slice(1)]]) {
    assert.throws(() => adaptHouseholdSources({ ...value, sources }, { now }));
  }
  value.sources[0].tasks = [null];
  assert.throws(() => adaptHouseholdSources(value, { now }));
});
test('operation cap retains all three source headers and declares omitted shopping rows', () => {
  const value = fixture();
  value.sources[1].overview.shopping_list = Array.from({ length: 60 }, (_, index) => ({ name: `Item ${index}`, amount: 1 }));
  const result = normalizeWorkbook(adaptHouseholdSources(value, { now }));
  assert.equal(result.today.operations.length, 50);
  assert.deepEqual(result.today.operations.slice(0, 3).map(row => row.id), ['garden-source', 'grocy-source', 'mealie-source']);
  assert.match(result.today.operations[1].detail, /47 of 50 selected rows/);
  assert.equal(result.today.operations[49].title, 'Shopping: Item 46');
});
test('fresh meals coexist with food and garden without ingredient inference', () => {
  const value = fixture();
  value.sources[2].status = 'available';
  value.sources[1].observedAt = now;
  const result = adaptHouseholdSources(value, { now });
  assert.equal(result.today.meals[0].status, 'warning');
  assert.match(result.today.meals[0].detail, /ingredient availability and food safety unknown/);
  assert.equal(result.today.food[0].status, 'healthy');
  assert.equal(result.dependencies, undefined);
  assert.equal(result.recovery, undefined);
});

test('version1.1 includes Recomp independently while version1.0 remains three-source', () => {
  const value = fixture();
  value.schemaVersion = 'household-sources/1.1';
  value.sources.push({ schemaVersion: 'recomp-plan/1.0', status: 'available', observedAt: '2020-01-01T00:00:00Z', planDate: '2026-10-04', routines: { items: [{ id: 'private', name: 'Sunday routine', scheduleDays: [6] }] } });
  const result = adaptHouseholdSources(value, { now });
  assert.equal(result.today.workouts[0].status, 'stale');
  assert.equal(result.today.operations[3].id, 'recomp-source');
  assert.match(result.source.label, /four saved sources/);
  assert.throws(() => adaptHouseholdSources({ ...value, schemaVersion: 'household-sources/1.0' }, { now }));
  assert.throws(() => adaptHouseholdSources({ ...fixture(), schemaVersion: 'household-sources/1.1' }, { now }));
});
test('four-source operation cap reserves all observations before shopping', () => {
  const value = fixture(); value.schemaVersion = 'household-sources/1.1';
  value.sources.push({ schemaVersion: 'recomp-plan/1.0', status: 'unavailable', planDate: '2026-10-04' });
  value.sources[1].overview.shopping_list = Array.from({ length: 60 }, (_, id) => ({ name: `Item ${id}` }));
  const result = normalizeWorkbook(adaptHouseholdSources(value, { now }));
  assert.equal(result.today.operations.length, 50);
  assert.equal(result.today.operations[3].id, 'recomp-source');
  assert.match(result.today.operations[1].detail, /46 of 50 selected rows/);
});
