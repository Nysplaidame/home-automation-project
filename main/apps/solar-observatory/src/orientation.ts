import { toScene, type Vector3 } from "./astronomy.ts";

export type OrientedBody = "earth" | "moon";
export interface BodyAxes { x: Vector3; y: Vector3; z: Vector3 }
const J2000 = Date.UTC(2000, 0, 1, 12);
export const ORIENTATION_START_MS = Date.UTC(2017, 0, 1);
// IERS Bulletin C 72: no leap second at December 2026; next decision June 2027.
export const ORIENTATION_END_MS = Date.UTC(2027, 6, 1);
const radians = (degrees: number) => (degrees % 360) * Math.PI / 180;

/** NAIF naif0012 DELTET approximation; deliberately bounded leap-second coverage. */
export function utcToTdbSeconds(utcMs: number): number {
  if (!Number.isSafeInteger(utcMs) || utcMs < ORIENTATION_START_MS || utcMs >= ORIENTATION_END_MS) {
    throw new RangeError("Orientation time is outside verified leap-second coverage");
  }
  const tt = (utcMs - J2000) / 1000 + 37 + 32.184;
  let tdb = tt;
  for (let i = 0; i < 3; i++) {
    const m = 6.239996 + 1.99096871e-7 * tdb;
    tdb = tt + 0.001657 * Math.sin(m + 0.01671 * Math.sin(m));
  }
  return tdb;
}

// pck00011 BODY3_NUT_PREC_ANGLES, in degrees and degrees/Julian century.
const lunarAngles = [
  [125.045, -1935.5364525], [250.089, -3871.072905],
  [260.008, 475263.3328725], [176.625, 487269.629985],
  [357.529, 35999.0509575], [311.589, 964468.49931],
  [134.963, 477198.869325], [276.617, 12006.300765],
  [34.226, 63863.5132425], [15.134, -5806.6093575],
  [119.743, 131.84064], [239.961, 6003.1503825], [25.053, 473327.79642],
];
const lunarRa = [-3.8787, -0.1204, 0.0700, -0.0172, 0, 0.0072, 0, 0, 0, -0.0052, 0, 0, 0.0043];
const lunarDec = [1.5419, 0.0239, -0.0278, 0.0068, 0, -0.0029, 0.0009, 0, 0, 0.0008, 0, 0, -0.0009];
const lunarW = [3.5610, 0.1208, -0.0642, 0.0158, 0.0252, -0.0066, -0.0047, -0.0046, 0.0028, 0.0052, 0.0040, 0.0019, -0.0044];

/** Body-fixed prime-meridian/east/north axes expressed in ICRF. Not an EOP solution. */
export function bodyAxes(body: OrientedBody, utcMs: number): BodyAxes {
  const days = utcToTdbSeconds(utcMs) / 86400;
  const centuries = days / 36525;
  let ra: number, dec: number, w: number;
  if (body === "earth") {
    ra = -0.641 * centuries;
    dec = 90 - 0.557 * centuries;
    w = 190.147 + 360.9856235 * days;
  } else if (body === "moon") {
    ra = 269.9949 + 0.0031 * centuries;
    dec = 66.5392 + 0.0130 * centuries;
    w = 38.3213 + 13.17635815 * days - 1.4e-12 * days * days;
    lunarAngles.forEach(([base, rate], i) => {
      const angle = radians(base + rate * centuries);
      ra += lunarRa[i] * Math.sin(angle);
      dec += lunarDec[i] * Math.cos(angle);
      w += lunarW[i] * Math.sin(angle);
    });
  } else throw new Error("Unsupported orientation body");
  const a = radians(ra), d = radians(dec), meridian = radians(w);
  const sa = Math.sin(a), ca = Math.cos(a), sd = Math.sin(d), cd = Math.cos(d);
  const sw = Math.sin(meridian), cw = Math.cos(meridian);
  // Transpose of SPICE's inertial-to-body R3(W) R1(90-Dec) R3(90+RA).
  return {
    x: [-sa * cw - ca * sd * sw, ca * cw - sa * sd * sw, cd * sw],
    y: [sa * sw - ca * sd * cw, -ca * sw - sa * sd * cw, cd * cw],
    z: [ca * cd, sa * cd, sd],
  };
}

/** Three sphere UV: map centre = +X, north = +Y, east = -Z. */
export function surfaceAxes(body: OrientedBody, utcMs: number): BodyAxes {
  const axes = bodyAxes(body, utcMs);
  return {
    x: toScene(axes.x, 1),
    y: toScene(axes.z, 1),
    z: toScene(axes.y.map(value => -value) as unknown as Vector3, 1),
  };
}
