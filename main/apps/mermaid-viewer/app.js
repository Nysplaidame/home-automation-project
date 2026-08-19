let state = { diagrams: [], filtered: [], activeId: null, section: 'all' };

const el = (id) => document.getElementById(id);

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function currentDiagram() {
  return state.diagrams.find((d) => d.id === state.activeId) || null;
}

function renderSections() {
  const sections = ['all', ...new Set(state.diagrams.map((d) => d.section))];
  el('section-list').innerHTML = sections.map((section) => `
    <button class="chip ${section === state.section ? 'active' : ''}" data-section="${section}">
      ${section === 'all' ? 'All' : section}
    </button>
  `).join('');
  el('section-list').querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', () => {
      state.section = button.dataset.section;
      applyFilters();
    });
  });
}

function renderList() {
  const list = el('diagram-list');
  list.innerHTML = state.filtered.map((diagram) => `
    <div class="item ${diagram.id === state.activeId ? 'active' : ''}" data-id="${diagram.id}">
      <strong>${diagram.title}</strong>
      <div class="summary">${diagram.summary}</div>
    </div>
  `).join('') || '<p class="summary">No diagrams match the current filter.</p>';
  list.querySelectorAll('[data-id]').forEach((item) => {
    item.addEventListener('click', () => selectDiagram(item.dataset.id));
  });
}

async function copy(text) {
  await navigator.clipboard.writeText(text);
}

function renderDiagram(diagram) {
  el('diagram-path').textContent = diagram.path;
  el('diagram-title').textContent = diagram.title;
  el('diagram-summary').textContent = diagram.summary;
  const target = el('render-target');
  target.textContent = 'Rendering...';
  el('source-view').hidden = true;
  const mermaid = window.mermaid;
  if (!mermaid) {
    target.textContent = 'Mermaid failed to load. Refresh the page and try again.';
    return;
  }

  mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'dark' });
  const source = diagram.source;
  el('source-view').textContent = source;
  el('source-view').hidden = false;
  const id = `diagram-${slugify(diagram.id)}-${Date.now()}`;
  mermaid.render(id, source).then(({ svg }) => {
    target.innerHTML = svg;
  }).catch((error) => {
    target.textContent = `Render failed: ${error.message}`;
  });
}

function selectDiagram(id) {
  state.activeId = id;
  renderList();
  const diagram = currentDiagram();
  if (diagram) renderDiagram(diagram);
}

function applyFilters() {
  const query = el('search').value.trim().toLowerCase();
  state.filtered = state.diagrams.filter((diagram) => {
    const matchesSection = state.section === 'all' || diagram.section === state.section;
    const haystack = [diagram.title, diagram.summary, diagram.section, diagram.tags.join(' '), diagram.path].join(' ').toLowerCase();
    return matchesSection && haystack.includes(query);
  });
  if (!state.filtered.some((d) => d.id === state.activeId)) {
    state.activeId = state.filtered[0]?.id ?? state.diagrams[0]?.id ?? null;
  }
  renderSections();
  renderList();
  const diagram = currentDiagram();
  if (diagram) renderDiagram(diagram);
}

async function init() {
  const module = await import('./diagram-data.js');
  state.diagrams = module.diagrams;
  state.filtered = state.diagrams;
  state.activeId = state.diagrams[0]?.id ?? null;
  renderSections();
  renderList();
  if (state.activeId) renderDiagram(currentDiagram());

  el('search').addEventListener('input', applyFilters);
  el('copy-current').addEventListener('click', async () => {
    const diagram = currentDiagram();
    if (diagram) await copy(window.location.origin + window.location.pathname + `?diagram=${diagram.id}`);
  });
  el('copy-markdown').addEventListener('click', async () => {
    const diagram = currentDiagram();
    if (diagram) await copy(`[[docs/diagrams/${diagram.path}]]`);
  });
  el('copy-path').addEventListener('click', async () => {
    const diagram = currentDiagram();
    if (diagram) await copy(`docs/diagrams/${diagram.path}`);
  });
}

init();
