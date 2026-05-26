---
title: Mealie Install Manual
description: Tier 2 recipe and meal-planning draft install
tags: [install, docker-host, mealie]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# Mealie Install Manual

## Purpose

Host household recipes and meal planning.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Internal-only access chosen.

## Inputs

- `<MEALIE_ADMIN_EMAIL>`
- `<MEALIE_ADMIN_PASSWORD>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/mealie/data
cd /opt/stacks/mealie
cat > docker-compose.yml <<'COMPOSE'
services:
  mealie:
    image: ghcr.io/mealie-recipes/mealie:latest
    container_name: mealie
    restart: unless-stopped
    ports:
      - "9925:9000"
    volumes:
      - ./data:/app/data
    environment:
      ALLOW_SIGNUP: "false"
      PUID: "1000"
      PGID: "1000"
      TZ: "Europe/London"
COMPOSE
docker compose config
docker compose up -d
```

## Explanation

The SQLite-style deployment is simplest for a single household. Disable open
signup unless there is a reason to allow it.

## Expected result

Mealie loads at `http://192.168.20.102:9925/`.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/mealie && docker compose ps
```

## Backup

Back up `/opt/stacks/mealie/data`.

## Failure recovery

If the web UI does not load, inspect `docker compose logs --tail=80`.

## Completion checklist

- [ ] UI loads.
- [ ] Signup disabled.
- [ ] Data directory backed up.
