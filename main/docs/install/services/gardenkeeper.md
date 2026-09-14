---
title: GardenKeeper Install Manual
description: Internal garden care, task, calendar, and map app on docker-host
tags: [install, docker-host, gardenkeeper]
created: 2026-06-29
modified: 2026-09-14
type: install-guide
status: live
---

# GardenKeeper Install Manual

## Purpose

Run GardenKeeper as an internal household garden operations app for plant care
profiles, garden tasks, reminders, calendar projection, mapped zones, and safe
Home Assistant Assist task commands.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- GardenKeeper source is available under `/opt/stacks/gardenkeeper/source`.
- Docker-host has an approved update/build path for base images and npm/pip
  dependencies, either through a temporary maintenance window or offline image
  transfer.
- DNS alias `gardenkeeper.home.local` points to `192.168.20.102`.
- Docker-host firewall template allows ports `8090` and `8091` from approved
  sources.

## Inputs

Required for first deployment:

- Generated `POSTGRES_PASSWORD`.

Optional integration secrets:

- `GARDENKEEPER_NOTIFICATION_BROKER_URL` and broker token, if using the central
  notification broker.
- `HOME_ASSISTANT_WEBHOOK_SECRET`, if enabling Assist command ingress.
- `NEXTCLOUD_CALDAV_URL`, `NEXTCLOUD_USER`, and `NEXTCLOUD_APP_PASSWORD`, if
  projecting tasks and garden calendar events to Nextcloud.
- Mealie, Grocy, and future Knowledge Hub API credentials only after those
  contracts are approved.

## Current live state

GardenKeeper is live on docker-host at:

```text
/opt/stacks/gardenkeeper/
```

Source templates remain under:

```text
configs/docker-host/stacks/gardenkeeper/
```

Live URLs:

- Web UI: `http://gardenkeeper.home.local:8091/`
- API health: `http://gardenkeeper.home.local:8090/health`

Current live integrations:

- Home Assistant package installed at `/config/packages/gardenkeeper_package.yaml`.
- HA Monitoring dashboard includes a GardenKeeper health card and app link.
- Uptime Kuma monitors cover the API health endpoint and web UI.
- ntfy broker integration is configured through the central notification stack.
- Local Postgres dump timer is enabled on docker-host.

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/gardenkeeper
cd /opt/stacks/gardenkeeper
cp /path/to/templates/docker-compose.yml .
test ! -e .env || exit 1
umask 077
cp /path/to/templates/env.example .env
```

Edit `.env`, set generated passwords/secrets, and ensure `DATABASE_URL` uses the
same generated Postgres password.

Place GardenKeeper source at `/opt/stacks/gardenkeeper/source`, then:

Run on: docker-host over SSH.

```sh
docker compose config --quiet && docker compose up -d --build
```

## Explanation

GardenKeeper is a modular monolith with PostgreSQL, Redis, FastAPI, a worker,
and a static React/Vite web app served by nginx. It belongs on docker-host
because it is internal-only, lightweight, and does not run model weights. Local
LLM, STT, TTS, and wake-word inference remain on CT 114 `llm-host`.

## Expected result

- `gardenkeeper-postgres` and `gardenkeeper-redis` are healthy.
- API responds at `http://gardenkeeper.home.local:8090/health`.
- Web UI loads at `http://gardenkeeper.home.local:8091/`.
- API status reports the configured integration state.

## Validation

Run on: Admin laptop.

```powershell
Test-NetConnection 192.168.20.102 -Port 8090
Test-NetConnection 192.168.20.102 -Port 8091
Invoke-RestMethod http://gardenkeeper.home.local:8090/health
```

Run on: docker-host over SSH.

```sh
cd /opt/stacks/gardenkeeper
docker compose ps
docker compose logs --tail=100 api worker web
```

## Backup

Back up:

- `/opt/stacks/gardenkeeper/.env`
- `/opt/stacks/gardenkeeper/docker-compose.yml`
- A checked PostgreSQL logical dump; raw `postgres-data` only as a stopped,
  version-compatible checkpoint, never an ordinary live directory copy.

The docker-host template also includes a lightweight local PostgreSQL dump
timer:

Run on: docker-host over SSH.

```sh
install -m 0755 backup-gardenkeeper.sh /opt/stacks/gardenkeeper/backup-gardenkeeper.sh
install -m 0644 gardenkeeper-backup.service /etc/systemd/system/gardenkeeper-backup.service
install -m 0644 gardenkeeper-backup.timer /etc/systemd/system/gardenkeeper-backup.timer
systemctl daemon-reload
systemctl enable --now gardenkeeper-backup.timer
systemctl start gardenkeeper-backup.service
```

It writes compressed dumps to `/opt/stacks/gardenkeeper/backups/` and keeps
14 days by default.

Read-only check on 2026-07-06:

- `/opt/stacks/gardenkeeper/backups` exists and is `36K`.
- Recent daily dumps exist through
  `gardenkeeper-postgres-20260706T022024Z.sql.gz`.
- A checked PostgreSQL logical dump; raw `postgres-data` only as a stopped,
  version-compatible checkpoint, never an ordinary live directory copy. exists and is `47M`.
- OMV exports `backups/docker-host` to docker-host; the docker-host
  `/mnt/omv/docker-host-backups` mount and daily `03:45` app-data backup timer
  are live and restore-smoked as of 2026-07-07.

The repo-side docker-host app-data backup templates now include
`/opt/stacks/gardenkeeper/backups`. Treat the local dump timer as the database
consistency layer and the docker-host app-data backup as the off-host copy.

Redis data is rebuildable task/worker state unless future behavior makes it
authoritative.

## Failure recovery

- If migrations fail, keep the existing Postgres data directory intact and
  inspect `docker compose logs api` before retrying.
- If the web UI loads but API calls fail, verify nginx proxying through the web
  image and direct API health on port `8090`.
- If Docker pulls fail, use the docker-host maintenance window or offline image
  transfer pattern from `docs/procedures/update_maintenance_playbook.md`.

## Completion checklist

- [x] Stack starts cleanly.
- [x] Web UI loads.
- [x] API health and status pass.
- [x] Docker-host firewall and router DNS include GardenKeeper.
- [ ] Homepage link added.
- [x] Uptime Kuma monitors added for web and API health.
- [x] Secrets stored outside Git.
- [x] Local Postgres dump timer is enabled and producing dumps.
- [x] July7 historical off-host copy/restore-smoke is recorded in the body.
- [ ] Prove a current checked dump and application-level isolated restore.

## Source and migration recovery gap

The tracked Compose builds API/worker/web from `./source`, which is a separate
application checkout absent from this vault template. The live source tree was located and its migration implementation inspected on
September11 (see below). Recover repository provenance, complete source/locks
and matching build artifacts off-host before calling this a reproducible build. `AUTO_RUN_MIGRATIONS` can run migrations at startup;
never start a candidate against the production database merely to discover its
schema requirements. Recover the deployed setting and schema revision first.

## Checked checkpoint and isolated recovery

The pre-September12 script piped `pg_dump` to gzip and could mask dump failure.
That defect is now repaired and deployed: dump, non-empty check, compression and
archive validation run separately, then the checked artifact is published before
retention. The following manual procedure remains a recovery alternative.
Run in Bash on docker-host, after pausing application writes/workers and with
PostgreSQL left running. The destination below is root-only local staging.

Run on: docker-host Bash shell as root.

```bash
set -euo pipefail
umask 077
checkpoint_dir=$(mktemp -d /root/gardenkeeper-checkpoint.XXXXXX)
docker exec gardenkeeper-postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > "$checkpoint_dir/database.sql"
test -s "$checkpoint_dir/database.sql"
gzip "$checkpoint_dir/database.sql"
gzip -t "$checkpoint_dir/database.sql.gz"
printf 'Protected checkpoint: %s\n' "$checkpoint_dir"
```

Copy the successful dump, protected `.env`, Compose, source revision, image IDs,
owned uploads if the recovered application defines any, and configuration to
approved protected off-host storage. Resume unchanged services after capture.
Compression validation is only transport proof; importing is required.

Restore into a disposable Docker VM without production routes. Use new database
storage, loopback UI/API ports, unique container/network names and copied
configuration; remove external alerting networks, production HA/notification/
calendar credentials and automatic schedules. Keep worker and API stopped until
the dump imports into a PostgreSQL instance compatible with the saved version.
Use `psql` with `ON_ERROR_STOP=1` and a disposable owner/database matching the
recovered dump; record its exit status. Do not guess migration commands from
the mirror: obtain them from the recovered application source.

Start the saved API/web against the restored DB with external integrations
removed. Confirm representative plants/tasks/zones and schema version, then a
disposable local task workflow. Treat Redis reconstruction as unproven until
its queued-work semantics are checked in source; do not replay production jobs
from a copied queue. Stop the test and record artifact, source/image/schema,
import and workflow outcomes.

## Update and rollback

Retain old images/source and the checked pre-update checkpoint. Rehearse the
candidate's migration on copied data before changing the production image.
Pause writes/workers, deploy the reviewed generation and validate API/UI/tasks
before restoring integrations. On failure stop the candidate, preserve failed
data, and restore old source/images plus the matched database/configuration.
Account for changes since the checkpoint; an older image alone cannot undo a
schema migration. Unknown source/migration behavior is a stop condition.

Diagrams: [service placement](../../diagrams/infrastructure/docker-host-service-placement.mermaid)
and [backup flow](../../diagrams/storage/storage-and-backup-flow.mermaid).

## September 11 live source and schema inspection

Read-only SSH inspection located the current source at
`/opt/stacks/gardenkeeper/source`. No `.git` directory was found within three
levels of the stack root; this does not establish the upstream repository or
commit. Several dated `source.prev`/`source.pre` copies also exist; they are not
interchangeable with the current source.

The source migration contract is `docs/reference/database-migrations.md` and
`apps/api/gardenkeeper/core/migrations.py`. The latter's SHA-256 is
`7e4efabb79769e58fe6c7026b514fa1a2bcfdf281974479c73bff4d4c21ce443`.
It runs with `python -m gardenkeeper.core.migrations` from `apps/api`, using
the application's configured database. This command **applies** migrations;
it is not a read-only status command and was not executed in this inspection.

The read-only PostgreSQL query of `schema_migrations` returned all versions
`0001` through `0029`. The current source's migration list ends at `0029`.
Versions `0006` and `0009` call `Base.metadata.drop_all` before recreating
application tables. Never omit the migration ledger from a restored database,
clear its entries, or run this runner against a legacy data import merely to
repair missing tables. Such a restore could replay the prototype resets.
For a copied-data rehearsal, restore the complete logical dump including the
ledger, compare its versions with the saved source, and disable automatic
migration and fallback table creation until that comparison is reviewed.

The runner exposes upgrades, not a downgrade workflow. Rollback therefore uses
the saved application generation and complete matching database checkpoint.
These source/schema observations close the unknown migration-command question,
not off-host source recovery, dump-script correctness or actual restore proof.
No domain records were queried and no migration ran.

## September 11 off-host source checkpoint

A source snapshot was copied to the restricted workstation recovery directory
`C:/Users/Admin/home-automation-recovery/source-20260911-224938/gardenkeeper-source.tar.gz`.
SHA-256: `30f42065058ee0387f2b24c9955e414e7b6b7c9bfecf82e351b6b6f8f6141901`. Remote/local hashes matched and the archive member stream
was readable. Windows ACL inheritance is disabled on the recovery directory;
access is limited to the signed-in administrator and SYSTEM. This is a local
protected recovery copy, not an encrypted archival/off-site backup or Git commit.
Remote staging remains at `/root/documentation-source-recovery.ODR9yT`.

The snapshot excludes `.env*`, dependency caches, Git metadata and `.bak` files;
Household Hub also excludes application data and includes only apps, packages,
infra, docs, README and root package manifests. It is not a database, credentials
or complete deployment backup. Review this scoped snapshot against build inputs
before claiming source-complete reconstruction. No secrets were intentionally
printed or added to the vault; treat the archive as protected source material.
Build/import/restore acceptance and repository provenance remain open.

## September 12 repair and restore acceptance (rechecked September 14)

The repaired [backup script](../../../configs/docker-host/stacks/gardenkeeper/backup-gardenkeeper.sh)
uses root-only staging, rejects concurrent runs, cleans failed staging and only
prunes after a complete validated archive is published. It reads the actual
PostgreSQL container user/database rather than parsing shell assignments from
`.env`. A stale lock after a hard kill requires process review before removal;
do not delete an active job's lock.

Seven [offline regression tests](../../../configs/docker-host/stacks/gardenkeeper/tests/test_backup.py)
passed on Linux: partial dump failure, empty dump, compression failure, corrupt
compressed output, invalid retention, concurrent lock and successful publication/
pruning. Run with `python3 tests/test_backup.py` from the stack source on Linux;
Docker calls are mocked and no real database is used by these tests.

The new script is installed at `/opt/stacks/gardenkeeper/backup-gardenkeeper.sh`.
The pre-change script is protected at
`/root/recovery-verification-20260912/gardenkeeper/backup-before.sh`.
Its first live run produced
`gardenkeeper-postgres-20260912T191436Z.sql.gz` with systemd success/exit0.
September14 status still reports success. Do not restore the defective script
as routine rollback; retain it only as historical evidence.

The recovered source archive built API, worker and web images successfully
through the existing permitted package-download path. Offline builds failed
because dependencies were not cached; an offline rebuild still needs dependency
artifacts. No firewall policy changed and no rebuilt image replaced production.

The dump imported into a disposable PostgreSQL instance with `ON_ERROR_STOP=1`;
its0001–0029 ledger matched. The rebuilt API then used that restored database
with automatic migrations/table creation disabled, a test-only token and no
production credentials. `/health`, an authenticated `/api/tasks` read and
anonymous401 denial passed. The database had `--network none`; the API shared
only that isolated network namespace. All test containers were removed.
Worker delivery, every UI workflow and any container-local uploads were outside
this test. Protected logs/scripts/dumps remain under
`/root/recovery-verification-20260912/`; an off-VM dump copy is alongside the
source archive in the restricted workstation recovery directory.
