---
title: GardenKeeper Install Manual
description: Internal garden care, task, calendar, and map app on docker-host
tags: [install, docker-host, gardenkeeper]
created: 2026-06-29
modified: 2026-06-29
type: install-guide
status: draft-installable
---

# GardenKeeper Install Manual

## Purpose

Run GardenKeeper as an internal household garden operations app for plant care
profiles, garden tasks, reminders, calendar projection, mapped zones, and safe
Home Assistant Assist task commands.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- GardenKeeper source is available under `/opt/stacks/gardenkeeper/source`.
- Docker-host has an approved update/build path for base images and npm/pip
  dependencies, either through a temporary maintenance window or offline image
  transfer.
- DNS alias `gardenkeeper.home.local` points to `192.168.20.102`.
- Docker-host firewall template allows ports `8090` and `8091` from approved
  sources.

## Inputs

Required for first deployment:

- Generated `POSTGRES_PASSWORD`.

Optional integration secrets:

- `GARDENKEEPER_NOTIFICATION_BROKER_URL` and broker token, if using the central
  notification broker.
- `HOME_ASSISTANT_WEBHOOK_SECRET`, if enabling Assist command ingress.
- `NEXTCLOUD_CALDAV_URL`, `NEXTCLOUD_USER`, and `NEXTCLOUD_APP_PASSWORD`, if
  projecting tasks and garden calendar events to Nextcloud.
- Mealie, Grocy, and future Knowledge Hub API credentials only after those
  contracts are approved.

## Current live state

Not yet live. Template path:

```text
configs/docker-host/stacks/gardenkeeper/
```

Planned URLs:

- Web UI: `http://gardenkeeper.home.local:8091/`
- API health: `http://gardenkeeper.home.local:8090/health`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/gardenkeeper
cd /opt/stacks/gardenkeeper
cp /path/to/templates/docker-compose.yml .
cp /path/to/templates/env.example .env
```

Edit `.env`, set generated passwords/secrets, and ensure `DATABASE_URL` uses the
same generated Postgres password.

Place GardenKeeper source at `/opt/stacks/gardenkeeper/source`, then:

```sh
docker compose config
docker compose up -d --build
```

## Explanation

GardenKeeper is a modular monolith with PostgreSQL, Redis, FastAPI, a worker,
and a static React/Vite web app served by nginx. It belongs on docker-host
because it is internal-only, lightweight, and does not run model weights. Local
LLM, STT, TTS, and wake-word inference remain on CT 114 `llm-host`.

## Expected result

- `gardenkeeper-postgres` and `gardenkeeper-redis` are healthy.
- API responds at `http://gardenkeeper.home.local:8090/health`.
- Web UI loads at `http://gardenkeeper.home.local:8091/`.
- API status reports the configured integration state.

## Validation

Run on: Admin laptop.

```powershell
Test-NetConnection 192.168.20.102 -Port 8090
Test-NetConnection 192.168.20.102 -Port 8091
Invoke-RestMethod http://gardenkeeper.home.local:8090/health
```

Run on: docker-host over SSH.

```sh
cd /opt/stacks/gardenkeeper
docker compose ps
docker compose logs --tail=100 api worker web
```

## Backup

Back up:

- `/opt/stacks/gardenkeeper/.env`
- `/opt/stacks/gardenkeeper/docker-compose.yml`
- `/opt/stacks/gardenkeeper/postgres-data`

Redis data is rebuildable task/worker state unless future behavior makes it
authoritative.

## Failure recovery

- If migrations fail, keep the existing Postgres data directory intact and
  inspect `docker compose logs api` before retrying.
- If the web UI loads but API calls fail, verify nginx proxying through the web
  image and direct API health on port `8090`.
- If Docker pulls fail, use the docker-host maintenance window or offline image
  transfer pattern from `docs/procedures/update_maintenance_playbook.md`.

## Completion checklist

- [ ] Stack starts cleanly.
- [ ] Web UI loads.
- [ ] API health and status pass.
- [ ] Docker-host firewall and router DNS include GardenKeeper.
- [ ] Homepage link added.
- [ ] Uptime Kuma monitors added for web and API health.
- [ ] Secrets stored outside Git.
