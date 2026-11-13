import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, rename, writeFile, unlink } from "node:fs/promises";
import { join } from "node:path";
import { validateSegment, type TrajectorySegment } from "./astronomy.ts";

export interface EphemerisBundle {
  version: 1;
  generatedAtMs: number;
  segments: TrajectorySegment[];
}

export function validateBundle(bundle: EphemerisBundle): void {
  if (bundle.version !== 1 || !Number.isSafeInteger(bundle.generatedAtMs) ||
      !Array.isArray(bundle.segments) || !bundle.segments.length) throw new Error("Invalid bundle");
  const ids = new Set<string>();
  for (const segment of bundle.segments) {
    validateSegment(segment);
    if (ids.has(segment.objectId)) throw new Error("Duplicate object in refresh bundle");
    ids.add(segment.objectId);
  }
  for (const segment of bundle.segments) {
    const chain = new Set<string>();
    let current = segment;
    while (current.parentId !== "sun") {
      if (chain.has(current.objectId)) throw new Error("Cyclic bundle hierarchy");
      chain.add(current.objectId);
      const parent = bundle.segments.find(s => s.objectId === current.parentId);
      if (!parent || parent.samples[0].utcMs > current.samples[0].utcMs ||
          parent.samples.at(-1)!.utcMs < current.samples.at(-1)!.utcMs) throw new Error("Parent coverage missing");
      current = parent;
    }
  }
}

// Same-directory renames: readers see either the previous manifest or the new one.
// Network-share atomicity is a deployment gate; this prototype uses local storage only.
export async function publishBundle(directory: string, bundle: EphemerisBundle): Promise<string> {
  validateBundle(bundle);
  const contents = JSON.stringify(bundle) + "\n";
  const hash = createHash("sha256").update(contents).digest("hex");
  const filename = `bundle-${hash}.json`;
  await mkdir(directory, { recursive: true });
  await writeFile(join(directory, filename), contents, { flag: "wx" }).catch(error => {
    if (error.code !== "EEXIST") throw error;
  });
  // Never point the manifest at a damaged pre-existing content-addressed file.
  const stored = await readFile(join(directory, filename));
  if (createHash("sha256").update(stored).digest("hex") !== hash) throw new Error("Cached bundle checksum mismatch");
  const temporary = join(directory, `manifest-${randomUUID()}.tmp`);
  try {
    await writeFile(temporary, JSON.stringify({ version: 1, filename, sha256: hash }) + "\n", { flag: "wx" });
    await rename(temporary, join(directory, "current.json"));
  } finally {
    await unlink(temporary).catch(error => { if (error.code !== "ENOENT") throw error; });
  }
  return filename;
}

export async function readCurrentBundle(directory: string): Promise<EphemerisBundle> {
  const manifest = JSON.parse(await readFile(join(directory, "current.json"), "utf8"));
  if (manifest.version !== 1 || typeof manifest.sha256 !== "string" || !/^[a-f0-9]{64}$/.test(manifest.sha256) ||
      manifest.filename !== `bundle-${manifest.sha256}.json`) throw new Error("Invalid cache manifest");
  const contents = await readFile(join(directory, manifest.filename), "utf8");
  if (createHash("sha256").update(contents).digest("hex") !== manifest.sha256) throw new Error("Cache checksum mismatch");
  const bundle = JSON.parse(contents);
  validateBundle(bundle);
  return bundle;
}
