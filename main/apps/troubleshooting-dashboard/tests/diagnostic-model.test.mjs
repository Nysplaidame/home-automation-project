import test from 'node:test';
import assert from 'node:assert/strict';
import {
  buildIncidentReport,
  snapshotFreshness,
  MAX_EVIDENCE_AGE_MS,
  expectedStates,
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
    example: false,
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
  const snapshot = normalizeSnapshot({ timestamp: new Date().toISOString(), checks: { router: 'pass', docker_host: 'pass', homepage: 'fail' } });
  assert.equal(evaluateSymptom(homepage, snapshot), 'fail');
});

test('missing evidence remains unknown instead of healthy', () => {
  const snapshot = normalizeSnapshot({ timestamp: new Date().toISOString(), checks: { router: 'pass', docker_host: 'pass' } });
  assert.equal(evaluateSymptom(homepage, snapshot), 'unknown');
});

test('dependency path aggregation stops on any failed signal', () => {
  const snapshot = normalizeSnapshot({ timestamp: new Date().toISOString(), checks: { a: 'pass', b: 'fail', c: 'pass' } });
  assert.equal(evaluateKeys(['a', 'b', 'c'], snapshot), 'fail');
  assert.equal(evaluateKeys([], snapshot), 'unknown');
});

test('summary is recalculated from normalized checks', () => {
  const snapshot = normalizeSnapshot({ timestamp: new Date().toISOString(), checks: { a: 'pass', b: 'fail', c: 'skipped' } });
  assert.deepEqual(snapshotSummary(snapshot), { pass: 1, fail: 1, warn: 0, unknown: 1, total: 3 });
});

test('focus selects the first failed evidence boundary', () => {
  const snapshot = normalizeSnapshot({ timestamp: new Date().toISOString(), checks: { router: 'pass', docker_host: 'pass', homepage: 'fail' } });
  const focus = evidenceFocus(homepage, snapshot);
  assert.equal(focus.status, 'fail');
  assert.equal(focus.label, 'Homepage HTTPS');
  assert.deepEqual(evidenceCoverage(homepage, snapshot), { collected: 3, total: 3 });
});

test('focus asks for missing evidence before claiming health', () => {
  const snapshot = normalizeSnapshot({ timestamp: new Date().toISOString(), checks: { router: 'pass' } });
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

const now = Date.parse('2026-09-10T12:00:00Z');
const snapshotAt = timestamp => normalizeSnapshot({ timestamp, checks: { router: 'pass', docker_host: 'pass', homepage: 'pass' } });

test('age accepts explicit offsets and exactly 36 hours, rejects older evidence', () => {
  assert.equal(snapshotFreshness(snapshotAt('2026-09-10T13:00:00+01:00'), now).usable, true);
  assert.equal(snapshotFreshness(snapshotAt(new Date(now - MAX_EVIDENCE_AGE_MS).toISOString()), now).usable, true);
  assert.equal(snapshotFreshness(snapshotAt(new Date(now - MAX_EVIDENCE_AGE_MS - 1).toISOString()), now).usable, false);
});

test('missing, ambiguous, malformed and future timestamps cannot establish health', () => {
  for (const timestamp of [undefined, '2026-09-10 12:00:00', 'yesterday', '2026-02-30T00:00:00Z', '2026-09-10T24:00:00Z', '2026-09-10T12:00:01Z']) {
    assert.equal(snapshotFreshness(snapshotAt(timestamp), now).usable, false, timestamp);
  }
});

test('stale passes and failures retain observations but cannot claim current health', () => {
  const snapshot = snapshotAt('2020-01-01T00:00:00Z');
  assert.equal(evaluateSymptom(homepage, snapshot), 'unknown');
  assert.match(evidenceFocus(homepage, snapshot).label, /Refresh/);
  snapshot.checks.homepage = 'fail';
  assert.equal(evaluateSymptom(homepage, snapshot), 'unknown');
  assert.match(buildIncidentReport(homepage, snapshot), /Homepage HTTPS: fail/);
  assert.match(buildIncidentReport(homepage, snapshot), /Stale/);
});

test('JSON cannot declare itself a trusted example', () => {
  const raw = { example: true, checks: { router: 'pass', docker_host: 'pass', homepage: 'pass' } };
  assert.equal(evaluateSymptom(homepage, normalizeSnapshot(raw)), 'unknown');
  const demo = normalizeSnapshot(raw, { example: true });
  assert.equal(evaluateSymptom(homepage, demo), 'pass');
  assert.match(buildIncidentReport(homepage, demo), /Example only/);
});

test('planned offline context never masks service and storage failures', () => {
  const camera = symptoms.find(item => item.id === 'camera');
  const snapshot = normalizeSnapshot({ timestamp: new Date().toISOString(), checks: { camera_01: 'fail', frigate_ping: 'pass', frigate_http: 'fail', frigate_mount: 'fail' } });
  assert.match(expectedStates.camera, /intentionally disconnected/);
  assert.equal(evaluateSymptom(camera, snapshot), 'fail');
  assert.match(buildIncidentReport(camera, snapshot), /Recording mount: fail/);
  assert.match(buildIncidentReport(camera, snapshot), /Recorded context:/);
});


test('route catalog has unique IDs, complete steps and no duplicate evidence keys', () => {
  assert.ok(symptoms.length >= 25);
  assert.equal(new Set(symptoms.map(item => item.id)).size, symptoms.length);
  for (const item of symptoms) {
    assert.ok(item.category && item.title && item.description, item.id);
    assert.ok(item.steps.length >= 3 && item.checks.length >= 3, item.id);
    assert.equal(new Set(item.checks.map(check => check.key)).size, item.checks.length);
    for (const step of item.steps) assert.ok(step.runOn && step.command && step.expected && step.failure, item.id);
  }
});

test('new routes never infer application health from a reachable shared host', () => {
  const basic = normalizeSnapshot({ timestamp: new Date().toISOString(), checks: { router: 'pass', docker_host: 'pass', ha_http: 'pass', mqtt: 'pass', nas: 'pass', grafana: 'pass', uptime_kuma: 'pass', llamacpp: 'pass' } });
  for (const route of symptoms.slice(5)) assert.equal(evaluateSymptom(route, basic), 'unknown', route.id);
});

test('new routes prioritize actual failure over missing deeper evidence', () => {
  for (const route of symptoms.slice(5)) {
    const snapshot = normalizeSnapshot({ timestamp: new Date().toISOString(), checks: { [route.checks[0].key]: 'fail' } });
    assert.equal(evaluateSymptom(route, snapshot), 'fail', route.id);
    assert.equal(evidenceFocus(route, snapshot).key, route.checks[0].key);
  }
});
