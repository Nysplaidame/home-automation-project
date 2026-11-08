const byId = id => document.getElementById(id);
let targets = {};
let bundles = {};
let history = null;
let bundleRunning = false;
let bundleStop = false;
let currentRoute = new URLSearchParams(location.hash.slice(1)).get('route') || 'homepage';
let latest = null;
let running = false;
const results = [];

async function request(path, options = {}) {
  const response = await fetch(new URL(`./api/${path}`, document.baseURI), { ...options, signal: AbortSignal.timeout(12000), cache: 'no-store' });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Request failed: ${response.status}`);
  return data;
}
function node(tag, text) {
  const item = document.createElement(tag);
  if (text !== undefined) item.textContent = text;
  return item;
}
function number(value, suffix = '') {
  return Number.isFinite(value) ? `${value.toFixed(1)}${suffix}` : 'Unknown';
}
function renderResources() {
  if (!latest) return;
  const { snapshot, status } = latest;
  const age = (Date.now() / 1000) - snapshot.timestamp;
  const fresh = Number.isFinite(age) && age >= -30 && age <= 300;
  const issues = Object.keys(snapshot.errors || {});
  const incidents = Object.entries(status.active_or_pending || {});
  const health = status.collector_health || {};
  const delivery = status.delivery_errors || [];
  const label = !fresh ? 'Stale — current health unknown' : issues.length ? 'Degraded coverage' : health.failures || health.active ? 'Collector failure' : delivery.length || health.delivery_error ? 'Notification delivery failure' : health.pending ? 'Collector notification queued' : incidents.length ? 'Active or queued incidents' : 'Fresh coverage';
  byId('resource-status').textContent = `${label} · ${Math.max(0, Math.round(age))} seconds old · ${Object.keys(snapshot.samples || {}).length} systems sampled`;
  byId('resource-status').className = fresh && !issues.length && !incidents.length && !health.failures && !health.active && !delivery.length && !health.delivery_error ? 'status-pass' : 'status-fail';
  byId('resource-summary').textContent = `Host load ${number(snapshot.load)} / ${snapshot.cpus ?? '?'} CPUs · blocked tasks ${snapshot.blocked ?? '?'} · thin pool ${number(snapshot.thin_pct, '%')} · metadata ${number(snapshot.thin_metadata_pct, '%')}`;
  const body = byId('resource-rows');
  body.replaceChildren();
  const names = new Map((snapshot.inventory || []).map(row => [String(row.vmid), row]));
  const ids = new Set(['host', ...(snapshot.expected || []), ...(snapshot.inventory || []).map(row => String(row.vmid)), ...Object.keys(snapshot.samples || {})]);
  for (const id of ids) {
    const sample = snapshot.samples?.[id];
    const guest = names.get(id);
    const row = node('tr');
    const label = id === 'host' ? 'Proxmox host' : `${guest?.type?.toUpperCase() || 'Guest'} ${id} · ${guest?.name || ''}`;
    const values = [label, guest?.status === 'stopped' ? 'Stopped' : sample ? fresh ? 'Sampled' : 'Stale' : 'No sample', sample ? `${number(sample.available_pct, '%')} / ${number(sample.available_mib / 1024, ' GiB')}` : 'Unknown', Number.isFinite(guest?.cpu) && snapshot.inventory_valid ? number(guest.cpu * 100, '%') : 'Unknown', number(sample?.disk_pct, '%'), `${number(sample?.memory_psi, '%')} / ${number(sample?.io_psi, '%')}`, sample?.oom ?? 'Unknown'];
    values.forEach(value => row.append(node('td', String(value))));
    body.append(row);
  }
  const alerts = byId('resource-alerts');
  alerts.replaceChildren();
  const descriptions = [];
  issues.forEach(key => descriptions.push(`Coverage: ${key} — ${snapshot.errors[key]}`));
  incidents.forEach(([key, value]) => descriptions.push(`${key}: ${value.undelivered ? 'delivery queued' : value.active ? 'active' : 'pending'}`));
  delivery.forEach(key => descriptions.push(`Notification delivery failed: ${key}`));
  if (health.failures || health.active || health.pending || health.delivery_error) descriptions.push(`Collector: ${health.failures || 0} failures; ${health.pending || (health.active ? 'active failure' : 'recovering')}${health.delivery_error ? '; notification delivery failed' : ''}`);
  (descriptions.length ? descriptions : ['No active incidents, queued alerts or reported delivery errors in this snapshot.']).forEach(text => alerts.append(node('li', text)));
}
async function refresh() {
  byId('refresh-resources').disabled = true;
  try {
    latest = await request('resources');
    renderResources();
  } catch (error) {
    byId('resource-status').textContent = `Unavailable — current health unknown. ${error.message}`;
    byId('resource-status').className = 'status-fail';
    byId('resource-rows').replaceChildren();
    byId('resource-summary').textContent = 'The Proxmox collector and ntfy alert delivery operate independently of this page.';
    byId('resource-alerts').replaceChildren();
  } finally {
    byId('refresh-resources').disabled = false;
  }
}
function chooseTarget() {
  const config = targets[byId('probe-target').value];
  const previousPort = byId('probe-port').value;
  byId('probe-port').replaceChildren();
  for (const port of config?.ports || []) {
    const option = node('option', String(port)); option.value = port; byId('probe-port').append(option);
  }
  if (config?.ports.includes(Number(previousPort))) byId('probe-port').value = previousPort;
  byId('probe-address').textContent = config ? `${config.ip} · DNS: ${config.dns}` : 'Targets unavailable';
  byId('probe-http').disabled = !config?.url || running;
  updateControls();
}
function transcript() {
  return results.map(result => `[${new Date(result.timestamp * 1000).toISOString()}] ${result.source}\n> ${result.command}\n${result.severity === 'unknown' ? 'UNKNOWN' : result.severity === 'warn' ? 'WARNING' : result.ok ? 'PASS' : 'FAILED'} (${result.duration_ms} ms)\n${result.output}`).join('\n\n');
}
function updateControls() {
  document.querySelectorAll('[data-probe], #console-run, #bundle-run').forEach(button => button.disabled = running || bundleRunning || !Object.keys(targets).length);
  byId('bundle-stop').disabled = !bundleRunning;
  const config = targets[byId('probe-target').value];
  byId('probe-http').disabled ||= !config?.url;
  byId('probe-tls').disabled ||= !config?.tls;
}
async function run(command, fromBundle = false) {
  if (bundleRunning && !fromBundle) return;
  if (running) return;
  running = true;
  updateControls();
  byId('console-state').textContent = `Running ${command} from VM103…`;
  try {
    const result = await request('probe', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Diagnostic-Request': '1' }, body: JSON.stringify({ command }) });
    results.push(result); if (results.length > 20) results.shift();
    byId('console-output').textContent = transcript();
    byId('console-output').scrollTop = byId('console-output').scrollHeight;
    byId('console-state').textContent = `${result.severity === 'unknown' ? 'Result unknown' : result.severity === 'warn' ? 'Check has a warning' : result.ok ? 'Check passed' : 'Check failed'} · ${result.duration_ms} ms · VM103${result.history_error ? ' · ' + result.history_error : ''}`;
    refreshHistory();
    return result;
  } catch (error) {
    byId('console-state').textContent = error.message;
  } finally {
    running = false;
    chooseTarget();
    updateControls();
  }
}
function selectedBundle() {
  const bundle = bundles[byId('bundle-select').value];
  byId('bundle-plan').textContent = bundle ? `Will run from VM103: ${bundle.commands.join(' → ')}. Individual failures do not stop the remaining checks.` : 'No bundle available.';
}
function recommendBundle(event) {
  if (event?.detail?.id) currentRoute = event.detail.id;
  const match = Object.entries(bundles).find(([, value]) => value.routes.includes(currentRoute));
  if (match && !bundleRunning) byId('bundle-select').value = match[0];
  selectedBundle();
}
byId('bundle-select').addEventListener('change', selectedBundle);
window.addEventListener('investigation-changed', recommendBundle);
byId('bundle-stop').addEventListener('click', () => { bundleStop = true; byId('bundle-state').textContent = 'Stopping after the current bounded check…'; });
byId('bundle-run').addEventListener('click', async () => {
  const bundle = bundles[byId('bundle-select').value];
  if (!bundle || running || bundleRunning) return;
  bundleRunning = true; bundleStop = false;
  byId('bundle-select').disabled = true;
  updateControls();
  let completed = 0, failed = 0, warnings = 0, unknown = 0, unavailable = false;
  try {
    for (const command of bundle.commands) {
      if (bundleStop) break;
      byId('bundle-state').textContent = `Check ${completed + 1}/${bundle.commands.length}: ${command}`;
      const result = await run(command, true);
      if (!result) { unavailable = true; break; }
      completed++;
      if (result.severity === 'unknown') unknown++;
      else if (!result.ok) failed++;
      if (result.severity === 'warn') warnings++;
    }
  } finally {
    bundleRunning = false;
    byId('bundle-select').disabled = false;
    updateControls();
    byId('bundle-state').textContent = `${unavailable ? 'Service unavailable or rate limited' : bundleStop ? 'Stopped' : 'Bundle complete'} · ${completed}/${bundle.commands.length} checks · ${failed} failures · ${warnings} warnings · ${unknown} unknown. Route evidence remains independent.`;
  }
});
function renderHistory() {
  if (!history) return;
  const filter = byId('history-filter').value;
  const events = history.events.filter(event => !filter || event.kind === filter);
  byId('history-state').textContent = `${events.length} shown from the latest ${history.events.length} of ${history.total} retained events. History started ${new Date(history.started_at * 1000).toLocaleString()}; retained up to ${history.retention_days} days / ${history.max_events} events.`;
  const list = byId('history-events');
  list.replaceChildren();
  if (!events.length) list.append(node('li', 'No matching events recorded. Earlier incidents are not reconstructed.'));
  for (const event of events) {
    const item = node('li'), details = node('details');
    details.append(node('summary', `${new Date(event.timestamp * 1000).toLocaleString()} · ${event.severity.toUpperCase()} · ${event.title}`), node('p', `${event.kind === 'diagnostic' ? 'Operator-requested test' : event.kind === 'viewer' ? 'Viewer publication' : 'Primary monitor observation'} · ${event.detail}`));
    const links = node('p');
    const from = Math.round((event.timestamp - 600) * 1000), to = Math.round((event.timestamp + 600) * 1000);
    for (const [label, dashboard] of [['Grafana resources', 'infrastructure-fleet/infrastructure-fleet'], ['Central logs', 'central-logs/central-logs']]) {
      const link = node('a', label);
      link.href = `https://homepage.home.local:8202/d/${dashboard}?from=${from}&to=${to}`;
      link.target = '_blank'; link.rel = 'noopener noreferrer';
      links.append(link, document.createTextNode(' · '));
    }
    details.append(links); item.append(details); list.append(item);
  }
}
async function refreshHistory() {
  byId('refresh-history').disabled = true;
  try { history = await request('events'); renderHistory(); }
  catch (error) { byId('history-state').textContent = `${error.message} Previously displayed events may be out of date.`; }
  finally { byId('refresh-history').disabled = false; }
}
byId('refresh-history').addEventListener('click', refreshHistory);
function revealAnchor() {
  if (['#incident-history', '#connection-tests'].includes(location.hash)) byId(location.hash.slice(1)).open = true;
}
window.addEventListener('hashchange', revealAnchor);
revealAnchor();
byId('history-filter').addEventListener('change', renderHistory);
byId('history-copy').addEventListener('click', async () => {
  try {
    const events = (history?.events || []).filter(event => !byId('history-filter').value || event.kind === byId('history-filter').value);
    await navigator.clipboard.writeText(events.map(event => `[${new Date(event.timestamp * 1000).toISOString()}] ${event.kind} ${event.severity} ${event.title}\n${event.detail}`).join('\n\n'));
    byId('history-state').textContent = 'Visible event summaries copied.';
  } catch { byId('history-state').textContent = 'Copy unavailable. Select the event text manually.'; }
});
byId('refresh-resources').addEventListener('click', refresh);
window.addEventListener('connection-test', event => {
  byId('connection-tests').open = true;
  byId('connection-tests').scrollIntoView({ block: 'start' });
  const match = Object.entries(targets).find(([, target]) => target.ip === event.detail.ip && target.ports.includes(event.detail.port));
  if (!match) {
    byId('console-state').textContent = 'This target or port is outside the diagnostic allowlist. Use the manual check on its stated host.';
    return;
  }
  byId('probe-target').value = match[0];
  chooseTarget();
  byId('probe-port').value = event.detail.port;
  run(`tcp ${match[0]} ${event.detail.port}`);
});
byId('probe-target').addEventListener('change', chooseTarget);
document.querySelectorAll('[data-probe]').forEach(button => button.addEventListener('click', () => run(`${button.dataset.probe} ${byId('probe-target').value}${button.dataset.probe === 'tcp' ? ` ${byId('probe-port').value}` : ''}`)));
byId('console-form').addEventListener('submit', event => { event.preventDefault(); run(byId('console-command').value.trim()); });
byId('console-copy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(transcript()); byId('console-state').textContent = 'Results copied.'; }
  catch { byId('console-state').textContent = 'Copy unavailable. Select the console text manually.'; }
});
byId('console-clear').addEventListener('click', () => { results.length = 0; byId('console-output').textContent = ''; byId('console-state').textContent = 'Console cleared.'; });
try {
  ({ targets, bundles = {} } = await request('targets'));
  for (const [id, target] of Object.entries(targets)) {
    const option = node('option', target.label); option.value = id; byId('probe-target').append(option);
  }
  for (const [id, bundle] of Object.entries(bundles)) {
    const option = node('option', bundle.label); option.value = id; byId('bundle-select').append(option);
  }
  chooseTarget();
  recommendBundle();
} catch {
  byId('console-state').textContent = 'Diagnostic service unavailable. The manual guides remain usable.';
  document.querySelectorAll('[data-probe], #console-run, #bundle-run').forEach(button => button.disabled = true);
}
refresh();
refreshHistory();
setInterval(() => { if (!document.hidden) refreshHistory(); }, 60000);
setInterval(() => { if (!document.hidden) refresh(); }, 60000);
setInterval(() => { if (latest && !byId('resource-status').textContent.startsWith('Unavailable')) renderResources(); }, 10000);
