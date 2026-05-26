---
title: Dozzle Install Manual
description: Tier 1 internal Docker log viewer
tags: [install, docker-host, dozzle, logs]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# Dozzle Install Manual

## Purpose

Provide a lightweight internal view of Docker container logs on docker-host.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Admin/internal-only access policy accepted.

## Inputs

No required secrets for the basic internal deployment.

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/dozzle
cd /opt/stacks/dozzle
cat > docker-compose.yml <<'COMPOSE'
services:
  dozzle:
    image: amir20/dozzle:latest
    container_name: dozzle
    restart: unless-stopped
    ports:
      - "8081:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
COMPOSE
docker compose config
docker compose up -d
```

## Explanation

Dozzle needs read-only Docker socket access to read logs. Keep it off Guest, DMZ,
and public networks.

## Expected result

Dozzle loads at `http://dozzle.home.local:8081/`.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/dozzle
docker compose ps
docker compose logs --tail=20
```

## Backup

No critical app data. Back up the Compose file for reproducibility.

## Failure recovery

- If it shows no containers, check the Docker socket mount.
- If access is too broad, stop the stack until firewall/UFW is corrected.

## Completion checklist

- [ ] UI loads.
- [ ] Docker socket mounted read-only.
- [ ] Access restricted to approved networks.
