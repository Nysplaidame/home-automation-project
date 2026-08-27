import {
  buildIncidentReport,
  evidenceCoverage,
  evidenceFocus,
  evaluateKeys,
  evaluateSymptom,
  normalizeSnapshot,
  sampleSnapshots,
  snapshotSummary,
  statusMeta,
  symptoms,
} from './diagnostic-model.js';

const state = {
  activeId: symptoms[0].id,
  snapshot: null,
  completed: new Set(),
};
let liveMessageTimer;

const byId = (id) => document.getElementById(id);
const activeSymptom = () => symptoms.find(({ id }) => id === state.activeId) ?? symptoms[0];

function make(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function statusNode(status, compact = false) {
  const meta = statusMeta[status] ?? statusMeta.unknown;
  const node = make('span', `status status-${status}`);
  node.append(make('span', 'status-mark', meta.mark));
  if (!compact) node.append(make('span', 'status-label', meta.label));
  node.setAttribute('aria-label', meta.label);
  return node;
}

function setLiveMessage(message) {
  clearTimeout(liveMessageTimer);
  byId('live-message').textContent = message;
  byId('live-message').classList.add('visible');
  liveMessageTimer = setTimeout(() => {
    byId('live-message').textContent = '';
    byId('live-message').classList.remove('visible');
  }, 2600);
}

async function copyText(text, successMessage) {
  try {
    await navigator.clipboard.writeText(text);
    setLiveMessage(successMessage);
  } catch {
    setLiveMessage('Copy failed. Select the text manually.');
  }
}

function renderSummary() {
  const summary = snapshotSummary(state.snapshot);
  byId('snapshot-time').textContent = state.snapshot?.timestamp ?? 'Not loaded';
  byId('snapshot-source').textContent = state.snapshot?.collector ?? 'Collector not supplied';
  byId('pass-count').textContent = String(summary.pass);
  byId('fail-count').textContent = String(summary.fail);
  const symptomUnknown = symptoms.filter((item) => evaluateSymptom(item, state.snapshot) === 'unknown').length;
  byId('unknown-count').textContent = `${symptomUnknown} symptom${symptomUnknown === 1 ? '' : 's'}`;
}

function renderSymptoms() {
  const list = byId('symptom-list');
  list.replaceChildren();
  for (const symptom of symptoms) {
    const status = evaluateSymptom(symptom, state.snapshot);
    const button = make('button', `symptom-button${symptom.id === state.activeId ? ' active' : ''}`);
    button.type = 'button';
    button.setAttribute('aria-pressed', String(symptom.id === state.activeId));
    button.addEventListener('click', () => {
      state.activeId = symptom.id;
      render();
      byId('active-title').focus({ preventScroll: true });
    });
    const top = make('span', 'symptom-topline');
    top.append(make('span', 'symptom-order', symptom.order), statusNode(status, true));
    button.append(top, make('strong', '', symptom.title), make('span', 'symptom-short', symptom.short));
    list.append(button);
  }
}

function renderPath(symptom) {
  const path = byId('dependency-path');
  path.replaceChildren();
  symptom.path.forEach((node, index) => {
    const status = evaluateKeys(node.keys, state.snapshot);
    const item = make('li', `path-node status-border-${status}`);
    item.append(make('span', 'path-index', String(index + 1).padStart(2, '0')), make('strong', '', node.label));
    path.append(item);
  });
}

function renderSteps(symptom) {
  const list = byId('diagnostic-steps');
  list.replaceChildren();
  symptom.steps.forEach((item, index) => {
    const row = make('li', 'diagnostic-step');
    const checkWrap = make('div', 'step-check');
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.id = `step-${symptom.id}-${item.id}`;
    input.checked = state.completed.has(`${symptom.id}:${item.id}`);
    input.addEventListener('change', () => {
      const key = `${symptom.id}:${item.id}`;
      input.checked ? state.completed.add(key) : state.completed.delete(key);
    });
    const label = document.createElement('label');
    label.htmlFor = input.id;
    label.textContent = `Mark step ${index + 1} collected`;
    checkWrap.append(input, label);

    const body = make('div', 'step-body');
    const heading = make('div', 'step-heading');
    heading.append(make('span', 'step-stage', item.stage), make('h4', '', item.title));
    const context = make('p', 'step-context');
    context.append(make('span', '', 'Run on '), make('strong', '', item.runOn));
    const commandRow = make('div', 'command-row');
    commandRow.append(make('code', '', item.command));
    const copyButton = make('button', 'copy-command', 'Copy');
    copyButton.type = 'button';
    copyButton.addEventListener('click', () => copyText(item.command, `Copied step ${index + 1} command.`));
    commandRow.append(copyButton);
    const interpretation = make('dl', 'interpretation');
    interpretation.append(make('dt', '', 'Expected'), make('dd', '', item.expected), make('dt', '', 'If not'), make('dd', '', item.failure));
    body.append(heading, context, commandRow, interpretation);
    row.append(checkWrap, body);
    list.append(row);
  });
}

function renderEvidence(symptom) {
  const list = byId('evidence-list');
  list.replaceChildren();
  for (const item of symptom.checks) {
    const status = state.snapshot?.checks[item.key] ?? 'unknown';
    const row = make('div', 'evidence-row');
    const copy = make('div');
    copy.append(make('strong', '', item.label), make('span', 'evidence-stage', item.stage));
    const detail = state.snapshot?.details[item.key];
    if (detail) copy.append(make('span', 'evidence-detail', detail));
    row.append(copy, statusNode(status));
    list.append(row);
  }
}

function renderReferences(symptom) {
  const list = byId('reference-list');
  list.replaceChildren();
  for (const [label, path] of symptom.docs) {
    const item = document.createElement('li');
    const button = make('button', 'reference-button');
    button.type = 'button';
    button.append(make('strong', '', label), make('code', '', path));
    button.addEventListener('click', () => copyText(path, `Copied ${label} path.`));
    item.append(button);
    list.append(item);
  }
}

function renderInvestigation() {
  const symptom = activeSymptom();
  const status = evaluateSymptom(symptom, state.snapshot);
  byId('active-order').textContent = `Symptom ${symptom.order}`;
  byId('active-title').textContent = symptom.title;
  byId('active-title').tabIndex = -1;
  byId('active-description').textContent = symptom.description;
  const pill = byId('active-status');
  pill.className = `status-pill status-${status}`;
  pill.textContent = `${statusMeta[status].mark} ${statusMeta[status].label}`;
  const focus = evidenceFocus(symptom, state.snapshot);
  const focusBox = byId('evidence-focus');
  focusBox.className = `evidence-focus status-border-${focus.status}`;
  byId('focus-stage').textContent = focus.stage;
  byId('focus-label').textContent = focus.label;
  byId('focus-message').textContent = focus.message;
  const coverage = evidenceCoverage(symptom, state.snapshot);
  byId('evidence-coverage').textContent = `${coverage.collected}/${coverage.total} signals collected`;
  renderPath(symptom);
  renderSteps(symptom);
  renderEvidence(symptom);
  renderReferences(symptom);
}

function render() {
  renderSummary();
  renderSymptoms();
  renderInvestigation();
}

function loadSnapshot(raw, message) {
  const error = byId('snapshot-error');
  try {
    state.snapshot = normalizeSnapshot(raw);
    error.hidden = true;
    error.textContent = '';
    render();
    setLiveMessage(message);
  } catch (caught) {
    error.textContent = caught instanceof Error ? caught.message : 'Snapshot could not be loaded.';
    error.hidden = false;
  }
}

function initSamples() {
  const select = byId('sample-select');
  for (const [key, sample] of Object.entries(sampleSnapshots)) {
    const option = document.createElement('option');
    option.value = key;
    option.textContent = sample.label;
    select.append(option);
  }
  select.addEventListener('change', () => {
    if (!select.value) return;
    loadSnapshot(sampleSnapshots[select.value].value, `Loaded ${sampleSnapshots[select.value].label}.`);
  });
}

byId('snapshot-file').addEventListener('change', async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  if (file.size > 512 * 1024) {
    byId('snapshot-error').textContent = 'Snapshot is larger than the 512 KiB POC limit.';
    byId('snapshot-error').hidden = false;
    return;
  }
  try {
    const parsed = JSON.parse(await file.text());
    loadSnapshot(parsed, `Loaded ${file.name}.`);
  } catch {
    byId('snapshot-error').textContent = 'The selected file is not valid JSON.';
    byId('snapshot-error').hidden = false;
  }
});

byId('clear-snapshot').addEventListener('click', () => {
  state.snapshot = null;
  byId('sample-select').value = '';
  byId('snapshot-file').value = '';
  byId('snapshot-error').hidden = true;
  render();
  setLiveMessage('Diagnostic snapshot cleared.');
});

byId('copy-report').addEventListener('click', () => {
  copyText(buildIncidentReport(activeSymptom(), state.snapshot, byId('notes').value), 'Incident report copied.');
});

initSamples();
render();
