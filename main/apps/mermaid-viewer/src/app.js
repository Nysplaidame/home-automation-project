const state = {
  diagrams: [],
  filtered: [],
  activeId: null,
  section: 'all',
  view: {
    scale: 1,
    x: 0,
    y: 0,
    width: 1,
    height: 1,
    minScale: 0.05,
    maxScale: 6,
  },
};

const el = (id) => document.getElementById(id);
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

function currentDiagram() {
  return state.diagrams.find((diagram) => diagram.id === state.activeId) ?? null;
}

function makeButton(className, text, attributes = {}) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = className;
  button.textContent = text;
  for (const [name, value] of Object.entries(attributes)) {
    button.dataset[name] = value;
  }
  return button;
}

function renderSections() {
  const sections = ['all', ...new Set(state.diagrams.map((diagram) => diagram.section))];
  const container = el('section-list');
  container.replaceChildren();
  for (const section of sections) {
    const button = makeButton(
      `chip ${section === state.section ? 'active' : ''}`,
      section === 'all' ? 'All' : section,
      { section },
    );
    button.addEventListener('click', () => {
      state.section = section;
      applyFilters();
    });
    container.append(button);
  }
}

function renderList() {
  const list = el('diagram-list');
  list.replaceChildren();
  if (!state.filtered.length) {
    const empty = document.createElement('p');
    empty.className = 'summary';
    empty.textContent = 'No diagrams match the current filter.';
    list.append(empty);
    return;
  }

  for (const diagram of state.filtered) {
    const button = makeButton(`item ${diagram.id === state.activeId ? 'active' : ''}`, '');
    button.dataset.id = diagram.id;
    const title = document.createElement('strong');
    title.textContent = diagram.title;
    const summary = document.createElement('span');
    summary.className = 'summary';
    summary.textContent = diagram.summary;
    button.append(title, summary);
    button.addEventListener('click', () => selectDiagram(diagram.id));
    list.append(button);
  }
}

async function copy(text, button) {
  await navigator.clipboard.writeText(text);
  if (!button) return;
  const original = button.textContent;
  button.textContent = 'Copied';
  setTimeout(() => {
    button.textContent = original;
  }, 1200);
}

function applyTransform() {
  const canvas = el('diagram-canvas');
  canvas.style.transform = `translate(${state.view.x}px, ${state.view.y}px) scale(${state.view.scale})`;
  el('zoom-level').textContent = `${Math.round(state.view.scale * 100)}%`;
}

function fitView() {
  const stage = el('diagram-stage');
  const padding = 48;
  const availableWidth = Math.max(1, stage.clientWidth - padding);
  const availableHeight = Math.max(1, stage.clientHeight - padding);
  state.view.scale = clamp(
    Math.min(availableWidth / state.view.width, availableHeight / state.view.height),
    state.view.minScale,
    2,
  );
  state.view.x = (stage.clientWidth - state.view.width * state.view.scale) / 2;
  state.view.y = (stage.clientHeight - state.view.height * state.view.scale) / 2;
  applyTransform();
}

function actualSize() {
  const stage = el('diagram-stage');
  state.view.scale = 1;
  state.view.x = Math.max(24, (stage.clientWidth - state.view.width) / 2);
  state.view.y = 24;
  applyTransform();
}

function zoomAt(factor, clientX, clientY) {
  const stage = el('diagram-stage');
  const rect = stage.getBoundingClientRect();
  const pointX = clientX ?? rect.left + rect.width / 2;
  const pointY = clientY ?? rect.top + rect.height / 2;
  const localX = pointX - rect.left;
  const localY = pointY - rect.top;
  const worldX = (localX - state.view.x) / state.view.scale;
  const worldY = (localY - state.view.y) / state.view.scale;
  const nextScale = clamp(state.view.scale * factor, state.view.minScale, state.view.maxScale);
  state.view.x = localX - worldX * nextScale;
  state.view.y = localY - worldY * nextScale;
  state.view.scale = nextScale;
  applyTransform();
}

function prepareSvg(svgMarkup) {
  const canvas = el('diagram-canvas');
  canvas.innerHTML = svgMarkup;
  const svg = canvas.querySelector('svg');
  if (!svg) throw new Error('Mermaid returned no SVG element.');
  const viewBox = svg.viewBox?.baseVal;
  const width = viewBox?.width || Number.parseFloat(svg.getAttribute('width')) || 1200;
  const height = viewBox?.height || Number.parseFloat(svg.getAttribute('height')) || 800;
  state.view.width = width;
  state.view.height = height;
  svg.removeAttribute('width');
  svg.removeAttribute('height');
  svg.style.width = `${width}px`;
  svg.style.height = `${height}px`;
  svg.style.maxWidth = 'none';
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  el('render-status').hidden = true;
  requestAnimationFrame(fitView);
}

async function renderDiagram(diagram) {
  el('diagram-path').textContent = diagram.path;
  el('diagram-title').textContent = diagram.title;
  el('diagram-summary').textContent = diagram.summary;
  el('source-view').textContent = diagram.source;
  el('diagram-canvas').replaceChildren();
  const status = el('render-status');
  status.hidden = false;
  status.textContent = 'Rendering full canonical source…';

  if (!window.mermaid) {
    status.textContent = 'Mermaid failed to load. Refresh the page and try again.';
    return;
  }

  try {
    window.mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      theme: 'dark',
      flowchart: { htmlLabels: true, curve: 'basis', useMaxWidth: false },
    });
    const renderId = `diagram-${diagram.id}-${Date.now()}`;
    const { svg } = await window.mermaid.render(renderId, diagram.source);
    prepareSvg(svg);
  } catch (error) {
    status.hidden = false;
    status.textContent = `Render failed: ${error.message}`;
  }
}

function selectDiagram(id) {
  state.activeId = id;
  renderList();
  const diagram = currentDiagram();
  if (!diagram) return;
  const url = new URL(window.location.href);
  url.searchParams.set('diagram', diagram.id);
  history.replaceState({}, '', url);
  renderDiagram(diagram);
}

function applyFilters() {
  const query = el('search').value.trim().toLowerCase();
  state.filtered = state.diagrams.filter((diagram) => {
    const matchesSection = state.section === 'all' || diagram.section === state.section;
    const haystack = [
      diagram.title,
      diagram.summary,
      diagram.section,
      diagram.tags.join(' '),
      diagram.path,
    ].join(' ').toLowerCase();
    return matchesSection && haystack.includes(query);
  });
  if (!state.filtered.some((diagram) => diagram.id === state.activeId)) {
    state.activeId = state.filtered[0]?.id ?? state.diagrams[0]?.id ?? null;
  }
  el('diagram-count').textContent = `${state.filtered.length}/${state.diagrams.length}`;
  renderSections();
  renderList();
  const diagram = currentDiagram();
  if (diagram) renderDiagram(diagram);
}

function bindPanAndZoom() {
  const stage = el('diagram-stage');
  let drag = null;

  stage.addEventListener('wheel', (event) => {
    event.preventDefault();
    zoomAt(event.deltaY < 0 ? 1.12 : 1 / 1.12, event.clientX, event.clientY);
  }, { passive: false });

  stage.addEventListener('pointerdown', (event) => {
    if (event.button !== 0) return;
    drag = { pointerId: event.pointerId, startX: event.clientX, startY: event.clientY, x: state.view.x, y: state.view.y };
    stage.setPointerCapture(event.pointerId);
    stage.classList.add('is-panning');
  });
  stage.addEventListener('pointermove', (event) => {
    if (!drag || drag.pointerId !== event.pointerId) return;
    state.view.x = drag.x + event.clientX - drag.startX;
    state.view.y = drag.y + event.clientY - drag.startY;
    applyTransform();
  });
  const endDrag = (event) => {
    if (!drag || drag.pointerId !== event.pointerId) return;
    drag = null;
    stage.classList.remove('is-panning');
  };
  stage.addEventListener('pointerup', endDrag);
  stage.addEventListener('pointercancel', endDrag);
  stage.addEventListener('dblclick', fitView);
}

function bindControls() {
  document.querySelector('[data-view-action="zoom-out"]').addEventListener('click', () => zoomAt(1 / 1.25));
  document.querySelector('[data-view-action="zoom-in"]').addEventListener('click', () => zoomAt(1.25));
  document.querySelector('[data-view-action="fit"]').addEventListener('click', fitView);
  document.querySelector('[data-view-action="actual"]').addEventListener('click', actualSize);
  document.querySelector('[data-view-action="fullscreen"]').addEventListener('click', async () => {
    const viewer = el('viewer-panel');
    if (document.fullscreenElement) {
      await document.exitFullscreen();
    } else {
      await viewer.requestFullscreen();
      requestAnimationFrame(fitView);
    }
  });

  el('toggle-source').addEventListener('click', () => {
    const source = el('source-view');
    source.hidden = !source.hidden;
    el('toggle-source').setAttribute('aria-pressed', String(!source.hidden));
  });
}

async function init() {
  const module = await import('./diagram-data.js');
  state.diagrams = module.diagrams;
  state.filtered = state.diagrams;
  const requested = new URLSearchParams(window.location.search).get('diagram');
  const defaultDiagram = state.diagrams.find(
    (diagram) => diagram.id === 'current-master-architecture',
  );
  state.activeId = state.diagrams.some((diagram) => diagram.id === requested)
    ? requested
    : defaultDiagram?.id ?? state.diagrams[0]?.id ?? null;

  bindPanAndZoom();
  bindControls();
  renderSections();
  renderList();
  el('diagram-count').textContent = `${state.diagrams.length}/${state.diagrams.length}`;
  if (state.activeId) renderDiagram(currentDiagram());

  el('search').addEventListener('input', applyFilters);
  el('copy-current').addEventListener('click', async (event) => {
    const diagram = currentDiagram();
    if (!diagram) return;
    const url = new URL(window.location.href);
    url.searchParams.set('diagram', diagram.id);
    await copy(url.toString(), event.currentTarget);
  });
  el('copy-markdown').addEventListener('click', async (event) => {
    const diagram = currentDiagram();
    if (diagram) await copy(`[[docs/diagrams/${diagram.path}]]`, event.currentTarget);
  });
  el('copy-path').addEventListener('click', async (event) => {
    const diagram = currentDiagram();
    if (diagram) await copy(`docs/diagrams/${diagram.path}`, event.currentTarget);
  });
}

init();
