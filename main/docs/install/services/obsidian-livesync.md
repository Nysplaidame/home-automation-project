---
title: Obsidian Self-hosted LiveSync
description: Central multi-device synchronization for the project documentation vault
tags: [install, docker-host, obsidian, couchdb, tailscale]
created: 2026-06-21
modified: 2026-08-24
type: install-guide
status: live-client-setup-pending
---

# Obsidian Self-hosted LiveSync

## Purpose

Provide rapid multi-device freshness for the Obsidian vault without replacing
Git history, off-host backups, or the canonical checkout rule.

## Architecture

Obsidian remains a local application on each device. CouchDB on docker-host is
the central synchronization backend for the Self-hosted LiveSync community
plugin. Git remains the durable version history and GitHub backup; LiveSync
removes the need to pull before reading or editing on another device.

The canonical vault is `K:\Documents\Obsidian\home-automation-project`. Other
device checkouts are working copies and may lag or diverge; do not initialise
the CouchDB database from an old `E:` or `G:` checkout. The backend is
`obsidian-sync.home.local:5984` internally. Mobile clients must
use the Tailscale HTTPS endpoint
`https://docker-host.tail7012a0.ts.net:8443`. Tailscale Serve is enabled and the
authenticated endpoint has been validated. The database is
`home-automation-project`.

Credentials are stored only in `/opt/stacks/obsidian-livesync/.env` and must be
copied to Bitwarden under `obsidian-livesync`. The LiveSync E2EE
passphrase and setup-URI passphrase are separate secrets and also belong there.

## Runs on

- docker-host over SSH at `192.168.20.102` for CouchDB;
- the canonical `K:` checkout for the first authoritative client;
- a separate, backed-up working copy for the second-device acceptance test;
- Tailscale admin/clients only for the approved HTTPS `8443` path.

## Prerequisites

- Phase 05 docker-host, Phase 06 OMV backup, and Phase 08 baseline complete.
- One explicit authoritative vault selected; for this project it is the `K:`
  checkout unless the project rules are deliberately changed first.
- Both vault copies backed up and all intended Git changes committed/pushed.
- Every other vault writer/synchronizer disabled during first upload, including
  Obsidian Sync, iCloud, OneDrive, Dropbox or automated Git operations.

## Inputs

- `<OBSIDIAN_LIVESYNC_ADMIN_USER>` and
  `<OBSIDIAN_LIVESYNC_ADMIN_PASSWORD>` from the
  [secrets ledger](../reference/secrets-placeholder-ledger.md).
- Separate vault-encryption and Setup-URI passphrases stored in Bitwarden; the
  Setup URI and its passphrase must not travel through the same channel.

## Backend installation

Run on: docker-host over SSH.

```sh
install -d -o 5984 -g 5984 -m 0750 /opt/stacks/obsidian-livesync/data
cp /path/to/repo/main/configs/docker-host/stacks/obsidian-livesync/docker-compose.yml \
  /opt/stacks/obsidian-livesync/docker-compose.yml
cp /path/to/repo/main/configs/docker-host/stacks/obsidian-livesync/local.ini \
  /opt/stacks/obsidian-livesync/local.ini
cd /opt/stacks/obsidian-livesync
read -r -p 'CouchDB admin user: ' couch_user
read -r -s -p 'CouchDB admin password: ' couch_password
printf '\n'
umask 077
printf 'COUCHDB_USER=%s\nCOUCHDB_PASSWORD=%s\n' \
  "$couch_user" "$couch_password" >.env
unset couch_user couch_password
docker compose config --quiet
docker compose config --images
ss -lnt '( sport = :5984 )'
```

Expected result: `.env` is mode `0600`, Compose prints the reviewed CouchDB
digest, and no unexplained listener owns `5984`. Stop here if validation fails;
the backend has not been started and no client data can sync yet.

Run on: docker-host over SSH after the pre-start review passes.

```sh
cd /opt/stacks/obsidian-livesync
docker compose up -d
docker compose ps
curl -I http://127.0.0.1:5984/
```

Expected result: the container is running and anonymous HTTP returns `401
Unauthorized`. A `200` anonymous response is a security failure.

Run on: docker-host over SSH as root; do not enable shell tracing.

```sh
cd /opt/stacks/obsidian-livesync
set -a
. ./.env
set +a
status="$(curl -sS -o /dev/null -w '%{http_code}' \
  --user "$COUCHDB_USER:$COUCHDB_PASSWORD" \
  -X PUT http://127.0.0.1:5984/home-automation-project)"
case "$status" in
  201) printf 'database created\n' ;;
  412) printf 'database already exists; inspect before client initialisation\n' ;;
  *) printf 'unexpected CouchDB status: %s\n' "$status" >&2; exit 1 ;;
esac
unset COUCHDB_USER COUCHDB_PASSWORD
```

Expected result: a blank rebuild returns `201`. `412` is acceptable only when
the existing database provenance and backup have been reviewed; it is not
permission to overwrite remote content.

Current live check on 2026-07-07:

- Container `obsidian-livesync` was up on docker-host.
- `curl -I http://127.0.0.1:5984/` returned `HTTP/1.1 401 Unauthorized`, which
  confirms CouchDB is reachable and requires auth.
- Authenticated CouchDB root check returned CouchDB `3.5.0`.
- Database `home-automation-project` exists and was empty before the first
  authoritative Obsidian upload.
- CORS is enabled under `[chttpd]`; an `OPTIONS` preflight from
  `Origin: app://obsidian.md` returned `204 No Content` with
  `Access-Control-Allow-Origin: app://obsidian.md`.
- Tailscale Serve still maps
  `https://docker-host.tail7012a0.ts.net:8443/` to
  `http://127.0.0.1:5984/`. This admin laptop did not resolve the tailnet name
  during the 2026-07-07 check, so validate the HTTPS endpoint from a
  Tailscale-connected client before relying on mobile/off-LAN sync.
- Self-hosted LiveSync plugin `0.25.80` was installed and enabled in the local
  root Obsidian vault at `.obsidian/plugins/obsidian-livesync`.
- Client wizard setup and second-device rollout remain open because they
  require the CouchDB credential and new E2EE/setup-URI passphrases to be
  entered/stored outside repo files.

## Stop-before-live gate

Starting CouchDB does not make LiveSync live. The irreversible boundary is the
first client's **Restart and Initialise Server** confirmation, which can replace
remote state. Do not cross it unless all of these are true:

- `git -C K:\Documents\Obsidian\home-automation-project status --short` is
  empty and the intended branch is pushed;
- a separate filesystem backup of the canonical vault opens successfully;
- CouchDB has a fresh off-host backup and the remote database is empty or its
  existing content has been explicitly accepted;
- other sync engines are disabled on every participating vault;
- `.git/`, `.obsidian/workspace*.json`, and device-specific cache/state are
  excluded from LiveSync;
- the Tailscale HTTPS endpoint succeeds from every intended remote client.

If any check fails, leave the backend running but client rollout parked. As of
the 2026-08-24 dry-read, the project has uncommitted work, so this gate is not
presently satisfied.

## First authoritative client

1. Open the plugin in the canonical `K:` vault. If onboarding is not visible,
   use **Self-hosted LiveSync settings -> Setup -> Rerun Onboarding Wizard**.
2. Choose **I am setting this up for the first time** and the recommended Setup
   URI/CouchDB path.
3. Enter the approved HTTPS endpoint, database and CouchDB credentials. Enable
   end-to-end encryption with its separate stored passphrase.
4. Select **Test Settings and Continue**. Stop if HTTPS trust, authentication,
   CORS, or database checks fail.
5. Re-read the overwrite warning, then select **Restart and Initialise Server**
   only because `K:` is the selected source of truth.
6. Keep Obsidian open until the queue is empty. Compare the vault file count and
   several representative Markdown/attachment files before adding device two.
7. Generate **Copy current settings as a new Setup URI**, give it a new
   Setup-URI passphrase, and store URI and passphrase separately.

The upstream [quick-setup guide](https://github.com/vrtmrz/obsidian-livesync/blob/main/docs/quick_setup.md)
is the UI-label authority when plugin wording changes.

## Second-device rollout and two-way acceptance

1. Start from a new or separately backed-up vault. Do not point LiveSync at a
   divergent checkout containing unmerged files.
2. Install the same reviewed plugin version and choose **I am adding a device
   to an existing synchronisation setup**.
3. Import the Setup URI, enter its passphrase, choose the existing-device/fetch
   path, and let the initial retrieval finish before editing.
4. Confirm representative Markdown files and attachments match the canonical
   vault.
5. Create `livesync-acceptance-<date>.md` with harmless text on device two;
   verify it appears on `K:`. Append a second line on `K:` and verify it returns
   to device two.
6. Delete the test note only after both devices see both directions and both
   queues are empty. Make the next deliberate Git checkpoint from `K:`.

Keep normal Git commits/pushes as deliberate history. Do not run automatic Git
pull, reset, checkout, clean, or merge operations against an actively synced
vault.

## Backup

Back up `/opt/stacks/obsidian-livesync/data` through the docker-host app-data
backup layer to OMV `backups/docker-host`. CouchDB synchronization is not a
substitute for Git history or an offline backup.

Consistency rule:

- Git remains the deliberate project history and rollback layer.
- Before first two-device rollout, ensure the authoritative vault has a clean
  Git checkpoint and the CouchDB data path is included in the docker-host
  backup plan.
- For file-level restore, stop the CouchDB container first or use a
  CouchDB-native replication/export method.

Run on: docker-host over SSH before accepting the backend backup.

```sh
findmnt -T /mnt/omv/docker-host-backups
backup_id="$(date -u +%Y%m%dT%H%M%SZ)"
backup_root="/mnt/omv/docker-host-backups/manual/${backup_id}/obsidian-livesync"
install -d -m 0750 "$backup_root"
cd /opt/stacks/obsidian-livesync
docker compose stop couchdb
rsync -aH data/ "$backup_root/"
docker compose up -d
test -d "$backup_root/_shards"
curl -I http://127.0.0.1:5984/
printf 'record this LiveSync checkpoint: %s\n' "$backup_root"
```

Expected result: the target is the OMV filesystem, CouchDB shard data exists in
the dated checkpoint, and anonymous production access again returns `401`.
Phase 10 may add the consolidated scheduled job after all required source paths
exist; this stopped checkpoint is the accepted Phase 08 recovery proof.

## Isolated backend restore drill

Test a copy with the same pinned CouchDB image, a separate container name and a
loopback-only port. Keep every Obsidian client pointed at production. Replace
the literal `REPLACE_WITH_RECORDED_ID` below with the timestamp printed by the
accepted backup command.

Run on: docker-host over SSH.

```sh
cd /opt/stacks/obsidian-livesync
restore_root="$(mktemp -d /var/tmp/livesync-restore.XXXXXX)"
chown 5984:5984 "$restore_root"
chmod 0750 "$restore_root"
install -d -o 5984 -g 5984 -m 0750 "$restore_root/data"
backup_source=/mnt/omv/docker-host-backups/manual/REPLACE_WITH_RECORDED_ID/obsidian-livesync
test -d "$backup_source/_shards"
rsync -aH "$backup_source/" "$restore_root/data/"
image="$(docker compose config --images | sed -n '1p')"
docker run -d --name livesync-restore-smoke --restart=no --user 5984:5984 \
  --env-file /opt/stacks/obsidian-livesync/.env \
  -p 127.0.0.1:15984:5984 \
  -v "$restore_root/data:/opt/couchdb/data" \
  -v /opt/stacks/obsidian-livesync/local.ini:/opt/couchdb/etc/local.d/obsidian-livesync.ini:ro \
  "$image"
curl -I http://127.0.0.1:15984/
```

Expected result: anonymous access returns `401`. Authenticate from a trusted
local diagnostic without logging the credential and confirm
`home-automation-project` exists with a non-zero document count. Do not connect
an ordinary client to the restore-smoke database.

Run on: docker-host over SSH after the database check passes.

```sh
data_root="$(docker inspect livesync-restore-smoke \
  --format '{{range .Mounts}}{{if eq .Destination "/opt/couchdb/data"}}{{.Source}}{{end}}{{end}}')"
restore_root="$(dirname -- "$data_root")"
case "$restore_root" in
  /var/tmp/livesync-restore.*) ;;
  *) printf 'refusing unsafe cleanup path: %s\n' "$restore_root" >&2; exit 1 ;;
esac
docker rm -f livesync-restore-smoke
rm -rf -- "$restore_root"
```

Expected result: only the disposable container and verified temporary path are
removed; production still returns an authenticated response on `5984`.

## Rollback and failure recovery

If a client begins uploading the wrong vault, pause/disable LiveSync on every
client first. Preserve the local vaults, CouchDB data and Git state before any
reset. Never use a Git reset or remote database deletion as the first recovery
action.

| Failure | Safe response | Proof before continuing |
|---|---|---|
| HTTPS or CORS test fails | Keep client rollout parked; repair Tailscale Serve, trust or `local.ini`. | Wizard connection test passes without disabling TLS checks. |
| Existing CouchDB database is non-empty unexpectedly | Stop before initialise; back it up and identify its source. | Remote provenance and chosen source of truth are documented. |
| Wrong vault starts uploading | Pause all clients, preserve every copy and CouchDB, then compare Git and file inventories. | One authoritative copy is selected without deleting alternatives. |
| Conflict/duplicate files appear | Stop editing on both devices and export plugin diagnostics without secrets. | Conflicts are resolved on copies and round-trip test is clean. |
| Backend update fails | Restore the previous digest and matching stopped/consistent CouchDB checkpoint. | Auth, database count, CORS and two-device sync pass. |
| Device must be removed | Disable LiveSync on that device and revoke/regenerate shared connection credentials if exposure is possible. | Remaining clients authenticate and the removed device cannot. |

## Household Hub Markdown outbox

Household Hub's optional Obsidian exporter is live at container path
`/exports/obsidian`, backed by
`/opt/stacks/household-hub/data/obsidian-exports` on docker-host. Treat this as
a persistent Markdown staging outbox only. It does not write directly into the
`home-automation-project` CouchDB database because LiveSync owns that internal
document format and may encrypt it.

The 2026-08-09 deployment smoke created a sanitized recipe Markdown note,
verified its content, and removed the exact disposable note. Moving selected
outbox notes into an authoritative Obsidian vault remains a separate controlled
workflow until a supported vault filesystem mount exists.

The export API requires a persisted recipe confirmation UUID, and the confirmed
candidate's title and source URL must match the requested note. An unconfirmed
production probe returned `404` and left the outbox unchanged.

The docker-host app-data job includes the outbox as
`household-hub-exports`. Its dry-run and real NAS run `20260809T130054Z` passed,
and `latest/household-hub-exports` exists.

## Completion checklist

- [x] CouchDB backend responds and requires auth.
- [x] Tailscale HTTPS endpoint documented for mobile clients.
- [ ] Credentials, E2EE passphrase, and setup-URI passphrase stored in
  Bitwarden.
- [x] Local root vault plugin installed and enabled.
- [x] Backend database and CORS preflight verified.
- [ ] Authoritative Obsidian device connected and fully uploaded.
- [ ] Second Obsidian device connected from generated setup URI.
- [x] CouchDB data backup path verified.
- [x] Backup copied to a temporary path and CouchDB shard presence checked;
  repeat the authenticated isolated restore after material changes.
- [ ] `K:` canonical vault has a clean pushed Git checkpoint before initialisation.
- [ ] Two-way disposable-note acceptance passes with no conflict files.
- [ ] Update, device-removal, and wrong-source rollback evidence recorded.
