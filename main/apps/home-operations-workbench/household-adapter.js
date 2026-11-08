// Explicit saved bundle only: validate each source independently, no live merge.
import { adaptGardenTasks } from './garden-adapter.js';
import { adaptGrocyOverview } from './grocy-adapter.js';
import { adaptMealiePlan } from './mealie-adapter.js';
import { adaptRecompPlan } from './recomp-adapter.js';
const baseAdapters = [
  ['garden-tasks/1.0', adaptGardenTasks],
  ['grocy-overview/1.0', adaptGrocyOverview],
  ['mealie-plan/1.0', adaptMealiePlan],
];
export function adaptHouseholdSources(bundle, options = {}) {
  const adapters = bundle?.schemaVersion === 'household-sources/1.1'
    ? [...baseAdapters, ['recomp-plan/1.0', adaptRecompPlan]] : baseAdapters;
  if (!bundle || typeof bundle !== 'object' || Array.isArray(bundle) || !['household-sources/1.0', 'household-sources/1.1'].includes(bundle.schemaVersion) || !Array.isArray(bundle.sources) || bundle.sources.length !== adapters.length) {
    throw new Error('Saved household bundle requires exactly one of each versioned household source.');
  }
  const sources = new Map();
  for (const source of bundle.sources) {
    if (!source || typeof source !== 'object' || Array.isArray(source) || !adapters.some(([schema]) => schema === source.schemaVersion) || sources.has(source.schemaVersion)) {
      throw new Error('Unsupported or duplicate household source.');
    }
    sources.set(source.schemaVersion, source);
  }
  // Use one import clock, without substituting it for any source observation.
  const now = new Date(options.now ?? Date.now());
  const converted = adapters.map(([schema, adapter]) => adapter(sources.get(schema), { ...options, now }));
  const [garden, grocy, mealie, recomp] = converted;
  const headers = converted.map(source => ({ ...source.today.operations[0] }));
  const shopping = grocy.today.operations.slice(1);
  const selectedShopping = shopping.slice(0, 50 - headers.length);
  if (selectedShopping.length < shopping.length) {
    headers[1].detail = `Bundle shopping display: ${selectedShopping.length} of ${shopping.length} selected rows; no complete inventory or writes. ${headers[1].detail}`;
  }
  return {
    schemaVersion: '1.0', generatedAt: now.toISOString(),
    source: { label: `Household — ${recomp ? 'four' : 'three'} saved sources (offline bundle)` },
    today: { gardenTasks: garden.today.gardenTasks, food: grocy.today.food,
      meals: mealie.today.meals, workouts: recomp?.today.workouts ?? [], operations: [...headers, ...selectedShopping] },
  };
}
