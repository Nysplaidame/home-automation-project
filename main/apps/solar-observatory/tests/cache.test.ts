import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve, dirname, basename } from "node:path";
import { publishBundle, readCurrentBundle, validateBundle, type EphemerisBundle } from "../src/cache.ts";
import { parseHorizons } from "../src/horizons.ts";

async function cleanup(directory: string): Promise<void> {
  const absolute = resolve(directory);
  if (dirname(absolute) !== resolve(tmpdir()) || !/^observatory-test-[a-zA-Z0-9]+$/.test(basename(absolute))) {
    throw new Error("Refusing cleanup outside the allocated test directory");
  }
  await rm(absolute, { recursive: true, force: true });
}

async function fixture(): Promise<EphemerisBundle> {
  const f = JSON.parse(await readFile(new URL("./fixtures/earth.json", import.meta.url), "utf8"));
  return { version: 1, generatedAtMs: 1791072000000, segments: [parseHorizons(f.payload, f.request)] };
}

test("local manifest publication round-trips; rejected refresh leaves previous generation readable", async () => {
  const directory = await mkdtemp(join(tmpdir(), "observatory-test-"));
  try {
    const bundle = await fixture();
    const first = await publishBundle(directory, bundle);
    assert.deepEqual(await readCurrentBundle(directory), bundle);
    const before = await readFile(join(directory, "current.json"), "utf8");
    await assert.rejects(publishBundle(directory, { ...bundle, segments: [] }));
    assert.equal(await readFile(join(directory, "current.json"), "utf8"), before);
    assert.equal(await publishBundle(directory, bundle), first);
    const updated = { ...bundle, generatedAtMs: bundle.generatedAtMs + 1000 };
    assert.notEqual(await publishBundle(directory, updated), first);
    assert.deepEqual(await readCurrentBundle(directory), updated);
    await writeFile(join(directory, first), "corrupted");
    await assert.rejects(publishBundle(directory, bundle), /checksum/);
    assert.deepEqual(await readCurrentBundle(directory), updated);
  } finally { await cleanup(directory); }
});

test("manifest cannot traverse directories or conceal corrupted data", async () => {
  const directory = await mkdtemp(join(tmpdir(), "observatory-test-"));
  try {
    const filename = await publishBundle(directory, await fixture());
    await writeFile(join(directory, filename), "{}");
    await assert.rejects(readCurrentBundle(directory), /checksum/);
    await writeFile(join(directory, "current.json"), JSON.stringify({ version: 1, filename: "../secret.json", sha256: "0".repeat(64) }));
    await assert.rejects(readCurrentBundle(directory), /manifest/);
  } finally { await cleanup(directory); }
});

test("refresh bundles require unambiguous parent coverage", async () => {
  const bundle = await fixture();
  assert.throws(() => validateBundle({ ...bundle, segments: [...bundle.segments, ...bundle.segments] }));
  assert.throws(() => validateBundle({ ...bundle, segments: [{ ...bundle.segments[0], parentId: "missing" }] }));
});
