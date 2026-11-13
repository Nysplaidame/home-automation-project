import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { evaluate, evaluateWorld, distance, samplePath, toScene, validateSegment, type TrajectorySegment } from "../src/astronomy.ts";
import { parseHorizons, requestUrl } from "../src/horizons.ts";

const ids = ["earth", "moon", "jupiter", "io", "saturn", "jwst"];
const fixtures = ids.map(id => JSON.parse(readFileSync(new URL(`./fixtures/${id}.json`, import.meta.url), "utf8")));
const segments = fixtures.map(f => parseHorizons(f.payload, f.request));

for (const [index, id] of ids.entries()) {
  test(`${id}: Hermite midpoints agree with withheld JPL samples within 1 km`, () => {
    const full = segments[index];
    const coarse = { ...full, samples: full.samples.filter((_, i) => i % 2 === 0) };
    let worst = 0;
    for (const [i, reference] of full.samples.entries()) {
      const result = evaluate(coarse, reference.utcMs);
      const error = distance(result.positionKm, reference.positionKm);
      if (i % 2 === 1) worst = Math.max(worst, error);
      assert.ok(error < 1, `${id}: ${error} km at ${reference.utcMs}`);
    }
    console.log(`${id} maximum withheld midpoint error: ${worst.toFixed(6)} km`);
  });
}

test("parent composition evaluates both levels at the identical instant", () => {
  const utcMs = segments[0].samples[3].utcMs;
  const moon = evaluateWorld("moon", utcMs, segments);
  const earth = evaluateWorld("earth", utcMs, segments);
  const local = evaluate(segments[1], utcMs);
  assert.ok(distance(moon.positionKm, earth.positionKm.map((p, i) => p + local.positionKm[i]) as [number, number, number]) < 1e-8);
  assert.deepEqual(moon.velocityKmS, earth.velocityKmS.map((v, i) => v + local.velocityKmS[i]));
});

test("path vertices and body positions use the same right-handed transform", () => {
  const segment = segments[1];
  const times = segment.samples.map(s => s.utcMs);
  const path = samplePath(segment, times, 100000);
  times.forEach((time, i) => assert.deepEqual(path[i], toScene(evaluate(segment, time).positionKm, 100000)));
  assert.deepEqual(toScene([1, 2, 3], 1), [1, 3, -2]);
  assert.throws(() => toScene([1, 2, 3], 0));
});

test("invalid samples, extrapolation, gaps, cycles and ambiguous coverage fail closed", () => {
  const segment = segments[1];
  const start = segment.samples[0].utcMs;
  assert.throws(() => evaluate(segment, start - 1));
  assert.throws(() => evaluate(segment, segment.samples.at(-1)!.utcMs + 1));
  assert.throws(() => evaluate(segment, NaN));
  assert.throws(() => validateSegment({ ...segment, samples: [...segment.samples].reverse() }));
  assert.throws(() => validateSegment({ ...segment, samples: [{ ...segment.samples[0], positionKm: [NaN, 0, 0] }, segment.samples[1]] }));
  assert.throws(() => evaluateWorld("moon", start, [segment]));
  assert.throws(() => evaluateWorld("moon", start, [...segments, segment]));
  assert.throws(() => evaluateWorld("moon", start, [segment, { ...segments[0], parentId: "moon" }]));
  const split: TrajectorySegment[] = [
    { ...segment, samples: segment.samples.slice(0, 3) },
    { ...segment, samples: segment.samples.slice(4) },
  ];
  assert.throws(() => evaluateWorld("moon", segment.samples[3].utcMs, [...split, segments[0]]));
});

test("parser rejects upstream errors and metadata drift rather than guessing", () => {
  const { payload, request } = fixtures[1];
  for (const changed of [
    { ...payload, error: "No ephemeris" },
    { ...payload, signature: { version: "9.0" } },
    { ...payload, result: payload.result.replace("ICRF", "B1950") },
    { ...payload, result: payload.result.replace("KM-S", "AU-D") },
    { ...payload, result: payload.result.replace("$$EOE", "END") },
  ]) assert.throws(() => parseHorizons(changed, request));
  assert.throws(() => parseHorizons(payload, { ...request, target: "501" }));
  assert.throws(() => parseHorizons(payload, { ...request, stepMinutes: 10 }));
  assert.throws(() => requestUrl({ ...request, center: "invalid" }));
});
