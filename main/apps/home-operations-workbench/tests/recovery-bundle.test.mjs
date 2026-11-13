import assert from 'node:assert/strict';
import test from 'node:test';
import { mkdtemp, mkdir, readFile, writeFile, rm, symlink } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { createRecoveryBundle, verifyRecoveryBundle } from '../recovery-bundle.mjs';

async function setup() {
  const parent = await mkdtemp(path.join(os.tmpdir(), 'recovery-bundle-'));
  const vault = path.join(parent, 'vault'), output = path.join(parent, 'pack');
  await mkdir(path.join(vault, 'main/docs'), { recursive: true });
  const input = { schemaVersion: '1.0', sourceRecords: ['main/docs/source.md'],
    recovery: { systems: [{ id: 'example', label: 'Synthetic system', runbookPath: 'main/docs/runbook.md',
      backup: { status: 'stale', detail: 'Historical only.' }, restore: { status: 'unknown' } }] } };
  await writeFile(path.join(vault, 'main/docs/source.md'), '# Source\n');
  await writeFile(path.join(vault, 'main/docs/runbook.md'),
    '# Runbook\n[[source|Source]]\n[Source](source.md#source)\n[Config](../config.yaml)\n[Online](https://example.test/)\n' +
    '```sh\nread -s -p \'RTSP password: \' rtsp_password\n[Example](not-a-reference.md)\n```\n');
  return { parent, vault, output, input, options: { support: [] } };
}

test('portable bundle includes selected documents, disables missing links and preserves commands', async () => {
  const f = await setup();
  try {
    const result = await createRecoveryBundle(f.input, f.vault, f.output, f.options);
    assert.equal(result.documents, 2); assert.equal(result.unbundledReferences, 1);
    const text = await readFile(path.join(f.output, 'main/docs/runbook.md'), 'utf8');
    assert.match(text, /\[Source\]\(source.md\)/);
    assert.match(text, /\[Source\]\(source.md#source\)/);
    assert.match(text, /Config \(not bundled/);
    assert.match(text, /\[Example\]\(not-a-reference.md\)/);
    assert.match(await readFile(path.join(f.output, 'recovery-index.md'), 'utf8'), /\[main\/docs\/runbook.md\]\(main\/docs\/runbook.md\)/);
    const manifest = JSON.parse(await readFile(path.join(f.output, 'manifest.json')));
    assert.equal(manifest.links.length, 4);
    const changed = manifest.documents.find(document => document.path === 'main/docs/runbook.md');
    assert.notEqual(changed.originalSha256, changed.bundledSha256);
    assert.equal((await verifyRecoveryBundle(f.output)).verifiedFiles, 6);
    const moved = path.join(f.parent, 'offline-copy');
    // A moved directory, rather than original vault availability, is sufficient.
    await rm(f.vault, { recursive: true });
    const { rename } = await import('node:fs/promises'); await rename(f.output, moved);
    assert.equal((await verifyRecoveryBundle(moved)).verifiedFiles, 6);
    await writeFile(path.join(moved, 'unexpected.sh'), 'not part of bundle');
    await assert.rejects(verifyRecoveryBundle(moved), /Unexpected file/);
    await rm(path.join(moved, 'unexpected.sh'));
    await writeFile(path.join(moved, 'main/docs/source.md'), 'tampered');
    await assert.rejects(verifyRecoveryBundle(moved), /checksum mismatch/);
  } finally { await rm(f.parent, { recursive: true, force: true }); }
});

test('bundle refuses existing output, inside-vault output and unsafe source paths', async () => {
  const f = await setup();
  try {
    await assert.rejects(createRecoveryBundle(f.input, f.vault, path.join(f.vault, 'pack'), f.options), /outside the vault/);
    await assert.rejects(createRecoveryBundle({ ...f.input, sourceRecords: ['main/../outside.md'] }, f.vault, f.output, f.options), /vault-relative/);
    await createRecoveryBundle(f.input, f.vault, f.output, f.options);
    const original = await readFile(path.join(f.output, 'SHA256SUMS'));
    await assert.rejects(createRecoveryBundle(f.input, f.vault, f.output, f.options), { code: 'EEXIST' });
    assert.deepEqual(await readFile(path.join(f.output, 'SHA256SUMS')), original);
    await writeFile(path.join(f.output, 'SHA256SUMS'), 'a'.repeat(64) + '  ../outside.md\n');
    await assert.rejects(verifyRecoveryBundle(f.output), /Invalid bundle checksum path/);
  } finally { await rm(f.parent, { recursive: true, force: true }); }
});

test('credential candidates and missing or oversized sources fail before publication', async () => {
  const f = await setup();
  try {
    for (const text of ['-----BEGIN OPENSSH PRIVATE KEY-----', 'password: "PRIVATE-MARKER"',
      'https://user:PRIVATE-MARKER@example.test/', 'https://example.test/?token=PRIVATE-MARKER', ' '.repeat(512 * 1024 + 1)]) {
      await writeFile(path.join(f.vault, 'main/docs/source.md'), text);
      await assert.rejects(createRecoveryBundle(f.input, f.vault, f.output, f.options), error => {
        assert.doesNotMatch(error.message, /PRIVATE-MARKER/); return true;
      });
      await assert.rejects(readFile(path.join(f.output, 'COMPLETE')), { code: 'ENOENT' });
    }
    await rm(path.join(f.vault, 'main/docs/source.md'));
    await assert.rejects(createRecoveryBundle(f.input, f.vault, f.output, f.options), { code: 'ENOENT' });
  } finally { await rm(f.parent, { recursive: true, force: true }); }
});

test('symlinked source ancestors are refused (Windows junction included)', async t => {
  const f = await setup();
  try {
    try { await symlink(path.join(f.vault, 'main/docs'), path.join(f.vault, 'main/linked'), process.platform === 'win32' ? 'junction' : 'dir'); }
    catch (error) { if (error.code === 'EPERM') { t.skip('Windows symlink privilege unavailable'); return; } throw error; }
    f.input.sourceRecords = ['main/linked/source.md'];
    await assert.rejects(createRecoveryBundle(f.input, f.vault, f.output, f.options), /Symlinked/);
  } finally { await rm(f.parent, { recursive: true, force: true }); }
});
