import { test } from "node:test";
import assert from "node:assert/strict";
import { SnapshotPublisher, mapDisplayState } from "../src/safety-host.ts";
import { SafetyReceiver } from "../src/safety.ts";

test("fixed display mapping never includes credentials, attributes or unrelated entities", () => {
  const context = {
    connection: { connected: true }, auth: { access_token: "test-only-secret" },
    states: {
      "input_boolean.ventsys_failsafe": { state: "off", attributes: { secret: "hidden" } },
      "fan.inline_fan": { state: "on" },
      "sensor.unrelated": { state: "private" },
    },
    callService: () => { throw new Error("No service calls permitted"); },
  };
  const publisher = new SnapshotPublisher();
  const snapshot = publisher.next(context, 100000);
  assert.deepEqual(snapshot.state, { failsafe: "off", fan: "on", monitoring: "unverified" });
  assert.ok(!JSON.stringify(snapshot).includes("secret"));
  assert.ok(!JSON.stringify(snapshot).includes("private"));
  assert.equal(snapshot.sequence, 0);
  assert.equal(publisher.next(context, 105000).sequence, 1);
  assert.equal(publisher.next(null, 110000).type, "offline");
  assert.equal(publisher.next({ ...context, connection: { connected: false } }, 111000).type, "offline");
});

test("unknown states cannot be mapped to off or healthy", () => {
  for (const state of [null, undefined, 0, false, "unavailable", "unknown", "OFF", {}]) {
    assert.deepEqual(mapDisplayState({ states: {
      "input_boolean.ventsys_failsafe": { state }, "fan.inline_fan": { state },
    } }), { failsafe: "unknown", fan: "unknown", monitoring: "unverified" });
  }
});

test("publisher heartbeats renew receiver trust only within their validity and session", () => {
  const publisher = new SnapshotPublisher();
  const parent = {};
  const receiver = new SafetyReceiver("https://ha.test", parent, publisher.sessionId);
  const context = { connection: { connected: true }, states: { "input_boolean.ventsys_failsafe": { state: "on" } } };
  for (let time = 100000; time <= 120000; time += 5000) {
    assert.equal(receiver.receive({ origin: "https://ha.test", source: parent, data: publisher.next(context, time) }, time, time - 100000), true);
    assert.equal(receiver.view(time, time - 100000).critical, true);
  }
  assert.equal(receiver.view(135000, 35000).connected, false);
  const nextSession = new SnapshotPublisher();
  assert.notEqual(nextSession.sessionId, publisher.sessionId);
  assert.equal(receiver.receive({ origin: "https://ha.test", source: parent, data: nextSession.next(context, 135001) }, 135001, 35001), false);
});
