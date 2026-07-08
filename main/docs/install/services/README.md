---
title: Docker-host Service Manuals
description: Install entrypoint for Tier 1, Tier 2, and Tier 3 docker-host services
tags: [install, docker-host, services]
created: 2026-05-24
modified: 2026-07-06
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

## Tier 1

- [adguard-home.md](adguard-home.md) — preflight-live DNS/ad-blocking baseline
- [immich.md](immich.md) — preflight-live with OMV media mount, real-library import still gated
- [homepage.md](homepage.md) — preflight-live service dashboard
- [dozzle.md](dozzle.md) — preflight-live log viewer with host-firewall scoping

## Tier 2

- [paperless-ngx.md](paperless-ngx.md) — candidate
- [mealie.md](mealie.md) — live; admin rotation and backup proof still open
- [grocy.md](grocy.md) — live; admin rotation, household model, and backup proof still open
- [obsidian-livesync.md](obsidian-livesync.md) — backend, CORS, local plugin install, and backup proof live; client wizard/second-device rollout still open
- [gardenkeeper.md](gardenkeeper.md) — live; local dumps proven, off-host copy still open
- [ntfy.md](ntfy.md) — preflight-live internal notifications
- [actual-budget.md](actual-budget.md) — candidate
- [scrypted.md](scrypted.md) — candidate
- [searxng.md](searxng.md) — preflight-live internal metasearch
- [whoogle.md](whoogle.md) — preflight-live internal search proxy

## Tier 3 / evaluate

- [vaultwarden.md](vaultwarden.md)
- [portainer.md](portainer.md)
- [watchtower-monitor-only.md](watchtower-monitor-only.md)
- [local-registry-mirror.md](local-registry-mirror.md)
- [node-red.md](node-red.md)
