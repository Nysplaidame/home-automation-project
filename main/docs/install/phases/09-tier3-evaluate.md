---
title: Phase 09 - Tier 3 Evaluate Apps
description: Risk-gated draft manuals for Vaultwarden, Portainer, Watchtower monitor-only, registry mirror, and Node-RED
tags: [install, docker-host, tier3, evaluate]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: active
---

# Phase 09 - Tier 3 Evaluate Apps

## Purpose

Document draft install paths for high-sensitivity or optional services without
silently approving them for live use.

## Runs on

docker-host over SSH unless a decision gate chooses a different host.

## Prerequisites

- Phase 05 complete.
- Decision gates reviewed.
- Backups and access controls understood.

## Inputs

- `<VAULTWARDEN_ADMIN_TOKEN>`
- `<PORTAINER_ADMIN_PASSWORD>`
- `<WATCHTOWER_HTTP_API_TOKEN>`
- `<NODE_RED_CREDENTIAL_SECRET>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/vaultwarden /opt/stacks/portainer /opt/stacks/watchtower /opt/stacks/registry-mirror /opt/stacks/node-red
```

Follow:

- [../services/vaultwarden.md](../services/vaultwarden.md)
- [../services/portainer.md](../services/portainer.md)
- [../services/watchtower-monitor-only.md](../services/watchtower-monitor-only.md)
- [../services/local-registry-mirror.md](../services/local-registry-mirror.md)
- [../services/node-red.md](../services/node-red.md)

## Explanation

These services can increase security, operational complexity, or blast radius.
The manuals are useful, but the decision gate decides when they are safe enough
to become live.

## Expected result

No Tier 3 service becomes live unless its gate is explicitly satisfied.

## Validation

Run on: docker-host over SSH.

```sh
for s in vaultwarden portainer watchtower registry-mirror node-red; do
  test -d "/opt/stacks/$s" && echo "$s directory exists"
done
```

## Failure recovery

Stop and remove the candidate stack before live use if its risk gate is not met:

Run on: docker-host over SSH.

```sh
cd /opt/stacks/<service>
docker compose down
```

## Completion checklist

- [ ] Tier 3 decision gates reviewed.
- [ ] Draft manuals exist.
- [ ] No Tier 3 service is marked live without approval.
