# Recomp tracker — containerized

A self-hosted version of the weight-loss/recomposition tracker, built to sit alongside
your other home automation containers. Data lives in SQLite on a mounted volume
(survives container restarts/rebuilds), and it can push reminders via ntfy.

## What's different from the browser artifact

- Server-side SQLite instead of browser storage — accessible from any device on
  your network, not tied to one browser.
- A routine builder with the full built-in exercise list, custom exercises, and
  reusable routine templates.
- A daily Diet tab with editable/archivable constants and foods, user-managed
  meal sections, reusable saved meals, weight-based macro/calorie totals,
  configurable targets, saved daily records and a copy-previous-day shortcut.
  Completed days retain nutrition snapshots, so later library changes cannot
  rewrite history. The separate Food library tab provides searchable,
  category-filtered per-100g foods and should be checked against the relevant
  label or recipe.
- A live workout tab: persistent session stopwatch, 60/90/120-second rest
  timers, per-set completion checkboxes, reps/load/RPE and set-type fields,
  previous-session context and exercise-specific form cues. Routines can define
  planned sets, rest, target RPE and set type per exercise; completed sessions
  retain their copied details.
- Editable daily and workout history with a short undo window. Data writes use
  optimistic version checks, and the server retains prior KV revisions so a
  second device cannot silently overwrite a newer change.
- Built-in JSON export, restore preview and a server-side pre-import snapshot.
- A background scheduler pushes ntfy notifications:
  - Timed light, hydration, meal, supplement and post-meal movement prompts
  - Day-aware workout prompts: calisthenics Mon/Wed, cardio Tue/Thu, weights
    Sat, and a rest-day prompt Fri/Sun
  - Monthly reminder for photos/waist/weigh-in

The original artifact markup remains in `templates/index.html` for the Guide.
`static/app-v2.js` supplies the self-hosted tracker interface and its
server-backed persistence features.

## Food-library source data

On 2026-08-14 the live library was expanded to 281 active foods. The 257
CoFID additions are common generic UK foods from Public Health England's
McCance and Widdowson's Composition of Foods Integrated Dataset (CoFID) 2021.
Each imported record retains its CoFID food code and exact source description;
the description deliberately states preparation (for example raw, baked,
boiled, canned/drained) because values differ between forms. Branded or recipe
foods should still be added from their own label.

`tools/import_cofid_foods.py` is a reproducible, dry-run-first importer. It
adds only absent names and uses the version-checked API, so it does not replace
user-created foods or silently overwrite another device's change.

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
