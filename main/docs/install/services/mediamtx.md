---
title: MediaMTX Phone Stream Relay
description: Authenticated Android RTSP relay and direct NAS recording on docker-host
tags: [install, docker-host, mediamtx, rtsp, garage, recording]
created: 2026-08-27
modified: 2026-09-14
type: install-guide
status: live
---

# MediaMTX Phone Stream Relay

Diagrams: [service placement](../../diagrams/infrastructure/docker-host-service-placement.mermaid),
[access](../../diagrams/network/security-access-flow.mermaid) and
[recording storage](../../diagrams/storage/storage-and-backup-flow.mermaid).

The live observations below are dated deployment evidence. This September10
manual expansion adds operating procedures, not a fresh streaming/restore test.

## Live design

- Android/Larix publishes an already-compressed camera stream over HomeAdmin
  Wi-Fi to `192.168.20.102:8554`.
- MediaMTX relays the packets without transcoding and records fMP4 directly to
  `/mnt/omv/media/phone-recordings/garage-phone/` on OMV.
- The garage Pi reads the same RTSP path and performs playback decode. MediaMTX
  does not decode the stream.
- Only RTSP-over-TCP is enabled. RTMP, HLS, WebRTC, SRT, MoQ, API, metrics,
  profiling and playback HTTP are disabled.

## Access and credentials

The firewall permits `8554/tcp` only from HomeAdmin/Management
`192.168.10.0/24`; IPv6 and every other IPv4 source are dropped. MediaMTX also
requires distinct path-scoped accounts:

- `garage-publisher`: publish-only access to `garage-phone`.
- `garage-viewer`: read-only access to `garage-phone`.

Passwords exist only in `/opt/stacks/mediamtx/.env` on VM 103, mode `0600`.
Retrieve them on docker-host when configuring a client; never copy the populated
file into this repository.

Publisher URL:

```text
rtsp://garage-publisher:<publisher-password>@192.168.20.102:8554/garage-phone
```

Viewer URL:

```text
rtsp://garage-viewer:<viewer-password>@192.168.20.102:8554/garage-phone
```

## Larix starting profile

Use the rear main camera, H.264, `1920x1080`, fixed `30 fps`, `8 Mbit/s`, a
one-second keyframe interval, audio off, local recording off and overlays off.
Confirm a stable 1080p session before trying H.265 or 4K. For the old Larix
build, add the publisher URL as an RTSP connection and start/stop the stream in
the app.

## Stack and storage

Tracked source is under `configs/docker-host/stacks/mediamtx/`; live source is
`/opt/stacks/mediamtx/`. The container runs as `1007:100` (`media-service`),
uses read-only root filesystem/no capabilities/no-new-privileges, and is capped
at one CPU and 256 MiB RAM. Its explicit bridge is `10.240.16.0/24`.

Recordings use one-second fMP4 parts and 30-minute segments. Automatic deletion
is disabled (`recordDeleteAfter: 0s`), so choose and document a retention policy
before unattended or frequent recording.

## Validation

Run on: docker-host shell.

```sh
cd /opt/stacks/mediamtx
docker compose config --quiet
docker compose ps
docker logs --tail 50 mediamtx
docker stats --no-stream mediamtx
find /mnt/omv/media/phone-recordings/garage-phone -type f -name '*.mp4' -printf '%TY-%Tm-%Td %TH:%TM %s %p\n'
iptables -S DOCKER-USER | grep -- '--ctorigdstport 8554'
```

Expected behavior is that an unauthenticated reader/publisher fails, the
publisher creates a stream at `garage-phone`, the viewer decodes it, and the
completed segment is owned by `media-service:users` on the NAS.

## Rollback

Run on: docker-host shell during the selected service maintenance window.

```sh
cd /opt/stacks/mediamtx
docker compose down
```

Remove the UFW `8554/tcp` rule and the tracked MediaMTX block from
`docker-host-firewall.sh` only if retiring the service. Do not delete the NAS
recordings as part of service rollback.

## Fresh installation and last safe stop

Copy the tracked `docker-compose.yml` and `mediamtx.yml` from
`configs/docker-host/stacks/mediamtx/` into `/opt/stacks/mediamtx/`. Supply
`MEDIAMTX_PUBLISH_PASSWORD` and `MEDIAMTX_VIEW_PASSWORD` in the protected `.env`;
retain their recovery record outside Git. Verify the media-service UID/GID
against OMV before adopting the recorded `1007:100` runtime identity.

Run on: docker-host shell before starting the service.

```sh
cd /opt/stacks/mediamtx || exit 1
findmnt -T /mnt/omv/media
test -d /mnt/omv/media/phone-recordings
docker compose config --quiet
docker compose config --images
```

Expected: the intended OMV NFS source backs the path, the recording directory
exists there and Compose resolves to the reviewed image digest. A local root
filesystem returned by `findmnt -T` is a failure. Keep the candidate down until
mount permissions, scoped port8554 policy and the retention decision are ready.
Do not create the recording directory on a missing mount as a workaround.

Run on: docker-host shell after those prerequisites pass.

```sh
docker compose up -d
docker compose ps
```

Expected: MediaMTX remains running. Follow the authenticated publish/read and
recording checks above from the approved client network. A listener alone does
not establish stream or recording acceptance. Keep client URLs containing
passwords out of shell history, screenshots and logs shared with others.

## Backup and isolated restore

MediaMTX now has a separate daily protected configuration job, described below.
It is independent of the central app-data job and does not back up recordings.
The owner selected no automatic recording deletion, with manual review.

Before an update, stop the publisher and allow its current recording segment
to finish; then stop the relay. Preserve the matched image digest, non-secret
configuration, protected credential record and completed recordings required by
the owner's retention policy. Do not delete recording files during rollback.

For isolated proof, use a distinct container/network name, unused loopback
RTSP port, test-only accounts and a copied/disposable recording directory.
Do not mount production recordings writable or reuse real publisher URLs.
Publish one disposable clip, read it through the test viewer and validate a
completed recorded segment. Record the backup/config generation, image, tested
paths and outcome before removing only the test resources.

## Manual protected configuration checkpoint

This procedure prepares a recovery artifact; it does not enable a recurring
backup or choose recording deletion. Run before a reviewed update after stopping
the publisher and relay as described above. Keep the checkpoint root-only:
`.env` contains both stream passwords. Do not place the plaintext archive in a
shared media directory or the repository.

Run on: docker-host shell as root, with the service stopped.

```sh
set -eu
cd /opt/stacks/mediamtx
test -f docker-compose.yml && test -f mediamtx.yml && test -f .env
umask 077
checkpoint_dir=$(mktemp -d /root/mediamtx-checkpoint.XXXXXX)
docker compose config --quiet
docker compose config --images > "$checkpoint_dir/images.txt"
docker inspect mediamtx --format '{{.Image}}' > "$checkpoint_dir/running-image-id.txt"
tar -C /opt/stacks/mediamtx -czf "$checkpoint_dir/mediamtx-config.tar.gz" \
  docker-compose.yml mediamtx.yml .env
(cd "$checkpoint_dir" && sha256sum mediamtx-config.tar.gz > SHA256SUMS)
tar -tzf "$checkpoint_dir/mediamtx-config.tar.gz"
printf 'Protected checkpoint: %s\n' "$checkpoint_dir"
```

Expected: Compose validates, the recorded image is understood, and the archive
lists exactly the three configuration files without printing their contents.
This assumes the existing stopped container is retained for `docker inspect`;
if it has already been removed, recover the previous runtime image evidence
before claiming a matched checkpoint. Keep the previous image available or
retain an approved image archive; a digest is not an offline copy of an image.

Transfer the checkpoint through the approved encrypted backup workflow to
storage outside VM103, with access limited to credential custodians. Record its
actual destination and restore access; a root-only file inside VM103 alone is
not an off-host backup. No encrypted destination or recurring configuration
capture is established by this manual revision.

On an isolated recovery VM, verify `sha256sum -c SHA256SUMS` in the copied
checkpoint directory. Inspect the archive member list before extracting into a
new protected directory; never extract over the live stack. Preserve the real
credentials as recovery material, but replace them with test-only values in the
separate test Compose environment before the rehearsal above. Record the
checkpoint date, source digest, successful extraction and stream/record proof.

## Recording capacity and retention decision

The tracked `recordDeleteAfter: 0s` retains recordings indefinitely. Before
unattended recording, record an owner-selected maximum age or capacity budget,
which clips need independent backup, and the response when space is low.
Automatic deletion is a separate reviewed change; do not enable it implicitly
while adding configuration backup.

At the suggested 8 Mbit/s profile, video alone is approximately 3.6 GB per hour
(86.4 GB per day) before container overhead. Use measured completed-segment
sizes and actual recording hours to refine this estimate. Check OMV free space
and the recording directory size; a healthy relay process cannot prove storage
headroom. If the budget is exhausted, stop publishing and review retained clips
before any deliberate deletion. NAS residence does not provide an independent
copy of recordings.

## Updates and diagnosis

Review the pinned image through the [version policy](../reference/version-policy.md).
Save the checkpoint above, update only the relay, validate Compose and repeat
publish/read/recording plus intended-denial tests. If the candidate fails,
restore the old image and matching config, leaving existing recordings intact.

| Symptom | Next check | Recovery boundary |
|---|---|---|
| No connection | Approved HomeAdmin source, listener8554, host policy and client TCP setting | Do not enable extra protocols or broaden network access |
| Authentication denied | Correct publish/read role, exact `garage-phone` path and protected credential | Do not grant a viewer publishing rights to bypass the error |
| Stream plays but no recording | Exact OMV mount, media UID/GID, free space and relay logs | Stop publishing before mount repair; never accept local fallback writes |
| Disk usage grows | Completed segments and retention decision | `recordDeleteAfter: 0s` disables deletion; no unreviewed purge |
| High client load or poor video | Source profile, Wi-Fi and viewer decode resources | The relay is not a transcoder; do not diagnose it as one |

## September 12 scheduled configuration backup and retention decision

Owner decision: keep `recordDeleteAfter: 0s`; review recordings manually.
Before recording, check free space and intended duration. Review accumulated
clips weekly and after long sessions; stop publishing if capacity is insufficient.
No automatic deletion was enabled and no recording files were removed.

The [backup script](../../../configs/docker-host/system/mediamtx-config-backup.sh),
[service](../../../configs/docker-host/system/mediamtx-config-backup.service) and
[timer](../../../configs/docker-host/system/mediamtx-config-backup.timer) are
installed on VM103. The timer is enabled at03:35 host time (Europe/London), with
persistent catch-up. The script refuses a missing/wrong OMV NFS source and archives
only `.env`, Compose and `mediamtx.yml`, plus an image ID and checksum manifest.
It excludes recordings. Checkpoint directories are owner-only and files are
explicitly mode0600 because NAS default ACLs can affect creation modes.

Destination: `/mnt/omv/docker-host-backups/mediamtx-config/<UTC timestamp>/`.
The first checkpoint was `20260912T191716Z`; hashes passed, extraction to a new
root-only directory succeeded, and all three restored files matched live copies.
The September14 scheduled run completed successfully; the next run was listed
for September15 at03:35 BST. This proves configuration recovery, not stream or
recording-content restore. NAS access controls protect the secret-bearing archive;
it is not an encrypted/off-site backup. Small config checkpoints also remain
until manual review; this script performs no pruning.

For rebuild, stage the three tracked files, install the script mode0755 under
`/usr/local/sbin/` and units mode0644 under `/etc/systemd/system/`, validate units,
reload systemd, run the service once and inspect its checksum/private permissions
before enabling the timer. Confirm the expected export in the script matches
Phase06's actual storage identity. To disable recurrence, disable/stop only
`mediamtx-config-backup.timer`; it does not stop the relay or delete checkpoints.

Offline mount-boundary regression tests are in
[the test file](../../../configs/docker-host/system/tests/test_mediamtx_config_backup.py);
both missing-mount and wrong-export cases passed without reaching Docker or
writing a checkpoint. Run with Python3 on Linux.
