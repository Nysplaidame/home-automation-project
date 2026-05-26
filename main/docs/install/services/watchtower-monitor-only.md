---
title: Watchtower Monitor-only Install Manual
description: Tier 3 update notification candidate without automatic updates
tags: [install, docker-host, watchtower, tier3]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
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

- `<WATCHTOWER_HTTP_API_TOKEN>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/watchtower
cd /opt/stacks/watchtower
cat > docker-compose.yml <<'COMPOSE'
services:
  watchtower:
    image: containrrr/watchtower:latest
    container_name: watchtower
    restart: unless-stopped
    environment:
      WATCHTOWER_MONITOR_ONLY: "true"
      WATCHTOWER_SCHEDULE: "0 0 4 * * *"
      WATCHTOWER_HTTP_API_METRICS: "true"
      WATCHTOWER_HTTP_API_TOKEN: "<WATCHTOWER_HTTP_API_TOKEN>"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
COMPOSE
docker compose config
docker compose up -d
```

## Explanation

`WATCHTOWER_MONITOR_ONLY=true` is the central safety setting. Do not remove it
without a new decision.

## Expected result

Watchtower runs and reports updates, but does not recreate containers.

## Validation

Run on: docker-host over SSH.

```sh
docker inspect watchtower --format '{{range .Config.Env}}{{println .}}{{end}}' | grep WATCHTOWER_MONITOR_ONLY
```

## Backup

No critical data. Back up the Compose file.

## Failure recovery

If automatic update behavior is observed, stop the stack and inspect environment.

## Completion checklist

- [ ] Monitor-only setting present.
- [ ] No auto-update policy accepted.
- [ ] Notification path documented.
