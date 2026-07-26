---
title: Vaultwarden Install Manual
description: Tier 3 password vault candidate with strict decision gate
tags: [install, docker-host, vaultwarden, tier3]
created: 2026-05-24
modified: 2026-07-26
type: install-guide
status: planned-not-installable
---

# Vaultwarden Install Manual

## Purpose

Evaluate Vaultwarden as a self-hosted password vault. This is high sensitivity
and must not become live until the gate is approved.

## Runs on

docker-host over SSH at `192.168.20.102` after gate approval.

## Approved design

Follow the implementation design and gates in
[[docs/procedures/household-services-implementation-plan|Household Services
Implementation Plan]]. Vaultwarden belongs on docker-host with persistent data
under `/opt/stacks/vaultwarden/data`, a dedicated local-CA HTTPS hostname, and a
fixed TLS-proxy route. It is not embeddable in Homepage and its raw HTTP port
must not be reachable outside Docker.

## Prerequisites

- Dedicated HTTPS hostname, local DNS and mobile certificate trust proven.
- Fixed proxy and source-scoped firewall design approved.
- Backup and isolated restore proof completed on non-production data.
- Household 2FA, recovery-code storage and emergency-access policy approved.

## Inputs

- `<VAULTWARDEN_IMAGE_TAG>`
- `<VAULTWARDEN_ADMIN_TOKEN_HASH>`

## Commands

Run on: docker-host over SSH after gate approval.

```sh
mkdir -p /opt/stacks/vaultwarden/data
cd /opt/stacks/vaultwarden
cat > docker-compose.yml <<'COMPOSE'
services:
  vaultwarden:
    image: vaultwarden/server:<VAULTWARDEN_IMAGE_TAG>
    container_name: vaultwarden
    restart: unless-stopped
    # Bind only to an internal/loopback endpoint; fixed HTTPS proxy owns access.
    ports:
      - "127.0.0.1:8082:80"
    environment:
      DOMAIN: "https://vault.home.local"
      SIGNUPS_ALLOWED: "false"
      ADMIN_TOKEN: "<VAULTWARDEN_ADMIN_TOKEN_HASH>"
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

This is a template shape, not an authorisation to deploy. Do not use `latest`
without a scheduled review/pinning policy, and do not populate the token until
the implementation gates are approved.

## Expected result

Vaultwarden is internal-only and not used for primary passwords until restore is tested.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/vaultwarden && docker compose ps
```

## Backup

Create a SQLite-consistent Vaultwarden backup plus copies of attachments, sends
and keys, then send dated generations to OMV `backups/docker-host`. Test an
isolated restore before storing real secrets; see the implementation plan.

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
