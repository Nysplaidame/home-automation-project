---
title: Recomp Tracker Operations
description: Installation, data protection, notification boundaries and recovery for the self-hosted tracker
tags: [install, tracker, sqlite, backup, recovery]
created: 2026-09-10
modified: 2026-09-10
type: install-guide
status: active
---

# Recomp Tracker Operations

The [feature reference](../../../configs/docker-host/stacks/recomp-tracker/README.md)
describes the UI and data model. This manual covers the deployed service
contract from [Compose](../../../configs/docker-host/stacks/recomp-tracker/docker-compose.yml)
and application source; it is not a new live acceptance record.

Diagrams: [service placement](../../diagrams/infrastructure/docker-host-service-placement.mermaid),
[remote access](../../diagrams/network/remote-access-flow.mermaid),
[backup storage](../../diagrams/storage/storage-and-backup-flow.mermaid).

## Host, state and access

- VM 103, stack `/opt/stacks/recomp-tracker`, direct UI port `8420`, Homepage
  fixed HTTPS proxy `8209`.
- Explicit bridge `10.240.31.0/24` plus the existing external `local-alerting`
  network. The latter is required by the tracked Compose and the ntfy path.
- Persistent SQLite file `/opt/stacks/recomp-tracker/data/recomp.db`, mounted
  inside the app at `/data/recomp.db`. Browser storage is not the system of record.
- The application has no user login. Its trusted source firewall/proxy scope
  is part of the data boundary; never expose it publicly as a rebuild shortcut.
- `.env` supplies `RECOMP_NTFY_TOPIC`, `RECOMP_NTFY_USER`,
  `RECOMP_NTFY_PASSWORD` and `RECOMP_TIMEZONE`. The publisher should write only
  its selected ntfy topic. Keep credentials outside Git and reports.

## Install and last safe stop

1. Complete the docker-host phase and the [ntfy manual](ntfy.md). Check that
   the external network exists; do not create a same-named arbitrary network
   to conceal a missing notification dependency.
2. Copy the full tracked source directory to the stack path, including the
   Dockerfile, requirements, templates, static files and Compose source.
3. Prepare `.env` from `.env.example`, protect it, and preserve any recovered
   `data/` before building. For a blank build, create the data directory with
   permissions appropriate to the tracked runtime; do not overwrite an
   existing database with an empty one.
4. Record the source revision and retain the old local image before an update.
   The stack builds from source, so an image tag alone does not identify which
   source was deployed.

Run on: docker-host shell.

```sh
cd /opt/stacks/recomp-tracker || exit 1
test -f .env
docker network inspect local-alerting --format '{{.Name}}'
docker compose config --quiet
docker compose build
```

Expected: the existing alerting network is found and config/build succeed.
Use the maintenance policy for dependency pulls. Last safe stop is after build
but before startup: startup enables the scheduler as well as the web service.
Do not start a duplicate production copy with live publisher credentials.

Run on: docker-host shell after access, data and notification prerequisites pass.

```sh
cd /opt/stacks/recomp-tracker || exit 1
docker compose up -d --no-build
docker compose ps
curl -fsS http://127.0.0.1:8420/healthz
```

Expected: the container becomes healthy and the endpoint succeeds. Test the
direct UI from an approved source and the fixed Homepage proxy separately.
Use a disposable record to prove a write survives refresh and a second client
read. Do not alter existing diet/workout history for acceptance. Notification
delivery is a separate authorized test; healthy HTTP does not prove it.

## Backup and exports

Use the UI's JSON export for a portable application copy and retain it in a
protected backup location. Its restore preview/pre-import snapshot are useful
recovery aids, but those local snapshots do not replace off-host backups.

The [app-data backup source](../../../configs/docker-host/system/docker-host-app-data-backup.sh)
uses SQLite's backup API to stage `recomp.db`, then copies it to the
`recomp-tracker` directory in dated runs and `latest` on OMV. This is stronger
than copying a changing database file directly, but job success still requires
an isolated restore check. The database contains personal records; keep it out
of the project vault and source repository.

Before updates, retain a consistent database checkpoint, JSON export, source
revision, image ID and protected `.env` recovery information. Verify the exact
backup mount and generation using the [backup strategy](../../../scripts/backup/backup_strategy.md).
Do not invoke the whole-house app-data job just to inspect this service.
Its `--dry-run` creates staging and destination directories, so it is not a
strictly read-only evidence command.

## Isolated restore

Restore into a separate guest or temporary stack with a copied database,
unique container/network names and an unused loopback port. Never attach
production `data/` or the real `local-alerting` network.

The source suppresses notifications when the application's `NTFY_TOPIC` is
empty. For the isolated Compose definition, explicitly set that container
variable empty, remove production publisher credentials and deny notification
egress. The production template's required `RECOMP_NTFY_TOPIC` substitution is
not a restore-test template and should not be copied unchanged.

1. Restore the selected SQLite backup into the isolated data path with the
   saved matching application image.
2. Open the isolated UI and inspect representative routines, completed
   sessions, diet records and settings without changing the production service.
3. Create/edit a disposable item, restart the isolated app and verify persistence.
4. Separately test the saved JSON export through restore preview in the isolated
   copy. Review the proposed changes before applying them there.
5. Record generation, source/image, data checks, notification isolation and
   elapsed recovery time. Remove only the identified test resources afterward.

Do not overwrite production with a restored database until the operator has
reviewed which records changed after the backup and chosen a recovery point.

## Troubleshooting

Run on: docker-host shell.

```sh
cd /opt/stacks/recomp-tracker || exit 1
docker compose ps
docker compose logs --tail=60
df -h /opt/stacks/recomp-tracker/data
```

| Symptom | Next check | Bounded recovery |
|---|---|---|
| Startup fails on external network | Verify `local-alerting` and ntfy installation | Restore the intended dependency; do not add a broad network |
| Health passes but UI is wrong | Source/image revision, browser errors and matching static/template files | Restore a coherent build; avoid mixing files from different releases |
| Save rejected after another client edited | Version conflict and latest server record | Refresh/reconcile the change rather than replaying stale writes |
| Database locked or unwritable | Duplicate app process, actual mount, free space and permissions | Preserve logs and a consistent backup; do not delete SQLite journal/WAL files |
| Reminders absent | Topic/user scope, app timezone, scheduler logs and ntfy response | A subscriber test or HTTP health is not publisher acceptance; test delivery separately |
| Direct access works, portal fails | Fixed `8209` upstream and source grant | Use the written Homepage diagnostic path |

## Update and rollback

Review the source changes and data migrations, save the checkpoint above, and
build the candidate from a recorded revision. Recreate only this service and
repeat health, UI, persistence and intended notification checks. If a migration
or feature test fails, stop the candidate and restore the old coherent image
with its matching database checkpoint. Preserve post-checkpoint data for review
instead of silently discarding it. A restart or JSON export alone does not
prove this rollback path.
