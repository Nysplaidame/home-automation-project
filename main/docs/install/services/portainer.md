---
title: Portainer Install Manual
description: Tier 3 Docker management UI candidate with socket exposure gate
tags: [install, docker-host, portainer, tier3]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# Portainer Install Manual

## Purpose

Evaluate Portainer as a Docker management UI. It increases the admin surface and
requires explicit approval before deployment.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- Portainer decision gate approved.
- Access restricted to Management/Tailscale.

## Inputs

- `<PORTAINER_ADMIN_PASSWORD>`

## Commands

Run on: docker-host over SSH after gate approval.

```sh
mkdir -p /opt/stacks/portainer/data
cd /opt/stacks/portainer
cat > docker-compose.yml <<'COMPOSE'
services:
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    ports:
      - "9443:9443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data:/data
COMPOSE
docker compose config
docker compose up -d
```

## Explanation

Portainer controls Docker through the Docker socket. That is convenient but
powerful, so access must stay tightly restricted.

## Expected result

Portainer loads at `https://192.168.20.102:9443/`.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/portainer && docker compose ps
```

## Backup

Back up `/opt/stacks/portainer/data`.

## Failure recovery

If exposure is too broad or not understood, stop Portainer immediately.

## Completion checklist

- [ ] Socket exposure gate approved.
- [ ] UI restricted.
- [ ] Data backed up.
