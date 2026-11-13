import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { normalizeWorkbook, buildEmergencyPack } from './models.js';

export function documentPath(value) {
  if (typeof value !== 'string' || value.length > 240
      || !/^main\/[A-Za-z0-9_./-]+\.md$/.test(value)
      || value.split('/').some(segment => segment === '..' || segment === '.')) {
    throw new Error('Recovery references must be vault-relative main Markdown paths.');
  }
  return value;
}

export function createRecoveryPack(input) {
  const workbook = normalizeWorkbook(input);
  const lines = [buildEmergencyPack(workbook),
    '## Scope and source index', '',
    'Historical success is not current freshness or full-system recovery. Missing facts remain unknown.', '',
    'Open the following paths from the canonical vault root; no network or credentials are needed.', '',
  ];
  for (const reference of (input.sourceRecords ?? []).slice(0, 20)) {
    lines.push(`- Source: ${documentPath(reference)}`);
  }
  const systems = input.recovery?.systems ?? [];
  for (const system of workbook.recovery) {
    const original = systems.find(item => item.id === system.id);
    lines.push('', `### ${system.label}`);
    for (const kind of ['backup', 'integrity', 'restore']) {
      const detail = system[kind].detail;
      if (detail && detail !== 'Sensitive detail omitted.') lines.push(`- ${kind}: ${detail}`);
    }
    if (original?.runbookPath) lines.push(`- Vault runbook: ${documentPath(original.runbookPath)}`);
    if (system.dependencies.length) lines.push(`- Dependencies to check first: ${system.dependencies.join(', ')}`);
  }
  return lines.join('\n') + '\n';
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const [inputPath, outputPath, ...extra] = process.argv.slice(2);
    if (!inputPath || !outputPath || extra.length) throw new Error('Usage: node recovery-pack.mjs INPUT.json OUTPUT.md');
    const bytes = await readFile(inputPath);
    if (bytes.length > 512 * 1024) throw new Error('Recovery snapshots are limited to 512 KB.');
    const input = JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/, ''));
    await writeFile(outputPath, createRecoveryPack(input), { flag: 'wx' });
    console.log('Created offline recovery index; existing output is never overwritten.');
  } catch (error) {
    console.error(error instanceof SyntaxError ? 'Input is not valid JSON.'
      : error.code ? `File operation failed (${error.code}).` : error.message);
    process.exitCode = 1;
  }
}
