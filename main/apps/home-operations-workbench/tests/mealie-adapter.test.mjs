import test from 'node:test';
import assert from 'node:assert/strict';
import { adaptMealiePlan } from '../mealie-adapter.js';
const now = '2026-10-04T12:00:00Z';
const fixture = () => ({ schemaVersion: 'mealie-plan/1.0', status: 'available', observedAt: now,
  planDate: '2026-10-04', ownerUrl: 'https://mealie.example.invalid/', plan: { items: [
    { date: '2026-10-04', entryType: 'dinner', title: '', text: 'PRIVATE-NOTE', userId: 'PRIVATE-USER', recipe: { name: 'Bean stew', slug: 'PRIVATE-SLUG', image: 'PRIVATE-IMAGE', orgURL: 'PRIVATE-URL' } },
    { date: '2026-10-05', entryType: 'lunch', title: 'Other date meal' }], next: 'PRIVATE-NEXT', total: 1000 } });

test('verified paginated shape selects an explicit calendar date and excludes private payload', () => {
  const result = adaptMealiePlan(fixture(), { now });
  assert.equal(result.today.meals.length, 1);
  assert.equal(result.today.meals[0].title, 'Bean stew');
  assert.equal(result.today.meals[0].due, '2026-10-04');
  assert.equal(result.today.meals[0].status, 'warning');
  assert.match(result.today.meals[0].detail, /ingredient availability and food safety unknown/);
  assert.match(result.today.operations[0].detail, /1 other-date entries omitted/);
  assert.doesNotMatch(JSON.stringify(result), /PRIVATE|Other date meal/);
});
test('unavailable, empty and partial pages never invent meals or complete coverage', () => {
  const result = adaptMealiePlan({ ...fixture(), status: 'unavailable' }, { now });
  assert.deepEqual(result.today.meals, []);
  assert.equal(result.today.operations[0].status, 'unknown');
  const empty = adaptMealiePlan({ ...fixture(), planDate: '2026-10-06' }, { now });
  assert.equal(empty.today.meals.length, 0);
  assert.match(empty.today.operations[0].detail, /No complete-plan coverage/);
});
test('stale, future and ambiguous observations never certify a current plan', () => {
  for (const [observedAt, expected] of [['2020-01-01T00:00:00Z', 'stale'], ['2026-10-04T12:00:01Z', 'unknown'], ['2026-10-03T24:00:00Z', 'unknown'], [null, 'unknown']]) {
    const result = adaptMealiePlan({ ...fixture(), observedAt }, { now });
    assert.equal(result.today.meals[0].status, expected);
    assert.equal(result.today.operations[0].status, expected);
  }
});
test('bounds apply after date selection and unsafe labels and links are omitted', () => {
  const value = fixture();
  value.plan.items = [...Array(60).fill({ date: '2026-10-03', entryType: 'lunch' }), ...Array(70).fill({ date: '2026-10-04', entryType: 'dinner', title: 'token PRIVATE', recipe: { name: 'secret PRIVATE' } })];
  value.ownerUrl = 'https://mealie.example.invalid/#access_token=PRIVATE';
  const result = adaptMealiePlan(value, { now });
  assert.equal(result.today.meals.length, 50);
  assert.equal(result.today.meals[0].title, 'Unnamed planned meal');
  assert.equal(result.today.meals[0].ownerUrl, '');
  assert.match(result.today.operations[0].detail, /50 of 70 matching/);
});
test('invalid calendar selection, row type and oversized structure fail closed', () => {
  for (const value of [null, {}, { ...fixture(), planDate: '2026-02-29' }, { ...fixture(), plan: { items: [null] } },
    { ...fixture(), plan: { items: [{ date: '2026-02-30', entryType: 'dinner' }] } },
    { ...fixture(), plan: { items: [{ date: '2026-10-04', entryType: 'invalid' }] } },
    { ...fixture(), plan: { items: Array(5001).fill({ date: '2026-10-04', entryType: 'dinner' }) } }]) assert.throws(() => adaptMealiePlan(value, { now }));
  assert.throws(() => adaptMealiePlan(fixture(), { now, maxAgeHours: NaN }));
});
