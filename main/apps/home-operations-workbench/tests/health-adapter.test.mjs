import test from 'node:test';
import assert from 'node:assert/strict';
import { adaptHealthSnapshot } from '../health-adapter.js';
import { normalizeWorkbook } from '../models.js';

const now = '2026-09-07T21:30:00Z';
const snapshot = { collector: 'Windows management workstation', timestamp: now, checks: { router: { status: 'pass', detail: 'private payload 123' }, camera_01: 'fail' } };
test('imports Windows checks without inventing missing health or planned downtime', () => {
  const output = normalizeWorkbook(adaptHealthSnapshot(snapshot, { now }));
  assert.equal(output.dependencies.find(x => x.id === 'router').status, 'healthy');
  assert.equal(output.dependencies.find(x => x.id === 'camera_01').status, 'failed');
  assert.equal(output.dependencies.find(x => x.id === 'nas').status, 'unknown');
  assert.ok(!JSON.stringify(output).includes('private payload'));
  assert.ok(output.recovery.every(x => x.backup.status === 'unknown'));
});
test('Proxmox backups never imply integrity or restore proof', () => {
  const output = normalizeWorkbook(adaptHealthSnapshot({ collector: 'Proxmox host', timestamp: now, checks: { backup_vm100: 'pass', backup_ct111: 'fail' } }, { now }));
  assert.equal(output.recovery.find(x => x.id === 'vm100').backup.status, 'healthy');
  assert.equal(output.recovery.find(x => x.id === 'ct111').backup.status, 'failed');
  assert.ok(output.recovery.every(x => x.integrity.status === 'unknown' && x.restore.status === 'unknown'));
});
test('old, missing, ambiguous and future timestamps cannot produce current health', () => {
  for (const timestamp of [undefined, 'garbage', '2026-02-31T00:00:00Z', '2026-09-07 22:28:55', '2027-01-01T00:00:00Z']) {
    assert.equal(adaptHealthSnapshot({ ...snapshot, timestamp }, { now }).dependencies[0].status, 'unknown');
  }
  assert.equal(adaptHealthSnapshot({ ...snapshot, timestamp: '2026-09-01T00:00:00Z' }, { now }).dependencies[0].status, 'stale');
  assert.equal(adaptHealthSnapshot({ ...snapshot, timestamp: '2026-09-07 22:28:55' }, { now, timestampOffset: '+01:00' }).dependencies[0].status, 'healthy');
});
test('rejects unsupported inputs and invalid freshness policy', () => {
  for (const value of [null, [], {}, { collector: 'untrusted', checks: {} }]) assert.throws(() => adaptHealthSnapshot(value));
  assert.throws(() => adaptHealthSnapshot(snapshot, { maxAgeHours: -1 }));
  assert.throws(() => adaptHealthSnapshot(snapshot, { timestampOffset: 'local' }));
});
