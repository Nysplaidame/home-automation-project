---
title: Watchtower Monitor-only Install Manual
description: Tier 3 update notification candidate without automatic updates
tags: [install, docker-host, watchtower, tier3]
created: 2026-05-24
modified: 2026-08-09
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

Copy the source-controlled Compose file, then enter the ntfy password without
putting it in shell history. Do not substitute an unreviewed upstream Compose
example: the tracked file pins `1.7.1` and carries the monitor-only invariant.

Run on: docker-host over SSH.

```bash
install -d -m 0750 /opt/stacks/watchtower
cp /path/to/repo/main/configs/docker-host/stacks/watchtower/docker-compose.yml \
  /opt/stacks/watchtower/docker-compose.yml
cd /opt/stacks/watchtower
read -r -s -p 'WATCHTOWER_NTFY_PASSWORD from Bitwarden: ' watchtower_ntfy_password
printf '\n'
umask 077
printf 'WATCHTOWER_NTFY_PASSWORD=%s\n' "$watchtower_ntfy_password" >.env
unset watchtower_ntfy_password
chmod 0600 .env
docker compose config --quiet
docker compose config --format json \
  | jq -e '.services.watchtower.environment.WATCHTOWER_MONITOR_ONLY == "true"' >/dev/null
docker compose up -d
docker compose ps
```

Expected result: both validation commands exit `0`, Watchtower is `Up`, and no
HTTP/API port is published. If the JSON assertion fails, do not start/recreate
the container.

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

```bash
docker inspect watchtower --format '{{range .Config.Env}}{{println .}}{{end}}' | grep WATCHTOWER_MONITOR_ONLY
docker logs --tail 80 watchtower
```

Expected output contains exactly `WATCHTOWER_MONITOR_ONLY=true`; logs may report
available images but must not report stopping, recreating, or updating a target
container. During an approved registry-egress window, record target container
IDs/start times before and after a scan and prove they are unchanged.

## Backup

No critical data. Back up the Compose file.

## Failure recovery

If automatic update behavior is observed, stop Watchtower immediately, capture
logs and target container IDs, restore any affected service using its own pinned
image/data rollback, then repair the tracked/runtime monitor-only setting before
another notification test.

## Completion checklist

- [x] Monitor-only setting present.
- [x] No auto-update policy accepted.
- [x] Notification path documented.
