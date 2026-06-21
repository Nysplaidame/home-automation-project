---
title: Obsidian Self-hosted LiveSync
description: Central multi-device synchronization for the project documentation vault
tags: [install, docker-host, obsidian, couchdb, tailscale]
created: 2026-06-21
modified: 2026-06-21
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

## Client rollout

1. Back up both existing vault copies and ensure all Git changes are committed.
2. Install the Self-hosted LiveSync plugin on the authoritative device first.
3. Use its setup wizard with the HTTPS endpoint, database and credentials.
4. Enable end-to-end encryption and store its passphrase in Bitwarden.
5. Exclude `.git/`, `.obsidian/workspace*.json`, and device-specific cache files.
6. Let the authoritative device upload fully before connecting device two.
7. On device two, start from a fresh/backup vault and use the generated setup URI.
8. Keep normal Git commits and pushes as deliberate project checkpoints; do not
   run automatic Git pull/reset operations against an actively synced vault.

Back up `/opt/stacks/obsidian-livesync/data`. CouchDB synchronization is not a
substitute for Git history or an offline backup.
