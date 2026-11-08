import { test } from "node:test";
import assert from "node:assert/strict";
import { SafetyReceiver, type DisplayMessage } from "../src/safety.ts";

const origin = "https://ha.example.test";
const sessionId = "test-session-00000001";
const source = {};
const message = (sequence = 0): DisplayMessage => ({
  version: 1, type: "state_snapshot", sessionId, sequence, issuedAtMs: 100000, expiresAtMs: 115000,
  state: { failsafe: "off", fan: "on", monitoring: "unverified" },
});
const event = (data: unknown) => ({ origin, source, data });
const receiver = () => new SafetyReceiver(origin, source, sessionId);

test("starts offline; connected does not imply healthy; no state references leak", () => {
  const r = receiver();
  assert.equal(r.view(100000, 0).connected, false);
  const m = message();
  assert.equal(r.receive(event(m), 100000, 0), true);
  m.state!.failsafe = "on";
  const view = r.view(100001, 1);
  assert.equal(view.label, "Monitoring incomplete");
  assert.equal(view.critical, false);
  view.state!.failsafe = "on";
  assert.equal(r.view(100002, 2).critical, false);
});

test("unrelated windows cannot change or clear trusted state", () => {
  const r = receiver();
  r.receive(event(message()), 100000, 0);
  assert.equal(r.receive({ ...event(message(1)), origin: "https://other.test" }, 100001, 1), false);
  assert.equal(r.receive({ ...event(message(1)), source: {} }, 100001, 1), false);
  assert.equal(r.view(100001, 1).connected, true);
});

test("replays, bad sessions, commands, extra fields and invalid times clear state", () => {
  const bad = [
    message(), { ...message(1), sessionId: "wrong-session-00000" },
    { ...message(1), type: "service-call" }, { ...message(1), token: "forbidden" },
    { ...message(1), expiresAtMs: 160000 }, { ...message(1), expiresAtMs: 100001 },
    { ...message(1), issuedAtMs: 100002 }, { ...message(1), sequence: NaN },
    { ...message(1), state: { ...message().state, extra: true } },
    { ...message(1), state: { ...message().state, failsafe: null } },
  ];
  for (const value of bad) {
    const r = receiver();
    r.receive(event(message()), 100000, 0);
    assert.equal(r.receive(event(value), 100001, 1), false);
    assert.equal(r.view(100001, 1).connected, false);
  }
});

test("expiry uses wall and monotonic clocks; backwards wall clock cannot prolong trust", () => {
  const r = receiver();
  r.receive(event(message()), 100000, 0);
  assert.equal(r.view(114999, 14999).connected, true);
  assert.equal(r.view(90000, 15000).connected, false);
  r.receive(event(message(1)), 100000, 15001);
  assert.equal(r.view(115000, 15002).connected, false);
});

test("fresh identical snapshots renew expiry; disconnect and reload clear status", () => {
  const r = receiver();
  r.receive(event(message()), 100000, 0);
  r.receive(event({ ...message(1), issuedAtMs: 105000, expiresAtMs: 120000 }), 105000, 5000);
  assert.equal(r.view(115001, 15001).connected, true);
  r.disconnect();
  assert.equal(r.view(115002, 15002).connected, false);
  assert.equal(receiver().view(105000, 5000).connected, false);
});

test("failsafe remains critical even when monitoring is unavailable; offline clears it", () => {
  const r = receiver();
  const m = message();
  m.state = { failsafe: "on", fan: "unknown", monitoring: "unavailable" };
  r.receive(event(m), 100000, 0);
  assert.equal(r.view(100001, 1).critical, true);
  const { state, ...offline } = message(1);
  assert.equal(r.receive(event({ ...offline, type: "offline" }), 100001, 1), true);
  assert.equal(r.view(100002, 2).connected, false);
});
