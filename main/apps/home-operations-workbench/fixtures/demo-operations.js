export const demoOperations = Object.freeze({
  schemaVersion: '1.0',
  generatedAt: '2026-09-05 10:30 BST',
  source: { label: 'Demonstration evidence — no live connection' },
  today: {
    gardenTasks: [
      { id: 'garden-herbs', title: 'Check herb bed moisture', due: 'Today', status: 'warning', detail: 'Last recorded check was four days ago.', ownerUrl: 'http://gardenkeeper.home.local:8091/' },
      { id: 'garden-tomatoes', title: 'Tie tomato growth', due: 'Tomorrow', status: 'healthy', ownerUrl: 'http://gardenkeeper.home.local:8091/' },
    ],
    food: [
      { id: 'food-spinach', title: 'Spinach', quantity: '200 g', location: 'Fridge', expires: 'Today', status: 'warning', detail: 'Use soon.', ownerUrl: 'http://grocy.home.local:9283/' },
      { id: 'food-potatoes', title: 'Potatoes', quantity: '1.5 kg', location: 'Pantry', expires: 'No expiry recorded', status: 'healthy', ownerUrl: 'http://grocy.home.local:9283/' },
    ],
    meals: [
      { id: 'meal-traybake', title: 'Vegetable traybake', due: 'Tonight', status: 'healthy', detail: 'Planned meal.', ownerUrl: 'http://mealie.home.local:9925/' },
    ],
    workouts: [
      { id: 'workout-pull', title: 'Calisthenics pull session', due: '18:30', status: 'healthy', detail: 'Scheduled session.', ownerUrl: 'https://homepage.home.local:8209/' },
    ],
    operations: [
      { id: 'ops-vm103', title: 'Review VM 103 root storage', due: 'Today', status: 'warning', detail: 'Recent evidence shows 75% root-disk use.' },
      { id: 'ops-camera', title: 'Camera path', due: 'When CCTV is reconnected', status: 'planned_offline', detail: 'Cameras are intentionally disconnected.' },
    ],
  },
  dependencies: [
    { id: 'proxmox', label: 'Proxmox host', kind: 'host', status: 'healthy', observedAt: '2026-09-05 10:20 BST', detail: 'Host reached by the management collector.' },
    { id: 'vm103', label: 'VM 103 / docker-host', kind: 'host', status: 'warning', observedAt: '2026-09-05 10:20 BST', detail: 'Root storage needs review.', dependsOn: ['proxmox'] },
    { id: 'homepage', label: 'Homepage', kind: 'service', status: 'warning', observedAt: '2026-09-05 10:20 BST', detail: 'Example service warning.', dependsOn: ['vm103'] },
    { id: 'grocy', label: 'Grocy', kind: 'service', status: 'warning', observedAt: '2026-09-05 10:20 BST', detail: 'Example service warning.', dependsOn: ['vm103'] },
    { id: 'omv', label: 'OMV backup storage', kind: 'storage', status: 'healthy', observedAt: '2026-09-05 10:20 BST', detail: 'NFS probe succeeded.' },
    { id: 'backups', label: 'Proxmox backup freshness', kind: 'backup', status: 'warning', observedAt: '2026-09-05 10:20 BST', detail: 'CT 114 restore evidence still needs review.', dependsOn: ['omv'] },
    { id: 'camera', label: 'Camera path', kind: 'device', status: 'planned_offline', observedAt: '2026-09-05 10:20 BST', detail: 'Cameras intentionally disconnected.' },
  ],
  incidents: [
    { id: 'incident-vm103', title: 'VM 103 shared-service warning', observedAt: '2026-09-05 10:20 BST', status: 'warning', signals: ['vm103', 'homepage', 'grocy'], note: 'Example only. Investigate VM 103 before treating application warnings as unrelated.' },
    { id: 'incident-cctv', title: 'CCTV rollout paused', observedAt: '2026-09-05 09:00 BST', status: 'planned_offline', signals: ['camera'], note: 'Cameras are intentionally disconnected during the current network work.' },
  ],
  recovery: {
    systems: [
      { id: 'ha', label: 'Home Assistant', backup: { status: 'healthy', observedAt: '2026-09-05', detail: 'OMV backup mount has accepted prior write proof.' }, integrity: { status: 'healthy', observedAt: '2026-07-05', detail: 'Backup archive integrity was checked.' }, restore: { status: 'unknown', observedAt: 'Not recorded', detail: 'No isolated restore exercise recorded in this fixture.' }, runbook: 'https://homeassistant.home.local:8123/' },
      { id: 'docker-host', label: 'Docker host applications', backup: { status: 'healthy', observedAt: '2026-08-01', detail: 'App-data backup heartbeat accepted.' }, integrity: { status: 'healthy', observedAt: '2026-07-29', detail: 'SQLite backup integrity checks passed.' }, restore: { status: 'healthy', observedAt: '2026-07-29', detail: 'Isolated restore proof recorded for selected applications.' }, runbook: 'https://homepage.home.local/' },
      { id: 'frigate', label: 'Frigate recordings', backup: { status: 'healthy', observedAt: '2026-08-01', detail: 'Recordings mount is monitored.' }, integrity: { status: 'unknown', observedAt: 'Not recorded', detail: 'Archive integrity evidence was not supplied.' }, restore: { status: 'unknown', observedAt: 'Not recorded', detail: 'No isolated restore exercise supplied.' } },
    ],
  },
  cooking: {
    candidates: [
      { id: 'recipe-traybake', title: 'Vegetable traybake', detail: 'Uses spinach that is due today.', sourceUrl: 'http://mealie.home.local:9925/', ingredients: [
        { id: 'spinach', name: 'Spinach', required: '200 g', available: '200 g', availability: 'available', expires: 'Today' },
        { id: 'potatoes', name: 'Potatoes', required: '600 g', available: '1.5 kg', availability: 'available' },
      ] },
      { id: 'recipe-chilli', title: 'Bean chilli', detail: 'A meal option with an inventory gap.', sourceUrl: 'http://mealie.home.local:9925/', ingredients: [
        { id: 'beans', name: 'Black beans', required: '1 tin', availability: 'missing' },
        { id: 'tomatoes', name: 'Tinned tomatoes', required: '1 tin', available: '1 tin', availability: 'available' },
      ] },
    ],
  },
  commissioning: {
    devices: [
      { id: 'fdm-sensor', label: 'FDM sensor board', type: 'ESPHome sensor', stage: 'planned', checks: [
        { title: 'Board identity recorded', status: 'unknown' },
        { title: 'Bench calibration', status: 'unknown' },
        { title: 'MQTT TLS proof', status: 'unknown' },
      ] },
      { id: 'main-fan', label: 'Main fan controller', type: 'ESPHome controller', stage: 'planned', checks: [
        { title: 'Wiring photographed', status: 'unknown' },
        { title: 'Fail-safe behaviour observed', status: 'unknown' },
      ] },
    ],
    scenarios: [
      { id: 'scenario-air-quality', label: 'Elevated air-quality reading', description: 'A visual-only rehearsal of dashboard state. It is not connected to MQTT, Home Assistant or a controller.', steps: [
        { title: 'Sensor reading rises', status: 'warning', detail: 'Example input: VOC trend crosses the configured review threshold.' },
        { title: 'Dashboard shows an alarm state', status: 'warning', detail: 'Visual state only; no command is issued.' },
        { title: 'Operator follows the approved emergency procedure', status: 'unknown', detail: 'Physical response requires the existing HA/ESPHome safety acceptance.' },
      ] },
    ],
  },
});
