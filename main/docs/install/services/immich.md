---
title: Immich Install Manual
description: Tier 1 docker-host photo and gallery service with OMV-backed media storage
tags: [install, docker-host, immich, photos]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# Immich Install Manual

## Purpose

Provide a self-hosted photo gallery and upload service. Immich runs on docker-host;
bulk media storage is OMV-backed.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- OMV Immich share mounted at `/mnt/omv/immich` before real imports.
- Docker Compose plugin installed.

## Inputs

- `<IMMICH_ADMIN_EMAIL>`
- `<IMMICH_ADMIN_PASSWORD>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/immich
cd /opt/stacks/immich
wget -O docker-compose.yml https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml
wget -O .env https://github.com/immich-app/immich/releases/latest/download/example.env
sed -i 's#^UPLOAD_LOCATION=.*#UPLOAD_LOCATION=/mnt/omv/immich#' .env
docker compose config
docker compose up -d
docker compose ps
```

## Explanation

Immich publishes official Compose files per release. The upload location is
changed to the OMV-backed mount so the VM disk is not the long-term media store.

## Expected result

Immich loads at `http://immich.home.local:2283/` or
`http://192.168.20.102:2283/`.

## Validation

Run on: docker-host over SSH.

```sh
findmnt /mnt/omv/immich
cd /opt/stacks/immich && docker compose ps
```

## Backup

Back up Immich database volumes and `/mnt/omv/immich`. Do not import a real photo
library until restore steps are documented and tested.

## Failure recovery

- If OMV mount is missing, stop Immich before uploads.
- If containers restart, inspect `docker compose logs --tail=120`.
- If the official Compose file changes materially, record the release before editing.

## Completion checklist

- [ ] OMV media path mounted.
- [ ] Compose config passes.
- [ ] UI loads.
- [ ] Backup/restore note accepted before real import.
