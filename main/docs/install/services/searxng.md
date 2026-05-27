---
title: SearXNG Install Manual
description: Tier 2 internal metasearch candidate on docker-host
tags: [install, docker-host, searxng, search, privacy]
created: 2026-05-27
modified: 2026-05-27
type: install-guide
status: draft-installable
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

- [ ] Current upstream deployment docs checked.
- [ ] `secret_key` generated and stored outside git.
- [ ] Egress/rate-limit policy accepted.
- [ ] Internal-only access confirmed.
- [ ] Uptime Kuma monitor added if promoted beyond evaluation.
