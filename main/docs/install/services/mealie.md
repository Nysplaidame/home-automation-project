---
title: Mealie Install Manual
description: Live internal recipe and meal-planning service
tags: [install, docker-host, mealie]
created: 2026-05-24
modified: 2026-06-21
type: install-guide
status: live
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

- An operator ready to replace the bootstrap administrator credentials on first login.

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/mealie/data
cp /path/to/repo/main/configs/docker-host/stacks/mealie/docker-compose.yml \
  /opt/stacks/mealie/docker-compose.yml
cd /opt/stacks/mealie
docker compose config
docker compose up -d
```

## Explanation

The SQLite deployment is appropriate for this household. The image is pinned to
`v3.19.2`, open signup is disabled, and `mealie.home.local` is the canonical
internal name. Image pulls use the temporary Docker-host maintenance window in
`docs/procedures/update_maintenance_playbook.md`.

## Expected result

Mealie loads at `http://mealie.home.local:9925/`.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/mealie && docker compose ps
curl -fsS -o /dev/null http://127.0.0.1:9925/
```

## Backup

Back up `/opt/stacks/mealie/data`.

## Failure recovery

If the web UI does not load, inspect `docker compose logs --tail=80`.

## Completion checklist

- [x] UI loads.
- [x] Signup disabled.
- [ ] Data directory backed up.
- [ ] Bootstrap administrator credentials replaced and stored in Bitwarden.
