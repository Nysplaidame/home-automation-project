# Handoff: recomp-tracker → deploy to docker-host (VM 103)

## OCR speed and calorie fix — deployed 2026-10-10

Current build is r14 (2026.10.10-r14), service-worker v33, superseding r13 below.
Calorie extraction handles standalone/split kcal lines, Calories on a separate
line, OCR kcaI/kca1 and explicit kJ/kcal pairs. Labelled kJ-only energy is
converted with a review warning; ambiguous/malformed values remain blank.
The active fast English model is 1,984,273 bytes versus 10,923,060 previously
(about 82% less language download). Opening the scanner prepares the reader;
repeat scans reuse it. Cancellation, backgrounding, detachment and idle release
free the worker. Versioned language storage and cache-first OCR assets reduce
repeat downloads. The root /service-worker.js route fixes the old /static/
scope, which excluded the app; legacy registration is removed. API responses
are not cached. No dependency change or database migration.

Checks passed: nine parser tests, existing frontend regressions, JS syntax,
full fixture browser suite (real split-line OCR, review gates, worker reuse,
offline asset cache, persistence and 1440/390/320px layouts), and eight isolated
backend tests. Repeat fixture recognition took about 0.15–0.17 seconds on the
workstation; phone timing remains unverified. Live direct HTTP and Homepage
HTTPS checks passed at 390px, including calories=200 from split energy text,
persisted sections, HTTPS root service-worker control and legacy removal.
API writes were blocked and none attempted. Live checksums match source,
container health passed and SQLite integrity is ok. The user's actual label
has not been reproduced.

Live image: recomp-tracker:release-r14-20261010, manifest
sha256:7920798d037efe1b95893bba60b7ebc5022b211cae59eb40bb9b137df1ab8dd9.
Backup/source/checkpoint/old image identity:
/opt/backups/recomp-tracker-ocr-speed-20261010-143951/.
Previous image also retained as recomp-tracker:pre-ocr-speed-20261010.
Built with Dockerfile.runtime from retained r13 runtime, network none.
Only app.py and static source updated; Compose, environment and records retained.
Rollback: restore source.tar, tag old-image.txt's image as
recomp-tracker-recomp-tracker:latest and recreate with
docker compose up -d --no-build --no-deps recomp-tracker. Do not restore the DB.
Next check: retry the user's label on their phone after refreshing.

## Nutrition photo OCR and persistent sections — deployed 2026-10-10 (r13, historical)

Food add/edit supports on-device English OCR with camera/gallery inputs,
rotation and percentage crop, editable recognised text/values, explicit column
selection, review confirmation and per-serving conversion to 100g/ml. Four
reviewed values are required before applying; no scan writes automatically.
Unknown/kJ-only/less-than/duplicate readings stay blank. Scanning controls sit
outside the food form, so an invalid scan draft cannot block manual food saving.
Nutrition form inputs accept decimal precision. Diet and Food library cards
have native keyboard-accessible collapse controls with per-browser saved choices.
Daily-use sections start open; target planning, meal management, constant editor
and saved meals start closed. Food recipe/archive sections start closed. Edits
reveal the editor without overwriting a closed preference; quick-add/load reveals
the destination meal. Collapse does not discard unsaved values. Storage failure
falls back to session state. Build `2026.10.10-r13`, service-worker cache v32.

Bundled Tesseract.js 6.0.1/core 6.1.2 and English language data add approximately
40 MB under `static/ocr`; provenance/licenses/hashes accompany assets. No image
upload endpoint, Python dependency or database migration. Existing unrelated
working-tree changes were preserved. Backend and dependency hashes match the
prior live source; production diet/workout/food records were not modified.

Verification (local fixtures, isolated image and read-only live acceptance):

- `node --check static/nutrition-ocr.js`, `static/app-v2.js` and
  `static/service-worker.js`.
- `node --test tools/test_nutrition_ocr.cjs`: six parser tests covering columns,
  decimals, absent/ambiguous values, kcal/kJ, units, negative values and basis.
- `node tools/test_frontend.cjs`: existing regression suite.
- `node tools/test_nutrition_ocr_browser.cjs`: actual bundled OCR on a synthetic
  label, editable correction, review gate, save payload, serving conversion,
  column selection, engine failure, cancellation, invalid image and
  1440/390/320px layouts. Desktop/mobile screenshots inspected from the system
  temporary `recomp-ocr-browser` directory. Test uses the existing
  `main/tools/playwright-smoke/node_modules/playwright` installation (or
  `RECOMP_PLAYWRIGHT` override).
- Expanded browser checks prove collapse defaults, keyboard toggling,
  date/tab rerender and reload persistence, unsaved-value retention, blocked
  storage fallback and automatic editor reveal. The initial runtime smoke
  health wait was too short; the rerun with a 30-second startup budget passed.
- The candidate image passed health/scripts plus food save/readback with a
  new isolated database, network `none` and notifications disabled. Its test
  container and anonymous volume were removed.
- Live direct HTTP and Homepage HTTPS browser checks passed at390px: r13,
  persisted collapse state and actual OCR of a synthetic label. All API writes
  were blocked during acceptance and none were attempted. HTTPS acceptance used
  a browser test context allowing the lab certificate; it does not verify a
  new phone's CA trust. No phone capture, real packaging or notification test.

The healthy live image is `recomp-tracker:release-r13-20261010`, manifest
`sha256:e140a43c74d35915a68b3a44e34fda5b4ea3d833758b970f866fc34c50ea8e4c`.
Consistent SQLite checkpoint (`integrity_check=ok`), old image identity and
source archive are retained at
`/opt/backups/recomp-tracker-ocr-collapse-20261010-125657/` on VM103. The old
image is also tagged `recomp-tracker:pre-ocr-collapse-20261010`. Live post-release
SQLite integrity is `ok`; all frontend and bundled OCR asset hashes match source.

Rebuild used the recorded candidate directory and the existing runtime:

```sh
docker build --network none --pull=false --provenance=false --build-arg RUNTIME_IMAGE=recomp-tracker:pre-ocr-collapse-20261010 -f Dockerfile.runtime -t recomp-tracker:release-r13-20261010 .
docker tag recomp-tracker:release-r13-20261010 recomp-tracker-recomp-tracker:latest
docker compose up -d --no-build --no-deps recomp-tracker
```

Only `static/` and `templates/` were copied into the live stack. `.env`, Compose,
backend and data paths were retained. For rollback, restore `source.tar` into
the stack, tag the image identified by `old-image.txt` as
`recomp-tracker-recomp-tracker:latest`, and recreate only this service with the
above no-build/no-deps command. Do not restore the database for this UI rollback.

OCR misread a synthetic decimal before correction. Real packaging accuracy,
phone camera capture and on-phone latency remain unverified. Next: representative
label/phone acceptance. This release supersedes the prior r12/v30 live state.

## What this is

A personal weight-loss/recomposition tracker (daily habits, workouts, a long
reference Guide, ntfy reminders). It's been running for weeks as a **Claude
artifact** (browser storage, works today, no deployment needed) and is now
being moved to run as a **real, always-on service** on the user's home
docker host, mainly to get the ntfy push notifications actually working
(the artifact can't run a background scheduler when the tab is closed).

## Current deployment state (2026-08-28)

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
- Smarter targets, body-composition and interval-recording release
  (2026-08-28): fresh routine/programme workouts now seed explicit planned
  reps/seconds and numeric load from the most recent completed performance,
  while actual fields remain empty until logged. Suggestions can be applied as
  targets, target completion appears in workout summaries, and three or more
  comparable non-improving sessions over at least seven days produce a
  conservative stall/deload prompt. Searchable, keyboard-operable exercise
  pickers now cover goals, workout additions, substitutions and HIIT activity.
  Dashboard and Habits & Trends add seven-day average weight, regression-based
  weight/waist rates, baseline change, guarded energy-equivalent context and
  recorded strength-to-bodyweight trends without treating missing data as zero.
  A completed HIIT timer can optionally create one Records workout with one
  completed seconds-based set per work interval. Backup schema is 11 and the
  offline shell cache is v20.
- Live acceptance for this release verified that a fresh bodyweight routine
  planned Pull-up at 3 × 6 from the prior completed 3 × 5 while its actual
  fields stayed blank; exact-name picker ranking and ArrowDown/Enter selection;
  body trend and relative-strength cards; and an end-to-end 1-second HIIT save
  showing 1/1 completed and 1/1 targets met in Records. Desktop and 375 × 812
  checks found no horizontal overflow and browser warnings/errors remained
  empty. The exact HIIT acceptance record and two blank workout drafts were
  removed with version-checked writes, leaving the user's 10 completed workouts
  and no active draft. HIIT defaults remain 40/20 × 10 with 10 seconds prep.
  A stopped-container backup was saved as
  `/opt/stacks/recomp-tracker/data/recomp.pre-next-batch-20260828.db` before the
  release.
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

2. Copy `.env.example` to `.env` and set its required variables. The canonical
   standalone `docker-compose.yml` consumes:
   - `RECOMP_NTFY_TOPIC` — a random, unguessable slug. The host already
     runs a self-hosted ntfy instance on a docker network called
     `local-alerting`; join that network and point `NTFY_URL` at
     `http://ntfy` (internal DNS name), not the public ntfy.sh.
   - `RECOMP_NTFY_USER` and `RECOMP_NTFY_PASSWORD` — the dedicated
     least-privilege ntfy publisher credentials.
   - `RECOMP_TIMEZONE` — defaults to `Europe/London`, preserving DST-aware
     reminder scheduling without a fixed UTC-offset variable.

3. Use the standalone `docker-compose.yml` without merging fragments. It
   contains the provenance-disabled build setting, explicit
   `10.240.31.0/24` service network, external `local-alerting` join,
   least-privilege container settings, persistent data mount and `/healthz`
   healthcheck.

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
  design). The fix is present in canonical `docker-compose.yml`
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

## Null workout-session recovery — 2026-09-16

- A run of workout deletions left one JSON `null` element in
  `workout-log.sessions`. The v2 startup migration previously assumed every
  array element was a session and failed on `session.id`, so the tracker showed
  “Could not load the tracker … Cannot read properties of null (reading 'id')”.
- `static/app-v2.js` now filters non-object workout entries during migration
  and persists that repair through the existing optimistic-versioned workout
  write. It retains every valid session; it does not alter the remaining
  session records.
- A consistent pre-repair SQLite backup and the prior app script are retained
  at `/opt/backups/recomp-tracker-null-session-20260916/`; the previous image
  is tagged `recomp-tracker:pre-null-session-20260916`.
- Live browser startup completed, `workout-log` now contains 15 sessions and
  zero null entries, `/healthz` is green, and `PRAGMA integrity_check` returned
  `ok`. The live and stack-source script hashes match.
- `docker compose build` could not complete because Docker's default `docker0`
  bridge is missing (`adding interface … to bridge docker0 failed: Device does
  not exist`). The running container was left up; the validated frontend was
  copied into it as a scoped hotfix. Once the host Docker bridge is repaired,
  rebuild/recreate this stack so the image again contains the tracked source.

## Reliability, UI and alarm release — deployed 2026-09-17

Supersedes the hotfix-only deployment above. Live build `2026.09.16-r2` is in a
recreated healthy container, image `recomp-tracker:release-r2-20260917`, manifest
`sha256:c861c3265b5bb560c9278580d2242c86536298a5b58b8b3b583d35cc9a35adfb`.
The compose image `recomp-tracker-recomp-tracker:latest` points to this release.

- Repeated/missing-ID deletes cannot remove another workout or insert null.
  Bulk delete and persistent Recently deleted recovery are available.
- Backend validates saved section shapes and handles atomic version-checked
  batches. Completion saves the workout and clears its draft atomically; backup
  import validates first and snapshots the previous state in the same transaction.
- Schema 12 includes active draft and trash. Conflicts retain unsaved work.
- Fixed local dates, baseline/trend windows, missing Today glance and legacy
  hidden summary; primary navigation is Today/Diet/Workout/Records with More.
  Records supports history beyond 60 entries; save/connection/build state and
  unsaved-edit warnings are visible.
- HIIT has sustained school-bell/dive-siren alarms, volume, preview and stop.
  Idle HIIT controls collapse below the workout controls. Device volume still
  governs physical loudness; background mobile audio is not guaranteed.

Fresh consistent pre-release DB and previous source are retained at
`/opt/backups/recomp-tracker-r2-20260917/`; an additional SQLite checkpoint is
`/opt/stacks/recomp-tracker/data/recomp-pre-r2-20260917.db`. Older recovery backup
and `recomp-tracker:pre-null-session-20260916` image remain available.

Verification: six backend regression tests, frontend race/failure/date/alarm
tests, validation of all populated production sections, isolated browser
completion and 65→66-session pagination, all-tab mobile checks, and live HTTPS
Homepage UI/console/mobile checks passed. Post-deploy integrity is `ok`; all 15
workout sessions exactly match the pre-release checkpoint. Live app/script/worker
hashes match canonical source. No live test workouts or notifications were created.

The missing Docker default bridge remains a host follow-up. `Dockerfile.runtime`
uses an explicitly selected installed runtime without RUN/network steps; the
requirements SHA256 matched `24157eae2f9b22055d015ba60f28bd844fd281f3a6207456d4400f77e7966a9b`.
For source-only rebuilds, from the stack directory:

```sh
docker build --network none --pull=false --provenance=false --build-arg RUNTIME_IMAGE=recomp-tracker:pre-null-session-20260916 -f Dockerfile.runtime -t recomp-tracker:release-r2-20260917 .
docker tag recomp-tracker:release-r2-20260917 recomp-tracker-recomp-tracker:latest
docker compose up -d --no-build --no-deps recomp-tracker
```

Use the normal Dockerfile when requirements change. The build argument has no
default intentionally; Docker's InvalidDefaultArgInFrom warning is expected.
For rollback, retain a fresh DB checkpoint first, select the prior image, recreate
only this service and restore the backed-up hotfix frontend/source consistently
(the prior image predates that frontend hotfix). Do not restore the old database
unless explicitly recovering data: it would discard subsequent user entries.

## HIIT sets and recovery — deployed 2026-09-17

Build `2026.09.17-r3` changes HIIT from a flat round loop to sets of rounds.
It provides `Rounds per set`, `Sets`, and distinct `Recovery between sets`;
the default is five sets and 120 seconds recovery. Timer state reports both set
and round, alarms fire at the recovery phase, and saved HIIT history labels each
work interval by its set while preserving both rest durations in the session.
Existing HIIT settings migrate safely to the new five-set defaults.

The final container image is `recomp-tracker:release-r5-20260917` (manifest
`sha256:1f8d0ca6bec822ae35b6374210f8b444e20335d8bde19a9e6b17b43c23b5ec0a`).
It advances the service-worker cache to v23 so a browser cannot retain an
older frontend after this release. The live default is School alarm bell at 100%
volume, with the existing 5-second work/rest, five rounds per set, five sets,
120-second set recovery and two-second preparation retained.

Visual QA on this release corrected the legacy-looking secondary navigation:
the More tabs now use the rounded card/forest-selected treatment of primary
navigation. Long record summaries use safe wrapping. Browser checks found no
console errors, horizontal overflow or off-viewport inputs, buttons, cards,
timer panels, metric cards or rows across all 11 screens at 1280×720 and
390×844.

## Quantity-aware daily constants — deployed 2026-09-17

Live build `2026.09.17-r6` adds schema 13 support for quantity-aware daily
constants. A new or edited constant can select any saved food, including a
calculated recipe, and choose its normal daily quantity in g/ml. Its nutrition
is then calculated from that item's per-100g/per-100ml values. The daily
checklist also allows an actual quantity for that date, independently of the
default.

- The selected source and its nutrition are snapshotted when the constant is
  recorded, so editing a food or recipe later cannot rewrite a completed day.
  Manual per-100g/per-100ml constants remain available for supplements and
  other items that are not in the library.
- Existing constants were deliberately retained as **legacy fixed portions**:
  their current totals and historical snapshots are unchanged. They explicitly
  prompt the user to edit and link the appropriate library food/recipe before
  enabling the g/ml quantity field; a former serving total is never mislabelled
  as a per-100 value.
- Eight high-confidence existing-library links have been applied without
  recreating food records: both Greek-yogurt constants (200g), ground flaxseed
  (14g), whey protein powder (30g), olive oil (20g and 4.5g), fish oil (4g),
  and potato starch (25g). Eggs, casein, creatine and the vascular shot remain
  fixed because their available library values were absent or materially
  different. Completed days continue to show their original snapshots; users
  can untick and re-tick a linked item to start using its quantity today.
- Backend validation rejects invalid constant quantities and source shapes;
  schema-13 exports preserve the source link, default quantity, per-day
  quantity and snapshot.

The container is healthy on image `recomp-tracker:release-r10-20260917`,
manifest `sha256:a3379e2074e08116237d36766d5734c879b02ae99ac33cabfb6c01f840b1e99d`.
The live browser build is `2026.09.17-r9`, with service-worker cache v28.
Before deployment, a consistent source/database backup was retained at
`/opt/backups/recomp-tracker-quantity-20260917/` and the SQLite checkpoint at
`/opt/stacks/recomp-tracker/data/recomp-pre-quantity-20260917.db`; the
pre-compatibility checkpoint is
`/opt/stacks/recomp-tracker/data/recomp-pre-legacy-correction-20260917.db`,
and the pre-link checkpoint is
`/opt/stacks/recomp-tracker/data/recomp-pre-constant-source-links-20260917.db`.

Verification passed: frontend quantity/snapshot calculations, seven isolated
backend reliability tests, live browser source-preview and layout checks,
no browser console warnings/errors or horizontal overflow, matching
app/frontend/service-worker hashes, `/healthz`, and SQLite integrity. The
production database still has 15 workout sessions and 36 diet days; no test
entries were saved. The live UI confirms a linked 200g Greek-yogurt item
calculates 106 kcal / 22g protein from its per-100g source.

## Compact mobile Diet summary — deployed 2026-09-17

Build `2026.09.17-r10` makes the sticky Diet macro balance a 74px-tall
four-metric strip at phone widths. It retains the consumed/target figures for
calories, protein, carbs and fat, while the secondary remaining/over text and
target-progress note are omitted only from that sticky mobile presentation.
Desktop and the rest of the Diet screen are unchanged. The mobile card values
wrap safely without overflow.

The healthy live container is `recomp-tracker:release-r11-20260917`, manifest
`sha256:8c5014417c8e34bc6c5d1fd02ff863d154109f9d0977eacb034d2c892dfe0140`,
with service-worker cache v29. Verification covered the frontend regression
suite, syntax and whitespace checks, `/healthz`, and a live 390x844 browser
check: four 79px cards fit without overflow, the sticky summary remains 74px
tall at a 4px scroll offset, and the normal browser viewport was restored.

## Workout UUID compatibility fix — deployed 2026-09-21

Some browser/WebView runtimes expose `crypto` but not `crypto.randomUUID()`,
which prevented an otherwise-valid live workout from being saved. Workout
completion now uses `workoutUuid()`: native `randomUUID()` when available, a
standards-shaped UUID v4 made with `crypto.getRandomValues()` otherwise, and a
last-resort random-byte fallback when the Web Crypto API itself is unavailable.

The live container was rebuilt from the retained r11 runtime as
`recomp-tracker:release-r12-20260921`, manifest
`sha256:d3cf8b13b9b8cdbeff568552701ae8d236974c4dee9507a2021cc7368d2a66b7`.
The service-worker cache is v30, so a refresh fetches the new frontend. The
pre-update frontend files and image identity are in
`/opt/backups/recomp-tracker-uuid-fallback-20260921/`; a consistent, verified
SQLite checkpoint is
`/opt/stacks/recomp-tracker/data/recomp-pre-uuid-fallback-20260921.db`.

Verification passed: JavaScript syntax, the frontend regression suite with a
simulated `crypto` object that lacks `randomUUID`, matching tracked/live
frontend hashes, healthy Compose state and `/healthz`, plus SQLite
`PRAGMA integrity_check = ok`. No workout was created or altered for this
deployment check.
