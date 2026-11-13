// Routine schedule projection only; no health history, session completion or writes.
import { normalizeWorkbook } from './models.js';
import { parseObservation } from './evidence-time.js';
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
function calendar(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return '';
  const date = new Date(`${value}T00:00:00Z`);
  return Number.isFinite(date.valueOf()) && date.toISOString().slice(0, 10) === value ? value : '';
}
function name(value) {
  if (typeof value !== 'string' || /\b(password|passphrase|token|secret|api[ _-]?key|bearer|private[ _-]?key)\b/i.test(value)) return 'Unnamed routine';
  return value.replace(/\s+/g, ' ').trim().slice(0, 160) || 'Unnamed routine';
}
export function adaptRecompPlan(snapshot, options = {}) {
  if (!object(snapshot) || snapshot.schemaVersion !== 'recomp-plan/1.0' || !['available', 'unavailable'].includes(snapshot.status) || !calendar(snapshot.planDate)) throw new Error('Saved Recomp plan requires an explicit calendar selection.');
  const now = new Date(options.now ?? Date.now()), maxAgeHours = options.maxAgeHours ?? 36;
  if (!Number.isFinite(now.valueOf()) || !Number.isFinite(maxAgeHours) || maxAgeHours <= 0) throw new Error('Invalid freshness policy.');
  const observed = parseObservation(snapshot.observedAt), reliable = observed && observed <= now;
  const sourceStatus = snapshot.status === 'unavailable' || !reliable ? 'unknown' : now - observed > maxAgeHours * 3600000 ? 'stale' : 'healthy';
  const observedAt = reliable ? observed.toISOString() : 'Not recorded reliably';
  const ownerUrl = normalizeWorkbook({ schemaVersion: '1.0', today: { workouts: [{ ownerUrl: snapshot.ownerUrl }] } }).today.workouts[0].ownerUrl;
  let plans = [], ignored = 0;
  if (snapshot.status === 'available') {
    const routines = snapshot.routines;
    if (!object(routines) || !Array.isArray(routines.items) || routines.items.length > 5000) throw new Error('Saved routine items must be bounded.');
    const byId = new Map();
    for (const row of routines.items) {
      if (!object(row) || typeof row.id !== 'string' || !row.id || row.id.includes('|') || row.id.length > 200 || byId.has(row.id) || (row.scheduleDays !== undefined && (!Array.isArray(row.scheduleDays) || row.scheduleDays.length > 7 || row.scheduleDays.some(day => !Number.isInteger(day) || day < 0 || day > 6)))) throw new Error('Invalid saved routine schedule.');
      byId.set(row.id, row);
    }
    const overrides = routines.scheduleOverrides ?? {};
    if (!object(overrides) || Object.keys(overrides).length > 5000) throw new Error('Saved schedule overrides must be bounded.');
    for (const [key, target] of Object.entries(overrides)) {
      const parts = key.split('|');
      if (parts.length !== 2 || !calendar(parts[0]) || !parts[1] || !calendar(target)) throw new Error('Invalid saved schedule move.');
      if (!byId.has(parts[1])) ignored++;
    }
    const day = (new Date(`${snapshot.planDate}T00:00:00Z`).getUTCDay() + 6) % 7;
    for (const row of routines.items) {
      if (!(row.scheduleDays ?? []).includes(day)) continue;
      const key = `${snapshot.planDate}|${row.id}`;
      if (!Object.hasOwn(overrides, key)) plans.push({ row, sourceDate: snapshot.planDate });
    }
    for (const [key, target] of Object.entries(overrides)) {
      if (target !== snapshot.planDate) continue;
      const [sourceDate, id] = key.split('|');
      if (byId.has(id)) plans.push({ row: byId.get(id), sourceDate });
    }
  }
  const selected = plans.slice(0, 50);
  const freshness = snapshot.status === 'unavailable' ? 'Recomp source unavailable.' : !reliable ? 'Observation time is missing, ambiguous, invalid or future.' : sourceStatus === 'stale' ? `Saved observation exceeds ${maxAgeHours} hours.` : 'Saved observation within freshness window.';
  return {
    schemaVersion: '1.0', generatedAt: now.toISOString(), source: { label: 'Recomp — saved routine plan (offline import)' },
    today: {
      workouts: selected.map(({ row, sourceDate }, index) => ({ id: `recomp-plan-${index + 1}`, title: name(row.name), status: sourceStatus === 'healthy' ? 'warning' : sourceStatus, due: snapshot.planDate,
        detail: `Planned routine only; completion and readiness unknown. ${sourceDate !== snapshot.planDate ? `Moved from ${sourceDate}. ` : ''}Source calendar date; observed: ${observedAt}.`, ownerUrl })),
      operations: [{ id: 'recomp-source', title: `Recomp saved selection: ${snapshot.planDate}`, status: sourceStatus,
        detail: `${freshness} Observed: ${observedAt}. Displayed ${selected.length} of ${plans.length} selected occurrences; ${ignored} orphan moves omitted. Routine selection only, not complete training coverage or today's schedule. No health history, completion inference or writes.`, ownerUrl }],
    },
  };
}
