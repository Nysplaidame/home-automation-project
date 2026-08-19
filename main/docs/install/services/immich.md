---
title: Immich Install Manual
description: Tier 1 docker-host photo and gallery service with OMV-backed media storage
tags: [install, docker-host, immich, photos]
created: 2026-05-24
modified: 2026-06-26
type: install-guide
status: preflight-live
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
- VM 103 sized for Immich pre-flight load. Current live size is 2 cores and
  4096 MiB RAM.

## Inputs

- `<IMMICH_ADMIN_EMAIL>`
- `<IMMICH_ADMIN_PASSWORD>`
- `<IMMICH_DB_PASSWORD>`

## Commands

Run on: docker-host over SSH.

Copy the reviewed tracked `configs/docker-host/stacks/immich/` template into
`/opt/stacks/immich/`. Compare it with the current official Immich release
before deployment and record the accepted version/digests.

Run on: docker-host over SSH.

```sh
findmnt -n -o SOURCE,FSTYPE,TARGET --target /mnt/omv/immich
test "$(findmnt -n -o FSTYPE --target /mnt/omv/immich)" = nfs4
cd /opt/stacks/immich
cp .env.example .env
chmod 600 .env
nano .env
! grep -n '<IMMICH_DB_PASSWORD>' .env
docker compose config --quiet
docker compose up -d database redis immich-server
docker compose ps
```

Enter `<IMMICH_DB_PASSWORD>` only in the local editor and save it to the
password manager. The negated `grep` must return success with no output.

## Current live state

As of 2026-06-26, Immich uses OMV-backed media storage:

- Stack path: `/opt/stacks/immich`.
- Version: `v2.7.5`.
- URL: `http://192.168.20.102:2283/` / `http://immich.home.local:2283/`.
- `UPLOAD_LOCATION=/mnt/omv/immich`.
- OMV mount: `192.168.40.50:/export/immich` at `/mnt/omv/immich`.
- `DB_DATA_LOCATION=./postgres`.
- Database password is stored on docker-host at `/root/immich-db-password.txt`.
- `vm.overcommit_memory=1` is set through `/etc/sysctl.d/98-immich-valkey.conf`.
- `immich_server`, `immich_postgres`, and `immich_redis` are running.
- `immich_machine_learning` is intentionally stopped to keep VM 103 stable at
  the current pre-flight sizing.
- UFW and `docker-host-firewall.service` scope port `2283` to management, LAN,
  monitoring, and `tailscale0`.
- Uptime Kuma monitor `Immich UI` is live and returned `200 OK`.
- docker-host Telegraf bind-mounts `/` with `rslave` propagation so the NFS
  mount is visible in disk telemetry.

Do not import a real library until backup/restore expectations for the OMV media
path and local PostgreSQL data are accepted.

## Explanation

Immich publishes official Compose files per release. The tracked template is the
reviewed rebuild baseline; compare it with upstream before updates. The upload
location stays on the OMV-backed mount so the VM disk cannot become accidental
long-term media storage.

## Expected result

Immich loads at `http://immich.home.local:2283/` or
`http://192.168.20.102:2283/`.

## Validation

Run on: docker-host over SSH.

```sh
findmnt /mnt/omv/immich
cd /opt/stacks/immich && docker compose ps
curl -fsS -o /dev/null -w '%{http_code}\n' http://192.168.20.102:2283/
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
- [x] Pre-flight Compose config passes.
- [x] Pre-flight UI loads.
- [ ] Backup/restore note accepted before real import.
