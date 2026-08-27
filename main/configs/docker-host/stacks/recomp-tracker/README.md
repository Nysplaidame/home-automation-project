# Recomp tracker — containerized

A self-hosted version of the weight-loss/recomposition tracker, built to sit alongside
your other home automation containers. Data lives in SQLite on a mounted volume
(survives container restarts/rebuilds), and it can push reminders via ntfy.

## What's different from the browser artifact

- Server-side SQLite instead of browser storage — accessible from any device on
  your network, not tied to one browser.
- A routine builder with 135 active exercises, custom exercises, duplication,
  drag-and-button ordering, optional exercises, supersets/circuits with shared
  rounds and rest, and reusable warm-up/cooldown templates. Exercise names use
  `Exercise - Variation`; every exercise has an editable form cue, at least
  three setup/performance steps, and a lightweight in-app position schematic
  shown in the library and live workout.
- A daily Diet tab with editable/archivable constants and foods, user-managed
  meal sections, reusable saved meals, weight-based macro/calorie totals,
  configurable targets, saved daily records and a copy-previous-day shortcut.
  Completed days retain nutrition snapshots, so later library changes cannot
  rewrite history. The separate Food library tab provides searchable,
  category-filtered per-100g/per-100ml foods, with ascending/descending sorting by name,
  calories, protein, carbohydrate or fat. Foods can be favourited, and the Diet
  tab offers favourite/recent-food shortcuts. Its sticky daily balance shows
  consumed and remaining macros against editable Standard, Training and Rest
  target profiles assigned across the week. Values should be checked against
  the relevant label or recipe. Foods can also carry search aliases and
  reusable scoop/slice/tablespoon/portion presets; meal sections surface their
  own recently used foods. The recipe builder combines saved ingredients with
  a final cooked yield and creates a calculated per-100g food with an automatic
  whole-recipe serving. Source-quality labels distinguish official CoFID,
  calculated recipes, supplied sources and personal entries. Archived foods
  have a searchable restore manager.
- A live workout tab: persistent session stopwatch, 60/90/120-second rest
  timers, pause/resume, a sticky control card and a persistent compact mode.
  Rest can start automatically after a completed set or shared group round;
  compact form/substitution guides are lazy-loaded only when opened. The runner
  has per-set completion checkboxes, reps/load/RPE and set-type fields,
  previous-session context, one-tap prior-performance/set copying and
  exercise-specific form cues. Routines can define
  planned sets, rest, target RPE and set type per exercise; completed sessions
  retain their copied details. Any weekly programme session can be loaded
  directly into this runner with its warm-up, skill, accessory and cooldown
  targets. Set completion synchronises the related programme checkbox; each
  programme exercise can record assistance/variation, tempo and form quality.
  The runner visually groups supersets/circuits, allows optional work to be
  skipped, and offers one-tap easier/harder or full-library substitutions while
  preserving the slot's sets, targets, rest, programme link and substitution
  history. Exercises may also be added, removed or reordered during the live
  session. Assistance/variation, tempo, form quality, discomfort, failed-set
  flags and short cues are saved with the exercise. A serialized debounced
  autosave indicator and one-step workout undo protect rapid edits.
- A progression and planning layer: routines can be assigned to weekdays and
  appear on Today in a seven-day calendar, with one-off rescheduling that does
  not alter the normal routine. Routine edits retain version snapshots and
  completed sessions keep the version they used. Each exact exercise variation
  has a recent-performance chart and a conservative next-session suggestion
  based on its logged range, load, RPE, form, failed-set and discomfort data.
  Suggestions never invent bodyweight loads and can be applied to the draft for
  review before sets are completed. The runner also includes a configurable
  bar/plate calculator, while Review stores the normal load increment, bar
  weight and available plate pairs.
- A weekly Dashboard that combines recorded diet adherence, protein-target
  days, completed and planned training, sets/work, sleep, weight trend and
  habit completion without treating missing entries as zero. Recovery signals
  remain conservative and explain which logged readiness, form, failure, RPE
  or discomfort data produced them.
- Exercise goals for reps, hold duration or external load. Goals can be edited,
  archived and restored; their progress and milestones use the same reconciled
  history as Records, so legacy exercise names continue contributing after a
  library rename without rewriting completed workouts.
- A configurable HIIT interval timer at the top of Workout, with work, rest,
  round and preparation controls, 40/20, 30/30 and Tabata presets, pause/resume,
  automatic generated transition alarms and a screen wake-lock request while
  running. Values are saved as defaults, and the timer does not create a
  workout record by itself.
- Finishing a workout now opens a post-session summary with completed/planned
  sets, work, numeric loaded volume, duration, average logged RPE, PR signals,
  discomfort and comparison with the previous matching routine. Records keeps
  the same summary with each session. Blank RPE fields remain unscored rather
  than being treated as zero, and recovery flags are deliberately advisory.
- Editable daily and workout history with a short undo window. Data writes use
  optimistic version checks, and the server retains prior KV revisions so a
  second device cannot silently overwrite a newer change.
- Built-in JSON export, restore preview and a server-side pre-import snapshot.
- A Records tab with date-range presets, meal/workout and routine filters, plus
  filtered calorie, protein, target-adherence and workout summaries. It also
  reports personal records by reconciled exercise variation, eight-week completed
  sets/reps-or-seconds and numeric loaded volume, programme adherence, recent
  joint-discomfort/form-quality flags, and a durable skill-stage timeline.
- A long-term tendon-first calisthenics Programme tab for muscle-up, handstand
  push-up and planche. It keeps independent skill stages, phase/week position,
  prerequisites, deload and joint-comfort notes, exact advancement criteria,
  and editable four-week test records. Each weekly session is an executable
  checklist: wrist/shoulder preparation, current skill work, accessories and
  stretches all have their own persistent checkbox and linked form steps.
- A background scheduler pushes ntfy notifications:
  - Timed light, hydration, meal, supplement and post-meal movement prompts
  - Day-aware workout prompts: calisthenics Mon/Wed, cardio Tue/Thu, weights
    Sat, and a rest-day prompt Fri/Sun
  - Monthly reminder for photos/waist/weigh-in

The original artifact markup remains in `templates/index.html` for the Guide.
`static/app-v2.js` supplies the self-hosted tracker interface and its
server-backed persistence features.

## Food-library source data

As of 2026-08-24 the live library has 2,691 active foods. It retains the
existing personal/curated entries and adds 2,392 usable current records from
McCance and Widdowson's Composition of Foods Integrated Dataset (CoFID) 2021.
Each imported record retains its CoFID food code and exact source description;
the description deliberately states preparation (for example raw, baked,
boiled, canned/drained) because values differ between forms. Branded or recipe
foods should still be added from their own label. Rows whose core macros are
unavailable and descriptions weighed with bone/shell are excluded. Alcoholic
drinks retain CoFID's per-100ml basis; other imported records use per 100g.

`tools/import_cofid_foods.py` is a reproducible, dry-run-first importer with
curated and `--full` modes. It adds only absent names/codes and uses the
version-checked API, so it does not replace user-created foods or silently
overwrite another device's change. The Food library renders 80 results at a
time so search and nutrient sorting remain responsive at this size.

`static/exercise-catalog.json` is the canonical guided exercise catalogue.
`tools/expand_exercise_library.py` is the dry-run-first migration that renames
legacy exercises, refreshes form guidance, updates routine references and adds
missing catalogue entries without rewriting completed workout history.

The food library is stored in one version-checked JSON record by design. With
2,691 foods that record is about 840 KB, so the backend retains a bounded 8 MB
request ceiling (configurable with `MAX_CONTENT_LENGTH`) rather than the former
1 MB ceiling. This leaves room for recipes, aliases and servings while still
rejecting unexpectedly large requests. Backups using schema version 10 include
food metadata, programme stage history, progression links, routine groups,
optional exercise flags, reusable routine templates, compact-workout settings
and live-session rest/quick-note state, weekday schedules and overrides,
routine versions, equipment/load settings, workout summaries, exercise goals
and saved HIIT defaults.

## Setup

1. Copy this folder to `/opt/stacks/recomp-tracker` on docker-host.
2. Create `/opt/stacks/recomp-tracker/.env` from `.env.example`. Use a
   dedicated ntfy publisher account with write access only to the selected topic.
   The local ntfy server denies anonymous publishing, so the username and
   password are required.
3. The standalone `docker-compose.yml` is canonical. It joins the existing
   `local-alerting` network and publishes the UI on port 8420.
4. `docker compose up -d --build`
5. Visit `http://<docker-host>:8420`.
6. Subscribe to the topic through the self-hosted ntfy server, not ntfy.sh.

## Deliberately out of scope for now

- Food database/barcode scanning and in-app progress-photo storage. These need
  a separate privacy, licensing and storage design; photos are intentionally
  recorded as a monthly-review checkbox and kept in the private photo library.
- Internet exposure. The app has no user login and is intentionally limited to
  the trusted LAN/Tailscale firewall scope. Add authentication before exposing
  it through a public reverse proxy.
