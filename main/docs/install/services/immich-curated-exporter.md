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

Run on docker-host:

```sh
findmnt -n -o SOURCE,FSTYPE,TARGET --target /mnt/omv/media/jellyfin/immich-curated
sudo -u media-service /usr/bin/python3 /opt/stacks/immich-curated-exporter/exporter.py --dry-run
sudo systemctl start immich-curated-exporter.service
sudo systemctl status immich-curated-exporter.service --no-pager
sudo jq . /opt/stacks/immich-curated-exporter/state/manifest.json
sudo jq . /opt/stacks/immich-curated-exporter/state/review-queue.json
sudo systemctl enable --now immich-curated-exporter.timer
```

## Recovery

Disable the timer before correcting an allow-list or API-key problem. Existing
published files are safe to leave in place; use the review queue and a
documented approval to decide whether any should be removed. Restore the state
directory from the docker-host app-data backup before recreating its history.
