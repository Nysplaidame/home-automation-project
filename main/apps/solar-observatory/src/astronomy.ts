export type Vector3 = readonly [number, number, number];
export interface StateVector {
  utcMs: number;
  positionKm: Vector3;
  velocityKmS: Vector3;
}
export interface TrajectorySegment {
  objectId: string;
  parentId: string;
  frame: "ICRF";
  timeScale: "UTC";
  units: "KM-S";
  source: string;
  samples: readonly StateVector[];
}

const finiteVector = (v: Vector3) => Array.isArray(v) && v.length === 3 && v.every(Number.isFinite);
export const add = (a: Vector3, b: Vector3): Vector3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
export const distance = (a: Vector3, b: Vector3): number => Math.hypot(...a.map((n, i) => n - b[i]));

export function validateSegment(segment: TrajectorySegment): void {
  if (!segment.objectId || !segment.parentId || segment.objectId === segment.parentId ||
      segment.frame !== "ICRF" || segment.timeScale !== "UTC" || segment.units !== "KM-S" ||
      !segment.source || !Array.isArray(segment.samples) || segment.samples.length < 2) {
    throw new Error("Invalid trajectory metadata");
  }
  let previous = -Infinity;
  for (const sample of segment.samples) {
    if (!Number.isSafeInteger(sample.utcMs) || sample.utcMs <= previous ||
        !finiteVector(sample.positionKm) || !finiteVector(sample.velocityKmS)) {
      throw new Error("Invalid or unordered trajectory sample");
    }
    previous = sample.utcMs;
  }
}

// A segment is a continuous, validated coverage interval. Split at gaps or manoeuvres upstream.
export function evaluate(segment: TrajectorySegment, utcMs: number): StateVector {
  validateSegment(segment);
  const samples = segment.samples;
  if (!Number.isFinite(utcMs) || utcMs < samples[0].utcMs || utcMs > samples.at(-1)!.utcMs) {
    throw new RangeError("Time outside trajectory coverage");
  }
  let low = 0;
  let high = samples.length - 1;
  while (high - low > 1) {
    const mid = (low + high) >>> 1;
    if (samples[mid].utcMs <= utcMs) low = mid;
    else high = mid;
  }
  const a = samples[low];
  const b = samples[high];
  const dt = (b.utcMs - a.utcMs) / 1000;
  const t = (utcMs - a.utcMs) / (b.utcMs - a.utcMs);
  const t2 = t * t;
  const t3 = t2 * t;
  const positionKm = a.positionKm.map((p, i) =>
    (2 * t3 - 3 * t2 + 1) * p + (t3 - 2 * t2 + t) * dt * a.velocityKmS[i] +
    (-2 * t3 + 3 * t2) * b.positionKm[i] + (t3 - t2) * dt * b.velocityKmS[i]) as unknown as Vector3;
  const velocityKmS = a.positionKm.map((p, i) =>
    ((6 * t2 - 6 * t) * p + (3 * t2 - 4 * t + 1) * dt * a.velocityKmS[i] +
    (-6 * t2 + 6 * t) * b.positionKm[i] + (3 * t2 - 2 * t) * dt * b.velocityKmS[i]) / dt) as unknown as Vector3;
  return { utcMs, positionKm, velocityKmS };
}

export function evaluateWorld(
  id: string, utcMs: number, segments: readonly TrajectorySegment[], rootId = "sun", visiting = new Set<string>(),
): StateVector {
  if (id === rootId) return { utcMs, positionKm: [0, 0, 0], velocityKmS: [0, 0, 0] };
  if (visiting.has(id)) throw new Error("Cyclic parent hierarchy");
  const matches = segments.filter(s => s.objectId === id && s.samples.length >= 2 &&
    utcMs >= s.samples[0].utcMs && utcMs <= s.samples.at(-1)!.utcMs);
  if (matches.length !== 1) throw new Error("Missing or ambiguous trajectory coverage");
  const segment = matches[0];
  const local = evaluate(segment, utcMs);
  const next = new Set(visiting).add(id);
  const parent = evaluateWorld(segment.parentId, utcMs, segments, rootId, next);
  return { utcMs, positionKm: add(parent.positionKm, local.positionKm), velocityKmS: add(parent.velocityKmS, local.velocityKmS) };
}

// A right-handed axis change, shared by paths and meshes; no per-moon flattening.
export function toScene(position: Vector3, kmPerUnit: number): Vector3 {
  if (!Number.isFinite(kmPerUnit) || kmPerUnit <= 0 || !finiteVector(position)) throw new Error("Invalid display scale");
  return [position[0] / kmPerUnit, position[2] / kmPerUnit, -position[1] / kmPerUnit];
}

export function samplePath(segment: TrajectorySegment, times: readonly number[], kmPerUnit: number): Vector3[] {
  return times.map(time => toScene(evaluate(segment, time).positionKm, kmPerUnit));
}
