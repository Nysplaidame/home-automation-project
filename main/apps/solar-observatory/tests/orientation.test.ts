import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { Matrix4, SphereGeometry, Vector3 as ThreeVector } from "three";
import { bodyAxes, surfaceAxes, utcToTdbSeconds, ORIENTATION_START_MS, ORIENTATION_END_MS, type OrientedBody, type BodyAxes } from "../src/orientation.ts";
import { type Vector3, toScene } from "../src/astronomy.ts";
import { parseHorizons } from "../src/horizons.ts";

const fixture = JSON.parse(readFileSync(new URL("./fixtures/orientations.json", import.meta.url), "utf8")) as {
  samples: { utc: string; body: OrientedBody; tdbSeconds: number; axes: BodyAxes }[];
};
const dot = (a: Vector3, b: Vector3) => a.reduce((sum, value, i) => sum + value * b[i], 0);
const cross = (a: Vector3, b: Vector3): Vector3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];

for (const sample of fixture.samples) {
  test(`${sample.body} orientation matches independent CSPICE at ${sample.utc}`, () => {
    const time = Date.parse(sample.utc);
    assert.ok(Math.abs(utcToTdbSeconds(time) - sample.tdbSeconds) < 5e-7);
    const axes = bodyAxes(sample.body, time);
    for (const axis of ["x", "y", "z"] as const) {
      axes[axis].forEach((value, i) => assert.ok(Math.abs(value - sample.axes[axis][i]) < 1e-10));
    }
  });
}

test("surface basis stays orthonormal and right-handed throughout supported dates", () => {
  for (const sample of fixture.samples) {
    const a = surfaceAxes(sample.body, Date.parse(sample.utc));
    for (const axis of [a.x, a.y, a.z]) assert.ok(Math.abs(dot(axis, axis) - 1) < 1e-12);
    assert.ok(Math.abs(dot(a.x, a.y)) < 1e-12);
    assert.ok(Math.abs(dot(a.y, a.z)) < 1e-12);
    assert.ok(Math.abs(dot(a.z, a.x)) < 1e-12);
    assert.ok(Math.abs(dot(cross(a.x, a.y), a.z) - 1) < 1e-12);
  }
});

test("actual Three sphere UVs map Greenwich, east and north to the correct body axes", () => {
  const time = Date.parse("2026-10-04T01:00:00Z");
  const body = bodyAxes("earth", time);
  const axes = surfaceAxes("earth", time);
  const matrix = new Matrix4().makeBasis(new ThreeVector(...axes.x), new ThreeVector(...axes.y), new ThreeVector(...axes.z));
  const geometry = new SphereGeometry(1, 96, 64);
  const uv = geometry.getAttribute("uv"), position = geometry.getAttribute("position");
  for (const [u, v, expected] of [[0.5, 0.5, body.x], [0.75, 0.5, body.y], [0.5, 1, body.z]] as const) {
    const indices = Array.from({ length: uv.count }, (_, i) => i);
    // Pole vertices have a half-cell U offset; longitude is immaterial there.
    const index = indices.find(i => Math.abs(uv.getY(i) - v) < 1e-6 && (v === 1 || Math.abs(uv.getX(i) - u) < 1e-6))!;
    assert.notEqual(index, undefined);
    const actual = new ThreeVector().fromBufferAttribute(position, index).applyMatrix4(matrix);
    assert.ok(actual.distanceTo(new ThreeVector(...toScene(expected, 1))) < 1e-7);
  }
  geometry.dispose();
});

test("Moon prime meridian approximately faces Earth rather than a mirrored far side", () => {
  const raw = JSON.parse(readFileSync(new URL("./fixtures/moon.json", import.meta.url), "utf8"));
  const moon = parseHorizons(raw.payload, raw.request);
  for (const sample of moon.samples) {
    const earthDirection = sample.positionKm.map(x => -x / Math.hypot(...sample.positionKm)) as unknown as Vector3;
    assert.ok(dot(bodyAxes("moon", sample.utcMs).x, earthDirection) > Math.cos(10 * Math.PI / 180));
  }
});

test("orientation refuses unsupported times rather than assuming future leap seconds", () => {
  for (const time of [NaN, Infinity, ORIENTATION_START_MS - 1, ORIENTATION_END_MS, 123.5]) {
    assert.throws(() => bodyAxes("earth", time), RangeError);
  }
  assert.doesNotThrow(() => bodyAxes("moon", ORIENTATION_START_MS));
  assert.doesNotThrow(() => bodyAxes("moon", ORIENTATION_END_MS - 1));
});
