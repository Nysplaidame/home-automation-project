---
title: Grocy Install Manual
description: Live household food-stock and expiry-tracking service
tags: [install, docker-host, grocy, food-inventory]
created: 2026-06-21
modified: 2026-08-24
type: install-guide
status: live
---

# Grocy Install Manual

## Purpose

Provide the household system of record for stock quantities, storage locations,
purchases, consumption and expiry. Recipes remain in Mealie.

## Runs on

- docker-host over SSH at `192.168.20.102` for Compose and backup work;
- a trusted HomeAdmin/Tailscale browser for Grocy administration.

## Prerequisites

- Phase 05 docker-host and Phase 06 OMV backup storage complete.
- The pinned LinuxServer Grocy image and explicit `10.240.6.0/24` network
  reviewed in the tracked Compose file.
- Port `9283` unused.

## Inputs

- `<GROCY_ADMIN_PASSWORD>` prepared through the
  [secrets ledger](../reference/secrets-placeholder-ledger.md).
- A pre-pilot checkpoint so the first workflow can be reversed.

Grocy runs on docker-host at `http://grocy.home.local:9283/` using the pinned
LinuxServer image for Grocy 4.6.0. Persistent state is under
`/opt/stacks/grocy/config`.

Run on: docker-host over SSH.

```sh
install -d -o 1000 -g 1000 -m 0750 /opt/stacks/grocy/config
cp /path/to/repo/main/configs/docker-host/stacks/grocy/docker-compose.yml \
  /opt/stacks/grocy/docker-compose.yml
cd /opt/stacks/grocy
docker compose config --quiet
docker compose config --images
ss -lnt '( sport = :9283 )'
```

Expected result: Compose validation prints no error, the reviewed pinned image
is shown, and no existing listener owns `9283`. Stop here on any mismatch.

Run on: docker-host over SSH after the pre-start checks pass.

```sh
cd /opt/stacks/grocy
docker compose up -d
```

Expected result: `docker compose ps` shows Grocy running and
`curl -I http://127.0.0.1:9283/` returns the expected login redirect.

The initial login is `admin` / `admin`; replace it immediately with
`<GROCY_ADMIN_PASSWORD>` and store the new credential in Bitwarden. Do not
import household stock while the default password still works.

Current live check on 2026-07-07:

- Container `grocy` was up on docker-host.
- `curl -I http://127.0.0.1:9283/` returned `HTTP/1.1 302 Found`, matching a
  login/session redirect rather than a dead service.
- A database checkpoint was created before seeding:
  `/opt/stacks/grocy/config/data/grocy.db.pre-household-seed-20260707T125250Z`.
- Core household model was seeded:
  - Locations: `Pantry`, `Fridge`, `Freezer`, `Cleaning`, `Garage/Workshop`.
  - Quantity units: existing `Piece`/`Pack`, plus `each`, `box`, `bottle`,
    `jar`, `g`, `kg`, `ml`, and `L`.
  - Product groups: `Dry goods`, `Chilled`, `Frozen`, `Cleaning`,
    `Household consumables`, and `Printer/workshop consumables`.
- OMV app-data backup run `20260707T125454Z` captured the seeded database.
- Home Assistant voice/Assist shopping-list API access was deployed and
  backup run `20260707T132647Z` captured the Grocy API-key state.

## Operator setup

Do this from a trusted browser on HomeAdmin/LAN or over the approved docker-host
Tailscale path:

1. Open `http://grocy.home.local:9283/`.
2. Sign in, replace `admin` / `admin`, sign out, and prove the old password is
   rejected before adding data.
3. Confirm the core locations, units, and product groups or create them before
   products. Avoid near-duplicates such as `Piece`, `piece`, and `each` unless
   their conversion relationship is deliberate.
4. Complete the disposable pilot workflow below before adding the household
   catalogue.

Completion proof:

- Grocy still returns a login redirect instead of an error.
- Locations, units, and product groups exist.
- At least one pilot product can be purchased, consumed, and corrected.
- `/opt/stacks/grocy/config` is included in the docker-host backup plan.

## Disposable pilot workflow

Create one product named `Install Manual Pilot Item`. Assign a simple unit such
as `each`, a storage location, and an expiry-tracked purchase rule. Then:

1. purchase quantity `2` with a near-future expiry date;
2. consume quantity `1` and verify stock becomes `1`;
3. perform an inventory correction to quantity `3` and verify the stock journal
   records the correction rather than silently rewriting history;
4. confirm the item appears in the relevant expiry view;
5. reverse/undo the disposable transactions through Grocy's stock journal where
   the UI permits it, reduce stock to zero, and remove or deactivate the pilot
   product.

Before step 1, create a named database checkpoint. If the UI cannot cleanly undo
the pilot without deleting useful reference data, stop Grocy and restore the
pre-pilot checkpoint during a controlled window. Never experiment on the seeded
household model without a checkpoint.

Run on: docker-host over SSH before the pilot workflow.

```sh
cd /opt/stacks/grocy
docker compose stop grocy
checkpoint="config/data/grocy.db.pre-pilot-$(date -u +%Y%m%dT%H%M%SZ)"
cp --preserve=mode,timestamps config/data/grocy.db "$checkpoint"
test -s "$checkpoint"
docker compose up -d
curl -I http://127.0.0.1:9283/
```

Expected result: a non-empty checkpoint exists and the login redirect returns
after restart. Record the exact checkpoint name with the pilot evidence.

## Backup

Back up `/opt/stacks/grocy/config` through the docker-host app-data backup layer
to OMV `backups/docker-host`. This directory contains the Grocy application
state, including the database used by the LinuxServer container.

Consistency rule:

- Stop the `grocy` container before file-level restore.
- Before large data-model changes, take a manual copy or app export as a
  named checkpoint.

Run on: docker-host over SSH before accepting a new backup.

```sh
findmnt -T /mnt/omv/docker-host-backups
backup_id="$(date -u +%Y%m%dT%H%M%SZ)"
backup_root="/mnt/omv/docker-host-backups/manual/${backup_id}/grocy"
install -d -m 0750 "$backup_root"
cd /opt/stacks/grocy
docker compose stop grocy
rsync -aH config/ "$backup_root/"
docker compose up -d
test -s "$backup_root/data/grocy.db"
curl -I http://127.0.0.1:9283/
printf 'record this Grocy checkpoint: %s\n' "$backup_root"
```

Expected result: the target is the OMV filesystem, the dated Grocy database is
non-empty, and Grocy restarts. Phase 10 may add the consolidated scheduled job
after all required source paths exist; this stopped checkpoint is the accepted
recovery proof during Phase 08.

## Isolated restore and rollback drill

Test a copy under a new container name and loopback-only port. Do not overwrite
the live `config` directory merely to prove that a backup exists. Replace the
literal `REPLACE_WITH_RECORDED_ID` below with the timestamp printed by the
accepted backup command.

Run on: docker-host over SSH.

```sh
cd /opt/stacks/grocy
restore_root="$(mktemp -d /var/tmp/grocy-restore.XXXXXX)"
chown 1000:1000 "$restore_root"
chmod 0750 "$restore_root"
install -d -o 1000 -g 1000 -m 0750 "$restore_root/config"
backup_source=/mnt/omv/docker-host-backups/manual/REPLACE_WITH_RECORDED_ID/grocy
test -s "$backup_source/data/grocy.db"
rsync -aH "$backup_source/" "$restore_root/config/"
image="$(docker compose config --images | sed -n '1p')"
docker run -d --name grocy-restore-smoke --restart=no \
  -p 127.0.0.1:19283:80 \
  -v "$restore_root/config:/config" \
  -e PUID=1000 -e PGID=1000 -e TZ=Europe/London \
  "$image"
```

Expected result: `curl -I http://127.0.0.1:19283/` returns the login redirect.
Use an SSH tunnel to `127.0.0.1:19283`, sign in, and confirm the seeded
locations and a representative product/stock record. Production remains on
`9283` and must not be modified by the drill.

Run on: docker-host over SSH after the isolated application check passes.

```sh
config_root="$(docker inspect grocy-restore-smoke \
  --format '{{range .Mounts}}{{if eq .Destination "/config"}}{{.Source}}{{end}}{{end}}')"
restore_root="$(dirname -- "$config_root")"
case "$restore_root" in
  /var/tmp/grocy-restore.*) ;;
  *) printf 'refusing unsafe cleanup path: %s\n' "$restore_root" >&2; exit 1 ;;
esac
docker rm -f grocy-restore-smoke
rm -rf -- "$restore_root"
```

Expected result: only the disposable container and verified temporary path are
removed. Recheck production on `9283`.

## Updates

Keep the image pinned. Before changing it, create a Grocy database checkpoint,
run the off-host backup, record the current digest, and read both Grocy and
LinuxServer release notes. Re-run login, pilot operations on disposable data,
HA read/write boundary checks, Household Hub read-only checks, and the isolated
restore drill. Automatic updates are not approved.

Rollback uses the previous image digest plus the matching pre-update `config`
checkpoint. Do not run an old container against a database already migrated by
an incompatible newer release.

## Failure recovery

| Failure | Safe response | Proof before continuing |
|---|---|---|
| Default password still works | Keep access source-scoped and add no real stock. | Default login fails and the stored admin credential works. |
| Pilot produces the wrong quantity | Stop adding transactions; inspect Stock journal and undo only the disposable entries. | Expected quantity and journal history agree. |
| Pilot cannot be removed cleanly | Preserve evidence and restore the named pre-pilot checkpoint in a controlled window. | Seeded model remains and pilot data is absent. |
| Backup target is local | Stop the backup and repair the OMV mount. | `findmnt` shows the remote source. |
| Isolated restore fails | Preserve production and the failed copy; inspect logs and database/image compatibility. | Representative data opens in isolation. |
| Upgrade fails | Restore the previous digest and matching checkpoint. | UI, API consumers, stock and expiry checks pass. |

## Home Assistant voice access

Home Assistant exposes Grocy to Assist through the repo custom integration
`configs/home-assistant/custom_components/grocy_llm/`. The integration registers
LLM tools for two low-risk shopping-list actions only:

- add an item to the Grocy shopping list
- list unchecked Grocy shopping-list items

Do not use voice tools for purchase, consume, stock correction, inventory
counts, product deletion, or marking items completed until a confirmation-gated
workflow exists.

Live state on 2026-07-07:

- HA `/config/configuration.yaml` includes `grocy_llm` and adds
  `grocy_household` to the local LLM exposed API list.
- HA `/config/secrets.yaml` contains `grocy_api_key`.
- The dedicated Grocy key is named `home-assistant-voice`; a live copy is on
  docker-host at `/root/grocy-home-assistant-voice-api-key.txt` with root-only
  permissions. Store the value in Bitwarden as part of the hardening pass.
- docker-host firewall allows HA `192.168.20.101` and the HA Supervisor network
  `172.30.32.0/23` to reach Grocy `9283/tcp`.
- HA config check passed, HA restarted cleanly, and logs showed no Grocy custom
  component errors.
- HA-to-Grocy API proof succeeded by creating a temporary product, adding it to
  the shopping list, deleting the temporary product, and confirming the shopping
  list was empty afterward.

Manual Assist phrases to test:

- "Add bananas to the shopping list."
- "What's on the Grocy shopping list?"

## Household Hub read-only access

Household Hub joins `grocy_default` and uses its own API-key identity named
`household-hub-read-only`. The key is stored only on docker-host in the Hub
environment and `/root/household-hub-grocy-api-key.txt`; it is not the Home
Assistant voice key and is not tracked in Git.

`GET /api/integrations/grocy/overview` reads locations, stock/expiry and
unchecked shopping-list items. The Hub client exposes only GET requests and no
mutation route. Grocy API keys are not endpoint-scoped, so this application
boundary and independent revocation are the effective safeguards.

Before creating the key, the live database was checkpointed at
`/opt/stacks/grocy/config/data/grocy.db.pre-household-hub-20260809`. The first
live overview on 2026-08-09 returned all five seeded locations; stock and the
shopping list were both empty. NAS app-data run `20260809T130054Z` then captured
the updated Grocy configuration and key state.

## Completion checklist

- [x] UI responds.
- [x] Core household locations, quantity units, and product groups configured.
- [ ] Default administrator password is rejected and the replacement is stored.
- [ ] Pilot product purchase/consume/correction and expiry workflow tested.
- [x] `/opt/stacks/grocy/config` backup path verified.
- [x] Backup copied to a temporary path and database presence checked; repeat
  the application-level isolated restore after material changes.
- [x] HA Assist backend/API path proved for add/list shopping-list actions.
- [ ] Representative data opens in the loopback-only isolated restore target.
- [ ] Update and matching-data rollback evidence recorded.
