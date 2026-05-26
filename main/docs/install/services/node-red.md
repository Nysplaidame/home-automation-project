---
title: Node-RED Install Manual
description: Tier 3 automation workflow candidate
tags: [install, docker-host, node-red, tier3]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# Node-RED Install Manual

## Purpose

Evaluate Node-RED only if Home Assistant native automations are insufficient.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- Node-RED decision gate approved.
- Flow backup plan documented.
- Credential secret generated.

## Inputs

- `<NODE_RED_CREDENTIAL_SECRET>`

## Commands

Run on: docker-host over SSH after gate approval.

```sh
mkdir -p /opt/stacks/node-red/data
cd /opt/stacks/node-red
cat > docker-compose.yml <<'COMPOSE'
services:
  node-red:
    image: nodered/node-red:latest
    container_name: node-red
    restart: unless-stopped
    ports:
      - "1880:1880"
    environment:
      TZ: "Europe/London"
    volumes:
      - ./data:/data
COMPOSE
docker compose config
docker compose up -d
```

## Explanation

Node-RED can become a second automation brain. Keep it gated so HA remains the
default automation platform unless a concrete need exists.

## Expected result

Node-RED loads at `http://192.168.20.102:1880/`.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/node-red && docker compose ps
```

## Backup

Back up `/opt/stacks/node-red/data`, especially flows and credentials.

## Failure recovery

If flows misbehave, stop Node-RED before troubleshooting HA automations.

## Completion checklist

- [ ] Gate approved.
- [ ] Credential secret stored.
- [ ] Flow backup path documented.
