# Handoff: recomp-tracker → deploy to docker-host (VM 103)

## What this is

A personal weight-loss/recomposition tracker (daily habits, workouts, a long
reference Guide, ntfy reminders). It's been running for weeks as a **Claude
artifact** (browser storage, works today, no deployment needed) and is now
being moved to run as a **real, always-on service** on the user's home
docker host, mainly to get the ntfy push notifications actually working
(the artifact can't run a background scheduler when the tab is closed).

## Current deployment state (2026-08-13)

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
- Food-library population (2026-08-14): the live library has 281 active foods
  (existing entries retained plus 257 common generic foods imported from UK
  CoFID 2021). Every imported item has the exact CoFID food name/code and
  per-100g energy, protein, carbohydrate and fat values; source names state
  preparation so raw, cooked and canned/drained items are not conflated.
  `tools/import_cofid_foods.py` is the dry-run-first, conflict-aware
  reproducible importer. It only adds missing names and never overwrites a
  user-created food.
- Navigation refinement (2026-08-14): Diet now focuses on logging a day;
  food creation/editing/archive work is in its own `Food library` tab. The
  library has live text search and category filtering for its 281 active foods.
  The former Trends tab is now `Records` and holds saved meal days plus completed
  workouts. The former Habits tab is `Habits & Trends`, combining the streaks
  with the weight, waist and sleep trend charts.
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
`exercise-library`, `tracker-settings`, `monthly-reviews`,
`reminder-settings`, and `active-workout`. Keep the model in those JSON blobs;
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
