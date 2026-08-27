import { cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const mainRoot = path.resolve(appRoot, '../..');
const diagramRoot = path.join(mainRoot, 'docs/diagrams');
const sourceRoot = path.join(appRoot, 'src');
const distRoot = path.join(appRoot, 'dist');

const metadata = {
  'infrastructure/docker-host-service-placement.mermaid': {
    title: 'Docker-host Service Placement',
    summary: 'Live application stacks, operational tooling, data services, storage, and backup boundaries.',
    tags: ['docker', 'services', 'containers', 'placement'],
  },
  'infrastructure/proxmox-guests-and-backups.mermaid': {
    title: 'Proxmox Guests and Backups',
    summary: 'Production guests, rollback guests, shared iGPU paths, and OMV backup schedules.',
    tags: ['proxmox', 'vm', 'lxc', 'backup', 'gpu'],
  },
  'install/install-sequence.mermaid': {
    title: 'Install and Recovery Sequence',
    summary: 'Fresh deployment order with validation and safety gates.',
    tags: ['install', 'recovery', 'sequence'],
  },
  'network/current-master-architecture.mermaid': {
    title: 'Logical Architecture',
    summary: 'Current logical relationships across networking, compute, apps, storage, monitoring, and remote access.',
    tags: ['architecture', 'logical', 'services', 'network'],
  },
  'network/dns-ntp-flow.mermaid': {
    title: 'DNS and NTP Flow',
    summary: 'Router authority, AdGuard filtering, public fallback, and restricted-device time flow.',
    tags: ['dns', 'ntp', 'adguard'],
  },
  'network/physical-port-and-cabling.mermaid': {
    title: 'Physical Ports and Cabling',
    summary: 'Live router, Proxmox trunk, managed-switch ports, camera, NAS, and Wi-Fi attachment.',
    tags: ['physical', 'ports', 'switch', 'cabling'],
  },
  'network/remote-access-flow.mermaid': {
    title: 'Remote Access Flow',
    summary: 'Tailscale daily access, approved host routes, and dormant WireGuard fallback.',
    tags: ['tailscale', 'wireguard', 'remote'],
  },
  'network/security-access-flow.mermaid': {
    title: 'Security Access Flow',
    summary: 'Zone policy, service authentication, host firewalls, and deliberately blocked paths.',
    tags: ['security', 'firewall', 'acl'],
  },
  'network/vlan_architecture_clean.mermaid': {
    title: 'VLAN Architecture',
    summary: 'All network segments, subnets, core hosts, physical trunks, and remote-access placement.',
    tags: ['vlan', 'subnet', 'router'],
  },
  'storage/storage-and-backup-flow.mermaid': {
    title: 'Storage and Backup Flow',
    summary: 'Live OMV-backed recordings, media, guest backups, application data, and restore verification.',
    tags: ['storage', 'backup', 'omv', 'restore'],
  },
  'ventsys/ventsys-control-and-safety-flow.mermaid': {
    title: 'VentSys Control and Safety',
    summary: 'Control, telemetry, airflow, emergency actions, and fail-safe relationships.',
    tags: ['ventsys', 'safety', 'mqtt', 'esphome'],
  },
};

async function findDiagramFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      files.push(...await findDiagramFiles(absolute));
    } else if (entry.isFile() && entry.name.endsWith('.mermaid')) {
      files.push(absolute);
    }
  }
  return files;
}

function titleFromPath(relativePath) {
  return path.basename(relativePath, '.mermaid')
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

await rm(distRoot, { recursive: true, force: true });
await mkdir(path.join(distRoot, 'vendor'), { recursive: true });

for (const asset of ['index.html', 'app.js', 'styles.css']) {
  await cp(path.join(sourceRoot, asset), path.join(distRoot, asset));
}

const mermaidBundle = path.join(appRoot, 'node_modules/mermaid/dist/mermaid.min.js');
await cp(mermaidBundle, path.join(distRoot, 'vendor/mermaid.min.js'));

const files = (await findDiagramFiles(diagramRoot)).sort();
const diagrams = [];
for (const absolute of files) {
  const relative = path.relative(diagramRoot, absolute).replaceAll('\\', '/');
  const source = (await readFile(absolute, 'utf8')).trim();
  if (!source) continue;
  const details = metadata[relative] ?? {};
  const fileName = path.basename(relative, '.mermaid');
  diagrams.push({
    id: fileName,
    title: details.title ?? titleFromPath(relative),
    section: relative.split('/')[0],
    path: relative,
    summary: details.summary ?? 'Canonical project diagram.',
    tags: details.tags ?? [],
    source,
  });
}

await writeFile(
  path.join(distRoot, 'diagram-data.js'),
  `export const diagrams = ${JSON.stringify(diagrams, null, 2)};\n`,
  'utf8',
);

console.log(`Built ${diagrams.length} canonical diagrams into ${distRoot}`);
