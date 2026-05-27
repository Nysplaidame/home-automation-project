---
title: SearXNG Install Manual
description: Tier 2 internal metasearch candidate on docker-host
tags: [install, docker-host, searxng, search, privacy]
created: 2026-05-27
modified: 2026-05-27
type: install-guide
status: preflight-live
---

# SearXNG Install Manual

## Purpose

Provide an internal metasearch service for household/private search experiments.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Egress and rate-limit gate reviewed. SearXNG queries external search engines,
  so deployment changes docker-host's outbound traffic profile.
- Internal-only exposure accepted; no public exposure without a separate review.
- Check current upstream SearXNG deployment docs before live deployment.

## Inputs

- `<SEARXNG_SECRET_KEY>`

## Current pre-flight live state

As of 2026-05-27:

- Stack path: `/opt/stacks/searxng`.
- Direct URL: `http://192.168.20.102:8087/` /
  `http://searxng.home.local:8087/`.
- SearXNG is not behind Caddy/nginx yet; this is intentional for pre-flight.
- `SEARXNG_SECRET` is stored live-only in `/opt/stacks/searxng/.env` and
  `/root/searxng-secret.txt`.
- UFW and `docker-host-firewall.service` scope `8087/tcp` to management, LAN,
  monitoring, and `tailscale0`.
- Uptime Kuma monitor `SearXNG UI` is live and returned `200 OK`.
- Temporary router WiFi uplink is currently required for upstream search while
  the GL-MT6000 is staged behind the existing home router.

## Commands

Run on: docker-host over SSH after approval.

```sh
mkdir -p /opt/stacks/searxng/searxng
cd /opt/stacks/searxng
cat > docker-compose.yml <<'COMPOSE'
services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    restart: unless-stopped
    ports:
      - "8087:8080"
    environment:
      BASE_URL: "http://searxng.home.local:8087/"
      INSTANCE_NAME: "Home SearXNG"
    volumes:
      - ./searxng:/etc/searxng
COMPOSE
docker compose config
```

Do not start the stack until `settings.yml` has a real `secret_key`, limiter
policy, and engine policy reviewed.

## Expected result

After approval and start, SearXNG loads internally at
`http://searxng.home.local:8087/`.

## Validation

Run on: Admin laptop.

```powershell
Test-NetConnection 192.168.20.102 -Port 8087
```

## Backup

Back up `/opt/stacks/searxng/searxng`. Do not treat cache/search history as a
durable asset unless a later decision says otherwise.

## Failure recovery

Run on: docker-host over SSH.

```sh
cd /opt/stacks/searxng
docker compose down
```

If search engines begin rate-limiting or blocking, stop the stack before tuning
outbound access.

## Completion checklist

- [x] Current upstream deployment docs checked.
- [x] `secret_key` generated and stored outside git.
- [x] Egress/rate-limit policy accepted for pre-flight.
- [x] Internal-only access confirmed.
- [x] Uptime Kuma monitor added.
