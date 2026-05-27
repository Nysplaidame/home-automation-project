---
title: ntfy Install Manual
description: Tier 2 notification service draft install
tags: [install, docker-host, ntfy, notifications]
created: 2026-05-24
modified: 2026-05-27
type: install-guide
status: preflight-live
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
- `<NTFY_WATCHTOWER_PASSWORD>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/ntfy/cache /opt/stacks/ntfy/etc
cd /opt/stacks/ntfy
cat > etc/server.yml <<'YAML'
base-url: "http://ntfy.home.local:8085"
listen-http: ":80"
cache-file: "/var/cache/ntfy/cache.db"
auth-file: "/etc/ntfy/user.db"
auth-default-access: "deny-all"
behind-proxy: true
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
    networks:
      - alerting
networks:
  alerting:
    name: local-alerting
COMPOSE
docker compose config
docker compose up -d
```

## Current pre-flight live state

As of 2026-05-27:

- Stack path: `/opt/stacks/ntfy`.
- URL: `http://192.168.20.102:8085/` / `http://ntfy.home.local:8085/`.
- DNS alias `ntfy.home.local` points to `192.168.20.102`.
- Credentials are stored on docker-host at `/root/ntfy-credentials.txt`.
- `auth-default-access: "deny-all"` is live.
- Users:
  - `admin`: admin role.
  - `watchtower`: write-only access to topic `watchtower`.
- UFW and `docker-host-firewall.service` scope `8085/tcp` to management, LAN,
  HA, monitoring, and `tailscale0`.
- Uptime Kuma monitor `ntfy UI` is live.

## Explanation

The default policy denies access until users/topics are configured. This avoids
accidentally creating an unauthenticated notification relay.

## Expected result

ntfy listens internally at `http://192.168.20.102:8085/`.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/ntfy && docker compose ps
curl -fsS -o /dev/null -w '%{http_code}\n' http://192.168.20.102:8085/
```

## Backup

Back up `/opt/stacks/ntfy/etc` and cache if message history matters.

## Failure recovery

If auth blocks expected messages, inspect `server.yml` and user configuration
before changing firewall exposure.

## Completion checklist

- [x] Internal/public decision recorded.
- [x] Default access is not open.
- [x] Config is backed up by stack path and Proxmox VM backup.
