import { open, writeFile } from 'node:fs/promises';
import { adaptGrocyOverview } from './grocy-adapter.js';

const [input, output, ...extra] = process.argv.slice(2);
let source;
try {
  if (!input || !output || extra.length) throw new Error('Usage: node import-grocy.mjs INPUT.json OUTPUT.json');
  source = await open(input, 'r');
  const bytes = Buffer.alloc(512 * 1024 + 1);
  let bytesRead = 0;
  while (bytesRead < bytes.length) {
    const result = await source.read(bytes, bytesRead, bytes.length - bytesRead, bytesRead);
    if (!result.bytesRead) break;
    bytesRead += result.bytesRead;
  }
  if (bytesRead > 512 * 1024) throw new Error('Saved overviews are limited to 512 KB.');
  const workbook = adaptGrocyOverview(JSON.parse(bytes.subarray(0, bytesRead).toString('utf8').replace(/^\uFEFF/, '')));
  await writeFile(output, JSON.stringify(workbook, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
  console.log('Created offline evidence file; source notes and unknown fields excluded.');
} catch (error) {
  console.error(error instanceof SyntaxError ? 'Input is not valid JSON.' : error.code ? `File operation failed (${error.code}).` : error.message);
  process.exitCode = 1;
} finally {
  await source?.close();
}
