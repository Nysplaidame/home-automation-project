export const statusMeta = Object.freeze({
  pass: { label: 'Healthy', mark: 'OK' },
  fail: { label: 'Action needed', mark: '!' },
  warn: { label: 'Degraded', mark: '~' },
  unknown: { label: 'Needs evidence', mark: '?' },
});

const check = (key, label, stage) => ({ key, label, stage });
const pathNode = (label, ...keys) => ({ label, keys });
const step = (id, stage, title, runOn, command, expected, failure) => ({
  id, stage, title, runOn, command, expected, failure,
});

export const symptoms = Object.freeze([
  {
    id: 'homepage',
    order: '01',
    title: 'Homepage access',
    short: 'The operations portal will not open.',
    description: 'Trace the request from the client through name resolution and TLS to VM 103 and the Homepage listener.',
    checks: [
      check('router', 'Router reachable', 'Network'),
      check('docker_host', 'Docker host reachable', 'Host'),
      check('homepage', 'Homepage HTTPS', 'Service'),
    ],
    path: [
      pathNode('Client'),
      pathNode('DNS / TLS', 'homepage'),
      pathNode('Router', 'router'),
      pathNode('VM 103', 'docker_host'),
      pathNode('Homepage', 'homepage'),
    ],
    steps: [
      step('resolve', 'Client', 'Confirm the canonical name resolves', 'Admin workstation', 'Resolve-DnsName homepage.home.local', 'The answer resolves to 192.168.20.102.', 'A different or missing answer points to client DNS or split-DNS policy.'),
      step('tls', 'TLS', 'Inspect the HTTPS response without changing trust', 'Admin workstation', 'curl.exe -k -I https://homepage.home.local/', 'An HTTP response is returned; 200 or a deliberate redirect proves the listener answered.', 'A certificate warning is different from a timeout. Record which one occurred.'),
      step('host', 'Network', 'Test the listener from the management workstation', 'Admin workstation', 'Test-NetConnection 192.168.20.102 -Port 443', 'TcpTestSucceeded is True.', 'If SSH also fails, investigate VM 103 or its network before the Homepage container.'),
      step('service', 'Service', 'Read the container state before considering changes', 'VM 103 / docker-host', 'docker compose -f /opt/stacks/homepage/docker-compose.yml ps', 'Homepage and preview-proxy are running.', 'Preserve the state and logs; do not recreate the stack from this dashboard.'),
    ],
    docs: [
      ['Homepage runbook', 'docs/install/services/homepage.md'],
      ['Remote access flow', 'docs/diagrams/network/remote-access-flow.mermaid'],
      ['Access matrix', 'docs/reference/access-matrix.md'],
    ],
  },
  {
    id: 'home-assistant',
    order: '02',
    title: 'Home Assistant availability',
    short: 'The HA interface or automations appear unavailable.',
    description: 'Separate a client trust problem from VM 100, native HTTPS and the MQTT dependency.',
    checks: [
      check('router', 'Router reachable', 'Network'),
      check('ha_http', 'Home Assistant HTTPS', 'Service'),
      check('mqtt', 'MQTT TLS listener', 'Dependency'),
    ],
    path: [
      pathNode('Client'),
      pathNode('VLAN 20', 'router'),
      pathNode('VM 100', 'ha_http'),
      pathNode('HA Core', 'ha_http'),
      pathNode('MQTT', 'mqtt'),
    ],
    steps: [
      step('https', 'Client', 'Capture the native HTTPS result', 'Admin workstation', 'curl.exe -k -I https://192.168.20.101:8123/', 'Home Assistant returns an HTTP response over TLS.', 'A trust warning does not justify reverting HA to HTTP.'),
      step('port', 'Network', 'Confirm the HA listener is reachable', 'Admin workstation', 'Test-NetConnection 192.168.20.101 -Port 8123', 'TcpTestSucceeded is True.', 'If false, check VM 100 state and VLAN 20 before changing HA configuration.'),
      step('vm', 'Guest', 'Read VM 100 state from Proxmox', 'Proxmox host', 'qm status 100', 'status: running', 'Use the Proxmox console to capture boot errors; do not repeatedly restart the VM.'),
      step('mqtt', 'Dependency', 'Confirm the TLS broker listener', 'Admin workstation', 'Test-NetConnection 192.168.20.101 -Port 8883', 'TcpTestSucceeded is True.', 'An open HA UI with failed MQTT narrows the incident to the broker or client credentials.'),
    ],
    docs: [
      ['Home Assistant troubleshooting', 'docs/troubleshooting/troubleshooting_reference.md#home-assistant'],
      ['Current live state', 'docs/reference/current-live-state.md'],
      ['TLS guide', 'docs/procedures/ssl_tls_guide.md'],
    ],
  },
  {
    id: 'camera',
    order: '03',
    title: 'One camera path',
    short: 'Camera 1 is grey, stale or missing in Frigate.',
    description: 'Follow Camera 1 from PoE/VLAN 30 through RTSP ingest, CT 111 and its recording mount.',
    checks: [
      check('camera_01', 'Camera 1 reachable', 'Device'),
      check('frigate_ping', 'CT 111 SSH', 'Guest'),
      check('frigate_http', 'Frigate API', 'Service'),
      check('frigate_mount', 'Recording mount', 'Storage'),
    ],
    path: [
      pathNode('Camera .21', 'camera_01'),
      pathNode('GS1900 p2', 'camera_01'),
      pathNode('VLAN 30', 'camera_01'),
      pathNode('CT 111', 'frigate_ping', 'frigate_http'),
      pathNode('OMV recordings', 'frigate_mount'),
    ],
    steps: [
      step('camera', 'Device', 'Check Camera 1 without exposing credentials', 'Monitoring VM or approved management source', 'ping 192.168.30.21', 'The camera answers from an approved diagnostic source.', 'No response can mean power, cabling, switch-port VLAN or camera state.'),
      step('rtsp', 'Ingest', 'Probe the verified substream from CT 111', 'CT 111 / Frigate', "ffprobe 'rtsp://admin:<password>@192.168.30.21:554/Streaming/Channels/102'", 'Video metadata is returned for the 1280x720 substream.', 'Keep the password out of incident notes and screenshots.'),
      step('frigate', 'Service', 'Read Frigate camera errors', 'CT 111 / Frigate', 'docker logs --since 15m frigate', 'No repeated ffmpeg or authentication failure for cam_01_annke_c500.', 'Correlate the first error timestamp with camera and switch evidence.'),
      step('mount', 'Storage', 'Confirm the host-backed recording path', 'CT 111 / Frigate', 'findmnt /mnt/nas/frigate', 'The CT path is present and backed by the Proxmox-host bind mount.', 'Do not mount NFS directly inside unprivileged CT 111.'),
    ],
    docs: [
      ['Camera preflight', 'docs/procedures/frigate_camera_preflight_checklist.md'],
      ['Physical cabling', 'docs/reference/physical-port-and-cabling.md'],
      ['Frigate troubleshooting', 'docs/troubleshooting/troubleshooting_reference.md#frigate'],
    ],
  },
  {
    id: 'p1s',
    order: '04',
    title: 'P1S telemetry',
    short: 'Bambuddy cannot see the Bambu P1S.',
    description: 'Distinguish printer reachability from Bambuddy, printer-side MQTT/FTP and HA-side MQTT.',
    checks: [
      check('p1s', 'P1S reachable', 'Device'),
      check('docker_host', 'Docker host reachable', 'Host'),
      check('bambuddy', 'Bambuddy HTTP', 'Service'),
      check('mqtt', 'HA MQTT TLS', 'Dependency'),
    ],
    path: [
      pathNode('P1S .35.200', 'p1s'),
      pathNode('VLAN 35', 'p1s'),
      pathNode('VM 103', 'docker_host'),
      pathNode('Bambuddy', 'bambuddy'),
      pathNode('HA MQTT', 'mqtt'),
    ],
    steps: [
      step('printer', 'Device', 'Confirm the printer is online', 'VM 103 / docker-host', 'ping 192.168.35.200', 'The printer answers when powered and connected.', 'The accepted blocker is currently VM103-to-P1S reachability; do not bypass VLAN policy.'),
      step('ports', 'Network', 'Test the two printer-side dependencies from VM 103', 'VM 103 / docker-host', 'nc -zvw3 192.168.35.200 21 8883', 'FTP 21 and printer MQTT 8883 are reachable.', 'If both fail, stop at the controlled network/firewall remediation boundary.'),
      step('bambuddy', 'Service', 'Read Bambuddy state without restarting it', 'VM 103 / docker-host', 'docker inspect bambuddy --format "{{.State.Status}} {{.HostConfig.NetworkMode}}"', 'The container is running; host networking remains the documented temporary exception.', 'Do not migrate to the prepared bridge until both printer ports pass from VM 103.'),
      step('ha-mqtt', 'Dependency', 'Confirm HA-side MQTT TLS separately', 'VM 103 / docker-host', 'nc -zvw3 192.168.20.101 8883', 'The HA MQTT TLS listener is reachable.', 'A pass here with failed printer ports isolates the incident away from HA.'),
    ],
    docs: [
      ['Bambuddy entity', '../wiki/pages/entities/bambuddy.md'],
      ['Printer VLAN decision', 'docs/decisions/02-printer-vlan-architecture.md'],
      ['Docker-host setup', 'scripts/setup/proxmox/docker_host_setup_guide.md'],
    ],
  },
  {
    id: 'backups',
    order: '05',
    title: 'Backup freshness',
    short: 'A scheduled backup may be missing or stale.',
    description: 'Verify the OMV path, then each protected guest archive, without starting a restore.',
    checks: [
      check('nas', 'OMV NFS listener', 'Storage'),
      check('backup_vm100', 'VM 100 archive', 'Backup'),
      check('backup_vm102', 'VM 102 archive', 'Backup'),
      check('backup_vm103', 'VM 103 archive', 'Backup'),
      check('backup_ct111', 'CT 111 archive', 'Backup'),
      check('backup_ct114', 'CT 114 archive', 'Backup'),
    ],
    path: [
      pathNode('Guest jobs', 'backup_vm100', 'backup_vm102', 'backup_vm103', 'backup_ct111', 'backup_ct114'),
      pathNode('Proxmox', 'backup_vm100', 'backup_vm102', 'backup_vm103', 'backup_ct111', 'backup_ct114'),
      pathNode('NFS client', 'nas'),
      pathNode('OMV', 'nas'),
      pathNode('omv-backups', 'nas'),
    ],
    steps: [
      step('storage', 'Storage', 'Confirm the backup target is active', 'Proxmox host', 'pvesm status | grep omv-backups', 'The storage reports active with expected capacity.', 'Do not start ad-hoc backups until the target and free space are understood.'),
      step('jobs', 'Scheduler', 'Read recent job results', 'Proxmox host', 'journalctl --since "36 hours ago" -u pvescheduler --no-pager', 'Scheduled jobs show completion rather than mount or tmpdir errors.', 'Capture the first failure and affected guest IDs.'),
      step('archives', 'Evidence', 'List newest archives without modifying them', 'Proxmox host', 'find /mnt/pve/omv-backups/dump -maxdepth 1 -type f -printf "%TY-%Tm-%Td %TH:%TM %f\n" | sort -r | head', 'Recent archives exist for VMs 100/102/103 and CTs 111/114.', 'Missing CT archives may indicate the required host-local /var/tmp setting regressed.'),
      step('restore', 'Boundary', 'Stop before restore testing', 'No host — deliberate stop', 'No command in v1', 'A restore exercise is planned separately with explicit stop/ask gates.', 'Never overwrite a live guest to prove a backup from this workflow.'),
    ],
    docs: [
      ['Backup strategy', 'scripts/backup/backup_strategy.md'],
      ['Current backup state', 'docs/reference/current-live-state.md#backup-and-restore-state'],
      ['OMV cutover runbook', 'docs/procedures/omv_cutover_execution_runbook.md'],
    ],
  },
]);

const acceptedStatuses = new Set(['pass', 'fail', 'warn', 'unknown', 'skipped']);

function normalizeStatus(value) {
  const candidate = typeof value === 'object' && value !== null ? value.status : value;
  const normalized = String(candidate ?? 'unknown').trim().toLowerCase();
  return acceptedStatuses.has(normalized) ? (normalized === 'skipped' ? 'unknown' : normalized) : 'unknown';
}

function boundedText(value, fallback, limit) {
  const text = String(value ?? fallback).trim();
  return (text || fallback).slice(0, limit);
}

export function normalizeSnapshot(raw) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    throw new Error('Snapshot must be a JSON object.');
  }
  if (!raw.checks || typeof raw.checks !== 'object' || Array.isArray(raw.checks)) {
    throw new Error('Snapshot must contain a checks object.');
  }
  const checks = {};
  const details = {};
  for (const [key, value] of Object.entries(raw.checks)) {
    if (value && typeof value === 'object' && !Array.isArray(value) && !('status' in value)) continue;
    checks[key] = normalizeStatus(value);
    if (value && typeof value === 'object' && !Array.isArray(value) && value.detail != null) {
      details[key] = boundedText(value.detail, '', 240);
    }
  }
  return {
    timestamp: boundedText(raw.timestamp, 'Timestamp not supplied', 100),
    collector: boundedText(raw.collector ?? raw.source, 'Collector not supplied', 100),
    checks,
    details,
  };
}

export function evaluateSymptom(symptom, snapshot) {
  return evaluateKeys(symptom.checks.map(({ key }) => key), snapshot);
}

export function evaluateKeys(keys, snapshot) {
  if (!snapshot || keys.length === 0) return 'unknown';
  const values = keys.map((key) => snapshot.checks[key] ?? 'unknown');
  if (values.includes('fail')) return 'fail';
  if (values.includes('warn')) return 'warn';
  if (values.includes('unknown')) return 'unknown';
  return values.length > 0 && values.every((value) => value === 'pass') ? 'pass' : 'unknown';
}

export function evidenceFocus(symptom, snapshot) {
  if (!snapshot) {
    return {
      status: 'unknown',
      label: 'Load a health snapshot',
      stage: 'Evidence',
      message: 'No diagnostic evidence is loaded, so no boundary can be assessed yet.',
    };
  }

  const assessed = symptom.checks.map((item) => ({
    ...item,
    status: snapshot.checks[item.key] ?? 'unknown',
  }));
  const target = assessed.find(({ status }) => status === 'fail')
    ?? assessed.find(({ status }) => status === 'warn')
    ?? assessed.find(({ status }) => status === 'unknown');

  if (target) {
    const message = target.status === 'unknown'
      ? 'Collect this missing signal before assuming the downstream system is healthy.'
      : 'Start here, preserve the result, and avoid changing downstream systems until this boundary is understood.';
    return { ...target, message };
  }

  return {
    status: 'pass',
    label: 'All required signals passed',
    stage: 'Assessment',
    message: 'The imported checks do not reproduce this symptom; capture the exact client error and time next.',
  };
}

export function evidenceCoverage(symptom, snapshot) {
  const total = symptom.checks.length;
  const collected = snapshot
    ? symptom.checks.filter(({ key }) => (snapshot.checks[key] ?? 'unknown') !== 'unknown').length
    : 0;
  return { collected, total };
}

export function snapshotSummary(snapshot) {
  if (!snapshot) return { pass: 0, fail: 0, warn: 0, unknown: 0, total: 0 };
  const summary = { pass: 0, fail: 0, warn: 0, unknown: 0, total: 0 };
  for (const value of Object.values(snapshot.checks)) {
    const status = statusMeta[value] ? value : 'unknown';
    summary[status] += 1;
    summary.total += 1;
  }
  return summary;
}

export function buildIncidentReport(symptom, snapshot, notes = '') {
  const status = evaluateSymptom(symptom, snapshot);
  const lines = [
    `Incident: ${symptom.title}`,
    `Assessment: ${statusMeta[status].label}`,
    `Snapshot: ${snapshot?.timestamp ?? 'not loaded'}`,
    '',
    'Relevant checks:',
  ];
  for (const item of symptom.checks) {
    lines.push(`- ${item.label}: ${snapshot?.checks[item.key] ?? 'unknown'}`);
  }
  if (notes.trim()) lines.push('', 'Operator notes:', notes.trim());
  lines.push('', 'No credentials or automatic remediation are included.');
  return lines.join('\n');
}

export const sampleSnapshots = Object.freeze({
  healthy: {
    label: 'Healthy reference',
    value: { timestamp: '2026-08-25 14:00:00', checks: { router: 'pass', docker_host: 'pass', homepage: 'pass', ha_http: 'pass', mqtt: 'pass', camera_01: 'pass', frigate_ping: 'pass', frigate_http: 'pass', frigate_mount: 'pass', p1s: 'pass', bambuddy: 'pass', nas: 'pass', backup_vm100: 'pass', backup_vm102: 'pass', backup_vm103: 'pass', backup_ct111: 'pass', backup_ct114: 'pass' } },
  },
  homepage: {
    label: 'Homepage listener failure',
    value: { timestamp: 'Example incident', checks: { router: 'pass', docker_host: 'pass', homepage: 'fail', ha_http: 'pass', mqtt: 'pass' } },
  },
  p1s: {
    label: 'P1S path unavailable',
    value: { timestamp: 'Accepted current exception', checks: { router: 'pass', docker_host: 'pass', p1s: 'fail', bambuddy: 'pass', mqtt: 'pass' } },
  },
  backups: {
    label: 'One stale backup',
    value: { timestamp: 'Example incident', checks: { nas: 'pass', backup_vm100: 'pass', backup_vm102: 'pass', backup_vm103: 'pass', backup_ct111: 'fail', backup_ct114: 'pass' } },
  },
});
