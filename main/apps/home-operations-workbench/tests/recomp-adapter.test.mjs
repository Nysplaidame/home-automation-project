import test from 'node:test';
import assert from 'node:assert/strict';
import { adaptRecompPlan } from '../recomp-adapter.js';
const now = '2026-10-04T12:00:00Z';
const fixture = () => ({ schemaVersion: 'recomp-plan/1.0', status: 'available', observedAt: now, planDate: '2026-10-04',
  routines: { items: [{ id: 'PRIVATE-ID', name: 'Sunday routine', scheduleDays: [6], exercises: [{ discomfort: 'PRIVATE-HEALTH' }] },
    { id: 'monday', name: 'Monday routine', scheduleDays: [0] }], scheduleOverrides: {} }, health: 'PRIVATE-HISTORY' });
test('source weekday convention projects only selected routines without health or completion inference', () => {
  const result = adaptRecompPlan(fixture(), { now });
  assert.equal(result.today.workouts.length, 1);
  assert.equal(result.today.workouts[0].title, 'Sunday routine');
  assert.equal(result.today.workouts[0].status, 'warning');
  assert.equal(result.today.workouts[0].due, '2026-10-04');
  assert.match(result.today.workouts[0].detail, /completion and readiness unknown/);
  assert.doesNotMatch(JSON.stringify(result), /PRIVATE|Monday routine/);
});
test('one-off moves suppress original occurrence and import moved-in occurrences', () => {
  const value = fixture();
  value.routines.scheduleOverrides = { '2026-10-04|PRIVATE-ID': '2026-10-05', '2026-10-05|monday': '2026-10-04', '2026-10-01|removed': '2026-10-04' };
  const result = adaptRecompPlan(value, { now });
  assert.equal(result.today.workouts.length, 1);
  assert.equal(result.today.workouts[0].title, 'Monday routine');
  assert.match(result.today.workouts[0].detail, /Moved from 2026-10-05/);
  assert.match(result.today.operations[0].detail, /1 orphan moves omitted/);
  value.routines.scheduleOverrides = { '2026-10-04|PRIVATE-ID': '2026-10-04' };
  assert.equal(adaptRecompPlan(value, { now }).today.workouts.length, 1);
});
test('unavailable, stale, future and empty schedules preserve absence and uncertainty', () => {
  for (const [observedAt, expected] of [['2020-01-01T00:00:00Z', 'stale'], ['2026-10-04T12:00:01Z', 'unknown'], [null, 'unknown']]) assert.equal(adaptRecompPlan({ ...fixture(), observedAt }, { now }).today.workouts[0].status, expected);
  assert.equal(adaptRecompPlan({ ...fixture(), status: 'unavailable' }, { now }).today.workouts.length, 0);
  const empty = adaptRecompPlan({ ...fixture(), planDate: '2026-10-06' }, { now });
  assert.equal(empty.today.workouts.length, 0);
  assert.match(empty.today.operations[0].detail, /not complete training coverage/);
});
test('invalid routine or move structures reject before projecting partial plans', () => {
  for (const routines of [{ items: [null] }, { items: [{ id: 'x', scheduleDays: [7] }] }, { items: [{ id: 'x' }, { id: 'x' }] },
    { items: [], scheduleOverrides: { '2026-02-30|x': '2026-10-04' } }, { items: [], scheduleOverrides: { '2026-10-04|x': 'bad' } },
    { items: Array(5001).fill({ id: 'x' }) }, { items: [], scheduleOverrides: [] }]) assert.throws(() => adaptRecompPlan({ ...fixture(), routines }, { now }));
  assert.throws(() => adaptRecompPlan({ ...fixture(), planDate: '2026-02-29' }, { now }));
});
test('bounds and shared privacy validation apply after schedule projection', () => {
  const value = fixture();
  value.routines.items = Array.from({ length: 70 }, (_, id) => ({ id: String(id), name: 'secret PRIVATE', scheduleDays: [6] }));
  value.ownerUrl = 'https://recomp.example.invalid/?token=PRIVATE';
  const result = adaptRecompPlan(value, { now });
  assert.equal(result.today.workouts.length, 50);
  assert.equal(result.today.workouts[0].title, 'Unnamed routine');
  assert.equal(result.today.workouts[0].ownerUrl, '');
  assert.match(result.today.operations[0].detail, /50 of 70 selected occurrences/);
});
