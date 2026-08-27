---
title: ntfy Install Manual
description: Tier 2 notification service draft install
tags: [install, docker-host, ntfy, notifications]
created: 2026-05-24
modified: 2026-08-01
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
- `<NTFY_MONITORING_PASSWORD>`
- `<NTFY_MOBILE_SUBSCRIBER_PASSWORD>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/ntfy/cache /opt/stacks/ntfy/etc
cd /opt/stacks/ntfy
cat > etc/server.yml <<'YAML'
base-url: "https://192.168.20.102:8193"
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
- Primary browser URL: `https://192.168.20.102:8193/`, terminated by the
  Homepage local-CA HTTPS proxy. This is the required secure context for the
  browser Notifications API.
- Raw `http://192.168.20.102:8085/` remains an internal service listener only;
  do not use it in a browser or as ntfy's advertised base URL.
- Mobile Tailscale URL: `https://docker-host.tail7012a0.ts.net:8444/`, served
  privately by Tailscale Serve with a Tailscale-issued certificate.
- DNS alias `ntfy.home.local` points to `192.168.20.102`.
- Credentials are stored on docker-host at `/root/ntfy-credentials.txt`.
- `auth-default-access: "deny-all"` is live.
- Users:
  - `admin`: admin role.
  - `watchtower`: write-only access to topic `watchtower`.
  - `monitoring`: write-only access to topic `monitoring`.
  - `mobile-monitoring`: read-only access to topics `monitoring` and
    `watchtower`; generated credential stored outside the repository in Windows
    Credential Manager target `home-automation/ntfy-mobile`.
- UFW and `docker-host-firewall.service` scope `8085/tcp` to management, LAN,
  HA, monitoring, and `tailscale0`.
- Uptime Kuma monitor `ntfy UI` is live.
- Uptime Kuma notification `ntfy Monitoring` is active/default and mapped to all
  active monitors; database backup before enabling it:
  `/opt/monitoring/uptime-kuma/kuma.db.backup-20260527-172349-before-ntfy-notification`.

## Explanation

The default policy denies access until users/topics are configured. This avoids
accidentally creating an unauthenticated notification relay.

## Expected result

ntfy's browser-facing base URL is `https://192.168.20.102:8193/`; it listens
internally on HTTP `8085` only behind the HTTPS/Tailscale terminators.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/ntfy && docker compose ps
curl -kfsS -o /dev/null -w '%{http_code}\n' https://192.168.20.102:8193/
```

## Mobile subscriber rollout

Create a separate read-only identity for household phones rather than signing
the app in as the ntfy administrator or a publisher account:

Run on: docker-host over SSH.

```sh
docker exec -it ntfy ntfy user add mobile-monitoring
docker exec ntfy ntfy access mobile-monitoring monitoring ro
docker exec ntfy ntfy access mobile-monitoring watchtower ro
docker exec ntfy ntfy user list
docker exec ntfy ntfy access
```

Store the generated password in a credential manager; do not add it to this
repository. The live account was created on 2026-07-29 and its credential is in
Windows Credential Manager under `home-automation/ntfy-mobile`.
On the phone, connect Tailscale and add a custom ntfy server using:

- server: `https://docker-host.tail7012a0.ts.net:8444`
- topic: `monitoring`
- user: `mobile-monitoring`
- password: the Bitwarden value

This must be entered manually rather than through the old `ntfy://` deep link.
The mobile endpoint uses a Tailscale-issued HTTPS certificate; do not expose
port `8085` publicly.

After subscribing, publish one labelled test message and confirm it appears on
the phone before relying on ntfy for incident delivery.

## Backup

VM 103's recurring Proxmox backup covers the whole stack. The live docker-host
app-data backup job also stages a consistent SQLite snapshot of `etc/user.db`
and `cache/cache.db` using Python's SQLite backup API, plus the remaining files
under `etc/`. On 2026-07-29 a fresh NAS run completed and temporary restored
copies of both databases passed SQLite integrity checks.

## Failure recovery

If auth blocks expected messages, inspect `server.yml` and user configuration
before changing firewall exposure.

## Completion checklist

- [x] Internal/public decision recorded.
- [x] Default access is not open.
- [x] Topic users created for Watchtower and Uptime Kuma monitoring.
- [x] Config is backed up by stack path and Proxmox VM backup.
- [x] Create the read-only `mobile-monitoring` subscriber and validate its
  authenticated subscription; phone-side notification acceptance is pending.
- [x] Deploy and restore-smoke the granular ntfy app-data backup template.
- [ ] Add an HTTPS canonical endpoint before permitting any access outside the
  LAN or tailnet.
