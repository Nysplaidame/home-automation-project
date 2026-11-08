import { mkdir, writeFile } from "node:fs/promises";
import { requestUrl, parseHorizons, type HorizonsRequest } from "../src/horizons.ts";

const targets = [
  ["earth", "sun", "399", "500@10"],
  ["moon", "earth", "301", "500@399"],
  ["jupiter", "sun", "599", "500@10"],
  ["io", "jupiter", "501", "500@599"],
  ["saturn", "sun", "699", "500@10"],
  ["jwst", "earth", "-170", "500@399"],
];
const directory = new URL("../tests/fixtures/", import.meta.url);
await mkdir(directory, { recursive: true });
// Explicit maintainer command only. Unit tests never call the network.
for (const [objectId, parentId, target, center] of targets) {
  const request: HorizonsRequest = {
    objectId, parentId, target, center, start: "2026-10-04 00:00", stop: "2026-10-04 02:00", stepMinutes: 5,
  };
  const url = requestUrl(request);
  const response = await fetch(url, { signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`Horizons HTTP ${response.status}; capture stopped`);
  const payload: unknown = await response.json();
  const segment = parseHorizons(payload, request);
  await writeFile(new URL(`${objectId}.json`, directory), JSON.stringify({
    capturedAt: new Date().toISOString(), request, payload,
  }, null, 2) + "\n");
  console.log(`${objectId}: ${segment.samples.length} validated samples`);
}
