---
title: Scrypted Install Manual
description: Tier 2 camera platform draft install with placement gate
tags: [install, docker-host, scrypted, cameras]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# Scrypted Install Manual

## Purpose

Evaluate Scrypted for camera workflows. Upstream documentation prefers Proxmox
for dedicated Intel/AMD servers; Docker placement requires an explicit gate.

## Runs on

docker-host over SSH only if the Scrypted placement gate is accepted.

## Prerequisites

- docker-host phase complete.
- Scrypted decision gate reviewed.
- Camera network impact understood.

## Inputs

- `<SCRYPTED_ADMIN_PASSWORD>`

## Commands

Run on: docker-host over SSH after placement gate approval.

```sh
mkdir -p /opt/stacks/scrypted
cd /opt/stacks/scrypted
curl -fsSL https://docs.scrypted.app/install/docker-compose.yml -o docker-compose.yml
docker compose config
docker compose up -d
```

## Explanation

This is a draft Docker path. If Scrypted becomes core camera infrastructure,
revisit whether it should be a dedicated Proxmox workload instead.

## Expected result

Scrypted UI loads on its documented local HTTPS port, commonly 10443.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/scrypted && docker compose ps
ss -tlnp | grep -E '10443|11080' || true
```

## Backup

Back up Scrypted config/data before pairing real cameras.

## Failure recovery

If networking or discovery fails, stop the Docker draft and reassess Proxmox
placement before punching broader firewall holes.

## Completion checklist

- [ ] Placement gate accepted.
- [ ] UI loads.
- [ ] Camera access remains narrow and documented.
