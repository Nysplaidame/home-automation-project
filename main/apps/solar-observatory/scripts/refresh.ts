import { resolve } from "node:path";
import { mkdir, open, unlink } from "node:fs/promises";
import { parseHorizons, requestUrl, type HorizonsRequest } from "../src/horizons.ts";
import { publishBundle } from "../src/cache.ts";
import type { TrajectorySegment } from "../src/astronomy.ts";

// Deliberately local-only until hosting, Samba publication and scheduling are accepted.
const directory = resolve(import.meta.dirname, "../.cache/ephemerides");
await mkdir(directory, { recursive: true });
const lockPath = resolve(directory, "refresh.lock");
const lock = await open(lockPath, "wx");
try {
  const now = Date.now();
  const startMs = Math.floor(now / 86400000) * 86400000;
  const calendar = (ms: number) => new Date(ms).toISOString().slice(0, 16).replace("T", " ");
  const targets = [
    ["earth", "sun", "399", "500@10", 7], ["moon", "earth", "301", "500@399", 7],
    ["jupiter", "sun", "599", "500@10", 7], ["io", "jupiter", "501", "500@599", 7],
    ["saturn", "sun", "699", "500@10", 7], ["jwst", "earth", "-170", "500@399", 2],
  ] as const;
  const segments: TrajectorySegment[] = [];
  for (const [objectId, parentId, target, center, days] of targets) {
    const request: HorizonsRequest = {
      objectId, parentId, target, center, start: calendar(startMs), stop: calendar(startMs + days * 86400000), stepMinutes: 5,
    };
    const response = await fetch(requestUrl(request), { signal: AbortSignal.timeout(30000) });
    if (!response.ok) throw new Error(`Horizons HTTP ${response.status}; old manifest retained`);
    const segment = parseHorizons(await response.json(), request);
    segments.push(segment);
    console.log(`${objectId}: ${segment.samples.length} samples`);
  }
  const filename = await publishBundle(directory, { version: 1, generatedAtMs: now, segments });
  console.log(`Published local cache ${filename}; no live deployment changed.`);
} finally {
  await lock.close();
  await unlink(lockPath);
}
