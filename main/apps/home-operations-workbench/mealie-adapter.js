// Saved Mealie page only; no API, ingredients, recipe import or calendar writes.
import { normalizeWorkbook } from './models.js';
import { parseObservation } from './evidence-time.js';
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const types = new Set(['breakfast', 'lunch', 'dinner', 'side', 'snack', 'drink', 'dessert']);
function calendar(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return '';
  const date = new Date(`${value}T00:00:00Z`);
  return Number.isFinite(date.valueOf()) && date.toISOString().slice(0, 10) === value ? value : '';
}
function label(value) {
  if (typeof value !== 'string' || /\b(password|passphrase|token|secret|api[ _-]?key|bearer|private[ _-]?key)\b/i.test(value)) return '';
  return value.replace(/\s+/g, ' ').trim().slice(0, 160);
}
export function adaptMealiePlan(snapshot, options = {}) {
  if (!object(snapshot) || snapshot.schemaVersion !== 'mealie-plan/1.0' || !['available', 'unavailable'].includes(snapshot.status) || !calendar(snapshot.planDate)) {
    throw new Error('Saved Mealie plan requires a supported envelope and explicit calendar selection.');
  }
  const now = new Date(options.now ?? Date.now());
  const maxAgeHours = options.maxAgeHours ?? 36;
  if (!Number.isFinite(now.valueOf()) || !Number.isFinite(maxAgeHours) || maxAgeHours <= 0) throw new Error('Invalid freshness policy.');
  const observed = parseObservation(snapshot.observedAt);
  const reliable = observed && observed <= now;
  const sourceStatus = snapshot.status === 'unavailable' || !reliable ? 'unknown'
    : now - observed > maxAgeHours * 3600000 ? 'stale' : 'healthy';
  const ownerUrl = normalizeWorkbook({ schemaVersion: '1.0', today: { meals: [{ ownerUrl: snapshot.ownerUrl }] } }).today.meals[0].ownerUrl;
  let rows = [];
  if (snapshot.status === 'available') {
    if (!object(snapshot.plan) || !Array.isArray(snapshot.plan.items) || snapshot.plan.items.length > 5000 || snapshot.plan.items.some(row => !object(row) || !calendar(row.date) || !types.has(row.entryType))) {
      throw new Error('Saved Mealie page requires bounded entries with calendar dates and meal types.');
    }
    rows = snapshot.plan.items;
  }
  const matching = rows.filter(row => row.date === snapshot.planDate);
  const selected = matching.slice(0, 50);
  const freshness = snapshot.status === 'unavailable' ? 'Mealie source unavailable.' : !reliable
    ? 'Observation time is missing, ambiguous, invalid or future.' : sourceStatus === 'stale'
      ? `Saved observation exceeds ${maxAgeHours} hours.` : 'Saved observation within freshness window.';
  const observedAt = reliable ? observed.toISOString() : 'Not recorded reliably';
  return {
    schemaVersion: '1.0', generatedAt: now.toISOString(), source: { label: 'Mealie — saved meal plan (offline import)' },
    today: {
      meals: selected.map((row, index) => ({ id: `mealie-plan-${index + 1}`,
        title: label(row.title) || label(object(row.recipe) ? row.recipe.name : null) || 'Unnamed planned meal',
        status: sourceStatus === 'healthy' ? 'warning' : sourceStatus, due: row.date,
        detail: `${row.entryType}. Source calendar date; no timezone conversion. Planned only; ingredient availability and food safety unknown. Observed: ${observedAt}.`, ownerUrl })),
      operations: [{ id: 'mealie-source', title: `Mealie saved selection: ${snapshot.planDate}`, status: sourceStatus,
        detail: `${freshness} Observed: ${observedAt}. Displayed ${selected.length} of ${matching.length} matching entries in this saved page; ${rows.length - matching.length} other-date entries omitted. Selected date is explicit, not inferred as today. No complete-plan coverage or ingredient inference; no writes.`, ownerUrl }],
    },
  };
}
