---
title: Docker-host Service Manuals
description: Install entrypoint for Tier 1, Tier 2, and Tier 3 docker-host services
tags: [install, docker-host, services]
created: 2026-05-24
modified: 2026-08-24
type: install-guide
status: active
---

# Docker-host Service Manuals

All services in this directory run on `docker-host` unless the manual says a
decision gate must choose another host. Standard stack path:

```text
/opt/stacks/<service>/
```

Each new service starts as `draft installable`. It becomes `deploy approved`
only after its backup, auth, exposure, monitoring, and rollback notes are
complete. Several services below are already live or preflight-live; their
manuals record the remaining setup gaps instead of pretending they are still
only candidates.

## Promotion boundary: installed is not live

Every rebuild must have a deliberate pause between preparing/validating a
service and allowing household data, clients, firewall/DNS dependencies, or
automatic schedules to rely on it. At that pause, `docker compose config` or
the equivalent configuration check must pass, secrets must remain outside Git,
and the operator must be able to leave the service absent or stopped without
damaging an existing service.

| Manual | Last safe stop before live | Evidence required to promote |
|---|---|---|
| AdGuard Home | Leave Compose down before binding DNS or changing router resolver policy. | Local canary resolution, source-scoped listeners, fallback resolver, monitoring and rollback. |
| Immich | Leave Compose down before mounting/importing the real library. | Database/media backup, OMV mount identity, health, mobile login and isolated restore. |
| Homepage | Leave Compose down before users or proxy routes depend on it. | Config validation, trusted HTTPS, source-scoped proxies, health and rollback. |
| Dozzle | Leave Compose down before granting the read-only Docker socket. | Socket risk accepted, narrow exposure, authentication decision and clean removal. |
| Mermaid Viewer | Stop after the static build and Compose validation. | Local assets only, HTTP health, explicit network/firewall and previous-image rollback. |
| Immich curated exporter | Stop after dry-run; keep its timer disabled. | One allow-listed album, manifest/review queue, no-delete proof, Jellyfin scan and backup. |
| Paperless-ngx | Stop before first `up` and before importing any real document. | Auth/HTTPS, OCR/ingest policy, exporter backup, isolated import/restore and rollback. |
| Mealie | Stop after Compose/image/port validation. | Named admin, signup denial, UI backup, recipe export, isolated restore and rollback. |
| Grocy | Stop after Compose/image/port validation. | Default-login denial, disposable stock workflow, consistent backup, isolated restore and rollback. |
| Obsidian LiveSync | Backend may run, but stop before **Restart and Initialise Server** on the first client. | Clean pushed canonical vault, off-host backups, exclusions, HTTPS/CORS and two-device round trip. |
| GardenKeeper | Leave Compose down before HA/LLM consumers or real garden state use it. | Database dump, API/UI health, bounded auth, off-host backup and restore. |
| ntfy | Leave Compose down before HA/Kuma/Grafana publish or phones subscribe. | Named auth/topic policy, anonymous denial, delivery, SQLite-consistent backup and rollback. |
| SearXNG | Leave Compose down before agents receive its endpoint. | Instance secret, bounded API, source denial, egress/rate policy and rollback. |
| Whoogle | Leave Compose down before Homepage/agents depend on it. | Narrow exposure, abuse/egress policy, health and rollback. |
| Gridfinity Layout Tool | Stop after build/Compose validation. | Stateless health, browser export/download and clean container removal. |
| Transfer Portal | Keep the candidate portal disabled before creating persistent bind units or a real job. | Exact source/destination, preview, case-collision check, audit log, bounded copy and unit rollback. |
| Actual Budget | Stop before first `up` and before importing financial data. | Loopback raw listener, HTTPS, auth/E2EE recovery, export, isolated restore and rollback. |
| Scrypted | Stop before running an installer or granting camera/iGPU/storage access. | Placement/non-overlap decision, dedicated boundaries, auth, backup and Frigate/HA rollback. |
| Vaultwarden | Stop before owner creation or importing real credentials. | HTTPS-only access, backup/restore, 2FA/recovery/emergency access and route rollback. |
| Portainer | Stop before granting the Docker socket or starting the admin UI. | Root-equivalent risk accepted, loopback/private HTTPS, named admin, backup and full removal proof. |
| Watchtower monitor-only | Stop before first `up`. | Monitor-only flags, notification proof, no update actions and rollback of any touched target. |
| Local registry mirror | Stop before changing Docker daemon config or a client pull path. | Capacity/TLS policy, public-only upstream, one-client canary and direct-pull rollback. |
| Node-RED | Stop before first `up`; later stop again before promoting any flow. | Authenticated editor, safe mode, credential restore, non-safety-critical flow test and explicit promotion. |

If the required evidence is incomplete, the accepted outcome is to leave the
service stopped, absent, or parked and continue only with independent phases.

## Tier 1

- [adguard-home.md](adguard-home.md) — preflight-live DNS/ad-blocking baseline
- [immich.md](immich.md) — preflight-live with OMV media mount, real-library import still gated
- [immich-curated-exporter.md](immich-curated-exporter.md) — staged, allow-listed one-way album export to Jellyfin; live test-album proof still required
- [homepage.md](homepage.md) — preflight-live service dashboard
- [dozzle.md](dozzle.md) — preflight-live log viewer with host-firewall scoping
- [mermaid-viewer.md](mermaid-viewer.md) — live internal Mermaid diagram browser

## Tier 2

- [paperless-ngx.md](paperless-ngx.md) — candidate
- [mealie.md](mealie.md) — live; admin/export and application-level restore acceptance remain
- [grocy.md](grocy.md) — live; admin and disposable pilot workflow remain
- [obsidian-livesync.md](obsidian-livesync.md) — backend, CORS, local plugin install, and backup proof live; client wizard/second-device rollout still open
- [gardenkeeper.md](gardenkeeper.md) — live; local dumps proven, off-host copy still open
- [ntfy.md](ntfy.md) — preflight-live internal notifications
- [actual-budget.md](actual-budget.md) — candidate
- [scrypted.md](scrypted.md) — candidate
- [searxng.md](searxng.md) — preflight-live internal metasearch
- [whoogle.md](whoogle.md) — preflight-live internal search proxy

- [gridfinity-layout-tool.md](gridfinity-layout-tool.md) — live local Gridfinity planner

## Related OMV-native service

- [transferportal.md](transferportal.md) — live native OMV transfer service;
  new portal mappings remain preview-first and decision-gated

## Tier 3 / evaluate

- [vaultwarden.md](vaultwarden.md)
- [portainer.md](portainer.md)
- [watchtower-monitor-only.md](watchtower-monitor-only.md)
- [local-registry-mirror.md](local-registry-mirror.md)
- [node-red.md](node-red.md)
