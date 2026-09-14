import {
  buildEmergencyPack,
  buildIncidentReport,
  commissioningProgress,
  cookingAvailability,
  normalizeWorkbook,
  recoveryAssessment,
  sharedDependencyGroups,
  statusMeta,
} from './models.js';
import { demoOperations } from './fixtures/demo-operations.js';
import { adaptHealthSnapshot } from './health-adapter.js';

const tabs = ['today', 'incidents', 'recovery', 'cook', 'commissioning'];
const state = {
  activeTab: 'today',
  evidence: null,
  selectedScenarioId: '',
};

const panel = document.querySelector('#panel');
const evidenceSource = document.querySelector('#evidence-source');
const evidenceGenerated = document.querySelector('#evidence-time');
const healthyCount = document.querySelector('#healthy-count');
const reviewCount = document.querySelector('#review-count');
const unknownCount = document.querySelector('#unknown-count');
const liveMessage = document.querySelector('#live-message');
const importInput = document.querySelector('#evidence-file');
let messageTimer;

function element(tagName, className, content) {
  const node = document.createElement(tagName);
  if (className) node.className = className;
  if (content !== undefined) node.textContent = content;
  return node;
}

function sectionHeading(title, description) {
  const heading = element('header', 'section-heading');
  heading.append(element('h2', '', title));
  if (description) heading.append(element('p', '', description));
  return heading;
}

function statusBadge(value) {
  const normalized = statusMeta[value] ? value : 'unknown';
  const meta = statusMeta[normalized];
  const badge = element('span', `status status-${normalized}`);
  badge.append(element('span', 'status-mark', meta.mark));
  badge.append(document.createTextNode(meta.label));
  return badge;
}

function emptyState(message) {
  return element('p', 'empty', message);
}

function actionLink(url, label = 'Open source') {
  if (!url) return null;
  const link = element('a', 'action-link', label);
  link.href = url;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  return link;
}

function note(text) {
  return element('p', 'notice', text);
}

function setLiveMessage(message, isError = false) {
  window.clearTimeout(messageTimer);
  liveMessage.textContent = message;
  liveMessage.classList.toggle('error', isError);
  liveMessage.classList.add('visible');
  messageTimer = window.setTimeout(() => {
    liveMessage.textContent = '';
    liveMessage.classList.remove('error');
    liveMessage.classList.remove('visible');
  }, 6000);
}

function downloadText(contents, filename, message) {
  const blob = new Blob([contents], { type: 'text/plain;charset=utf-8' });
  const objectUrl = URL.createObjectURL(blob);
  const download = document.createElement('a');
  download.href = objectUrl;
  download.download = filename;
  document.body.append(download);
  download.click();
  download.remove();
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 0);
  setLiveMessage(message);
}

function renderEvidenceStrip() {
  if (!state.evidence) {
    evidenceSource.textContent = 'No evidence loaded';
    evidenceGenerated.textContent = 'Not loaded';
    healthyCount.textContent = '0';
    reviewCount.textContent = '0';
    unknownCount.textContent = '0';
    return;
  }

  evidenceSource.textContent = `Source: ${state.evidence.source}`;
  evidenceGenerated.textContent = state.evidence.generatedAt;
  const dependencyStatuses = state.evidence.dependencies.map((item) => item.status);
  const healthy = dependencyStatuses.filter((value) => value === 'healthy').length;
  const review = dependencyStatuses.filter((value) => ['failed', 'warning', 'stale'].includes(value)).length;
  const evidenceNeeded = dependencyStatuses.filter((value) => ['unknown', 'planned_offline'].includes(value)).length;

  healthyCount.textContent = String(healthy);
  reviewCount.textContent = String(review);
  unknownCount.textContent = String(evidenceNeeded);
}

function summaryItem(label, value, stateClass) {
  const item = element('div', `summary-item ${stateClass}`);
  item.append(element('span', '', label));
  item.append(element('strong', '', value));
  return item;
}

function renderTabs() {
  document.querySelectorAll('[role="tab"]').forEach((tab) => {
    const selected = tab.dataset.tab === state.activeTab;
    tab.classList.toggle('active', selected);
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
  });
  panel.setAttribute('aria-labelledby', `tab-${state.activeTab}`);
}

function renderActionList(items, detailFor) {
  if (!items.length) return emptyState('No imported evidence is available for this area.');
  const list = element('ul', 'item-list');
  for (const item of items) {
    const row = element('li', 'item-row');
    const copy = element('div', 'item-copy');
    copy.append(element('h3', '', item.title));
    const detail = detailFor(item);
    if (detail) copy.append(element('p', '', detail));
    if (item.detail) copy.append(element('p', 'muted', item.detail));
    row.append(copy, statusBadge(item.status));
    const link = actionLink(item.ownerUrl);
    if (link) row.append(link);
    list.append(row);
  }
  return list;
}

function renderToday() {
  const today = state.evidence.today;
  const content = element('div', 'stack');
  content.append(sectionHeading('Today at Home', 'Imported tasks and observations from the current evidence file. Links open their recorded source in a separate tab.'));
  const grid = element('div', 'today-grid');
  const areas = [
    ['Garden', today.gardenTasks, (item) => item.due ? `Due: ${item.due}` : 'Garden observation'],
    ['Food to use', today.food, (item) => [item.location, item.quantity, item.expires ? `Use by: ${item.expires}` : ''].filter(Boolean).join(' · ')],
    ['Meals', today.meals, (item) => item.due ? `Planned: ${item.due}` : 'Meal idea'],
    ['Training', today.workouts, (item) => item.due ? `Planned: ${item.due}` : 'Training item'],
    ['Operations', today.operations, (item) => item.due ? `Review by: ${item.due}` : 'Operations observation'],
  ];
  for (const [label, items, detailFor] of areas) {
    const card = element('section', 'area-card');
    card.append(element('h2', '', label), renderActionList(items, detailFor));
    grid.append(card);
  }
  content.append(grid, note('This screen only presents imported evidence. It does not create chores, alter stock, start backups, or control equipment.'));
  panel.replaceChildren(content);
}

function renderDependencyRow(dependency) {
  const row = element('li', 'item-row');
  const copy = element('div', 'item-copy');
  copy.append(element('h3', '', dependency.label));
  copy.append(element('p', '', `${dependency.kind} · observed ${dependency.observedAt}`));
  if (dependency.detail) copy.append(element('p', 'muted', dependency.detail));
  row.append(copy, statusBadge(dependency.status));
  const runbook = actionLink(dependency.runbook, 'Open runbook');
  if (runbook) row.append(runbook);
  return row;
}

function renderIncidents() {
  const content = element('div', 'stack');
  content.append(sectionHeading('Dependency-aware troubleshooting', 'Compare the evidence timestamps before treating correlated symptoms as a single root cause.'));

  const groups = sharedDependencyGroups(state.evidence);
  const groupSection = element('section', 'area-card');
  groupSection.append(element('h2', '', 'Possible shared dependencies'));
  if (!groups.length) {
    groupSection.append(emptyState('No notable imported symptoms share a direct declared dependency.'));
  } else {
    const list = element('ul', 'group-list');
    for (const group of groups) {
      const row = element('li', 'dependency-group');
      const header = element('div', 'row-header');
      header.append(element('h3', '', group.dependency.label), statusBadge(group.status));
      const names = group.impacted.map((item) => item.label).join(', ');
      row.append(header, element('p', '', `${names} each declare this dependency.`));
      if (group.dependency.detail) row.append(element('p', 'muted', group.dependency.detail));
      list.append(row);
    }
    groupSection.append(list);
  }
  content.append(groupSection, note('A shared dependency is a triage hint, not a root-cause claim. Verify each service and its timestamps before remediation.'));

  const dependencySection = element('section', 'area-card');
  dependencySection.append(element('h2', '', 'Imported dependency evidence'));
  const dependencies = element('ul', 'item-list');
  for (const dependency of state.evidence.dependencies) dependencies.append(renderDependencyRow(dependency));
  dependencySection.append(dependencies);
  content.append(dependencySection);

  const incidentSection = element('section', 'area-card');
  incidentSection.append(element('h2', '', 'Incident evidence'));
  if (!state.evidence.incidents.length) {
    incidentSection.append(emptyState('No imported incidents.'));
  } else {
    const incidents = element('ul', 'item-list');
    for (const incident of state.evidence.incidents) {
      const row = element('li', 'item-row');
      const copy = element('div', 'item-copy');
      copy.append(element('h3', '', incident.title));
      copy.append(element('p', '', `Observed ${incident.observedAt}`));
      if (incident.note) copy.append(element('p', 'muted', incident.note));
      const exportButton = element('button', 'secondary-button', 'Download incident report');
      exportButton.type = 'button';
      exportButton.addEventListener('click', () => {
        downloadText(buildIncidentReport(incident, state.evidence), `${incident.id}-evidence.txt`, 'Incident evidence report downloaded.');
      });
      row.append(copy, statusBadge(incident.status), exportButton);
      incidents.append(row);
    }
    incidentSection.append(incidents);
  }
  content.append(incidentSection);
  panel.replaceChildren(content);
}

function confidenceLabel(value) {
  return {
    proved: 'Restore exercise proved',
    not_proven: 'Backed up, not restore-proven',
    attention: 'Recovery evidence needs attention',
    needs_evidence: 'Recovery evidence incomplete',
  }[value] ?? 'Recovery evidence incomplete';
}

function evidenceCell(label, evidence) {
  const cell = element('div', 'evidence-cell');
  cell.append(element('span', '', label), statusBadge(evidence.status), element('small', '', evidence.observedAt));
  if (evidence.detail) cell.append(element('small', 'muted', evidence.detail));
  return cell;
}

function renderRecovery() {
  const content = element('div', 'stack');
  const heading = sectionHeading('Recovery readiness', 'Backups, integrity evidence, and restore exercises are tracked separately so a green backup does not imply a proven recovery.');
  const exportButton = element('button', 'secondary-button', 'Download emergency pack');
  exportButton.type = 'button';
  exportButton.addEventListener('click', () => {
    downloadText(buildEmergencyPack(state.evidence), 'home-operations-emergency-pack.md', 'Emergency evidence pack downloaded.');
  });
  heading.append(exportButton);
  content.append(heading);
  const systems = element('div', 'recovery-grid');
  for (const system of state.evidence.recovery) {
    const card = element('section', 'recovery-card');
    const header = element('div', 'row-header');
    const confidence = recoveryAssessment(system);
    header.append(element('h2', '', system.label), element('span', `confidence confidence-${confidence}`, confidenceLabel(confidence)));
    card.append(header);
    const cells = element('div', 'evidence-grid');
    cells.append(evidenceCell('Backup', system.backup), evidenceCell('Integrity', system.integrity), evidenceCell('Restore exercise', system.restore));
    card.append(cells);
    const runbook = actionLink(system.runbook, 'Open recovery runbook');
    if (runbook) card.append(runbook);
    systems.append(card);
  }
  content.append(systems, note('The downloaded pack is an evidence index. It contains no credentials and cannot run a restore.'));
  panel.replaceChildren(content);
}

function cookingStatus(value) {
  return { ready: 'healthy', missing: 'warning', unknown: 'unknown' }[value] ?? 'unknown';
}

function renderCook() {
  const content = element('div', 'stack');
  content.append(sectionHeading('Cook what we have', 'Recipe candidates are ranked only by the ingredient availability declared in imported evidence.'));
  if (!state.evidence.cooking.length) {
    content.append(emptyState('No imported recipe candidates.'));
  } else {
    const candidates = element('div', 'recipe-grid');
    for (const candidate of state.evidence.cooking) {
      const card = element('section', 'recipe-card');
      const availability = cookingAvailability(candidate);
      const header = element('div', 'row-header');
      header.append(element('h2', '', candidate.title), statusBadge(cookingStatus(availability)));
      card.append(header);
      if (candidate.detail) card.append(element('p', 'muted', candidate.detail));
      const ingredients = element('ul', 'ingredient-list');
      for (const ingredient of candidate.ingredients) {
        const row = element('li', `ingredient ${ingredient.availability}`);
        const name = element('span', '', ingredient.name);
        const values = [ingredient.required && `Need ${ingredient.required}`, ingredient.available && `Have ${ingredient.available}`, ingredient.expires && `Use by ${ingredient.expires}`].filter(Boolean).join(' · ');
        row.append(name, element('small', '', values || 'No quantity evidence'));
        ingredients.append(row);
      }
      card.append(ingredients);
      const source = actionLink(candidate.sourceUrl, 'Open recipe source');
      if (source) card.append(source);
      candidates.append(card);
    }
    content.append(candidates);
  }
  content.append(note('Availability is advisory. Confirm stock, allergens, and dates in the authoritative household systems before cooking.'));
  panel.replaceChildren(content);
}

function renderCommissioning() {
  const content = element('div', 'stack');
  content.append(sectionHeading('VentSys commissioning companion', 'A visual checklist for disconnected hardware. This workbench cannot publish MQTT, change Home Assistant, or energise a device.'));
  const progress = commissioningProgress(state.evidence.commissioning.devices);
  const progressList = element('div', 'progress-list');
  for (const [stage, count] of Object.entries(progress)) {
    progressList.append(summaryItem(stage[0].toUpperCase() + stage.slice(1), `${count}`, stage === 'accepted' && count ? 'healthy' : 'unknown'));
  }
  content.append(progressList);

  const devices = element('div', 'commissioning-grid');
  for (const device of state.evidence.commissioning.devices) {
    const card = element('section', 'device-card');
    const header = element('div', 'row-header');
    header.append(element('h2', '', device.label), element('span', `stage stage-${device.stage}`, device.stage));
    card.append(header, element('p', 'muted', device.type));
    if (!device.checks.length) {
      card.append(emptyState('No checks have been imported.'));
    } else {
      const checks = element('ul', 'check-list');
      for (const check of device.checks) {
        const row = element('li', 'check-row');
        const copy = element('div', 'item-copy');
        copy.append(element('h3', '', check.title), element('p', '', `Observed ${check.observedAt}`));
        if (check.detail) copy.append(element('p', 'muted', check.detail));
        row.append(copy, statusBadge(check.status));
        checks.append(row);
      }
      card.append(checks);
    }
    devices.append(card);
  }
  content.append(devices);

  const scenarios = state.evidence.commissioning.scenarios;
  const scenarioSection = element('section', 'scenario-card');
  scenarioSection.append(element('h2', '', 'Visual-only scenarios'));
  if (!scenarios.length) {
    scenarioSection.append(emptyState('No scenarios have been imported.'));
  } else {
    if (!scenarios.some((scenario) => scenario.id === state.selectedScenarioId)) state.selectedScenarioId = scenarios[0].id;
    const selector = element('div', 'scenario-selector');
    for (const scenario of scenarios) {
      const button = element('button', 'scenario-button', scenario.label);
      button.type = 'button';
      const selected = scenario.id === state.selectedScenarioId;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
      button.addEventListener('click', () => {
        state.selectedScenarioId = scenario.id;
        renderPanel();
      });
      selector.append(button);
    }
    const selected = scenarios.find((scenario) => scenario.id === state.selectedScenarioId) ?? scenarios[0];
    const steps = element('ol', 'scenario-steps');
    for (const step of selected.steps) {
      const row = element('li', 'check-row');
      const copy = element('div', 'item-copy');
      copy.append(element('h3', '', step.title));
      if (step.detail) copy.append(element('p', 'muted', step.detail));
      row.append(copy, statusBadge(step.status));
      steps.append(row);
    }
    scenarioSection.append(selector);
    if (selected.description) scenarioSection.append(element('p', 'muted', selected.description));
    scenarioSection.append(steps);
  }
  content.append(scenarioSection, note('Record observations in the source system, then import a fresh evidence file. This companion never sends a command.'));
  panel.replaceChildren(content);
}

function renderEmpty() {
  const content = element('section', 'empty-panel');
  content.append(element('h2', '', 'Load operational evidence'), element('p', '', 'Use the demonstration data to explore the workflows, or import a schema 1.0 JSON evidence export. Data stays in this browser tab and is cleared when you close it.'));
  const demo = element('button', 'primary-button', 'Load demonstration');
  demo.type = 'button';
  demo.addEventListener('click', () => loadEvidence(demoOperations, 'Demonstration evidence loaded.'));
  content.append(demo, note('The demonstration is deliberately disconnected from Home Assistant, household apps, food stock, and VentSys hardware.'));
  panel.replaceChildren(content);
}

function renderPanel() {
  renderTabs();
  renderEvidenceStrip();
  if (!state.evidence) {
    renderEmpty();
    return;
  }
  ({
    today: renderToday,
    incidents: renderIncidents,
    recovery: renderRecovery,
    cook: renderCook,
    commissioning: renderCommissioning,
  }[state.activeTab] ?? renderToday)();
}

function loadEvidence(rawEvidence, message) {
  try {
    state.evidence = normalizeWorkbook(rawEvidence);
    state.selectedScenarioId = '';
    renderPanel();
    setLiveMessage(message);
  } catch (error) {
    setLiveMessage(error instanceof Error ? error.message : 'The evidence file could not be read.', true);
  }
}

async function importEvidence(file) {
  if (!file) return;
  if (file.size > 512 * 1024) {
    setLiveMessage('Evidence imports are limited to 512 KB.', true);
    return;
  }
  try {
    const rawEvidence = JSON.parse(await file.text());
    const evidence = rawEvidence && !rawEvidence.schemaVersion && rawEvidence.collector
      ? adaptHealthSnapshot(rawEvidence) : rawEvidence;
    loadEvidence(evidence, `Imported evidence from ${file.name}.`);
  } catch (error) {
    setLiveMessage(error instanceof SyntaxError ? 'The selected file is not valid JSON.' : 'The evidence file could not be imported.', true);
  } finally {
    importInput.value = '';
  }
}

document.querySelector('#load-demo').addEventListener('click', () => loadEvidence(demoOperations, 'Demonstration evidence loaded.'));
document.querySelector('#clear-evidence').addEventListener('click', () => {
  state.evidence = null;
  state.selectedScenarioId = '';
  renderPanel();
  setLiveMessage('Imported evidence cleared from this browser tab.');
});
importInput.addEventListener('change', () => importEvidence(importInput.files?.[0]));

document.querySelector('#tabs').addEventListener('click', (event) => {
  const tab = event.target.closest('[role="tab"]');
  if (!tab) return;
  state.activeTab = tab.dataset.tab;
  renderPanel();
});

document.querySelector('#tabs').addEventListener('keydown', (event) => {
  const currentIndex = tabs.indexOf(state.activeTab);
  let nextIndex = currentIndex;
  if (event.key === 'ArrowRight') nextIndex = (currentIndex + 1) % tabs.length;
  if (event.key === 'ArrowLeft') nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
  if (event.key === 'Home') nextIndex = 0;
  if (event.key === 'End') nextIndex = tabs.length - 1;
  if (nextIndex === currentIndex) return;
  event.preventDefault();
  state.activeTab = tabs[nextIndex];
  renderPanel();
  document.querySelector(`[data-tab="${state.activeTab}"]`)?.focus();
});

renderPanel();
