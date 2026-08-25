import test from 'node:test';
import assert from 'node:assert/strict';
import {
  buildIncidentReport,
  evidenceCoverage,
  evidenceFocus,
  evaluateKeys,
  evaluateSymptom,
  normalizeSnapshot,
  snapshotSummary,
  symptoms,
} from '../diagnostic-model.js';

const homepage = symptoms.find(({ id }) => id === 'homepage');

test('normalizes supported scalar and object statuses', () => {
  const snapshot = normalizeSnapshot({
    timestamp: 'test',
    collector: 'Windows workstation',
    checks: { router: 'PASS', homepage: { status: 'fail', detail: 'HTTP 503' }, skipped: 'skipped', nested: { ignored: true } },
  });
  assert.deepEqual(snapshot, {
    timestamp: 'test',
    collector: 'Windows workstation',
    checks: { router: 'pass', homepage: 'fail', skipped: 'unknown' },
    details: { homepage: 'HTTP 503' },
  });
});

test('rejects snapshots without a checks object', () => {
  assert.throws(() => normalizeSnapshot({ timestamp: 'test' }), /checks object/);
});

test('failed dependency wins symptom assessment', () => {
  const snapshot = normalizeSnapshot({ checks: { router: 'pass', docker_host: 'pass', homepage: 'fail' } });
  assert.equal(evaluateSymptom(homepage, snapshot), 'fail');
});

test('missing evidence remains unknown instead of healthy', () => {
  const snapshot = normalizeSnapshot({ checks: { router: 'pass', docker_host: 'pass' } });
  assert.equal(evaluateSymptom(homepage, snapshot), 'unknown');
});

test('dependency path aggregation stops on any failed signal', () => {
  const snapshot = normalizeSnapshot({ checks: { a: 'pass', b: 'fail', c: 'pass' } });
  assert.equal(evaluateKeys(['a', 'b', 'c'], snapshot), 'fail');
  assert.equal(evaluateKeys([], snapshot), 'unknown');
});

test('summary is recalculated from normalized checks', () => {
  const snapshot = normalizeSnapshot({ checks: { a: 'pass', b: 'fail', c: 'skipped' } });
  assert.deepEqual(snapshotSummary(snapshot), { pass: 1, fail: 1, warn: 0, unknown: 1, total: 3 });
});

test('focus selects the first failed evidence boundary', () => {
  const snapshot = normalizeSnapshot({ checks: { router: 'pass', docker_host: 'pass', homepage: 'fail' } });
  const focus = evidenceFocus(homepage, snapshot);
  assert.equal(focus.status, 'fail');
  assert.equal(focus.label, 'Homepage HTTPS');
  assert.deepEqual(evidenceCoverage(homepage, snapshot), { collected: 3, total: 3 });
});

test('focus asks for missing evidence before claiming health', () => {
  const snapshot = normalizeSnapshot({ checks: { router: 'pass' } });
  const focus = evidenceFocus(homepage, snapshot);
  assert.equal(focus.status, 'unknown');
  assert.equal(focus.label, 'Docker host reachable');
  assert.deepEqual(evidenceCoverage(homepage, snapshot), { collected: 1, total: 3 });
});

test('incident report contains only selected evidence and notes', () => {
  const snapshot = normalizeSnapshot({ timestamp: 'now', checks: { router: 'pass', docker_host: 'pass', homepage: 'fail' } });
  const report = buildIncidentReport(homepage, snapshot, 'TLS timeout at 14:32');
  assert.match(report, /Homepage HTTPS: fail/);
  assert.match(report, /TLS timeout at 14:32/);
  assert.doesNotMatch(report, /password/i);
});
