import { distance, type Vector3 } from "./astronomy.ts";

export interface SphereBounds { center: Vector3; radius: number }
export interface CameraFit {
  target: Vector3;
  distance: number;
  near: number;
  far: number;
  radius: number;
}

// Fit individual spheres against the four frustum planes, rather than enclosing
// a flat ring system in one unnecessarily large sphere.
export function fitOrientedCamera(
  objects: readonly SphereBounds[], width: number, height: number, direction: Vector3,
  verticalFovDegrees = 32, fill = 0.7,
): CameraFit {
  const base = fitCamera(objects, width, height, verticalFovDegrees, fill);
  const length = Math.hypot(...direction);
  if (!direction.every(Number.isFinite) || length < 1e-9) throw new Error("Invalid viewing direction");
  const forward = direction.map(n => n / length) as unknown as Vector3;
  const rightLength = Math.hypot(forward[2], forward[0]);
  if (rightLength < 1e-9) throw new Error("Viewing direction parallel to camera up");
  const right: Vector3 = [forward[2] / rightLength, 0, -forward[0] / rightLength];
  const up: Vector3 = [forward[1] * right[2], forward[2] * right[0] - forward[0] * right[2], -forward[1] * right[0]];
  const dot = (a: Vector3, b: Vector3) => a.reduce((sum, n, i) => sum + n * b[i], 0);
  const tanY = Math.tan(verticalFovDegrees * Math.PI / 360) * fill;
  const tanX = tanY * width / height;
  const projected = objects.map(object => {
    const offset = object.center.map((n, i) => n - base.target[i]) as unknown as Vector3;
    return { x: dot(offset, right), y: dot(offset, up), z: dot(offset, forward), radius: object.radius };
  });
  const distance = Math.max(...projected.map(p => Math.max(
    p.z + Math.abs(p.x) / tanX + p.radius * Math.sqrt(1 + 1 / tanX ** 2),
    p.z + Math.abs(p.y) / tanY + p.radius * Math.sqrt(1 + 1 / tanY ** 2),
  )));
  return { ...base, distance,
    near: Math.max(0.001, Math.min(...projected.map(p => distance - p.z - p.radius)) / 2),
    far: Math.max(...projected.map(p => distance - p.z + p.radius)) * 1.2,
  };
}

// width/height describe the usable render viewport, excluding safety and caption areas.
export function fitCamera(
  objects: readonly SphereBounds[], width: number, height: number, verticalFovDegrees = 32, fill = 0.7,
): CameraFit {
  if (!objects.length || ![width, height, verticalFovDegrees, fill].every(Number.isFinite) ||
      width <= 0 || height <= 0 || verticalFovDegrees <= 0 || verticalFovDegrees >= 170 || fill <= 0 || fill >= 1) {
    throw new Error("Invalid camera viewport");
  }
  const min = [Infinity, Infinity, Infinity];
  const max = [-Infinity, -Infinity, -Infinity];
  for (const object of objects) {
    if (!Number.isFinite(object.radius) || object.radius <= 0 || object.center.length !== 3 || !object.center.every(Number.isFinite)) {
      throw new Error("Invalid scene bounds");
    }
    object.center.forEach((value, axis) => {
      min[axis] = Math.min(min[axis], value - object.radius);
      max[axis] = Math.max(max[axis], value + object.radius);
    });
  }
  const target = min.map((value, axis) => (value + max[axis]) / 2) as unknown as Vector3;
  const radius = Math.max(...objects.map(object => distance(target, object.center) + object.radius));
  const tanY = Math.tan(verticalFovDegrees * Math.PI / 360);
  const tanLimit = Math.min(tanY, tanY * width / height) * fill;
  const cameraDistance = radius * Math.sqrt(1 + 1 / (tanLimit * tanLimit));
  return {
    target, radius, distance: cameraDistance,
    near: Math.max(radius * 0.001, (cameraDistance - radius) * 0.5),
    far: cameraDistance + radius * 2,
  };
}

export interface MotionSample { value: number; velocity: number; acceleration: number }
export interface Motion {
  startMs: number;
  durationMs: number;
  initial: MotionSample;
  target: number;
}

// Quintic boundary conditions preserve position, velocity and acceleration when retargeted.
export function motionAt(motion: Motion, nowMs: number): MotionSample {
  const { startMs, durationMs, initial, target } = motion;
  if (![startMs, durationMs, initial.value, initial.velocity, initial.acceleration, target, nowMs].every(Number.isFinite) || durationMs <= 0) {
    throw new Error("Invalid camera motion");
  }
  if (nowMs <= startMs) return { ...initial };
  if (nowMs >= startMs + durationMs) return { value: target, velocity: 0, acceleration: 0 };
  const seconds = durationMs / 1000;
  const t = (nowMs - startMs) / durationMs;
  const c0 = initial.value;
  const c1 = initial.velocity * seconds;
  const c2 = initial.acceleration * seconds * seconds / 2;
  const b = target - c0 - c1 - c2;
  const c = -c1 - 2 * c2;
  const d = -2 * c2;
  const c3 = 10 * b - 4 * c + d / 2;
  const c4 = -15 * b + 7 * c - d;
  const c5 = 6 * b - 3 * c + d / 2;
  return {
    value: c0 + c1 * t + c2 * t ** 2 + c3 * t ** 3 + c4 * t ** 4 + c5 * t ** 5,
    velocity: (c1 + 2 * c2 * t + 3 * c3 * t ** 2 + 4 * c4 * t ** 3 + 5 * c5 * t ** 4) / seconds,
    acceleration: (2 * c2 + 6 * c3 * t + 12 * c4 * t ** 2 + 20 * c5 * t ** 3) / seconds ** 2,
  };
}

export function retarget(motion: Motion, nowMs: number, target: number, durationMs = 24000): Motion {
  const next = { startMs: nowMs, durationMs, initial: motionAt(motion, nowMs), target };
  motionAt(next, nowMs);
  return next;
}
