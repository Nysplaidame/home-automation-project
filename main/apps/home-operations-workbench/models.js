export const statusMeta = Object.freeze({
  healthy: { label: 'Healthy', mark: 'OK' },
  failed: { label: 'Action needed', mark: '!' },
  warning: { label: 'Needs review', mark: '~' },
  stale: { label: 'Stale evidence', mark: '⌛' },
  unknown: { label: 'Needs evidence', mark: '?' },
  planned_offline: { label: 'Planned offline', mark: '–' },
});

const STATUS_ALIASES = Object.freeze({
  pass: 'healthy',
  fail: 'failed',
  warn: 'warning',
  skipped: 'unknown',
  planned: 'planned_offline',
});
const VALID_STATUSES = new Set(Object.keys(statusMeta));
const COMMISSIONING_STAGES = new Set(['planned', 'bench', 'installed', 'accepted']);
const SENSITIVE_PATTERN = /\b(password|passphrase|token|secret|api[ _-]?key|bearer|private[ _-]?key)\b/i;
const SENSITIVE_URL_PARAMETER_PATTERN = /password|passphrase|token|secret|api[_-]?key|bearer|private[_-]?key/i;

function object(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
}

function items(value, limit = 50) {
  return Array.isArray(value) ? value.slice(0, limit) : [];
}

function text(value, fallback = '', limit = 240) {
  if (typeof value !== 'string') return fallback;
  const compact = value.replace(/\s+/g, ' ').trim().slice(0, limit);
  return compact || fallback;
}

function id(value, fallback) {
  const normalized = text(value, '', 80).toLowerCase().replace(/[^a-z0-9_-]/g, '-');
  return normalized.replace(/-+/g, '-').replace(/^-|-$/g, '') || fallback;
}

function status(value, fallback = 'unknown') {
  const candidate = STATUS_ALIASES[text(value, fallback, 40).toLowerCase()] ?? text(value, fallback, 40).toLowerCase();
  return VALID_STATUSES.has(candidate) ? candidate : fallback;
}

function safeDetail(value) {
  const detail = text(value, '', 320);
  return SENSITIVE_PATTERN.test(detail) ? 'Sensitive detail omitted.' : detail;
}

function safeUrl(value) {
  const candidate = text(value, '', 600);
  if (!candidate) return '';
  try {
    const parsed = new URL(candidate);
    if (!['http:', 'https:'].includes(parsed.protocol)) return '';
    if (parsed.username || parsed.password) return '';
    if ([...parsed.searchParams.keys()].some((key) => SENSITIVE_URL_PARAMETER_PATTERN.test(key))) return '';
    return parsed.href;
  } catch {
    return '';
  }
}

function evidence(value) {
  const source = typeof value === 'string' ? { status: value } : object(value);
  return {
    status: status(source.status),
    observedAt: text(source.observedAt ?? source.timestamp, 'Not recorded', 100),
    detail: safeDetail(source.detail),
  };
}

function action(value, prefix, index) {
  const source = object(value);
  return {
    id: id(source.id, `${prefix}-${index + 1}`),
    title: text(source.title, 'Untitled item', 160),
    detail: safeDetail(source.detail),
    status: status(source.status, 'unknown'),
    due: text(source.due, '', 80),
    ownerUrl: safeUrl(source.ownerUrl ?? source.url),
  };
}

function ingredient(value, index) {
  const source = object(value);
  const availability = text(source.availability, 'unknown', 40).toLowerCase();
  return {
    id: id(source.id, `ingredient-${index + 1}`),
    name: text(source.name, 'Unnamed ingredient', 120),
    required: text(source.required, '', 80),
    available: text(source.available, '', 80),
    availability: ['available', 'missing', 'unknown'].includes(availability) ? availability : 'unknown',
    expires: text(source.expires, '', 80),
  };
}

export function normalizeWorkbook(raw) {
  const source = object(raw);
  if (text(source.schemaVersion, '', 20) !== '1.0') {
    throw new Error('This file does not use the supported Home Operations evidence schema (1.0).');
  }

  const today = object(source.today);
  const recovery = object(source.recovery);
  const commissioning = object(source.commissioning);
  const dependencies = items(source.dependencies).map((value, index) => {
    const item = object(value);
    return {
      id: id(item.id, `dependency-${index + 1}`),
      label: text(item.label, 'Unnamed dependency', 120),
      kind: text(item.kind, 'service', 80),
      status: status(item.status),
      observedAt: text(item.observedAt, 'Not recorded', 100),
      detail: safeDetail(item.detail),
      runbook: safeUrl(item.runbook),
      dependsOn: items(item.dependsOn, 12).map((dependencyId) => id(dependencyId, '')).filter(Boolean),
    };
  });

  return {
    schemaVersion: '1.0',
    generatedAt: text(source.generatedAt, 'Not recorded', 100),
    source: text(object(source.source).label ?? source.source, 'Imported evidence', 120),
    today: {
      gardenTasks: items(today.gardenTasks).map((value, index) => action(value, 'garden', index)),
      food: items(today.food).map((value, index) => {
        const item = action(value, 'food', index);
        return { ...item, location: text(object(value).location, 'Location not recorded', 100), quantity: text(object(value).quantity, '', 80), expires: text(object(value).expires, '', 80) };
      }),
      meals: items(today.meals).map((value, index) => action(value, 'meal', index)),
      workouts: items(today.workouts).map((value, index) => action(value, 'workout', index)),
      operations: items(today.operations).map((value, index) => action(value, 'operation', index)),
    },
    dependencies,
    incidents: items(source.incidents, 30).map((value, index) => {
      const item = object(value);
      return {
        id: id(item.id, `incident-${index + 1}`),
        title: text(item.title, 'Untitled incident', 160),
        observedAt: text(item.observedAt, 'Not recorded', 100),
        status: status(item.status),
        note: safeDetail(item.note),
        signals: items(item.signals, 20).map((signal) => id(signal, '')).filter(Boolean),
      };
    }),
    recovery: items(recovery.systems).map((value, index) => {
      const item = object(value);
      return {
        id: id(item.id, `recovery-${index + 1}`),
        label: text(item.label, 'Unnamed system', 120),
        backup: evidence(item.backup),
        integrity: evidence(item.integrity),
        restore: evidence(item.restore),
        runbook: safeUrl(item.runbook),
        dependencies: items(item.dependencies, 12).map((dependencyId) => id(dependencyId, '')).filter(Boolean),
      };
    }),
    cooking: items(object(source.cooking).candidates).map((value, index) => {
      const item = object(value);
      return {
        id: id(item.id, `recipe-${index + 1}`),
        title: text(item.title, 'Untitled recipe', 160),
        sourceUrl: safeUrl(item.sourceUrl),
        detail: safeDetail(item.detail),
        ingredients: items(item.ingredients).map(ingredient),
      };
    }),
    commissioning: {
      devices: items(commissioning.devices).map((value, index) => {
        const item = object(value);
        const stage = text(item.stage, 'planned', 40).toLowerCase();
        return {
          id: id(item.id, `device-${index + 1}`),
          label: text(item.label, 'Unnamed device', 120),
          type: text(item.type, 'Device', 80),
          stage: COMMISSIONING_STAGES.has(stage) ? stage : 'planned',
          checks: items(item.checks, 20).map((check, checkIndex) => {
            const normalized = action(check, `device-${index + 1}-check`, checkIndex);
            return { ...normalized, observedAt: text(object(check).observedAt, 'Not recorded', 100) };
          }),
        };
      }),
      scenarios: items(commissioning.scenarios).map((value, index) => {
        const item = object(value);
        return {
          id: id(item.id, `scenario-${index + 1}`),
          label: text(item.label, 'Untitled scenario', 120),
          description: safeDetail(item.description),
          steps: items(item.steps, 12).map((step, stepIndex) => action(step, `scenario-${index + 1}`, stepIndex)),
        };
      }),
    },
  };
}

function statusRank(value) {
  return ['failed', 'warning', 'stale', 'unknown', 'planned_offline', 'healthy'].indexOf(value);
}

export function aggregateStatus(values) {
  const normalized = values.map((value) => status(value));
  return normalized.sort((left, right) => statusRank(left) - statusRank(right))[0] ?? 'unknown';
}

export function sharedDependencyGroups(workbook) {
  const notable = workbook.dependencies.filter(({ status: value }) => ['failed', 'warning', 'stale'].includes(value));
  const byId = new Map(workbook.dependencies.map((item) => [item.id, item]));
  const groups = new Map();
  for (const item of notable) {
    for (const dependencyId of item.dependsOn) {
      if (!groups.has(dependencyId)) groups.set(dependencyId, []);
      groups.get(dependencyId).push(item);
    }
  }
  return [...groups.entries()]
    .filter(([, impacted]) => impacted.length > 1)
    .map(([dependencyId, impacted]) => ({
      dependency: byId.get(dependencyId) ?? { id: dependencyId, label: dependencyId, status: 'unknown', detail: '' },
      impacted,
      status: aggregateStatus(impacted.map((item) => item.status)),
    }));
}

export function recoveryAssessment(system) {
  if (system.restore.status === 'healthy') return 'proved';
  if (['failed', 'warning', 'stale'].includes(system.backup.status) || ['failed', 'warning', 'stale'].includes(system.integrity.status)) return 'attention';
  if (system.backup.status === 'healthy' && system.integrity.status === 'healthy') return 'not_proven';
  return 'needs_evidence';
}

export function cookingAvailability(candidate) {
  const states = candidate.ingredients.map(({ availability }) => availability);
  if (states.includes('missing')) return 'missing';
  if (states.includes('unknown')) return 'unknown';
  return 'ready';
}

export function commissioningProgress(devices) {
  const summary = { planned: 0, bench: 0, installed: 0, accepted: 0 };
  for (const { stage } of devices) summary[stage] += 1;
  return summary;
}

export function buildIncidentReport(incident, workbook) {
  const dependencyById = new Map(workbook.dependencies.map((item) => [item.id, item]));
  const lines = [
    `Incident: ${incident.title}`,
    `Observed: ${incident.observedAt}`,
    `Assessment: ${statusMeta[incident.status].label}`,
    '',
    'Signals:',
  ];
  for (const signalId of incident.signals) {
    const signal = dependencyById.get(signalId);
    lines.push(`- ${signal?.label ?? signalId}: ${statusMeta[signal?.status ?? 'unknown'].label}`);
  }
  if (incident.note) lines.push('', 'Operator note:', incident.note);
  lines.push('', 'This report contains imported evidence only. It does not contain credentials or remediation actions.');
  return lines.join('\n');
}

export function buildEmergencyPack(workbook) {
  const lines = [
    '# Home Operations Emergency Pack',
    '',
    `Generated from: ${workbook.source}`,
    `Evidence timestamp: ${workbook.generatedAt}`,
    '',
    'This is an evidence index. It cannot restore a service and contains no credentials.',
    '',
  ];
  for (const system of workbook.recovery) {
    lines.push(`## ${system.label}`);
    lines.push(`- Backup: ${statusMeta[system.backup.status].label} (${system.backup.observedAt})`);
    lines.push(`- Integrity: ${statusMeta[system.integrity.status].label} (${system.integrity.observedAt})`);
    lines.push(`- Restore exercise: ${statusMeta[system.restore.status].label} (${system.restore.observedAt})`);
    lines.push(`- Recovery confidence: ${recoveryAssessment(system).replace('_', ' ')}`);
    if (system.runbook) lines.push(`- Runbook: ${system.runbook}`);
    lines.push('');
  }
  return lines.join('\n');
}
