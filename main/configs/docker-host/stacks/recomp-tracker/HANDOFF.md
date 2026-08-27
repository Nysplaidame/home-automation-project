# Handoff: recomp-tracker → deploy to docker-host (VM 103)

## What this is

A personal weight-loss/recomposition tracker (daily habits, workouts, a long
reference Guide, ntfy reminders). It's been running for weeks as a **Claude
artifact** (browser storage, works today, no deployment needed) and is now
being moved to run as a **real, always-on service** on the user's home
docker host, mainly to get the ntfy push notifications actually working
(the artifact can't run a background scheduler when the tab is closed).

## Current deployment state (2026-08-27)

- Live on docker-host VM 103 at `http://192.168.20.102:8420/`; the container
  is healthy and uses the explicit `10.240.31.0/24` bridge, avoiding the
  earlier automatic-range routing collision with management.
- SQLite data persists at `/opt/stacks/recomp-tracker/data/recomp.db`. A
  write, container restart and subsequent readback passed; SQLite integrity is
  `ok`. The docker-host app-data backup job includes a consistent SQLite copy;
  its `--dry-run` passed on 2026-08-13.
- ntfy has `auth-default-access: deny-all`. A dedicated `recomp-tracker`
  account has write-only access to the existing tracker topic. Its generated
  password is only in the mode-0600 live `.env`; it is not in the repository.
- Reminder publishing was tested successfully from the live container. The
  scheduler uses `Europe/London` and reported BST during this check, so the
  schedule follows daylight-saving changes rather than a manually maintained
  UTC offset.
- The app runs under Waitress with one process and four request threads; this
  preserves exactly one scheduler thread while avoiding Flask's development
  server in production.
- `docker-host-firewall.service` now applies the port-8420 DOCKER-USER allow
  rules for management, LAN and Tailscale followed by a deny rule. Homepage's
  Tools tab contains the `Recomp Tracker` card.
- The VM was found to have a stale frontend even though the container was
  healthy: its `Workouts` marker count was `0` while the repository version
  contained the tab. On 2026-08-13 the app source/templates were synced again
  without touching live `.env` or `data/`, then rebuilt with `--no-cache`.
  The running template hash now matches source and its `Workouts` count is `7`.
- On 2026-08-13 the tracker interface was upgraded to v2. It adds server-backed
  daily/workout edits and undo, version-checked writes with retained revisions,
  JSON backup/restore with a pre-import snapshot, and configurable reminders.
  It also adds a complete exercise library, reusable manual routines and a
  persistent live-workout tab with set ticks, stopwatch, rest timers and form
  cues. A real-browser check passed for all tabs, 17 built-in exercises, and
  the workout controls; its temporary routine/draft was removed without adding
  a workout or health entry.
- Follow-up UI repair (2026-08-13): the original Trends, Habits and Guide
  panels are preserved by the v2 shell rather than replaced. Routine, workout,
  review and backup controls now use the app's rounded input/button system and
  responsive spacing. The kitchen-close habit and reminder were removed; past
  entry fields were deliberately retained. `GET /api/reminders` is the UI's
  catalogue source, so every scheduler prompt is configurable and each workout
  reminder shows its real weekday schedule.
- Diet-tab addition (2026-08-13): `daily-diet-log`, `food-library`, and
  `diet-settings` are new versioned KV records. The Diet tab starts with the
  plan's regular food/supplement constants, provides reusable foods with
  per-100g macros, four meal sections, ticked-item totals and a saved-day
  history. Default nutrition values are convenient estimates; the user should
  update/add foods from product labels or recipes. Backups at schema v3 include
  all three diet records.
- Diet usability repair (2026-08-13): individual meal-food rows can now be
  removed before saving; daily constants have Edit and Archive controls; macro
  text wraps within the diet cards at phone widths; and the full exercise
  library has Edit and Archive controls. The Workout tab labels RPE as the
  1–10 effort scale and explains the practical 7–10 range.
- Flexibility foundation (2026-08-13): diet entries now snapshot their foods
  and checked constants when saved, so library edits cannot rewrite historical
  totals. Food, constant, exercise and saved-meal libraries support
  archive-based management; diet sections are user-managed; and saved meals
  can be loaded into any section. Routines now carry per-exercise planned set
  count, rest, target RPE and set type into the live workout. The Today and
  Review tabs add a concise current-day overview and data-quality-aware 7-day
  summary. Backups are schema v4 and include saved meals.
- Food-library population: as of 2026-08-24 the live library has 2,691 active
  foods (the existing 299 retained plus 2,392 usable current CoFID 2021
  records). This adds broad vegetables/legumes, fruit, sauces/soups/condiments,
  cereals, 196 fish/seafood, 539 meat/poultry, 153 further dairy/cheese records,
  nuts/seeds, herbs/spices, eggs, fats and drinks. Every imported item retains
  its exact CoFID food name/code and macro values. Unavailable core-macro rows
  and descriptions weighed with bone/shell are excluded; alcoholic drinks use
  CoFID's per-100ml basis and all other imports use per 100g. The library is
  paginated 80 at a time. `tools/import_cofid_foods.py --full` is the
  dry-run-first, conflict-aware importer and never overwrites a user-created
  food or matching source code.
- Navigation refinement (2026-08-14): Diet now focuses on logging a day;
  food creation/editing/archive work is in its own `Food library` tab. The
  library has live text search and category filtering for its active foods.
  The former Trends tab is now `Records` and holds saved meal days plus completed
  workouts. The former Habits tab is `Habits & Trends`, combining the streaks
  with the weight, waist and sleep trend charts.
- Navigation and library refinement (2026-08-24): the nine destinations are
  ordered by everyday use and rendered as a contained five-column grid on
  wider screens and a three-column grid on phones, eliminating horizontal tab
  overflow. Tabs support Left/Right/Home/End keyboard navigation. Active foods
  can be sorted ascending or descending by name, calories, protein,
  carbohydrate or fat, alongside the existing search and category filters.
- Diet, Records and programme expansion (2026-08-24): Diet now keeps its daily
  consumed/remaining macro balance visible while scrolling, supports favourite
  foods and recent-food quick add, and has editable Standard, Training and Rest
  target profiles with a weekday schedule. Records has 7/30/90-day and custom
  date filtering, meal/workout and routine filtering, and aggregate adherence
  summaries. The new `calisthenics-programme` record backs a dedicated Programme
  tab based on the supplied tendon-first muscle-up/HSPU/planche plan: independent
  stages, phase/week position, prerequisites, weekly session/deload checks,
  joint-comfort notes, complete progression criteria, and editable four-week
  test logs. Backups are schema v5 and include programme progress. The live
  container was rebuilt, source hash matched, the new key persisted across a
  browser reload, and desktop browser checks passed for all new screens.
- Exercise and programme expansion (2026-08-24): the live exercise library now
  has 135 unique active entries. All use `Exercise - Variation`, including the
  37 legacy entries renamed in place; 98 exercises were added with a strong
  calisthenics focus. Every entry has an editable cue, at least three form steps
  and a code-native position schematic. Guidance appears in library cards,
  live workouts, programme prerequisites and every progression stage.
  `tools/expand_exercise_library.py` updated all 16 routine references while
  deliberately leaving completed workout history untouched. Programme weeks
  now expand into 35 individually tickable preparation, skill, accessory and
  stretch tasks across four sessions, each with linked instructions. A
  pre-migration server snapshot was saved locally; both importers used
  version-checked writes, and server revisions retain the replaced values.
  Post-deploy validation found no duplicate food names/codes, invalid macros,
  duplicate/malformed exercise names, missing/short guidance or broken routine
  references. Desktop and 375px browser checks passed with no console errors or
  horizontal overflow, and a container restart retained 2,691 foods and 135
  exercises before Docker returned healthy.
- Connected workflow and analytics release (2026-08-25): each of the four
  programme days now has `Start workout`/`Resume workout`. Loading a day creates
  a persistent live workout containing its current 8–10 preparation, skill,
  accessory and cooldown tasks with parsed set/hold targets and rest periods.
  Completing all sets for an item synchronises its weekly programme checkbox;
  finishing records the session-complete state. Programme exercises also retain
  assistance/variation, tempo and form-quality metadata. Changing a skill stage
  records a dated stage-history entry instead of losing the prior position.
  Records now includes an eight-week reps-or-seconds/set/load chart, searchable
  exercise-variation personal records, checklist adherence, stage history,
  joint-discomfort context and conservative deload/repeated-form-quality flags.
- Flexible food workflow release (2026-08-25): foods support collision-checked
  search aliases and editable serving presets. Selecting a preset fills the
  diary amount, aliases resolve back to the canonical food, and each meal shows
  its own recent foods. A recipe builder calculates a reusable food from saved
  ingredient snapshots and final cooked yield; calculated recipes receive a
  whole-recipe serving and remain editable. Library rows now identify official
  CoFID, calculated recipe, supplied-source and personal-entry quality, while a
  searchable archived-food manager restores entries. The single food-library
  value is about 840 KB, so the bounded request ceiling was raised from 1 MB to
  8 MB (`MAX_CONTENT_LENGTH`) to provide safe growth headroom; a live-container
  contract test accepted 1.2 MB and rejected 9 MB with HTTP 413.
- Workout-flexibility release (2026-08-25): the routine builder now keeps an
  explicit exercise order with drag-and-drop plus keyboard-accessible up/down
  buttons, duplicates routines, marks optional work, and saves reusable warm-up
  or cooldown templates. Adjacent exercises can share a named superset/circuit,
  round count and between-round rest. The live runner renders those groups,
  permits optional items to be skipped without harming completion, and supports
  one-tap regression/progression or full-library substitution while retaining
  the slot's sets, targets, rest and programme task link. The exercise editor
  exposes easier/harder links; twelve common calisthenics pathways receive
  sensible defaults and same-family variations remain available automatically.
  Legacy `warmup` set types migrate to the runner's canonical `warm-up` value.
  Backup schema version is 7.
- Live-workout usability release (2026-08-25): the runner now has a sticky
  session control card, pause/resume, a persistent compact/full-detail setting,
  durable automatic and manual rest timers, and visible queued-autosave state.
  Compact mode lazy-loads each form/substitution guide only when opened rather
  than constructing every 135-option substitution menu up front. Superset and
  circuit groups expose shared round progress and a one-tap `Complete round`
  action; automatic rest starts after the whole round, not the first exercise.
  Each exercise supports copying the previous set, prefilling the last logged
  performance, add/remove/reorder/substitute actions during a live session, and
  session-only assistance, tempo, form-quality, discomfort, failed-set and cue
  notes. Destructive workout edits have a persistent undo action. Set and note
  fields update the in-memory draft on input and use a short serialized save
  debounce, preventing rapid type-then-copy actions from reading stale values.
  Backup schema version is 8 and the offline shell cache is v10.
- Live acceptance for this release covered stopwatch pause/resume, compact
  rendering, typed set copying, quick-note autosave, automatic rest, exercise
  add/reorder/remove/undo and two shared superset rounds. Browser logs stayed
  empty. Testing exposed and fixed both the blur-only draft update and hidden
  compact-guide DOM inflation before release. The five affected live records
  were then restored byte-for-byte from the pre-test snapshot; final state is
  three routines, nine completed workouts, no active draft and 135 exercises.
  Local source, VM source and running-container frontend hashes match, and the
  container returned healthy.
- The workout-flexibility live acceptance created a reversible four-exercise
  routine with a 4-round/75-second superset, optional work, warm-up/cooldown
  templates and a duplicate. Ordering, shared-group propagation, grouped live
  rendering, one-tap pull-up progression, preserved four-set programming and
  optional skip/restore all passed. Browser testing also caught and fixed an
  empty progression-neighbour fault and stray `null` text before release.
  Desktop and 375px layouts had no browser warnings/errors. Exact post-migration
  baselines were restored with version-checked writes: three original routines,
  zero templates/test routines, no active draft, 135 exercises and nine workouts.
- The 2026-08-25 live acceptance used reversible test state. Alias lookup,
  serving selection, calculated recipe persistence, programme-to-workout
  loading, set-to-checklist synchronisation, Records analytics and desktop/
  375px layouts passed. Exact baseline values were restored through
  version-checked writes; the final state has 2,691 foods, no `Codex test*`
  foods, no active workout draft and the original nine completed workouts.
  Browser logs were empty.
- Progression, recovery and planning release (2026-08-27): routines now have
  weekday schedules, one-off date moves and retained version snapshots. Today
  shows due/missed/moved/active/completed states in a seven-day calendar and can
  launch the scheduled routine with its source date and version preserved.
  Exact exercise variations show recent-performance charts plus conservative
  load/rep/variation suggestions derived from history, RPE, form, failures and
  discomfort. The live runner adds a plate calculator backed by configurable
  bar weight, plate pairs and normal load increment. Finishing creates a
  Records summary for completion, work, numeric volume, duration, logged RPE,
  PR signals, discomfort and previous-session comparison. Backup schema is 9;
  the offline shell cache is v12.
- Acceptance for this release covered routine version creation, weekday
  scheduling, immediate Today/calendar refresh without reloading, scheduled
  workout metadata, per-exercise suggestions/history, a 100 kg plate setup,
  equipment controls, Records summaries and desktop/375 px layouts. Testing
  found and fixed stale Today content after saving a routine and blank RPE
  values being averaged as zero. A temporary schedule routine was removed;
  final browser logs are empty and every major tab has zero horizontal overflow
  at phone width. A workout completed while the long-running acceptance draft
  existed was preserved; only the known test set/flags, acceptance name/date
  metadata and invalid overnight timer were removed with version-checked writes.
- Dashboard, reconciled history, goals and intervals release (2026-08-27): a
  dedicated Dashboard now reports the current week's diet, protein, training,
  sleep, weight and habit signals from recorded data. Records and the workout
  progression views reconcile all known legacy exercise names to the current
  `Exercise - Variation` identity at read time; immutable completed workout
  blobs were deliberately left unchanged. Duration descriptions such as
  `40 sec` are no longer interpreted as kilogram loads. Exercise goals support
  reps, seconds or external kilograms with progress, milestone, edit and
  archive/restore controls. The Workout tab now starts with a configurable HIIT
  timer with work/rest/round/preparation values, presets, pause/resume/reset,
  generated transition alarms and a best-effort screen wake lock. Backup schema
  is 10 and the offline shell cache is v15.
- Live acceptance exercised an existing renamed pull-up history through a
  temporary 10-rep then 8-rep goal, including edit, archive and restore. The
  HIIT timer passed Work → Rest → Work → Complete using short test intervals;
  pause held the displayed time, resume continued it, reset returned Ready and
  Test sound produced no browser warning/error. Acceptance found and fixed the
  completed timer retaining its running action and ensured the AudioContext is
  unlocked directly from the start gesture. The exact test goal was removed
  with a version-checked write and HIIT defaults were restored to 40 seconds
  work, 20 seconds rest, 10 rounds and 10 seconds preparation.
- Remaining acceptance: add a read-only subscriber for the tracker topic in
  the ntfy phone app and confirm receipt of the test/scheduled notification.
  Keep that subscriber separate from `mobile-monitoring`, which remains scoped
  to monitoring and watchtower topics.

**The app itself is done and tested.** This handoff records the deployed
features and normal operating constraints.

## What's in this folder

```
app.py                     Flask backend — generic KV store + ntfy scheduler
templates/index.html       Legacy artifact/Guide markup plus v2 shell
static/app-v2.js           Server-backed tracker interface
static/exercise-catalog.json Canonical guided exercise catalogue
static/service-worker.js   Lightweight offline app shell cache
static/manifest.webmanifest PWA metadata
Dockerfile                 Builds the image
requirements.txt           Flask, requests
docker-compose.yml         Canonical standalone Compose stack
docker-compose.snippet.yml Deprecated marker for the old merge workflow
README.md                  Current deployment notes
```

## Architecture — read this before touching anything

The backend remains a generic JSON key-value store, but it is no longer just a
browser-artifact compatibility layer. `static/app-v2.js` is the active
self-hosted interface; it uses the version returned by `GET /api/kv/<key>` in
each write. A stale write receives HTTP 409 rather than silently overwriting a
newer edit from another device. Each replaced value is retained in
`kv_revisions` for recovery.

`templates/index.html` still contains the legacy `Storage` compatibility shim
and Guide content:

```js
const Storage = {
  async get(key) {
    if (window.storage) return window.storage.get(key);      // Claude artifact mode
    const res = await fetch('/api/kv/' + encodeURIComponent(key));
    ...
  },
  async set(key, value) { ... same pattern ... }
};
```

The v2 data keys are `health-log`, `workout-log`, `workout-routines`,
`exercise-library`, `tracker-settings`, `monthly-reviews`, `reminder-settings`,
`active-workout`, `daily-diet-log`, `food-library`, `diet-settings`,
`meal-templates`, and `calisthenics-programme`. Keep the model in those JSON blobs;
do not replace it with an `entries` relational schema. If the old artifact is
updated, merge its Guide/content changes deliberately rather than overwriting
the v2 script reference or tracker shell.

## Already verified locally (in the sandbox this was built in)

- `app.py` syntax-checked and imports cleanly
- KV get/put round-trips correctly through SQLite
- Live HTTP smoke test passed: `/healthz` → 200, versioned KV writes reject a
  stale version with HTTP 409, revision restore works, `GET /` → 200 and
  serves the real page
- The reminder scheduler's habit-check logic (`get_today_habit_entry`)
  correctly parses a real `health-log` blob and reads today's fields

**Deployment verification completed**: Docker health, LAN reachability,
SQLite persistence across a restart, authenticated self-hosted ntfy publishing,
the source-scoped firewall policy, and the Homepage configuration have all
passed. Phone-side subscription/receipt remains the sole open acceptance item.

## Historical deployment steps

1. Copy this whole folder to `/opt/stacks/recomp-tracker` on docker-host
   (`192.168.20.102`), matching the path convention every other stack on
   that host uses (see `/opt/stacks/*` for reference — this host already
   runs several other services this way).

2. `cp .env.example .env` if present, or create one — check
   `docker-compose.snippet.yml` for the required variables:
   - `RECOMP_NTFY_TOPIC` — a random, unguessable slug. The host already
     runs a self-hosted ntfy instance on a docker network called
     `local-alerting`; join that network and point `NTFY_URL` at
     `http://ntfy` (internal DNS name), not the public ntfy.sh.
   - `RECOMP_TZ_OFFSET_HOURS` — local UTC offset, so the reminder times
     (07:15, 12:45, 18:30, etc. — see `REMINDERS` list in `app.py`) fire
     at the right actual clock time.

3. Merge `docker-compose.snippet.yml` into the host's real compose file
   (or use it standalone) — it already has the provenance-disabled build
   flag set (see the known issue below for why that matters), the
   `local-alerting` network join, and a healthcheck hitting `/healthz`.

4. `docker compose up -d --build`

5. Verify: `curl http://192.168.20.102:8420/healthz` should return
   `{"status":"ok"}`. Then open it in a browser and confirm the app loads
   and a Today-tab entry actually saves and reloads (i.e., the KV API is
   really being hit, not silently failing).

6. Apply the firewall scoping — this host firewalls every service by port.
   A draft `DOCKER-USER` iptables block for port 8420 (LAN + Tailscale only,
   no auth on this app) should already exist in the host's
   `system/docker-host-firewall.sh` template from an earlier session — if
   it's not there, add one matching the pattern used for other low-stakes
   internal tools on this host, then reload the firewall service.

## Known landmines from prior attempts — read before you hit these yourself

- **`docker compose build` can hang indefinitely at "resolving provenance
  for metadata file."** This is a known BuildKit issue, more likely on
  hosts with restricted outbound access (this one is firewalled by
  design). Fix already applied in `docker-compose.snippet.yml`
  (`provenance: false` under the build key) — if you're building some
  other way (bare `docker build`), add `--provenance=false` to the command.

- **SSH sessions to this host have, in a prior session, caused a
  connected tool's process bridge to hang** on subsequent commands after
  an SSH call, requiring a full reconnect to recover. If you're running
  through an MCP-style tool bridge rather than a native terminal and
  commands start silently returning nothing after an SSH call, that's
  likely what's happening — restart your connection rather than assume
  the remote host is unresponsive (it probably isn't).

- **Ping to this host may fail even when it's fully reachable.** ICMP can
  behave inconsistently on this network; trust `Test-NetConnection`/TCP
  port checks over `ping` if diagnosing connectivity.

- **The compose network name is `local-alerting`**, already created by
  the ntfy stack — don't create a second one with a different name or the
  app won't be able to reach ntfy internally.

## What "done" looks like

- Container running, `/healthz` green
- A real Today-tab entry saved from a browser survives a container
  restart (proves the volume mount + KV persistence actually works, not
  just that the page loads)
- At least one ntfy notification received on the phone at its scheduled
  time (confirms the scheduler thread, the KV read path, and the ntfy
  network join are all correctly wired together, not just each piece in
  isolation)
- Firewall rule applied so it's reachable on LAN/Tailscale per this
  host's normal security posture

## What NOT to do

- Don't overwrite `templates/index.html` from the old artifact without first
  preserving the v2 script reference and testing the self-hosted interface
- Don't reintroduce a relational `entries` table — the KV model is
  intentional, not a shortcut
- Don't add authentication unless asked — this matches the exposure tier
  of similar low-stakes single-user tools already on this host (LAN +
  Tailscale only, no login), that was a deliberate prior decision, not
  an oversight
