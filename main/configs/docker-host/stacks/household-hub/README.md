# Household Hub deployment boundary

This directory contains a network-safe production Compose mirror, **not the
complete application source**. `docker-compose.prod.yml` explicitly expects a
separate Household Hub deployment repository. Its relative build context
`../..`, `apps/api/Dockerfile`, `apps/web/Dockerfile` and export path are intended
for that repository's layout, not this mirror directory.

Do not run `docker compose up --build` here or imply this mirror alone is a
fresh rebuild manual. The exact source checkout/revision, migration commands,
build artifacts and application restore procedure must be recovered from the
separate repository before a blank deployment can be certified.

## Contract visible in this mirror

- VM103 stack `/opt/stacks/household-hub`; web listener8100; explicit
  `10.240.14.0/24` network plus external `searxng`, `mealie` and `grocy` networks.
- PostgreSQL, Redis and Qdrant use named volumes. API and web are separate
  application images/builds. A successful database health check does not prove
  schema migration, API authorization or household workflows.
- Protected inputs include PostgreSQL credentials, Household Hub API token
  and HA secret, plus enabled integration credentials. Keep the populated
  environment in the deployment's approved secret store, never this vault.
- `HOUSEHOLD_HUB_AUTO_CREATE_SCHEMA` defaults false. Do not turn it on simply
  to conceal a missing migration procedure.
- The central VM103 app-data backup copies `data/obsidian-exports`, not all
  three named service volumes. That export copy alone is not a Household Hub
  database/vector-store restore strategy.

## Recovery requirements still to close

1. Record the canonical application repository location and deployed revision.
2. Link its verified build, database migration and rollback procedures.
3. Capture PostgreSQL and Qdrant recovery artifacts and establish whether Redis
   state is reconstructible or requires backup for this application.
4. Prove an isolated restore with copied stores and disabled production
   integration/notification credentials; never let a test clone write to HA,
   Grocy, Mealie or the live Obsidian export destination.
5. Validate API authorization, representative household workflows and matched
   image/schema rollback before calling the documentation rebuild-complete.

See [service placement](../../../../docs/diagrams/infrastructure/docker-host-service-placement.mermaid),
[storage/backup](../../../../docs/diagrams/storage/storage-and-backup-flow.mermaid),
the [service matrix](../../../../docs/reference/service-matrix.md) and
[documentation checklist](../../../../docs/install/INSTALL-TO-DO.md).

## Historical recovery leads

The [current handoff](../../../../HANDOFF-2026-07-27-portal-services.md) records
an August9 Alembic migration `20260809_0002` for `recipe_workflows`, disposable
PostgreSQL migration round-trip tests, and the protected pre-migration dump
`/opt/backups/household-hub/pre-recipe-workflow-20260809.sql.gz`. Source rollback
copies were made beneath `/opt/stacks/household-hub/` with dated `.bak` suffixes.
These are useful recovery leads, not proof the files still exist or cover the
current schema/data. Preserve them during source recovery; do not restore an
August checkpoint over the live database simply because its path is recorded.

Recover the deployment repository metadata and deployed revision from that
host through an existing authorized management route, then match its migration
history and built images to a current consistent database checkpoint. Repository
remotes can contain credentials: record only a sanitized location, never raw
remote URLs or populated environment output. The vault mirror still lacks the
application source and cannot supply the missing migration command reliably.

## September 11 live source and schema inspection

Read-only SSH inspection located the live application tree at
`/opt/stacks/household-hub`, including `apps/api`, `apps/web`, `apps/worker`,
shared packages and `infra/docker`. No `.git` directory was found within three
levels of the stack root; repository/commit provenance and a complete off-host
source checkpoint remain unresolved. The vault still contains only the mirror.

The live API Dockerfile sets `/app` as its working directory and starts with
`alembic -c /app/alembic.ini upgrade head && uvicorn household_hub.main:app ...`.
Alembic obtains its URL from `DATABASE_URL`; thus starting that API image can
change the database even when `HOUSEHOLD_HUB_AUTO_CREATE_SCHEMA=false`.
Do not rely on the application schema flag to disable entrypoint migrations.
Keep API/worker stopped during an isolated database import; override the test
entrypoint or inspect the schema with PostgreSQL first. Enable the saved API
only after comparing the imported schema ledger and saved migrations.

Read-only `SELECT version_num FROM alembic_version` returned `20260809_0002`.
The two migration files found in the live tree are:

| Artifact | SHA-256 |
|---|---|
| API Dockerfile | `8dfe752aaf12f53f4283dde8fab2696413c1eaf88affe7d1413dd87cd9a623e9` |
| `20260617_0001_create_transcript_tables.py` | `5f5754927d5af675d7f10d0ec9b520ef2636a131b5cc487b76cdafbebdacea77` |
| `20260809_0002_create_recipe_workflows.py` | `2b6975924f1dd7195b606fe9e41c2acd98c6327f06c2249570d036ca0aad194a` |

A matching ledger is only schema metadata, not proof of a complete PostgreSQL,
Qdrant or Redis backup. Preserve a verified application generation and complete
store recovery contract before upgrading. Prefer a matched old database/image
checkpoint for rollback; do not assume an Alembic downgrade reverses application
or external integration side effects. No migration or domain-data query was
executed during this inspection.

## September 11 off-host source checkpoint

A source snapshot was copied to the restricted workstation recovery directory
`C:/Users/Admin/home-automation-recovery/source-20260911-224938/household-hub-source.tar.gz`.
SHA-256: `be21e45bc0b1604b231d3c51cc36bbc5366cb25053f7f1fbda3a426f9b7eadab`. Remote/local hashes matched and the archive member stream
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

## September 12 source-build and isolated restore acceptance

The recovered off-host archive successfully built API, worker and web images.
Builds required the existing permitted package-download path; offline builds
failed because dependencies were not cached. Production images/containers were
not replaced. Repository commit provenance remains unknown, but the dated source
archive and build logs now identify a tested recovery generation.

A fresh PostgreSQL logical dump imported with `ON_ERROR_STOP=1` into a disposable
PostgreSQL container with networking disabled. Its ledger matched20260809_0002.
The rebuilt API shared that isolated database namespace, used only a test token,
and bypassed the image's automatic-migration entrypoint. Health, authenticated
`/api/transcripts` read and anonymous401 denial passed. Containers were removed.

Two Qdrant collection snapshots were captured and restored with the same live
image into a separate network-disabled instance; collection point counts matched
4 and1 (five total). Snapshot hashes were verified. This followed the
[Qdrant snapshot procedure](https://qdrant.tech/documentation/operations/snapshots/):
start an empty same-version single-node instance with each saved snapshot mapped
to its original collection using `--snapshot`. Production storage was never
mounted writable into the test. Redis reported zero keys at inspection; this
is not a general guarantee that future queued work can be discarded.

Protected scripts, import/build logs, dumps and snapshot manifests reside at
`/root/recovery-verification-20260912/`; off-host dumps and Qdrant snapshots are
in the restricted workstation source-recovery directory. These were separate
component checkpoints, not a coordinated cross-store transaction. Future changes
that span PostgreSQL/Qdrant/Redis require a quiesced matched recovery point.
Worker delivery, external integrations and every browser workflow were not
exercised; do not promote those as newly verified.

## September 15 coordinated recovery checkpoint

A one-off coordinated backup now exists on the NAS at
`/mnt/omv/docker-host-backups/household-hub-coordinated/20260915T142413Z`.
Web/API were stopped before all three stores; with all writers stopped, cold
volume archives captured PostgreSQL, Redis and Qdrant together. The checkpoint
also includes `.env`, `infra/docker` and `data/obsidian-exports`. No worker is
running in this deployment; the recovered worker source is a placeholder loop.
The original five containers were restarted and production API health returned200.
This operation briefly interrupts Hub availability; it is not a scheduled job.

The owner-only checkpoint contains `manifest.json`, `SHA256SUMS`, `COMPLETE`,
three volume archives and `deployment-and-exports.tar.gz`. Treat it as secret and
household data. Require COMPLETE and verify every checksum before restore.
Incomplete directories must never be selected merely because they are newest.

A disposable restore extracted copies to a protected directory, used the exact
store images, and shared only a network-disabled namespace. PostgreSQL ledger
20260809_0002, Redis zero-key count, Qdrant collections with1 and4 points, API
health/authenticated transcript read and anonymous401 all passed. Configuration
and exports also extracted successfully. Original backup archives were untouched;
test containers were removed. Scripts and restored copies remain protected under
`/root/recovery-verification-20260915/`.

For recovery, restore each volume into a new empty destination using the manifest
mapping and matching image; never extract over an active database. Restore the
configuration/exports privately and preserve numeric file ownership. Start stores
before API/web. During isolated validation, omit production networks/integrations,
use a test token and override API startup to bypass automatic Alembic migration.
Read-only API checks do not prove external integrations or every browser workflow.
For live recovery, review integration destinations and schema/image compatibility
before allowing writes or restoring the original API entrypoint.

## Offline image recovery, September 15

The NAS directory `/mnt/omv/docker-host-backups/offline-app-images/20260915`
contains `images.tar`, image/content identity manifest, checksums and both dated
source archives. It preserves the six recovered API/worker/web images plus the
GardenKeeper PostgreSQL and Hub PostgreSQL/Redis/Qdrant images (ten total).
Installed dependencies are embedded in these images; independent offline builds
from source still require a package/base-image dependency bundle.

Verify `SHA256SUMS` and `SOURCE-SHA256SUMS` in this protected directory, then use
`docker image load -i images.tar` on the recovery host. Application tags are
`recovery-<gardenkeeper|household-hub>-<api|worker|web>:20260912`.
Store images saved by ID may load untagged: inspect `docker image ls -a` and match
architecture, RootFS layers and configuration to the manifest before selecting
one. Different Docker image-store backends can report different image IDs for
identical content; an ID string alone is insufficient across backends.

The archive was loaded into an initially empty, separate Docker daemon. All ten
image configurations/layer sets matched; both API dependency imports, both web
nginx executables and both worker Python executables ran with no networking and
`--pull never`. The temporary daemon and its10GB working store were removed,
returning host free space to14GB. This proves image availability and executable
checks, not full offline worker/application integration or source rebuilds.
