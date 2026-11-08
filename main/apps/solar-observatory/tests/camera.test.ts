import { test } from "node:test";
import assert from "node:assert/strict";
import { fitCamera, fitOrientedCamera, motionAt, retarget, type Motion } from "../src/camera.ts";

for (const [width, height] of [[800, 480], [1024, 600], [480, 800]]) {
  test(`framing respects both dimensions and depth at ${width}x${height}`, () => {
    const fit = fitCamera([{ center: [0, 0, 0], radius: 1 }, { center: [4, 1, -2], radius: 0.1 }], width, height);
    const angularTangent = fit.radius / Math.sqrt(fit.distance ** 2 - fit.radius ** 2);
    const tanY = Math.tan(32 * Math.PI / 360);
    assert.ok(angularTangent / tanY <= 0.700000001);
    assert.ok(angularTangent / (tanY * width / height) <= 0.700000001);
    assert.ok(fit.near < fit.distance - fit.radius);
    assert.ok(fit.far > fit.distance + fit.radius);
    assert.ok(fit.near > 0);
  });
}

test("single body portrait fills 70 percent of usable landscape height", () => {
  const fit = fitCamera([{ center: [0, 0, 0], radius: 1 }], 800, 440);
  const fraction = 1 / Math.sqrt(fit.distance ** 2 - 1) / Math.tan(32 * Math.PI / 360);
  assert.ok(Math.abs(fraction - 0.7) < 1e-12);
  assert.throws(() => fitCamera([], 800, 480));
  assert.throws(() => fitCamera([{ center: [0, 0, 0], radius: 1 }], 0, 480));
});

const move: Motion = { startMs: 0, durationMs: 24000, initial: { value: 0, velocity: 0, acceleration: 0 }, target: 10 };
test("flat rings do not force portrait framing to use their full diameter as height", () => {
  const objects = [{ center: [0, 0, 0] as const, radius: 1 },
    ...Array.from({ length: 180 }, (_, i) => ({
      center: [2.27 * Math.cos(i / 180 * Math.PI * 2), 0.4 * Math.sin(i / 180 * Math.PI * 2), 0] as const,
      radius: 0.01,
    }))];
  const fit = fitOrientedCamera(objects, 800, 292, [0, 0, 1]);
  const conservative = fitCamera(objects, 800, 292);
  assert.ok(fit.distance < conservative.distance * 0.6);
  const planetFill = 1 / Math.sqrt(fit.distance ** 2 - 1) / Math.tan(32 * Math.PI / 360);
  assert.ok(planetFill > 0.69);
  const tanY = Math.tan(32 * Math.PI / 360) * 0.7;
  const tanX = tanY * 800 / 292;
  for (const o of objects) {
    assert.ok((fit.distance - o.center[2]) * tanX - Math.abs(o.center[0]) >= o.radius * Math.sqrt(1 + tanX ** 2) - 1e-10);
    assert.ok((fit.distance - o.center[2]) * tanY - Math.abs(o.center[1]) >= o.radius * Math.sqrt(1 + tanY ** 2) - 1e-10);
  }
});
test("24-second motion starts and ends at rest, without a fast initial jump", () => {
  assert.deepEqual(motionAt(move, 0), move.initial);
  assert.deepEqual(motionAt(move, 24000), { value: 10, velocity: 0, acceleration: 0 });
  assert.ok(motionAt(move, 1000).value < 0.01);
  assert.ok(motionAt(move, 23000).velocity < motionAt(move, 18000).velocity);
  let previous = 0;
  for (let time = 0; time <= 24000; time += 100) {
    const current = motionAt(move, time).value;
    assert.ok(current >= previous && current <= 10);
    previous = current;
  }
});

test("retargeting preserves position, velocity and acceleration; the latest target replaces the old", () => {
  const current = motionAt(move, 8000);
  const next = retarget(move, 8000, -5);
  assert.deepEqual(motionAt(next, 8000), current);
  const following = motionAt(next, 8000.01);
  assert.ok(Math.abs(following.value - current.value) < 0.001);
  assert.ok(Math.abs(following.velocity - current.velocity) < 0.001);
  assert.ok(Math.abs(following.acceleration - current.acceleration) < 0.001);
  const latest = retarget(next, 9000, 20);
  assert.deepEqual(motionAt(latest, 33000), { value: 20, velocity: 0, acceleration: 0 });
  assert.throws(() => retarget(move, 1000, 2, 0));
});
