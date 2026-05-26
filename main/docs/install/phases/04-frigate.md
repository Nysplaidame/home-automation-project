---
title: Phase 04 - Frigate
description: Frigate Debian VM, Docker, placeholders, camera paths, and HA integration
tags: [install, frigate, nvr]
created: 2026-05-24
modified: 2026-05-25
type: install-guide
status: active
---

# Phase 04 - Frigate

## Purpose

Prepare VM 101 for Frigate NVR using Debian, Docker, a project Compose file,
camera placeholders, MQTT integration, and later OMV-backed archive storage.
Camera networks remain isolated: no direct internet access to raw camera feeds,
Home Assistant reaches only the intended Frigate paths, and regular Frigate UI
use waits until HTTPS/SSL is configured.

## Runs on

Frigate VM over SSH at `192.168.30.20`.

## Prerequisites

- Phase 03 complete.
- Debian VM 101 exists.
- Camera models and RTSP URLs may still be placeholders.
- `<FRIGATE_RTSP_PASSWORD>` and `<FRIGATE_MQTT_PASSWORD>` recorded when known.

## Inputs

- `<FRIGATE_RTSP_PASSWORD>`
- `<FRIGATE_MQTT_PASSWORD>`
- `<MQTT_PASSWORD>`

## Commands

Run on: Frigate VM over SSH.

```sh
apt-get update && apt-get upgrade -y
apt-get install -y ca-certificates curl gnupg nfs-common ufw
docker --version || true
```

Run on: Frigate VM over SSH after Docker is installed from the official Docker repo.

```sh
mkdir -p /opt/frigate/config /opt/frigate/db
cd /opt/frigate
docker compose config
docker compose up -d
docker compose logs --tail=80 frigate
```

## Explanation

Frigate needs Docker, local database storage, camera configuration, and MQTT
access to Home Assistant. NAS storage is added later so the VM can be validated
before depending on OMV.

## Expected result

- Docker and Compose work.
- Frigate container starts.
- UI is reachable on the documented Frigate port.
- MQTT events can be observed after camera config is real.
- Raw camera streams stay private to the NVR network and Frigate path.

## Validation

Run on: Frigate VM over SSH.

```sh
docker compose ps
ss -tlnp | grep -E '8971|5000|8554' || true
```

Run on: Home Assistant Terminal add-on.

```sh
mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt -u mqtt -P '<MQTT_PASSWORD>' -t 'frigate/#' -C 1
```

## Failure recovery

- If Compose fails, run `docker compose config` and fix YAML/env values first.
- If camera streams fail, validate RTSP with `ffprobe` before changing Frigate.
- If MQTT fails, test HA Mosquitto credentials before changing firewall rules.

## Completion checklist

- [ ] Docker Compose validates.
- [ ] Frigate starts or the placeholder blocker is documented.
- [ ] HA can reach Frigate over the intended firewall path.
- [ ] NAS archive storage remains disabled until OMV is validated.
- [ ] HTTPS/SSL plan documented before regular UI use.
- [ ] WebRTC/audio and Lumen/mobile-viewing needs are documented after camera models are selected.
