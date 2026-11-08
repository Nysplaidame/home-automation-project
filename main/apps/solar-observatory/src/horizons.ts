import { validateSegment, type StateVector, type TrajectorySegment, type Vector3 } from "./astronomy.ts";

export interface HorizonsRequest {
  objectId: string;
  parentId: string;
  target: string;
  center: string;
  start: string;
  stop: string;
  stepMinutes: number;
}

export function requestUrl(request: HorizonsRequest): string {
  if (!/^-?\d+$/.test(request.target) || !/^500@-?\d+$/.test(request.center) ||
      !Number.isInteger(request.stepMinutes) || request.stepMinutes < 1 ||
      !/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(request.start) ||
      !/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(request.stop)) throw new Error("Invalid Horizons request");
  const params = new URLSearchParams({ format: "json" });
  const options = {
    COMMAND: request.target, CENTER: request.center, START_TIME: request.start, STOP_TIME: request.stop,
    STEP_SIZE: `${request.stepMinutes} min`, EPHEM_TYPE: "VECTORS", TIME_TYPE: "UT",
    REF_SYSTEM: "ICRF", REF_PLANE: "FRAME", OUT_UNITS: "KM-S", VEC_TABLE: "2",
    VEC_CORR: "NONE", CSV_FORMAT: "YES", OBJ_DATA: "NO", TIME_DIGITS: "FRACSEC",
  };
  for (const [key, value] of Object.entries(options)) params.set(key, `'${value}'`);
  return `https://ssd.jpl.nasa.gov/api/horizons.api?${params}`;
}

export function parseHorizons(payload: unknown, request: HorizonsRequest): TrajectorySegment {
  if (!payload || typeof payload !== "object") throw new Error("Invalid Horizons envelope");
  const data = payload as { error?: unknown; result?: unknown; signature?: { version?: unknown; source?: unknown } };
  if (data.error || data.signature?.version !== "1.2" || typeof data.result !== "string") {
    throw new Error("Horizons error or unsupported API version");
  }
  const raw = data.result;
  const target = raw.match(/^Target body name:.*?\((-?\d+)\)/m)?.[1];
  const center = raw.match(/^Center body name:.*?\((-?\d+)\)/m)?.[1];
  if (target !== request.target || center !== request.center.slice(4) ||
      !/^Reference frame\s*:\s*ICRF\s*$/m.test(raw) ||
      !/^Output units\s*:\s*KM-S\s*$/m.test(raw) ||
      !/^Start time\s*:.* UT\s*$/m.test(raw) ||
      !/^Output type\s*:\s*GEOMETRIC cartesian states\s*$/m.test(raw)) {
    throw new Error("Unexpected Horizons target, centre, frame, units or correction");
  }
  const block = raw.match(/\$\$SOE\s*([\s\S]*?)\s*\$\$EOE/)?.[1];
  if (!block) throw new Error("Missing Horizons vector table");
  const samples: StateVector[] = block.trim().split(/\r?\n/).map(line => {
    const columns = line.split(",").map(s => s.trim());
    if (columns.length !== 9 || columns.at(-1) !== "" || !columns[1].startsWith("A.D.")) {
      throw new Error("Malformed Horizons vector row");
    }
    const numbers = [columns[0], ...columns.slice(2, 8)].map(value => value === "" ? NaN : Number(value));
    if (!numbers.every(Number.isFinite)) throw new Error("Nonfinite Horizons vector");
    return {
      utcMs: Math.round((numbers[0] - 2440587.5) * 86400000),
      positionKm: numbers.slice(1, 4) as unknown as Vector3,
      velocityKmS: numbers.slice(4, 7) as unknown as Vector3,
    };
  });
  const expectedStart = Date.parse(request.start.replace(" ", "T") + ":00Z");
  const expectedStop = Date.parse(request.stop.replace(" ", "T") + ":00Z");
  if (samples[0]?.utcMs !== expectedStart || samples.at(-1)?.utcMs !== expectedStop ||
      samples.some((sample, i) => i > 0 && sample.utcMs - samples[i - 1].utcMs !== request.stepMinutes * 60000)) {
    throw new Error("Incomplete or gapped Horizons coverage");
  }
  const segment: TrajectorySegment = {
    objectId: request.objectId, parentId: request.parentId, frame: "ICRF", timeScale: "UTC", units: "KM-S",
    source: requestUrl(request), samples,
  };
  validateSegment(segment);
  return segment;
}
