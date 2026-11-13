---
title: Immich Curated Exporter Runbook
description: Non-destructive allow-listed Immich album export into Jellyfin
tags: [install, docker-host, immich, jellyfin, media]
created: 2026-08-10
type: install-guide
status: staged
---

# Immich Curated Exporter Runbook

## Purpose

Publish specifically approved Immich albums to Jellyfin without granting
Jellyfin access to Immich's live upload/library tree. This is a one-way copy:
Immich remains the photo system of record.

## Safety contract

- An Immich user-scoped API key has only `album.read`, `asset.read`, and
  `asset.download` permissions. Store it only in
  `/etc/immich-curated-exporter.env` with mode `0600`.
- `albums.json` maps explicit album UUIDs to safe, named Jellyfin collections.
  Album discovery, wildcard selection, and arbitrary filesystem paths are not
  supported.
- The output root must be backed by the OMV NFS export. The job fails before
  writing if it detects a local filesystem fallback.
- Downloads use a same-directory temporary file and atomic rename. The state
  manifest stores source checksum/version, SHA-256, byte count, and target.
- Removing an asset from Immich or an allowed album never deletes the published
  Jellyfin copy. It creates a review-queue entry instead.

## Source and target paths

| Purpose | Path |
|---|---|
| Tracked deployment source | `configs/docker-host/stacks/immich-curated-exporter/` |
| Live job source | `/opt/stacks/immich-curated-exporter/` |
| Local secret environment | `/etc/immich-curated-exporter.env` |
| Exported Jellyfin media | `/mnt/omv/media/jellyfin/immich-curated/` |
| State to back up | `/opt/stacks/immich-curated-exporter/state/` |

## First deployment

1. Confirm the existing `media-service` identity can write only the curated
   export directory and Jellyfin still has its existing read-only mount.
2. Copy the source directory to docker-host, copy `albums.json.example` to
   `albums.json`, and replace the example album UUID only after the household
   has selected a test album.
3. Create a scoped Immich API key and enter it in the local environment file;
   do not put it in Git, Home Assistant, Homepage, or a browser URL.
4. Run `exporter.py --dry-run`, then start the one-shot service for a single
   bounded test album.
5. Verify the manifest, output file, Jellyfin scan, and app-data backup.
6. Remove one test asset from the allowed album. Run the service again and
   confirm a review item is added while the published copy remains.
7. Enable the six-hour timer only after those acceptance checks pass.

## Validation commands

Run on: docker-host over SSH.

```sh
findmnt -n -o SOURCE,FSTYPE,TARGET --target /mnt/omv/media/jellyfin/immich-curated
sudo -u media-service /usr/bin/python3 /opt/stacks/immich-curated-exporter/exporter.py --dry-run
sudo systemctl start immich-curated-exporter.service
sudo systemctl status immich-curated-exporter.service --no-pager
sudo jq . /opt/stacks/immich-curated-exporter/state/manifest.json
sudo jq . /opt/stacks/immich-curated-exporter/state/review-queue.json
```

Keep the timer disabled until the bounded test, no-delete check and protected
checkpoint above have passed. Only then enable recurrence from docker-host:

Run on: docker-host over SSH, after acceptance.

```sh
sudo systemctl enable --now immich-curated-exporter.timer
```

## Recovery

Disable the timer before correcting an allow-list or API-key problem. Existing
published files are safe to leave in place; use the review queue and a
documented approval to decide whether any should be removed. Restore the state
directory from the docker-host app-data backup before recreating its history.

## Consistent checkpoint and isolated restore

Disable the timer and wait for the running one-shot job to finish before taking
a matched copy of `state/`, `albums.json`, exporter source, unit/timer files and
protected `/etc/immich-curated-exporter.env`. Preserve ownership, source revision
and manifest schema version. The app-data job copies state only when present;
it does not cover the secret/allow-list or exported media itself. Back up the
published media separately if its retention requires an independent copy.

Restore copied state/config in a disposable VM with no production credentials,
no active timer and a disposable mount-backed export root. Verify manifest and
review-queue JSON/schema and sample recorded hashes against copied exported
files. Do not rewrite restored history merely to make validation pass. For an
API exercise use a separate test Immich and scoped test key; `--dry-run` still
needs an API source and is not a promise of offline execution.

Prove a bounded test export, then remove a test asset from the test album and
confirm only a review item is created while its published copy remains. Do not
use production assets for this destructive-input test. Record checkpoint,
source/schema and outcomes before stopping the isolated job.

## Update and rollback

Review source/manifest compatibility and rehearse on copies before changing the
installed script. Preserve the prior source, allow-list and matched state while
the timer is disabled. After update, dry-run and inspect exactly the selected
albums before a bounded execution and timer re-enable. On failure stop the job,
preserve failed state and restore the previous generation; reconcile any files
already exported against hashes before retrying. Rollback must not delete the
published library or erase pending review items. Use the
[backup diagram](../../diagrams/storage/storage-and-backup-flow.mermaid).
