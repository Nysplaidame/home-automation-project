import { readFile, writeFile } from 'node:fs/promises';
import { adaptHealthSnapshot } from './health-adapter.js';

const [input, output, timestampOffset, ...extra] = process.argv.slice(2);
try {
  if (!input || !output || extra.length) throw new Error('Usage: node import-health.mjs INPUT.json OUTPUT.json [COLLECTOR_OFFSET]');
  const bytes = await readFile(input);
  if (bytes.length > 512 * 1024) throw new Error('Health snapshots are limited to 512 KB.');
  const workbook = adaptHealthSnapshot(JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/, '')), { timestampOffset });
  await writeFile(output, JSON.stringify(workbook, null, 2) + '\n', { flag: 'wx' });
  console.log('Created offline evidence file. Existing files are never overwritten.');
} catch (error) {
  // Never echo a malformed JSON payload or a source filename that may be sensitive.
  console.error(error instanceof SyntaxError ? 'Input is not valid JSON.' : error.code ? `File operation failed (${error.code}).` : error.message);
  process.exitCode = 1;
}
