/* Recomp Tracker v2: accessible, conflict-aware personal tracking UI. */
(() => {
  'use strict';

  const KEY = {
    health: 'health-log', workouts: 'workout-log', routines: 'workout-routines',
    library: 'exercise-library', settings: 'tracker-settings', reviews: 'monthly-reviews',
    reminders: 'reminder-settings', active: 'active-workout', preImport: 'pre-import-snapshot',
    diet: 'daily-diet-log', foods: 'food-library', dietSettings: 'diet-settings', mealTemplates: 'meal-templates',
    programme: 'calisthenics-programme'
  };
  const VERSIONS = {};
  const state = { health: { entries: {} }, workouts: { sessions: [] }, routines: { items: [] },
    library: { items: [] }, settings: { goalWeight: null, weeklyRate: 0.4 }, reviews: { items: {} },
    reminders: { enabled: {}, times: {} }, reminderCatalog: [], diet: { days: {} }, foods: { items: [] },
    dietSettings: { constants: [], targets: { calories: 2010, protein: 180, carbs: 0, fat: 0 } }, mealTemplates: { items: [] },
    programme: { currentPhase: 'phase-0', currentWeek: 1, skillStages: { muscleUp: 1, hspu: 1, planche: 1 }, prerequisites: {}, weeklyChecks: {}, tests: [], stageHistory: [] },
    exerciseCatalog: [], active: null, selectedRoutine: null, editExerciseGoal: null, undo: null, lastWorkoutId: null, recordsFilters: { type: 'all', from: '', to: '', routine: '' } };
  const HABITS = [
    ['training', 'Resistance training / calisthenics'], ['proteinBreakfast', 'Protein-forward breakfast'],
    ['postMealWalk', 'Post-meal walk after biggest carb meal'], ['dimLight', 'Dim light / no screens before bed'],
    ['morningLight', 'Morning light exposure']
  ];
  const EXERCISE_NAME_ALIASES = {
    'air squats': 'Squat - Air', 'back squat': 'Squat - Barbell back', 'bicep curl': 'Curl - Biceps', 'calf raise': 'Calf raise - Standing', 'dead hang': 'Hang - Dead',
    'dip back-off (bodyweight/light)': 'Dip - Bodyweight back-off', "farmer's carry": "Carry - Farmer's", 'full form chin-up': 'Chin-up - Full form', 'full form dips': 'Dip - Full form',
    'full form pull-up': 'Pull-up - Full form', 'full form push up': 'Push-up - Full form', 'isometric hold (wall squat / dip bottom)': 'Isometric hold - Wall squat or dip bottom',
    'isometrics - dip': 'Dip - Isometric hold', 'isometrics - pull up': 'Pull-up - Isometric hold', 'isometrics - push-up': 'Push-up - Isometric hold', 'jump squat': 'Squat - Jump',
    'lateral bound': 'Bound - Lateral', 'lateral raise': 'Raise - Dumbbell lateral', 'mobility - arm twists': 'Arm circle - Mobility', 'overhead press': 'Press - Barbell overhead',
    'pull-up back-off (bodyweight/light)': 'Pull-up - Bodyweight back-off', 'rings - dips': 'Dip - Rings', 'rings - pull-ups': 'Pull-up - Rings', 'rings - push-ups': 'Push-up - Rings',
    'rings - rows': 'Row - Rings', 'romanian deadlift': 'Deadlift - Romanian', 'row': 'Row - Weighted', 'skipping': 'Skipping - Freestyle', 'skipping - boxer': 'Skipping - Boxer step',
    'skipping - forward and back': 'Skipping - Forward and back', 'skipping - knees up': 'Skipping - High knees', 'skipping - normal': 'Skipping - Basic', 'static bike - hiit': 'Bike - Static HIIT',
    'tricep pushdown': 'Pushdown - Triceps', 'weighted / leverage push-up': 'Push-up - Weighted', 'weighted dip': 'Dip - Weighted', 'weighted pull-up': 'Pull-up - Weighted'
  };
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
  const PROGRAMME_PHASES = [
    { id: 'phase-0', name: 'Phase 0 — Foundation', duration: '4–6 weeks', focus: 'Prerequisites, general tendon conditioning, wrist and shoulder prehab' },
    { id: 'phase-1', name: 'Phase 1 — Base building', duration: 'Months 2–5', focus: 'Muscle-up progressions, HSPU wall work, planche lean and tuck' },
    { id: 'phase-2', name: 'Phase 2 — Intermediate', duration: 'Months 5–10', focus: 'Muscle-up refinement, freestanding HSPU, advanced tuck and straddle planche' },
    { id: 'phase-3', name: 'Phase 3 — Specialisation', duration: 'Months 10+', focus: 'Full planche, strict or deficit HSPU, muscle-up volume and control' }
  ];
  const PROGRAMME_PREREQUISITES = [
    ['pullups', '8 strict pull-ups', 'Full dead hang to chin over bar', 'Pull-up - Full form'], ['pushups', '15 push-ups', 'Clean, repeatable form', 'Push-up - Full form'],
    ['dips', '10 parallel-bar dips', 'Pain-free depth', 'Dip - Full form'], ['hollow', '30-second hollow body hold', 'Position maintained', 'Hollow body - Hold'],
    ['handstand', '20-second chest-to-wall handstand', 'Or 30 seconds cumulative freestanding balance', 'Handstand - Chest to wall'],
    ['painFree', 'No pain at rest or under light load', 'Wrist, elbow and shoulder', null]
  ];
  const PROGRAMME_SESSIONS = [
    ['mon', 'Mon', 'Muscle-up progression + pulling volume'], ['tue', 'Tue', 'HSPU progression + wrist/shoulder tendon work'],
    ['thu', 'Thu', 'Planche progression + pushing/compression volume'], ['sat', 'Sat', 'Full-body integration: lighter versions of all three + mobility']
  ];
  const PROGRAMME_SKILLS = {
    muscleUp: { label: 'Muscle-up', timeline: '4–8 months', risk: 'Biceps tendon, elbow, wrist transition and shoulder', addition: 'From Stage 4: false-grip transition support holds, 2×20s twice weekly.', stages: [
      ['Strict pull-ups to sternum, 4×6', '4×8 clean, no elbow discomfort', 'Pull-up - Sternum'], ['False-grip dead hangs, 3×15–20s', '3×30s pain-free', 'Hang - False grip'],
      ['False-grip pull-ups, full ROM, 4×5', '4×8', 'Pull-up - False grip'], ['High pull-ups, 4×5', '4×6 with a controlled descent', 'Pull-up - Chest to bar'],
      ['Straight-bar dips, 4×8', '4×12', 'Dip - Straight bar'], ['Russian dips or band-assisted transitions, 4×5', 'Controlled transition with no wrist pinch', 'Dip - Russian'],
      ['Negative muscle-ups, 3–5s eccentric, 4×4', '4×6 smooth eccentrics', 'Muscle-up - Negative'], ['Band-assisted full muscle-ups, 3×4', 'Reduce band tension until unassisted', 'Muscle-up - Band assisted'],
      ['Strict muscle-ups, singles to sets', '3×3 clean strict reps', 'Muscle-up - Strict bar']
    ] },
    hspu: { label: 'Handstand push-up', timeline: '6–12 months', risk: 'Wrist and shoulder under overhead bodyweight', addition: 'From Stage 2: wrist extension isometrics and partial-bodyweight handstand wrist prep 3×/week.', stages: [
      ['Feet-elevated pike push-ups, 4×8', '4×12', 'Push-up - Pike, feet elevated'], ['Chest-to-wall handstand hold, 5×20s', '5×45s with pain-free wrists', 'Handstand - Chest to wall'],
      ['Back-to-wall handstand hold', '3×30s controlled', 'Handstand - Back to wall'], ['Wall walks, 3×5', 'Smooth and controlled both directions', 'Handstand - Wall walk'],
      ['Wall HSPU negatives, 4×3', '4×5 with 3–4s eccentrics', 'Handstand push-up - Wall negative'], ['Box/deficit pike push-ups, 4×6', '4×10', 'Push-up - Pike, feet elevated'],
      ['Wall-assisted HSPU, partial ROM, 4×5', '4×8', 'Handstand push-up - Wall partial range'], ['Wall-assisted HSPU, full ROM, 4×5', '4×8 clean', 'Handstand push-up - Wall full range'],
      ['Freestanding handstand hold, 5×15–30s', '60s+ consistent balance', 'Handstand - Freestanding practice'], ['Freestanding or deficit HSPU', '3×3–5', 'Handstand push-up - Freestanding']
    ] },
    planche: { label: 'Planche', timeline: '12–30 months', risk: 'Wrist, elbow and shoulder under near-maximal straight-arm tension', addition: 'Daily wrist mobility plus straight-arm support holds 3×/week and parallel compression work.', stages: [
      ['Planche lean, 5×15s', '5×30s pain-free', 'Planche - Lean'], ['Frog stand / tuck planche, 5×10s', '5×20s', 'Planche - Frog stand'],
      ['Tuck planche, 5×10s', '5×20s', 'Planche - Tuck'], ['Advanced tuck planche, 5×8s', '5×15s', 'Planche - Advanced tuck'],
      ['Straddle planche, 5×5s', '5×12s', 'Planche - Straddle'], ['Half-lay / single-leg planche', '5×8s per side', 'Planche - Single leg'], ['Full planche', 'Build toward 5×10s', 'Planche - Full']
    ] }
  };
  const EXERCISE_CHAINS = [
    ['Push-up - Incline', 'Push-up - Knee', 'Push-up - Full form', 'Push-up - Decline', 'Push-up - Archer', 'Push-up - One-arm assisted', 'Push-up - One-arm'],
    ['Push-up - Pike', 'Push-up - Pike, feet elevated', 'Handstand push-up - Wall negative', 'Handstand push-up - Wall partial range', 'Handstand push-up - Wall full range', 'Handstand push-up - Deficit wall', 'Handstand push-up - Freestanding'],
    ['Pull-up - Scapular', 'Pull-up - Band assisted', 'Pull-up - Negative', 'Pull-up - Full form', 'Pull-up - Chest to bar', 'Pull-up - Sternum', 'Pull-up - Archer', 'Pull-up - Weighted'],
    ['Dip - Band assisted', 'Dip - Negative', 'Dip - Full form', 'Dip - Straight bar', 'Dip - Rings', 'Dip - Weighted'],
    ['Muscle-up - Jumping transition', 'Muscle-up - Band assisted', 'Muscle-up - Negative', 'Muscle-up - Strict bar', 'Muscle-up - Strict rings'],
    ['Planche - Lean', 'Planche - Frog stand', 'Planche - Tuck', 'Planche - Advanced tuck', 'Planche - Single leg', 'Planche - Straddle', 'Planche - Full'],
    ['Front lever - Tuck', 'Front lever - Advanced tuck', 'Front lever - Single leg', 'Front lever - Straddle', 'Front lever - Full'],
    ['Back lever - Skin the cat', 'Back lever - Tuck', 'Back lever - Advanced tuck', 'Back lever - Straddle', 'Back lever - Full'],
    ['Row - Inverted', 'Row - Inverted, feet elevated', 'Row - Rings', 'Row - Rings archer', 'Row - Weighted'],
    ['Hang - Dead', 'Hang - Active', 'Hang - False grip'],
    ['L-sit - Tuck', 'L-sit - Full'],
    ['Pistol squat - Assisted', 'Pistol squat - Full']
  ];

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
  function libraryExercise(name) {
    return state.library.items.find(item => item.name === name) || state.exerciseCatalog.find(item => item.name === name) || null;
  }
  function exerciseById(id) { return state.library.items.find(item => item.id === id) || null; }
  function defaultProgression(exercise) {
    const chain = EXERCISE_CHAINS.find(items => items.includes(exercise.name)); if (!chain) return { regressionId: '', progressionId: '' };
    const index = chain.indexOf(exercise.name); return { regressionId: index > 0 ? libraryExercise(chain[index - 1])?.id || '' : '', progressionId: index < chain.length - 1 ? libraryExercise(chain[index + 1])?.id || '' : '' };
  }
  function progressionFor(exercise) {
    const defaults = defaultProgression(exercise); return { regressionId: exercise.progression?.regressionId ?? defaults.regressionId, progressionId: exercise.progression?.progressionId ?? defaults.progressionId };
  }
  function exerciseFamily(exercise) { return String(exercise?.name || '').split(' - ')[0].trim().toLowerCase(); }
  function exerciseVisual(exercise) {
    const family = exercise?.visual || 'general';
    const poses = {
      push: [[18,48,43,43],[43,43,70,52],[20,48,9,62],[70,52,88,60]], pull: [[50,28,50,55],[50,55,34,77],[50,55,66,77],[50,36,28,14],[50,36,72,14]],
      dip: [[50,30,50,56],[50,40,31,39],[50,40,69,39],[50,56,38,82],[50,56,62,82]], handstand: [[50,72,50,42],[50,42,35,18],[50,42,65,18],[50,72,39,88],[50,72,61,88]],
      planche: [[25,45,53,42],[53,42,82,35],[25,45,15,68],[25,45,38,69]], lever: [[20,38,50,42],[50,42,84,42],[20,38,10,16],[20,38,31,16]],
      legs: [[50,31,47,57],[47,57,28,81],[47,57,69,76],[50,43,30,54],[50,43,70,51]], core: [[20,62,52,52],[52,52,82,34],[20,62,7,74],[52,52,69,72]],
      stretch: [[49,29,49,57],[49,57,28,82],[49,57,69,82],[49,42,25,27],[49,42,76,20]], weights: [[50,28,50,58],[50,58,35,83],[50,58,65,83],[50,42,24,30],[50,42,76,30]],
      cardio: [[48,29,50,53],[50,53,29,76],[50,53,73,69],[50,40,26,53],[50,40,72,24]], support: [[50,29,50,57],[50,57,37,82],[50,57,63,82],[50,39,28,53],[50,39,72,53]],
      row: [[22,43,53,48],[53,48,79,66],[22,43,8,22],[22,43,34,19]], mobility: [[50,28,50,57],[50,57,35,83],[50,57,65,83],[50,40,23,24],[50,40,77,24]],
      general: [[50,28,50,57],[50,57,35,83],[50,57,65,83],[50,40,28,54],[50,40,72,54]]
    };
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.setAttribute('viewBox', '0 0 100 100'); svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', `${exercise?.name || 'Exercise'} movement schematic`);
    const line = (x1, y1, x2, y2, extra = {}) => { const node = document.createElementNS(svg.namespaceURI, 'line'); Object.entries({ x1, y1, x2, y2, ...extra }).forEach(([key, value]) => node.setAttribute(key, value)); svg.append(node); };
    line(8, 90, 92, 90, { class: 'v2-ground' }); if (['pull', 'lever'].includes(family)) line(9, 13, 91, 13, { class: 'v2-apparatus' }); if (family === 'dip') { line(12, 39, 39, 39, { class: 'v2-apparatus' }); line(61, 39, 88, 39, { class: 'v2-apparatus' }); }
    const segments = poses[family] || poses.general; segments.forEach(([x1, y1, x2, y2]) => line(x1, y1, x2, y2)); const head = document.createElementNS(svg.namespaceURI, 'circle'); head.setAttribute('cx', String(segments[0][0])); head.setAttribute('cy', String(segments[0][1] - 8)); head.setAttribute('r', '6'); svg.append(head);
    return el('figure', { class: 'v2-exercise-visual' }, [svg, el('figcaption', { text: 'Position schematic — follow the written steps.' })]);
  }
  function exerciseGuide(exercise, showVisual = true) {
    if (!exercise) return el('p', { class: 'v2-muted', text: 'No form guide has been linked to this item yet.' });
    const steps = Array.isArray(exercise.instructions) && exercise.instructions.length ? exercise.instructions : ['Set a stable start position.', 'Move through a controlled, pain-free range.', 'Stop before technique breaks down.'];
    return el('div', { class: 'v2-exercise-guide' }, [showVisual ? exerciseVisual(exercise) : null, el('div', { class: 'grow' }, [el('p', { class: 'v2-tip', text: 'Key cue: ' + exercise.tip }), el('ol', {}, steps.map(step => el('li', { text: step })))])]);
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
    const [health, workouts, routines, library, settings, reviews, reminders, active, reminderCatalog, diet, foods, dietSettings, mealTemplates, programme, exerciseCatalog] = await Promise.all([
      read(KEY.health, { entries: {} }), read(KEY.workouts, { sessions: [] }), read(KEY.routines, { items: [] }),
      read(KEY.library, { items: [] }), read(KEY.settings, { goalWeight: null, weeklyRate: 0.4 }),
      read(KEY.reviews, { items: {} }), read(KEY.reminders, { enabled: {}, times: {} }), read(KEY.active, null),
      fetch('/api/reminders').then(response => response.ok ? response.json() : { items: [] }).catch(() => ({ items: [] })),
      read(KEY.diet, { days: {} }), read(KEY.foods, { items: [] }),
      read(KEY.dietSettings, { constants: [], targets: { calories: 2010, protein: 180, carbs: 0, fat: 0 } }), read(KEY.mealTemplates, { items: [] }),
      read(KEY.programme, { currentPhase: 'phase-0', currentWeek: 1, skillStages: { muscleUp: 1, hspu: 1, planche: 1 }, prerequisites: {}, weeklyChecks: {}, tests: [] }),
      fetch('/static/exercise-catalog.json').then(response => response.ok ? response.json() : []).catch(() => [])
    ]);
    state.health = health && health.entries ? health : { entries: {} };
    state.workouts = workouts && workouts.sessions ? workouts : { sessions: [] };
    state.routines = routines && routines.items ? routines : { items: [], templates: [] };
    state.library = library && library.items ? library : { items: [] };
    state.settings = settings || { goalWeight: null, weeklyRate: 0.4 };
    state.reviews = reviews && reviews.items ? reviews : { items: {} };
    state.reminders = reminders || { enabled: {}, times: {} };
    state.reminderCatalog = Array.isArray(reminderCatalog?.items) ? reminderCatalog.items : [];
    state.diet = diet && diet.days ? diet : { days: {} };
    state.foods = foods && foods.items ? foods : { items: [] };
    state.dietSettings = dietSettings && dietSettings.targets ? dietSettings : { constants: [], targets: { calories: 2010, protein: 180, carbs: 0, fat: 0 } };
    state.mealTemplates = mealTemplates && mealTemplates.items ? mealTemplates : { items: [] };
    state.programme = programme && programme.skillStages ? programme : { currentPhase: 'phase-0', currentWeek: 1, skillStages: { muscleUp: 1, hspu: 1, planche: 1 }, prerequisites: {}, weeklyChecks: {}, tests: [] };
    state.exerciseCatalog = Array.isArray(exerciseCatalog) ? exerciseCatalog : [];
    state.active = active || null;
    migrate();
  }
  function migrate() {
    let dietMigrated = false, libraryMigrated = false, routinesMigrated = false, settingsMigrated = false;
    if (!state.library.items.length) state.library.items = clone(state.exerciseCatalog.length ? state.exerciseCatalog : DEFAULT_EXERCISES);
    state.library.items.forEach(item => { item.id ||= slug(item.name); item.target ||= targetFor(item.name); item.tip ||= 'Use a controlled, pain-free range of motion.'; item.instructions ||= ['Set a stable start position.', 'Move through a controlled, pain-free range.', 'Stop the set when position or tempo breaks down.']; item.visual ||= 'general'; item.archived ||= false; if (!item.progression) { item.progression = defaultProgression(item); libraryMigrated = true; } });
    if (!Array.isArray(state.routines.templates)) { state.routines.templates = []; routinesMigrated = true; }
    if (!state.routines.scheduleOverrides || typeof state.routines.scheduleOverrides !== 'object') { state.routines.scheduleOverrides = {}; routinesMigrated = true; }
    state.routines.items.forEach(routine => { if (!Array.isArray(routine.scheduleDays)) { routine.scheduleDays = []; routinesMigrated = true; } const normalDays = [...new Set(routine.scheduleDays.map(Number).filter(day => Number.isInteger(day) && day >= 0 && day <= 6))].sort((a, b) => a - b); if (JSON.stringify(normalDays) !== JSON.stringify(routine.scheduleDays)) { routine.scheduleDays = normalDays; routinesMigrated = true; } if (!Array.isArray(routine.versions)) { routine.versions = []; routinesMigrated = true; } if (!Number.isFinite(Number(routine.version))) { routine.version = 1; routinesMigrated = true; } else routine.version = Number(routine.version); routine.exercises.forEach(exercise => { const before = JSON.stringify(exercise.programming || {}); exercise.programming = normaliseProgramming(exercise.programming || defaultProgram(exercise)); if (before !== JSON.stringify(exercise.programming)) routinesMigrated = true; }); });
    if (!state.foods.items.length) state.foods.items = clone(DEFAULT_FOODS);
    state.foods.items.forEach(item => { item.id ||= slug(item.name); item.basis ||= '100g'; item.aliases = Array.isArray(item.aliases) ? item.aliases : []; item.servings = Array.isArray(item.servings) ? item.servings : []; item.archived ||= false; item.favourite = item.favourite === true; });
    if (!state.dietSettings.constants.length) state.dietSettings.constants = clone(DEFAULT_CONSTANTS);
    if (!Array.isArray(state.dietSettings.sections) || !state.dietSettings.sections.length) state.dietSettings.sections = MEALS.map(([id, label]) => ({ id, label, archived: false }));
    if (!state.dietSettings.targetProfiles) {
      const base = clone(state.dietSettings.targets);
      state.dietSettings.targetProfiles = {
        standard: { label: 'Standard', ...clone(base) }, training: { label: 'Training day', ...clone(base) }, rest: { label: 'Rest day', ...clone(base) }
      };
    }
    state.dietSettings.targetSchedule ||= { 0: 'rest', 1: 'training', 2: 'training', 3: 'standard', 4: 'training', 5: 'standard', 6: 'training' };
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
    state._migratedLibrary = libraryMigrated; state._migratedRoutines = routinesMigrated;
    Object.values(state.health.entries).forEach(entry => { entry.createdAt ||= entry.updatedAt || new Date().toISOString(); entry.updatedAt ||= entry.createdAt; });
    state.workouts.sessions.forEach(session => { session.id ||= session.date + '-' + Math.random().toString(36).slice(2); session.createdAt ||= new Date().toISOString(); session.updatedAt ||= session.createdAt; });
    state.settings.compactWorkout = state.settings.compactWorkout === true;
    if (!state.settings.equipment) { state.settings.equipment = { loadIncrement: 2.5, barWeight: 20, platePairs: [25, 25, 20, 20, 15, 10, 5, 2.5, 1.25, 0.5] }; settingsMigrated = true; }
    state.settings.equipment.loadIncrement = Math.max(0.1, Number(state.settings.equipment.loadIncrement) || 2.5); state.settings.equipment.barWeight = Math.max(0, Number(state.settings.equipment.barWeight) || 20); if (!Array.isArray(state.settings.equipment.platePairs)) { state.settings.equipment.platePairs = [25, 25, 20, 20, 15, 10, 5, 2.5, 1.25, 0.5]; settingsMigrated = true; }
    if (!Array.isArray(state.settings.exerciseGoals)) { state.settings.exerciseGoals = []; settingsMigrated = true; }
    state.settings.exerciseGoals.forEach(goal => { goal.id ||= 'exercise-goal-' + Math.random().toString(36).slice(2); goal.metric = ['reps', 'seconds', 'load'].includes(goal.metric) ? goal.metric : 'reps'; goal.target = Math.max(0.1, Number(goal.target) || 1); goal.archived = goal.archived === true; goal.createdAt ||= new Date().toISOString(); });
    if (!state.settings.hiit || typeof state.settings.hiit !== 'object') { state.settings.hiit = { workSeconds: 40, restSeconds: 20, rounds: 10, prepareSeconds: 10, sound: true }; settingsMigrated = true; }
    const hiit = state.settings.hiit; const normalHiit = { workSeconds: Math.min(3600, Math.max(1, Number(hiit.workSeconds) || 40)), restSeconds: Math.min(3600, Math.max(0, Number(hiit.restSeconds) || 0)), rounds: Math.min(100, Math.max(1, Number(hiit.rounds) || 10)), prepareSeconds: Math.min(600, Math.max(0, Number(hiit.prepareSeconds) || 0)), sound: hiit.sound !== false }; if (JSON.stringify(hiit) !== JSON.stringify(normalHiit)) { state.settings.hiit = normalHiit; settingsMigrated = true; }
    if (state.active) { state.active.autoRest = state.active.autoRest !== false; state.active.restEndsAt ||= null; state.active.exercises ||= []; state.active.exercises.forEach(exercise => { exercise.programming = normaliseProgramming(exercise.programming || defaultProgram(exercise)); exercise.sets ||= plannedSets(exercise); exercise.quickNotes ||= { pain: '', failed: false, note: '' }; }); }
    state.programme.currentPhase ||= 'phase-0'; state.programme.currentWeek = Math.max(1, Number(state.programme.currentWeek) || 1);
    state.programme.skillStages ||= { muscleUp: 1, hspu: 1, planche: 1 }; state.programme.prerequisites ||= {}; state.programme.weeklyChecks ||= {}; state.programme.tests ||= []; state.programme.stageHistory ||= [];
    state._migratedSettings = settingsMigrated;
  }

  function styles() {
    if ($('#v2-style')) return;
    const css = `
      .v2-toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:14px 0}
      .v2-btn{min-height:38px;border:1px solid var(--line);border-radius:7px;background:#fff;color:var(--forest);padding:8px 12px;font:500 13px 'Work Sans',sans-serif;cursor:pointer}
      .v2-btn.primary{background:var(--forest);color:#fff;border-color:var(--forest)}.v2-btn.danger{color:var(--danger)}.v2-btn:disabled{opacity:.55;cursor:not-allowed}
      .v2-btn:focus-visible,#tab-dashboard input:focus-visible,#tab-dashboard select:focus-visible,#tab-routines input:focus-visible,#tab-workout input:focus-visible,#tab-review input:focus-visible,#tab-diet input:focus-visible,#tab-foods input:focus-visible,#tab-programme input:focus-visible,#tab-routines textarea:focus-visible,#tab-workout textarea:focus-visible,#tab-review textarea:focus-visible,#tab-diet textarea:focus-visible,#tab-foods textarea:focus-visible,#tab-programme textarea:focus-visible{outline:3px solid #9fc6af;outline-offset:2px}
      .v2-banner{background:#fff4d6;border:1px solid #e8c66b;border-radius:8px;padding:10px 12px;margin-bottom:12px;font-size:13px}
      .v2-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-bottom:14px}.v2-grid.one{grid-template-columns:1fr}
      .v2-row{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:12px 0;border-bottom:1px solid var(--line)}.v2-row:last-child{border-bottom:0}.v2-row .grow{flex:1;min-width:160px}.v2-meta{font-size:12px;color:var(--ink-faint)}.v2-actions{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.v2-list{display:flex;flex-direction:column}
      .v2-set{display:grid;grid-template-columns:28px 82px minmax(0,1fr) minmax(0,1fr) 72px 74px;gap:8px;align-items:center;margin:8px 0}.v2-set input,.v2-set select{min-width:0}.v2-set-actions{display:flex;gap:4px}.v2-set-actions .v2-btn{min-width:32px;padding:5px}.v2-set.done{background:#edf5ef;border-radius:7px;padding:4px}
      .v2-exercise{border:1px solid var(--line);border-radius:8px;padding:14px;margin:12px 0;background:#fff}.v2-exercise.skipped{opacity:.68;background:var(--card)}.v2-tip{font-size:12px;color:var(--ink-soft);margin:7px 0}.v2-timer{font:600 28px 'IBM Plex Mono',monospace;color:var(--forest);letter-spacing:-1px}
      .v2-exercise-guide{display:grid;grid-template-columns:120px minmax(0,1fr);gap:14px;align-items:start;margin:12px 0;padding:12px;border:1px solid var(--line);border-radius:8px;background:var(--forest-dim)}.v2-exercise-guide ol{margin:7px 0 0;padding-left:20px;font-size:13px}.v2-exercise-guide li+li{margin-top:5px}.v2-exercise-visual{margin:0;text-align:center}.v2-exercise-visual svg{display:block;width:100%;max-width:112px;aspect-ratio:1;border-radius:8px;background:#fff;stroke:var(--forest);stroke-width:4;stroke-linecap:round;stroke-linejoin:round;fill:none}.v2-exercise-visual svg circle{fill:#fff}.v2-exercise-visual .v2-ground{stroke:var(--line);stroke-width:2}.v2-exercise-visual .v2-apparatus{stroke:var(--ink-soft);stroke-width:3}.v2-exercise-visual figcaption{font-size:10px;color:var(--ink-faint);margin-top:4px}.v2-programme-task{align-items:flex-start}.v2-programme-task>.v2-check{padding-top:12px}.v2-programme-session{border:1px solid var(--line);border-radius:8px;padding:12px;margin:12px 0}.v2-programme-progress{font-weight:600;color:var(--forest)}
      nav[role=tablist]{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;overflow:visible;border:0;margin-bottom:22px}nav[role=tablist] .v2-tab{min-width:0;min-height:42px;white-space:normal;margin:0;padding:8px 7px;border:1px solid var(--line);border-radius:8px;background:var(--card);line-height:1.2}nav[role=tablist] .v2-tab[aria-selected=true]{color:var(--forest);border-color:var(--forest);background:var(--forest-dim)}
      .v2-check{display:flex;gap:8px;align-items:center;font-size:13px;margin:0}.v2-check input{width:18px;height:18px}.v2-toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);z-index:20;background:#20352a;color:#fff;border-radius:8px;padding:10px 14px;font-size:13px;box-shadow:0 4px 18px #0003}.v2-toast button{margin-left:10px;border:0;background:transparent;color:#fff;text-decoration:underline;cursor:pointer}.v2-muted{color:var(--ink-faint);font-size:13px}.v2-summary{font-size:13px;background:var(--forest-dim);border-radius:7px;padding:9px}.v2-chip{border:1px solid var(--line);border-radius:14px;padding:4px 9px;font-size:12px;background:#fff}
      #tab-dashboard input:not([type=checkbox]),#tab-dashboard select,#tab-routines input:not([type=checkbox]),#tab-workout input:not([type=checkbox]),#tab-review input:not([type=checkbox]),#tab-diet input:not([type=checkbox]),#tab-foods input:not([type=checkbox]),#tab-programme input:not([type=checkbox]),#tab-routines textarea,#tab-workout textarea,#tab-review textarea,#tab-diet textarea,#tab-foods textarea,#tab-programme textarea,#tab-routines select,#tab-workout select,#tab-review select,#tab-diet select,#tab-foods select,#tab-programme select{width:100%;font-family:'IBM Plex Mono',monospace;font-size:14px;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:#fff;color:var(--ink)}
      #tab-routines textarea,#tab-workout textarea,#tab-review textarea,#tab-diet textarea,#tab-foods textarea,#tab-programme textarea{font-family:'Work Sans',sans-serif}.v2-routine-form{display:flex;flex-direction:column;gap:14px}.v2-field{display:flex;flex-direction:column;gap:5px}.v2-field label{margin:0}.v2-library{max-height:255px;overflow:auto;border:1px solid var(--line);border-radius:8px;padding:8px 10px;background:#fff}.v2-library label{display:flex;align-items:center;gap:8px;padding:8px 4px;margin:0;font-size:13px}.v2-custom-row{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}.v2-custom-row input{flex:1;min-width:200px}.v2-session-head{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.v2-progress{font-size:12px;color:var(--ink-soft)}.v2-reminder-copy{display:flex;flex-direction:column;gap:2px}.v2-data-actions{align-items:center}.v2-food-filter{margin-bottom:4px}.v2-food-filter input,.v2-food-filter select{width:auto!important;flex:1;min-width:180px}
      .v2-macro-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.v2-macro{background:#fff;border:1px solid var(--line);border-radius:8px;padding:9px 10px}.v2-macro strong{display:block;font:500 17px 'IBM Plex Mono',monospace}.v2-macro span{display:block;font-size:10px;color:var(--ink-faint);text-transform:uppercase;letter-spacing:.04em}.v2-diet-section{margin-top:16px}.v2-diet-section h3{font-family:'Fraunces',serif;font-size:16px;font-weight:500;margin:0 0 4px}.v2-diet-row{display:grid;grid-template-columns:26px minmax(0,1fr) 76px 70px;gap:8px;align-items:center;padding:9px 0;border-bottom:1px solid var(--line)}.v2-diet-row:last-child{border-bottom:0}.v2-diet-row input[type=checkbox]{width:18px;height:18px}.v2-serving-select{grid-column:2 / -1}.v2-diet-macros{grid-column:2 / -1;min-width:0;font:12px/1.45 'IBM Plex Mono',monospace;color:var(--ink-soft);overflow-wrap:anywhere}.v2-constant-row{grid-template-columns:26px minmax(0,1fr) auto}.v2-diet-actions{display:flex;gap:6px;justify-content:flex-end;flex-wrap:wrap}.v2-btn.compact{min-height:30px;padding:5px 8px;font-size:12px}.v2-diet-note{font-size:12px;color:var(--ink-faint);margin:0 0 10px}.v2-diet-history{margin-top:14px}.v2-library-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)}.v2-library-row:last-child{border-bottom:0}.v2-recipe-row{display:grid;grid-template-columns:minmax(0,1fr) 100px auto;gap:8px;align-items:center;margin:8px 0}.v2-bar-chart{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:7px;align-items:end;height:150px;padding:12px 0 24px}.v2-bar{min-height:2px;background:var(--forest);border-radius:5px 5px 0 0;position:relative}.v2-bar span{position:absolute;bottom:-21px;left:50%;transform:translateX(-50%);font-size:9px;color:var(--ink-faint);white-space:nowrap}.v2-pr-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.v2-pr{border:1px solid var(--line);border-radius:8px;padding:10px;background:#fff}.v2-routine-program{border:1px solid var(--line);border-radius:8px;padding:12px;background:#fff}.v2-routine-program[draggable=true]{cursor:grab}.v2-routine-program.dragging{opacity:.45}.v2-routine-program-head{display:flex;gap:10px;align-items:center;justify-content:space-between;margin-bottom:10px}.v2-routine-program-head strong{overflow-wrap:anywhere}.v2-group-fields{padding:10px;margin-top:10px;background:var(--forest-dim);border-radius:8px}.v2-workout-group{border:2px solid #b8c9bf;border-radius:10px;padding:0 12px 4px;margin:16px 0;background:var(--forest-dim)}.v2-workout-group>.v2-group-head{padding:12px 2px 0}.v2-workout-group .v2-exercise{margin:10px 0}.v2-chain{display:flex;gap:6px;flex-wrap:wrap;margin-top:7px}.v2-substitute{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;margin:10px 0}.v2-badge{display:inline-block;border-radius:12px;padding:3px 8px;background:var(--forest-dim);color:var(--forest);font-size:11px;font-weight:600}
      .v2-diet-balance{position:sticky;top:8px;z-index:8;box-shadow:0 6px 20px #20352a18}.v2-diet-balance .v2-macro strong{font-size:15px}#tab-diet .card{scroll-margin-top:160px}.v2-food-shortcuts{display:flex;gap:7px;flex-wrap:wrap}.v2-food-shortcuts .v2-btn{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.v2-profile{border-top:1px solid var(--line);padding-top:12px;margin-top:12px}.v2-week-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:7px}.v2-week-grid .v2-field{min-width:0}.v2-record-summary{margin-bottom:14px}.v2-programme-stage{padding:10px 0;border-bottom:1px solid var(--line)}.v2-programme-stage.current{background:var(--forest-dim);border-radius:8px;padding:10px}.v2-programme-stage:last-child{border-bottom:0}.v2-programme-stage strong{display:block}.v2-programme-skill summary{cursor:pointer;font-family:'Fraunces',serif;font-size:17px;padding:8px 0}.v2-programme-skill[open] summary{margin-bottom:6px}.v2-session-check{align-items:flex-start}.v2-session-check input{margin-top:2px}.v2-warning{border-left:4px solid #c28b2c;padding-left:12px}.v2-workout-controls{position:sticky;top:5px;z-index:10;box-shadow:0 7px 22px #20352a24}.v2-control-strip{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}.v2-control-strip .v2-toolbar{margin:4px 0}.v2-save-status{font:12px 'IBM Plex Mono',monospace;color:var(--ink-faint)}.v2-save-status.saving{color:#9a6c12}.v2-save-status.error{color:var(--danger)}.v2-workout-details{margin:10px 0}.v2-workout-details summary{cursor:pointer;color:var(--forest);font-weight:600;font-size:13px;padding:7px 0}.v2-workout-compact .v2-workout-details:not([open]){margin:2px 0}.v2-quick-notes{margin:10px 0;padding:10px;background:var(--forest-dim);border-radius:8px}.v2-round-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:9px}.v2-manage-exercises{margin-top:10px;border-top:1px solid var(--line);padding-top:9px}.v2-manage-exercises summary{cursor:pointer;font-weight:600;color:var(--forest)}.v2-manage-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;margin-top:9px}.v2-exercise-position{font:11px 'IBM Plex Mono',monospace;color:var(--ink-faint)}
      .v2-training-week{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px}.v2-training-day{border:1px solid var(--line);border-radius:8px;padding:9px;background:#fff;min-width:0}.v2-training-day.today{border-color:var(--forest);background:var(--forest-dim)}.v2-training-day>strong{display:block;margin-bottom:7px}.v2-calendar-item{border-top:1px solid var(--line);padding:7px 0}.v2-calendar-item:first-of-type{border-top:0}.v2-calendar-item .v2-actions{margin-top:6px}.v2-status{display:inline-block;border-radius:12px;padding:2px 7px;font-size:10px;font-weight:600;background:var(--card);color:var(--ink-soft)}.v2-status.completed{background:#dcecdf;color:var(--forest)}.v2-status.missed{background:#f7e3df;color:var(--danger)}.v2-status.moved{background:#fff0ca;color:#845f13}.v2-progression-box{border-left:4px solid var(--forest);background:var(--forest-dim);padding:9px 11px;margin:10px 0;border-radius:0 8px 8px 0}.v2-progression-box.warning{border-left-color:#c28b2c;background:#fff8e7}.v2-progression-box strong{display:block}.v2-mini-chart{display:flex;align-items:flex-end;gap:6px;height:92px;padding:8px 0 20px}.v2-mini-bar{flex:1;min-width:12px;max-width:45px;background:var(--forest);border-radius:4px 4px 0 0;position:relative}.v2-mini-bar span{position:absolute;bottom:-17px;left:50%;transform:translateX(-50%);font-size:8px;color:var(--ink-faint);white-space:nowrap}.v2-summary-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.v2-session-summary{border:1px solid var(--line);border-radius:8px;padding:12px;background:var(--forest-dim)}.v2-plate-result{font:13px/1.5 'IBM Plex Mono',monospace;background:#fff;border:1px solid var(--line);border-radius:7px;padding:9px;overflow-wrap:anywhere}.v2-routine-history summary,.v2-exercise-history summary,.v2-load-tools summary{cursor:pointer;color:var(--forest);font-weight:600;font-size:13px;padding:7px 0}.v2-day-checks{display:flex;gap:8px;flex-wrap:wrap}.v2-day-checks .v2-check{border:1px solid var(--line);border-radius:7px;padding:7px 9px;background:#fff}
      .v2-goal{border:1px solid var(--line);border-radius:8px;padding:11px;margin:10px 0;background:#fff}.v2-goal-head{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;flex-wrap:wrap}.v2-goal-progress{height:10px;border-radius:999px;background:var(--card);overflow:hidden;margin:9px 0}.v2-goal-progress>span{display:block;height:100%;background:var(--forest);border-radius:inherit}.v2-goal.achieved .v2-goal-progress>span{background:#4f8b61}.v2-dashboard-signal{padding:8px 0;border-bottom:1px solid var(--line);font-size:13px}.v2-dashboard-signal:last-child{border-bottom:0}
      .v2-hiit{border-color:#b8c9bf}.v2-hiit-display{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:14px;align-items:center;background:var(--forest-dim);border-radius:10px;padding:14px;margin:12px 0}.v2-hiit-phase{font:600 18px 'Work Sans',sans-serif;color:var(--forest)}.v2-hiit-clock{font:600 46px 'IBM Plex Mono',monospace;color:var(--forest);line-height:1}.v2-hiit-round{font:12px 'IBM Plex Mono',monospace;color:var(--ink-faint);margin-top:4px}.v2-hiit-progress{height:10px;border-radius:999px;background:#fff;overflow:hidden;margin-top:10px}.v2-hiit-progress>span{display:block;height:100%;background:var(--forest);border-radius:inherit;transition:width .2s linear}.v2-hiit-presets{display:flex;gap:7px;flex-wrap:wrap}.v2-hiit.running .v2-hiit-display{box-shadow:inset 4px 0 0 var(--forest)}.v2-hiit.rest .v2-hiit-display{background:#fff4d6}.v2-hiit.complete .v2-hiit-display{background:#dcecdf}
      @media(max-width:700px){.v2-week-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
      @media(max-width:900px){.v2-training-week{grid-template-columns:repeat(2,minmax(0,1fr))}}
      @media(max-width:560px){nav[role=tablist]{grid-template-columns:repeat(2,minmax(0,1fr));gap:5px}nav[role=tablist] .v2-tab{font-size:12px;padding:8px 5px}.v2-grid{grid-template-columns:1fr}.v2-set{grid-template-columns:26px 68px minmax(0,1fr) minmax(0,1fr) 54px 68px;gap:4px;font-size:12px}.v2-set select{padding-left:4px;padding-right:2px}.v2-set-actions{gap:2px}.v2-set-actions .v2-btn{min-height:38px;min-width:31px;padding:4px}.v2-btn{min-height:42px}.v2-timer{font-size:24px}.v2-hiit-display{grid-template-columns:1fr;text-align:center}.v2-hiit-clock{font-size:40px}.v2-row .grow{min-width:0}.v2-actions{width:100%}.v2-actions .v2-btn{flex:1}.v2-custom-row{align-items:stretch}.v2-custom-row input{min-width:0;flex-basis:100%}.v2-macro-grid,.v2-summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.v2-diet-row{grid-template-columns:24px minmax(0,1fr) 68px 62px;gap:6px}.v2-constant-row{grid-template-columns:24px minmax(0,1fr)}.v2-constant-row .v2-diet-actions{grid-column:2 / -1;justify-content:flex-start}.v2-library-row{grid-template-columns:1fr}.v2-library-row .v2-actions{width:auto}.v2-diet-balance{top:4px}.v2-week-grid,.v2-training-week{grid-template-columns:1fr}.v2-exercise-guide{grid-template-columns:1fr}.v2-exercise-visual svg{max-width:100px}.v2-recipe-row{grid-template-columns:minmax(0,1fr) 75px}.v2-recipe-row .v2-btn{grid-column:1/-1}.v2-pr-list{grid-template-columns:1fr}.v2-substitute{grid-template-columns:1fr}.v2-workout-group{padding:0 8px 3px}.v2-workout-controls{top:3px;padding:10px}.v2-control-strip{align-items:flex-start}.v2-manage-row{grid-template-columns:1fr}.v2-manage-row .v2-btn{width:100%}}
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
    const { live = false, ...attributes } = props; const control = el('input', { id, type, ...attributes }); control.value = value ?? ''; control.addEventListener(live ? 'input' : 'change', () => onChange(control.value)); field.append(control); return field;
  }

  function buildShell() {
    styles();
    const nav = $('nav'); clear(nav); nav.setAttribute('role', 'tablist');
    [['today', 'Today'], ['dashboard', 'Dashboard'], ['diet', 'Diet'], ['workout', 'Workout'], ['programme', 'Programme'], ['habits', 'Habits & Trends'], ['records', 'Records'], ['routines', 'Routines'], ['foods', 'Food library'], ['review', 'Review'], ['guide', 'Guide']].forEach(([id, label], index) => {
      const tab = el('button', { id: 'nav-' + id, class: 'v2-tab' + (index === 0 ? ' active' : ''), role: 'tab', 'aria-controls': 'tab-' + id, 'aria-selected': index === 0 ? 'true' : 'false', tabindex: index === 0 ? '0' : '-1', 'data-tab': id, text: label,
        onclick: () => selectTab(id) }); nav.append(tab);
    });
    const tabs = [...nav.querySelectorAll('.v2-tab')];
    tabs.forEach((tab, index) => tab.addEventListener('keydown', event => {
      const next = event.key === 'ArrowRight' ? (index + 1) % tabs.length : event.key === 'ArrowLeft' ? (index - 1 + tabs.length) % tabs.length : event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : null;
      if (next === null) return; event.preventDefault(); selectTab(tabs[next].dataset.tab); tabs[next].focus();
    }));
    ['today', 'trends', 'habits', 'guide', 'workouts'].forEach(id => {
      const section = $('#tab-' + id);
      if (!section) return;
      section.style.removeProperty('display');
      section.hidden = id !== 'today';
    });
    const dashboardPanel = el('div', { id: 'tab-dashboard', role: 'tabpanel', hidden: 'true' });
    const dietPanel = el('div', { id: 'tab-diet', role: 'tabpanel', hidden: 'true' });
    const foodsPanel = el('div', { id: 'tab-foods', role: 'tabpanel', hidden: 'true' });
    const routinePanel = el('div', { id: 'tab-routines', role: 'tabpanel', hidden: 'true' });
    const workoutPanel = el('div', { id: 'tab-workout', role: 'tabpanel', hidden: 'true' });
    const recordsPanel = el('div', { id: 'tab-records', role: 'tabpanel', hidden: 'true' });
    const programmePanel = el('div', { id: 'tab-programme', role: 'tabpanel', hidden: 'true' });
    const reviewPanel = el('div', { id: 'tab-review', role: 'tabpanel', hidden: 'true' });
    $('#tab-workouts').after(dashboardPanel, dietPanel, foodsPanel, routinePanel, workoutPanel, programmePanel, recordsPanel, reviewPanel);
    $('#tab-workouts').hidden = true;
    syncLegacyHealth();
    $('#summary-cards').hidden = true; $('#photo-reminder').hidden = true;
  }
  function selectTab(id) {
    ['today', 'dashboard', 'diet', 'foods', 'trends', 'habits', 'records', 'routines', 'workout', 'programme', 'review', 'guide', 'workouts'].forEach(name => { const panel = $('#tab-' + name); if (panel) panel.hidden = name !== id; });
    $('nav').querySelectorAll('button').forEach(btn => { const selected = btn.dataset.tab === id; btn.classList.toggle('active', selected); btn.setAttribute('aria-selected', String(selected)); btn.tabIndex = selected ? 0 : -1; });
    if (id === 'today') renderToday();
    if (id === 'dashboard') renderDashboard();
    if (id === 'workout') renderWorkout();
    if (id === 'diet') renderDiet();
    if (id === 'foods') renderFoods();
    if (id === 'habits') renderHabits();
    if (id === 'records') renderRecords();
    if (id === 'routines') renderRoutines();
    if (id === 'programme') renderProgramme();
    if (id === 'review') renderReview();
  }
  function syncLegacyHealth() {
    if (typeof DATA !== 'undefined') DATA = state.health;
  }
  function render() { renderToday(); renderDashboard(); renderDiet(); renderFoods(); renderHabits(); renderRoutines(); renderWorkout(); renderProgramme(); renderRecords(); renderReview(); }

  function renderToday() {
    const panel = clear($('#tab-today')); const entries = state.health.entries; const currentDate = panel.dataset.editDate || isoToday(); const current = entries[currentDate] || {};
    const snapshot = todaySnapshotCard(currentDate); if (snapshot) panel.append(snapshot, todayTrainingCard(currentDate), trainingCalendarCard(currentDate));
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
  const TRAINING_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  function datePlus(date, days) { const value = new Date(date + 'T12:00:00'); value.setDate(value.getDate() + days); return value.toISOString().slice(0, 10); }
  function trainingDayIndex(date) { const day = new Date(date + 'T12:00:00').getDay(); return day === 0 ? 6 : day - 1; }
  function scheduledPlans(date, includeMovedOut = false) {
    const overrides = state.routines.scheduleOverrides || {}; const plans = [];
    state.routines.items.forEach(routine => {
      if (!(routine.scheduleDays || []).includes(trainingDayIndex(date))) return;
      const key = `${date}|${routine.id}`; const movedTo = overrides[key];
      if (movedTo) { if (includeMovedOut) plans.push({ routine, date, sourceDate: date, movedOut: true, movedTo, key }); }
      else plans.push({ routine, date, sourceDate: date, key });
    });
    Object.entries(overrides).forEach(([key, movedTo]) => { if (movedTo !== date) return; const [sourceDate, routineId] = key.split('|'); const routine = state.routines.items.find(item => item.id === routineId); if (routine) plans.push({ routine, date, sourceDate, movedIn: true, key }); });
    return plans;
  }
  function sessionForPlan(plan) { return state.workouts.sessions.find(session => session.routineId === plan.routine.id && (session.scheduledDate === plan.sourceDate || (!session.scheduledDate && session.date === plan.date))); }
  function activeForPlan(plan) { return state.active?.routineId === plan.routine.id && (state.active.scheduledDate === plan.sourceDate || (!state.active.scheduledDate && state.active.date === plan.date)); }
  function planStatus(plan) { if (plan.movedOut) return 'moved'; if (sessionForPlan(plan)) return 'completed'; if (activeForPlan(plan)) return 'active'; if (plan.date < isoToday()) return 'missed'; if (plan.date === isoToday()) return 'due'; return 'upcoming'; }
  async function moveScheduledWorkout(plan) { const next = prompt(`Move ${plan.routine.name} from ${plan.sourceDate} to which date?`, plan.date); if (!next) return; if (!/^\d{4}-\d{2}-\d{2}$/.test(next) || Number.isNaN(Date.parse(next + 'T12:00:00'))) return toast('Enter a valid date in YYYY-MM-DD format.'); state.routines.scheduleOverrides[`${plan.sourceDate}|${plan.routine.id}`] = next; try { await save('routines'); renderToday(); toast(`Workout moved to ${next}.`); } catch (error) { toast(error.message); } }
  async function resetScheduledMove(plan) { delete state.routines.scheduleOverrides[`${plan.sourceDate}|${plan.routine.id}`]; try { await save('routines'); renderToday(); toast('Workout returned to its regular date.'); } catch (error) { toast(error.message); } }
  function todayTrainingCard(date) {
    const plans = scheduledPlans(date); const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Planned training' }));
    const signals = currentReadinessSignals(); if (signals.length) card.append(el('div', { class: 'v2-summary v2-warning' }, signals.map(signal => el('div', { text: '• ' + signal }))));
    if (!plans.length) { card.append(el('p', { class: 'v2-muted', text: 'No routine is scheduled today. Assign weekdays in the Routines tab or start any routine manually.' }), button('Open routines', () => selectTab('routines'))); return card; }
    plans.forEach(plan => { const status = planStatus(plan); const actions = []; if (status === 'active') actions.push(button('Resume', () => selectTab('workout'), 'primary compact')); else if (status === 'completed') actions.push(button('View record', () => { state.recordsFilters.routine = plan.routine.name; selectTab('records'); }, 'compact')); else actions.push(button(status === 'missed' ? 'Start catch-up' : status === 'upcoming' ? 'Start early' : 'Start workout', () => startRoutine(plan.routine.id, null, plan), 'primary compact')); actions.push(button('Move', () => moveScheduledWorkout(plan), 'compact')); card.append(el('div', { class: 'v2-row' }, [el('div', { class: 'grow' }, [el('strong', { text: plan.routine.name }), el('div', { class: `v2-status ${status}`, text: status === 'due' ? 'Due today' : status })]), el('div', { class: 'v2-actions' }, actions)])); }); return card;
  }
  function trainingCalendarCard(anchorDate = isoToday()) {
    const start = mondayOf(anchorDate); const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Training week' }), el('p', { class: 'v2-muted', text: 'Completed, active, missed, moved and upcoming routine sessions. Moving one occurrence does not change the routine’s normal weekday schedule.' })); const week = el('div', { class: 'v2-training-week' });
    for (let offset = 0; offset < 7; offset++) { const date = datePlus(start, offset); const day = el('section', { class: 'v2-training-day' + (date === isoToday() ? ' today' : '') }); day.append(el('strong', { text: `${TRAINING_DAYS[offset]} ${date.slice(8)}` })); const plans = scheduledPlans(date, true); if (!plans.length) day.append(el('span', { class: 'v2-meta', text: 'Rest / unscheduled' })); plans.forEach(plan => { const status = planStatus(plan); const item = el('div', { class: 'v2-calendar-item' }); item.append(el('div', { text: plan.routine.name }), el('span', { class: `v2-status ${status}`, text: plan.movedOut ? `Moved to ${plan.movedTo}` : plan.movedIn ? `Moved from ${plan.sourceDate.slice(5)}` : status })); const actions = el('div', { class: 'v2-actions' }); if (plan.movedOut) actions.append(button('Reset', () => resetScheduledMove(plan), 'compact')); else { if (status === 'active') actions.append(button('Resume', () => selectTab('workout'), 'compact')); else if (status !== 'completed') actions.append(button('Start', () => startRoutine(plan.routine.id, null, plan), 'compact')); actions.append(button('Move', () => moveScheduledWorkout(plan), 'compact')); if (plan.movedIn) actions.append(button('Reset', () => resetScheduledMove(plan), 'compact')); } item.append(actions); day.append(item); }); week.append(day); }
    card.append(week); return card;
  }
  function weekDates(anchor = isoToday()) { const start = mondayOf(anchor); return Array.from({ length: 7 }, (_, index) => datePlus(start, index)); }
  function validAverage(items, getter) { const values = items.map(getter).map(Number).filter(value => Number.isFinite(value) && value > 0); return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null; }
  function weeklyDashboardCard() {
    const dates = weekDates(); const priorDates = dates.map(date => datePlus(date, -7)); const dietDates = dates.filter(date => state.diet.days[date]?.updatedAt); const health = dates.map(date => state.health.entries[date]).filter(Boolean); const sessions = state.workouts.sessions.filter(session => dates.includes(session.date)); const previousHealth = priorDates.map(date => state.health.entries[date]).filter(Boolean);
    const caloriesOnTarget = dietDates.filter(date => { const calories = dietTotals(state.diet.days[date]).total.calories; const target = Number(targetProfileForDate(date).calories); return target > 0 && Math.abs(calories - target) / target <= .1; }).length; const proteinTarget = dietDates.filter(date => dietTotals(state.diet.days[date]).total.protein >= Number(targetProfileForDate(date).protein || 0)).length;
    const planned = dates.flatMap(date => scheduledPlans(date, true).filter(plan => !plan.movedOut)).length; const metrics = sessions.map(workoutMetrics); const completedSets = metrics.reduce((sum, item) => sum + item.completedSets, 0); const work = metrics.reduce((sum, item) => sum + item.work, 0); const sleep = validAverage(health, item => item.sleepHours); const weight = validAverage(health, item => item.weight); const priorWeight = validAverage(previousHealth, item => item.weight); const habitChecks = health.reduce((sum, entry) => sum + HABITS.filter(([key]) => entry[key] === true).length, 0); const possibleHabits = health.length * HABITS.length;
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: `Week of ${dates[0]}` }), el('p', { class: 'v2-muted', text: 'A concise status view built only from recorded data. Missing entries stay missing rather than being counted as zero.' })); const grid = el('div', { class: 'v2-macro-grid' });
    [['Diet logged', `${dietDates.length}/7`, `${caloriesOnTarget} calorie days within ±10%`], ['Protein target', `${proteinTarget}/${dietDates.length || 0}`, 'Saved diet days'], ['Training', planned ? `${sessions.length}/${planned}` : `${sessions.length} done`, `${planned} planned · ${completedSets} sets · ${Math.round(work)} reps/seconds`], ['Average sleep', sleep === null ? '—' : `${sleep.toFixed(1)} h`, `${health.length} daily entries`], ['Weight trend', weight === null ? '—' : `${weight.toFixed(1)} kg`, priorWeight === null || weight === null ? 'No prior-week comparison' : `${weight - priorWeight >= 0 ? '+' : ''}${(weight - priorWeight).toFixed(1)} kg vs prior week`], ['Habits', possibleHabits ? `${Math.round(habitChecks / possibleHabits * 100)}%` : '—', `${habitChecks}/${possibleHabits} checks on logged days`]].forEach(([label, value, note]) => grid.append(el('div', { class: 'v2-macro' }, [el('span', { text: label }), el('strong', { text: value }), el('span', { text: note })]))); card.append(grid); return card;
  }
  function dashboardRecoveryCard() {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Recovery and progression signals' })); const signals = currentReadinessSignals(); const recent = state.workouts.sessions.slice().sort(byDate).slice(-3); const failed = recent.flatMap(session => session.exercises || []).filter(exercise => exercise.quickNotes?.failed).length; const poorForm = recent.flatMap(session => session.exercises || []).filter(exercise => exercise.formQuality === 'needs-work').length; const highEffort = recent.flatMap(session => session.exercises || []).filter(exercise => { const value = exercisePerformance(exercise).avgRpe; return value !== null && value >= 9.5; }).length; if (failed >= 2) signals.push(`${failed} failed or shortened exercise entries appear across the last three workouts.`); if (poorForm >= 3) signals.push(`${poorForm} exercise entries were rated “Needs work” across the last three workouts.`); if (highEffort >= 3) signals.push(`${highEffort} exercise entries averaged RPE 9.5 or higher across the last three workouts.`); if (!signals.length) signals.push('No automatic recovery flag from the currently recorded sleep, soreness, discomfort, failure, form or RPE data.'); signals.forEach(signal => card.append(el('div', { class: 'v2-dashboard-signal', text: signal }))); card.append(el('p', { class: 'v2-muted', text: 'These are prompts for judgement, not medical advice or an automatic instruction to progress.' })); return card;
  }
  function goalReference(goal) { return state.library.items.find(item => item.id === goal.exerciseId) || goal.name || 'Unknown exercise'; }
  function goalMetricValue(exercise, metric) { const performance = exercisePerformance(exercise); return metric === 'load' ? performance.maxLoad || 0 : performance.best || 0; }
  function goalProgressSeries(goal) { let best = 0; const points = []; exerciseSessionHistory(goalReference(goal)).forEach(({ session, exercise }) => { const value = goalMetricValue(exercise, goal.metric); if (value > best) { best = value; points.push({ date: session.date, value }); } }); return points; }
  function exerciseGoalCard(goal) { const reference = goalReference(goal); const identity = canonicalExerciseIdentity(reference); const points = goalProgressSeries(goal); const current = points.at(-1)?.value || 0; const target = Number(goal.target) || 1; const achieved = current >= target; const unit = goal.metric === 'load' ? 'kg external load' : goal.metric; const wrapper = el('div', { class: 'v2-goal' + (achieved ? ' achieved' : '') }); const head = el('div', { class: 'v2-goal-head' }, [el('div', {}, [el('strong', { text: identity.name }), el('div', { class: 'v2-meta', text: `${goal.metric === 'load' ? 'External load' : goal.metric === 'seconds' ? 'Hold duration' : 'Repetitions'} goal · ${current} / ${target} ${unit}` })]), el('span', { class: 'v2-status ' + (achieved ? 'completed' : ''), text: achieved ? 'Achieved' : `${Math.min(100, Math.round(current / target * 100))}%` })]); const progress = el('div', { class: 'v2-goal-progress', role: 'progressbar', 'aria-label': `${identity.name} goal progress`, 'aria-valuemin': '0', 'aria-valuemax': String(target), 'aria-valuenow': String(Math.min(current, target)) }, [el('span', { style: `width:${Math.min(100, current / target * 100)}%` })]); const remaining = Math.max(0, target - current); wrapper.append(head, progress, el('div', { class: 'v2-meta', text: achieved ? `Target reached on ${points.find(point => point.value >= target)?.date || 'a recorded session'}. Maintain it or set a new target.` : current ? `${remaining} ${unit} remaining. Repeat clean performance before increasing difficulty.` : 'No reconciled performance recorded yet. The first matching session will establish the baseline.' })); if (points.length) wrapper.append(el('div', { class: 'v2-meta', text: 'Milestones: ' + points.slice(-5).map(point => `${point.date.slice(5)} · ${point.value}`).join(' → ') })); wrapper.append(el('div', { class: 'v2-toolbar' }, [button('Edit', () => { state.editExerciseGoal = goal.id; renderDashboard(); }, 'compact'), button('Archive', async () => { const previous = goal.archived; goal.archived = true; try { await save('settings'); renderDashboard(); toast('Exercise goal archived.'); } catch (error) { goal.archived = previous; toast(error.message); } }, 'compact danger')])); return wrapper;
  }
  function exerciseGoalsCard() {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Exercise goals' }), el('p', { class: 'v2-muted', text: 'Targets use reconciled exercise history, including records saved under an earlier name.' })); const editing = state.settings.exerciseGoals.find(goal => goal.id === state.editExerciseGoal); const form = el('form'); const exercise = el('select', { name: 'exercise', 'aria-label': 'Goal exercise' }); state.library.items.filter(item => !item.archived).slice().sort((a, b) => a.name.localeCompare(b.name)).forEach(item => exercise.append(el('option', { value: item.id, text: item.name }))); exercise.value = editing?.exerciseId || exercise.value; const metric = el('select', { name: 'metric', 'aria-label': 'Goal metric' }, [el('option', { value: 'reps', text: 'Repetitions' }), el('option', { value: 'seconds', text: 'Hold seconds' }), el('option', { value: 'load', text: 'External load (kg)' })]); metric.value = editing?.metric || (state.library.items.find(item => item.id === exercise.value)?.target?.unit === 'seconds' ? 'seconds' : 'reps'); const target = el('input', { type: 'number', name: 'target', min: '0.1', max: '10000', step: '0.1', required: 'true', 'aria-label': 'Goal target' }); target.value = editing?.target || ''; exercise.addEventListener('change', () => { metric.value = state.library.items.find(item => item.id === exercise.value)?.target?.unit === 'seconds' ? 'seconds' : 'reps'; }); const submit = button(editing ? 'Save goal changes' : 'Add exercise goal', null, 'primary'); submit.type = 'submit'; const actions = [submit]; if (editing) actions.push(button('Cancel', () => { state.editExerciseGoal = null; renderDashboard(); })); form.append(el('div', { class: 'v2-grid' }, [el('div', { class: 'v2-field' }, [el('label', { text: 'Exercise' }), exercise]), el('div', { class: 'v2-field' }, [el('label', { text: 'Measure' }), metric]), el('div', { class: 'v2-field' }, [el('label', { text: 'Target' }), target])]), el('div', { class: 'v2-toolbar' }, actions)); form.addEventListener('submit', async event => { event.preventDefault(); const selected = state.library.items.find(item => item.id === exercise.value); const value = Number(target.value); if (!selected || !Number.isFinite(value) || value <= 0) return toast('Choose an exercise and enter a positive target.'); const duplicate = state.settings.exerciseGoals.find(goal => !goal.archived && goal.id !== editing?.id && canonicalExerciseIdentity(goalReference(goal)).key === canonicalExerciseIdentity(selected).key && goal.metric === metric.value); if (duplicate) return toast('An active goal already exists for that exercise and measure.'); const previous = clone(state.settings.exerciseGoals); const next = { id: editing?.id || 'exercise-goal-' + Date.now(), exerciseId: selected.id, name: selected.name, metric: metric.value, target: value, archived: false, createdAt: editing?.createdAt || new Date().toISOString(), updatedAt: new Date().toISOString() }; if (editing) state.settings.exerciseGoals[state.settings.exerciseGoals.findIndex(goal => goal.id === editing.id)] = next; else state.settings.exerciseGoals.push(next); try { await save('settings'); state.editExerciseGoal = null; renderDashboard(); toast(editing ? 'Exercise goal updated.' : 'Exercise goal added.'); } catch (error) { state.settings.exerciseGoals = previous; toast(error.message); } }); card.append(form); const active = state.settings.exerciseGoals.filter(goal => !goal.archived); if (!active.length) card.append(el('p', { class: 'v2-muted', text: 'No active exercise goals yet.' })); active.forEach(goal => card.append(exerciseGoalCard(goal))); const archived = state.settings.exerciseGoals.filter(goal => goal.archived); if (archived.length) { const details = el('details'); details.append(el('summary', { text: `Archived goals (${archived.length})` })); archived.forEach(goal => details.append(el('div', { class: 'v2-row' }, [el('span', { class: 'grow', text: `${canonicalExerciseIdentity(goalReference(goal)).name} · ${goal.target} ${goal.metric}` }), button('Restore', async () => { goal.archived = false; try { await save('settings'); renderDashboard(); toast('Exercise goal restored.'); } catch (error) { goal.archived = true; toast(error.message); } }, 'compact')]))); card.append(details); } return card;
  }
  function renderDashboard() { const panel = clear($('#tab-dashboard')); panel.append(el('div', { class: 'card' }, [el('h2', { text: 'Weekly dashboard' }), el('p', { class: 'v2-muted', text: 'Diet adherence, training, recovery and exercise targets in one place.' })]), weeklyDashboardCard(), dashboardRecoveryCard(), trainingCalendarCard(), exerciseGoalsCard()); }
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
  function foodBasis(food) { return food?.basis === '100ml' ? '100ml' : '100g'; }
  function foodUnit(food) { return foodBasis(food) === '100ml' ? 'ml' : 'g'; }
  function snapshotFood(food) { return { id: food.id, name: food.name, calories: Number(food.calories) || 0, protein: Number(food.protein) || 0, carbs: Number(food.carbs) || 0, fat: Number(food.fat) || 0, basis: foodBasis(food), servings: clone(food.servings || []) }; }
  function foodByName(name, includeArchived = false) {
    const query = String(name || '').trim().toLowerCase();
    return state.foods.items.find(food => (includeArchived || !food.archived) && (food.name.toLowerCase() === query || (food.aliases || []).some(alias => alias.toLowerCase() === query)));
  }
  function foodSearchText(food) { return [food.name, ...(food.aliases || [])].join(' ').toLowerCase(); }
  function parseServings(value) {
    return String(value || '').split('\n').map(line => line.trim()).filter(Boolean).map((line, index) => {
      const match = line.match(/^(.+?)\s*=\s*(\d+(?:\.\d+)?)\s*(?:g|ml)?$/i);
      return match ? { id: 'serving-' + index + '-' + slug(match[1]), label: match[1].trim(), amount: Number(match[2]) } : null;
    }).filter(item => item && item.amount > 0);
  }
  function foodForEntry(entry) { const live = state.foods.items.find(food => food.id === entry.foodId) || foodByName(entry.name, true); return entry.foodSnapshot ? { ...entry.foodSnapshot, servings: clone(live?.servings || entry.foodSnapshot.servings || []) } : live; }
  function recentFoods(limit = 8) {
    const found = []; const seen = new Set();
    Object.entries(state.diet.days).sort((a, b) => b[0].localeCompare(a[0])).forEach(([, day]) => {
      Object.values(day.meals || {}).flat().forEach(entry => {
        const food = state.foods.items.find(item => !item.archived && item.id === entry.foodId) || foodByName(entry.name);
        if (food && !seen.has(food.id)) { seen.add(food.id); found.push(food); }
      });
    });
    return found.slice(0, limit);
  }
  function recentFoodsForSection(sectionId, limit = 6) {
    const found = []; const seen = new Set(); Object.entries(state.diet.days).sort((a, b) => b[0].localeCompare(a[0])).forEach(([, day]) => { (day.meals?.[sectionId] || []).forEach(entry => { const food = state.foods.items.find(item => !item.archived && item.id === entry.foodId) || foodByName(entry.name); if (food && !seen.has(food.id)) { seen.add(food.id); found.push(food); } }); }); return found.slice(0, limit);
  }
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
  function targetProfileForDate(date) {
    const dayIndex = new Date((date || isoToday()) + 'T12:00:00').getDay();
    const profileId = state.dietSettings.targetSchedule?.[dayIndex] || 'standard';
    const profile = state.dietSettings.targetProfiles?.[profileId] || { label: 'Standard', ...state.dietSettings.targets };
    return { id: profileId, ...profile };
  }
  function renderDietSummary(container, day, date = $('#tab-diet')?.dataset.dietDate || isoToday()) {
    const { total, completed, trackable } = dietTotals(day); const targets = targetProfileForDate(date);
    clear(container);
    const grid = el('div', { class: 'v2-macro-grid' });
    [['Calories', total.calories, targets.calories, 'kcal'], ['Protein', total.protein, targets.protein, 'g'], ['Carbs', total.carbs, targets.carbs, 'g'], ['Fat', total.fat, targets.fat, 'g']].forEach(([label, value, target, unit]) => {
      const remaining = Number(target) - value; const hasTarget = Number(target) > 0;
      grid.append(el('div', { class: 'v2-macro' }, [el('span', { text: label + ' consumed' }), el('strong', { text: hasTarget ? `${Math.round(value)} / ${Math.round(target)}${unit}` : `${Math.round(value)}${unit}` }), hasTarget ? el('span', { text: remaining >= 0 ? `${Math.round(remaining)}${unit} remaining` : `${Math.abs(Math.round(remaining))}${unit} over` }) : el('span', { text: 'No target set' })]));
    });
    container.append(grid, el('p', { class: 'v2-diet-note', text: `${targets.label} targets · ${completed}/${trackable} entered items ticked and included.` }));
  }
  function renderDiet() {
    const panel = clear($('#tab-diet')); const date = panel.dataset.dietDate || isoToday(); const day = dietDay(date);
    const titleCard = el('div', { class: 'card' }); titleCard.append(el('h2', { text: 'Daily diet' }), el('p', { class: 'v2-muted', text: 'Tick constants and foods when taken/eaten. Totals include ticked entries only; food values use the 100g or 100ml basis shown in the library, so check brand labels.' }));
    const dateInput = el('input', { type: 'date', 'aria-label': 'Diet date' }); dateInput.value = date; dateInput.addEventListener('change', () => { panel.dataset.dietDate = dateInput.value; renderDiet(); });
    const copyYesterday = button('Copy previous diet', () => {
      const previous = Object.keys(state.diet.days).filter(item => item < date).sort().at(-1);
      if (!previous) return toast('No earlier diet entry to copy.');
      state.diet.days[date] = { ...clone(state.diet.days[previous]), createdAt: day.createdAt, updatedAt: null };
      renderDiet(); toast('Previous diet copied. Review it, then save.');
    });
    titleCard.append(el('div', { class: 'v2-toolbar' }, [dateInput, copyYesterday]));
    const summary = el('div', { class: 'card v2-diet-balance' }); renderDietSummary(summary, day, date); panel.append(titleCard, summary);
    const optionList = el('datalist', { id: 'diet-food-options' }); state.foods.items.filter(food => !food.archived).slice().sort((a, b) => a.name.localeCompare(b.name)).forEach(food => { optionList.append(el('option', { value: food.name })); (food.aliases || []).forEach(alias => optionList.append(el('option', { value: alias, label: food.name }))); }); panel.append(optionList);
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
    panel.append(foodShortcutsCard(day), constantsCard);
    mealSections().forEach(section => panel.append(dietMealCard(section.id, section.label, day, summary)));
    panel.append(dietTargetsCard(), mealSectionsCard(), addConstantCard(), savedMealsCard(day, summary));
    const actions = el('div', { class: 'card' });
    actions.append(el('h2', { text: 'Record this diet' }), el('p', { class: 'v2-muted', text: 'Save the selected date when you have checked what you actually ate/took.' }), button('Save daily diet', async () => { captureDietSnapshots(day); day.updatedAt = new Date().toISOString(); try { await save('diet'); renderDiet(); toast('Daily diet saved.'); } catch (error) { toast(error.message); } }, 'primary'));
    panel.append(actions);
  }
  function foodShortcutsCard(day) {
    const favourites = state.foods.items.filter(food => !food.archived && food.favourite).sort((a, b) => a.name.localeCompare(b.name));
    const favouriteIds = new Set(favourites.map(food => food.id)); const recents = recentFoods().filter(food => !favouriteIds.has(food.id));
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Quick add foods' }), el('p', { class: 'v2-diet-note', text: 'Add a favourite or recently used food, then enter the amount in its meal row.' }));
    const target = el('select', { 'aria-label': 'Meal section for quick-added food' }); mealSections().forEach(section => target.append(el('option', { value: section.id, text: section.label })));
    const add = food => {
      const rows = day.meals[target.value]; const entry = rows.find(row => !row.name) || (rows.push({ name: '', grams: '', checked: false }), rows.at(-1));
      Object.assign(entry, { foodId: food.id, foodSnapshot: snapshotFood(food), name: food.name, grams: '', checked: false }); renderDiet(); toast(`${food.name} added to ${target.options[target.selectedIndex].text}.`);
    };
    const shortcuts = el('div', { class: 'v2-food-shortcuts' });
    favourites.slice(0, 10).forEach(food => shortcuts.append(button('★ ' + food.name, () => add(food), 'compact')));
    recents.slice(0, 8).forEach(food => shortcuts.append(button(food.name, () => add(food), 'compact')));
    card.append(el('div', { class: 'v2-field' }, [el('label', { text: 'Add to meal' }), target]), shortcuts.children.length ? shortcuts : el('p', { class: 'v2-muted', text: 'No recent foods yet. Mark favourites in Food library or save a diet day.' }));
    return card;
  }
  function dietMealCard(id, label, day, summary) {
    const card = el('div', { class: 'card v2-diet-section' }); card.append(el('h3', { text: label }), el('p', { class: 'v2-diet-note', text: 'Choose a saved food and enter its edible/cooked weight in grams, or volume in ml for drinks recorded per 100ml.' }));
    const rows = el('div'); const refresh = () => renderDietSummary(summary, day);
    const renderRows = () => {
      clear(rows);
      day.meals[id].forEach((entry, index) => {
        const checked = el('input', { type: 'checkbox', 'aria-label': `Include ${label} item ${index + 1}` }); checked.checked = !!entry.checked;
        const food = el('input', { type: 'text', list: 'diet-food-options', placeholder: 'Food' }); food.value = entry.name || '';
        const grams = el('input', { type: 'number', min: '0', step: '1', placeholder: 'g', 'aria-label': `${label} item ${index + 1} amount` }); grams.value = entry.grams || '';
        const serving = el('select', { class: 'v2-serving-select', 'aria-label': `${label} item ${index + 1} serving preset` });
        const macros = el('span', { class: 'v2-diet-macros' });
        const updateServings = source => { clear(serving); serving.append(el('option', { value: '', text: 'Choose a serving preset' })); (source?.servings || []).forEach(item => serving.append(el('option', { value: String(item.amount), text: `${item.label} · ${item.amount}${foodUnit(source)}` }))); serving.hidden = !(source?.servings || []).length; };
        const update = () => { entry.checked = checked.checked; entry.name = food.value; entry.grams = grams.value; const found = foodByName(entry.name); if (found) { entry.foodId = found.id; entry.foodSnapshot = snapshotFood(found); if (entry.name.toLowerCase() !== found.name.toLowerCase()) { entry.name = found.name; food.value = found.name; } } else if (entry.name !== (entry.foodSnapshot?.name || '')) { entry.foodId = null; entry.foodSnapshot = null; } const source = foodForEntry(entry); updateServings(source); const unit = foodUnit(source); grams.placeholder = unit; grams.setAttribute('aria-label', `${label} item ${index + 1} ${unit}`); macros.textContent = source ? displayMacros(scaledMacros(source, entry.grams)) : (entry.name ? 'Add this food to the library before saving' : ''); refresh(); };
        serving.addEventListener('change', () => { if (serving.value) { grams.value = serving.value; entry.grams = serving.value; } const source = foodForEntry(entry); macros.textContent = source ? displayMacros(scaledMacros(source, entry.grams)) : ''; refresh(); });
        checked.addEventListener('change', update); food.addEventListener('input', update); food.addEventListener('change', update); grams.addEventListener('input', update); update();
        const remove = button('Remove', () => { day.meals[id].splice(index, 1); renderRows(); refresh(); }, 'compact danger');
        rows.append(el('div', { class: 'v2-diet-row' }, [checked, food, grams, remove, serving, macros]));
      });
    };
    renderRows();
    const sectionRecents = recentFoodsForSection(id); if (sectionRecents.length) { const shortcuts = el('div', { class: 'v2-food-shortcuts' }); sectionRecents.forEach(item => shortcuts.append(button(item.name, () => { const entry = day.meals[id].find(row => !row.name) || (day.meals[id].push({ name: '', grams: '', checked: false }), day.meals[id].at(-1)); Object.assign(entry, { foodId: item.id, foodSnapshot: snapshotFood(item), name: item.name, grams: '', checked: false }); renderRows(); }, 'compact'))); card.append(el('p', { class: 'v2-diet-note', text: 'Recently used in this meal' }), shortcuts); }
    card.append(rows, button('+ Add food row', () => { day.meals[id].push({ name: '', grams: '', checked: false }); renderRows(); }, ''));
    return card;
  }
  function dietTargetsCard() {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Weekly target plan' }), el('p', { class: 'v2-diet-note', text: 'Maintain separate Standard, Training day and Rest day targets, then assign one to each weekday. Initial values match your existing target until you change them.' }));
    card.append(button(state.showTargetEditor ? 'Hide target editor' : 'Manage target profiles and weekday schedule', () => { state.showTargetEditor = !state.showTargetEditor; renderDiet(); }));
    if (!state.showTargetEditor) return card;
    const form = el('form');
    Object.entries(state.dietSettings.targetProfiles).forEach(([id, profile]) => {
      const grid = el('div', { class: 'v2-macro-grid' });
      [['Calories', 'calories', 'kcal'], ['Protein', 'protein', 'g'], ['Carbs', 'carbs', 'g'], ['Fat', 'fat', 'g']].forEach(([label, key, unit]) => grid.append(input(`${label} (${unit})`, 'number', profile[key], () => {}, { name: `${id}-${key}`, min: '0', step: '1' })));
      form.append(el('section', { class: 'v2-profile' }, [el('h3', { text: profile.label }), grid]));
    });
    const schedule = el('div', { class: 'v2-week-grid v2-profile' });
    [[1, 'Mon'], [2, 'Tue'], [3, 'Wed'], [4, 'Thu'], [5, 'Fri'], [6, 'Sat'], [0, 'Sun']].forEach(([index, label]) => {
      const select = el('select', { name: 'day-' + index, 'aria-label': label + ' target profile' });
      Object.entries(state.dietSettings.targetProfiles).forEach(([id, profile]) => select.append(el('option', { value: id, text: profile.label })));
      select.value = state.dietSettings.targetSchedule[index] || 'standard'; schedule.append(el('div', { class: 'v2-field' }, [el('label', { text: label }), select]));
    });
    const submit = button('Save weekly targets', null, 'primary'); submit.type = 'submit'; form.append(el('h3', { text: 'Weekday schedule' }), schedule, submit);
    form.addEventListener('submit', async event => {
      event.preventDefault(); const data = new FormData(form);
      Object.keys(state.dietSettings.targetProfiles).forEach(id => ['calories', 'protein', 'carbs', 'fat'].forEach(key => state.dietSettings.targetProfiles[id][key] = numberOrNull(data.get(`${id}-${key}`)) || 0));
      [0, 1, 2, 3, 4, 5, 6].forEach(index => state.dietSettings.targetSchedule[index] = data.get('day-' + index) || 'standard');
      state.dietSettings.targets = Object.fromEntries(['calories', 'protein', 'carbs', 'fat'].map(key => [key, state.dietSettings.targetProfiles.standard[key]]));
      try { await save('dietSettings'); renderDiet(); toast('Weekly target plan saved.'); } catch (error) { toast(error.message); }
    });
    card.append(form); return card;
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
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: editing ? 'Edit food' : 'Add food to library' }), el('p', { class: 'v2-diet-note', text: 'Enter nutrition using the basis on the package or recipe. Historical meals retain the value used when they were saved.' }));
    const form = el('form'); const name = el('input', { type: 'text', required: 'true', 'aria-label': 'Food name', placeholder: 'e.g. Your protein bar' }); name.value = editing?.name || '';
    const aliases = el('input', { type: 'text', 'aria-label': 'Food aliases', placeholder: 'e.g. courgette, zucchini' }); aliases.value = (editing?.aliases || []).join(', ');
    const servings = el('textarea', { rows: '3', 'aria-label': 'Serving presets', placeholder: '1 scoop = 30\n1 tablespoon = 15' }); servings.value = (editing?.servings || []).map(item => `${item.label} = ${item.amount}`).join('\n');
    const basis = el('select', { name: 'basis', 'aria-label': 'Nutrition basis' }, [el('option', { value: '100g', text: 'Per 100g' }), el('option', { value: '100ml', text: 'Per 100ml' })]); basis.value = foodBasis(editing);
    const grid = el('div', { class: 'v2-grid' }); [['Calories', 'calories'], ['Protein', 'protein'], ['Carbs', 'carbs'], ['Fat', 'fat']].forEach(([label, key]) => grid.append(input(label, 'number', editing?.[key] ?? 0, () => {}, { name: key, min: '0', step: '0.1' })));
    const submit = button(editing ? 'Save food' : 'Add food', null, 'primary'); submit.type = 'submit'; const cancel = editing ? button('Cancel', () => { state.editFood = null; renderFoods(); }) : null;
    form.append(el('div', { class: 'v2-grid' }, [el('div', { class: 'v2-field' }, [el('label', { text: 'Food name' }), name]), el('div', { class: 'v2-field' }, [el('label', { text: 'Nutrition basis' }), basis])]), el('div', { class: 'v2-field' }, [el('label', { text: 'Search aliases — comma separated' }), aliases]), grid, el('div', { class: 'v2-field' }, [el('label', { text: 'Serving presets — one per line as label = amount' }), servings]), el('div', { class: 'v2-toolbar' }, [submit, cancel])); form.addEventListener('submit', async event => { event.preventDefault(); const data = new FormData(form); const foodName = name.value.trim(); const aliasList = aliases.value.split(',').map(value => value.trim()).filter(Boolean); const identities = new Set([foodName, ...aliasList].map(value => value.toLowerCase())); const duplicate = state.foods.items.find(item => item.id !== editing?.id && [item.name, ...(item.aliases || [])].some(value => identities.has(value.toLowerCase()))); if (!foodName || duplicate) return toast(foodName ? `That name or alias is already used by ${duplicate.name}.` : 'Enter a food name.'); const next = { ...(editing || {}), id: editing?.id || slug(foodName) + '-' + Date.now(), name: foodName, aliases: aliasList, servings: parseServings(servings.value), calories: numberOrNull(data.get('calories')) || 0, protein: numberOrNull(data.get('protein')) || 0, carbs: numberOrNull(data.get('carbs')) || 0, fat: numberOrNull(data.get('fat')) || 0, basis: data.get('basis') === '100ml' ? '100ml' : '100g', archived: false, favourite: editing?.favourite === true }; if (editing) state.foods.items[state.foods.items.findIndex(item => item.id === editing.id)] = next; else state.foods.items.push(next); try { await save('foods'); state.editFood = null; renderFoods(); toast(editing ? 'Food updated.' : 'Food added to the library.'); } catch (error) { toast(error.message); } }); card.append(form); return card;
  }
  function foodLibraryCard() {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Food library' }), el('p', { class: 'v2-diet-note', text: 'Edit, archive, or reuse foods. Archive removes a food from new entries without altering recorded days.' }));
    const list = el('div', { class: 'v2-list' }); const items = state.foods.items.filter(item => !item.archived).slice().sort((a, b) => a.name.localeCompare(b.name));
    items.forEach(item => list.append(el('div', { class: 'v2-library-row' }, [el('div', {}, [el('strong', { text: item.name }), el('div', { class: 'v2-meta', text: displayMacros(item) + ' per 100g' })]), el('div', { class: 'v2-actions' }, [button('Edit', () => { state.editFood = item.id; renderDiet(); }, 'compact'), button('Archive', async () => { if (!confirm(`Archive “${item.name}”? It will remain in historical entries.`)) return; item.archived = true; try { await save('foods'); renderDiet(); toast('Food archived.'); } catch (error) { item.archived = false; toast(error.message); } }, 'compact danger')])])));
    card.append(items.length ? list : el('p', { class: 'v2-muted', text: 'No active foods in the library.' })); return card;
  }
  function foodManagementCard() {
    const card = el('div', { class: 'card' });
    card.append(el('h2', { text: 'All active foods' }), el('p', { class: 'v2-diet-note', text: 'Each row shows its 100g or 100ml basis. Archive removes a food from new diary entries without changing saved days.' }));
    const list = el('div', { class: 'v2-list' });
    const items = state.foods.items.filter(item => !item.archived).slice();
    const search = el('input', { type: 'search', placeholder: 'Search foods', 'aria-label': 'Search foods' }); search.value = state.foodSearch || '';
    const category = el('select', { 'aria-label': 'Filter foods by category' });
    const categories = [...new Set(items.map(item => item.category || 'Personal'))].sort();
    category.append(el('option', { value: '', text: 'All categories' })); categories.forEach(value => category.append(el('option', { value, text: value })));
    category.value = state.foodCategory || '';
    const sortMetric = el('select', { 'aria-label': 'Sort foods by' }, [
      el('option', { value: 'name', text: 'Sort: Name' }), el('option', { value: 'calories', text: 'Sort: Calories' }),
      el('option', { value: 'protein', text: 'Sort: Protein' }), el('option', { value: 'carbs', text: 'Sort: Carbs' }), el('option', { value: 'fat', text: 'Sort: Fat' })
    ]); sortMetric.value = state.foodSortMetric || 'name';
    const sortDirection = el('select', { 'aria-label': 'Food sort direction' }, [
      el('option', { value: 'asc', text: 'A–Z / low to high' }), el('option', { value: 'desc', text: 'Z–A / high to low' })
    ]); sortDirection.value = state.foodSortDirection || 'asc';
    const resultCount = el('p', { class: 'v2-diet-note' });
    const redraw = (resetPage = false) => {
      state.foodSearch = search.value; state.foodCategory = category.value; state.foodSortMetric = sortMetric.value; state.foodSortDirection = sortDirection.value; clear(list);
      if (resetPage) state.foodPageSize = 80;
      const query = search.value.trim().toLowerCase();
      const visible = items.filter(item => (!query || foodSearchText(item).includes(query)) && (!category.value || (item.category || 'Personal') === category.value));
      const direction = sortDirection.value === 'desc' ? -1 : 1;
      visible.sort((a, b) => {
        if (sortMetric.value === 'name') return direction * a.name.localeCompare(b.name);
        return direction * ((Number(a[sortMetric.value]) || 0) - (Number(b[sortMetric.value]) || 0)) || a.name.localeCompare(b.name);
      });
      const sortLabel = sortMetric.options[sortMetric.selectedIndex].text.replace('Sort: ', '');
      const limit = Math.max(80, Number(state.foodPageSize) || 80); const shown = visible.slice(0, limit);
      resultCount.textContent = `${shown.length} shown of ${visible.length} matches · ${items.length} active · ${sortLabel}, ${sortDirection.value === 'asc' ? 'ascending' : 'descending'}.`;
      shown.forEach(item => {
        const archive = async () => {
          if (!confirm('Archive "' + item.name + '"? It will remain in historical entries.')) return;
          item.archived = true;
          try { await save('foods'); renderFoods(); toast('Food archived.'); }
          catch (error) { item.archived = false; toast(error.message); }
        };
        const quality = item.sourceFoodCode ? 'Official CoFID record' : item.isRecipe ? 'Calculated recipe' : item.source ? 'Label/source supplied' : 'Personal entry';
        const source = (item.category || 'Personal') + ' · ' + quality + (item.aliases?.length ? ' · aliases: ' + item.aliases.join(', ') : '') + (item.servings?.length ? ` · ${item.servings.length} serving preset${item.servings.length === 1 ? '' : 's'}` : '');
        const favourite = async () => { item.favourite = !item.favourite; try { await save('foods'); redraw(); toast(item.favourite ? 'Food added to favourites.' : 'Food removed from favourites.'); } catch (error) { item.favourite = !item.favourite; toast(error.message); } };
        list.append(el('div', { class: 'v2-library-row' }, [
          el('div', {}, [el('strong', { text: (item.favourite ? '★ ' : '') + item.name }), el('div', { class: 'v2-meta', text: displayMacros(item) + ' per ' + foodBasis(item) + ' · ' + source })]),
          el('div', { class: 'v2-actions' }, [button(item.favourite ? 'Unfavourite' : 'Favourite', favourite, 'compact'), button(item.isRecipe ? 'Edit recipe' : 'Edit', () => { if (item.isRecipe) state.editRecipe = item.id; else state.editFood = item.id; renderFoods(); }, 'compact'), button('Archive', archive, 'compact danger')])
        ]));
      });
      if (!visible.length) list.append(el('p', { class: 'v2-muted', text: 'No foods match this filter.' }));
      if (shown.length < visible.length) list.append(button(`Show ${Math.min(80, visible.length - shown.length)} more`, () => { state.foodPageSize = limit + 80; redraw(); }));
    };
    search.addEventListener('input', () => redraw(true)); category.addEventListener('change', () => redraw(true)); sortMetric.addEventListener('change', () => redraw(true)); sortDirection.addEventListener('change', () => redraw(true));
    card.append(el('div', { class: 'v2-toolbar v2-food-filter' }, [search, category, sortMetric, sortDirection]), resultCount, list); redraw();
    return card;
  }
  function recipeBuilderCard() {
    const editing = state.foods.items.find(item => item.id === state.editRecipe && item.isRecipe); const card = el('div', { class: 'card' });
    card.append(el('h2', { text: editing ? 'Edit recipe' : 'Recipe builder' }), el('p', { class: 'v2-diet-note', text: 'Combine saved foods by edible weight or volume. Enter the final cooked yield so the app calculates nutrition per 100g.' }));
    const form = el('form'); const name = el('input', { type: 'text', required: 'true', 'aria-label': 'Recipe name', placeholder: 'e.g. Turkey chilli' }); name.value = editing?.name || '';
    const aliases = el('input', { type: 'text', 'aria-label': 'Recipe aliases', placeholder: 'Search aliases, comma separated' }); aliases.value = (editing?.aliases || []).join(', ');
    const yieldAmount = el('input', { type: 'number', min: '1', step: '1', required: 'true', 'aria-label': 'Final cooked yield', placeholder: 'Final cooked yield (g)' }); yieldAmount.value = editing?.recipe?.yieldAmount || '';
    const optionList = el('datalist', { id: 'recipe-food-options' }); state.foods.items.filter(item => !item.archived && item.id !== editing?.id).sort((a, b) => a.name.localeCompare(b.name)).forEach(food => optionList.append(el('option', { value: food.name })));
    const initial = editing?.recipe?.ingredients?.map(item => ({ name: item.name, amount: item.amount })) || [{ name: '', amount: '' }, { name: '', amount: '' }, { name: '', amount: '' }]; const ingredientRows = initial.length ? initial : [{ name: '', amount: '' }];
    const rows = el('div'); const preview = el('p', { class: 'v2-summary', text: 'Add ingredients and a final yield to calculate the recipe.' }); const ingredientFood = value => { const food = foodByName(value); return food?.id === editing?.id ? null : food; };
    const recipeTotals = () => { const total = zeroMacros(); let recognised = 0; ingredientRows.forEach(row => { const food = ingredientFood(row.name); if (food && Number(row.amount) > 0) { addMacros(total, scaledMacros(food, row.amount)); recognised++; } }); const yieldValue = Number(yieldAmount.value) || 0; return { total, recognised, yieldValue, per100: yieldValue > 0 ? Object.fromEntries(Object.entries(total).map(([key, value]) => [key, value * 100 / yieldValue])) : zeroMacros() }; };
    const updatePreview = () => { const result = recipeTotals(); preview.textContent = result.recognised && result.yieldValue ? `${result.recognised} ingredients · ${displayMacros(result.total)} total · ${displayMacros(result.per100)} per 100g` : 'Add recognised ingredients and a final cooked yield to calculate the recipe.'; };
    const redrawRows = () => { clear(rows); ingredientRows.forEach((row, index) => { const food = el('input', { type: 'text', list: 'recipe-food-options', placeholder: 'Ingredient', 'aria-label': `Recipe ingredient ${index + 1}` }); food.value = row.name; const amount = el('input', { type: 'number', min: '0', step: '1', placeholder: 'g / ml', 'aria-label': `Recipe ingredient ${index + 1} amount` }); amount.value = row.amount; const updateFood = () => { const found = ingredientFood(food.value); row.name = found?.name || food.value; updatePreview(); }; food.addEventListener('input', updateFood); food.addEventListener('change', () => { const found = ingredientFood(food.value); row.name = found?.name || food.value; if (found) food.value = found.name; updatePreview(); }); amount.addEventListener('input', () => { row.amount = amount.value; updatePreview(); }); rows.append(el('div', { class: 'v2-recipe-row' }, [food, amount, button('Remove', () => { ingredientRows.splice(index, 1); if (!ingredientRows.length) ingredientRows.push({ name: '', amount: '' }); redrawRows(); updatePreview(); }, 'compact danger')])); }); };
    yieldAmount.addEventListener('input', updatePreview); redrawRows(); updatePreview();
    const submit = button(editing ? 'Save recipe' : 'Create recipe food', null, 'primary'); submit.type = 'submit';
    form.append(el('div', { class: 'v2-grid' }, [el('div', { class: 'v2-field' }, [el('label', { text: 'Recipe name' }), name]), el('div', { class: 'v2-field' }, [el('label', { text: 'Final cooked yield (g)' }), yieldAmount])]), el('div', { class: 'v2-field' }, [el('label', { text: 'Search aliases' }), aliases]), optionList, rows, button('+ Add ingredient', () => { ingredientRows.push({ name: '', amount: '' }); redrawRows(); }), preview, el('div', { class: 'v2-toolbar' }, [submit, editing ? button('Cancel', () => { state.editRecipe = null; renderFoods(); }) : null]));
    form.addEventListener('submit', async event => { event.preventDefault(); const title = name.value.trim(); const aliasList = aliases.value.split(',').map(value => value.trim()).filter(Boolean); const result = recipeTotals(); const ingredients = ingredientRows.map(row => { const food = ingredientFood(row.name); return food && Number(row.amount) > 0 ? { foodId: food.id, name: food.name, amount: Number(row.amount), foodSnapshot: snapshotFood(food) } : null; }).filter(Boolean); const identities = new Set([title, ...aliasList].map(value => value.toLowerCase())); const duplicate = state.foods.items.find(item => item.id !== editing?.id && [item.name, ...(item.aliases || [])].some(value => identities.has(value.toLowerCase()))); if (!title || duplicate) return toast(title ? `That name or alias is already used by ${duplicate.name}.` : 'Enter a recipe name.'); if (!ingredients.length || result.yieldValue <= 0) return toast('Add at least one recognised ingredient and the final cooked yield.'); const next = { ...(editing || {}), id: editing?.id || 'recipe-' + slug(title) + '-' + Date.now(), name: title, aliases: aliasList, calories: result.per100.calories, protein: result.per100.protein, carbs: result.per100.carbs, fat: result.per100.fat, basis: '100g', category: 'Personal recipes', source: 'Calculated from saved ingredients', isRecipe: true, recipe: { yieldAmount: result.yieldValue, ingredients }, servings: [{ id: 'whole-recipe', label: 'Whole recipe', amount: result.yieldValue }], archived: false, favourite: editing?.favourite === true, updatedAt: new Date().toISOString() }; if (editing) state.foods.items[state.foods.items.findIndex(item => item.id === editing.id)] = next; else state.foods.items.push(next); try { await save('foods'); state.editRecipe = null; renderFoods(); toast(editing ? 'Recipe updated.' : 'Recipe added to the food library.'); } catch (error) { toast(error.message); } }); card.append(form); return card;
  }
  function archivedFoodsCard() {
    const archived = state.foods.items.filter(item => item.archived); const card = el('div', { class: 'card' }); card.append(el('h2', { text: `Archived foods (${archived.length})` }), button(state.showArchivedFoods ? 'Hide archived foods' : 'Manage archived foods', () => { state.showArchivedFoods = !state.showArchivedFoods; renderFoods(); })); if (!state.showArchivedFoods) return card;
    const search = el('input', { type: 'search', placeholder: 'Search archived foods', 'aria-label': 'Search archived foods' }); const list = el('div', { class: 'v2-list' });
    const redraw = () => {
      clear(list); const query = search.value.trim().toLowerCase(); const visible = archived.filter(item => !query || foodSearchText(item).includes(query)).slice(0, 100);
      visible.forEach(item => list.append(el('div', { class: 'v2-library-row' }, [
        el('div', {}, [el('strong', { text: item.name }), el('div', { class: 'v2-meta', text: displayMacros(item) + ' per ' + foodBasis(item) })]),
        button('Restore', async () => { item.archived = false; try { await save('foods'); renderFoods(); toast('Food restored.'); } catch (error) { item.archived = true; toast(error.message); } }, 'compact')
      ])));
      if (!visible.length) list.append(el('p', { class: 'v2-muted', text: 'No archived foods match.' }));
    };
    search.addEventListener('input', redraw); card.append(search, list); redraw(); return card;
  }
  function renderFoods() {
    const panel = clear($('#tab-foods'));
    const intro = el('div', { class: 'card' });
    intro.append(el('h2', { text: 'Food library' }), el('p', { class: 'v2-muted', text: 'Manage reusable foods separately from the daily diary. Generic foods use official UK composition data; packaged and recipe foods should follow their own labels.' }));
    panel.append(intro, addFoodCard(), recipeBuilderCard(), foodManagementCard(), archivedFoodsCard());
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
  function recordDateVisible(date) { const filter = state.recordsFilters; return (!filter.from || date >= filter.from) && (!filter.to || date <= filter.to); }
  function recordsDietHistoryCard(dates) {
    const card = el('div', { class: 'card v2-diet-history' });
    card.append(el('h2', { text: 'Meal history' }), el('p', { class: 'v2-muted', text: 'Saved daily diet records. Open one to make a correction in Diet.' }));
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
  function recordsFilterCard() {
    const filter = state.recordsFilters; const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Filter records' }));
    const type = el('select', { 'aria-label': 'Record type' }, [['all', 'Meals and workouts'], ['diet', 'Meals only'], ['workouts', 'Workouts only']].map(([value, text]) => el('option', { value, text }))); type.value = filter.type;
    const from = el('input', { type: 'date', 'aria-label': 'Records from date' }); from.value = filter.from;
    const to = el('input', { type: 'date', 'aria-label': 'Records to date' }); to.value = filter.to;
    const routine = el('select', { 'aria-label': 'Filter workout routine' }); routine.append(el('option', { value: '', text: 'All routines' }));
    [...new Set(state.workouts.sessions.map(session => session.routineName || 'Ad hoc workout'))].sort().forEach(name => routine.append(el('option', { value: name, text: name }))); routine.value = filter.routine;
    const apply = () => { filter.type = type.value; filter.from = from.value; filter.to = to.value; filter.routine = routine.value; renderRecords(); };
    type.addEventListener('change', apply); from.addEventListener('change', apply); to.addEventListener('change', apply); routine.addEventListener('change', apply);
    const preset = days => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - days + 1); filter.from = start.toISOString().slice(0, 10); filter.to = end.toISOString().slice(0, 10); renderRecords(); };
    card.append(el('div', { class: 'v2-grid' }, [el('div', { class: 'v2-field' }, [el('label', { text: 'Record type' }), type]), el('div', { class: 'v2-field' }, [el('label', { text: 'Routine' }), routine]), el('div', { class: 'v2-field' }, [el('label', { text: 'From' }), from]), el('div', { class: 'v2-field' }, [el('label', { text: 'To' }), to])]), el('div', { class: 'v2-toolbar' }, [button('Last 7 days', () => preset(7), 'compact'), button('Last 30 days', () => preset(30), 'compact'), button('Last 90 days', () => preset(90), 'compact'), button('All time', () => { filter.from = ''; filter.to = ''; renderRecords(); }, 'compact')]));
    return card;
  }
  function recordsSummaryCard(dates, sessions) {
    const totals = dates.map(date => dietTotals(state.diet.days[date]).total); const avg = key => totals.length ? totals.reduce((sum, item) => sum + item[key], 0) / totals.length : null;
    const onTarget = dates.filter(date => { const calories = dietTotals(state.diet.days[date]).total.calories; const target = Number(targetProfileForDate(date).calories); return target > 0 && Math.abs(calories - target) / target <= 0.1; }).length;
    const card = el('div', { class: 'card v2-record-summary' }); card.append(el('h2', { text: 'Filtered summary' })); const grid = el('div', { class: 'v2-macro-grid' });
    [['Diet days', String(dates.length), onTarget ? `${onTarget} within ±10% calorie target` : 'Saved records'], ['Avg calories', avg('calories') === null ? '—' : Math.round(avg('calories')) + ' kcal', 'Filtered diet days'], ['Avg protein', avg('protein') === null ? '—' : Math.round(avg('protein')) + ' g', 'Filtered diet days'], ['Workouts', String(sessions.length), 'Filtered completed sessions']].forEach(([label, value, note]) => grid.append(el('div', { class: 'v2-macro' }, [el('span', { text: label }), el('strong', { text: value }), el('span', { text: note })]))); card.append(grid); return card;
  }
  function numericLoad(value) { const text = String(value || '').trim().replace(',', '.'); if (!text) return null; const marked = text.match(/-?\d+(?:\.\d+)?\s*(?:kg|kilograms?)/i); if (marked) return Number(marked[0].match(/-?\d+(?:\.\d+)?/)[0]); if (/^(?:\+\s*)?-?\d+(?:\.\d+)?$/.test(text)) return Number(text.replace('+', '').trim()); if (/\b(?:sec(?:ond)?s?|mins?|minutes?|reps?|body\s*weight|bw|band)\b/i.test(text)) return null; return null; }
  function normalExerciseName(value) { return String(value || '').trim().toLowerCase().replace(/\s+/g, ' '); }
  function canonicalExerciseIdentity(reference) {
    const exerciseId = typeof reference === 'object' ? reference?.exerciseId : null; const rawName = typeof reference === 'string' ? reference : reference?.name; const byId = exerciseId ? state.library.items.find(item => item.id === exerciseId) : null;
    const desiredName = byId?.name || EXERCISE_NAME_ALIASES[normalExerciseName(rawName)] || rawName || 'Unknown exercise'; const byName = state.library.items.find(item => normalExerciseName(item.name) === normalExerciseName(desiredName));
    return { key: 'exercise:' + (byId?.id || byName?.id || normalExerciseName(desiredName)), id: byId?.id || byName?.id || null, name: byId?.name || byName?.name || desiredName };
  }
  function sameExercise(left, right) { return canonicalExerciseIdentity(left).key === canonicalExerciseIdentity(right).key; }
  function completedExerciseSets(exercise) { return (exercise.sets || []).filter(set => set.done || set.reps !== '' && set.reps !== null && set.reps !== undefined); }
  function exerciseSessionHistory(reference, excludeId = null) { return state.workouts.sessions.filter(session => session.id !== excludeId && session.exercises?.some(exercise => sameExercise(exercise, reference))).slice().sort(byDate).map(session => ({ session, exercise: session.exercises.find(exercise => sameExercise(exercise, reference)) })); }
  function loggedRpes(sets) { return sets.map(set => set.rpe).filter(value => value !== '' && value !== null && value !== undefined && Number.isFinite(Number(value))).map(Number); }
  function exercisePerformance(exercise) { const sets = completedExerciseSets(exercise); const reps = sets.map(set => Number(set.reps) || 0); const loads = sets.map(set => numericLoad(set.load)).filter(value => value !== null); const rpes = loggedRpes(sets); return { sets: sets.length, best: Math.max(0, ...reps), total: reps.reduce((sum, value) => sum + value, 0), maxLoad: loads.length ? Math.max(...loads) : null, volume: sets.reduce((sum, set) => { const load = numericLoad(set.load); return sum + (load === null ? 0 : load * (Number(set.reps) || 0)); }, 0), avgRpe: rpes.length ? rpes.reduce((sum, value) => sum + value, 0) / rpes.length : null }; }
  function currentReadinessSignals() { const today = state.health.entries[isoToday()] || {}; const signals = []; if (Number(today.sleepHours) > 0 && Number(today.sleepHours) < 6) signals.push(`Only ${today.sleepHours} hours of sleep is logged; keep today submaximal if performance feels suppressed.`); if (Number(today.energy) > 0 && Number(today.energy) <= 2) signals.push('Energy is rated 2/5 or lower; consider maintaining rather than progressing.'); if (Number(today.soreness) >= 4) signals.push('Soreness is rated 4/5 or higher; use pain-free substitutions or reduce volume.'); if (Number(today.sleepQuality) > 0 && Number(today.sleepQuality) <= 2) signals.push('Sleep quality is rated 2/5 or lower; avoid forcing a progression.'); const recent = state.workouts.sessions.slice().sort(byDate).slice(-3); const discomfortSessions = recent.filter(session => session.exercises?.some(exercise => Number(exercise.quickNotes?.pain) >= 4)).length; if (discomfortSessions >= 2) signals.push('Discomfort of 4/10 or higher appears in at least two of the last three workouts; review exercise choice and volume.'); return signals; }
  function exerciseRecoverySignals(reference) { const history = exerciseSessionHistory(reference).slice(-3); const signals = []; const discomfort = history.filter(({ exercise }) => Number(exercise.quickNotes?.pain) >= 4).length; const failures = history.filter(({ exercise }) => exercise.quickNotes?.failed === true).length; const poorForm = history.filter(({ exercise }) => exercise.formQuality === 'needs-work').length; const highRpe = history.filter(({ exercise }) => { const value = exercisePerformance(exercise).avgRpe; return value !== null && value >= 9.5; }).length; if (discomfort) signals.push(`${discomfort} of the last ${history.length} sessions recorded discomfort at 4/10 or higher.`); if (failures >= 2) signals.push('Two or more recent sessions recorded a failed or shortened set.'); if (poorForm >= 2) signals.push('Form was rated “Needs work” in two or more recent sessions.'); if (highRpe >= 2) signals.push('Two or more recent sessions averaged RPE 9.5 or higher.'); return signals; }
  function progressionSuggestion(exercise) {
    const previous = previousExercise(exercise, state.active?.id); if (!previous) return { tone: 'neutral', text: 'No previous performance yet. Start inside the target range and leave 2–3 good reps in reserve.' };
    const performance = exercisePerformance(previous); const target = exercise.target || previous.target || targetFor(exercise.name); const increment = Number(state.settings.equipment?.loadIncrement) || 2.5; const signals = exerciseRecoverySignals(exercise); const lastReps = performance.best || Number(target.min) || 1; let suggestedReps = lastReps, suggestedLoad = performance.maxLoad;
    if (signals.length) { if (suggestedLoad !== null) suggestedLoad = Math.max(0, suggestedLoad - increment); suggestedReps = Math.max(1, Number(target.min) || Math.floor(lastReps * 0.8)); return { tone: 'warning', text: `Hold or reduce: ${signals[0]} Aim for ${suggestedReps} ${target.unit}${suggestedLoad === null ? '' : ` at about ${suggestedLoad} kg`} with clean, pain-free form.`, reps: suggestedReps, load: suggestedLoad, signals }; }
    const hitTop = completedExerciseSets(previous).length > 0 && completedExerciseSets(previous).every(set => Number(set.reps) >= Number(target.max));
    if (hitTop && (performance.avgRpe === null || performance.avgRpe <= 8.5)) { if (suggestedLoad !== null) { suggestedLoad += increment; return { tone: 'progress', text: `Progress load by the configured ${increment} kg increment to about ${suggestedLoad} kg while returning to ${target.min}–${target.max} ${target.unit}.`, reps: Number(target.min) || lastReps, load: suggestedLoad }; } const harder = exerciseById(progressionFor(exerciseById(exercise.exerciseId) || exercise).progressionId); return { tone: 'progress', text: harder ? `Top of the range was achieved at manageable effort. Consider ${harder.name}, or repeat once to confirm.` : `Top of the range was achieved at manageable effort. Add ${target.unit === 'seconds' ? '5 seconds' : 'one controlled rep'} or use a slightly harder variation.`, reps: lastReps + (target.unit === 'seconds' ? 5 : 1), load: null }; }
    if (performance.avgRpe !== null && performance.avgRpe >= 9.5) { if (suggestedLoad !== null) suggestedLoad = Math.max(0, suggestedLoad - increment); suggestedReps = Math.max(Number(target.min) || 1, lastReps - 1); return { tone: 'warning', text: `Average effort was RPE ${performance.avgRpe.toFixed(1)}. Reduce to roughly ${suggestedReps} ${target.unit}${suggestedLoad === null ? '' : ` at ${suggestedLoad} kg`} and rebuild clean reps.`, reps: suggestedReps, load: suggestedLoad }; }
    suggestedReps = Math.min(Number(target.max) || lastReps + 1, lastReps + (target.unit === 'seconds' ? 5 : 1)); return { tone: 'progress', text: `Keep the same variation${suggestedLoad === null ? '' : ` and about ${suggestedLoad} kg`}; target roughly ${suggestedReps} ${target.unit} before adding load or difficulty.`, reps: suggestedReps, load: suggestedLoad };
  }
  async function applyProgressionSuggestion(exercise, suggestion) { if (suggestion.reps === undefined && suggestion.load === undefined) return; captureWorkoutUndo('apply progression suggestion'); exercise.sets.forEach(set => { if (suggestion.reps !== undefined) set.reps = String(suggestion.reps); if (suggestion.load !== undefined && suggestion.load !== null) set.load = String(suggestion.load); set.done = false; }); if (!await persistDraft()) return renderWorkout(); renderWorkout(); toast('Suggested values applied; adjust any set before completing it.'); }
  function progressionPanel(exercise) { const suggestion = progressionSuggestion(exercise); const box = el('div', { class: 'v2-progression-box' + (suggestion.tone === 'warning' ? ' warning' : '') }, [el('strong', { text: suggestion.tone === 'warning' ? 'Recovery-aware suggestion' : 'Next-session suggestion' }), el('div', { class: 'v2-meta', text: suggestion.text })]); if (suggestion.reps !== undefined || suggestion.load !== undefined) box.append(button('Apply suggested values', () => applyProgressionSuggestion(exercise, suggestion), 'compact')); return box; }
  function exerciseHistoryDetails(exercise) { const history = exerciseSessionHistory(exercise, state.active?.id).slice(-8); const identity = canonicalExerciseIdentity(exercise); const details = el('details', { class: 'v2-exercise-history' }); details.append(el('summary', { text: `History & progression (${history.length} session${history.length === 1 ? '' : 's'})` })); if (!history.length) { details.append(el('p', { class: 'v2-muted', text: 'No completed sessions for this exercise yet.' })); return details; } const values = history.map(item => ({ date: item.session.date, ...exercisePerformance(item.exercise) })); const max = Math.max(1, ...values.map(item => item.best)); const chart = el('div', { class: 'v2-mini-chart', role: 'img', 'aria-label': `${identity.name} best reps or seconds over recent sessions` }); values.forEach(item => chart.append(el('div', { class: 'v2-mini-bar', title: `${item.date}: best ${item.best}; ${item.sets} sets; average RPE ${item.avgRpe?.toFixed(1) || 'not logged'}`, style: `height:${Math.max(8, item.best / max * 100)}%` }, [el('span', { text: item.date.slice(5) })]))); const latest = values.at(-1); details.append(chart, el('div', { class: 'v2-meta', text: `Latest: best ${latest.best} · ${latest.sets} logged sets${latest.maxLoad === null ? '' : ` · max numeric load ${latest.maxLoad} kg`}${latest.avgRpe === null ? '' : ` · avg RPE ${latest.avgRpe.toFixed(1)}`}` })); return details; }
  function plateBreakdown(total) { const equipment = state.settings.equipment; const targetPerSide = Math.max(0, (Number(total) - Number(equipment.barWeight)) / 2); let remaining = targetPerSide; const used = []; [...equipment.platePairs].map(Number).filter(value => value > 0).sort((a, b) => b - a).forEach(plate => { if (plate <= remaining + 0.0001) { used.push(plate); remaining -= plate; } }); const loaded = Number(equipment.barWeight) + 2 * used.reduce((sum, value) => sum + value, 0); return { used, loaded, remainder: Math.max(0, Number(total) - loaded) }; }
  function loadTools() { const details = el('details', { class: 'v2-load-tools' }); const target = el('input', { type: 'number', min: '0', step: '0.25', placeholder: 'Target total kg', 'aria-label': 'Target barbell total weight' }); const result = el('div', { class: 'v2-plate-result', text: 'Enter a target total to calculate plates.' }); const calculate = () => { if (!target.value) return result.textContent = 'Enter a target total to calculate plates.'; const breakdown = plateBreakdown(target.value); result.textContent = `Bar ${state.settings.equipment.barWeight} kg · each side: ${breakdown.used.length ? breakdown.used.join(' + ') + ' kg' : 'no plates'} · loaded ${breakdown.loaded} kg${breakdown.remainder > 0.01 ? ` · ${breakdown.remainder.toFixed(2)} kg below target with available pairs` : ''}`; }; target.addEventListener('input', calculate); details.append(el('summary', { text: 'Load tools and plate calculator' }), el('div', { class: 'v2-grid' }, [el('div', { class: 'v2-field' }, [el('label', { text: 'Target barbell weight (kg)' }), target]), result])); return details; }
  function workoutMetrics(session) { const exercises = (session.exercises || []).filter(exercise => !exercise.skipped); const allSets = exercises.flatMap(exercise => exercise.sets || []); const completed = allSets.filter(set => set.done || set.reps !== '' && set.reps !== null && set.reps !== undefined); const work = completed.reduce((sum, set) => sum + (Number(set.reps) || 0), 0); const loadedVolume = completed.reduce((sum, set) => { const load = numericLoad(set.load); return sum + (load === null ? 0 : load * (Number(set.reps) || 0)); }, 0); const rpes = loggedRpes(completed); const discomfort = Math.max(0, ...exercises.map(exercise => Number(exercise.quickNotes?.pain) || 0)); return { completedSets: completed.length, plannedSets: allSets.length, completion: allSets.length ? completed.length / allSets.length * 100 : 0, work, loadedVolume, avgRpe: rpes.length ? rpes.reduce((sum, value) => sum + value, 0) / rpes.length : null, discomfort }; }
  function buildWorkoutSummary(session, priorSessions = state.workouts.sessions.filter(item => item.id !== session.id)) { const metrics = workoutMetrics(session); const eligible = priorSessions.filter(item => item.id !== session.id && (!session.date || item.date <= session.date)); const priorBests = new Map(); eligible.forEach(item => item.exercises?.forEach(exercise => { const performance = exercisePerformance(exercise); const key = canonicalExerciseIdentity(exercise).key; const prior = priorBests.get(key) || { best: 0, maxLoad: null, volume: 0 }; prior.best = Math.max(prior.best, performance.best); if (performance.maxLoad !== null) prior.maxLoad = prior.maxLoad === null ? performance.maxLoad : Math.max(prior.maxLoad, performance.maxLoad); prior.volume = Math.max(prior.volume, performance.volume); priorBests.set(key, prior); })); let prs = 0; session.exercises.forEach(exercise => { const current = exercisePerformance(exercise); const prior = priorBests.get(canonicalExerciseIdentity(exercise).key); if (current.best > (prior?.best || 0) || current.maxLoad !== null && current.maxLoad > (prior?.maxLoad ?? -Infinity) || current.volume > (prior?.volume || 0)) prs++; }); const previous = eligible.filter(item => session.routineId ? item.routineId === session.routineId : item.routineName === session.routineName).slice().sort(byDate).at(-1); const priorMetrics = previous ? workoutMetrics(previous) : null; return { ...metrics, prs, previousDate: previous?.date || null, setDelta: priorMetrics ? metrics.completedSets - priorMetrics.completedSets : null, volumeDelta: priorMetrics ? metrics.loadedVolume - priorMetrics.loadedVolume : null, durationDelta: priorMetrics ? Number(session.elapsedSeconds || 0) - Number(previous.elapsedSeconds || 0) : null, generatedAt: new Date().toISOString() }; }
  function workoutSummaryCard(session, title = 'Workout summary') { const summary = session.summary || buildWorkoutSummary(session); const card = el('div', { class: 'card v2-session-summary' }); card.append(el('h2', { text: title }), el('p', { class: 'v2-meta', text: `${session.date} · ${session.routineName || 'Ad hoc workout'}${session.routineVersion ? ` · routine v${session.routineVersion}` : ''}` })); const grid = el('div', { class: 'v2-summary-grid' }); [['Completed sets', `${summary.completedSets}/${summary.plannedSets}`, `${Math.round(summary.completion)}% of planned`], ['Work', String(Math.round(summary.work)), 'Reps or hold-seconds'], ['Numeric volume', String(Math.round(summary.loadedVolume)), 'Reps × numeric load'], ['Duration', timeDisplay(session.elapsedSeconds || 0), summary.durationDelta === null ? 'First comparable session' : `${summary.durationDelta >= 0 ? '+' : ''}${Math.round(summary.durationDelta / 60)} min vs previous`], ['Average RPE', summary.avgRpe === null ? '—' : summary.avgRpe.toFixed(1), 'Logged efforts only'], ['PR signals', String(summary.prs), 'Rep, load or volume bests'], ['Discomfort', `${summary.discomfort}/10`, 'Highest exercise note'], ['Set change', summary.setDelta === null ? '—' : `${summary.setDelta >= 0 ? '+' : ''}${summary.setDelta}`, summary.previousDate ? `Versus ${summary.previousDate}` : 'No prior routine session']].forEach(([label, value, note]) => grid.append(el('div', { class: 'v2-macro' }, [el('span', { text: label }), el('strong', { text: value }), el('span', { text: note })]))); card.append(grid); if (summary.discomfort >= 4 || summary.avgRpe >= 9.5) card.append(el('p', { class: 'v2-summary v2-warning', text: 'Recovery flag: review discomfort, form and effort notes before progressing the next session.' })); return card; }
  function personalBests(sessions) {
    const bests = new Map(); sessions.forEach(session => session.exercises.forEach(exercise => { const identity = canonicalExerciseIdentity(exercise); const item = bests.get(identity.key) || { key: identity.key, exerciseId: identity.id, name: identity.name, unit: exercise.target?.unit || 'reps', best: 0, load: null, volume: 0, date: session.date, aliases: new Set() }; if (exercise.name !== identity.name) item.aliases.add(exercise.name); exercise.sets.forEach(set => { const performance = Number(set.reps) || 0; const load = numericLoad(set.load); if (performance > item.best) { item.best = performance; item.date = session.date; } if (load !== null && (item.load === null || load > item.load)) item.load = load; if (load !== null) item.volume = Math.max(item.volume, performance * load); }); bests.set(identity.key, item); })); return [...bests.values()].filter(item => item.best || item.load !== null).sort((a, b) => b.best - a.best || a.name.localeCompare(b.name));
  }
  function recordsPersonalBestsCard(sessions) {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Personal records' }), el('p', { class: 'v2-muted', text: 'Historical exercise names are reconciled with their current exercise and variation, so renamed records contribute to one progression history. Bodyweight and band descriptions are not guessed as kilograms.' })); const search = el('input', { type: 'search', placeholder: 'Filter personal records', 'aria-label': 'Filter personal records' }); const list = el('div', { class: 'v2-pr-list' }); const items = personalBests(sessions); const redraw = () => { clear(list); const query = search.value.trim().toLowerCase(); const visible = items.filter(item => !query || item.name.toLowerCase().includes(query) || [...item.aliases].some(alias => alias.toLowerCase().includes(query))).slice(0, 30); visible.forEach(item => list.append(el('div', { class: 'v2-pr' }, [el('strong', { text: item.name }), el('div', { class: 'v2-meta', text: `Best ${item.best} ${item.unit}${item.load === null ? '' : ` · max numeric load ${item.load} kg`}${item.volume ? ` · best loaded volume ${Math.round(item.volume)}` : ''}` }), el('div', { class: 'v2-meta', text: 'Latest best performance: ' + item.date }), item.aliases.size ? el('div', { class: 'v2-meta', text: 'Includes earlier names: ' + [...item.aliases].join(', ') }) : null]))); if (!visible.length) list.append(el('p', { class: 'v2-muted', text: 'No matching logged performance yet.' })); }; search.addEventListener('input', redraw); card.append(search, list); redraw(); return card;
  }
  function mondayOf(date) { const value = new Date(date + 'T12:00:00'); const day = value.getDay() || 7; value.setDate(value.getDate() - day + 1); return value.toISOString().slice(0, 10); }
  function recordsTrainingLoadCard(sessions) {
    const weeks = []; const current = new Date(isoToday() + 'T12:00:00'); const currentDay = current.getDay() || 7; current.setDate(current.getDate() - currentDay + 1); for (let offset = 7; offset >= 0; offset--) { const start = new Date(current); start.setDate(start.getDate() - offset * 7); weeks.push({ key: start.toISOString().slice(0, 10), sets: 0, work: 0, loadedVolume: 0 }); } const lookup = Object.fromEntries(weeks.map(item => [item.key, item])); sessions.forEach(session => { const week = lookup[mondayOf(session.date)]; if (!week) return; session.exercises.forEach(exercise => exercise.sets.forEach(set => { if (!(set.done || set.reps)) return; const performance = Number(set.reps) || 0; week.sets++; week.work += performance; const load = numericLoad(set.load); if (load !== null) week.loadedVolume += performance * load; })); }); const max = Math.max(1, ...weeks.map(item => item.work)); const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Eight-week training load' }), el('p', { class: 'v2-muted', text: 'Total logged reps or hold-seconds. Numeric loaded volume is reported separately; the chart does not invent a bodyweight load.' })); const chart = el('div', { class: 'v2-bar-chart', role: 'img', 'aria-label': 'Eight week training work chart' }); weeks.forEach(item => { const bar = el('div', { class: 'v2-bar', title: `${item.key}: ${item.work} reps/seconds across ${item.sets} sets`, style: `height:${Math.max(2, item.work / max * 100)}%` }, [el('span', { text: item.key.slice(5) })]); chart.append(bar); }); const latest = weeks.at(-1); card.append(chart, el('p', { class: 'v2-summary', text: `Current week: ${latest.sets} completed sets · ${Math.round(latest.work)} reps/seconds · ${Math.round(latest.loadedVolume)} numeric loaded volume.` })); return card;
  }
  function recordsProgrammeAnalyticsCard() {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Programme progression' })); const weekEntries = Object.entries(state.programme.weeklyChecks).sort((a, b) => Number(a[0]) - Number(b[0])); const tasksPerWeek = PROGRAMME_SESSIONS.reduce((sum, session) => sum + programmeSessionItems(session[0]).length, 0); const completed = weekEntries.reduce((sum, [, week]) => sum + Object.values(week.items || {}).filter(Boolean).length, 0); const possible = weekEntries.length * tasksPerWeek; const avgAdherence = possible ? completed / possible * 100 : 0; const discomfort = weekEntries.filter(([, item]) => item.jointComfort !== '' && item.jointComfort !== null && item.jointComfort !== undefined).map(([week, item]) => ({ week, value: Number(item.jointComfort) })).filter(item => Number.isFinite(item.value)); const recentNeedsWork = state.workouts.sessions.filter(session => session.programme && session.date >= new Date(Date.now() - 28 * 86400000).toISOString().slice(0, 10)).flatMap(session => session.exercises).filter(exercise => exercise.formQuality === 'needs-work').length; const grid = el('div', { class: 'v2-macro-grid' }); [['Tracked weeks', String(weekEntries.length), `${completed}/${possible || 0} checklist items`], ['Average adherence', possible ? Math.round(avgAdherence) + '%' : '—', 'Individually ticked programme tasks'], ['Stage changes', String(state.programme.stageHistory.length), 'Recorded from this release onward'], ['Latest discomfort', discomfort.length ? discomfort.at(-1).value + '/10' : '—', discomfort.length ? `Programme week ${discomfort.at(-1).week}` : 'No weekly score']].forEach(([label, value, note]) => grid.append(el('div', { class: 'v2-macro' }, [el('span', { text: label }), el('strong', { text: value }), el('span', { text: note })]))); card.append(grid);
    const signals = []; const recentWeeks = weekEntries.slice(-6); if (Number(state.programme.currentWeek) % 5 === 0 || Number(state.programme.currentWeek) % 6 === 0) signals.push('Current week falls on the planned 5th–6th-week deload window.'); if (recentWeeks.length >= 5 && !recentWeeks.some(([, week]) => week.deload)) signals.push('No deload is marked in the most recent tracked six-week window.'); if (discomfort.slice(-2).length === 2 && discomfort.slice(-2).every(item => item.value >= 4)) signals.push('The last two recorded joint-discomfort scores are 4/10 or higher; review volume and exercise choice before progressing.'); if (recentNeedsWork >= 3) signals.push(`${recentNeedsWork} recent programme exercises were rated “Needs work”; review their cues before adding difficulty.`); card.append(el('div', { class: 'v2-summary' }, signals.length ? signals.map(signal => el('div', { text: '• ' + signal })) : [el('span', { text: 'No automatic deload, discomfort or repeated form-quality flags from the recorded data.' })]));
    if (state.programme.stageHistory.length) { const history = el('div', { class: 'v2-list' }); state.programme.stageHistory.slice().reverse().slice(0, 12).forEach(entry => { const changes = entry.changes || []; history.append(el('div', { class: 'v2-row' }, [el('strong', { text: `${entry.date} · week ${entry.programmeWeek}` }), el('span', { class: 'v2-meta', text: changes.length ? changes.map(change => `${PROGRAMME_SKILLS[change.skill]?.label || change.skill}: ${change.from} → ${change.to}`).join(' · ') : 'Phase changed' })])); }); card.append(el('h3', { text: 'Stage timeline' }), history); } return card;
  }
  function renderRecords() {
    const panel = clear($('#tab-records'));
    const intro = el('div', { class: 'card' });
    intro.append(el('h2', { text: 'Records' }), el('p', { class: 'v2-muted', text: 'Your saved meal days and completed workout sessions, kept separately from the live logging screens.' }));
    const dates = Object.keys(state.diet.days).filter(date => state.diet.days[date].updatedAt && recordDateVisible(date)).sort().reverse();
    const sessions = state.workouts.sessions.filter(session => recordDateVisible(session.date) && (!state.recordsFilters.routine || (session.routineName || 'Ad hoc workout') === state.recordsFilters.routine)).slice().sort(byDate).reverse();
    panel.append(intro); const latestSummary = state.workouts.sessions.find(session => session.id === state.lastWorkoutId); if (latestSummary) panel.append(workoutSummaryCard(latestSummary, 'Just completed')); panel.append(recordsFilterCard(), recordsSummaryCard(state.recordsFilters.type === 'workouts' ? [] : dates, state.recordsFilters.type === 'diet' ? [] : sessions));
    if (state.recordsFilters.type !== 'diet') panel.append(recordsTrainingLoadCard(sessions), recordsPersonalBestsCard(sessions), recordsProgrammeAnalyticsCard());
    if (state.recordsFilters.type !== 'workouts') panel.append(recordsDietHistoryCard(dates));
    if (state.recordsFilters.type !== 'diet') panel.append(workoutHistoryCard(sessions));
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
  function routineRow(routine) {
    const groupCount = new Set(routine.exercises.map(exercise => exercise.programming?.group?.id).filter(Boolean)).size; const optionalCount = routine.exercises.filter(exercise => exercise.programming?.optional).length;
    const scheduled = (routine.scheduleDays || []).map(day => TRAINING_DAYS[day]).join(', '); const meta = [`Version ${routine.version || 1}${scheduled ? ` · scheduled ${scheduled}` : ' · not scheduled'}`, routine.exercises.map(ex => ex.name).join(' · '), groupCount ? `${groupCount} superset/circuit group${groupCount === 1 ? '' : 's'}` : '', optionalCount ? `${optionalCount} optional` : ''].filter(Boolean);
    const actions = [button('Load workout', () => startRoutine(routine.id), 'primary'), button('Edit', () => { state.selectedRoutine = routine.id; renderRoutines(); }), button('Duplicate', () => duplicateRoutine(routine.id))];
    if (routine.exercises.some(exercise => exercise.programming?.setType === 'warm-up')) actions.push(button('Save warm-up', () => saveRoutineTemplate(routine, 'warm-up'), 'compact'));
    if (routine.exercises.some(exercise => exercise.programming?.setType === 'cooldown')) actions.push(button('Save cooldown', () => saveRoutineTemplate(routine, 'cooldown'), 'compact'));
    actions.push(button('Delete', () => deleteRoutine(routine.id), 'danger'));
    const wrapper = el('div'); wrapper.append(el('div', { class: 'v2-row' }, [el('div', { class: 'grow' }, [el('strong', { text: routine.name }), ...meta.map(text => el('div', { class: 'v2-meta', text }))]), el('div', { class: 'v2-actions' }, actions)]));
    if (routine.versions?.length) { const history = el('details', { class: 'v2-routine-history' }); history.append(el('summary', { text: `${routine.versions.length} earlier version${routine.versions.length === 1 ? '' : 's'}` })); routine.versions.slice().reverse().forEach(version => history.append(el('div', { class: 'v2-row' }, [el('div', { class: 'grow' }, [el('strong', { text: `Version ${version.version} — ${version.name}` }), el('div', { class: 'v2-meta', text: `${version.exercises.length} exercises · ${(version.scheduleDays || []).map(day => TRAINING_DAYS[day]).join(', ') || 'not scheduled'} · saved ${String(version.updatedAt || '').slice(0, 10)}` })]), button('Restore as new version', () => restoreRoutineVersion(routine.id, version.version), 'compact')]))); wrapper.append(history); }
    return wrapper;
  }
  function defaultProgram(exercise) { return { sets: 3, restSeconds: 90, targetRpe: '', setType: 'working', optional: false, group: null, target: clone(exercise.target || targetFor(exercise.name)) }; }
  function normaliseProgramming(program) {
    const next = { sets: Math.max(1, Number(program?.sets) || 1), restSeconds: Math.max(0, Number(program?.restSeconds) || 0), targetRpe: program?.targetRpe ?? '', setType: program?.setType === 'warmup' ? 'warm-up' : program?.setType || 'working', optional: program?.optional === true, target: clone(program?.target || { min: 1, max: 1, unit: 'reps' }), group: null };
    if (program?.group?.type === 'superset' || program?.group?.type === 'circuit') next.group = { id: program.group.id || slug(`${program.group.type}-${program.group.label || 'A'}`), type: program.group.type, label: program.group.label || 'A', rounds: Math.max(1, Number(program.group.rounds) || next.sets), restSeconds: Math.max(0, Number(program.group.restSeconds) || 0) };
    return next;
  }
  function plannedSets(exercise) { const program = normaliseProgramming(exercise.programming || defaultProgram(exercise)); const count = program.group?.rounds || program.sets; return Array.from({ length: Math.max(1, count) }, () => ({ reps: '', load: '', rpe: '', done: false, type: program.setType || 'working', targetRpe: program.targetRpe || '', restSeconds: Number(program.group?.restSeconds ?? program.restSeconds) || 0 })); }
  function exerciseSnapshot(item, program) { return { exerciseId: item.id, name: item.name, tip: item.tip, instructions: clone(item.instructions || []), visual: item.visual || 'general', target: clone(item.target), programming: normaliseProgramming(program || defaultProgram(item)) }; }
  function routineVersionSnapshot(routine) { return { version: Number(routine.version) || 1, name: routine.name, exercises: clone(routine.exercises), scheduleDays: clone(routine.scheduleDays || []), updatedAt: routine.updatedAt || routine.createdAt || new Date().toISOString() }; }
  async function restoreRoutineVersion(id, versionNumber) { const routine = state.routines.items.find(item => item.id === id); const version = routine?.versions?.find(item => item.version === versionNumber); if (!routine || !version || !confirm(`Restore version ${versionNumber} of ${routine.name} as a new current version?`)) return; const current = routineVersionSnapshot(routine); routine.versions = [...routine.versions, current].slice(-20); routine.version = (Number(routine.version) || 1) + 1; routine.name = version.name; routine.exercises = clone(version.exercises); routine.scheduleDays = clone(version.scheduleDays || []); routine.updatedAt = new Date().toISOString(); try { await save('routines'); render(); toast(`Restored as version ${routine.version}.`); } catch (error) { toast(error.message); } }
  async function duplicateRoutine(id) { const source = state.routines.items.find(item => item.id === id); if (!source) return; const copy = clone(source); copy.id = 'routine-' + Date.now(); copy.name = source.name + ' — Copy'; copy.version = 1; copy.versions = []; copy.createdAt = new Date().toISOString(); copy.updatedAt = copy.createdAt; state.routines.items.push(copy); try { await save('routines'); renderRoutines(); toast('Routine duplicated.'); } catch (error) { state.routines.items.pop(); toast(error.message); } }
  async function saveRoutineTemplate(routine, kind) { const exercises = routine.exercises.filter(exercise => exercise.programming?.setType === kind).map(clone); if (!exercises.length) return toast(`This routine has no ${kind} exercises.`); const base = `${routine.name} ${kind}`; let name = base; let suffix = 2; while (state.routines.templates.some(item => item.name.toLowerCase() === name.toLowerCase())) name = `${base} ${suffix++}`; state.routines.templates.push({ id: 'routine-template-' + Date.now(), name, kind, exercises, updatedAt: new Date().toISOString() }); try { await save('routines'); renderRoutines(); toast(`${kind === 'warm-up' ? 'Warm-up' : 'Cooldown'} template saved.`); } catch (error) { state.routines.templates.pop(); toast(error.message); } }
  async function deleteRoutineTemplate(id) { if (!confirm('Delete this reusable routine template?')) return; const index = state.routines.templates.findIndex(item => item.id === id); const removed = state.routines.templates.splice(index, 1)[0]; try { await save('routines'); renderRoutines(); toast('Template deleted.'); } catch (error) { state.routines.templates.splice(index, 0, removed); toast(error.message); } }
  function routineBuilder() {
    const editing = state.routines.items.find(item => item.id === state.selectedRoutine);
    const card = el('div', { class: 'card' });
    card.append(el('h2', { text: editing ? 'Edit routine' : 'Create routine' }));
    const form = el('form', { class: 'v2-routine-form' });
    const name = el('input', { type: 'text', required: 'true', placeholder: 'e.g. Calisthenics A' });
    name.value = editing?.name || '';
    const scheduleDays = new Set(editing?.scheduleDays || []); const schedulePicker = el('div', { class: 'v2-day-checks' }); TRAINING_DAYS.forEach((label, index) => { const check = el('input', { type: 'checkbox' }); check.checked = scheduleDays.has(index); check.addEventListener('change', () => check.checked ? scheduleDays.add(index) : scheduleDays.delete(index)); schedulePicker.append(el('label', { class: 'v2-check' }, [check, document.createTextNode(label)])); });
    const search = el('input', { type: 'search', placeholder: 'Filter exercise list' });
    const library = el('div', { class: 'v2-library' });
    const order = editing?.exercises.map(exercise => exercise.exerciseId) || []; const chosen = new Set(order); const programs = Object.fromEntries((editing?.exercises || []).map(exercise => [exercise.exerciseId, normaliseProgramming(exercise.programming || defaultProgram(exercise))])); const programming = el('div', { class: 'v2-routine-form' }); let draggedId = null;
    const updateGroup = (group, changes) => { const oldId = group.id; const next = { ...group, ...changes }; next.label = next.label || 'A'; next.id = slug(`${next.type}-${next.label}`); Object.values(programs).forEach(program => { if (program.group?.id === oldId) program.group = clone(next); }); };
    const move = (id, direction) => { const from = order.indexOf(id); const to = from + direction; if (from < 0 || to < 0 || to >= order.length) return; [order[from], order[to]] = [order[to], order[from]]; renderProgramming(); };
    const renderProgramming = () => { clear(programming); const selected = order.map(exerciseById).filter(Boolean); if (!selected.length) return; programming.append(el('h3', { text: 'Routine programming and order' }), el('p', { class: 'v2-muted', text: 'Drag exercises or use the arrow buttons to reorder. Give adjacent exercises the same group label to run them as a superset or circuit.' })); selected.forEach((item, position) => { const program = programs[item.id] ||= defaultProgram(item); const setType = el('select', {}, [['warm-up','Warm-up'],['working','Working'],['cooldown','Cooldown'],['drop','Drop'],['failure','Failure']].map(([value, text]) => el('option', { value, text }))); setType.value = program.setType || 'working'; setType.addEventListener('change', () => { program.setType = setType.value; }); const optional = el('input', { type: 'checkbox' }); optional.checked = !!program.optional; optional.addEventListener('change', () => { program.optional = optional.checked; }); const groupType = el('select', { 'aria-label': `${item.name} group type` }, [['','Standalone'],['superset','Superset'],['circuit','Circuit']].map(([value, text]) => el('option', { value, text }))); groupType.value = program.group?.type || ''; groupType.addEventListener('change', () => { if (!groupType.value) program.group = null; else { const candidate = { id: slug(`${groupType.value}-${program.group?.label || 'A'}`), type: groupType.value, label: program.group?.label || 'A', rounds: program.group?.rounds || program.sets, restSeconds: program.group?.restSeconds ?? program.restSeconds }; const shared = Object.values(programs).map(value => value.group).find(group => group?.id === candidate.id); program.group = clone(shared || candidate); } renderProgramming(); });
      const fields = el('div', { class: 'v2-grid' }); fields.append(input(program.group ? 'Sets / default rounds' : 'Sets', 'number', program.sets, value => { program.sets = Math.max(1, Number(value) || 1); }, { min: '1', max: '20', step: '1', live: true }), input('Exercise rest (seconds)', 'number', program.restSeconds, value => { program.restSeconds = Math.max(0, Number(value) || 0); }, { min: '0', max: '1800', step: '5', live: true }), input('Target RPE', 'number', program.targetRpe, value => { program.targetRpe = value; }, { min: '1', max: '10', step: '0.5', live: true }), el('div', { class: 'v2-field' }, [el('label', { text: 'Set type' }), setType]), el('div', { class: 'v2-field' }, [el('label', { text: 'Workout group' }), groupType]), el('label', { class: 'v2-check' }, [optional, document.createTextNode('Optional / skippable')])); const groupFields = el('div', { class: 'v2-group-fields' }); if (program.group) { groupFields.append(el('div', { class: 'v2-grid' }, [input('Group label', 'text', program.group.label, value => updateGroup(program.group, { label: value.trim() || 'A' }), { maxlength: '30', live: true }), input('Shared rounds', 'number', program.group.rounds, value => updateGroup(program.group, { rounds: Math.max(1, Number(value) || 1) }), { min: '1', max: '20', step: '1', live: true }), input('Rest after round (seconds)', 'number', program.group.restSeconds, value => updateGroup(program.group, { restSeconds: Math.max(0, Number(value) || 0) }), { min: '0', max: '1800', step: '5', live: true })])); }
      const cardRow = el('div', { class: 'v2-routine-program', draggable: 'true' }, [el('div', { class: 'v2-routine-program-head' }, [el('div', {}, [el('strong', { text: `${position + 1}. ${item.name}` }), el('div', { class: 'v2-meta', text: `${item.target.min}–${item.target.max} ${item.target.unit}` })]), el('div', { class: 'v2-actions' }, [button('↑', () => move(item.id, -1), 'compact'), button('↓', () => move(item.id, 1), 'compact')])]), fields, program.group ? groupFields : null]); cardRow.addEventListener('dragstart', () => { draggedId = item.id; cardRow.classList.add('dragging'); }); cardRow.addEventListener('dragend', () => { draggedId = null; cardRow.classList.remove('dragging'); }); cardRow.addEventListener('dragover', event => event.preventDefault()); cardRow.addEventListener('drop', event => { event.preventDefault(); if (!draggedId || draggedId === item.id) return; const from = order.indexOf(draggedId); const to = order.indexOf(item.id); order.splice(to, 0, order.splice(from, 1)[0]); renderProgramming(); }); programming.append(cardRow); }); };
    const populate = () => {
      clear(library);
      state.library.items.filter(item => !item.archived && item.name.toLowerCase().includes(search.value.toLowerCase())).forEach(item => {
        const check = el('input', { type: 'checkbox' });
        check.checked = chosen.has(item.id);
        check.addEventListener('change', () => { if (check.checked) { chosen.add(item.id); order.push(item.id); programs[item.id] ||= defaultProgram(item); } else { chosen.delete(item.id); order.splice(order.indexOf(item.id), 1); } renderProgramming(); });
        library.append(el('label', {}, [check, document.createTextNode(item.name)]));
      });
    };
    search.addEventListener('input', populate);
    populate();
    renderProgramming();
    const custom = el('input', { type: 'text', placeholder: 'Add a custom exercise to the full list' });
    const addCustom = button('Add custom exercise', async () => {
      let exerciseName = custom.value.trim(); if (exerciseName && !exerciseName.includes(' - ')) exerciseName += ' - Standard';
      if (!exerciseName || state.library.items.some(item => item.name.toLowerCase() === exerciseName.toLowerCase())) return;
      state.library.items.push({ id: slug(exerciseName) + '-' + Date.now(), name: exerciseName, tip: 'Use a controlled, pain-free range of motion.', instructions: ['Set a stable start position.', 'Move through a controlled, pain-free range.', 'Stop the set when position or tempo breaks down.'], visual: 'general', target: targetFor(exerciseName), archived: false });
      chosen.add(state.library.items.at(-1).id);
      programs[state.library.items.at(-1).id] = defaultProgram(state.library.items.at(-1));
      try { await save('library'); custom.value = ''; populate(); renderProgramming(); toast('Custom exercise added.'); } catch (error) { toast(error.message); }
    });
    const submit = button(editing ? 'Save routine' : 'Create routine', null, 'primary');
    submit.type = 'submit';
    const templateSelect = el('select', { 'aria-label': 'Reusable warm-up or cooldown template' }, [el('option', { value: '', text: 'Choose a reusable template' }), ...state.routines.templates.map(template => el('option', { value: template.id, text: `${template.name} (${template.kind})` }))]);
    const applyTemplate = button('Add template', () => { const template = state.routines.templates.find(item => item.id === templateSelect.value); if (!template) return; template.exercises.forEach(exercise => { if (chosen.has(exercise.exerciseId) || !exerciseById(exercise.exerciseId)) return; chosen.add(exercise.exerciseId); order.push(exercise.exerciseId); programs[exercise.exerciseId] = normaliseProgramming(clone(exercise.programming)); }); populate(); renderProgramming(); toast('Template added to this routine draft.'); });
    [
      el('div', { class: 'v2-field' }, [el('label', { text: 'Routine name' }), name]),
      el('div', { class: 'v2-field' }, [el('label', { text: 'Regular training days (optional)' }), schedulePicker, el('span', { class: 'v2-meta', text: 'The Today tab uses these days to build the weekly plan. Individual occurrences can be moved later.' })]),
      el('div', { class: 'v2-field' }, [el('label', { text: 'Exercises' }), search, library]),
      state.routines.templates.length ? el('div', { class: 'v2-custom-row' }, [templateSelect, applyTemplate]) : null,
      programming,
      el('div', { class: 'v2-custom-row' }, [custom, addCustom]),
      submit
    ].filter(Boolean).forEach(node => form.append(node));
    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (!chosen.size) return toast('Choose at least one exercise.');
      const sharedGroups = {}; order.forEach(id => { const group = programs[id]?.group; if (group && !sharedGroups[group.id]) sharedGroups[group.id] = clone(group); }); order.forEach(id => { const group = programs[id]?.group; if (group && sharedGroups[group.id]) programs[id].group = clone(sharedGroups[group.id]); });
      const now = new Date().toISOString(); const nextExercises = order.map(exerciseById).filter(Boolean).map(item => exerciseSnapshot(item, programs[item.id])); const nextSchedule = [...scheduleDays].sort((a, b) => a - b); const changed = !editing || editing.name !== name.value.trim() || JSON.stringify(editing.exercises) !== JSON.stringify(nextExercises) || JSON.stringify(editing.scheduleDays || []) !== JSON.stringify(nextSchedule); const versions = editing ? clone(editing.versions || []) : []; if (editing && changed) versions.push(routineVersionSnapshot(editing));
      const routine = { id: editing?.id || 'routine-' + Date.now(), name: name.value.trim(), exercises: nextExercises, scheduleDays: nextSchedule, version: editing ? (Number(editing.version) || 1) + (changed ? 1 : 0) : 1, versions: versions.slice(-20), createdAt: editing?.createdAt || now, updatedAt: now };
      if (!routine.name) return;
      const index = state.routines.items.findIndex(item => item.id === routine.id);
      if (index >= 0) state.routines.items[index] = routine; else state.routines.items.push(routine);
      try { await save('routines'); state.selectedRoutine = null; renderRoutines(); toast('Routine saved.'); } catch (error) { toast(error.message); }
    });
    card.append(form);
    if (state.routines.templates.length) { const templates = el('div', { class: 'v2-profile' }, [el('h3', { text: 'Reusable warm-up and cooldown templates' })]); state.routines.templates.forEach(template => templates.append(el('div', { class: 'v2-row' }, [el('div', { class: 'grow' }, [el('strong', { text: template.name }), el('div', { class: 'v2-meta', text: `${template.kind} · ${template.exercises.map(exercise => exercise.name).join(' · ')}` })]), button('Delete', () => deleteRoutineTemplate(template.id), 'compact danger')]))); card.append(templates); }
    return card;
  }
  function exerciseLibraryCard() {
    const editing = state.library.items.find(item => item.id === state.editExercise);
    const card = el('div', { class: 'card' });
    card.append(el('h2', { text: editing ? 'Edit exercise' : 'Exercise library' }), el('p', { class: 'v2-muted', text: editing ? 'Changes update the exercise in saved routines. Completed workout history is left untouched.' : 'Search the full list, then open any card for its picture, setup and form steps.' }));
    if (editing) {
      const form = el('form'); const name = el('input', { type: 'text', required: 'true' }); name.value = editing.name;
      const cue = el('textarea', { rows: '3', required: 'true' }); cue.value = editing.tip || '';
      const instructions = el('textarea', { rows: '6', required: 'true', placeholder: 'One instruction per line' }); instructions.value = (editing.instructions || []).join('\n');
      const visual = el('select', { name: 'visual' }, ['general', 'push', 'pull', 'row', 'dip', 'handstand', 'planche', 'lever', 'support', 'core', 'legs', 'stretch', 'mobility', 'weights', 'cardio'].map(value => el('option', { value, text: value[0].toUpperCase() + value.slice(1) }))); visual.value = editing.visual || 'general';
      const unit = el('select', { name: 'unit' }, [el('option', { value: 'reps', text: 'Reps' }), el('option', { value: 'seconds', text: 'Seconds' })]); unit.value = editing.target?.unit || 'reps';
      const linkOptions = label => [el('option', { value: '', text: label }), ...state.library.items.filter(item => !item.archived && item.id !== editing.id).slice().sort((a, b) => a.name.localeCompare(b.name)).map(item => el('option', { value: item.id, text: item.name }))]; const links = progressionFor(editing); const regression = el('select', { 'aria-label': 'Easier regression' }, linkOptions('No linked regression')); regression.value = links.regressionId || ''; const progression = el('select', { 'aria-label': 'Harder progression' }, linkOptions('No linked progression')); progression.value = links.progressionId || '';
      const submit = button('Save exercise', null, 'primary'); submit.type = 'submit';
      form.append(el('div', { class: 'v2-field' }, [el('label', { text: 'Exercise name — use Exercise - Variation' }), name]), el('div', { class: 'v2-field' }, [el('label', { text: 'Key form cue' }), cue]), el('div', { class: 'v2-field' }, [el('label', { text: 'Instructions — one step per line' }), instructions]), el('div', { class: 'v2-grid' }, [input('Target minimum', 'number', editing.target?.min, () => {}, { name: 'min', min: '0', step: '1' }), input('Target maximum', 'number', editing.target?.max, () => {}, { name: 'max', min: '0', step: '1' }), el('div', { class: 'v2-field' }, [el('label', { text: 'Target unit' }), unit]), el('div', { class: 'v2-field' }, [el('label', { text: 'Picture type' }), visual]), el('div', { class: 'v2-field' }, [el('label', { text: 'Easier regression' }), regression]), el('div', { class: 'v2-field' }, [el('label', { text: 'Harder progression' }), progression])]), el('p', { class: 'v2-muted', text: 'Exercises with the same name before the dash are also offered as substitutions automatically.' }), el('div', { class: 'v2-toolbar' }, [submit, button('Cancel', () => { state.editExercise = null; renderRoutines(); })]));
      form.addEventListener('submit', async event => {
        event.preventDefault(); const target = { min: numberOrNull(new FormData(form).get('min')) || 0, max: numberOrNull(new FormData(form).get('max')) || 0, unit: unit.value };
        let nextName = name.value.trim() || editing.name; if (!nextName.includes(' - ')) nextName += ' - Standard'; editing.name = nextName; editing.tip = cue.value.trim() || 'Use a controlled, pain-free range of motion.'; editing.instructions = instructions.value.split('\n').map(value => value.trim()).filter(Boolean); editing.visual = visual.value; editing.target = target; editing.progression = { regressionId: regression.value, progressionId: progression.value };
        let routinesChanged = false, activeChanged = false;
        const sync = exercise => { exercise.name = editing.name; exercise.tip = editing.tip; exercise.instructions = clone(editing.instructions); exercise.visual = editing.visual; exercise.target = clone(target); };
        state.routines.items.forEach(routine => { if (!routine.exercises.some(exercise => exercise.exerciseId === editing.id)) return; const before = routineVersionSnapshot(routine); routine.exercises.forEach(exercise => { if (exercise.exerciseId === editing.id) sync(exercise); }); routine.versions = [...(routine.versions || []), before].slice(-20); routine.version = (Number(routine.version) || 1) + 1; routine.updatedAt = new Date().toISOString(); routinesChanged = true; });
        state.active?.exercises.forEach(exercise => { if (exercise.exerciseId === editing.id) { sync(exercise); activeChanged = true; } }); if (activeChanged && state.active.routineId) state.active.routineVersion = state.routines.items.find(routine => routine.id === state.active.routineId)?.version || state.active.routineVersion;
        try { await save('library'); if (routinesChanged) await save('routines'); if (activeChanged) await save('active'); state.editExercise = null; renderRoutines(); toast('Exercise updated.'); } catch (error) { toast(error.message); }
      });
      card.append(form); return card;
    }
    const search = el('input', { type: 'search', placeholder: 'Search exercises or form cues', 'aria-label': 'Search exercise library' }); search.value = state.exerciseSearch || '';
    const count = el('p', { class: 'v2-diet-note' }); const list = el('div', { class: 'v2-list' }); const redraw = () => { state.exerciseSearch = search.value; clear(list); const query = search.value.trim().toLowerCase(); const visible = state.library.items.filter(item => !item.archived && (!query || item.name.toLowerCase().includes(query) || item.tip?.toLowerCase().includes(query))).slice().sort((a, b) => a.name.localeCompare(b.name)); count.textContent = `${visible.length} of ${state.library.items.filter(item => !item.archived).length} active exercises shown.`;
    visible.forEach(item => {
      const controls = el('div', { class: 'v2-actions' }, [
        button(state.expandedExercise === item.id ? 'Hide guide' : 'Show guide', () => { state.expandedExercise = state.expandedExercise === item.id ? null : item.id; redraw(); }, 'compact'),
        button('Edit', () => { state.editExercise = item.id; renderRoutines(); }, 'compact'),
        button('Archive', async () => {
          if (!confirm(`Remove “${item.name}” from the exercise library? Existing routines and completed sessions keep their copied exercise details.`)) return;
          item.archived = true;
          try { await save('library'); renderRoutines(); toast('Exercise archived from the library.'); } catch (error) { item.archived = false; toast(error.message); }
        }, 'compact danger')
      ]);
      const links = progressionFor(item); const easier = exerciseById(links.regressionId); const harder = exerciseById(links.progressionId); const familyCount = state.library.items.filter(candidate => !candidate.archived && candidate.id !== item.id && exerciseFamily(candidate) === exerciseFamily(item)).length;
      list.append(el('div', { class: 'v2-library-row' }, [el('div', {}, [el('strong', { text: item.name }), el('div', { class: 'v2-meta', text: `${item.target?.min ?? '?'}–${item.target?.max ?? '?'} ${item.target?.unit || 'reps'} · ${item.tip || ''}` }), (easier || harder || familyCount) ? el('div', { class: 'v2-chain' }, [easier ? el('span', { class: 'v2-chip', text: `Easier: ${easier.name}` }) : null, harder ? el('span', { class: 'v2-chip', text: `Harder: ${harder.name}` }) : null, familyCount ? el('span', { class: 'v2-chip', text: `${familyCount} same-family alternative${familyCount === 1 ? '' : 's'}` }) : null]) : null, state.expandedExercise === item.id ? exerciseGuide(item) : null]), controls]));
    });
    if (!visible.length) list.append(el('p', { class: 'v2-muted', text: 'No exercises match this search.' })); };
    search.addEventListener('input', redraw); card.append(search, count, list); redraw(); return card;
  }
  async function deleteRoutine(id) { if (!confirm('Delete this routine? Logged sessions are retained.')) return; state.routines.items = state.routines.items.filter(item => item.id !== id); try { await save('routines'); renderRoutines(); } catch (error) { toast(error.message); } }

  function workoutHistoryCard(filteredSessions = null) {
    const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Workout history' }));
    const sessions = filteredSessions || state.workouts.sessions.slice().sort(byDate).reverse();
    if (!sessions.length) card.append(el('p', { class: 'v2-muted', text: 'No completed workouts yet.' }));
    sessions.slice(0, 60).forEach(session => {
      const detail = session.exercises.map(exercise => exercise.name + ': ' + exercise.sets.map(set => `${set.reps || '—'} @ ${set.load || 'BW'}`).join(', ')).join(' · ');
      const summary = session.summary || buildWorkoutSummary(session); const summaryDetails = el('details', { class: 'v2-exercise-history' }); summaryDetails.append(el('summary', { text: 'Session summary' }), el('div', { class: 'v2-meta', text: `${summary.completedSets}/${summary.plannedSets} sets · ${Math.round(summary.work)} reps/seconds · ${Math.round(summary.loadedVolume)} numeric volume · ${timeDisplay(session.elapsedSeconds || 0)} · ${summary.prs} PR signal${summary.prs === 1 ? '' : 's'} · discomfort ${summary.discomfort}/10${summary.avgRpe === null ? '' : ` · avg RPE ${summary.avgRpe.toFixed(1)}`}` }));
      card.append(el('div', { class: 'v2-row' }, [el('div', { class: 'grow' }, [el('strong', { text: session.date + (session.routineName ? ' — ' + session.routineName : '') + (session.routineVersion ? ` (v${session.routineVersion})` : '') }), el('div', { class: 'v2-meta', text: detail || 'No sets' }), summaryDetails, session.notes ? el('div', { class: 'v2-meta', text: session.notes }) : null]), el('div', { class: 'v2-actions' }, [button('Edit', () => editWorkout(session.id)), button('Delete', () => deleteWorkout(session.id), 'danger')])]));
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

  async function startRoutine(id, draft = null, plan = null) {
    const routine = state.routines.items.find(item => item.id === id); if (!routine && !draft) return; if (state.active && !draft && !confirm('Replace the current live workout draft with this routine?')) return;
    if (!await flushDraftSave()) return; const previous = state.active; workoutUndo = null;
    const nextActive = draft || { id: null, routineId: id, routineName: routine.name, routineVersion: routine.version || 1, scheduledDate: plan?.sourceDate || null, plannedForDate: plan?.date || null, date: isoToday(), startedAt: Date.now(), elapsedSeconds: 0, autoRest: true, restEndsAt: null, exercises: routine.exercises.map(ex => { const next = clone(ex); next.programming = normaliseProgramming(next.programming || defaultProgram(next)); next.sets = plannedSets(next); next.skipped = false; next.quickNotes = { pain: '', failed: false, note: '' }; return next; }), notes: '' };
    state.active = nextActive; if (!await persistDraft()) { if (state.active === nextActive) state.active = previous; renderWorkout(); return; } selectTab('workout'); renderWorkout();
  }
  function programmeTaskPlan(task, exercise) {
    const text = task.target || ''; const setMatch = text.match(/(\d+)×\s*(\d+)(?:[–-](\d+))?/); const minuteMatch = text.match(/(\d+)\s*minute/i); const isTimed = /second|minute|hold|hang|planche/i.test(text) || exercise.target?.unit === 'seconds';
    const sets = setMatch ? Number(setMatch[1]) : /2 easy sets/i.test(text) ? 2 : 1; const minimum = minuteMatch ? Number(minuteMatch[1]) * 60 : setMatch ? Number(setMatch[2]) : exercise.target?.min || 1; const maximum = minuteMatch ? minimum : setMatch && setMatch[3] ? Number(setMatch[3]) : setMatch ? Number(setMatch[2]) : exercise.target?.max || minimum;
    const prep = /wrist|scap|arm-circle|pass-through/.test(task.id); const cooldown = /stretch/.test(task.id); return { sets, restSeconds: prep || cooldown ? 30 : task.id.includes('skill') ? 120 : 60, targetRpe: '', setType: prep ? 'warm-up' : cooldown ? 'cooldown' : 'working', target: { min: minimum, max: maximum, unit: isTimed ? 'seconds' : exercise.target?.unit || 'reps' } };
  }
  async function startProgrammeSession(sessionId) {
    const session = PROGRAMME_SESSIONS.find(item => item[0] === sessionId); if (!session) return;
    if (state.active?.programme?.week === state.programme.currentWeek && state.active?.programme?.sessionId === sessionId) { selectTab('workout'); renderWorkout(); return; }
    if (state.active && !confirm('Replace the current live workout draft with this programme session?')) return;
    const tasks = programmeSessionItems(sessionId); const exercises = tasks.map(task => { const source = libraryExercise(task.exerciseName); const programming = programmeTaskPlan(task, source); const exercise = { exerciseId: source.id, name: source.name, tip: source.tip, instructions: clone(source.instructions || []), visual: source.visual || 'general', target: clone(programming.target), programming, programmeTaskKey: `${sessionId}:${task.id}`, programmeTarget: task.target, programmeLabel: task.label, assistance: '', formQuality: '', tempo: '' }; exercise.sets = plannedSets(exercise); return exercise; });
    if (!await flushDraftSave()) return; const previous = state.active; workoutUndo = null; const nextActive = { id: null, routineId: null, routineName: `Programme · ${session[1]}`, date: isoToday(), startedAt: Date.now(), elapsedSeconds: 0, autoRest: true, restEndsAt: null, exercises, notes: '', programme: { week: state.programme.currentWeek, sessionId, sessionLabel: session[1], focus: session[2], stages: clone(state.programme.skillStages) } }; state.active = nextActive;
    if (!await persistDraft()) { if (state.active === nextActive) state.active = previous; renderWorkout(); return; } selectTab('workout'); renderWorkout(); toast(`${session[1]} programme session loaded.`);
  }
  function programmeWeekRecord(number) { const key = String(number); state.programme.weeklyChecks[key] ||= { sessions: {}, items: {}, deload: false, jointComfort: '', notes: '' }; state.programme.weeklyChecks[key].sessions ||= {}; state.programme.weeklyChecks[key].items ||= {}; return state.programme.weeklyChecks[key]; }
  async function syncProgrammeTask(exercise) {
    if (!state.active?.programme || !exercise.programmeTaskKey) return; const week = programmeWeekRecord(state.active.programme.week); const complete = exercise.sets.length > 0 && exercise.sets.every(set => set.done); if (!!week.items[exercise.programmeTaskKey] === complete) return; week.items[exercise.programmeTaskKey] = complete; try { await save('programme'); } catch (error) { toast(error.message); }
  }
  const hiitRuntime = { status: 'idle', phase: 'ready', round: 0, endAt: null, pausedMs: null, config: null };
  let hiitTicker = null, hiitAudio = null, hiitWakeLock = null;
  function hiitConfigFromControls(controls) { return { workSeconds: Math.min(3600, Math.max(1, Number(controls.work.value) || 40)), restSeconds: Math.min(3600, Math.max(0, Number(controls.rest.value) || 0)), rounds: Math.min(100, Math.max(1, Number(controls.rounds.value) || 10)), prepareSeconds: Math.min(600, Math.max(0, Number(controls.prepare.value) || 0)), sound: controls.sound.checked }; }
  async function saveHiitConfig(config) { const previous = clone(state.settings.hiit); state.settings.hiit = clone(config); try { await save('settings'); return true; } catch (error) { state.settings.hiit = previous; toast(error.message); return false; } }
  async function ensureHiitAudio() { const Audio = window.AudioContext || window.webkitAudioContext; if (!Audio) return false; hiitAudio ||= new Audio(); if (hiitAudio.state === 'suspended') await hiitAudio.resume(); return true; }
  function hiitTone(frequency, duration = .12, delay = 0) { if (!hiitAudio) return; const start = hiitAudio.currentTime + delay; const oscillator = hiitAudio.createOscillator(); const gain = hiitAudio.createGain(); oscillator.type = 'sine'; oscillator.frequency.setValueAtTime(frequency, start); gain.gain.setValueAtTime(.0001, start); gain.gain.exponentialRampToValueAtTime(.22, start + .015); gain.gain.exponentialRampToValueAtTime(.0001, start + duration); oscillator.connect(gain).connect(hiitAudio.destination); oscillator.start(start); oscillator.stop(start + duration + .02); }
  async function hiitAlarm(phase, force = false) { if (!force && !hiitRuntime.config?.sound) return; if (!await ensureHiitAudio()) return; if (phase === 'work') { hiitTone(880, .1); hiitTone(1100, .13, .14); } else if (phase === 'rest') hiitTone(440, .22); else if (phase === 'complete') { hiitTone(880, .12); hiitTone(1100, .12, .16); hiitTone(1320, .2, .32); } else hiitTone(660, .14); }
  async function requestHiitWakeLock() { if (!('wakeLock' in navigator) || document.visibilityState !== 'visible' || hiitRuntime.status !== 'running') return; try { hiitWakeLock = await navigator.wakeLock.request('screen'); hiitWakeLock.addEventListener('release', () => { hiitWakeLock = null; }); } catch { hiitWakeLock = null; } }
  async function releaseHiitWakeLock() { if (!hiitWakeLock) return; try { await hiitWakeLock.release(); } catch { /* Already released by the browser. */ } hiitWakeLock = null; }
  function hiitPhaseDuration() { const config = hiitRuntime.config || state.settings.hiit; return hiitRuntime.phase === 'prepare' ? config.prepareSeconds : hiitRuntime.phase === 'work' ? config.workSeconds : hiitRuntime.phase === 'rest' ? config.restSeconds : 0; }
  function hiitRemainingSeconds() { if (hiitRuntime.status === 'paused') return Math.max(0, Math.ceil(Number(hiitRuntime.pausedMs) / 1000)); if (hiitRuntime.status !== 'running') return hiitRuntime.status === 'complete' ? 0 : Number(state.settings.hiit.prepareSeconds || state.settings.hiit.workSeconds); return Math.max(0, Math.ceil((Number(hiitRuntime.endAt) - Date.now()) / 1000)); }
  function hiitPhaseLabel() { return hiitRuntime.phase === 'prepare' ? 'Get ready' : hiitRuntime.phase === 'work' ? 'Work' : hiitRuntime.phase === 'rest' ? 'Rest' : hiitRuntime.phase === 'complete' ? 'Complete' : 'Ready'; }
  function updateHiitDisplays() { const remaining = hiitRemainingSeconds(); const duration = Math.max(1, hiitPhaseDuration()); const percent = hiitRuntime.status === 'idle' ? 0 : hiitRuntime.status === 'complete' ? 100 : Math.min(100, Math.max(0, (duration - remaining) / duration * 100)); document.querySelectorAll('.v2-hiit').forEach(card => { card.classList.toggle('running', hiitRuntime.status === 'running'); card.classList.toggle('rest', hiitRuntime.phase === 'rest'); card.classList.toggle('complete', hiitRuntime.status === 'complete'); }); document.querySelectorAll('.v2-hiit-phase').forEach(node => node.textContent = hiitPhaseLabel()); document.querySelectorAll('.v2-hiit-clock').forEach(node => node.textContent = String(remaining).padStart(2, '0')); document.querySelectorAll('.v2-hiit-round').forEach(node => node.textContent = hiitRuntime.status === 'idle' ? `${state.settings.hiit.rounds} rounds configured` : `Round ${Math.min(hiitRuntime.round || 1, hiitRuntime.config?.rounds || 1)} of ${hiitRuntime.config?.rounds || state.settings.hiit.rounds}`); document.querySelectorAll('.v2-hiit-progress>span').forEach(node => node.style.width = percent + '%'); }
  function completeHiit() { hiitRuntime.status = 'complete'; hiitRuntime.phase = 'complete'; hiitRuntime.endAt = null; hiitRuntime.pausedMs = null; clearInterval(hiitTicker); hiitTicker = null; releaseHiitWakeLock(); hiitAlarm('complete'); renderWorkout(); }
  function advanceHiitPhase() { const config = hiitRuntime.config; if (hiitRuntime.phase === 'prepare') hiitRuntime.phase = 'work'; else if (hiitRuntime.phase === 'work') { if (hiitRuntime.round >= config.rounds) return completeHiit(); hiitRuntime.phase = config.restSeconds > 0 ? 'rest' : 'work'; if (hiitRuntime.phase === 'work') hiitRuntime.round++; } else if (hiitRuntime.phase === 'rest') { hiitRuntime.round++; hiitRuntime.phase = 'work'; } hiitRuntime.endAt += Math.max(0, hiitPhaseDuration()) * 1000; hiitAlarm(hiitRuntime.phase); }
  function hiitTick() { if (hiitRuntime.status !== 'running') return updateHiitDisplays(); let guard = 0; while (Date.now() >= Number(hiitRuntime.endAt) && hiitRuntime.status === 'running' && guard++ < 205) advanceHiitPhase(); updateHiitDisplays(); }
  async function startHiit(config) { await ensureHiitAudio(); if (!await saveHiitConfig(config)) return; hiitRuntime.config = clone(config); hiitRuntime.status = 'running'; hiitRuntime.phase = config.prepareSeconds > 0 ? 'prepare' : 'work'; hiitRuntime.round = 1; hiitRuntime.pausedMs = null; hiitRuntime.endAt = Date.now() + hiitPhaseDuration() * 1000; clearInterval(hiitTicker); hiitTicker = setInterval(hiitTick, 200); await requestHiitWakeLock(); hiitAlarm(hiitRuntime.phase); renderWorkout(); toast('HIIT timer started. Keep this app open for transition alarms.'); }
  async function pauseHiit() { if (hiitRuntime.status !== 'running') return; hiitRuntime.pausedMs = Math.max(0, Number(hiitRuntime.endAt) - Date.now()); hiitRuntime.status = 'paused'; clearInterval(hiitTicker); hiitTicker = null; await releaseHiitWakeLock(); renderWorkout(); }
  async function resumeHiit() { if (hiitRuntime.status !== 'paused') return; await ensureHiitAudio(); hiitRuntime.status = 'running'; hiitRuntime.endAt = Date.now() + Math.max(0, Number(hiitRuntime.pausedMs)); hiitRuntime.pausedMs = null; hiitTicker = setInterval(hiitTick, 200); await requestHiitWakeLock(); renderWorkout(); }
  async function resetHiit() { clearInterval(hiitTicker); hiitTicker = null; hiitRuntime.status = 'idle'; hiitRuntime.phase = 'ready'; hiitRuntime.round = 0; hiitRuntime.endAt = null; hiitRuntime.pausedMs = null; hiitRuntime.config = null; await releaseHiitWakeLock(); renderWorkout(); }
  function hiitTimerCard() {
    const card = el('div', { class: 'card v2-hiit' }); card.append(el('h2', { text: 'HIIT interval timer' }), el('p', { class: 'v2-muted', text: 'Custom work/rest rounds with automatic transition alarms. Starting the timer also saves these values as your defaults.' })); const config = hiitRuntime.config || state.settings.hiit; const work = el('input', { type: 'number', min: '1', max: '3600', step: '1', required: 'true', 'aria-label': 'HIIT work seconds' }); work.value = config.workSeconds; const rest = el('input', { type: 'number', min: '0', max: '3600', step: '1', required: 'true', 'aria-label': 'HIIT rest seconds' }); rest.value = config.restSeconds; const rounds = el('input', { type: 'number', min: '1', max: '100', step: '1', required: 'true', 'aria-label': 'HIIT rounds' }); rounds.value = config.rounds; const prepare = el('input', { type: 'number', min: '0', max: '600', step: '1', required: 'true', 'aria-label': 'HIIT preparation seconds' }); prepare.value = config.prepareSeconds; const sound = el('input', { type: 'checkbox', 'aria-label': 'HIIT transition sounds' }); sound.checked = config.sound; const controls = { work, rest, rounds, prepare, sound }; const locked = hiitRuntime.status === 'running' || hiitRuntime.status === 'paused'; [work, rest, rounds, prepare, sound].forEach(control => control.disabled = locked); const grid = el('div', { class: 'v2-grid' }, [el('div', { class: 'v2-field' }, [el('label', { text: 'Work (seconds)' }), work]), el('div', { class: 'v2-field' }, [el('label', { text: 'Rest (seconds)' }), rest]), el('div', { class: 'v2-field' }, [el('label', { text: 'Rounds' }), rounds]), el('div', { class: 'v2-field' }, [el('label', { text: 'Preparation (seconds)' }), prepare])]); const soundLabel = el('label', { class: 'v2-check' }, [sound, document.createTextNode('Play an alarm when the phase changes')]); const display = el('div', { class: 'v2-hiit-display' }, [el('div', {}, [el('div', { class: 'v2-hiit-phase', role: 'status', 'aria-live': 'assertive', text: hiitPhaseLabel() }), el('div', { class: 'v2-hiit-round', text: hiitRuntime.status === 'idle' ? `${config.rounds} rounds configured` : `Round ${hiitRuntime.round} of ${config.rounds}` }), el('div', { class: 'v2-hiit-progress' }, [el('span')])]), el('div', { class: 'v2-hiit-clock', role: 'timer', 'aria-label': 'Interval seconds remaining', text: String(hiitRemainingSeconds()).padStart(2, '0') })]); const applyPreset = preset => { work.value = preset[0]; rest.value = preset[1]; rounds.value = preset[2]; prepare.value = preset[3]; }; const presets = el('div', { class: 'v2-hiit-presets' }, [button('40 / 20 × 10', () => applyPreset([40, 20, 10, 10]), 'compact'), button('30 / 30 × 10', () => applyPreset([30, 30, 10, 10]), 'compact'), button('Tabata 20 / 10 × 8', () => applyPreset([20, 10, 8, 10]), 'compact')]); presets.querySelectorAll('button').forEach(item => item.disabled = locked); const actions = el('div', { class: 'v2-toolbar' }); if (hiitRuntime.status === 'running') actions.append(button('Pause intervals', pauseHiit, 'primary')); else if (hiitRuntime.status === 'paused') actions.append(button('Resume intervals', resumeHiit, 'primary')); else actions.append(button(hiitRuntime.status === 'complete' ? 'Start again' : 'Start intervals', () => startHiit(hiitConfigFromControls(controls)), 'primary')); actions.append(button('Reset', resetHiit)); if (!locked) actions.append(button('Save defaults', async () => { if (await saveHiitConfig(hiitConfigFromControls(controls))) { renderWorkout(); toast('HIIT defaults saved.'); } }, 'compact')); actions.append(button('Test sound', () => hiitAlarm('work', true), 'compact')); card.append(grid, soundLabel, el('p', { class: 'v2-meta', text: 'Presets' }), presets, display, actions, el('p', { class: 'v2-muted', text: 'The app requests a screen wake lock while running when the browser supports it. Mobile operating systems may still suppress web audio if the app is closed.' })); setTimeout(updateHiitDisplays, 0); return card;
  }
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && hiitRuntime.status === 'running') requestHiitWakeLock(); });
  let timerHandle, restHandle, draftSaveTimer = null, workoutUndo = null, draftSaveQueue = Promise.resolve(true);
  let draftSaveStatus = { state: 'saved', text: 'All changes saved' };
  function setDraftSaveStatus(status, text) { draftSaveStatus = { state: status, text }; document.querySelectorAll('.v2-save-status').forEach(node => { node.className = 'v2-save-status ' + status; node.textContent = text; }); }
  function captureWorkoutUndo(label) { if (!state.active) return; const snapshot = clone(state.active); snapshot.elapsedSeconds = sessionElapsed(state.active); snapshot.startedAt = state.active.startedAt ? Date.now() : null; workoutUndo = { label, active: snapshot }; document.querySelectorAll('.v2-undo-workout').forEach(node => { node.disabled = false; node.textContent = `Undo: ${label}`; }); }
  async function undoWorkoutAction() { if (!workoutUndo) return; const restore = workoutUndo; workoutUndo = null; state.active = restore.active; if (!await persistDraft()) return renderWorkout(); renderWorkout(); toast(`${restore.label} undone.`); }
  function renderWorkout() {
    const panel = clear($('#tab-workout')); clearInterval(timerHandle); clearInterval(restHandle);
    if (!state.active) {
      const card = el('div', { class: 'card' });
      card.append(el('h2', { text: 'Load a workout routine' }), el('p', { class: 'v2-muted', text: 'Choose a routine to begin. Your live session stays saved if the page closes.' }));
      state.routines.items.forEach(routine => card.append(el('div', { class: 'v2-row' }, [el('strong', { class: 'grow', text: routine.name }), button('Start', () => startRoutine(routine.id), 'primary')])));
      panel.append(hiitTimerCard(), card); return;
    }
    const active = state.active; active.autoRest = active.autoRest !== false; active.exercises.forEach(exercise => { exercise.quickNotes ||= { pain: '', failed: false, note: '' }; exercise.programming = normaliseProgramming(exercise.programming || defaultProgram(exercise)); }); panel.classList.toggle('v2-workout-compact', state.settings.compactWorkout === true);
    const top = el('div', { class: 'card v2-workout-controls' }); const elapsed = el('div', { class: 'v2-timer', text: timeDisplay(sessionElapsed(active)) }); timerHandle = setInterval(() => elapsed.textContent = timeDisplay(sessionElapsed(active)), 1000);
    const timerToggle = button(active.startedAt ? 'Pause' : 'Resume', () => toggleSessionTimer(), 'compact'); const compactToggle = button(state.settings.compactWorkout ? 'Full details' : 'Compact mode', () => toggleCompactWorkout(), 'compact');
    top.append(el('div', { class: 'v2-control-strip' }, [el('div', {}, [el('h2', { text: active.id ? 'Edit workout' : active.routineName }), el('div', { class: 'v2-meta', text: `${active.routineVersion ? `Routine version ${active.routineVersion}` : 'Live session'}${active.scheduledDate ? ` · scheduled occurrence ${active.scheduledDate}` : ''}` }), elapsed]), el('div', { class: 'v2-actions' }, [timerToggle, compactToggle, button('Discard draft', () => discardWorkout(), 'danger compact')])]));
    const date = el('input', { type: 'date', 'aria-label': 'Workout date' }); date.value = active.date; date.addEventListener('change', () => { active.date = date.value; persistDraft(); }); const autoRest = el('input', { type: 'checkbox' }); autoRest.checked = active.autoRest; autoRest.addEventListener('change', () => { active.autoRest = autoRest.checked; persistDraft(); }); const undo = button(workoutUndo ? `Undo: ${workoutUndo.label}` : 'Nothing to undo', () => undoWorkoutAction(), 'compact v2-undo-workout'); undo.disabled = !workoutUndo;
    top.append(el('div', { class: 'v2-control-strip' }, [el('div', { class: 'v2-actions' }, [date, el('label', { class: 'v2-check' }, [autoRest, document.createTextNode('Automatic rest')])]), el('div', { class: 'v2-actions' }, [el('span', { class: 'v2-save-status ' + draftSaveStatus.state, role: 'status', 'aria-live': 'polite', text: draftSaveStatus.text }), undo])])); const readinessSignals = currentReadinessSignals(); if (readinessSignals.length) top.append(el('div', { class: 'v2-summary v2-warning' }, readinessSignals.map(signal => el('div', { text: '• ' + signal })))); top.append(restTimer(), loadTools(), manageActiveExercises()); panel.append(top, hiitTimerCard()); startRestTicker();
    for (let index = 0; index < active.exercises.length;) { const exercise = active.exercises[index]; const group = exercise.programming?.group; if (!group) { panel.append(workoutExercise(exercise, index)); index += 1; continue; } const members = []; let cursor = index; while (cursor < active.exercises.length && active.exercises[cursor].programming?.group?.id === group.id) members.push([active.exercises[cursor], cursor++]); const nextRound = nextIncompleteRound(group, members.map(item => item[0])); const wrapper = el('section', { class: 'v2-workout-group', 'aria-label': `${group.type} ${group.label}` }); const roundButton = button(nextRound === null ? 'All rounds complete' : `Complete round ${nextRound + 1}`, () => completeGroupRound(group, members.map(item => item[0]), nextRound), 'primary compact'); roundButton.disabled = nextRound === null; wrapper.append(el('div', { class: 'v2-group-head' }, [el('span', { class: 'v2-badge', text: `${group.type === 'superset' ? 'Superset' : 'Circuit'} ${group.label}` }), el('div', { class: 'v2-meta', text: `${group.rounds || members[0][0].sets.length} shared rounds · ${group.restSeconds || 0}s rest after each round · complete one set of each exercise per round` }), el('div', { class: 'v2-round-actions' }, [roundButton, el('span', { class: 'v2-meta', text: `${completedRoundCount(group, members.map(item => item[0]))}/${group.rounds || members[0][0].sets.length} rounds complete` })])])); members.forEach(([member, memberIndex]) => wrapper.append(workoutExercise(member, memberIndex))); panel.append(wrapper); index = cursor; }
    const notes = el('textarea', { rows: '3', placeholder: 'Session notes: energy, pain, form, adjustments' }); notes.value = active.notes || ''; notes.addEventListener('input', () => { active.notes = notes.value; scheduleDraftSave(); }); const saveCard = el('div', { class: 'card' }); saveCard.append(el('label', { text: 'Session notes' }), notes, button(active.id ? 'Save corrections' : 'Finish workout', finishWorkout, 'primary')); panel.append(saveCard);
  }
  function workoutExercise(exercise, index) {
    const library = state.library.items.find(item => item.id === exercise.exerciseId) || exercise; const program = normaliseProgramming(exercise.programming || defaultProgram(exercise)); const card = el('section', { class: 'v2-exercise' + (exercise.skipped ? ' skipped' : '') }); const previous = previousExercise(exercise, state.active.id); const target = exercise.target || library.target || targetFor(exercise.name); exercise.quickNotes ||= { pain: '', failed: false, note: '' };
    const moveUp = button('↑', () => moveActiveExercise(index, -1), 'compact'); moveUp.disabled = index === 0; moveUp.setAttribute('aria-label', `Move ${exercise.name} earlier`); const moveDown = button('↓', () => moveActiveExercise(index, 1), 'compact'); moveDown.disabled = index === state.active.exercises.length - 1; moveDown.setAttribute('aria-label', `Move ${exercise.name} later`); const headingActions = [moveUp, moveDown]; if (program.optional) headingActions.push(button(exercise.skipped ? 'Restore optional' : 'Skip optional', async () => { captureWorkoutUndo(exercise.skipped ? 'restore optional exercise' : 'skip optional exercise'); exercise.skipped = !exercise.skipped; if (!await persistDraft()) return renderWorkout(); renderWorkout(); }, 'compact')); headingActions.push(button('Remove', () => removeActiveExercise(index), 'danger compact'));
    const heading = el('div', { class: 'v2-session-head' }, [el('div', {}, [el('span', { class: 'v2-exercise-position', text: `Exercise ${index + 1} of ${state.active.exercises.length}` }), el('h3', { text: exercise.programmeLabel || exercise.name }), program.optional ? el('span', { class: 'v2-badge', text: 'Optional' }) : null]), el('div', { class: 'v2-actions' }, headingActions)]); card.append(heading); if (exercise.programmeLabel) card.append(el('div', { class: 'v2-meta', text: `${exercise.name} · programme target: ${exercise.programmeTarget}` }));
    if (exercise.skipped) { card.append(el('p', { class: 'v2-muted', text: 'Skipped for this session. It remains in the routine and does not count against completion.' })); return card; }
    card.append(el('div', { class: 'v2-meta', text: `Plan: ${program.group?.rounds || program.sets || exercise.sets.length} ${program.setType || 'working'} sets · ${target.min}–${target.max} ${target.unit} · ${program.group?.restSeconds ?? program.restSeconds ?? 0}s rest${program.targetRpe ? ' · target RPE ' + program.targetRpe : ''}` }));
    const prior = el('div', { class: 'v2-row' }, [el('div', { class: 'grow v2-meta', text: previous ? 'Previous: ' + previous.sets.map(set => `${set.reps || '—'} @ ${set.load || 'BW'}`).join(', ') : 'No previous logged performance.' }), previous ? button('Prefill last workout', () => prefillPreviousExercise(exercise, previous), 'compact') : null]); card.append(prior, progressionPanel(exercise), exerciseHistoryDetails(exercise));
    const details = el('details', { class: 'v2-workout-details' }); details.append(el('summary', { text: 'Form guide, substitutions and RPE help' })); const loadDetails = () => { if (details.dataset.loaded) return; details.dataset.loaded = 'true'; details.append(exerciseGuide(library), substitutionControls(exercise)); if (exercise.substitutionHistory?.length) details.append(el('div', { class: 'v2-meta', text: 'Substitution: ' + exercise.substitutionHistory.map(item => `${item.from} → ${item.to}`).join(' · ') })); details.append(el('div', { class: 'v2-meta', text: 'Set fields: reps or seconds · load/variation · effort. RPE is effort on a 1–10 scale: 7 ≈ 3 reps left, 8 ≈ 2, 9 ≈ 1, 10 = maximum effort.' })); }; details.addEventListener('toggle', () => { if (details.open) loadDetails(); }); if (!state.settings.compactWorkout) { loadDetails(); details.open = true; } card.append(details, exerciseQuickNotes(exercise));
    const rows = el('div'); const redraw = () => { clear(rows); exercise.sets.forEach((set, setIndex) => rows.append(setRow(exercise, set, setIndex, redraw))); }; redraw(); card.append(rows, button('+ Add set', async () => { captureWorkoutUndo('add set'); exercise.sets.push({ reps: '', load: '', rpe: '', done: false, type: program.setType || 'working', targetRpe: program.targetRpe || '', restSeconds: Number(program.group?.restSeconds ?? program.restSeconds) || 0 }); if (!await persistDraft()) return renderWorkout(); await syncProgrammeTask(exercise); redraw(); })); return card;
  }
  function exerciseQuickNotes(exercise) { const assistance = el('input', { type: 'text', placeholder: 'Band, assistance, range or variation', 'aria-label': `${exercise.name} assistance or variation` }); assistance.value = exercise.assistance || ''; const tempo = el('input', { type: 'text', placeholder: 'e.g. 3-1-1 or 5s negative', 'aria-label': `${exercise.name} tempo` }); tempo.value = exercise.tempo || ''; const quality = el('select', { 'aria-label': `${exercise.name} form quality` }, [el('option', { value: '', text: 'Form quality — not rated' }), el('option', { value: 'needs-work', text: 'Needs work' }), el('option', { value: 'controlled', text: 'Controlled' }), el('option', { value: 'clean', text: 'Clean' })]); quality.value = exercise.formQuality || ''; const pain = el('input', { type: 'number', min: '0', max: '10', step: '1', placeholder: '0–10', 'aria-label': `${exercise.name} discomfort 0 to 10` }); pain.value = exercise.quickNotes.pain ?? ''; const note = el('input', { type: 'text', placeholder: 'Quick note: grip, range, cue or adjustment', 'aria-label': `${exercise.name} quick note` }); note.value = exercise.quickNotes.note || ''; const failed = el('input', { type: 'checkbox', 'aria-label': `${exercise.name} failed or shortened set` }); failed.checked = exercise.quickNotes.failed === true; const saveField = (node, event, fn) => node.addEventListener(event, () => { fn(); scheduleDraftSave(); }); saveField(assistance, 'input', () => exercise.assistance = assistance.value.trim()); saveField(tempo, 'input', () => exercise.tempo = tempo.value.trim()); saveField(quality, 'change', () => exercise.formQuality = quality.value); saveField(pain, 'input', () => exercise.quickNotes.pain = pain.value); saveField(note, 'input', () => exercise.quickNotes.note = note.value.trim()); saveField(failed, 'change', () => exercise.quickNotes.failed = failed.checked); return el('div', { class: 'v2-quick-notes' }, [el('div', { class: 'v2-grid' }, [el('div', { class: 'v2-field' }, [el('label', { text: 'Assistance / variation' }), assistance]), el('div', { class: 'v2-field' }, [el('label', { text: 'Tempo' }), tempo]), el('div', { class: 'v2-field' }, [el('label', { text: 'Form quality' }), quality]), el('div', { class: 'v2-field' }, [el('label', { text: 'Discomfort (0–10)' }), pain]), el('div', { class: 'v2-field' }, [el('label', { text: 'Quick note' }), note]), el('label', { class: 'v2-check' }, [failed, document.createTextNode('Failed or shortened set')])])]); }
  function substitutionControls(exercise) { const current = exerciseById(exercise.exerciseId) || exercise; const links = progressionFor(current); const easier = exerciseById(links.regressionId); const harder = exerciseById(links.progressionId); const sameFamily = state.library.items.filter(item => !item.archived && item.id !== current.id && exerciseFamily(item) === exerciseFamily(current)); const rest = state.library.items.filter(item => !item.archived && item.id !== current.id && !sameFamily.some(match => match.id === item.id)).slice().sort((a, b) => a.name.localeCompare(b.name)); const select = el('select', { 'aria-label': `Substitute ${exercise.name}` }, [el('option', { value: '', text: 'Choose another exercise' })]); const recommended = document.createElement('optgroup'); recommended.label = 'Recommended / same family'; [easier, harder, ...sameFamily].filter(Boolean).filter((item, position, all) => all.findIndex(candidate => candidate.id === item.id) === position).forEach(item => recommended.append(el('option', { value: item.id, text: item.name }))); if (recommended.children.length) select.append(recommended); const all = document.createElement('optgroup'); all.label = 'Full exercise library'; rest.forEach(item => all.append(el('option', { value: item.id, text: item.name }))); select.append(all); const controls = el('div', {}, [el('div', { class: 'v2-substitute' }, [select, button('Replace exercise', () => replaceActiveExercise(exercise, select.value), 'compact')]), el('div', { class: 'v2-chain' }, [easier ? button('Use easier: ' + easier.name, () => replaceActiveExercise(exercise, easier.id), 'compact') : null, harder ? button('Use harder: ' + harder.name, () => replaceActiveExercise(exercise, harder.id), 'compact') : null])]); return controls; }
  function manageActiveExercises() { const details = el('details', { class: 'v2-manage-exercises' }); const select = el('select', { 'aria-label': 'Exercise to add during workout' }, [el('option', { value: '', text: 'Choose an exercise to add' }), ...state.library.items.filter(item => !item.archived).slice().sort((a, b) => a.name.localeCompare(b.name)).map(item => el('option', { value: item.id, text: item.name }))]); details.append(el('summary', { text: 'Manage exercises during this session' }), el('div', { class: 'v2-manage-row' }, [select, button('Add exercise', () => addActiveExercise(select.value), 'primary compact')])); return details; }
  async function addActiveExercise(exerciseId) { const source = exerciseById(exerciseId); if (!source) return; captureWorkoutUndo('add exercise'); const exercise = exerciseSnapshot(source, defaultProgram(source)); exercise.sets = plannedSets(exercise); exercise.quickNotes = { pain: '', failed: false, note: '' }; exercise.addedDuringWorkout = true; state.active.exercises.push(exercise); if (!await persistDraft()) return renderWorkout(); renderWorkout(); toast(`${source.name} added to this session.`); }
  async function moveActiveExercise(index, direction) { const to = index + direction; if (to < 0 || to >= state.active.exercises.length) return; captureWorkoutUndo('reorder exercises'); [state.active.exercises[index], state.active.exercises[to]] = [state.active.exercises[to], state.active.exercises[index]]; if (!await persistDraft()) return renderWorkout(); renderWorkout(); }
  async function removeActiveExercise(index) { const exercise = state.active.exercises[index]; if (!exercise) return; captureWorkoutUndo('remove exercise'); state.active.exercises.splice(index, 1); if (!await persistDraft()) return renderWorkout(); renderWorkout(); toast(`${exercise.name} removed from this session.`, undoWorkoutAction); }
  async function prefillPreviousExercise(exercise, previous) { captureWorkoutUndo('prefill previous performance'); exercise.sets = exercise.sets.map((set, index) => { const source = previous.sets[index] || previous.sets.at(-1); return source ? { ...set, reps: source.reps || '', load: source.load || '', rpe: source.rpe || '', done: false } : set; }); if (!await persistDraft()) return renderWorkout(); renderWorkout(); toast('Previous performance copied; completion boxes remain clear.'); }
  async function replaceActiveExercise(exercise, replacementId) { const replacement = exerciseById(replacementId); if (!replacement || replacement.id === exercise.exerciseId) return; captureWorkoutUndo('substitute exercise'); const from = exercise.name; exercise.substitutionHistory ||= []; exercise.substitutionHistory.push({ from, to: replacement.name, at: new Date().toISOString() }); exercise.exerciseId = replacement.id; exercise.name = replacement.name; exercise.tip = replacement.tip; exercise.instructions = clone(replacement.instructions || []); exercise.visual = replacement.visual || 'general'; if (!await persistDraft()) return renderWorkout(); renderWorkout(); toast(`Replaced ${from} with ${replacement.name}; sets and programming were preserved.`, undoWorkoutAction); }
  function groupMembers(group) { return state.active.exercises.filter(exercise => exercise.programming?.group?.id === group.id && !exercise.skipped); }
  function roundIsComplete(group, index, members = groupMembers(group)) { return members.length > 0 && members.every(exercise => !exercise.sets[index] || exercise.sets[index].done); }
  function nextIncompleteRound(group, members = groupMembers(group)) { const rounds = Math.max(1, Number(group.rounds) || Math.max(...members.map(exercise => exercise.sets.length), 1)); for (let index = 0; index < rounds; index++) if (!roundIsComplete(group, index, members)) return index; return null; }
  function completedRoundCount(group, members = groupMembers(group)) { const rounds = Math.max(1, Number(group.rounds) || Math.max(...members.map(exercise => exercise.sets.length), 1)); return Array.from({ length: rounds }, (_, index) => roundIsComplete(group, index, members)).filter(Boolean).length; }
  async function completeGroupRound(group, members, index) { if (index === null) return; captureWorkoutUndo('complete group round'); members.filter(exercise => !exercise.skipped).forEach(exercise => { if (exercise.sets[index]) exercise.sets[index].done = true; }); if (state.active.autoRest && Number(group.restSeconds) > 0) { state.active.restEndsAt = Date.now() + Number(group.restSeconds) * 1000; state.active.restLabel = `${group.type === 'superset' ? 'Superset' : 'Circuit'} ${group.label}`; } if (!await persistDraft()) return renderWorkout(); if (state.active.programme) { const week = programmeWeekRecord(state.active.programme.week); members.forEach(exercise => { if (exercise.programmeTaskKey) week.items[exercise.programmeTaskKey] = exercise.sets.length > 0 && exercise.sets.every(set => set.done); }); try { await save('programme'); } catch (error) { toast(error.message); } } renderWorkout(); }
  function restTimer() { const bar = el('div', { class: 'v2-toolbar' }); bar.append(el('div', { class: 'v2-timer v2-rest-display', text: restDisplayText() }), button('60s', () => startRestTimer(60, 'Manual rest')), button('90s', () => startRestTimer(90, 'Manual rest')), button('2 min', () => startRestTimer(120, 'Manual rest')), button('Stop', () => stopRestTimer())); return bar; }
  function restDisplayText() { if (!state.active?.restEndsAt) return 'Rest ready'; const remaining = Math.max(0, Math.ceil((Number(state.active.restEndsAt) - Date.now()) / 1000)); return remaining ? `Rest ${timeDisplay(remaining)}${state.active.restLabel ? ' · ' + state.active.restLabel : ''}` : 'Rest complete'; }
  function updateRestDisplays() { document.querySelectorAll('.v2-rest-display').forEach(node => node.textContent = restDisplayText()); }
  function startRestTicker() { clearInterval(restHandle); updateRestDisplays(); if (!state.active?.restEndsAt) return; restHandle = setInterval(() => { if (!state.active?.restEndsAt) { clearInterval(restHandle); updateRestDisplays(); return; } if (Date.now() >= Number(state.active.restEndsAt)) { clearInterval(restHandle); state.active.restEndsAt = null; state.active.restLabel = ''; updateRestDisplays(); persistDraft(); toast('Rest complete.'); return; } updateRestDisplays(); }, 250); }
  async function startRestTimer(seconds, label = 'Rest') { if (!state.active || !Number(seconds)) return; state.active.restEndsAt = Date.now() + Number(seconds) * 1000; state.active.restLabel = label; if (!await persistDraft()) return renderWorkout(); startRestTicker(); }
  async function stopRestTimer() { if (!state.active) return; state.active.restEndsAt = null; state.active.restLabel = ''; clearInterval(restHandle); updateRestDisplays(); if (!await persistDraft()) renderWorkout(); }
  async function maybeStartAutoRest(exercise, setIndex) { if (!state.active?.autoRest) return; const group = exercise.programming?.group; if (group) { if (roundIsComplete(group, setIndex) && Number(group.restSeconds) > 0) await startRestTimer(group.restSeconds, `${group.type === 'superset' ? 'Superset' : 'Circuit'} ${group.label}`); return; } const seconds = Number(exercise.sets[setIndex]?.restSeconds ?? exercise.programming?.restSeconds) || 0; if (seconds > 0) await startRestTimer(seconds, exercise.name); }
  function setRow(exercise, set, index, redraw) { const done = el('input', { type: 'checkbox', 'aria-label': 'Mark set ' + (index + 1) + ' complete' }); done.checked = !!set.done; done.addEventListener('change', async () => { captureWorkoutUndo(done.checked ? 'complete set' : 'reopen set'); set.done = done.checked; if (!await persistDraft()) return renderWorkout(); await syncProgrammeTask(exercise); if (set.done) await maybeStartAutoRest(exercise, index); redraw(); }); const unit = exercise.target?.unit === 'seconds' ? 'Seconds' : 'Reps'; const reps = el('input', { type: 'number', min: '0', step: '1', placeholder: unit, 'aria-label': 'Set ' + (index + 1) + ' ' + unit.toLowerCase() }); reps.value = set.reps; reps.addEventListener('input', () => { set.reps = reps.value; scheduleDraftSave(); }); const load = el('input', { type: 'text', placeholder: 'Load / variation', 'aria-label': 'Set ' + (index + 1) + ' load or variation' }); load.value = set.load; load.addEventListener('input', () => { set.load = load.value; scheduleDraftSave(); }); const rpe = el('input', { type: 'number', min: '1', max: '10', step: '0.5', placeholder: set.targetRpe ? 'RPE ' + set.targetRpe : 'Effort 1–10', 'aria-label': 'Set ' + (index + 1) + ' effort, RPE 1 to 10' }); rpe.value = set.rpe; rpe.addEventListener('input', () => { set.rpe = rpe.value; scheduleDraftSave(); }); const type = el('select', { 'aria-label': 'Set ' + (index + 1) + ' type' }, ['warm-up', 'working', 'cooldown', 'drop', 'failure'].map(value => el('option', { value, text: value }))); type.value = set.type || 'working'; type.addEventListener('change', () => { set.type = type.value; scheduleDraftSave(); }); const copy = button('↳', async () => { if (index < 1) return; captureWorkoutUndo('copy previous set'); const previous = exercise.sets[index - 1]; set.reps = previous.reps; set.load = previous.load; set.rpe = previous.rpe; if (!await persistDraft()) return renderWorkout(); redraw(); }, 'compact'); copy.disabled = index < 1; copy.setAttribute('aria-label', index < 1 ? 'No previous set to copy' : `Copy values from set ${index} into set ${index + 1}`); const remove = button('×', async () => { captureWorkoutUndo('remove set'); exercise.sets.splice(index, 1); if (!await persistDraft()) return renderWorkout(); await syncProgrammeTask(exercise); redraw(); toast('Set removed.', undoWorkoutAction); }, 'danger compact'); remove.setAttribute('aria-label', `Remove set ${index + 1}`); return el('div', { class: 'v2-set' + (set.done ? ' done' : '') }, [done, type, reps, load, rpe, el('div', { class: 'v2-set-actions' }, [copy, remove])]); }
  function sessionElapsed(active) { return Math.max(0, Math.round((Number(active?.elapsedSeconds) || 0) + (active?.startedAt ? (Date.now() - Number(active.startedAt)) / 1000 : 0))); }
  function timeDisplay(total) { total = Math.max(0, Math.round(Number(total) || 0)); const hours = Math.floor(total / 3600); const minutes = Math.floor(total % 3600 / 60); const seconds = total % 60; return (hours ? String(hours).padStart(2, '0') + ':' : '') + String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0'); }
  async function toggleSessionTimer() { if (!state.active) return; if (state.active.startedAt) { state.active.elapsedSeconds = sessionElapsed(state.active); state.active.startedAt = null; } else state.active.startedAt = Date.now(); await persistDraft(); renderWorkout(); }
  async function toggleCompactWorkout() { const previous = state.settings.compactWorkout === true; state.settings.compactWorkout = !previous; try { await save('settings'); renderWorkout(); } catch (error) { state.settings.compactWorkout = previous; toast(error.message); } }
  function scheduleDraftSave() { setDraftSaveStatus('saving', 'Unsaved changes…'); clearTimeout(draftSaveTimer); draftSaveTimer = setTimeout(() => { draftSaveTimer = null; persistDraft(); }, 400); }
  function persistDraft() { clearTimeout(draftSaveTimer); draftSaveTimer = null; setDraftSaveStatus('saving', 'Saving…'); draftSaveQueue = draftSaveQueue.catch(() => false).then(() => save('active')).then(() => { setDraftSaveStatus('saved', `Saved ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`); return true; }).catch(error => { setDraftSaveStatus('error', 'Save failed — retrying is safe'); toast(error.message); return false; }); return draftSaveQueue; }
  function flushDraftSave() { if (draftSaveTimer) return persistDraft(); return draftSaveQueue; }
  async function discardWorkout() { if (!confirm('Discard this live workout?')) return; clearTimeout(draftSaveTimer); draftSaveTimer = null; await draftSaveQueue.catch(() => {}); const previous = state.active; state.active = null; workoutUndo = null; clearInterval(timerHandle); clearInterval(restHandle); if (!await persistDraft()) { if (!state.active) state.active = previous; } renderWorkout(); }
  function previousExercise(reference, excludeId) { return state.workouts.sessions.slice().sort(byDate).reverse().find(session => session.id !== excludeId && session.exercises.some(exercise => sameExercise(exercise, reference)))?.exercises.find(exercise => sameExercise(exercise, reference)); }
  async function finishWorkout() { if (!await flushDraftSave()) return; const active = state.active; if (!active) return; active.elapsedSeconds = sessionElapsed(active); active.startedAt = null; active.restEndsAt = null; active.restLabel = ''; active.updatedAt = new Date().toISOString(); if (!active.exercises.some(exercise => !exercise.skipped && exercise.sets.some(set => set.done || set.reps))) return toast('Log at least one set before saving.'); if (active.programme) { const week = programmeWeekRecord(active.programme.week); active.exercises.forEach(exercise => { if (exercise.programmeTaskKey) week.items[exercise.programmeTaskKey] = exercise.programming?.optional && exercise.skipped ? true : exercise.sets.length > 0 && exercise.sets.every(set => set.done); }); const taskKeys = programmeSessionItems(active.programme.sessionId).map(task => `${active.programme.sessionId}:${task.id}`); week.sessions[active.programme.sessionId] = taskKeys.every(key => week.items[key]); }
    const completed = clone(active); const index = state.workouts.sessions.findIndex(session => session.id === completed.id); if (index < 0) { completed.id = 'workout-' + Date.now(); completed.createdAt = completed.updatedAt; } completed.summary = buildWorkoutSummary(completed, state.workouts.sessions.filter(session => session.id !== completed.id)); if (index >= 0) state.workouts.sessions[index] = completed; else state.workouts.sessions.push(completed); state.workouts.sessions.sort(byDate); state.active = null; state.lastWorkoutId = completed.id; workoutUndo = null; clearInterval(timerHandle); clearInterval(restHandle); try { if (active.programme) await save('programme'); await save('workouts'); await save('active'); setDraftSaveStatus('saved', 'All changes saved'); render(); selectTab('records'); renderRecords(); toast(index >= 0 ? 'Workout corrections saved.' : 'Workout saved — summary ready.'); } catch (error) { toast(error.message); } }

  function programmeWeek() {
    return programmeWeekRecord(state.programme.currentWeek);
  }
  function programmeSessionItems(sessionId) {
    const stage = skillId => PROGRAMME_SKILLS[skillId].stages[Math.max(0, Number(state.programme.skillStages[skillId] || 1) - 1)];
    const task = (id, exerciseName, target, label = exerciseName) => ({ id, exerciseName, target, label });
    const sessions = {
      mon: [task('wrist-circles', 'Wrist - Circles', '1 minute each direction'), task('wrist-walks', 'Wrist - Quadruped walks', '2×6 slow steps'), task('scap-pull', 'Pull-up - Scapular', '2×8'), task('skill', stage('muscleUp')[2], stage('muscleUp')[0], 'Current muscle-up stage'), task('ring-row', 'Row - Rings', '3×8–12'), task('transition-hold', 'Support hold - False-grip transition', '2×20 seconds'), task('lat-stretch', 'Stretch - Lat on bench', '2×30 seconds'), task('wrist-flex', 'Stretch - Wrist flexion', '2×20 seconds')],
      tue: [task('wrist-circles', 'Wrist - Circles', '1 minute each direction'), task('wrist-walks', 'Wrist - Quadruped walks', '2×6 slow steps'), task('scap-push', 'Scapular push-up - Straight arm', '2×10'), task('skill', stage('hspu')[2], stage('hspu')[0], 'Current HSPU stage'), task('wrist-iso', 'Wrist - Extension isometric', '3×20 seconds'), task('pike', 'Push-up - Pike', '3×8–12'), task('wrist-stretch', 'Stretch - Wrist extension', '2×20 seconds'), task('shoulder-stretch', 'Stretch - Shoulder flexion at wall', '2×30 seconds')],
      thu: [task('wrist-circles', 'Wrist - Circles', '1 minute each direction'), task('wrist-walks', 'Wrist - Quadruped walks', '2×6 slow steps'), task('wrist-iso', 'Wrist - Extension isometric', '3×20 seconds'), task('scap-hold', 'Scapular protraction - Hold', '3×20 seconds'), task('skill', stage('planche')[2], stage('planche')[0], 'Current planche stage'), task('support', 'Support hold - Parallettes', '3×20–30 seconds'), task('compression', 'Compression - Seated leg lift', '3×8–12'), task('wrist-stretch', 'Stretch - Wrist extension', '2×20 seconds'), task('chest-stretch', 'Stretch - Chest doorway', '2×30 seconds')],
      sat: [task('wrist-circles', 'Wrist - Circles', '1 minute each direction'), task('arm-circles', 'Arm circle - Mobility', '1 minute'), task('pass-through', 'Shoulder pass-through - Band', '2×10'), task('muscle-light', stage('muscleUp')[2], '2 easy sets at least one stage below current', 'Light muscle-up practice'), task('hspu-light', stage('hspu')[2], '2 easy sets at least one stage below current', 'Light HSPU practice'), task('planche-light', stage('planche')[2], '2 easy sets at least one stage below current', 'Light planche practice'), task('hollow', 'Hollow body - Hold', '3×20–30 seconds'), task('lat-stretch', 'Stretch - Lat on bench', '2×30 seconds'), task('chest-stretch', 'Stretch - Chest doorway', '2×30 seconds'), task('wrist-stretch', 'Stretch - Wrist extension', '2×20 seconds')]
    };
    return sessions[sessionId] || [];
  }
  async function saveProgramme(message = 'Programme progress saved.') { try { await save('programme'); toast(message); } catch (error) { toast(error.message); } }
  function renderProgramme() {
    const panel = clear($('#tab-programme')); const progress = state.programme; const week = programmeWeek(); const phase = PROGRAMME_PHASES.find(item => item.id === progress.currentPhase) || PROGRAMME_PHASES[0];
    const intro = el('div', { class: 'card' }); intro.append(el('h2', { text: 'Long-term calisthenics programme' }), el('p', { class: 'v2-muted', text: 'A tendon-first tracker for muscle-up, handstand push-up and planche. Each skill advances independently; expected timelines are guidance, not deadlines.' }));
    const overview = el('div', { class: 'v2-macro-grid' });
    [['Current phase', phase.name.replace(/^Phase \d — /, ''), phase.duration], ['Programme week', String(progress.currentWeek), Number(progress.currentWeek) % 5 === 0 || Number(progress.currentWeek) % 6 === 0 ? 'Consider the planned deload' : 'Deload every 5th–6th week'], ...Object.entries(PROGRAMME_SKILLS).map(([id, skill]) => [skill.label, `Stage ${progress.skillStages[id] || 1}/${skill.stages.length}`, skill.timeline])].forEach(([label, value, note]) => overview.append(el('div', { class: 'v2-macro' }, [el('span', { text: label }), el('strong', { text: value }), el('span', { text: note })])));
    intro.append(overview, el('p', { class: 'v2-summary v2-warning', text: 'Advance only after hitting the clean rep/hold target and having zero joint pain or pinching for two full weeks. Change difficulty or volume in a week—never both.' })); panel.append(intro);

    const status = el('div', { class: 'card' }); status.append(el('h2', { text: 'Current position' })); const form = el('form'); const grid = el('div', { class: 'v2-grid' });
    const phaseSelect = el('select', { name: 'phase', 'aria-label': 'Programme phase' }); PROGRAMME_PHASES.forEach(item => phaseSelect.append(el('option', { value: item.id, text: item.name }))); phaseSelect.value = progress.currentPhase;
    grid.append(el('div', { class: 'v2-field' }, [el('label', { text: 'Overall phase' }), phaseSelect]), input('Programme week', 'number', progress.currentWeek, () => {}, { name: 'week', min: '1', step: '1' }));
    Object.entries(PROGRAMME_SKILLS).forEach(([id, skill]) => { const select = el('select', { name: id, 'aria-label': skill.label + ' stage' }); skill.stages.forEach((stage, index) => select.append(el('option', { value: String(index + 1), text: `Stage ${index + 1}: ${stage[0]}` }))); select.value = String(progress.skillStages[id] || 1); grid.append(el('div', { class: 'v2-field' }, [el('label', { text: skill.label + ' stage' }), select])); });
    const submit = button('Save current position', null, 'primary'); submit.type = 'submit'; form.append(grid, submit); form.addEventListener('submit', async event => { event.preventDefault(); const data = new FormData(form); const before = { phase: progress.currentPhase, week: progress.currentWeek, stages: clone(progress.skillStages) }; progress.currentPhase = data.get('phase'); progress.currentWeek = Math.max(1, Number(data.get('week')) || 1); Object.keys(PROGRAMME_SKILLS).forEach(id => progress.skillStages[id] = Number(data.get(id)) || 1); const changes = Object.keys(PROGRAMME_SKILLS).filter(id => Number(before.stages[id]) !== Number(progress.skillStages[id])).map(id => ({ skill: id, from: Number(before.stages[id]), to: Number(progress.skillStages[id]) })); if (changes.length || before.phase !== progress.currentPhase) progress.stageHistory.push({ id: 'stage-' + Date.now(), date: isoToday(), programmeWeek: progress.currentWeek, phaseFrom: before.phase, phaseTo: progress.currentPhase, changes, recordedAt: new Date().toISOString() }); await saveProgramme(); renderProgramme(); }); status.append(form, el('p', { class: 'v2-diet-note', text: phase.focus })); panel.append(status);

    const prerequisites = el('div', { class: 'card' }); prerequisites.append(el('h2', { text: 'Foundation prerequisites' }), el('p', { class: 'v2-diet-note', text: 'If any strength prerequisite is missing, use 4–6 weeks of general strength and joint conditioning before skill-specific loading.' }));
    PROGRAMME_PREREQUISITES.forEach(([id, label, note, exerciseName]) => {
      const check = el('input', { type: 'checkbox' }); check.checked = !!progress.prerequisites[id];
      check.addEventListener('change', async () => { progress.prerequisites[id] = check.checked; await saveProgramme('Prerequisite updated.'); });
      const copy = el('span', { class: 'grow' }, [el('strong', { text: label }), el('span', { class: 'v2-meta', text: note }), exerciseName ? exerciseGuide(libraryExercise(exerciseName), false) : null]);
      prerequisites.append(el('label', { class: 'v2-check v2-session-check v2-row' }, [check, copy]));
    }); panel.append(prerequisites);

    const weekly = el('div', { class: 'card' }); weekly.append(el('h2', { text: `Week ${progress.currentWeek} sessions` }), el('p', { class: 'v2-diet-note', text: 'Session order: 10 min joint prep → fresh skill work → 15–20 min accessory strength → 5 min mobility/cooldown.' }));
    PROGRAMME_SESSIONS.forEach(([id, day, focus]) => {
      const tasks = programmeSessionItems(id); const done = tasks.filter(task => week.items[`${id}:${task.id}`]).length; const section = el('section', { class: 'v2-programme-session' });
      const progressText = el('span', { class: 'v2-programme-progress', text: `${done}/${tasks.length} complete` });
      const isActive = state.active?.programme?.week === progress.currentWeek && state.active?.programme?.sessionId === id;
      section.append(el('div', { class: 'v2-row' }, [el('div', { class: 'grow' }, [el('h3', { text: `${day} — ${focus}` }), progressText]), el('div', { class: 'v2-actions' }, [button(isActive ? 'Resume workout' : 'Start workout', () => startProgrammeSession(id), 'primary compact'), button(done === tasks.length ? 'Clear session' : 'Mark all done', async () => { tasks.forEach(task => week.items[`${id}:${task.id}`] = done !== tasks.length); week.sessions[id] = done !== tasks.length; await saveProgramme('Session checklist updated.'); renderProgramme(); }, 'compact')]) ]));
      tasks.forEach(task => {
        const key = `${id}:${task.id}`; const check = el('input', { type: 'checkbox', 'aria-label': `Complete ${task.label}` }); check.checked = !!week.items[key];
        check.addEventListener('change', async () => { week.items[key] = check.checked; await saveProgramme('Programme item updated.'); renderProgramme(); });
        const exercise = libraryExercise(task.exerciseName); const copy = el('div', { class: 'grow' }, [el('strong', { text: task.label }), el('div', { class: 'v2-meta', text: `${task.exerciseName} · ${task.target}` }), exerciseGuide(exercise, false)]);
        section.append(el('div', { class: 'v2-row v2-programme-task' }, [el('label', { class: 'v2-check' }, [check]), copy]));
      }); weekly.append(section);
    });
    const deload = el('input', { type: 'checkbox' }); deload.checked = !!week.deload; deload.addEventListener('change', async () => { week.deload = deload.checked; await saveProgramme('Deload status updated.'); }); const joint = el('input', { type: 'number', min: '0', max: '10', step: '1', 'aria-label': 'Highest joint discomfort this week' }); joint.value = week.jointComfort ?? ''; const notes = el('textarea', { rows: '3', placeholder: 'Weekly notes: holds, reps, form, fatigue, pain or adjustments' }); notes.value = week.notes || '';
    weekly.append(el('label', { class: 'v2-check v2-row' }, [deload, document.createTextNode('This is a deload week: about 50% volume, no new progression attempts')]), el('div', { class: 'v2-grid' }, [el('div', { class: 'v2-field' }, [el('label', { text: 'Highest joint discomfort this week (0–10)' }), joint]), el('div', { class: 'v2-field' }, [el('label', { text: 'Week notes' }), notes])]), button('Save week notes', async () => { week.jointComfort = numberOrNull(joint.value); week.notes = notes.value.trim(); await saveProgramme('Week notes saved.'); }, 'primary')); panel.append(weekly);

    const paths = el('div', { class: 'card' }); paths.append(el('h2', { text: 'Skill pathways' }), el('p', { class: 'v2-diet-note', text: 'The highlighted row is your selected stage. Planche advances only when the target is reliable on your worst day, not after one best-day hold.' }));
    Object.entries(PROGRAMME_SKILLS).forEach(([id, skill]) => {
      const details = el('details', { class: 'v2-programme-skill' }); if (id === 'muscleUp') details.open = true;
      details.append(el('summary', { text: `${skill.label} · Stage ${progress.skillStages[id] || 1}/${skill.stages.length}` }), el('p', { class: 'v2-meta', text: `Risk zone: ${skill.risk}. ${skill.addition}` }));
      skill.stages.forEach(([exercise, criterion, exerciseName], index) => {
        const content = [el('strong', { text: `Stage ${index + 1}: ${exercise}` }), el('span', { class: 'v2-meta', text: 'Advance when: ' + criterion }), exerciseGuide(libraryExercise(exerciseName), false)];
        details.append(el('div', { class: 'v2-programme-stage' + (index + 1 === Number(progress.skillStages[id]) ? ' current' : '') }, content));
      }); paths.append(details);
    }); panel.append(paths, programmeTestCard());

    const safety = el('div', { class: 'card' }); safety.append(el('h2', { text: 'Autoregulation and non-negotiables' }), el('p', { text: 'Wrist prep and scapular control work belong in every session. Deload every 5–6 weeks.' }), el('p', { class: 'v2-summary v2-warning', text: 'Back off one full stage for at least 1–2 weeks if joint pain lasts more than 24 hours, a hold drops for two sessions, new grip/wrist weakness appears, or you feel pinching, clicking or a sharp sensation. Do not push through tendon warning signs.' })); panel.append(safety);
  }
  function programmeTestCard() {
    const editing = state.programme.tests.find(item => item.id === state.editProgrammeTest); const card = el('div', { class: 'card' }); card.append(el('h2', { text: editing ? 'Edit four-week test' : 'Four-week test log' }), el('p', { class: 'v2-diet-note', text: 'Test no more than every four weeks: stage performance, both sides where relevant, joint comfort at rest and under load, plus a form video kept in your private photo library.' }));
    const form = el('form'); const date = el('input', { type: 'date', name: 'date', required: 'true' }); date.value = editing?.date || isoToday(); const skill = el('select', { name: 'skill' }); Object.entries(PROGRAMME_SKILLS).forEach(([id, item]) => skill.append(el('option', { value: id, text: item.label }))); skill.value = editing?.skill || 'muscleUp';
    const performance = el('input', { type: 'text', name: 'performance', required: 'true', placeholder: 'e.g. 5×22s; left/right if asymmetric' }); performance.value = editing?.performance || ''; const notes = el('textarea', { name: 'notes', rows: '3', placeholder: 'Form notes, video reference, early overuse signals' }); notes.value = editing?.notes || '';
    const grid = el('div', { class: 'v2-grid' }); grid.append(el('div', { class: 'v2-field' }, [el('label', { text: 'Test date' }), date]), el('div', { class: 'v2-field' }, [el('label', { text: 'Skill' }), skill]), input('Stage', 'number', editing?.stage || 1, () => {}, { name: 'stage', min: '1', max: '10', step: '1' }), el('div', { class: 'v2-field' }, [el('label', { text: 'Max hold / reps / sets' }), performance]), input('Joint discomfort at rest (0–10)', 'number', editing?.restPain ?? 0, () => {}, { name: 'restPain', min: '0', max: '10', step: '1' }), input('Joint discomfort under load (0–10)', 'number', editing?.loadPain ?? 0, () => {}, { name: 'loadPain', min: '0', max: '10', step: '1' }));
    const submit = button(editing ? 'Save test corrections' : 'Record test', null, 'primary'); submit.type = 'submit'; form.append(grid, el('div', { class: 'v2-field' }, [el('label', { text: 'Notes / form video reference' }), notes]), el('div', { class: 'v2-toolbar' }, [submit, editing ? button('Cancel', () => { state.editProgrammeTest = null; renderProgramme(); }) : null]));
    form.addEventListener('submit', async event => { event.preventDefault(); const data = new FormData(form); const next = { id: editing?.id || 'test-' + Date.now(), date: data.get('date'), skill: data.get('skill'), stage: Number(data.get('stage')) || 1, performance: String(data.get('performance')).trim(), restPain: Number(data.get('restPain')) || 0, loadPain: Number(data.get('loadPain')) || 0, notes: String(data.get('notes')).trim(), updatedAt: new Date().toISOString() }; if (editing) state.programme.tests[state.programme.tests.findIndex(item => item.id === editing.id)] = next; else state.programme.tests.push(next); await saveProgramme(editing ? 'Test corrections saved.' : 'Test recorded.'); state.editProgrammeTest = null; renderProgramme(); }); card.append(form);
    state.programme.tests.slice().sort((a, b) => b.date.localeCompare(a.date)).forEach(test => {
      const item = PROGRAMME_SKILLS[test.skill]; const copy = el('div', { class: 'grow' }, [el('strong', { text: `${test.date} — ${item?.label || test.skill}, Stage ${test.stage}` }), el('div', { class: 'v2-meta', text: `${test.performance} · discomfort ${test.restPain}/10 rest, ${test.loadPain}/10 loaded` }), test.notes ? el('div', { class: 'v2-meta', text: test.notes }) : null]);
      const actions = el('div', { class: 'v2-actions' }, [button('Edit', () => { state.editProgrammeTest = test.id; renderProgramme(); }, 'compact'), button('Delete', () => deleteProgrammeTest(test.id), 'compact danger')]);
      card.append(el('div', { class: 'v2-row' }, [copy, actions]));
    }); return card;
  }
  async function deleteProgrammeTest(id) { if (!confirm('Delete this four-week test? You can undo for 10 seconds.')) return; const index = state.programme.tests.findIndex(item => item.id === id); const removed = state.programme.tests[index]; state.programme.tests.splice(index, 1); try { await save('programme'); renderProgramme(); toast('Test deleted.', async () => { state.programme.tests.splice(index, 0, removed); await save('programme'); renderProgramme(); toast('Test restored.'); }); } catch (error) { state.programme.tests.splice(index, 0, removed); toast(error.message); } }

  function renderReview() {
    const panel = clear($('#tab-review')); const settings = el('div', { class: 'card' }); settings.append(el('h2', { text: 'Goals and recovery' })); const form = el('form'); const grid = el('div', { class: 'v2-grid' }); grid.append(input('Goal weight (kg)', 'number', state.settings.goalWeight, () => {}, { name: 'goal', min: '20', max: '400', step: '0.1' }), input('Preferred weekly rate (kg)', 'number', state.settings.weeklyRate, () => {}, { name: 'rate', min: '0', max: '1.5', step: '0.05' })); form.append(grid, button('Save goals', null, 'primary')); form.lastChild.type = 'submit'; form.addEventListener('submit', async event => { event.preventDefault(); const fd = new FormData(form); state.settings.goalWeight = numberOrNull(fd.get('goal')); state.settings.weeklyRate = numberOrNull(fd.get('rate')); try { await save('settings'); toast('Goals saved.'); } catch (error) { toast(error.message); } }); settings.append(form); panel.append(weeklyReviewCard(), settings, equipmentSettingsCard(), monthlyReviewCard(), remindersCard(), dataCard());
  }
  function equipmentSettingsCard() { const equipment = state.settings.equipment; const card = el('div', { class: 'card' }); card.append(el('h2', { text: 'Equipment and loading' }), el('p', { class: 'v2-muted', text: 'Progression suggestions use the smallest normal load change. For the plate calculator, list each matching pair you have; repeat a size when you own more than one pair.' })); const form = el('form'); const increment = el('input', { type: 'number', min: '0.1', max: '100', step: '0.1', required: 'true' }); increment.value = equipment.loadIncrement; const bar = el('input', { type: 'number', min: '0', max: '100', step: '0.1', required: 'true' }); bar.value = equipment.barWeight; const plates = el('input', { type: 'text', required: 'true', placeholder: '25, 25, 20, 20, 15, 10, 5, 2.5, 1.25' }); plates.value = equipment.platePairs.join(', '); const submit = button('Save equipment settings', null, 'primary'); submit.type = 'submit'; form.append(el('div', { class: 'v2-grid' }, [el('div', { class: 'v2-field' }, [el('label', { text: 'Normal load increment (kg)' }), increment]), el('div', { class: 'v2-field' }, [el('label', { text: 'Bar weight (kg)' }), bar]), el('div', { class: 'v2-field' }, [el('label', { text: 'Available plate pairs (kg)' }), plates])]), submit); form.addEventListener('submit', async event => { event.preventDefault(); const parsed = plates.value.split(',').map(value => Number(value.trim())).filter(value => Number.isFinite(value) && value > 0 && value <= 100); if (!parsed.length || parsed.length > 40) return toast('Enter between 1 and 40 positive plate-pair sizes, separated by commas.'); const previous = clone(equipment); equipment.loadIncrement = Math.max(0.1, Number(increment.value) || 2.5); equipment.barWeight = Math.max(0, Number(bar.value) || 0); equipment.platePairs = parsed.sort((a, b) => b - a); try { await save('settings'); renderReview(); toast('Equipment settings saved.'); } catch (error) { state.settings.equipment = previous; toast(error.message); } }); card.append(form); return card; }
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
    card.append(el('h2', { text: 'Backup and recovery' }), el('p', { class: 'v2-muted', text: 'Exports include daily logs, diets, libraries, workouts, routines, calisthenics programme progress, settings, reviews, and reminder preferences.' }));
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
  async function exportBundle() { return { schemaVersion: 10, exportedAt: new Date().toISOString(), data: { health: state.health, diet: state.diet, foods: state.foods, dietSettings: state.dietSettings, mealTemplates: state.mealTemplates, workouts: state.workouts, routines: state.routines, library: state.library, programme: state.programme, settings: state.settings, reviews: state.reviews, reminders: state.reminders } }; }
  function downloadJSON(value, name) { const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' })); const link = el('a', { href: url, download: name }); link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); }

  async function boot() { try { await loadAll(); if (state._migratedDiet) { try { await save('diet'); } catch { /* Existing records remain usable; retry on the next successful save. */ } } if (state._migratedLibrary) { try { await save('library'); } catch { /* Retry on the next successful save. */ } } if (state._migratedRoutines) { try { await save('routines'); } catch { /* Retry on the next successful save. */ } } if (state._migratedSettings) { try { await save('settings'); } catch { /* Retry on the next successful save. */ } } buildShell(); render(); if ('serviceWorker' in navigator) navigator.serviceWorker.register('/static/service-worker.js').catch(() => {}); } catch (error) { document.body.prepend(el('div', { class: 'v2-banner', role: 'alert', text: 'Could not load the tracker. Check the connection and refresh. ' + error.message })); } }
  boot();
})();
