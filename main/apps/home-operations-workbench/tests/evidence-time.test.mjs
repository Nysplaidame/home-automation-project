import test from 'node:test';
import assert from 'node:assert/strict';
import { parseObservation } from '../evidence-time.js';
import { adaptGardenTasks } from '../garden-adapter.js';
import { adaptGrocyOverview } from '../grocy-adapter.js';
import { adaptHealthSnapshot } from '../health-adapter.js';

test('strict timestamp validation rejects rollovers, ambiguity and invalid offsets', () => {
  for (const value of [null, 123, '2026-02-29T12:00:00Z', '2026-04-31T12:00:00Z', '2026-10-04T24:00:00Z', '2026-10-04T12:60:00Z', '2026-10-04T12:00:60Z', '2026-10-04T12:00:00+14:01', '2026-10-04T12:00:00+15:00', '2026-10-04T12:00:00', '2026-10-04', '2026-10-04T12:00:00.1234567Z']) assert.equal(parseObservation(value), null, String(value));
  assert.equal(parseObservation('2024-02-29T12:00:00Z').toISOString(), '2024-02-29T12:00:00.000Z');
  assert.equal(parseObservation('2026-10-04T13:00:00.123456+01:00').toISOString(), '2026-10-04T12:00:00.123Z');
  assert.equal(parseObservation('2026-10-04T12:00:00+14:00').toISOString(), '2026-10-03T22:00:00.000Z');
});

test('all saved-source adapters share strict observation and fractional-second support', () => {
  const now = '2026-10-04T12:00:01Z';
  for (const [observedAt, expected] of [['2026-10-04T12:00:00.123456Z', 'healthy'], ['2026-10-04T12:00:02Z', 'unknown'], ['2026-10-03T24:00:00Z', 'unknown']]) {
    const garden = adaptGardenTasks({ schemaVersion: 'garden-tasks/1.0', status: 'available', observedAt, tasks: [] }, { now });
    const grocy = adaptGrocyOverview({ schemaVersion: 'grocy-overview/1.0', status: 'available', observedAt, overview: { stock: [], shopping_list: [] } }, { now });
    const health = adaptHealthSnapshot({ collector: 'Windows management workstation', timestamp: observedAt, checks: { router: 'pass' } }, { now });
    assert.equal(garden.today.operations[0].status, expected);
    assert.equal(grocy.today.operations[0].status, expected);
    assert.equal(health.dependencies[0].status, expected);
  }
});
