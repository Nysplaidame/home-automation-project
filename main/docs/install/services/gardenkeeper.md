---
title: GardenKeeper Install Manual
description: Internal garden care, task, calendar, and map app on docker-host
tags: [install, docker-host, gardenkeeper]
created: 2026-06-29
modified: 2026-07-06
type: install-guide
status: live
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

GardenKeeper is live on docker-host at:

```text
/opt/stacks/gardenkeeper/
```

Source templates remain under:

```text
configs/docker-host/stacks/gardenkeeper/
```

Live URLs:

- Web UI: `http://gardenkeeper.home.local:8091/`
- API health: `http://gardenkeeper.home.local:8090/health`

Current live integrations:

- Home Assistant package installed at `/config/packages/gardenkeeper_package.yaml`.
- HA Monitoring dashboard includes a GardenKeeper health card and app link.
- Uptime Kuma monitors cover the API health endpoint and web UI.
- ntfy broker integration is configured through the central notification stack.
- Local Postgres dump timer is enabled on docker-host.

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

Run on: docker-host over SSH.

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

The docker-host template also includes a lightweight local PostgreSQL dump
timer:

Run on: docker-host over SSH.

```sh
install -m 0755 backup-gardenkeeper.sh /opt/stacks/gardenkeeper/backup-gardenkeeper.sh
install -m 0644 gardenkeeper-backup.service /etc/systemd/system/gardenkeeper-backup.service
install -m 0644 gardenkeeper-backup.timer /etc/systemd/system/gardenkeeper-backup.timer
systemctl daemon-reload
systemctl enable --now gardenkeeper-backup.timer
systemctl start gardenkeeper-backup.service
```

It writes compressed dumps to `/opt/stacks/gardenkeeper/backups/` and keeps
14 days by default.

Read-only check on 2026-07-06:

- `/opt/stacks/gardenkeeper/backups` exists and is `36K`.
- Recent daily dumps exist through
  `gardenkeeper-postgres-20260706T022024Z.sql.gz`.
- `/opt/stacks/gardenkeeper/postgres-data` exists and is `47M`.
- OMV exports `backups/docker-host` to docker-host; the docker-host
  `/mnt/omv/docker-host-backups` mount and daily `03:45` app-data backup timer
  are live and restore-smoked as of 2026-07-07.

The repo-side docker-host app-data backup templates now include
`/opt/stacks/gardenkeeper/backups`. Treat the local dump timer as the database
consistency layer and the docker-host app-data backup as the off-host copy.

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

- [x] Stack starts cleanly.
- [x] Web UI loads.
- [x] API health and status pass.
- [x] Docker-host firewall and router DNS include GardenKeeper.
- [ ] Homepage link added.
- [x] Uptime Kuma monitors added for web and API health.
- [x] Secrets stored outside Git.
- [x] Local Postgres dump timer is enabled and producing dumps.
- [ ] OMV-backed off-host dump copy is mounted, verified, and restore-smoked.
