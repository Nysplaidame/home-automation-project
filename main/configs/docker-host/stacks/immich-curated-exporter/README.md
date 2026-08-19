# Immich curated exporter

This host-side Python job copies assets from explicitly allow-listed Immich
albums into Jellyfin's `immich-curated` library. It is not a sync engine:
Immich remains the photo system of record, no upload/library path is mounted
into Jellyfin, and album removals create review-queue entries rather than
deleting published files.

## Contract

- The API key is local-only in `/etc/immich-curated-exporter.env` (mode `0600`)
  and needs only `album.read`, `asset.read`, and `asset.download` permissions.
- `albums.json` is an explicit UUID-to-collection allow-list. A collection name
  may not contain path traversal characters, and IDs/names must be unique.
- The destination must resolve to an NFS/NFS4 mount. This blocks a missing-OMV
  mount from becoming a local VM fallback.
- Each download streams to a same-directory `.part` file, fsyncs, and is
  atomically promoted. The manifest records the Immich checksum, SHA-256,
  version time, size, and target path.
- The exporter refuses albums larger than its configured per-run limit and
  rejects individual assets above the configured byte limit.
- `state/manifest.json` and `state/review-queue.json` must be included in the
  existing docker-host app-data backup job.

## Deployment

Copy this directory to `/opt/stacks/immich-curated-exporter`, preserving the
executable bit on `exporter.py`. Grant the existing `media-service` identity
write access only to `/mnt/omv/media/jellyfin/immich-curated`; Jellyfin retains
its existing read-only bind mount.

Create the real allow-list and secret environment file outside Git:

```sh
install -d -o media-service -g "$(id -gn media-service)" -m 0750 /opt/stacks/immich-curated-exporter/state
install -m 0640 -o media-service -g "$(id -gn media-service)" albums.json.example /opt/stacks/immich-curated-exporter/albums.json
install -m 0600 /dev/null /etc/immich-curated-exporter.env
nano /etc/immich-curated-exporter.env
```

Before enabling the timer, run a dry run and then one bounded live test album:

```sh
sudo -u media-service /usr/bin/python3 exporter.py --dry-run
sudo systemctl daemon-reload
sudo systemctl start immich-curated-exporter.service
sudo systemctl status immich-curated-exporter.service --no-pager
sudo cat state/manifest.json
sudo cat state/review-queue.json
```

Check that the output exists under the selected collection, that Jellyfin sees
it through its read-only mount, and that removing an asset from the test album
adds a review item without deleting the copy. Only then enable the timer:

```sh
sudo systemctl enable --now immich-curated-exporter.timer
systemctl list-timers immich-curated-exporter.timer
```

Do not create the API key, set album IDs, or start this job until the operator
has selected the curated albums and has a restore path for the state directory.
