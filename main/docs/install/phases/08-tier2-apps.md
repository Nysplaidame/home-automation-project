---
title: Phase 08 - Tier 2 Apps
description: Tier 2 deployment manuals and remaining candidates
tags: [install, docker-host, tier2]
created: 2026-05-24
modified: 2026-07-06
type: install-guide
status: active
---

# Phase 08 - Tier 2 Apps

## Purpose

Provide install paths for useful household services while keeping approval
separate for candidates that are not already live.

## Runs on

docker-host over SSH unless a service manual says a decision gate may move it.

## Prerequisites

- Phase 05 complete.
- Tier 1 monitoring/logging preferably live.
- Relevant secrets created.

## Inputs

- `<PAPERLESS_ADMIN_USER>`
- `<PAPERLESS_ADMIN_PASSWORD>`
- `<MEALIE_ADMIN_EMAIL>`
- `<MEALIE_ADMIN_PASSWORD>`
- `<GROCY_ADMIN_PASSWORD>`
- `<OBSIDIAN_LIVESYNC_ADMIN_USER>`
- `<OBSIDIAN_LIVESYNC_ADMIN_PASSWORD>`
- `<NTFY_ADMIN_PASSWORD>`
- `<ACTUAL_PASSWORD>`
- `<SCRYPTED_ADMIN_PASSWORD>`
- `<SEARXNG_SECRET_KEY>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/paperless-ngx /opt/stacks/mealie /opt/stacks/grocy /opt/stacks/obsidian-livesync /opt/stacks/ntfy /opt/stacks/actual-budget /opt/stacks/scrypted /opt/stacks/searxng /opt/stacks/whoogle
```

Follow:

- [../services/paperless-ngx.md](../services/paperless-ngx.md)
- [../services/mealie.md](../services/mealie.md)
- [../services/grocy.md](../services/grocy.md)
- [../services/obsidian-livesync.md](../services/obsidian-livesync.md)
- [../services/ntfy.md](../services/ntfy.md)
- [../services/actual-budget.md](../services/actual-budget.md)
- [../services/scrypted.md](../services/scrypted.md)
- [../services/searxng.md](../services/searxng.md)
- [../services/whoogle.md](../services/whoogle.md)

## Explanation

Mealie, Grocy, Obsidian LiveSync/CouchDB, ntfy, SearXNG and Whoogle are live
as internal services. Grocy has the base household model seeded and backed up.
Obsidian LiveSync has backend, CORS, local plugin install, and backup proof
complete, but still needs the Obsidian client wizard and second-device rollout.
Remaining Tier 2 candidates still need backup, authentication, exposure and
resource review before deployment.

## Expected result

Each Tier 2 service can be installed as an internal draft and has a clear gate
before household use.

## Validation

Run on: docker-host over SSH.

```sh
for s in paperless-ngx mealie grocy obsidian-livesync ntfy actual-budget scrypted searxng whoogle; do
  test -d "/opt/stacks/$s" && echo "$s directory exists"
done
```

## Failure recovery

Stop the individual stack with `docker compose down` from its directory. Preserve
volumes until you have confirmed whether data must be kept or deleted.

## Completion checklist

- [ ] Every Tier 2 service has a stack directory.
- [ ] Every Tier 2 service has a draft install manual.
- [ ] Every Tier 2 service has a backup/auth/exposure note.
- [ ] Live household apps have client rollout and app-data backup proof before
  being marked household-complete.
