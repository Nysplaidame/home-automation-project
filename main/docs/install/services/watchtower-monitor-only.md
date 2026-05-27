---
title: Watchtower Monitor-only Install Manual
description: Tier 3 update notification candidate without automatic updates
tags: [install, docker-host, watchtower, tier3]
created: 2026-05-24
modified: 2026-05-27
type: install-guide
status: preflight-live
---

# Watchtower Monitor-only Install Manual

## Purpose

Monitor for container image updates without applying automatic updates.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- Monitor-only gate approved.
- Notification target chosen if desired.

## Inputs

- `<WATCHTOWER_NTFY_PASSWORD>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/watchtower
cd /opt/stacks/watchtower
cat > .env <<'ENV'
WATCHTOWER_NTFY_PASSWORD=<WATCHTOWER_NTFY_PASSWORD>
ENV
chmod 600 .env
cat > docker-compose.yml <<'COMPOSE'
services:
  watchtower:
    image: containrrr/watchtower:latest
    container_name: watchtower
    restart: unless-stopped
    environment:
      DOCKER_API_VERSION: "1.40"
      WATCHTOWER_MONITOR_ONLY: "true"
      WATCHTOWER_SCHEDULE: "0 0 4 * * *"
      WATCHTOWER_NOTIFICATIONS: "shoutrrr"
      WATCHTOWER_NOTIFICATION_URL: "ntfy://watchtower:${WATCHTOWER_NTFY_PASSWORD}@ntfy/watchtower?scheme=http"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - alerting
networks:
  alerting:
    name: local-alerting
    external: true
COMPOSE
docker compose config
docker compose up -d
```

## Current pre-flight live state

As of 2026-05-27:

- Stack path: `/opt/stacks/watchtower`.
- Watchtower `1.7.1` is running in monitor-only mode.
- `DOCKER_API_VERSION=1.40` is set because the docker-host daemon rejects the
  older default client API version.
- Notifications target internal ntfy topic `watchtower` over the shared
  `local-alerting` Docker network.
- No Watchtower HTTP/API port is exposed.
- Docker-host remains blocked from general internet access outside maintenance
  windows, so Watchtower update checks are meaningful only during an approved
  registry egress window unless a future decision allows narrow permanent
  registry access.

## Explanation

`WATCHTOWER_MONITOR_ONLY=true` is the central safety setting. Do not remove it
without a new decision.

## Expected result

Watchtower runs and reports updates, but does not recreate containers.

## Validation

Run on: docker-host over SSH.

```sh
docker inspect watchtower --format '{{range .Config.Env}}{{println .}}{{end}}' | grep WATCHTOWER_MONITOR_ONLY
docker logs --tail 80 watchtower
```

## Backup

No critical data. Back up the Compose file.

## Failure recovery

If automatic update behavior is observed, stop the stack and inspect environment.

## Completion checklist

- [x] Monitor-only setting present.
- [x] No auto-update policy accepted.
- [x] Notification path documented.
