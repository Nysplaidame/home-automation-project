---
title: Homepage Install Manual
description: Tier 1 internal dashboard for service links
tags: [install, docker-host, homepage]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# Homepage Install Manual

## Purpose

Provide a simple internal dashboard for project service links and status widgets.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Service matrix available.

## Inputs

No required secrets. Do not place tokens or passwords in visible Homepage config.

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/homepage/config
cd /opt/stacks/homepage
cat > docker-compose.yml <<'COMPOSE'
services:
  homepage:
    image: ghcr.io/gethomepage/homepage:latest
    container_name: homepage
    restart: unless-stopped
    ports:
      - "3001:3000"
    volumes:
      - ./config:/app/config
      - /var/run/docker.sock:/var/run/docker.sock:ro
COMPOSE
cat > config/services.yaml <<'YAML'
- Infrastructure:
    - Home Assistant:
        href: http://192.168.20.101:8123/
    - AdGuard Home:
        href: http://192.168.20.102:8080/
    - Immich:
        href: http://192.168.20.102:2283/
YAML
docker compose config
docker compose up -d
```

## Explanation

Homepage is internal navigation, not an authentication layer. It may read Docker
metadata through a read-only socket mount; remove that mount if not needed.

## Expected result

Homepage loads at `http://homepage.home.local:3001/`.

## Validation

Run on: Admin laptop.

```powershell
Test-NetConnection 192.168.20.102 -Port 3001
```

## Backup

Back up `/opt/stacks/homepage/config`.

## Failure recovery

- If config breaks the page, move the changed YAML aside and restart.
- If Docker socket exposure is undesired, remove the socket mount.

## Completion checklist

- [ ] UI loads.
- [ ] No secrets visible in config.
- [ ] Config directory backed up.
