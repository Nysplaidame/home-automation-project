---
title: MediaMTX Phone Stream Relay
description: Authenticated Android RTSP relay and direct NAS recording on docker-host
tags: [install, docker-host, mediamtx, rtsp, garage, recording]
created: 2026-08-27
modified: 2026-08-27
type: install-guide
status: live
---

# MediaMTX Phone Stream Relay

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

Run on docker-host:

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

```sh
cd /opt/stacks/mediamtx
docker compose down
```

Remove the UFW `8554/tcp` rule and the tracked MediaMTX block from
`docker-host-firewall.sh` only if retiring the service. Do not delete the NAS
recordings as part of service rollback.
