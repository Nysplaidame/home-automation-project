---
title: Media Library Service Operations
description: Shared installation, diagnosis, backup, update and recovery contract for Jellyfin, Calibre-Web and Atsumeru
tags: [install, media, recovery, jellyfin, calibre-web, atsumeru]
created: 2026-09-10
modified: 2026-09-10
type: install-guide
status: active
---

# Media Library Service Operations

This is the shared operating manual for the three media services on VM 103.
The adjacent stack READMEs record service-specific history; the Compose files
define exact images and mounts. This manual is reconciled with tracked source,
not a newly executed installation or restore proof.

Diagrams: [service placement](../../diagrams/infrastructure/docker-host-service-placement.mermaid),
[storage and backups](../../diagrams/storage/storage-and-backup-flow.mermaid),
[access policy](../../diagrams/network/security-access-flow.mermaid).

## Service and data contract

| Service | Source | Host listener | Persistent application data | OMV library and permission |
|---|---|---|---|---|
| Jellyfin | [Compose](../../../configs/docker-host/stacks/jellyfin/docker-compose.yml) | 8096 | `/opt/stacks/jellyfin/config` | `jellyfin/films`, `series`, `music`, `immich-curated`, each read-only under `/mnt/omv/media` |
| Calibre-Web | [Compose](../../../configs/docker-host/stacks/calibre-web/docker-compose.yml) | 8083 | `/opt/stacks/calibre-web/config` | `/mnt/omv/media/books/calibre-library` writable, exposed as `/books` |
| Atsumeru | [Compose](../../../configs/docker-host/stacks/atsumeru/docker-compose.yml) | 31337 | `/opt/stacks/atsumeru/config` and `database` | `/mnt/omv/media/comics/atsumeru-library` writable, exposed as `/library` |

The recorded media identity is UID `1007`, GID `100`; verify the actual OMV
identity before a new installation. Do not create a new user with those numbers
without checking existing ownership. Jellyfin has no GPU device mapping;
hardware transcoding remains a separate shared-iGPU capacity decision.
Atsumeru is primarily an authenticated API/client backend, so a missing
full-featured browser library manager is not itself a service failure.

## Installation and last safe stop

1. Complete [docker-host](../phases/05-docker-host.md) and
   [OMV](../phases/06-omv-nas.md). Confirm OMV is on router LAN4/VLAN40 and
   that docker-host's media mount is the intended NFS export.
2. Copy the selected tracked stack directory to its matching
   `/opt/stacks/` directory using the established authenticated transfer path.
   On a rebuild, preserve any recovered data before creating directories.
3. Prepare `.env` from that stack's `.env.example`; retain it outside Git.
   Set the verified `MEDIA_UID`/`MEDIA_GID` and Jellyfin's published URL where
   required. Keep application credentials in the password manager.
4. Create only the stack-local directories declared in its Compose file,
   with ownership appropriate to that runtime identity. Confirm that each
   library subdirectory already exists on the verified OMV mount. Do not
   create substitute local library directories beneath a missing NFS mount.
5. Review the pinned image/digest against the
   [version policy](../reference/version-policy.md) before pulling. Use the
   [maintenance window](../../procedures/update_maintenance_playbook.md) for
   temporary image-pull access.

Run on: docker-host Bash shell. Select exactly one of the three service names.

```bash
media_service=jellyfin
case "$media_service" in
  jellyfin|calibre-web|atsumeru) ;;
  *) echo 'Unknown media service'; exit 1 ;;
esac
cd "/opt/stacks/$media_service" || exit 1
findmnt -T /mnt/omv/media
test -f .env && docker compose config --quiet
docker compose config --images
```

Expected: the filesystem is NFS from the documented OMV media export, `.env`
exists, config validation exits zero, and the image is the reviewed digest.
`findmnt -T` may return the local root filesystem when NFS is absent; that is
a failure, even if the command exits zero. Inspect the result explicitly.

**Last safe stop:** leave the service stopped until mount identity, image,
ownership, source-scoped port rules, data backup and rollback plan are ready.
Do not publish it to a new source network as part of a rebuild.

Run on: docker-host shell, in the selected stack directory after those checks.

```sh
docker compose up -d
docker compose ps
docker compose logs --tail=60
```

Expected: selected service is running without a permission or restart loop.
Configure Jellyfin libraries only at its four `/media/` paths; point
Calibre-Web at its actual Calibre library under `/books`; configure Atsumeru's
client/library against `/library`. Replace bootstrap credentials before
household access. Use one known disposable media item for a browse/read test;
for writable book/comic workflows, check an isolated test library before
changing real library metadata.

## Diagnosis and acceptance

Run on: docker-host shell.

```sh
curl -I http://127.0.0.1:8096/
curl -I http://127.0.0.1:8083/
curl -I http://127.0.0.1:31337/
```

Expected: the configured service responds; redirects or an authentication
challenge can establish reachability but not successful login or media access.
Complete a client login and open a known library item separately. Test only
services selected for the current rebuild; an intentionally absent service
cannot pass or fail household acceptance.

| Symptom | Next check | Recovery boundary |
|---|---|---|
| All libraries disappear | `findmnt -T /mnt/omv/media`, OMV LAN4 connectivity, then NFS | Stop library writers before repairing a missing mount; verify the exact remote source before resuming |
| Service starts but library is empty | Container mount destination, configured library path, read permission and scan logs | Do not mount the entire media export or Immich live library to find files |
| Calibre-Web cannot open its library | `/books` content, Calibre metadata database, UID/GID and logs | Do not initialize over an existing library or recursively change all NAS ownership |
| Atsumeru URL responds but browsing fails | Authenticated client login, configured library and scanner logs | HTTP alone does not prove its API/client workflow |
| Local URL works but Homepage fails | Fixed proxy upstream/port, TLS and source grant | Use the [Homepage walkthrough](../../troubleshooting/diagnostic-walkthroughs.md#1-homepage-unavailable-or-one-card-fails) |
| High Jellyfin CPU or playback errors | Client codec/direct-play behavior, media and service logs | No unreviewed iGPU mapping; preserve Frigate/local-AI capacity |

## Backup: application state and library content are separate

The [app-data backup source](../../../configs/docker-host/system/docker-host-app-data-backup.sh)
copies Jellyfin config, Calibre-Web config, and Atsumeru config/database.
It does not back up the entire media libraries. Its ordinary directory copies
are not an application-level isolated restore proof, nor do they establish a
consistent checkpoint of a database being written during copying.

Before an update, take a clean checkpoint with the selected service stopped.
Also pause any other process that can write the selected library. Record the
image digest, Compose source and generation/time. Use the verified off-host
backup destination from the [backup strategy](../../../scripts/backup/backup_strategy.md).

Run on: docker-host shell, in the selected media stack, during its maintenance window.

```sh
docker compose stop
docker compose ps --all
```

Expected: the selected service is stopped. Copy its persistent application
directories from the table above, Compose file and protected `.env` to a
new dated backup generation. Preserve ownership and permissions. For
Calibre-Web, include a matching library/metadata checkpoint; for Atsumeru,
include library content needed by its restored index. For Jellyfin, retain the
library originals and the same mount paths alongside configuration. Confirm
the backup is off-host and nonempty before restarting the unchanged service.
Do not put protected `.env` contents or user data into the vault.

Run on: docker-host shell, after the checkpoint and mount revalidation.

```sh
docker compose start
docker compose ps
```

Expected: the original service returns and the original login/read check passes.
Cache directories can be rebuilt; do not confuse them with persistent config,
book metadata or Atsumeru's database. Record whether library originals have
independent backups or are intentionally recoverable from another source.

## Update and rollback

1. Read the selected version's official migration notes using the version
   policy; record a new immutable image reference and any data-format changes.
2. Complete the stopped checkpoint above and retain the previous Compose/image.
3. Change only the selected stack's image, validate Compose, then pull and
   recreate during its maintenance window. Repeat login, library read,
   intended-write, proxy and monitoring checks.
4. If startup or user checks fail, stop the candidate. Restore the previous
   image **with its matching pre-update application and library metadata**.
   Do not run an older image against a newly migrated database.
5. Revalidate the original checks before ending the incident. Record any
   post-checkpoint user writes that cannot safely be merged back.

## Isolated restore proof

Restore into a separate temporary guest or a deliberately isolated test stack.
The production Compose files have fixed container names and ports; copying
them unchanged and supplying only another project name is not isolation.

- Use unique container/network names and loopback-only unused ports.
- Mount copied application data and copied sample libraries. Do not attach
  writable production libraries or production application directories.
- Retain expected internal paths (`/books`, `/library`, `/media/...`) so the
  restored application can interpret its saved configuration.
- Use the matching saved image digest, then verify login, a representative
  media read, and test metadata writes only in the copied writable library.
- Confirm the production stack/data were unchanged. Record backup generation,
  image, checks, elapsed recovery time and cleanup target before removing the
  isolated test resources.

A successful historical restart is not this restore proof. Keep service-level
restore acceptance open until the isolated result is recorded in the current
handoff and the [documentation checklist](../INSTALL-TO-DO.md).
