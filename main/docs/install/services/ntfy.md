---
title: ntfy Install Manual
description: Tier 2 notification service draft install
tags: [install, docker-host, ntfy, notifications]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# ntfy Install Manual

## Purpose

Provide self-hosted notifications for monitoring and automation alerts.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Internal-only versus public relay decision gate reviewed.

## Inputs

- `<NTFY_ADMIN_PASSWORD>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/ntfy/{cache,etc}
cd /opt/stacks/ntfy
cat > etc/server.yml <<'YAML'
base-url: "http://ntfy.home.local:8085"
listen-http: ":80"
cache-file: "/var/cache/ntfy/cache.db"
auth-file: "/etc/ntfy/user.db"
auth-default-access: "deny-all"
YAML
cat > docker-compose.yml <<'COMPOSE'
services:
  ntfy:
    image: binwiederhier/ntfy:latest
    container_name: ntfy
    command: serve
    restart: unless-stopped
    ports:
      - "8085:80"
    volumes:
      - ./cache:/var/cache/ntfy
      - ./etc:/etc/ntfy
COMPOSE
docker compose config
docker compose up -d
```

## Explanation

The default policy denies access until users/topics are configured. This avoids
accidentally creating an unauthenticated notification relay.

## Expected result

ntfy listens internally at `http://192.168.20.102:8085/`.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/ntfy && docker compose ps
```

## Backup

Back up `/opt/stacks/ntfy/etc` and cache if message history matters.

## Failure recovery

If auth blocks expected messages, inspect `server.yml` and user configuration
before changing firewall exposure.

## Completion checklist

- [ ] Internal/public decision recorded.
- [ ] Default access is not open.
- [ ] Config is backed up.
