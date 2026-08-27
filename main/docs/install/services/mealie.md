---
title: Mealie Install Manual
description: Live internal recipe and meal-planning service
tags: [install, docker-host, mealie]
created: 2026-05-24
modified: 2026-08-24
type: install-guide
status: live
---

# Mealie Install Manual

## Purpose

Host household recipes and meal planning.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- Phase 05 docker-host and Phase 06 OMV backup storage complete.
- The tracked Compose file reviewed, including its pinned image digest and
  explicit `10.240.5.0/24` network.
- Internal-only access chosen; no public listener or open signup.
- A password-manager record prepared for the permanent administrator.
- Port `9925` unused by any other service.

## Inputs

- `<MEALIE_ADMIN_EMAIL>` and `<MEALIE_ADMIN_PASSWORD>` from the
  [secrets ledger](../reference/secrets-placeholder-ledger.md).
- Optional `<MEALIE_API_TOKEN>` only after the permanent administrator exists.
- An operator ready to replace the bootstrap administrator on first login.

## Commands

Run on: docker-host over SSH.

```sh
install -d -o 1000 -g 1000 -m 0750 /opt/stacks/mealie/data
cp /path/to/repo/main/configs/docker-host/stacks/mealie/docker-compose.yml \
  /opt/stacks/mealie/docker-compose.yml
cd /opt/stacks/mealie
docker compose config --quiet
docker compose config --images
ss -lnt '( sport = :9925 )'
```

Expected result: Compose validation prints no error, the image output is the
reviewed pinned Mealie reference, and the socket query prints no existing
listener. Stop here if any condition differs. Merely copying the stack does not
approve it for use.

Run on: docker-host over SSH after the pre-start checks pass.

```sh
cd /opt/stacks/mealie
docker compose up -d
```

## Explanation

The SQLite deployment is appropriate for this household. The image is pinned to
`v3.19.2`, open signup is disabled, and `mealie.home.local` is the canonical
internal name. Image pulls use the temporary Docker-host maintenance window in
`docs/procedures/update_maintenance_playbook.md`.

## Expected result

Mealie loads at `http://mealie.home.local:9925/`.

Current live check on 2026-07-05:

- Container `mealie` was up and healthy on docker-host.
- `curl -I http://127.0.0.1:9925/` returned `HTTP/1.1 200 OK` from docker-host.
- Bootstrap credential replacement remains the open operator action; do not
  store or rotate the Mealie admin credential in repo files.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/mealie && docker compose ps
curl -fsS -o /dev/null http://127.0.0.1:9925/
```

## Operator setup

Do this from a trusted browser on HomeAdmin/LAN or over the approved docker-host
Tailscale path:

1. Open `http://mealie.home.local:9925/`.
2. Sign in with the bootstrap administrator only long enough to replace it.
3. Change the administrator email/password to `<MEALIE_ADMIN_EMAIL>` and
   `<MEALIE_ADMIN_PASSWORD>`.
4. Store the final credential in Bitwarden item `mealie-admin`; never add it to
   Compose, shell history, this vault, or screenshots.
5. Create named household users only if they need separate meal-planning
   history or permissions; otherwise keep one admin plus API tokens.
6. Create a Mealie API token for Home Assistant recipe tools only after the
   final admin credential exists; store the token in Bitwarden and HA
   `secrets.yaml`, not in git.

Completion proof:

- Mealie still returns `HTTP/1.1 200 OK`.
- The bootstrap credential no longer logs in.
- The Bitwarden item exists.
- If the HA recipe tool is enabled, it can search/read a known saved recipe.

## Recipe export and application backup

Mealie 3.x has two different safeguards and this rebuild requires both:

1. In **Settings -> Admin Settings -> Backups** (or `/admin/backups`), create a
   full application backup, download the ZIP, and copy it to the approved
   protected backup location. This is the application-level migration copy.
2. In the group recipe data page, export a small known recipe set and download
   the archive. This proves recipes can leave Mealie in a portable form; it is
   not a substitute for the full application backup.
3. Stop Mealie briefly and create a dated file-level checkpoint on OMV so a
   consistent `data` directory is represented off-host. Phase 10 later adds the
   consolidated scheduled job after its complete source set exists.

Do not test Mealie's in-place **Restore** button against production. It replaces
the current database and is destructive. Use the disposable target below.

Run on: docker-host over SSH after the UI exports have been downloaded.

```sh
findmnt -T /mnt/omv/docker-host-backups
backup_id="$(date -u +%Y%m%dT%H%M%SZ)"
backup_root="/mnt/omv/docker-host-backups/manual/${backup_id}/mealie"
install -d -m 0750 "$backup_root"
cd /opt/stacks/mealie
docker compose stop mealie
rsync -aH data/ "$backup_root/"
docker compose up -d
test -s "$backup_root/mealie.db"
curl -fsS -o /dev/null http://127.0.0.1:9925/
printf 'record this Mealie checkpoint: %s\n' "$backup_root"
```

Expected result: `findmnt` identifies the OMV filesystem, the dated database is
non-empty, and Mealie restarts. If the mount is not remote, stop; do not accept
a copy written into an ordinary local directory. Keep the application ZIP,
portable recipe export and recorded stopped-data path together in the recovery
record.

## Home Assistant recipe tools

The repo includes a Home Assistant custom component at
`configs/home-assistant/custom_components/mealie_llm/`. It exposes narrow LLM
tools for importing a chosen recipe URL, searching saved recipes, and reading a
saved recipe back from Mealie.

To activate it on HA, add a Mealie bearer token to `secrets.yaml`:

```yaml
mealie_api_token: <MEALIE_API_TOKEN>
```

Then add the `mealie_llm` block from `configs/home-assistant/configuration.yaml`
to the live HA config, restart Home Assistant, and enable the `mealie_recipes`
LLM API on the local llama.cpp conversation agent.

Use `http://192.168.20.102:9925` in Home Assistant config so the tool does not
depend on HA resolving the internal `mealie.home.local` hostname.

## Isolated restore drill

Use a copy of the OMV backup, a different container name, a loopback-only port,
and the same pinned image. This validates the file-level recovery copy without
touching production. Replace the literal `REPLACE_WITH_RECORDED_ID` below with
the timestamp printed by the accepted backup command.

Run on: docker-host over SSH.

```sh
cd /opt/stacks/mealie
restore_root="$(mktemp -d /var/tmp/mealie-restore.XXXXXX)"
chown 1000:1000 "$restore_root"
chmod 0750 "$restore_root"
install -d -o 1000 -g 1000 -m 0750 "$restore_root/data"
backup_source=/mnt/omv/docker-host-backups/manual/REPLACE_WITH_RECORDED_ID/mealie
test -s "$backup_source/mealie.db"
rsync -aH "$backup_source/" "$restore_root/data/"
image="$(docker compose config --images | sed -n '1p')"
docker run -d --name mealie-restore-smoke --restart=no \
  -p 127.0.0.1:19925:9000 \
  -v "$restore_root/data:/app/data" \
  -e ALLOW_SIGNUP=false -e PUID=1000 -e PGID=1000 -e TZ=Europe/London \
  "$image"
```

Expected result: `docker ps --filter name=mealie-restore-smoke` becomes healthy
and `curl -fsS -o /dev/null http://127.0.0.1:19925/` succeeds. Use an SSH tunnel
to `127.0.0.1:19925` and confirm the known test recipe and household exist. Do
not expose port `19925` on the LAN.

Run on: docker-host over SSH after the application-level check passes.

```sh
data_root="$(docker inspect mealie-restore-smoke \
  --format '{{range .Mounts}}{{if eq .Destination "/app/data"}}{{.Source}}{{end}}{{end}}')"
restore_root="$(dirname -- "$data_root")"
case "$restore_root" in
  /var/tmp/mealie-restore.*) ;;
  *) printf 'refusing unsafe cleanup path: %s\n' "$restore_root" >&2; exit 1 ;;
esac
docker rm -f mealie-restore-smoke
rm -rf -- "$restore_root"
```

Expected result: only the disposable container and verified temporary path are
removed; production remains healthy on `9925`.

## Updates and rollback

Before an update, read the release notes, download a Mealie UI backup, run the
off-host app-data backup, record the current digest, and update only the tracked
image reference. Re-run Compose validation, health, login, known-recipe, export,
HA-token, and isolated-restore checks. Automatic updates are not approved.

Rollback means restoring the previous Compose/image digest and the matching
pre-update data checkpoint. Do not run an older image against a database already
migrated by a newer incompatible release.

Run on: docker-host over SSH during an approved rollback window.

```sh
cd /opt/stacks/mealie
docker compose down
# Restore the reviewed previous Compose file and its matching stopped-data copy.
docker compose config --quiet
docker compose up -d
curl -fsS -o /dev/null http://127.0.0.1:9925/
```

## Failure recovery

| Failure | Safe response | Proof before continuing |
|---|---|---|
| Port `9925` is occupied | Leave Mealie stopped and identify the existing owner with `ss` and `docker ps`. | One documented service owns the port. |
| Bootstrap login still works | Keep signup disabled and import no household data. | Bootstrap login fails and the named admin succeeds. |
| UI backup or recipe export fails | Preserve the data directory and inspect `docker compose logs --tail=100 mealie`. | Both a full backup and portable recipe export download successfully. |
| OMV target is absent | Stop the backup; repair the mount before copying. | `findmnt` shows the expected remote filesystem. |
| Disposable restore fails | Preserve production and the failed temporary copy; check image/data compatibility. | Known test data opens in the isolated target. |
| Update fails | Restore the previous digest and matching checkpoint. | Health, login, recipe, export, and token checks pass. |

## Completion checklist

- [x] UI loads.
- [x] Signup disabled.
- [x] Data directory is included in the off-host backup job.
- [x] Backup contents have been copied to a temporary path and structurally
  checked; repeat the application-level isolated restore after material changes.
- [ ] Bootstrap administrator credentials replaced and stored in Bitwarden.
- [ ] Full application backup and portable recipe export downloaded.
- [ ] Known recipe opens in a loopback-only isolated restore target.
- [ ] Update and matching-data rollback evidence recorded.
