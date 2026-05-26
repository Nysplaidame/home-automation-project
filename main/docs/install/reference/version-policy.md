---
title: Installation Version Policy
description: Pinning and latest-lookup rules for reproducible but maintainable rebuilds
tags: [install, versions, maintenance]
created: 2026-05-24
modified: 2026-05-24
type: reference
status: active
---

# Installation Version Policy

## Defaults

- Pin or record tested versions where a wrong version can break boot, networking,
  storage, or database compatibility.
- Use official latest lookup where fast-moving projects publish safe install
  artifacts and the existing guide already expects a lookup.
- Never hardcode stale point releases for HAOS, Debian ISO downloads, container
  images, or scripts unless a compatibility reason is documented.

## Pin or record tested version

| Area | Policy |
|---|---|
| Proxmox VE | Record installed major/minor version and repository family |
| OpenWrt router | Record image/build before applying configs |
| Debian VMs | Record Debian major release; current docs use Debian 13 where available |
| Docker Engine | Install from Docker official apt repo; record `docker --version` |
| Compose plugin | Install with Docker Engine; verify `docker compose version` |
| Databases | Avoid surprise major upgrades; note image tag before updates |
| Vaultwarden | Deploy only after security/backup gate; avoid blind latest updates |

## Use official latest lookup

| Area | Policy |
|---|---|
| HAOS image | Query latest official release before download |
| Immich stack files | Use official Immich release downloads, then record release used |
| Tailscale | Use official install script/repo and record `tailscale version` |
| AdGuard Home Docker image | Use supported Docker image and record image digest/tag |
| Tier 2/3 app drafts | Use documented upstream images but record tag before first live use |

## Official references used by this suite

- Docker Engine Debian install: <https://docs.docker.com/engine/install/debian/>
- Docker Compose documentation: <https://docs.docker.com/compose/>
- Tailscale subnet routers: <https://tailscale.com/docs/features/subnet-routers>
- AdGuard Home Docker wiki: <https://github.com/AdguardTeam/AdGuardHome/wiki/Docker>
- Immich install docs: <https://docs.immich.app/install/>
- OMV install docs: <https://www.openmediavault.org/install.html>
- Paperless-ngx setup: <https://docs.paperless-ngx.com/setup/>
- Mealie SQLite Docker Compose docs: <https://docs.mealie.io/documentation/getting-started/installation/sqlite/>
- ntfy install docs: <https://docs.ntfy.sh/install/>
- Actual Budget Docker docs: <https://actualbudget.org/docs/install/docker/>
- Scrypted install docs: <https://docs.scrypted.app/installation.html>
- Portainer Docker standalone docs: <https://docs.portainer.io/start/install-ce/server/docker>
- Docker registry mirror docs: <https://docs.docker.com/docker-hub/mirror/>
