/* Recomp Tracker v2: accessible, conflict-aware personal tracking UI. */
(() => {
  'use strict';

  const KEY = {
    health: 'health-log', workouts: 'workout-log', routines: 'workout-routines',
    library: 'exercise-library', settings: 'tracker-settings', reviews: 'monthly-reviews',
    reminders: 'reminder-settings', active: 'active-workout', preImport: 'pre-import-snapshot',
    diet: 'daily-diet-log', foods: 'food-library', dietSettings: 'diet-settings', mealTemplates: 'meal-templates'
  };
  const VERSIONS = {};
  const state = { health: { entries: {} }, workouts: { sessions: [] }, routines: { items: [] },
    library: { items: [] }, settings: { goalWeight: null, weeklyRate: 0.4 }, reviews: { items: {} },
    reminders: { enabled: {}, times: {} }, reminderCatalog: [], diet: { days: {} }, foods: { items: [] },
    dietSettings: { constants: [], targets: { calories: 2010, protein: 180, carbs: 0, fat: 0 } }, mealTemplates: { items: [] }, active: null, selectedRoutine: null, undo: null };
  const HABITS = [
    ['training', 'Resistance training / calisthenics'], ['proteinBreakfast', 'Protein-forward breakfast'],
    ['postMealWalk', 'Post-meal walk after biggest carb meal'], ['dimLight', 'Dim light / no screens before bed'],
    ['morningLight', 'Morning light exposure']
  ];
  const DEFAULT_EXERCISES = [
    ['Weighted pull-up', 'Drive elbows down and back; start from an active hang and keep your ribs controlled.'],
    ['Weighted dip', 'Keep shoulders depressed; use a pain-free depth and avoid bouncing at the bottom.'],
    ['Weighted / leverage push-up', 'Keep a rigid trunk and let chest and hips rise together.'],
    ['Row', 'Brace first, pull the elbow toward the hip, then control the return.'],
    ['Back squat', 'Brace before descent, keep pressure over mid-foot, and use a repeatable depth.'],
    ['Romanian deadlift', 'Hinge at the hips with a soft knee; keep the load close and spine neutral.'],
    ['Overhead press', 'Squeeze glutes, keep ribs down, and move your head through once the bar clears.'],
    ['Isometric hold (wall squat / dip bottom)', 'Breathe steadily. Use a consistent joint angle and stop for sharp pain.'],
    ['Pull-up back-off (bodyweight/light)', 'Use full controlled range; leave a rep or two in reserve when form degrades.'],
    ['Dip back-off (bodyweight/light)', 'Keep shoulders controlled and use the same safe depth for every rep.'],
    ['Bicep curl', 'Keep upper arms still; avoid swinging your torso to finish a rep.'],
    ['Lateral raise', 'Lead with elbows, use a light load, and stop before traps take over.'],
    ['Tricep pushdown', 'Keep elbows fixed by your sides and fully control the return.'],
    ['Calf raise', 'Pause briefly at the stretched bottom and at the top rather than bouncing.'],
    ['Jump squat', 'Land quietly with knees tracking over toes; end the set before jump height drops.'],
    ['Lateral bound', 'Stick each landing briefly; maintain knee control before the next bound.'],
    ['Farmer\'s carry', 'Stand tall, keep ribs stacked over pelvis, and take deliberate even steps.']
  ].map(([name, tip]) => ({ id: slug(name), name, tip, target: targetFor(name) }));
  const DEFAULT_FOODS = [
    ['Chicken breast, cooked', 165, 31, 0, 3.6], ['Salmon, cooked', 208, 20, 0, 13], ['Lean beef, cooked', 217, 26, 0, 12],
    ['Egg, whole', 144, 12.6, 0.7, 9.6], ['Greek yogurt, 5%', 97, 9, 4, 5], ['Whey protein powder', 400, 77, 10, 7],
    ['Casein protein powder', 375, 80, 10, 3], ['Ground flaxseed', 534, 18, 29, 42], ['Olive oil', 884, 0, 0, 100],
    ['Rice, cooked', 130, 2.7, 28, 0.3], ['Potato, cooked', 87, 1.9, 20, 0.1], ['Couscous, cooked', 112, 3.8, 23, 0.2],
    ['Lentils, cooked', 116, 9, 20, 0.4], ['Chickpeas, cooked', 164, 8.9, 27, 2.6], ['Mixed vegetables', 65, 3, 10, 0.5],
    ['Banana', 89, 1.1, 23, 0.3], ['Bread, wholemeal', 247, 13, 41, 4.2], ['Fish oil', 900, 0, 0, 100]
  ].map(([name, calories, protein, carbs, fat]) => ({ id: slug(name), name, calories, protein, carbs, fat }));
  const DEFAULT_CONSTANTS = [
    ['Breakfast: 2 whole eggs', 144, 12.6, 0.7, 9.6], ['Breakfast: 200g Greek yogurt (5%)', 194, 18, 8, 10],
    ['Breakfast: 2 tbsp ground flax', 75, 2.6, 4, 6], ['Lunch: whey protein shake', 120, 23, 3, 2],
    ['Bedtime: 100g Greek yogurt', 97, 9, 4, 5], ['Bedtime: casein protein shake', 110, 24, 3, 1],
    ['Throughout day: olive oil (3 tbsp)', 360, 0, 0, 40], ['Fish oil', 18, 0, 0, 2],
    ['Creatine monohydrate (3–5g)', 0, 0, 0, 0], ['Resistant starch powder', 90, 0, 20, 0]
  ].map(([name, calories, protein, carbs, fat]) => ({ id: slug(name), name, calories, protein, carbs, fat }));

  const $ = (selector, root = document) => root.querySelector(selector);
  const el = (tag, props = {}, children = []) => {
    const node = document.createElement(tag);
    Object.entries(props).forEach(([key, value]) => {
      if (key === 'class') node.className = value;
      else if (key === 'text') node.textContent = value;
      else if (key === 'html') node.innerHTML = value;
      else if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
      else if (value !== undefined && value !== null) node.setAttribute(key, value);
    });
    children.flat().filter(Boolean).forEach(child => node.append(child));
    return node;
  };
function slug(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}
  const isoToday = () => new Date().toISOString().slice(0, 10);
  const monthKey = () => isoToday().slice(0, 7);
  const clone = value => JSON.parse(JSON.stringify(value));
  const byDate = (a, b) => String(a.date).localeCompare(String(b.date));
  const esc = value => String(value || '');
  function targetFor(name) {
    if (/isometric|carry/i.test(name)) return { min: 20, max: 40, unit: 'seconds' };
    if (/back-off|curl|raise|pushdown|calf/i.test(name)) return { min: 8, max: 15, unit: 'reps' };
    if (/jump|bound/i.test(name)) return { min: 5, max: 8, unit: 'reps' };
    return { min: 3, max: 6, unit: 'reps' };
  }

  async function read(key, fallback) {
    const response = await fetch('/api/kv/' + encodeURIComponent(key));
    if (response.status === 404) return clone(fallback);
    if (!response.ok) throw new Error('Could not load ' + key);
    const payload = await response.json();
    VERSIONS[key] = payload.version;
    return JSON.parse(payload.value);
  }
  async function write(key, value) {
    const response = await fetch('/api/kv/' + encodeURIComponent(key), {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: JSON.stringify(value), expectedVersion: VERSIONS[key] ?? null })
    });
    if (response.status === 409) {
      await loadAll(); render();
      throw new Error('This data changed on another device. Your view was refreshed; make the edit again.');
    }
    if (!response.ok) throw new Error('Save failed');
    VERSIONS[key] = (await response.json()).version;
  }
  async function save(part) { await write(KEY[part], state[part]); }
  async function loadAll() {
    const [health, workouts, routines, library, settings, reviews, reminders, active, reminderCatalog, diet, foods, dietSettings, mealTemplates] = await Promise.all([
      read(KEY.health, { entries: {} }), read(KEY.workouts, { sessions: [] }), read(KEY.routines, { items: [] }),
      read(KEY.library, { items: [] }), read(KEY.settings, { goalWeight: null, weeklyRate: 0.4 }),
      read(KEY.reviews, { items: {} }), read(KEY.reminders, { enabled: {}, times: {} }), read(KEY.active, null),
      fetch('/api/reminders').then(response => response.ok ? response.json() : { items: [] }).catch(() => ({ items: [] })),
      read(KEY.diet, { days: {} }), read(KEY.foods, { items: [] }),
      read(KEY.dietSettings, { constants: [], targets: { calories: 2010, protein: 180, carbs: 0, fat: 0 } }), read(KEY.mealTemplates, { items: [] })
    ]);
    state.health = health && health.entries ? health : { entries: {} };
    state.workouts = workouts && workouts.sessions ? workouts : { sessions: [] };
    state.routines = routines && routines.items ? routines : { items: [] };
    state.library = library && library.items ? library : { items: [] };
    state.settings = settings || { goalWeight: null, weeklyRate: 0.4 };
    state.reviews = reviews && reviews.items ? reviews : { items: {} };
    state.reminders = reminders || { enabled: {}, times: {} };
    state.reminderCatalog = Array.isArray(reminderCatalog?.items) ? reminderCatalog.items : [];
    state.diet = diet && diet.days ? diet : { days: {} };
    state.foods = foods && foods.items ? foods : { items: [] };
    state.dietSettings = dietSettings && dietSettings.targets ? dietSettings : { constants: [], targets: { calories: 2010, protein: 180, carbs: 0, fat: 0 } };
    state.mealTemplates = mealTemplates && mealTemplates.items ? mealTemplates : { items: [] };
    state.active = active || null;
    migrate();
  }
  function migrate() {
    let dietMigrated = false;
    if (!state.library.items.length) state.library.items = clone(DEFAULT_EXERCISES);
    state.library.items.forEach(item => { item.id ||= slug(item.name); item.target ||= targetFor(item.name); item.tip ||= 'Use a controlled, pain-free range of motion.'; item.archived ||= false; });
    if (!state.foods.items.length) state.foods.items = clone(DEFAULT_FOODS);
    state.foods.items.forEach(item => { item.id ||= slug(item.name); item.archived ||= false; });
    if (!state.dietSettings.constants.length) state.dietSettings.constants = clone(DEFAULT_CONSTANTS);
    if (!Array.isArray(state.dietSettings.sections) || !state.dietSettings.sections.length) state.dietSettings.sections = MEALS.map(([id, label]) => ({ id, label, archived: false }));
    state.dietSettings.constants.forEach(item => { item.id ||= slug(item.name); item.archived ||= false; });
    Object.values(state.diet.days).forEach(day => {
      if (!day.constantSnapshots) { day.constantSnapshots = {}; dietMigrated = true; }
      Object.values(day.meals || {}).forEach(rows => rows.forEach(entry => {
        const food = state.foods.items.find(item => item.id === entry.foodId) || foodByName(entry.name, true);
        if (food) { if (!entry.foodId || !entry.foodSnapshot) dietMigrated = true; entry.foodId ||= food.id; entry.foodSnapshot ||= snapshotFood(food); }
      }));
      Object.entries(day.constants || {}).forEach(([id, checked]) => {
        const constant = state.dietSettings.constants.find(item => item.id === id);
        if (checked && constant && !day.constantSnapshots[id]) { day.constantSnapshots[id] = snapshotFood(constant); dietMigrated = true; }
      });
    });
    state._migratedDiet = dietMigrated;
    Object.values(state.health.entries).forEach(entry => { entry.createdAt ||= entry.updatedAt || new Date().toISOString(); entry.updatedAt ||= entry.createdAt; });
    state.workouts.sessions.forEach(session => { session.id ||= session.date + '-' + Math.random().toString(36).slice(2); session.createdAt ||= new Date().toISOString(); session.updatedAt ||= session.createdAt; });
  }

  function styles() {
    if ($('#v2-style')) return;
    const css = `
      .v2-toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:14px 0}
      .v2-btn{min-height:38px;border:1px solid var(--line);border-radius:7px;background:#fff;color:var(--forest);padding:8px 12px;font:500 13px 'Work Sans',sans-serif;cursor:pointer}
      .v2-btn.primary{background:var(--forest);color:#fff;border-color:var(--forest)}.v2-btn.danger{color:var(--danger)}.v2-btn:disabled{opacity:.55;cursor:not-allowed}
      .v2-btn:focus-visible,#tab-routines input:focus-visible,#tab-workout input:focus-visible,#tab-review input:focus-visible,#tab-diet input:focus-visible,#tab-foods input:focus-visible,#tab-routines textarea:focus-visible,#tab-workout textarea:focus-visible,#tab-review textarea:focus-visible,#tab-diet textarea:focus-visible,#tab-foods textarea:focus-visible{outline:3px solid #9fc6af;outline-offset:2px}
      .v2-banner{background:#fff4d6;border:1px solid #e8c66b;border-radius:8px;padding:10px 12px;margin-bottom:12px;font-size:13px}
      .v2-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-bottom:14px}.v2-grid.one{grid-template-columns:1fr}
      .v2-row{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:12px 0;border-bottom:1px solid var(--line)}.v2-row:last-child{border-bottom:0}.v2-row .grow{flex:1;min-width:160px}.v2-meta{font-size:12px;color:var(--ink-faint)}.v2-actions{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.v2-list{display:flex;flex-direction:column}
      .v2-set{display:grid;grid-template-columns:28px 82px minmax(0,1fr) minmax(0,1fr) 72px 38px;gap:8px;align-items:center;margin:8px 0}.v2-set input,.v2-set select{min-width:0}
      .v2-exercise{border:1px solid var(--line);border-radius:8px;padding:14px;margin:12px 0;background:#fff}.v2-tip{font-size:12px;color:var(--ink-soft);margin:7px 0}.v2-timer{font:600 28px 'IBM Plex Mono',monospace;color:var(--forest);letter-spacing:-1px}.v2-tab[aria-selected=true]{color:var(--forest);border-bottom-color:var(--forest)}
      .v2-check{display:flex;gap:8px;align-items:center;font-size:13px;margin:0}.v2-check input{width:18px;height:18px}.v2-toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);z-index:20;background:#20352a;color:#fff;border-radius:8px;padding:10px 14px;font-size:13px;box-shadow:0 4px 18px #0003}.v2-toast button{margin-left:10px;border:0;background:transparent;color:#fff;text-decoration:underline;cursor:pointer}.v2-muted{color:var(--ink-faint);font-size:13px}.v2-summary{font-size:13px;background:var(--forest-dim);border-radius:7px;padding:9px}.v2-chip{border:1px solid var(--line);border-radius:14px;padding:4px 9px;font-size:12px;background:#fff}
      #tab-routines input:not([type=checkbox]),#tab-workout input:not([type=checkbox]),#tab-review input:not([type=checkbox]),#tab-diet input:not([type=checkbox]),#tab-foods input:not([type=checkbox]),#tab-routines textarea,#tab-workout textarea,#tab-review textarea,#tab-diet textarea,#tab-foods textarea,#tab-routines select,#tab-workout select,#tab-review select,#tab-diet select,#tab-foods select{width:100%;font-family:'IBM Plex Mono',monospace;font-size:14px;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:#fff;color:var(--ink)}
      #tab-routines textarea,#tab-workout textarea,#tab-review textarea,#tab-diet textarea,#tab-foods textarea{font-family:'Work Sans',sans-serif}.v2-routine-form{display:flex;flex-direction:column;gap:14px}.v2-field{display:flex;flex-direction:column;gap:5px}.v2-field label{margin:0}.v2-library{max-height:255px;overflow:auto;border:1px solid var(--line);border-radius:8px;padding:8px 10px;background:#fff}.v2-library label{display:flex;align-items:center;gap:8px;padding:8px 4px;margin:0;font-size:13px}.v2-custom-row{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}.v2-custom-row input{flex:1;min-width:200px}.v2-session-head{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.v2-progress{font-size:12px;color:var(--ink-soft)}.v2-reminder-copy{display:flex;flex-direction:column;gap:2px}.v2-data-actions{align-items:center}.v2-food-filter{margin-bottom:4px}.v2-food-filter input,.v2-food-filter select{width:auto!important;flex:1;min-width:180px}
      .v2-macro-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.v2-macro{background:#fff;border:1px solid var(--line);border-radius:8px;padding:9px 10px}.v2-macro strong{display:block;font:500 17px 'IBM Plex Mono',monospace}.v2-macro span{display:block;font-size:10px;color:var(--ink-faint);text-transform:uppercase;letter-spacing:.04em}.v2-diet-section{margin-top:16px}.v2-diet-section h3{font-family:'Fraunces',serif;font-size:16px;font-weight:500;margin:0 0 4px}.v2-diet-row{display:grid;grid-template-columns:26px minmax(0,1fr) 76px 70px;gap:8px;align-items:center;padding:9px 0;border-bottom:1px solid var(--line)}.v2-diet-row:last-child{border-bottom:0}.v2-diet-row input[type=checkbox]{width:18px;height:18px}.v2-diet-macros{grid-column:2 / -1;min-width:0;font:12px/1.45 'IBM Plex Mono',monospace;color:var(--ink-soft);overflow-wrap:anywhere}.v2-constant-row{grid-template-columns:26px minmax(0,1fr) auto}.v2-diet-actions{display:flex;gap:6px;justify-content:flex-end;flex-wrap:wrap}.v2-btn.compact{min-height:30px;padding:5px 8px;font-size:12px}.v2-diet-note{font-size:12px;color:var(--ink-faint);margin:0 0 10px}.v2-diet-history{margin-top:14px}.v2-library-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)}.v2-library-row:last-child{border-bottom:0}
      @media(max-width:560px){.v2-grid{grid-template-columns:1fr}.v2-set{grid-template-columns:28px 72px minmax(0,1fr) minmax(0,1fr) 58px 34px;gap:5px;font-size:12px}.v2-set select{padding-left:4px;padding-right:2px}.v2-btn{min-height:42px}.v2-timer{font-size:24px}.v2-row .grow{min-width:0}.v2-actions{width:100%}.v2-actions .v2-btn{flex:1}.v2-custom-row{align-items:stretch}.v2-custom-row input{min-width:0;flex-basis:100%}.v2-macro-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.v2-diet-row{grid-template-columns:24px minmax(0,1fr) 68px 62px;gap:6px}.v2-constant-row{grid-template-columns:24px minmax(0,1fr)}.v2-constant-row .v2-diet-actions{grid-column:2 / -1;justify-content:flex-start}.v2-library-row{grid-template-columns:1fr}.v2-library-row .v2-actions{width:auto}}
    `;
    document.head.append(el('style', { id: 'v2-style', text: css }));
  }
  function toast(message, undo) {
    $('.v2-toast')?.remove();
    const box = el('div', { class: 'v2-toast', role: 'status', 'aria-live': 'polite', text: message });
    if (undo) box.append(el('button', { text: 'Undo', onclick: undo }));
    document.body.append(box); setTimeout(() => box.remove(), 10000);
  }
  function clear(node) { node.replaceChildren(); return node; }
  function button(text, fn, className = '') { return el('button', { type: 'button', class: 'v2-btn ' + className, text, onclick: fn }); }
  function input(label, type, value, onChange, props = {}) {
    const field = el('div'); const id = 'v2-' + Math.random().toString(36).slice(2);
    field.append(el('label', { for: id, text: label }));
    const control = el('input', { id, type, ...props }); control.value = value ?? ''; control.addEventListener('change', () => onChange(control.value)); field.append(control); return field;
  }

  function buildShell() {
    styles();
    const nav = $('nav'); clear(nav); nav.setAttribute('role', 'tablist');
    [['today', 'Today'], ['diet', 'Diet'], ['foods', 'Food library'], ['habits', 'Habits & Trends'], ['records', 'Records'], ['routines', 'Routines'], ['workout', 'Workout'], ['review', 'Review'], ['guide', 'Guide']].forEach(([id, label], index) => {
      const tab = el('button', { class: 'v2-tab' + (index === 0 ? ' active' : ''), role: 'tab', 'aria-selected': index === 0 ? 'true' : 'false', 'data-tab': id, text: label,
        onclick: () => selectTab(id) }); nav.append(tab);
    });
    ['today', 'trends', 'habits', 'guide', 'workouts'].forEach(id => {
      const section = $('#tab-' + id);
      if (!section) return;
      section.style.removeProperty('display');
      section.hidden = id !== 'today';
    });
    const dietPanel = el('div', { id: 'tab-diet', role: 'tabpanel', hidden: 'true' });
    const foodsPanel = el('div', { id: 'tab-foods', role: 'tabpanel', hidden: 'true' });
    const routinePanel = el('div', { id: 'tab-routines', role: 'tabpanel', hidden: 'true' });
    const workoutPanel = el('div', { id: 'tab-workout', role: 'tabpanel', hidden: 'true' });
    const recordsPanel = el('div', { id: 'tab-records', role: 'tabpanel', hidden: 'true' });
    const reviewPanel = el('div', { id: 'tab-review', role: 'tabpanel', hidden: 'true' });
    $('#tab-workouts').after(dietPanel, foodsPanel, routinePanel, workoutPanel, recordsPanel, reviewPanel);
    $('#tab-workouts').hidden = true;
    syncLegacyHealth();
    $('#summary-cards').hidden = true; $('#photo-reminder').hidden = true;
  }
  function selectTab(id) {
    ['today', 'diet', 'foods', 'trends', 'habits', 'records', 'routines', 'workout', 'review', 'guide', 'workouts'].forEach(name => { const panel = $('#tab-' + name); if (panel) panel.hidden = name !== id; });
    $('nav').querySelectorAll('button').forEach(btn => { const selected = btn.dataset.tab === id; btn.classList.toggle('active', selected); btn.setAttribute('aria-selected', String(selected)); });
    if (id === 'workout') renderWorkout();
    if (id === 'diet') renderDiet();
    if (id === 'foods') renderFoods();
    if (id === 'habits') renderHabits();
    if (id === 'records') renderRecords();
  }
  function syncLegacyHealth() {
    if (typeof DATA !== 'undefined') DATA = state.health;
  }
  function render() { renderToday(); renderDiet(); renderFoods(); renderHabits(); renderRoutines(); renderWorkout(); renderRecords(); renderReview(); }

  function renderToday() {
    const panel = clear($('#tab-today')); const entries = state.health.entries; const currentDate = panel.dataset.editDate || isoToday(); const current = entries[currentDate] || {};
    const snapshot = todaySnapshotCard(currentDate); if (snapshot) panel.append(snapshot);
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: currentDate in entries ? 'Edit daily entry' : 'Log daily entry' }));
    const form = el('form'); form.addEventListener('submit', async event => {
      event.preventDefault(); const fd = new FormData(form); const date = fd.get('date'); const old = entries[date] || {};
      const entry = { ...old, weight: numberOrNull(fd.get('weight')), waist: numberOrNull(fd.get('waist')), sleepHours: numberOrNull(fd.get('sleep')), bedtime: fd.get('bedtime') || null, notes: fd.get('notes') || '', energy: numberOrNull(fd.get('energy')), hunger: numberOrNull(fd.get('hunger')), soreness: numberOrNull(fd.get('soreness')), sleepQuality: numberOrNull(fd.get('sleepQuality')), createdAt: old.createdAt || new Date().toISOString(), updatedAt: new Date().toISOString() };
      HABITS.forEach(([key]) => { entry[key] = fd.get(key) === 'on'; }); state.health.entries[date] = entry;
      try { await save('health'); panel.dataset.editDate = date; render(); toast('Daily entry saved.'); } catch (error) { toast(error.message); }
    });
    const grid = el('div', { class: 'v2-grid' });
    grid.append(input('Date', 'date', currentDate, value => { panel.dataset.editDate = value; renderToday(); }, { name: 'date' }), input('Weight (kg)', 'number', current.weight, () => {}, { name: 'weight', step: '0.1', min: '20', max: '400' }), input('Waist (cm)', 'number', current.waist, () => {}, { name: 'waist', step: '0.1', min: '20', max: '250' }), input('Sleep (hours)', 'number', current.sleepHours, () => {}, { name: 'sleep', step: '0.25', min: '0', max: '24' }), input('Bedtime', 'time', current.bedtime, () => {}, { name: 'bedtime' }));
    form.append(grid, el('label', { text: 'Notes (symptoms, cravings, energy)' })); const notes = el('textarea', { name: 'notes', rows: '3' }); notes.value = current.notes || ''; form.append(notes);
    form.append(el('h2', { text: 'Readiness' })); const readiness = el('div', { class: 'v2-grid' }); [['Energy', 'energy'], ['Hunger', 'hunger'], ['Soreness', 'soreness'], ['Sleep quality', 'sleepQuality']].forEach(([label, key]) => readiness.append(input(label + ' (1–5)', 'number', current[key], () => {}, { name: key, min: '1', max: '5', step: '1' }))); form.append(readiness, el('h2', { text: 'Habits' }));
    HABITS.forEach(([key, label]) => { const check = el('input', { type: 'checkbox', name: key }); check.checked = current[key] === true; form.append(el('label', { class: 'v2-check' }, [check, document.createTextNode(label)])); });
    form.append(button('Save entry', null, 'primary')); form.querySelector('button').type = 'submit'; card.append(form); panel.append(card, dailyHistory());
  }
  const numberOrNull = value => value === '' || value === null ? null : Number(value);
  function todaySnapshotCard(date) {
    if (date !== isoToday()) return null;
    const day = state.diet.days[date]; const total = day ? dietTotals(day) : null; const sessions = state.workouts.sessions.filter(session => session.date === date).length;
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Today at a glance' }));
    const grid = el('div', { class: 'v2-macro-grid' });
    [['Diet', total ? `${Math.round(total.total.calories)} kcal` : 'Not logged', total ? `${Math.round(total.total.protein)}g protein` : 'Open Diet'], ['Training', sessions ? `${sessions} saved` : state.active ? 'In progress' : 'Not logged', sessions ? 'Completed session' : 'Open Workout'], ['Habits', Object.values(state.health.entries[date] || {}).filter(value => value === true).length + '/' + HABITS.length, 'Daily habits'], ['Review', state.settings.goalWeight ? `${state.settings.goalWeight} kg goal` : 'Set a goal', 'Open Review']].forEach(([label, value, note]) => grid.append(el('div', { class: 'v2-macro' }, [el('span', { text: label }), el('strong', { text: value }), el('span', { text: note })])));
    return card;
  }
  function dailyHistory() {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Daily history' })); const list = el('div', { class: 'v2-list' });
    Object.entries(state.health.entries).sort((a, b) => b[0].localeCompare(a[0])).slice(0, 60).forEach(([date, entry]) => {
      const summary = [entry.weight && entry.weight + ' kg', entry.waist && entry.waist + ' cm', entry.sleepHours && entry.sleepHours + ' h sleep'].filter(Boolean).join(' · ') || 'Habits / notes only';
      list.append(el('div', { class: 'v2-row' }, [el('div', { class: 'grow' }, [el('strong', { text: date }), el('div', { class: 'v2-meta', text: summary })]), el('div', { class: 'v2-actions' }, [button('Edit', () => { $('#tab-today').dataset.editDate = date; renderToday(); window.scrollTo({ top: 0, behavior: 'smooth' }); }), button('Delete', () => deleteDaily(date), 'danger')])]));
    });
    card.append(list); return card;
  }
  async function deleteDaily(date) {
    if (!confirm('Delete the entry for ' + date + '? You can undo for 10 seconds.')) return;
    const removed = state.health.entries[date]; delete state.health.entries[date];
    try { await save('health'); render(); toast('Entry deleted.', async () => { state.health.entries[date] = removed; await save('health'); render(); toast('Entry restored.'); }); } catch (error) { state.health.entries[date] = removed; toast(error.message); }
  }

  const MEALS = [['breakfast', 'Breakfast'], ['lunch', 'Lunch'], ['dinner', 'Dinner'], ['snacks', 'Snacks / extras']];
  function mealSections() { return (state.dietSettings.sections || MEALS.map(([id, label]) => ({ id, label, archived: false }))).filter(section => !section.archived); }
  const emptyFoodRows = () => Array.from({ length: 3 }, () => ({ name: '', grams: '', checked: false }));
  const zeroMacros = () => ({ calories: 0, protein: 0, carbs: 0, fat: 0 });
  const addMacros = (total, item) => ['calories', 'protein', 'carbs', 'fat'].forEach(key => total[key] += Number(item[key]) || 0);
  const displayMacros = macros => `${Math.round(macros.calories)} kcal · P ${macros.protein.toFixed(1)}g · C ${macros.carbs.toFixed(1)}g · F ${macros.fat.toFixed(1)}g`;
  function dietDay(date) {
    if (!state.diet.days[date]) state.diet.days[date] = { constants: {}, meals: Object.fromEntries(mealSections().map(section => [section.id, emptyFoodRows()])), createdAt: new Date().toISOString(), updatedAt: null };
    const day = state.diet.days[date];
    day.constants ||= {}; day.meals ||= {};
    mealSections().forEach(section => { const id = section.id; day.meals[id] ||= emptyFoodRows(); while (day.meals[id].length < 3) day.meals[id].push({ name: '', grams: '', checked: false }); });
    return day;
  }
  function snapshotFood(food) { return { id: food.id, name: food.name, calories: Number(food.calories) || 0, protein: Number(food.protein) || 0, carbs: Number(food.carbs) || 0, fat: Number(food.fat) || 0 }; }
  function foodByName(name, includeArchived = false) { return state.foods.items.find(food => (includeArchived || !food.archived) && food.name.toLowerCase() === String(name || '').trim().toLowerCase()); }
  function foodForEntry(entry) { return entry.foodSnapshot || state.foods.items.find(food => food.id === entry.foodId) || foodByName(entry.name, true); }
  function captureDietSnapshots(day) {
    day.constantSnapshots ||= {};
    state.dietSettings.constants.forEach(constant => { if (day.constants[constant.id]) day.constantSnapshots[constant.id] ||= snapshotFood(constant); });
    Object.values(day.meals || {}).forEach(rows => rows.forEach(entry => {
      const food = state.foods.items.find(item => item.id === entry.foodId) || foodByName(entry.name, true);
      if (food) { entry.foodId = food.id; entry.foodSnapshot = snapshotFood(food); entry.name = food.name; }
    }));
  }
  function scaledMacros(food, grams) {
    const scale = Math.max(0, Number(grams) || 0) / 100;
    return { calories: (Number(food?.calories) || 0) * scale, protein: (Number(food?.protein) || 0) * scale, carbs: (Number(food?.carbs) || 0) * scale, fat: (Number(food?.fat) || 0) * scale };
  }
  function dietTotals(day) {
    const total = zeroMacros(); let completed = 0; let trackable = 0;
    const activeConstantIds = new Set();
    state.dietSettings.constants.filter(constant => !constant.archived).forEach(constant => { activeConstantIds.add(constant.id); trackable++; if (day.constants[constant.id]) { completed++; addMacros(total, day.constantSnapshots?.[constant.id] || constant); } });
    Object.entries(day.constants || {}).forEach(([id, checked]) => {
      if (!checked || activeConstantIds.has(id) || !day.constantSnapshots?.[id]) return;
      trackable++; completed++; addMacros(total, day.constantSnapshots[id]);
    });
    Object.values(day.meals || {}).forEach(rows => rows.forEach(entry => {
      if (!entry.name || !entry.grams) return;
      trackable++;
      if (entry.checked) { completed++; addMacros(total, scaledMacros(foodForEntry(entry), entry.grams)); }
    }));
    return { total, completed, trackable };
  }
  function renderDietSummary(container, day) {
    const { total, completed, trackable } = dietTotals(day); const targets = state.dietSettings.targets;
    clear(container);
    const grid = el('div', { class: 'v2-macro-grid' });
    [['Calories', total.calories, targets.calories, 'kcal'], ['Protein', total.protein, targets.protein, 'g'], ['Carbs', total.carbs, targets.carbs, 'g'], ['Fat', total.fat, targets.fat, 'g']].forEach(([label, value, target, unit]) => {
      const suffix = target ? ` / ${Number(target).toFixed(label === 'Calories' ? 0 : 0)}${unit}` : '';
      grid.append(el('div', { class: 'v2-macro' }, [el('span', { text: label }), el('strong', { text: `${Math.round(value)}${unit}${suffix}` })]));
    });
    container.append(grid, el('p', { class: 'v2-diet-note', text: `${completed}/${trackable} entered items are ticked and included in today’s totals.` }));
  }
  function renderDiet() {
    const panel = clear($('#tab-diet')); const date = panel.dataset.dietDate || isoToday(); const day = dietDay(date);
    const titleCard = el('div', { class: 'card' }); titleCard.append(el('h2', { text: 'Daily diet' }), el('p', { class: 'v2-muted', text: 'Tick constants and foods when taken/eaten. Totals include ticked entries only; food values are per 100g, so check brand labels.' }));
    const dateInput = el('input', { type: 'date', 'aria-label': 'Diet date' }); dateInput.value = date; dateInput.addEventListener('change', () => { panel.dataset.dietDate = dateInput.value; renderDiet(); });
    const copyYesterday = button('Copy previous diet', () => {
      const previous = Object.keys(state.diet.days).filter(item => item < date).sort().at(-1);
      if (!previous) return toast('No earlier diet entry to copy.');
      state.diet.days[date] = { ...clone(state.diet.days[previous]), createdAt: day.createdAt, updatedAt: null };
      renderDiet(); toast('Previous diet copied. Review it, then save.');
    });
    titleCard.append(el('div', { class: 'v2-toolbar' }, [dateInput, copyYesterday]));
    const summary = el('div'); renderDietSummary(summary, day); titleCard.append(summary); panel.append(titleCard);
    const optionList = el('datalist', { id: 'diet-food-options' }); state.foods.items.filter(food => !food.archived).slice().sort((a, b) => a.name.localeCompare(b.name)).forEach(food => optionList.append(el('option', { value: food.name }))); panel.append(optionList);
    const constantsCard = el('div', { class: 'card v2-constants-card' }); constantsCard.append(el('h2', { text: 'Daily constants' }));
    state.dietSettings.constants.filter(constant => !constant.archived).forEach(constant => {
      const checked = el('input', { type: 'checkbox', 'aria-label': 'Mark ' + constant.name + ' taken' }); checked.checked = !!day.constants[constant.id];
      checked.addEventListener('change', () => { day.constants[constant.id] = checked.checked; if (checked.checked) { day.constantSnapshots ||= {}; day.constantSnapshots[constant.id] = snapshotFood(constant); } renderDietSummary(summary, day); });
      const actions = el('div', { class: 'v2-diet-actions' }, [
        button('Edit', () => { state.editConstant = constant.id; renderDiet(); }, 'compact'),
        button('Delete', async () => {
          if (!confirm(`Archive “${constant.name}” from the daily checklist? Existing diet days will remain intact.`)) return;
          constant.archived = true;
          try { await save('dietSettings'); renderDiet(); toast('Daily constant archived.'); } catch (error) { constant.archived = false; toast(error.message); }
        }, 'compact danger')
      ]);
      constantsCard.append(el('div', { class: 'v2-diet-row v2-constant-row' }, [checked, el('div', {}, [el('strong', { text: constant.name })]), actions, el('span', { class: 'v2-diet-macros', text: displayMacros(constant) })]));
    });
    panel.append(constantsCard);
    mealSections().forEach(section => panel.append(dietMealCard(section.id, section.label, day, summary)));
    panel.append(dietTargetsCard(), mealSectionsCard(), addConstantCard(), savedMealsCard(day, summary));
    const actions = el('div', { class: 'card' });
    actions.append(el('h2', { text: 'Record this diet' }), el('p', { class: 'v2-muted', text: 'Save the selected date when you have checked what you actually ate/took.' }), button('Save daily diet', async () => { captureDietSnapshots(day); day.updatedAt = new Date().toISOString(); try { await save('diet'); renderDiet(); toast('Daily diet saved.'); } catch (error) { toast(error.message); } }, 'primary'));
    panel.append(actions);
  }
  function dietMealCard(id, label, day, summary) {
    const card = el('div', { class: 'card v2-diet-section' }); card.append(el('h3', { text: label }), el('p', { class: 'v2-diet-note', text: 'Choose a saved food and enter its edible/cooked weight in grams.' }));
    const rows = el('div'); const refresh = () => renderDietSummary(summary, day);
    const renderRows = () => {
      clear(rows);
      day.meals[id].forEach((entry, index) => {
        const checked = el('input', { type: 'checkbox', 'aria-label': `Include ${label} item ${index + 1}` }); checked.checked = !!entry.checked;
        const food = el('input', { type: 'text', list: 'diet-food-options', placeholder: 'Food' }); food.value = entry.name || '';
        const grams = el('input', { type: 'number', min: '0', step: '1', placeholder: 'grams', 'aria-label': `${label} item ${index + 1} grams` }); grams.value = entry.grams || '';
        const macros = el('span', { class: 'v2-diet-macros' });
        const update = () => { entry.checked = checked.checked; entry.name = food.value; entry.grams = grams.value; const found = foodByName(entry.name); if (found) { entry.foodId = found.id; entry.foodSnapshot = snapshotFood(found); } else if (entry.name !== (entry.foodSnapshot?.name || '')) { entry.foodId = null; entry.foodSnapshot = null; } const source = foodForEntry(entry); macros.textContent = source ? displayMacros(scaledMacros(source, entry.grams)) : (entry.name ? 'Add this food to the library before saving' : ''); refresh(); };
        checked.addEventListener('change', update); food.addEventListener('change', update); grams.addEventListener('input', update); update();
        const remove = button('Remove', () => { day.meals[id].splice(index, 1); renderRows(); refresh(); }, 'compact danger');
        rows.append(el('div', { class: 'v2-diet-row' }, [checked, food, grams, remove, macros]));
      });
    };
    renderRows();
    card.append(rows, button('+ Add food row', () => { day.meals[id].push({ name: '', grams: '', checked: false }); renderRows(); }, ''));
    return card;
  }
  function dietTargetsCard() {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Daily macro targets' }), el('p', { class: 'v2-diet-note', text: 'Calories default to the existing meal-plan example; protein defaults to the plan’s 170–195g range. Set optional carb/fat targets if you use them.' }));
    const form = el('form'); const grid = el('div', { class: 'v2-grid' });
    [['Calories', 'calories', 'kcal'], ['Protein', 'protein', 'g'], ['Carbs', 'carbs', 'g'], ['Fat', 'fat', 'g']].forEach(([label, key, unit]) => grid.append(input(`${label} (${unit})`, 'number', state.dietSettings.targets[key], () => {}, { name: key, min: '0', step: '1' })));
    const submit = button('Save targets', null, 'primary'); submit.type = 'submit'; form.append(grid, submit); form.addEventListener('submit', async event => { event.preventDefault(); const data = new FormData(form); ['calories', 'protein', 'carbs', 'fat'].forEach(key => state.dietSettings.targets[key] = numberOrNull(data.get(key)) || 0); try { await save('dietSettings'); renderDiet(); toast('Diet targets saved.'); } catch (error) { toast(error.message); } }); card.append(form); return card;
  }
  function mealSectionsCard() {
    const editing = state.dietSettings.sections.find(section => section.id === state.editMealSection); const card = el('div', { class: 'card' }); card.append(el('h2', { text: editing ? 'Edit meal section' : 'Meal sections' }), el('p', { class: 'v2-diet-note', text: 'Add, rename, archive, or restore diary sections. Archived sections remain part of historical totals.' }));
    const form = el('form'); const label = el('input', { type: 'text', required: 'true', 'aria-label': 'Section name', placeholder: 'e.g. Pre-workout or Supper' }); label.value = editing?.label || ''; const submit = button(editing ? 'Save section' : 'Add section', null, 'primary'); submit.type = 'submit'; form.append(el('div', { class: 'v2-field' }, [el('label', { text: 'Section name' }), label]), el('div', { class: 'v2-toolbar' }, [submit, editing ? button('Cancel', () => { state.editMealSection = null; renderDiet(); }) : null]));
    form.addEventListener('submit', async event => { event.preventDefault(); const value = label.value.trim(); if (!value) return; if (state.dietSettings.sections.some(section => section.id !== editing?.id && section.label.toLowerCase() === value.toLowerCase())) return toast('A meal section already uses that name.'); if (editing) editing.label = value; else state.dietSettings.sections.push({ id: 'section-' + Date.now(), label: value, archived: false }); try { await save('dietSettings'); state.editMealSection = null; renderDiet(); toast(editing ? 'Meal section updated.' : 'Meal section added.'); } catch (error) { toast(error.message); } });
    const list = el('div', { class: 'v2-list' }); state.dietSettings.sections.forEach(section => list.append(el('div', { class: 'v2-library-row' }, [el('div', {}, [el('strong', { text: section.label }), el('div', { class: 'v2-meta', text: section.archived ? 'Archived — hidden from new diary days' : 'Active' })]), el('div', { class: 'v2-actions' }, [button('Edit', () => { state.editMealSection = section.id; renderDiet(); }, 'compact'), button(section.archived ? 'Restore' : 'Archive', async () => { section.archived = !section.archived; try { await save('dietSettings'); renderDiet(); toast(section.archived ? 'Meal section archived.' : 'Meal section restored.'); } catch (error) { section.archived = !section.archived; toast(error.message); } }, 'compact' + (section.archived ? '' : ' danger'))])])));
    card.append(form, list); return card;
  }
  function addConstantCard() {
    const editing = state.dietSettings.constants.find(item => item.id === state.editConstant);
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: editing ? 'Edit daily constant' : 'Add daily constant' }), el('p', { class: 'v2-diet-note', text: 'Use the nutrition label for the usual daily amount — this becomes a tickable item each day.' }));
    const form = el('form'); const name = el('input', { type: 'text', required: 'true', placeholder: 'e.g. Vitamin D' }); name.value = editing?.name || '';
    const grid = el('div', { class: 'v2-grid' }); [['Calories', 'calories'], ['Protein', 'protein'], ['Carbs', 'carbs'], ['Fat', 'fat']].forEach(([label, key]) => grid.append(input(label + ' per daily amount', 'number', editing?.[key] ?? 0, () => {}, { name: key, min: '0', step: '0.1' })));
    const submit = button(editing ? 'Save constant' : 'Add constant', null, 'primary'); submit.type = 'submit';
    const cancel = editing ? button('Cancel', () => { state.editConstant = null; renderDiet(); }) : null;
    form.append(el('div', { class: 'v2-field' }, [el('label', { text: 'Name' }), name]), grid, el('div', { class: 'v2-toolbar' }, [submit, cancel]));
    form.addEventListener('submit', async event => {
      event.preventDefault(); const data = new FormData(form); const constantName = name.value.trim(); if (!constantName) return;
      const next = { id: editing?.id || slug(constantName) + '-' + Date.now(), name: constantName, calories: numberOrNull(data.get('calories')) || 0, protein: numberOrNull(data.get('protein')) || 0, carbs: numberOrNull(data.get('carbs')) || 0, fat: numberOrNull(data.get('fat')) || 0 };
      if (editing) state.dietSettings.constants[state.dietSettings.constants.findIndex(item => item.id === editing.id)] = next; else state.dietSettings.constants.push(next);
      try { await save('dietSettings'); state.editConstant = null; renderDiet(); toast(editing ? 'Daily constant updated.' : 'Daily constant added.'); } catch (error) { toast(error.message); }
    });
    card.append(form); return card;
  }
  function addFoodCard() {
    const editing = state.foods.items.find(item => item.id === state.editFood);
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: editing ? 'Edit food' : 'Add food to library' }), el('p', { class: 'v2-diet-note', text: 'Enter nutrition per 100g from the package or recipe. Historical meals retain the value used when they were saved.' }));
    const form = el('form'); const name = el('input', { type: 'text', required: 'true', 'aria-label': 'Food name', placeholder: 'e.g. Your protein bar' }); name.value = editing?.name || '';
    const grid = el('div', { class: 'v2-grid' }); [['Calories', 'calories'], ['Protein', 'protein'], ['Carbs', 'carbs'], ['Fat', 'fat']].forEach(([label, key]) => grid.append(input(label + ' per 100g', 'number', editing?.[key] ?? 0, () => {}, { name: key, min: '0', step: '0.1' })));
    const submit = button(editing ? 'Save food' : 'Add food', null, 'primary'); submit.type = 'submit'; const cancel = editing ? button('Cancel', () => { state.editFood = null; renderFoods(); }) : null;
    form.append(el('div', { class: 'v2-field' }, [el('label', { text: 'Food name' }), name]), grid, el('div', { class: 'v2-toolbar' }, [submit, cancel])); form.addEventListener('submit', async event => { event.preventDefault(); const data = new FormData(form); const foodName = name.value.trim(); const duplicate = state.foods.items.find(item => item.id !== editing?.id && item.name.toLowerCase() === foodName.toLowerCase()); if (!foodName || duplicate) return toast(foodName ? 'That food name is already in the library.' : 'Enter a food name.'); const next = { id: editing?.id || slug(foodName) + '-' + Date.now(), name: foodName, calories: numberOrNull(data.get('calories')) || 0, protein: numberOrNull(data.get('protein')) || 0, carbs: numberOrNull(data.get('carbs')) || 0, fat: numberOrNull(data.get('fat')) || 0, archived: false }; if (editing) state.foods.items[state.foods.items.findIndex(item => item.id === editing.id)] = next; else state.foods.items.push(next); try { await save('foods'); state.editFood = null; renderFoods(); toast(editing ? 'Food updated.' : 'Food added to the library.'); } catch (error) { toast(error.message); } }); card.append(form); return card;
  }
  function foodLibraryCard() {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Food library' }), el('p', { class: 'v2-diet-note', text: 'Edit, archive, or reuse foods. Archive removes a food from new entries without altering recorded days.' }));
    const list = el('div', { class: 'v2-list' }); const items = state.foods.items.filter(item => !item.archived).slice().sort((a, b) => a.name.localeCompare(b.name));
    items.forEach(item => list.append(el('div', { class: 'v2-library-row' }, [el('div', {}, [el('strong', { text: item.name }), el('div', { class: 'v2-meta', text: displayMacros(item) + ' per 100g' })]), el('div', { class: 'v2-actions' }, [button('Edit', () => { state.editFood = item.id; renderDiet(); }, 'compact'), button('Archive', async () => { if (!confirm(`Archive “${item.name}”? It will remain in historical entries.`)) return; item.archived = true; try { await save('foods'); renderDiet(); toast('Food archived.'); } catch (error) { item.archived = false; toast(error.message); } }, 'compact danger')])])));
    card.append(items.length ? list : el('p', { class: 'v2-muted', text: 'No active foods in the library.' })); return card;
  }
  function foodManagementCard() {
    const card = el('div', { class: 'card' });
    card.append(el('h2', { text: 'All active foods' }), el('p', { class: 'v2-diet-note', text: 'Each value is per 100g. Archive removes a food from new diary entries without changing saved days.' }));
    const list = el('div', { class: 'v2-list' });
    const items = state.foods.items.filter(item => !item.archived).slice().sort((a, b) => a.name.localeCompare(b.name));
    const search = el('input', { type: 'search', placeholder: 'Search foods', 'aria-label': 'Search foods' }); search.value = state.foodSearch || '';
    const category = el('select', { 'aria-label': 'Filter foods by category' });
    const categories = [...new Set(items.map(item => item.category || 'Personal'))].sort();
    category.append(el('option', { value: '', text: 'All categories' })); categories.forEach(value => category.append(el('option', { value, text: value })));
    category.value = state.foodCategory || '';
    const resultCount = el('p', { class: 'v2-diet-note' });
    const redraw = () => {
      state.foodSearch = search.value; state.foodCategory = category.value; clear(list);
      const query = search.value.trim().toLowerCase();
      const visible = items.filter(item => (!query || item.name.toLowerCase().includes(query)) && (!category.value || (item.category || 'Personal') === category.value));
      resultCount.textContent = `${visible.length} of ${items.length} foods shown.`;
      visible.forEach(item => {
        const archive = async () => {
          if (!confirm('Archive "' + item.name + '"? It will remain in historical entries.')) return;
          item.archived = true;
          try { await save('foods'); renderFoods(); toast('Food archived.'); }
          catch (error) { item.archived = false; toast(error.message); }
        };
        const source = item.category ? item.category + (item.source ? ' · ' + item.source : '') : 'Personal food';
        list.append(el('div', { class: 'v2-library-row' }, [
          el('div', {}, [el('strong', { text: item.name }), el('div', { class: 'v2-meta', text: displayMacros(item) + ' per 100g · ' + source })]),
          el('div', { class: 'v2-actions' }, [button('Edit', () => { state.editFood = item.id; renderFoods(); }, 'compact'), button('Archive', archive, 'compact danger')])
        ]));
      });
      if (!visible.length) list.append(el('p', { class: 'v2-muted', text: 'No foods match this filter.' }));
    };
    search.addEventListener('input', redraw); category.addEventListener('change', redraw);
    card.append(el('div', { class: 'v2-toolbar v2-food-filter' }, [search, category]), resultCount, list); redraw();
    return card;
  }
  function renderFoods() {
    const panel = clear($('#tab-foods'));
    const intro = el('div', { class: 'card' });
    intro.append(el('h2', { text: 'Food library' }), el('p', { class: 'v2-muted', text: 'Manage reusable foods separately from the daily diary. Add packaged or recipe foods from their nutrition label; generic entries are per 100g.' }));
    panel.append(intro, addFoodCard(), foodManagementCard());
  }
  function savedMealsCard(day, summary) {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Saved meals' }), el('p', { class: 'v2-diet-note', text: 'Save a meal section as a reusable template, then load it into any section on another day.' }));
    const form = el('form'); const name = el('input', { type: 'text', required: 'true', 'aria-label': 'Template name', placeholder: 'e.g. Usual high-protein breakfast' }); const source = el('select', { 'aria-label': 'Save foods from section' }); mealSections().forEach(section => source.append(el('option', { value: section.id, text: section.label })));
    const submit = button('Save current meal', null, 'primary'); submit.type = 'submit'; form.append(el('div', { class: 'v2-grid' }, [el('div', { class: 'v2-field' }, [el('label', { text: 'Template name' }), name]), el('div', { class: 'v2-field' }, [el('label', { text: 'Save foods from' }), source])]), submit);
    form.addEventListener('submit', async event => { event.preventDefault(); const title = name.value.trim(); const entries = day.meals[source.value].filter(entry => foodForEntry(entry) && entry.grams).map(entry => ({ foodId: entry.foodId, name: foodForEntry(entry).name, foodSnapshot: snapshotFood(foodForEntry(entry)), grams: entry.grams, checked: true })); if (!title || !entries.length) return toast('Enter a name and add at least one recognised food with an amount.'); const existing = state.mealTemplates.items.find(item => item.name.toLowerCase() === title.toLowerCase() && !item.archived); if (existing) return toast('A saved meal already uses that name.'); state.mealTemplates.items.push({ id: 'meal-' + Date.now(), name: title, entries, archived: false, updatedAt: new Date().toISOString() }); try { await save('mealTemplates'); renderDiet(); toast('Saved meal created.'); } catch (error) { toast(error.message); } });
    card.append(form); const active = state.mealTemplates.items.filter(item => !item.archived).slice().sort((a, b) => a.name.localeCompare(b.name)); if (!active.length) return card;
    const target = el('select'); mealSections().forEach(section => target.append(el('option', { value: section.id, text: section.label })));
    card.append(el('div', { class: 'v2-field' }, [el('label', { text: 'Load into' }), target]));
    active.forEach(template => card.append(el('div', { class: 'v2-library-row' }, [el('div', {}, [el('strong', { text: template.name }), el('div', { class: 'v2-meta', text: template.entries.map(entry => entry.name).join(' · ') })]), el('div', { class: 'v2-actions' }, [button('Load', () => { if (!confirm(`Replace ${target.options[target.selectedIndex].text} with “${template.name}”?`)) return; day.meals[target.value] = clone(template.entries); renderDiet(); renderDietSummary(summary, day); toast('Saved meal loaded. Save the day when ready.'); }, 'compact'), button('Archive', async () => { template.archived = true; try { await save('mealTemplates'); renderDiet(); toast('Saved meal archived.'); } catch (error) { template.archived = false; toast(error.message); } }, 'compact danger')])])));
    return card;
  }
  function dietHistoryCard(currentDate) {
    const card = el('div', { class: 'card v2-diet-history' }); card.append(el('h2', { text: 'Diet history' })); const dates = Object.keys(state.diet.days).filter(date => state.diet.days[date].updatedAt).sort().reverse();
    if (!dates.length) card.append(el('p', { class: 'v2-muted', text: 'No saved diet days yet.' }));
    dates.slice(0, 30).forEach(date => { const totals = dietTotals(state.diet.days[date]).total; card.append(el('div', { class: 'v2-row' }, [el('div', { class: 'grow' }, [el('strong', { text: date }), el('div', { class: 'v2-meta', text: displayMacros(totals) })]), button(date === currentDate ? 'Current' : 'Edit', () => { $('#tab-diet').dataset.dietDate = date; renderDiet(); })])); });
    return card;
  }
  function recordsDietHistoryCard() {
    const card = el('div', { class: 'card v2-diet-history' });
    card.append(el('h2', { text: 'Meal history' }), el('p', { class: 'v2-muted', text: 'Saved daily diet records. Open one to make a correction in Diet.' }));
    const dates = Object.keys(state.diet.days).filter(date => state.diet.days[date].updatedAt).sort().reverse();
    if (!dates.length) card.append(el('p', { class: 'v2-muted', text: 'No saved diet days yet.' }));
    dates.slice(0, 60).forEach(date => {
      const totals = dietTotals(state.diet.days[date]).total;
      card.append(el('div', { class: 'v2-row' }, [
        el('div', { class: 'grow' }, [el('strong', { text: date }), el('div', { class: 'v2-meta', text: displayMacros(totals) })]),
        button('Edit in Diet', () => { $('#tab-diet').dataset.dietDate = date; selectTab('diet'); })
      ]));
    });
    return card;
  }
  function renderRecords() {
    const panel = clear($('#tab-records'));
    const intro = el('div', { class: 'card' });
    intro.append(el('h2', { text: 'Records' }), el('p', { class: 'v2-muted', text: 'Your saved meal days and completed workout sessions, kept separately from the live logging screens.' }));
    panel.append(intro, recordsDietHistoryCard(), workoutHistoryCard());
  }

  function trendValues(field) { return Object.entries(state.health.entries).sort((a, b) => a[0].localeCompare(b[0])).map(([date, entry]) => ({ date, value: entry[field] })).filter(point => Number.isFinite(point.value)); }
  function average(values) { return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null; }
  function renderTrends() {
    const panel = clear($('#tab-trends')); const weight = trendValues('weight'); const latest = weight.slice(-7).map(x => x.value); const first = weight.slice(0, 7).map(x => x.value); const recent28 = weight.slice(-28); const trend = average(latest); const start = average(first); const rate = recent28.length > 1 ? ((recent28.at(-1).value - recent28[0].value) / Math.max(1, (Date.parse(recent28.at(-1).date) - Date.parse(recent28[0].date)) / 86400000) * 7) : null;
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Trend, not the day' })); const grid = el('div', { class: 'metrics-row' });
    [['7-day weight', trend === null ? '—' : trend.toFixed(1) + ' kg'], ['Change from start', trend === null || start === null ? '—' : (trend - start).toFixed(1) + ' kg'], ['Weekly rate (28d)', rate === null ? '—' : rate.toFixed(2) + ' kg/wk']].forEach(([label, value]) => grid.append(el('div', { class: 'metric' }, [el('div', { class: 'label', text: label }), el('div', { class: 'value small', text: value })]))); card.append(grid);
    if (state.settings.goalWeight) card.append(el('p', { class: 'v2-summary', text: `Goal: ${state.settings.goalWeight} kg. This reports the trend; it does not prescribe a calorie change.` }));
    const chart = el('canvas', { height: '240', 'aria-label': 'Weight trend chart' }); card.append(chart); panel.append(card, simpleChartCard('Waist', trendValues('waist')), simpleChartCard('Sleep', trendValues('sleepHours'))); drawChart(chart, weight);
  }
  function simpleChartCard(title, points) { const card = el('div', { class: 'card' }); card.append(el('h2', { text: title })); const canvas = el('canvas', { height: '180', 'aria-label': title + ' chart' }); card.append(canvas); requestAnimationFrame(() => drawChart(canvas, points)); return card; }
  function drawChart(canvas, points) { const width = canvas.parentElement.clientWidth - 40; const height = Number(canvas.getAttribute('height')); const dpr = devicePixelRatio || 1; canvas.width = width * dpr; canvas.height = height * dpr; canvas.style.height = height + 'px'; const ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr); ctx.clearRect(0, 0, width, height); if (!points.length) { ctx.fillStyle = '#97998C'; ctx.fillText('No readings yet.', 10, height / 2); return; } const vals = points.map(p => p.value); let min = Math.min(...vals), max = Math.max(...vals); if (min === max) { min -= 1; max += 1; } const pad = (max - min) * 0.12; min -= pad; max += pad; const x = i => 34 + (points.length === 1 ? (width - 48) / 2 : i * (width - 48) / (points.length - 1)); const y = value => 10 + (height - 32) * (1 - (value - min) / (max - min)); ctx.strokeStyle = '#DAD9CC'; [0, .5, 1].forEach(t => { const yy = 10 + t * (height - 32); ctx.beginPath(); ctx.moveTo(34, yy); ctx.lineTo(width - 10, yy); ctx.stroke(); }); ctx.strokeStyle = '#2F6B4F'; ctx.lineWidth = 2; ctx.beginPath(); points.forEach((p, i) => i ? ctx.lineTo(x(i), y(p.value)) : ctx.moveTo(x(i), y(p.value))); ctx.stroke(); ctx.fillStyle = '#B9AE93'; points.forEach((p, i) => { ctx.beginPath(); ctx.arc(x(i), y(p.value), 3, 0, Math.PI * 2); ctx.fill(); }); }

  function appendTrendCards(panel) {
    const weight = trendValues('weight'); const latest = weight.slice(-7).map(x => x.value); const first = weight.slice(0, 7).map(x => x.value); const recent28 = weight.slice(-28); const trend = average(latest); const start = average(first); const rate = recent28.length > 1 ? ((recent28.at(-1).value - recent28[0].value) / Math.max(1, (Date.parse(recent28.at(-1).date) - Date.parse(recent28[0].date)) / 86400000) * 7) : null;
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Trend, not the day' })); const grid = el('div', { class: 'metrics-row' });
    [['7-day weight', trend === null ? '-' : trend.toFixed(1) + ' kg'], ['Change from start', trend === null || start === null ? '-' : (trend - start).toFixed(1) + ' kg'], ['Weekly rate (28d)', rate === null ? '-' : rate.toFixed(2) + ' kg/wk']].forEach(([label, value]) => grid.append(el('div', { class: 'metric' }, [el('div', { class: 'label', text: label }), el('div', { class: 'value small', text: value })]))); card.append(grid);
    if (state.settings.goalWeight) card.append(el('p', { class: 'v2-summary', text: `Goal: ${state.settings.goalWeight} kg. This reports the trend; it does not prescribe a calorie change.` }));
    const chart = el('canvas', { height: '240', 'aria-label': 'Weight trend chart' }); card.append(chart); panel.append(card, simpleChartCard('Waist', trendValues('waist')), simpleChartCard('Sleep', trendValues('sleepHours'))); drawChart(chart, weight);
  }
  function renderHabits() {
    const panel = clear($('#tab-habits')); appendTrendCards(panel); const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Calendar-true streaks' })); const grid = el('div', { class: 'streak-grid' });
    HABITS.forEach(([key, label]) => { let count = 0; const cursor = new Date(isoToday() + 'T12:00:00'); while (state.health.entries[cursor.toISOString().slice(0, 10)]?.[key] === true) { count++; cursor.setDate(cursor.getDate() - 1); } grid.append(el('div', { class: 'streak-card' }, [el('div', { class: 'n', text: String(count) }), el('div', { class: 'lbl', text: label })])); }); card.append(grid); panel.append(card);
    const recent = Object.entries(state.health.entries).sort((a, b) => b[0].localeCompare(a[0])).slice(0, 14);
    const history = el('div', { class: 'card' }); history.append(el('h2', { text: 'Last 14 logged days' }));
    recent.forEach(([date, entry]) => {
      history.append(el('div', { class: 'v2-row' }, [el('span', { text: date }), el('span', { class: 'v2-meta', text: HABITS.filter(([key]) => entry[key]).map(([, label]) => label).join(' · ') || 'None marked' })]));
    });
    panel.append(history);
  }

  function renderRoutines() {
    const panel = clear($('#tab-routines')); const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Routine library' }), el('p', { class: 'v2-muted', text: 'Build routines from the complete exercise list, then load one into the live workout tab.' }));
    const list = el('div', { class: 'v2-list' }); state.routines.items.forEach(routine => list.append(routineRow(routine))); card.append(list); panel.append(card, routineBuilder(), exerciseLibraryCard());
  }
  function routineRow(routine) { return el('div', { class: 'v2-row' }, [el('div', { class: 'grow' }, [el('strong', { text: routine.name }), el('div', { class: 'v2-meta', text: routine.exercises.map(ex => ex.name).join(' · ') })]), el('div', { class: 'v2-actions' }, [button('Load workout', () => startRoutine(routine.id), 'primary'), button('Edit', () => { state.selectedRoutine = routine.id; renderRoutines(); }), button('Delete', () => deleteRoutine(routine.id), 'danger')])]); }
  function defaultProgram(exercise) { return { sets: 3, restSeconds: 90, targetRpe: '', setType: 'working', target: clone(exercise.target || targetFor(exercise.name)) }; }
  function plannedSets(exercise) { const program = exercise.programming || defaultProgram(exercise); return Array.from({ length: Math.max(1, Number(program.sets) || 1) }, () => ({ reps: '', load: '', rpe: '', done: false, type: program.setType || 'working', targetRpe: program.targetRpe || '', restSeconds: Number(program.restSeconds) || 0 })); }
  function routineBuilder() {
    const editing = state.routines.items.find(item => item.id === state.selectedRoutine);
    const card = el('div', { class: 'card' });
    card.append(el('h2', { text: editing ? 'Edit routine' : 'Create routine' }));
    const form = el('form', { class: 'v2-routine-form' });
    const name = el('input', { type: 'text', required: 'true', placeholder: 'e.g. Calisthenics A' });
    name.value = editing?.name || '';
    const search = el('input', { type: 'search', placeholder: 'Filter exercise list' });
    const library = el('div', { class: 'v2-library' });
    const chosen = new Set(editing?.exercises.map(exercise => exercise.exerciseId) || []); const programs = Object.fromEntries((editing?.exercises || []).map(exercise => [exercise.exerciseId, clone(exercise.programming || defaultProgram(exercise))])); const programming = el('div', { class: 'v2-routine-form' });
    const renderProgramming = () => { clear(programming); const selected = state.library.items.filter(item => chosen.has(item.id)); if (!selected.length) return; programming.append(el('h3', { text: 'Routine programming' }), el('p', { class: 'v2-muted', text: 'Set a default plan for each exercise. Values remain editable in the live workout.' })); selected.forEach(item => { const program = programs[item.id] ||= defaultProgram(item); const fields = el('div', { class: 'v2-grid' }); const setType = el('select', {}, ['Warm-up', 'Working', 'Drop', 'Failure'].map(value => el('option', { value: value.toLowerCase().replace('-', ''), text: value }))); setType.value = program.setType || 'working'; setType.addEventListener('change', () => { program.setType = setType.value; }); fields.append(input('Sets', 'number', program.sets, value => { program.sets = Math.max(1, Number(value) || 1); }, { min: '1', max: '20', step: '1' }), input('Rest (seconds)', 'number', program.restSeconds, value => { program.restSeconds = Math.max(0, Number(value) || 0); }, { min: '0', max: '1800', step: '5' }), input('Target RPE', 'number', program.targetRpe, value => { program.targetRpe = value; }, { min: '1', max: '10', step: '0.5' }), el('div', { class: 'v2-field' }, [el('label', { text: 'Set type' }), setType])); programming.append(el('div', { class: 'v2-library-row' }, [el('div', {}, [el('strong', { text: item.name }), el('div', { class: 'v2-meta', text: `${item.target.min}–${item.target.max} ${item.target.unit}` })]), fields])); }); };
    const populate = () => {
      clear(library);
      state.library.items.filter(item => !item.archived && item.name.toLowerCase().includes(search.value.toLowerCase())).forEach(item => {
        const check = el('input', { type: 'checkbox' });
        check.checked = chosen.has(item.id);
        check.addEventListener('change', () => { if (check.checked) { chosen.add(item.id); programs[item.id] ||= defaultProgram(item); } else chosen.delete(item.id); renderProgramming(); });
        library.append(el('label', {}, [check, document.createTextNode(item.name)]));
      });
    };
    search.addEventListener('input', populate);
    populate();
    renderProgramming();
    const custom = el('input', { type: 'text', placeholder: 'Add a custom exercise to the full list' });
    const addCustom = button('Add custom exercise', async () => {
      const exerciseName = custom.value.trim();
      if (!exerciseName || state.library.items.some(item => item.name.toLowerCase() === exerciseName.toLowerCase())) return;
      state.library.items.push({ id: slug(exerciseName) + '-' + Date.now(), name: exerciseName, tip: 'Use a controlled, pain-free range of motion.', target: targetFor(exerciseName), archived: false });
      chosen.add(state.library.items.at(-1).id);
      programs[state.library.items.at(-1).id] = defaultProgram(state.library.items.at(-1));
      try { await save('library'); custom.value = ''; populate(); renderProgramming(); toast('Custom exercise added.'); } catch (error) { toast(error.message); }
    });
    const submit = button(editing ? 'Save routine' : 'Create routine', null, 'primary');
    submit.type = 'submit';
    form.append(
      el('div', { class: 'v2-field' }, [el('label', { text: 'Routine name' }), name]),
      el('div', { class: 'v2-field' }, [el('label', { text: 'Exercises' }), search, library]),
      programming,
      el('div', { class: 'v2-custom-row' }, [custom, addCustom]),
      submit
    );
    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (!chosen.size) return toast('Choose at least one exercise.');
      const routine = { id: editing?.id || 'routine-' + Date.now(), name: name.value.trim(), exercises: state.library.items.filter(item => chosen.has(item.id)).map(item => ({ exerciseId: item.id, name: item.name, target: clone(item.target), programming: clone(programs[item.id] || defaultProgram(item)) })), updatedAt: new Date().toISOString() };
      if (!routine.name) return;
      const index = state.routines.items.findIndex(item => item.id === routine.id);
      if (index >= 0) state.routines.items[index] = routine; else state.routines.items.push(routine);
      try { await save('routines'); state.selectedRoutine = null; renderRoutines(); toast('Routine saved.'); } catch (error) { toast(error.message); }
    });
    card.append(form);
    return card;
  }
  function exerciseLibraryCard() {
    const editing = state.library.items.find(item => item.id === state.editExercise);
    const card = el('div', { class: 'card' });
    card.append(el('h2', { text: editing ? 'Edit exercise' : 'Exercise library' }), el('p', { class: 'v2-muted', text: editing ? 'Changes update the exercise in saved routines. Completed workout history is left untouched.' : 'Manage the full exercise list used when building routines.' }));
    if (editing) {
      const form = el('form'); const name = el('input', { type: 'text', required: 'true' }); name.value = editing.name;
      const cue = el('textarea', { rows: '3', required: 'true' }); cue.value = editing.tip || '';
      const unit = el('select', { name: 'unit' }, [el('option', { value: 'reps', text: 'Reps' }), el('option', { value: 'seconds', text: 'Seconds' })]); unit.value = editing.target?.unit || 'reps';
      const submit = button('Save exercise', null, 'primary'); submit.type = 'submit';
      form.append(el('div', { class: 'v2-field' }, [el('label', { text: 'Exercise name' }), name]), el('div', { class: 'v2-field' }, [el('label', { text: 'Form cue' }), cue]), el('div', { class: 'v2-grid' }, [input('Target minimum', 'number', editing.target?.min, () => {}, { name: 'min', min: '0', step: '1' }), input('Target maximum', 'number', editing.target?.max, () => {}, { name: 'max', min: '0', step: '1' }), el('div', { class: 'v2-field' }, [el('label', { text: 'Target unit' }), unit])]), el('div', { class: 'v2-toolbar' }, [submit, button('Cancel', () => { state.editExercise = null; renderRoutines(); })]));
      form.addEventListener('submit', async event => {
        event.preventDefault(); const target = { min: numberOrNull(new FormData(form).get('min')) || 0, max: numberOrNull(new FormData(form).get('max')) || 0, unit: unit.value };
        editing.name = name.value.trim() || editing.name; editing.tip = cue.value.trim() || 'Use a controlled, pain-free range of motion.'; editing.target = target;
        let routinesChanged = false, activeChanged = false;
        state.routines.items.forEach(routine => routine.exercises.forEach(exercise => { if (exercise.exerciseId === editing.id) { exercise.name = editing.name; exercise.target = clone(target); routinesChanged = true; } }));
        state.active?.exercises.forEach(exercise => { if (exercise.exerciseId === editing.id) { exercise.name = editing.name; exercise.target = clone(target); activeChanged = true; } });
        try { await save('library'); if (routinesChanged) await save('routines'); if (activeChanged) await save('active'); state.editExercise = null; renderRoutines(); toast('Exercise updated.'); } catch (error) { toast(error.message); }
      });
      card.append(form); return card;
    }
    const list = el('div', { class: 'v2-list' });
    state.library.items.filter(item => !item.archived).slice().sort((a, b) => a.name.localeCompare(b.name)).forEach(item => {
      const controls = el('div', { class: 'v2-actions' }, [
        button('Edit', () => { state.editExercise = item.id; renderRoutines(); }, 'compact'),
        button('Archive', async () => {
          if (!confirm(`Remove “${item.name}” from the exercise library? Existing routines and completed sessions keep their copied exercise details.`)) return;
          item.archived = true;
          try { await save('library'); renderRoutines(); toast('Exercise archived from the library.'); } catch (error) { item.archived = false; toast(error.message); }
        }, 'compact danger')
      ]);
      list.append(el('div', { class: 'v2-library-row' }, [el('div', {}, [el('strong', { text: item.name }), el('div', { class: 'v2-meta', text: `${item.target?.min ?? '?'}–${item.target?.max ?? '?'} ${item.target?.unit || 'reps'} · ${item.tip || ''}` })]), controls]));
    });
    card.append(list); return card;
  }
  async function deleteRoutine(id) { if (!confirm('Delete this routine? Logged sessions are retained.')) return; state.routines.items = state.routines.items.filter(item => item.id !== id); try { await save('routines'); renderRoutines(); } catch (error) { toast(error.message); } }

  function workoutHistoryCard() {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Workout history' }));
    const sessions = state.workouts.sessions.slice().sort(byDate).reverse();
    if (!sessions.length) card.append(el('p', { class: 'v2-muted', text: 'No completed workouts yet.' }));
    sessions.slice(0, 60).forEach(session => {
      const detail = session.exercises.map(exercise => exercise.name + ': ' + exercise.sets.map(set => `${set.reps || '—'} @ ${set.load || 'BW'}`).join(', ')).join(' · ');
      card.append(el('div', { class: 'v2-row' }, [el('div', { class: 'grow' }, [el('strong', { text: session.date + (session.routineName ? ' — ' + session.routineName : '') }), el('div', { class: 'v2-meta', text: detail || 'No sets' }), session.notes ? el('div', { class: 'v2-meta', text: session.notes }) : null]), el('div', { class: 'v2-actions' }, [button('Edit', () => editWorkout(session.id)), button('Delete', () => deleteWorkout(session.id), 'danger')])]));
    });
    return card;
  }
  async function editWorkout(id) {
    if (state.active && !confirm('Replace the current live workout draft with this saved workout?')) return;
    const session = state.workouts.sessions.find(item => item.id === id); if (!session) return;
    await startRoutine(session.routineId, { ...clone(session), startedAt: null, elapsedSeconds: session.elapsedSeconds || 0 });
  }
  async function deleteWorkout(id) {
    if (!confirm('Delete this completed workout? You can undo for 10 seconds.')) return;
    const index = state.workouts.sessions.findIndex(item => item.id === id); const removed = state.workouts.sessions[index]; state.workouts.sessions.splice(index, 1);
    try { await save('workouts'); renderRecords(); toast('Workout deleted.', async () => { state.workouts.sessions.splice(index, 0, removed); await save('workouts'); renderRecords(); toast('Workout restored.'); }); } catch (error) { state.workouts.sessions.splice(index, 0, removed); toast(error.message); }
  }

  async function startRoutine(id, draft = null) {
    const routine = state.routines.items.find(item => item.id === id); if (!routine && !draft) return; state.active = draft || { id: null, routineId: id, routineName: routine.name, date: isoToday(), startedAt: Date.now(), elapsedSeconds: 0, exercises: routine.exercises.map(ex => ({ ...clone(ex), sets: plannedSets(ex) })), notes: '' }; try { await save('active'); selectTab('workout'); renderWorkout(); } catch (error) { toast(error.message); }
  }
  let timerHandle, restHandle, restEndsAt = null;
  function renderWorkout() {
    const panel = clear($('#tab-workout')); clearInterval(timerHandle);
    if (!state.active) {
      const card = el('div', { class: 'card' });
      card.append(el('h2', { text: 'Load a workout routine' }), el('p', { class: 'v2-muted', text: 'Choose a routine to begin. Your live session stays saved if the page closes.' }));
      state.routines.items.forEach(routine => {
        card.append(el('div', { class: 'v2-row' }, [el('strong', { class: 'grow', text: routine.name }), button('Start', () => startRoutine(routine.id), 'primary')]));
      });
      panel.append(card); return;
    }
    const active = state.active; const top = el('div', { class: 'card' }); const elapsed = el('div', { class: 'v2-timer', text: timeDisplay(sessionElapsed(active)) }); timerHandle = setInterval(() => elapsed.textContent = timeDisplay(sessionElapsed(active)), 1000); top.append(el('div', { class: 'v2-session-head' }, [el('div', {}, [el('h2', { text: active.id ? 'Edit workout' : active.routineName }), elapsed]), button('Discard draft', () => discardWorkout(), 'danger')])); const date = el('input', { type: 'date' }); date.value = active.date; date.addEventListener('change', () => { active.date = date.value; persistDraft(); }); top.append(el('label', { text: 'Workout date' }), date, restTimer()); panel.append(top);
    active.exercises.forEach((exercise, index) => panel.append(workoutExercise(exercise, index)));
    const notes = el('textarea', { rows: '3', placeholder: 'Session notes: energy, pain, form, adjustments' }); notes.value = active.notes || ''; notes.addEventListener('change', () => { active.notes = notes.value; persistDraft(); }); const saveCard = el('div', { class: 'card' }); saveCard.append(el('label', { text: 'Session notes' }), notes, button(active.id ? 'Save corrections' : 'Finish workout', finishWorkout, 'primary')); panel.append(saveCard);
  }
  function workoutExercise(exercise, index) {
    const library = state.library.items.find(item => item.id === exercise.exerciseId) || exercise; const card = el('section', { class: 'v2-exercise' }); const previous = previousExercise(exercise.name, state.active.id); const program = exercise.programming || defaultProgram(exercise); const target = exercise.target || library.target || targetFor(exercise.name); card.append(el('h3', { text: exercise.name }), el('div', { class: 'v2-tip', text: 'Form cue: ' + (library.tip || 'Use a controlled, pain-free range of motion.') }), el('div', { class: 'v2-meta', text: `Plan: ${program.sets || exercise.sets.length} ${program.setType || 'working'} sets · ${target.min}–${target.max} ${target.unit} · ${program.restSeconds || 0}s rest${program.targetRpe ? ' · target RPE ' + program.targetRpe : ''}` }), el('div', { class: 'v2-meta', text: previous ? 'Previous: ' + previous.sets.map(set => `${set.reps} @ ${set.load || 'BW'}`).join(', ') : 'No previous logged performance.' }), el('div', { class: 'v2-meta', text: 'Set fields: reps · load/variation · effort. RPE is effort on a 1–10 scale: 7 ≈ 3 reps left, 8 ≈ 2, 9 ≈ 1, 10 = maximum effort.' })); const rows = el('div'); const redraw = () => { clear(rows); exercise.sets.forEach((set, setIndex) => rows.append(setRow(exercise, set, setIndex, redraw))); }; redraw(); card.append(rows, button('+ Add set', () => { exercise.sets.push({ reps: '', load: '', rpe: '', done: false, type: program.setType || 'working', targetRpe: program.targetRpe || '', restSeconds: Number(program.restSeconds) || 0 }); persistDraft(); redraw(); })); return card;
  }
  function restTimer() {
    clearInterval(restHandle); const bar = el('div', { class: 'v2-toolbar' }); const display = el('div', { class: 'v2-timer', text: 'Rest ready' });
    const start = seconds => { restEndsAt = Date.now() + seconds * 1000; clearInterval(restHandle); restHandle = setInterval(() => { const remaining = Math.max(0, Math.ceil((restEndsAt - Date.now()) / 1000)); display.textContent = remaining ? 'Rest ' + timeDisplay(remaining) : 'Rest complete'; if (!remaining) { clearInterval(restHandle); toast('Rest complete.'); } }, 250); };
    bar.append(display, button('60s', () => start(60)), button('90s', () => start(90)), button('2 min', () => start(120)), button('Stop', () => { clearInterval(restHandle); display.textContent = 'Rest ready'; })); return bar;
  }
  function setRow(exercise, set, index, redraw) { const done = el('input', { type: 'checkbox', 'aria-label': 'Mark set ' + (index + 1) + ' complete' }); done.checked = !!set.done; done.addEventListener('change', () => { set.done = done.checked; persistDraft(); }); const unit = exercise.target?.unit === 'seconds' ? 'Seconds' : 'Reps'; const reps = el('input', { type: 'number', min: '0', step: '1', placeholder: unit, 'aria-label': 'Set ' + (index + 1) + ' ' + unit.toLowerCase() }); reps.value = set.reps; reps.addEventListener('change', () => { set.reps = reps.value; persistDraft(); }); const load = el('input', { type: 'text', placeholder: 'Load / variation', 'aria-label': 'Set ' + (index + 1) + ' load or variation' }); load.value = set.load; load.addEventListener('change', () => { set.load = load.value; persistDraft(); }); const rpe = el('input', { type: 'number', min: '1', max: '10', step: '0.5', placeholder: set.targetRpe ? 'RPE ' + set.targetRpe : 'Effort 1–10', 'aria-label': 'Set ' + (index + 1) + ' effort, RPE 1 to 10' }); rpe.value = set.rpe; rpe.addEventListener('change', () => { set.rpe = rpe.value; persistDraft(); }); const type = el('select', { 'aria-label': 'Set ' + (index + 1) + ' type' }, ['warm-up', 'working', 'drop', 'failure'].map(value => el('option', { value, text: value }))); type.value = set.type || 'working'; type.addEventListener('change', () => { set.type = type.value; persistDraft(); }); return el('div', { class: 'v2-set' }, [done, type, reps, load, rpe, button('×', () => { exercise.sets.splice(index, 1); persistDraft(); redraw(); }, 'danger')]); }
  function sessionElapsed(active) { return Math.round((active.elapsedSeconds || 0) + (active.startedAt ? (Date.now() - active.startedAt) / 1000 : 0)); }
  function timeDisplay(total) { const hours = Math.floor(total / 3600); const minutes = Math.floor(total % 3600 / 60); const seconds = total % 60; return (hours ? String(hours).padStart(2, '0') + ':' : '') + String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0'); }
  async function persistDraft() { try { await save('active'); } catch (error) { toast(error.message); } }
  async function discardWorkout() { if (!confirm('Discard this live workout?')) return; state.active = null; try { await save('active'); renderWorkout(); } catch (error) { toast(error.message); } }
  function previousExercise(name, excludeId) { return state.workouts.sessions.slice().sort(byDate).reverse().find(session => session.id !== excludeId && session.exercises.some(exercise => exercise.name === name))?.exercises.find(exercise => exercise.name === name); }
  async function finishWorkout() { const active = state.active; active.elapsedSeconds = sessionElapsed(active); active.startedAt = null; active.updatedAt = new Date().toISOString(); if (!active.exercises.some(exercise => exercise.sets.some(set => set.done || set.reps))) return toast('Log at least one set before saving.'); const completed = clone(active); const index = state.workouts.sessions.findIndex(session => session.id === completed.id); if (index >= 0) state.workouts.sessions[index] = completed; else { completed.id = 'workout-' + Date.now(); completed.createdAt = completed.updatedAt; state.workouts.sessions.push(completed); } state.workouts.sessions.sort(byDate); state.active = null; try { await save('workouts'); await save('active'); render(); toast(index >= 0 ? 'Workout corrections saved.' : 'Workout saved.'); } catch (error) { toast(error.message); } }

  function renderReview() {
    const panel = clear($('#tab-review')); const settings = el('div', { class: 'card' }); settings.append(el('h2', { text: 'Goals and recovery' })); const form = el('form'); const grid = el('div', { class: 'v2-grid' }); grid.append(input('Goal weight (kg)', 'number', state.settings.goalWeight, () => {}, { name: 'goal', min: '20', max: '400', step: '0.1' }), input('Preferred weekly rate (kg)', 'number', state.settings.weeklyRate, () => {}, { name: 'rate', min: '0', max: '1.5', step: '0.05' })); form.append(grid, button('Save goals', null, 'primary')); form.lastChild.type = 'submit'; form.addEventListener('submit', async event => { event.preventDefault(); const fd = new FormData(form); state.settings.goalWeight = numberOrNull(fd.get('goal')); state.settings.weeklyRate = numberOrNull(fd.get('rate')); try { await save('settings'); toast('Goals saved.'); } catch (error) { toast(error.message); } }); settings.append(form); panel.append(weeklyReviewCard(), settings, monthlyReviewCard(), remindersCard(), dataCard());
  }
  function weeklyReviewCard() {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Last 7 days' }), el('p', { class: 'v2-muted', text: 'A transparent summary of recorded data—not an automatic prescription.' }));
    const days = Array.from({ length: 7 }, (_, index) => { const value = new Date(); value.setDate(value.getDate() - index); return value.toISOString().slice(0, 10); });
    const dietDays = days.filter(date => state.diet.days[date]?.updatedAt).map(date => dietTotals(state.diet.days[date]).total); const healthDays = days.map(date => state.health.entries[date]).filter(Boolean); const workouts = state.workouts.sessions.filter(session => days.includes(session.date));
    const avg = (items, key) => items.length ? items.reduce((sum, item) => sum + (Number(item[key]) || 0), 0) / items.length : null;
    const values = [['Diet days', `${dietDays.length}/7`, dietDays.length >= 4 ? 'Enough for a useful average' : 'Log 4+ days for useful averages'], ['Avg calories', avg(dietDays, 'calories') === null ? '—' : Math.round(avg(dietDays, 'calories')) + ' kcal', 'Saved diet days only'], ['Avg protein', avg(dietDays, 'protein') === null ? '—' : Math.round(avg(dietDays, 'protein')) + ' g', 'Saved diet days only'], ['Workouts', String(workouts.length), 'Completed sessions'], ['Avg sleep', avg(healthDays, 'sleepHours') === null ? '—' : avg(healthDays, 'sleepHours').toFixed(1) + ' h', 'Daily entries']];
    const grid = el('div', { class: 'v2-macro-grid' }); values.forEach(([label, value, note]) => grid.append(el('div', { class: 'v2-macro' }, [el('span', { text: label }), el('strong', { text: value }), el('span', { text: note })]))); card.append(grid); return card;
  }
  function monthlyReviewCard() { const current = state.reviews.items[monthKey()] || {}; const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Monthly review — ' + monthKey() }), el('p', { class: 'v2-muted', text: 'Record a short reflection, measurements, and whether progress photos were taken. Photos remain in your private photo library.' })); const form = el('form'); const photos = el('input', { type: 'checkbox', name: 'photos' }); photos.checked = !!current.photosTaken; const text = el('textarea', { name: 'notes', rows: '4', placeholder: 'What worked? What will you adjust next month?' }); text.value = current.notes || ''; form.append(el('label', { class: 'v2-check' }, [photos, document.createTextNode('Progress photos taken (store them separately, e.g. Immich)')]), el('label', { text: 'Review notes' }), text, button('Save monthly review', null, 'primary')); form.lastChild.type = 'submit'; form.addEventListener('submit', async event => { event.preventDefault(); state.reviews.items[monthKey()] = { photosTaken: photos.checked, notes: text.value, updatedAt: new Date().toISOString() }; try { await save('reviews'); toast('Monthly review saved.'); } catch (error) { toast(error.message); } }); card.append(form); return card; }
  function reminderDays(days) {
    if (!Array.isArray(days)) return 'Every day';
    const names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return days.map(day => names[day]).join(' + ');
  }
  function remindersCard() {
    const card = el('div', { class: 'card' });
    card.append(el('h2', { text: 'Reminder controls' }), el('p', { class: 'v2-muted', text: 'The scheduler chooses the right training prompt for the day. Disable a prompt or adjust its local time here.' }));
    if (!state.reminderCatalog.length) card.append(el('p', { class: 'v2-muted', text: 'Reminder catalogue is unavailable. Refresh the page after the server is updated.' }));
    state.reminderCatalog.forEach(item => {
      const enabled = el('input', { type: 'checkbox' });
      enabled.checked = state.reminders.enabled[item.id] !== false;
      const time = el('input', { type: 'time', 'aria-label': item.label + ' time' });
      time.value = state.reminders.times[item.id] || item.time;
      enabled.addEventListener('change', () => { state.reminders.enabled[item.id] = enabled.checked; });
      time.addEventListener('change', () => { state.reminders.times[item.id] = time.value; });
      card.append(el('div', { class: 'v2-row' }, [
        el('label', { class: 'v2-check grow' }, [enabled, el('span', { class: 'v2-reminder-copy' }, [el('strong', { text: item.label }), el('span', { class: 'v2-meta', text: reminderDays(item.days) })])]),
        time
      ]));
    });
    const actions = el('div', { class: 'v2-toolbar' }, [
      button('Save reminder controls', async () => { try { await save('reminders'); toast('Reminder controls saved.'); } catch (error) { toast(error.message); } }, 'primary'),
      button('Send test notification', async () => { const response = await fetch('/api/reminders/test', { method: 'POST' }); toast(response.ok ? 'Test notification sent.' : 'Test notification failed.'); })
    ]);
    card.append(actions);
    return card;
  }
  function dataCard() {
    const card = el('div', { class: 'card' });
    card.append(el('h2', { text: 'Backup and recovery' }), el('p', { class: 'v2-muted', text: 'Exports include daily logs, diets, food and saved-meal libraries, constants, workouts, routines, settings, reviews, and reminder preferences.' }));
    const output = el('div', { class: 'v2-muted' });
    const file = el('input', { type: 'file', accept: 'application/json' });
    const restore = button('Restore selected backup', async () => {
      const candidate = file._bundle;
      if (!candidate) return;
      const snapshot = await exportBundle();
      try {
        await write(KEY.preImport, snapshot);
        for (const [part, value] of Object.entries(candidate.data)) if (KEY[part] && value !== null) { state[part] = value; await save(part); }
        await loadAll(); render(); toast('Backup restored. A pre-import snapshot was saved on the server.');
      } catch (error) { toast(error.message); }
    }, 'primary');
    restore.disabled = true;
    file.addEventListener('change', async () => {
      try {
        let candidate = JSON.parse(await file.files[0].text());
        if (!candidate?.data) throw new Error('Invalid');
        if (candidate.data['health-log']) candidate = { schemaVersion: 1, data: { health: candidate.data['health-log'], workouts: candidate.data['workout-log'], routines: null, library: null, settings: null, reviews: null, reminders: null } };
        file._bundle = candidate;
        const parts = Object.entries(candidate.data).filter(([, value]) => value !== null).map(([part, value]) => `${part}: ${Array.isArray(value?.sessions) ? value.sessions.length + ' sessions' : value?.entries ? Object.keys(value.entries).length + ' entries' : 'present'}`);
        output.textContent = 'Ready to restore — ' + parts.join(', ') + '. A snapshot will be made first.';
        restore.disabled = false;
      } catch { output.textContent = 'That file is not a valid Recomp Tracker backup.'; restore.disabled = true; }
    });
    card.append(
      el('div', { class: 'v2-toolbar v2-data-actions' }, [button('Download backup', async () => downloadJSON(await exportBundle(), 'recomp-tracker-backup-' + isoToday() + '.json'), 'primary')]),
      el('div', { class: 'v2-toolbar v2-data-actions' }, [file, restore]),
      output,
      el('div', { class: 'v2-toolbar' }, [button('Restore most recent pre-import snapshot', restorePreImport)])
    );
    return card;
  }
  async function restorePreImport() { try { const snapshot = await read(KEY.preImport, null); if (!snapshot?.data) return toast('No pre-import snapshot is available.'); if (!confirm('Restore the most recent pre-import snapshot?')) return; for (const [part, value] of Object.entries(snapshot.data)) if (KEY[part] && value !== null) { state[part] = value; await save(part); } await loadAll(); render(); toast('Pre-import snapshot restored.'); } catch (error) { toast(error.message); } }
  async function exportBundle() { return { schemaVersion: 4, exportedAt: new Date().toISOString(), data: { health: state.health, diet: state.diet, foods: state.foods, dietSettings: state.dietSettings, mealTemplates: state.mealTemplates, workouts: state.workouts, routines: state.routines, library: state.library, settings: state.settings, reviews: state.reviews, reminders: state.reminders } }; }
  function downloadJSON(value, name) { const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' })); const link = el('a', { href: url, download: name }); link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); }

  async function boot() { try { await loadAll(); if (state._migratedDiet) { try { await save('diet'); } catch { /* Existing records remain usable; retry on the next successful save. */ } } buildShell(); render(); if ('serviceWorker' in navigator) navigator.serviceWorker.register('/static/service-worker.js').catch(() => {}); } catch (error) { document.body.prepend(el('div', { class: 'v2-banner', role: 'alert', text: 'Could not load the tracker. Check the connection and refresh. ' + error.message })); } }
  boot();
})();
