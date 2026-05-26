---
title: Phase 07 - Tier 1 Apps
description: AdGuard Home, Immich, Homepage, and Dozzle on docker-host
tags: [install, docker-host, tier1]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: active
---

# Phase 07 - Tier 1 Apps

## Purpose

Deploy the core near-term docker-host services: AdGuard Home, Immich, Homepage,
and Dozzle. These services are internal by default.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- Phase 05 complete.
- Phase 06 complete before Immich bulk media import.
- DNS and firewall policy from router phase validated.

## Inputs

- `<ADGUARD_ADMIN_PASSWORD>`
- `<IMMICH_ADMIN_EMAIL>`
- `<IMMICH_ADMIN_PASSWORD>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/adguard-home /opt/stacks/immich /opt/stacks/homepage /opt/stacks/dozzle
ls -ld /opt/stacks/*
```

Then follow each service manual:

- [../services/adguard-home.md](../services/adguard-home.md)
- [../services/immich.md](../services/immich.md)
- [../services/homepage.md](../services/homepage.md)
- [../services/dozzle.md](../services/dozzle.md)

## Explanation

The stack directories enforce one consistent operational pattern and keep
container state away from random home directories.

## Expected result

- AdGuard answers DNS and the router can fall back if it is down.
- Immich UI loads and does not depend on VM disk for media storage long-term.
- Homepage shows internal service links.
- Dozzle can view Docker logs and remains admin/internal only.

## Validation

Run on: docker-host over SSH.

```sh
for s in adguard-home immich homepage dozzle; do
  echo "== $s =="
  cd "/opt/stacks/$s" && docker compose ps
done
```

## Failure recovery

- If a service fails, stay in that service directory and run
  `docker compose config` before restarting.
- If a port conflicts, check `ss -tlnp` before changing the service port.
- If remote access fails but LAN works, check Tailscale ACL/UFW, not broad VLAN routes.

## Completion checklist

- [ ] Each Tier 1 service has a stack directory.
- [ ] Each stack passes `docker compose config`.
- [ ] Each service has a backup note.
- [ ] Each service has a troubleshooting entry.
