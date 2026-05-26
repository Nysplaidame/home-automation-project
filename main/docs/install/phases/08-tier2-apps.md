---
title: Phase 08 - Tier 2 Apps
description: Draft installable manuals for Paperless-ngx, Mealie, ntfy, Actual Budget, and Scrypted
tags: [install, docker-host, tier2]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: active
---

# Phase 08 - Tier 2 Apps

## Purpose

Provide full draft install paths for useful next services while keeping deployment
approval separate from writing commands.

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
- `<NTFY_ADMIN_PASSWORD>`
- `<ACTUAL_PASSWORD>`
- `<SCRYPTED_ADMIN_PASSWORD>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/paperless-ngx /opt/stacks/mealie /opt/stacks/ntfy /opt/stacks/actual-budget /opt/stacks/scrypted
```

Follow:

- [../services/paperless-ngx.md](../services/paperless-ngx.md)
- [../services/mealie.md](../services/mealie.md)
- [../services/ntfy.md](../services/ntfy.md)
- [../services/actual-budget.md](../services/actual-budget.md)
- [../services/scrypted.md](../services/scrypted.md)

## Explanation

Tier 2 services are plausible household services, but each still needs backup,
auth, exposure, and resource review before becoming live.

## Expected result

Each Tier 2 service can be installed as an internal draft and has a clear gate
before household use.

## Validation

Run on: docker-host over SSH.

```sh
for s in paperless-ngx mealie ntfy actual-budget scrypted; do
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
