---
title: Obsidian Self-hosted LiveSync
description: Central multi-device synchronization for the project documentation vault
tags: [install, docker-host, obsidian, couchdb, tailscale]
created: 2026-06-21
modified: 2026-07-06
type: install-guide
status: live-client-setup-pending
---

# Obsidian Self-hosted LiveSync

## Architecture

Obsidian remains a local application on each device. CouchDB on docker-host is
the central synchronization backend for the Self-hosted LiveSync community
plugin. Git remains the durable version history and GitHub backup; LiveSync
removes the need to pull before reading or editing on another device.

The backend is `obsidian-sync.home.local:5984` internally. Mobile clients must
use the Tailscale HTTPS endpoint
`https://docker-host.tail7012a0.ts.net:8443`. Tailscale Serve is enabled and the
authenticated endpoint has been validated. The database is
`home-automation-project`.

Credentials are stored only in `/opt/stacks/obsidian-livesync/.env` and must be
copied to Bitwarden under `obsidian-livesync`. The future LiveSync E2EE
passphrase and setup-URI passphrase are separate secrets and also belong there.

Current live check on 2026-07-07:

- Container `obsidian-livesync` was up on docker-host.
- `curl -I http://127.0.0.1:5984/` returned `HTTP/1.1 401 Unauthorized`, which
  confirms CouchDB is reachable and requires auth.
- Authenticated CouchDB root check returned CouchDB `3.5.0`.
- Database `home-automation-project` exists and is empty before the first
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

## Client rollout

1. Back up both existing vault copies and ensure all Git changes are committed.
2. Open the Self-hosted LiveSync plugin on the authoritative device first.
   The plugin is already installed in this local root vault.
3. Use its setup wizard with the HTTPS endpoint, database and credentials.
4. Enable end-to-end encryption and store its passphrase in Bitwarden.
5. Exclude `.git/`, `.obsidian/workspace*.json`, and device-specific cache files.
6. Let the authoritative device upload fully before connecting device two.
7. On device two, start from a fresh/backup vault and use the generated setup URI.
8. Keep normal Git commits and pushes as deliberate project checkpoints; do not
   run automatic Git pull/reset operations against an actively synced vault.

Detailed rollout notes:

- Treat `E:\home-automation-project` as the authoritative Windows vault until
  the operator deliberately chooses another primary device.
- Before enabling LiveSync, close Obsidian on the second device or put it in a
  backup-only state so it cannot race the first upload.
- Exclude transient workspace/cache files before first sync. Git remains the
  deliberate history layer; LiveSync is for freshness, not rollback.
- After the authoritative upload completes, create the setup URI from that
  device and store the setup-URI passphrase in Bitwarden item
  `obsidian-livesync`.
- Connect the second device using the generated setup URI, wait for a full sync,
  then create one harmless test note and verify it appears on both devices.
- Delete the test note only after both devices have seen it, then make a normal
  Git commit for any durable project-doc changes.

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

Restore smoke:

```sh
cd /opt/stacks/obsidian-livesync
docker compose stop obsidian-livesync
# restore /opt/stacks/obsidian-livesync/data from the selected backup
docker compose up -d
curl -I http://127.0.0.1:5984/
```

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
- [x] Restore smoke tested to a temporary path or controlled service stop.
