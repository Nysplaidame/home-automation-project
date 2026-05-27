---
title: Whoogle Install Manual
description: Tier 2 internal Google-search proxy candidate on docker-host
tags: [install, docker-host, whoogle, search, privacy]
created: 2026-05-27
modified: 2026-05-27
type: install-guide
status: preflight-live
---

# Whoogle Install Manual

## Purpose

Provide an internal, lightweight Google-search proxy candidate for private search
experiments.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Egress and rate-limit gate reviewed. Whoogle queries Google and may be blocked
  or rate-limited.
- Internal-only exposure accepted; no public exposure without a separate review.
- Check current upstream Whoogle deployment docs before live deployment.

## Inputs

No required project secrets for a basic internal evaluation.

## Current pre-flight live state

As of 2026-05-27:

- Stack path: `/opt/stacks/whoogle`.
- Direct URL: `http://192.168.20.102:8088/` /
  `http://whoogle.home.local:8088/`.
- Whoogle is not behind Caddy/nginx yet; this is intentional for pre-flight.
- UFW and `docker-host-firewall.service` scope `8088/tcp` to management, LAN,
  monitoring, and `tailscale0`.
- Uptime Kuma monitor `Whoogle UI` is live and returned `200 OK`.
- Temporary router WiFi uplink is currently required for upstream search while
  the GL-MT6000 is staged behind the existing home router.

## Commands

Run on: docker-host over SSH after approval.

```sh
mkdir -p /opt/stacks/whoogle
cd /opt/stacks/whoogle
cat > docker-compose.yml <<'COMPOSE'
services:
  whoogle:
    image: benbusby/whoogle-search:latest
    container_name: whoogle
    restart: unless-stopped
    ports:
      - "8088:5000"
COMPOSE
docker compose config
```

Do not start the stack until the egress/rate-limit gate is accepted.

## Expected result

After approval and start, Whoogle loads internally at
`http://whoogle.home.local:8088/`.

## Validation

Run on: Admin laptop.

```powershell
Test-NetConnection 192.168.20.102 -Port 8088
```

## Backup

No critical app data for a basic evaluation. Back up the Compose file for
reproducibility if promoted.

## Failure recovery

Run on: docker-host over SSH.

```sh
cd /opt/stacks/whoogle
docker compose down
```

If upstream blocks or rate-limits queries, stop the stack before changing router
or host egress policy.

## Completion checklist

- [x] Current upstream deployment docs checked.
- [x] Egress/rate-limit policy accepted for pre-flight.
- [x] Internal-only access confirmed.
- [x] Uptime Kuma monitor added.
