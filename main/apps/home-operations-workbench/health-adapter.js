// Offline transformation only: no network, storage, commands or raw-detail copying.
const WINDOWS = {
  router: ['Router management', []],
  ha_http: ['Home Assistant HTTPS', ['router']],
  frigate_ping: ['Frigate management', ['router']],
  docker_host: ['Docker host management', ['router']],
  homepage: ['Homepage HTTPS', ['docker_host']],
  bambuddy: ['Bambuddy service', ['docker_host']],
  mqtt: ['MQTT TLS listener', ['router']],
  grafana: ['Grafana', ['router']],
  uptime_kuma: ['Uptime Kuma', ['router']],
  llamacpp: ['Local inference endpoint', ['router']],
  nas: ['OMV NFS listener', ['router']],
  camera_01: ['Camera 1 RTSP listener', ['router']],
  frigate_http: ['Frigate HTTPS listener', ['frigate_ping']],
};
const PROXMOX = {
  ct111_root: ['Frigate root capacity', []],
  ct114_root: ['Local AI root capacity', []],
  frigate_mount: ['Frigate recording mount', []],
  backup_vm100: ['Home Assistant backup freshness', []],
  backup_vm102: ['Monitoring backup freshness', []],
  backup_vm103: ['Docker host backup freshness', []],
  backup_ct111: ['Frigate backup freshness', []],
  backup_ct114: ['Local AI backup freshness', []],
};
const BACKUPS = { vm100: 'Home Assistant', vm102: 'Monitoring', vm103: 'Docker host', ct111: 'Frigate', ct114: 'Local AI' };
const STATUS = { pass: 'healthy', fail: 'failed', warn: 'warning', unknown: 'unknown', skipped: 'unknown' };
const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);

function observation(value, offset) {
  if (typeof value !== 'string') return null;
  let stamp = value.trim().replace(' ', 'T');
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(stamp) && offset) stamp += offset;
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})$/.test(stamp)) return null;
  const calendar = stamp.slice(0, 10);
  const calendarDate = new Date(`${calendar}T00:00:00Z`);
  if (!Number.isFinite(calendarDate.valueOf()) || calendarDate.toISOString().slice(0, 10) !== calendar) return null;
  const date = new Date(stamp);
  return Number.isFinite(date.valueOf()) ? date : null;
}

export function adaptHealthSnapshot(snapshot, options = {}) {
  if (!isObject(snapshot) || !isObject(snapshot.checks)) throw new Error('A health snapshot must contain a checks object.');
  const catalog = snapshot.collector === 'Windows management workstation' ? WINDOWS
    : snapshot.collector === 'Proxmox host' ? PROXMOX : null;
  if (!catalog) throw new Error('Unsupported health collector.');
  const now = new Date(options.now ?? Date.now());
  const maxAgeHours = options.maxAgeHours ?? 36;
  const offset = options.timestampOffset ?? '';
  if (!Number.isFinite(now.valueOf()) || !Number.isFinite(maxAgeHours) || maxAgeHours <= 0) throw new Error('Invalid freshness policy.');
  if (offset && !/^[+-](?:(?:0\d|1[0-3]):[0-5]\d|14:00)$/.test(offset)) throw new Error('Timestamp offset must be explicit, such as +01:00.');
  const observed = observation(snapshot.timestamp, offset);
  const invalidTime = !observed || observed.valueOf() > now.valueOf() + 5 * 60 * 1000;
  const stale = observed && now - observed > maxAgeHours * 3600000;
  const observedAt = invalidTime ? 'Not recorded reliably' : observed.toISOString();
  const dependencies = Object.entries(catalog).map(([key, [label, dependsOn]]) => {
    const check = Object.hasOwn(snapshot.checks, key) ? snapshot.checks[key] : undefined;
    const rawStatus = isObject(check) ? check.status : check;
    const normalized = typeof rawStatus === 'string' ? STATUS[rawStatus.toLowerCase()] : undefined;
    let status = normalized ?? 'unknown';
    let detail = 'Collector status only; no functional or restore acceptance is implied.';
    if (invalidTime) { status = 'unknown'; detail = 'Observation time is missing, ambiguous or in the future. Supply the collector timezone explicitly for older snapshots.'; }
    else if (stale && status !== 'unknown') { status = 'stale'; detail = `Observation exceeds the ${maxAgeHours}-hour evidence window; collect a fresh snapshot.`; }
    else if (status === 'unknown') detail = 'This collector did not provide usable evidence for this check.';
    return { id: key, label, kind: 'observed check', status, observedAt, detail, dependsOn };
  });
  const byId = new Map(dependencies.map(item => [item.id, item]));
  const systems = Object.entries(BACKUPS).map(([id, label]) => {
    const check = byId.get(`backup_${id}`);
    const unknown = { status: 'unknown', observedAt: 'Not recorded', detail: 'No evidence in this snapshot.' };
    return { id, label, backup: check ? { status: check.status, observedAt, detail: check.detail } : { ...unknown }, integrity: { ...unknown }, restore: { ...unknown }, dependencies: [] };
  });
  return {
    schemaVersion: '1.0', generatedAt: now.toISOString(),
    source: { label: `${snapshot.collector} — offline import` },
    today: { operations: dependencies.filter(item => item.status !== 'healthy').map(item => ({ id: item.id, title: item.label, status: item.status, detail: item.detail })) },
    dependencies,
    incidents: dependencies.filter(item => ['failed', 'warning', 'stale'].includes(item.status)).map(item => ({ id: `incident-${item.id}`, title: item.label, status: item.status, observedAt, signals: [item.id], note: item.detail })),
    recovery: { systems },
  };
}
