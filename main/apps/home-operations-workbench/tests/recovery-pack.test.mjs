import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile, access } from 'node:fs/promises';
import { normalizeWorkbook, recoveryAssessment } from '../models.js';
import { createRecoveryPack } from '../recovery-pack.mjs';

const snapshot = JSON.parse(await readFile(new URL('../evidence/recovery-2026-10-02.json', import.meta.url)));
const vaultRoot = new URL('../../../../', import.meta.url);

test('curated historical records never certify complete recovery or invent household data', async () => {
  const workbook = normalizeWorkbook(snapshot);
  assert.equal(workbook.recovery.length, 7);
  for (const system of workbook.recovery) {
    assert.equal(system.backup.status, 'stale');
    assert.equal(system.restore.status, 'unknown');
    assert.notEqual(recoveryAssessment(system), 'proved');
  }
  for (const rows of Object.values(workbook.today)) assert.equal(rows.length, 0);
  for (const source of snapshot.sourceRecords) await access(new URL(source, vaultRoot));
  for (const system of snapshot.recovery.systems) await access(new URL(system.runbookPath, vaultRoot));
  const pack = createRecoveryPack(snapshot);
  assert.match(pack, /NIC-free temporary VM9102 boot/);
  assert.match(pack, /full external integrations/);
  assert.match(pack, /Vault runbook: main\/docs/);
  assert.doesNotMatch(pack, /Recovery confidence: proved/);
});

test('recovery export rejects escaping paths and omits sensitive evidence', () => {
  for (const reference of ['../outside.md', 'main/../../outside.md', 'main/.env', 'https://example.com/runbook.md']) {
    assert.throws(() => createRecoveryPack({ ...snapshot, sourceRecords: [reference] }), /vault-relative/);
  }
  const altered = structuredClone(snapshot);
  altered.recovery.systems[0].backup.detail = 'password: do-not-export';
  assert.doesNotMatch(createRecoveryPack(altered), /do-not-export|Sensitive detail omitted/);
});
