// Saved task selection only; no API calls, credentials, completion or rescheduling.
import { normalizeWorkbook } from './models.js';
import { parseObservation } from './evidence-time.js';

const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
function title(value) {
  if (typeof value !== 'string' || /\b(password|passphrase|token|secret|api[ _-]?key|bearer|private[ _-]?key)\b/i.test(value)) return 'Unnamed task';
  return value.replace(/\s+/g, ' ').trim().slice(0, 160) || 'Unnamed task';
}

export function adaptGardenTasks(snapshot, options = {}) {
  if (!object(snapshot) || snapshot.schemaVersion !== 'garden-tasks/1.0' || !['available', 'unavailable'].includes(snapshot.status)) {
    throw new Error('Unsupported saved GardenKeeper task envelope.');
  }
  const now = new Date(options.now ?? Date.now());
  const maxAgeHours = options.maxAgeHours ?? 36;
  if (!Number.isFinite(now.valueOf()) || !Number.isFinite(maxAgeHours) || maxAgeHours <= 0) throw new Error('Invalid freshness policy.');
  const observed = parseObservation(snapshot.observedAt);
  const reliable = observed && observed <= now;
  const sourceStatus = snapshot.status === 'unavailable' || !reliable ? 'unknown'
    : now - observed > maxAgeHours * 3600000 ? 'stale' : 'healthy';
  const ownerUrl = normalizeWorkbook({ schemaVersion: '1.0', today: { gardenTasks: [{ ownerUrl: snapshot.ownerUrl }] } }).today.gardenTasks[0].ownerUrl;
  let records = [];
  if (snapshot.status === 'available') {
    if (!Array.isArray(snapshot.tasks) || snapshot.tasks.length > 5000 || snapshot.tasks.some(row => !object(row) || !['pending', 'completed', 'cancelled'].includes(row.status))) {
      throw new Error('Saved tasks require a bounded array with explicit source task states.');
    }
    records = snapshot.tasks;
  }
  const pending = records.filter(row => row.status === 'pending');
  const selected = pending.slice(0, 50);
  const freshness = snapshot.status === 'unavailable' ? 'GardenKeeper source unavailable.'
    : !reliable ? 'Observation time is missing, ambiguous, invalid or future.'
      : sourceStatus === 'stale' ? `Saved observation exceeds ${maxAgeHours} hours.` : 'Saved observation within freshness window.';
  const detail = `${freshness} Observed: ${reliable ? observed.toISOString() : 'Not recorded reliably'}. Displayed ${selected.length} of ${pending.length} pending records in this saved selection; ${records.length - pending.length} completed/cancelled records omitted. No complete-garden or overdue inference; no writes.`;
  return {
    schemaVersion: '1.0', generatedAt: now.toISOString(), source: { label: 'GardenKeeper — saved tasks (offline import)' },
    today: {
      gardenTasks: selected.map((row, index) => {
        const due = parseObservation(row.due_at);
        return { id: `garden-task-${index + 1}`, title: title(row.title),
          status: sourceStatus === 'healthy' ? 'warning' : sourceStatus,
          due: due ? due.toISOString() : '',
          detail: `Recorded pending in a saved selection; no overdue calculation. ${due ? 'Due time shown in UTC.' : 'Due time not recorded reliably.'} Observed: ${reliable ? observed.toISOString() : 'Not recorded reliably'}.`, ownerUrl };
      }),
      operations: [{ id: 'garden-source', title: 'GardenKeeper saved task selection', status: sourceStatus, detail, ownerUrl }],
    },
  };
}
