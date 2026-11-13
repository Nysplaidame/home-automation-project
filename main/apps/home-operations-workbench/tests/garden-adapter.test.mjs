import test from 'node:test';
import assert from 'node:assert/strict';
import { adaptGardenTasks } from '../garden-adapter.js';
const now = '2026-10-04T12:00:00Z';
const fixture = () => ({ schemaVersion: 'garden-tasks/1.0', status: 'available', observedAt: now,
  ownerUrl: 'https://garden.example.invalid/tasks', tasks: [
    { title: 'Water herbs', status: 'pending', due_at: '2026-10-04T13:00:00.123456+01:00', id: 'PRIVATE-ID', notes: 'PRIVATE-NOTE', plant_id: 'PRIVATE-PLANT', recurrence_rule: 'PRIVATE-RULE' },
    { title: 'Completed task', status: 'completed' }, { title: 'Cancelled task', status: 'cancelled' }], token: 'PRIVATE-TOKEN' });

test('verified task shape shows only pending records with UTC due time and scoped evidence', () => {
  const result = adaptGardenTasks(fixture(), { now });
  assert.equal(result.today.gardenTasks.length, 1);
  assert.equal(result.today.gardenTasks[0].due, '2026-10-04T12:00:00.123Z');
  assert.equal(result.today.gardenTasks[0].status, 'warning');
  assert.match(result.today.operations[0].detail, /2 completed\/cancelled records omitted/);
  assert.doesNotMatch(JSON.stringify(result), /PRIVATE/);
});
test('stale future ambiguous impossible and absent observations do not become current', () => {
  for (const [observedAt, status] of [['2026-10-02T23:59:59Z', 'stale'], ['2026-10-05T00:00:00Z', 'unknown'], ['2026-10-04T12:00:00', 'unknown'], ['2026-02-30T12:00:00Z', 'unknown'], [null, 'unknown']]) {
    const result = adaptGardenTasks({ ...fixture(), observedAt }, { now });
    assert.equal(result.today.operations[0].status, status);
    assert.equal(result.today.gardenTasks[0].status, status);
  }
  assert.equal(adaptGardenTasks({ ...fixture(), observedAt: '2026-10-03T00:00:00Z' }, { now }).today.operations[0].status, 'healthy');
});
test('unavailable and empty selections preserve absence without garden health claims', () => {
  const unavailable = adaptGardenTasks({ ...fixture(), status: 'unavailable' }, { now });
  assert.equal(unavailable.today.gardenTasks.length, 0);
  assert.equal(unavailable.today.operations[0].status, 'unknown');
  const empty = adaptGardenTasks({ ...fixture(), tasks: [] }, { now });
  assert.match(empty.today.operations[0].detail, /No complete-garden or overdue inference/);
  assert.equal(empty.today.gardenTasks.length, 0);
});
test('pending rows are capped after filtering and unsafe fields/links are omitted', () => {
  const value = fixture();
  value.tasks = [...Array.from({ length: 60 }, () => ({ status: 'completed' })), ...Array.from({ length: 70 }, () => ({ title: 'api_key PRIVATE', status: 'pending', due_at: 'bad' }))];
  value.ownerUrl = 'https://user:PRIVATE@example.invalid/?token=PRIVATE';
  const result = adaptGardenTasks(value, { now });
  assert.equal(result.today.gardenTasks.length, 50);
  assert.equal(result.today.gardenTasks[0].ownerUrl, '');
  assert.equal(result.today.gardenTasks[0].title, 'Unnamed task');
  assert.equal(result.today.gardenTasks[0].due, '');
  assert.match(result.today.operations[0].detail, /50 of 70 pending/);
  for (const ownerUrl of ['https://example.invalid/#access_token=PRIVATE', 'https://example.invalid/#%74oken=PRIVATE', 'https://example.invalid/#%ZZ', 'javascript:alert(1)']) {
    assert.equal(adaptGardenTasks({ ...fixture(), ownerUrl }, { now }).today.operations[0].ownerUrl, '');
  }
  assert.equal(adaptGardenTasks({ ...fixture(), ownerUrl: 'https://example.invalid/#tasks' }, { now }).today.operations[0].ownerUrl, 'https://example.invalid/#tasks');
});
test('invalid envelope structure states and policy fail closed', () => {
  for (const value of [null, {}, { ...fixture(), tasks: [null] }, { ...fixture(), tasks: [{ status: 'unknown' }] }, { ...fixture(), tasks: Array(5001).fill({ status: 'pending' }) }]) {
    assert.throws(() => adaptGardenTasks(value, { now }));
  }
  assert.throws(() => adaptGardenTasks(fixture(), { now, maxAgeHours: NaN }));
});
