---
title: Docker-host Service Manuals
description: Install entrypoint for Tier 1, Tier 2, and Tier 3 docker-host services
tags: [install, docker-host, services]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: active
---

# Docker-host Service Manuals

All services in this directory run on `docker-host` unless the manual says a
decision gate must choose another host. Standard stack path:

```text
/opt/stacks/<service>/
```

Each service starts as `draft installable`. It becomes `deploy approved` only
after its backup, auth, exposure, monitoring, and rollback notes are complete.

## Tier 1

- [adguard-home.md](adguard-home.md)
- [immich.md](immich.md)
- [homepage.md](homepage.md)
- [dozzle.md](dozzle.md)

## Tier 2

- [paperless-ngx.md](paperless-ngx.md)
- [mealie.md](mealie.md)
- [ntfy.md](ntfy.md)
- [actual-budget.md](actual-budget.md)
- [scrypted.md](scrypted.md)

## Tier 3 / evaluate

- [vaultwarden.md](vaultwarden.md)
- [portainer.md](portainer.md)
- [watchtower-monitor-only.md](watchtower-monitor-only.md)
- [local-registry-mirror.md](local-registry-mirror.md)
- [node-red.md](node-red.md)
