import { mkdir, copyFile, cp, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const distDir = path.join(root, 'dist');
const vendorDir = path.join(root, 'vendor');
const mermaidSource = path.join(root, 'node_modules', 'mermaid', 'dist', 'mermaid.min.js');
const mermaidTarget = path.join(vendorDir, 'mermaid.min.js');

await rm(distDir, { recursive: true, force: true });
await mkdir(vendorDir, { recursive: true });
await mkdir(distDir, { recursive: true });
await copyFile(mermaidSource, mermaidTarget);
console.log(`Copied ${mermaidSource} -> ${mermaidTarget}`);
await cp(path.join(root, 'index.html'), path.join(distDir, 'index.html'));
await cp(path.join(root, 'styles.css'), path.join(distDir, 'styles.css'));
await cp(path.join(root, 'app.js'), path.join(distDir, 'app.js'));
await cp(path.join(root, 'diagram-data.js'), path.join(distDir, 'diagram-data.js'));
await cp(vendorDir, path.join(distDir, 'vendor'), { recursive: true });
console.log(`Built viewer in ${distDir}`);
