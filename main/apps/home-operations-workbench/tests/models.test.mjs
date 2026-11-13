import assert from 'node:assert/strict';
import test from 'node:test';
import {
  aggregateStatus,
  buildEmergencyPack,
  cookingAvailability,
  normalizeWorkbook,
  recoveryAssessment,
  sharedDependencyGroups,
} from '../models.js';
import { demoOperations } from '../fixtures/demo-operations.js';

function cloneDemo() {
  return structuredClone(demoOperations);
}

test('normalizes the supported evidence schema and strips unsafe imported values', () => {
  const evidence = cloneDemo();
  evidence.dependencies[0].detail = 'API token: should never be displayed';
  evidence.today.food[0].ownerUrl = 'javascript:alert(1)';
  evidence.today.meals[0].ownerUrl = 'https://operator:password@example.test/runbook';
  evidence.today.workouts[0].ownerUrl = 'https://example.test/runbook?access_token=secret';
  evidence.dependencies[1].status = 'warn';

  const normalized = normalizeWorkbook(evidence);

  assert.equal(normalized.schemaVersion, '1.0');
  assert.equal(normalized.dependencies[0].detail, 'Sensitive detail omitted.');
  assert.equal(normalized.today.food[0].ownerUrl, '');
  assert.equal(normalized.today.meals[0].ownerUrl, '');
  assert.equal(normalized.today.workouts[0].ownerUrl, '');
  assert.equal(normalized.dependencies[1].status, 'warning');
});

test('rejects evidence from an unsupported schema version', () => {
  const evidence = cloneDemo();
  evidence.schemaVersion = '2.0';
  assert.throws(() => normalizeWorkbook(evidence), /supported Home Operations evidence schema/);
});

test('groups declared shared dependencies without claiming a root cause', () => {
  const normalized = normalizeWorkbook(cloneDemo());
  const groups = sharedDependencyGroups(normalized);

  assert.equal(groups.length, 1);
  assert.equal(groups[0].dependency.id, 'vm103');
  assert.deepEqual(groups[0].impacted.map((item) => item.id).sort(), ['grocy', 'homepage']);
  assert.equal(groups[0].status, 'warning');
});

test('keeps backup, integrity and restore evidence distinct', () => {
  const normalized = normalizeWorkbook(cloneDemo());
  const byId = new Map(normalized.recovery.map((system) => [system.id, system]));

  assert.equal(recoveryAssessment(byId.get('ha')), 'not_proven');
  assert.equal(recoveryAssessment(byId.get('docker-host')), 'proved');
  assert.equal(recoveryAssessment(byId.get('frigate')), 'needs_evidence');
});

test('reports recipe candidates from declared ingredient availability', () => {
  const normalized = normalizeWorkbook(cloneDemo());

  assert.equal(cookingAvailability(normalized.cooking[0]), 'ready');
  assert.equal(cookingAvailability(normalized.cooking[1]), 'missing');
  assert.equal(aggregateStatus(['healthy', 'unknown', 'warning']), 'warning');
});

test('emergency exports contain recovery evidence but never raw sensitive detail', () => {
  const evidence = cloneDemo();
  evidence.recovery.systems[0].backup.detail = 'password retained elsewhere';
  const pack = buildEmergencyPack(normalizeWorkbook(evidence));

  assert.match(pack, /Home Operations Emergency Pack/);
  assert.doesNotMatch(pack, /password retained elsewhere/);
  assert.doesNotMatch(pack, /Sensitive detail omitted\./);
});
