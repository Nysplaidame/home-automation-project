---
title: Vaultwarden Install Manual
description: Tier 3 password vault candidate with strict decision gate
tags: [install, docker-host, vaultwarden, tier3]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# Vaultwarden Install Manual

## Purpose

Evaluate Vaultwarden as a self-hosted password vault. This is high sensitivity
and must not become live until the gate is approved.

## Runs on

docker-host over SSH at `192.168.20.102` after gate approval.

## Prerequisites

- Vaultwarden decision gate complete.
- HTTPS/reverse proxy plan documented.
- Backup/restore tested on non-production data.

## Inputs

- `<VAULTWARDEN_ADMIN_TOKEN>`

## Commands

Run on: docker-host over SSH after gate approval.

```sh
mkdir -p /opt/stacks/vaultwarden/data
cd /opt/stacks/vaultwarden
cat > docker-compose.yml <<'COMPOSE'
services:
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: unless-stopped
    ports:
      - "8082:80"
    environment:
      SIGNUPS_ALLOWED: "false"
      ADMIN_TOKEN: "<VAULTWARDEN_ADMIN_TOKEN>"
    volumes:
      - ./data:/data
COMPOSE
docker compose config
```

Run on: docker-host over SSH only after confirming the gate.

```sh
docker compose up -d
```

## Explanation

The Compose file is draft installable, but a password vault has a higher bar:
HTTPS, recovery, backups, and admin-token handling must be settled first.

## Expected result

Vaultwarden is internal-only and not used for primary passwords until restore is tested.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/vaultwarden && docker compose ps
```

## Backup

Back up `/opt/stacks/vaultwarden/data` and test restore before storing real secrets.

## Failure recovery

If any gate is unresolved, stop the service:

Run on: docker-host over SSH.

```sh
cd /opt/stacks/vaultwarden
docker compose down
```

## Completion checklist

- [ ] Gate approved.
- [ ] HTTPS plan approved.
- [ ] Restore tested.
- [ ] Signups disabled.
