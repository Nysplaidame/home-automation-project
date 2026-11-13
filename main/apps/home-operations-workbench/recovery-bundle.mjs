import { constants } from 'node:fs';
import { open, lstat, realpath, mkdir, writeFile, readFile, readdir, unlink } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { createRecoveryPack, documentPath } from './recovery-pack.mjs';
import { normalizeWorkbook } from './models.js';

const SUPPORT = [
  'main/docs/install/phases/02-proxmox-host.md',
  'main/docs/install/phases/06-omv-nas.md',
  'main/scripts/backup/backup_strategy.md',
  'main/docs/reference/current-live-state.md',
  'main/docs/procedures/household-hub-coordinated-backup.md',
];
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const COMPLETE = 'Selected documents copied and checksums verified; not restore proof.\n';
const inside = (root, candidate) => {
  const relative = path.relative(root, candidate);
  return relative === '' || (!relative.startsWith('..' + path.sep) && relative !== '..' && !path.isAbsolute(relative));
};

export async function boundedRead(filename) {
  const handle = await open(filename, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
  try {
    if (!(await handle.stat()).isFile()) throw new Error('Bundle input must be a regular file.');
    const buffer = Buffer.alloc(512 * 1024 + 1);
    let length = 0;
    while (length < buffer.length) {
      const { bytesRead } = await handle.read(buffer, length, buffer.length - length, length);
      if (!bytesRead) break;
      length += bytesRead;
    }
    if (length > 512 * 1024) throw new Error('Bundle files are limited to 512 KB.');
    return buffer.subarray(0, length);
  } finally { await handle.close(); }
}

function rejectCredentials(text, document) {
  if (/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/.test(text)
      || /\bBearer\s+[A-Za-z0-9_.-]{20,}/i.test(text)
      || /https?:\/\/[^\s/@]+:[^\s/@]+@/i.test(text)) {
    throw new Error('Potential credential material in selected document; no bundle published.');
  }
  const literals = /(?:^|[,{])[ \t]*["']?[a-z0-9_]*(?:password|passphrase|token|secret|api[_-]?key)(?:_[a-z0-9]+)*["']?\s*[:=]\s*(["'])(.*?)\1/gim;
  for (const match of text.matchAll(literals)) {
    const value = match[2];
    if (value && !/[<$>{}]/.test(value) && !/^(?:REDACTED|CHANGE[_-]?ME|REPLACE[_-].*|\.{3})$/i.test(value)) {
      const line = text.slice(0, match.index).split('\n').length;
      throw new Error(`Potential credential literal in ${document}:${line}; no bundle published.`);
    }
  }
  for (const match of text.matchAll(/[?&](?:token|api[_-]?key|password|secret)=([^\s&#)]+)/gi)) {
    if (!/[<$>{}]/.test(match[1])) throw new Error('Potential credential URL in selected document; no bundle published.');
  }
}

function rewriteLinks(text, document, selected, links) {
  let fence = '';
  function resolve(target, wiki) {
    if (!target || target.startsWith('#')) return { status: 'same-document', target };
    if (/^(?:https?:|\/\/)/i.test(target)) return { status: 'external', target };
    if (/^[a-z][a-z0-9+.-]*:/i.test(target)) return { status: 'not-bundled', target };
    let decoded;
    try { decoded = decodeURIComponent(target.split('#')[0]); } catch { return { status: 'not-bundled', target }; }
    const candidates = [path.posix.normalize(path.posix.join(path.posix.dirname(document), decoded))];
    if (wiki) candidates.push(path.posix.normalize(decoded), path.posix.normalize('main/' + decoded));
    const found = candidates.flatMap(candidate => [candidate, candidate + '.md']).find(candidate => selected.has(candidate));
    if (!found) return { status: 'not-bundled', target };
    const fragment = target.includes('#') ? '#' + target.split('#').slice(1).join('#') : '';
    return { status: 'bundled', target, resolved: found,
      href: path.posix.relative(path.posix.dirname(document), found) + fragment };
  }
  return text.split('\n').map((line, index) => {
    const marker = line.match(/^\s*(`{3,}|~{3,})/);
    if (marker) {
      if (!fence) fence = marker[1];
      else if (marker[1][0] === fence[0] && marker[1].length >= fence.length) fence = '';
      return line;
    }
    if (fence) return line;
    return line.split(/(`+[^`]*`+)/).map((part, segment) => {
      if (segment % 2) return part;
      // One combined pass avoids processing generated links twice.
      return part.replace(/(!?)\[\[([^\]]+)\]\]|(!?)\[([^\]]*)\]\((<[^>]+>|[^\s)]*)(?:\s+"[^"]*")?\)/g,
        (whole, wikiImage, wikiBody, image, label, destination) => {
          const wiki = wikiBody !== undefined;
          const [wikiTarget, alias] = wiki ? wikiBody.split('|') : [];
          const target = wiki ? wikiTarget : destination.replace(/^<|>$/g, '');
          const result = resolve(target, wiki);
          links.push({ document, line: index + 1, ...result, anchorVerified: false });
          const caption = wiki ? alias ?? wikiTarget : label;
          if (result.status === 'bundled') return `[${caption}](${result.href})`;
          if (result.status === 'not-bundled') return `${caption} (not bundled; canonical reference: ${target})`;
          return whole;
        });
    }).join('');
  }).join('\n');
}

export async function createRecoveryBundle(input, vaultRoot, destination, options = {}) {
  const workbook = normalizeWorkbook(input);
  const systems = input.recovery?.systems;
  if (!Array.isArray(systems) || !systems.length || systems.length > 50
      || new Set(systems.map(s => s.id)).size !== systems.length
      || systems.some(s => !/^[a-z0-9_-]+$/.test(s.id))) throw new Error('Bundle requires unique, bounded recovery systems.');
  if (!Array.isArray(input.sourceRecords) || input.sourceRecords.length > 20) throw new Error('Bundle requires bounded source references.');
  const references = [...new Set([...input.sourceRecords, ...systems.map(s => s.runbookPath), ...(options.support ?? SUPPORT)].map(documentPath))].sort();
  if (references.length > 40) throw new Error('Bundle is limited to 40 selected documents.');
  const root = await realpath(vaultRoot);
  const parent = await realpath(path.dirname(path.resolve(destination)));
  const output = path.join(parent, path.basename(path.resolve(destination)));
  if (inside(root, output)) throw new Error('Generated bundles must stay outside the vault.');
  const files = new Map();
  let total = 0;
  for (const reference of references) {
    let current = root;
    for (const segment of reference.split('/')) {
      current = path.join(current, segment);
      if ((await lstat(current)).isSymbolicLink()) throw new Error('Symlinked bundle sources are refused.');
    }
    if (!inside(root, await realpath(current))) throw new Error('Bundle source escapes vault.');
    const bytes = await boundedRead(current);
    total += bytes.length;
    if (total > 2 * 1024 * 1024) throw new Error('Selected documents exceed the 2 MB bundle limit.');
    const text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
    rejectCredentials(text, reference);
    files.set(reference, { text, originalSha256: sha256(bytes) });
  }
  const links = [], selected = new Set(references);
  const manifest = { schemaVersion: 'recovery-bundle/1.0', createdAt: new Date().toISOString(),
    scope: 'Selected runbooks for named systems; not backup data, executable artifacts or a full-estate rebuild kit.',
    evidenceCanonicalJsonSha256: sha256(JSON.stringify(input)),
    systems: workbook.recovery.map(s => ({ id: s.id, label: s.label })), documents: [], links };
  const contents = new Map([['recovery-index.md', createRecoveryPack(input).replace(
    'Open the following paths from the canonical vault root; no network or credentials are needed.',
    'The listed source/runbook documents are included at matching paths in this pack. External dependencies are listed in manifest.json.')
    .replace(/- Source: (main\/[^\n]+)/g, '- Source: [$1]($1)')
    .replace(/- Vault runbook: (main\/[^\n]+)/g, '- Bundled runbook: [$1]($1)')]]);
  for (const [reference, source] of files) {
    const text = rewriteLinks(source.text, reference, selected, links);
    contents.set(reference, text);
    manifest.documents.push({ path: reference, originalSha256: source.originalSha256, bundledSha256: sha256(text) });
  }
  const missing = links.filter(link => link.status === 'not-bundled');
  contents.set('README.md', `# Offline recovery runbooks\n\nStart with [recovery-index.md](recovery-index.md).\n\n` +
    `Scope: ${workbook.recovery.length} named systems, ${references.length} selected documents. Historical evidence remains stale/unknown.\n\n` +
    'Runbooks are readable offline. Only selected Markdown and generated indexes are included; backup archives, images, configurations and credential files are excluded. ' +
    'Credential-candidate checks are conservative heuristics, not proof of absence. This pack does not authorize restore commands.\n\n' +
    'Local links to included documents are converted to Markdown; unbundled references are disabled and labelled. Commands/code blocks are unchanged. ' +
    `${missing.length} unbundled references and external links are itemized in manifest.json. Heading anchors and reference-style links are not verified.\n\n` +
    'Require COMPLETE and verify SHA256SUMS before use (Linux: run `sha256sum -c SHA256SUMS` from this directory). ' +
    'Checksums detect changes, not authenticity; preserve a trusted copy. ' +
    'Keep this pack private (internal topology and operational guidance). Windows permissions depend on the destination ACL.\n');
  contents.set('manifest.json', JSON.stringify(manifest, null, 2) + '\n');
  // Validate all source bytes before creating anything. Never merge into existing output.
  await mkdir(output, { mode: 0o700 });
  const checksums = [];
  for (const [relative, content] of contents) {
    const target = path.join(output, relative);
    await mkdir(path.dirname(target), { recursive: true, mode: 0o700 });
    await writeFile(target, content, { flag: 'wx', mode: 0o600 });
    if (sha256(await readFile(target)) !== sha256(content)) throw new Error('Bundle write verification failed.');
    checksums.push(`${sha256(content)}  ${relative}\n`);
  }
  checksums.push(`${sha256(COMPLETE)}  COMPLETE\n`);
  await writeFile(path.join(output, 'SHA256SUMS'), checksums.join(''), { flag: 'wx', mode: 0o600 });
  await writeFile(path.join(output, 'COMPLETE'), COMPLETE, { flag: 'wx', mode: 0o600 });
  try { await verifyRecoveryBundle(output); }
  catch (error) { await unlink(path.join(output, 'COMPLETE')); throw error; }
  return { systems: workbook.recovery.length, documents: references.length, unbundledReferences: missing.length };
}

export async function verifyRecoveryBundle(directory) {
  if ((await lstat(directory)).isSymbolicLink()) throw new Error('Symlinked bundle directory is refused.');
  const root = await realpath(directory);
  if ((await boundedRead(path.join(root, 'COMPLETE'))).toString('utf8') !== COMPLETE) throw new Error('Bundle is incomplete.');
  const lines = (await boundedRead(path.join(root, 'SHA256SUMS'))).toString('utf8').trim().split('\n');
  if (lines.length > 50) throw new Error('Invalid bundle checksum count.');
  const seen = new Set();
  for (const line of lines) {
    const match = line.match(/^([a-f0-9]{64})  ([A-Za-z0-9_./-]+)$/);
    if (!match || match[2].split('/').some(s => !s || s === '.' || s === '..') || seen.has(match[2])) throw new Error('Invalid bundle checksum path.');
    seen.add(match[2]);
    let file = root;
    for (const segment of match[2].split('/')) {
      file = path.join(file, segment);
      if ((await lstat(file)).isSymbolicLink()) throw new Error('Symlinked bundle files are refused.');
    }
    if (sha256(await boundedRead(file)) !== match[1]) throw new Error('Bundle checksum mismatch.');
  }
  for (const required of ['README.md', 'manifest.json', 'recovery-index.md', 'COMPLETE']) {
    if (!seen.has(required)) throw new Error('Required bundle file is not covered by checksums.');
  }
  let entries = 0;
  async function inventory(relative = '') {
    for (const entry of await readdir(path.join(root, relative), { withFileTypes: true })) {
      if (++entries > 200) throw new Error('Bundle inventory exceeds bounds.');
      const name = relative ? relative + '/' + entry.name : entry.name;
      if (entry.isSymbolicLink()) throw new Error('Symlinked bundle files are refused.');
      if (entry.isDirectory()) await inventory(name);
      else if (!entry.isFile() || (!seen.has(name) && name !== 'SHA256SUMS')) throw new Error('Unexpected file in bundle.');
    }
  }
  await inventory();
  return { verifiedFiles: seen.size };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const [inputPath, outputPath, ...extra] = process.argv.slice(2);
    if (!inputPath || !outputPath || extra.length) throw new Error('Usage: node recovery-bundle.mjs INPUT.json NEW_DIRECTORY_OUTSIDE_VAULT | --verify DIRECTORY');
    if (inputPath === '--verify') {
      console.log(JSON.stringify(await verifyRecoveryBundle(outputPath)));
    } else {
      const input = JSON.parse((await boundedRead(inputPath)).toString('utf8').replace(/^\uFEFF/, ''));
      const root = fileURLToPath(new URL('../../../', import.meta.url));
      console.log(JSON.stringify(await createRecoveryBundle(input, root, outputPath)));
    }
  } catch (error) {
    console.error(error instanceof SyntaxError ? 'Input is not valid JSON.' : error.code ? `File operation failed (${error.code}); incomplete output must not be used.` : error.message);
    process.exitCode = 1;
  }
}
