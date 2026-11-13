// Saved Hub overview only. No network, credentials, stock writes or recipe inference.
import { normalizeWorkbook } from './models.js';
import { parseObservation } from './evidence-time.js';

const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const sensitive = /\b(password|passphrase|token|secret|api[ _-]?key|bearer|private[ _-]?key)\b/i;
function display(value, fallback) {
  if (typeof value !== 'string' || sensitive.test(value)) return fallback;
  return value.replace(/\s+/g, ' ').trim().slice(0, 120) || fallback;
}
function calendar(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return '';
  const date = new Date(`${value}T00:00:00Z`);
  return Number.isFinite(date.valueOf()) && date.toISOString().slice(0, 10) === value ? value : '';
}
function rows(value) {
  if (!Array.isArray(value) || value.length > 5000 || value.some(row => !object(row))) {
    throw new Error('Saved overview requires bounded stock and shopping arrays of objects.');
  }
  return value.slice(0, 50);
}
function quantity(value) {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 ? `${value} (source units)` : 'Quantity unknown';
}

export function adaptGrocyOverview(snapshot, options = {}) {
  if (!object(snapshot) || snapshot.schemaVersion !== 'grocy-overview/1.0' ||
      !['available', 'unavailable'].includes(snapshot.status)) {
    throw new Error('Unsupported saved Grocy overview envelope.');
  }
  const now = new Date(options.now ?? Date.now());
  const maxAgeHours = options.maxAgeHours ?? 36;
  if (!Number.isFinite(now.valueOf()) || !Number.isFinite(maxAgeHours) || maxAgeHours <= 0) {
    throw new Error('Invalid freshness policy.');
  }
  const observed = parseObservation(snapshot.observedAt);
  const reliable = observed && observed <= now; // Never turn a future date into current evidence.
  const status = snapshot.status === 'unavailable' ? 'unknown' : !reliable ? 'unknown'
    : now - observed > maxAgeHours * 3600000 ? 'stale' : 'healthy';
  const observedAt = reliable ? observed.toISOString() : 'Not recorded reliably';
  // URL passes the workbook's scheme/userinfo/credential-parameter filters.
  const ownerUrl = normalizeWorkbook({ schemaVersion: '1.0', today: {
    food: [{ ownerUrl: snapshot.ownerUrl }],
  } }).today.food[0].ownerUrl;
  const scope = 'Saved overview only; filtered/limited rows do not establish complete inventory. No writes.';
  const context = snapshot.status === 'unavailable' ? 'Grocy source unavailable; no stock inferred.'
    : !reliable ? 'Observation time is missing, ambiguous, invalid or future.'
      : status === 'stale' ? `Saved observation exceeds ${maxAgeHours} hours.` : 'Saved observation within freshness window.';
  let stock = [], shopping = [];
  if (snapshot.status === 'available') {
    if (!object(snapshot.overview)) throw new Error('Saved overview payload is missing.');
    stock = rows(snapshot.overview.stock);
    shopping = rows(snapshot.overview.shopping_list);
  }
  const detail = `${context} Observed: ${observedAt}. ${scope}`;
  return {
    schemaVersion: '1.0', generatedAt: now.toISOString(),
    source: { label: 'Grocy — saved overview (offline import)' },
    today: {
      food: stock.map((row, index) => ({
        id: `grocy-stock-${index + 1}`, title: display(row.name, 'Unnamed product'), status,
        location: display(row.location, 'Location not recorded'), quantity: quantity(row.amount),
        // Grocy best-before is not a safety use-by date; never put it into UI's use-by field.
        detail: `${calendar(row.best_before_date) ? `Best before: ${calendar(row.best_before_date)}. ` : 'Best-before date not recorded. '}${detail}`,
        ownerUrl,
      })),
      operations: [{ id: 'grocy-source', title: 'Grocy saved overview', status, detail, ownerUrl },
        ...shopping.map((row, index) => ({ id: `grocy-shopping-${index + 1}`,
          title: `Shopping: ${display(row.name, 'Unnamed product')}`, status,
          detail: `${quantity(row.amount)}. ${detail}`, ownerUrl }))],
    },
  };
}
