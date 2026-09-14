---
title: Installation Version Policy
description: Pinning and latest-lookup rules for reproducible but maintainable rebuilds
tags: [install, versions, maintenance]
created: 2026-05-24
modified: 2026-08-24
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

## Fresh-rebuild version gate

An exact tag/digest in this repository is the tested recovery anchor, not an
instruction to upgrade silently or to substitute `latest`. Immediately before
deploying a volatile component:

1. open its official release notes or installation page;
2. compare the documented tested version with the current supported stable
   version and its database/config migration notes;
3. choose either the tested pin or a separately reviewed upgrade candidate;
4. record the selected tag, immutable digest, lookup date and rollback pair in
   the maintenance log; and
5. take the service-specific backup and prove its isolated restore before a
   major-version or database-format change.

Do not mix a newer migrated data directory with an older rollback image unless
the upstream project explicitly supports that downgrade.

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
| Local AI model alias | Keep `home-assistant-llm` stable, but record the underlying GGUF source, quantization and llama.cpp image digest before live use |

## Use official latest lookup

| Area | Policy |
|---|---|
| HAOS image | Query latest official release before download |
| Immich stack files | Use official Immich release downloads, then record release used |
| Tailscale | Use official install script/repo and record `tailscale version` |
| AdGuard Home Docker image | Use supported Docker image and record image digest/tag |
| llama.cpp / Open WebUI / Wyoming images | Use documented upstream images, verify current tags before deploy, and record image digests after first live use |
| Tier 2/3 app drafts | Use documented upstream images but record tag before first live use |

## Volatile manuals requiring an official lookup

| Component/manual | Official check immediately before deployment |
|---|---|
| OpenWrt/router-deploy | Confirm router model/revision, installed OpenWrt build and package feed compatibility; never flash a different hardware image. |
| Proxmox and Debian guests | Confirm supported major release, repository family and upgrade notes before changing the tested base. |
| HAOS and Home Assistant add-ons | Use the current official HAOS image and read breaking-change notes before restoring or upgrading. |
| Frigate | Review Frigate release notes, detector/schema changes and the tested iGPU/OpenVINO path before changing the pinned image. |
| Immich | Use the official release files only; review every intervening release and database migration before changing the server/ML pair. |
| Mealie and Grocy | Compare the pinned images with official stable releases; take application/stopped-data backups before schema changes. |
| Obsidian Self-hosted LiveSync | Review plugin and CouchDB compatibility; keep all clients on a reviewed compatible plugin version during rollout. |
| SearXNG, Whoogle and ntfy | Review upstream image/release notes and retain the tested digest plus config/data rollback. |
| Paperless-ngx, Actual Budget and Scrypted | Re-run their decision gate against current official deployment guidance before first install. |
| Vaultwarden, Portainer, Watchtower, registry mirror and Node-RED | Re-run security/backup gates and use current official documentation; never convert a draft into `latest`-tracked production. |
| llama.cpp, Open WebUI and Wyoming services | Record image/model digests and repeat performance/HA compatibility tests after updates. |

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
- llama.cpp Docker images: <https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md>
- Open WebUI docs: <https://docs.openwebui.com/>
- Wyoming Whisper image: <https://hub.docker.com/r/rhasspy/wyoming-whisper>
- Wyoming Piper image: <https://hub.docker.com/r/rhasspy/wyoming-piper>
