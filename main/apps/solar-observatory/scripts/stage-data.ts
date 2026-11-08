import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { readCurrentBundle, validateBundle, type EphemerisBundle } from "../src/cache.ts";
import { parseHorizons } from "../src/horizons.ts";

const directory = new URL("../public/data/", import.meta.url);
await mkdir(directory, { recursive: true });
const segments = [];
for (const id of ["earth", "moon", "jupiter", "io", "saturn", "jwst"]) {
  const f = JSON.parse(await readFile(new URL(`../tests/fixtures/${id}.json`, import.meta.url), "utf8"));
  segments.push(parseHorizons(f.payload, f.request));
}
const reference: EphemerisBundle = { version: 1, generatedAtMs: segments[0].samples[0].utcMs, segments };
validateBundle(reference);
await writeFile(new URL("reference.json", directory), JSON.stringify(reference));
let current: EphemerisBundle | null = null;
try {
  current = await readCurrentBundle(fileURLToPath(new URL("../.cache/ephemerides/", import.meta.url)));
} catch (error) {
  console.warn("Current cache unavailable; preview will identify reference replay.", String(error));
}
// Overwrite missing/invalid current data with null, never leave a previously staged generation behind.
await writeFile(new URL("current.json", directory), JSON.stringify(current));
