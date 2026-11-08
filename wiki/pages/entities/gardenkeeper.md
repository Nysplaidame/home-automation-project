---
title: "GardenKeeper"
category: entity
tags: [garden, service, docker-host, recovery]
created: 2026-09-16
updated: 2026-10-04
sources: [project-todo]
status: active
---

# GardenKeeper

**Type:** service  
**Status:** operational  
**Related:** [[docker-host]], [[openmediavault-nas]], [[home-assistant]]

## Overview

GardenKeeper is the internal garden-care service on [[docker-host]]. It uses
PostgreSQL for application state, Redis for rebuildable worker state, a FastAPI
API, a worker and a static web application. The canonical operational contract
is [[../../../main/docs/install/services/gardenkeeper]].

## Key Properties

- Stack: `/opt/stacks/gardenkeeper/` on docker-host; API port `8090`, web port
  `8091`.
- Database recovery: the local checked PostgreSQL dump timer feeds the existing
  off-host Docker-host app-data backup on [[openmediavault-nas]].
- Journal photos: a database `photo_url` points to separately stored image
  bytes. The API bind-mounts root-only
  `/opt/stacks/gardenkeeper/journal-media` at `/data/journal-media`; it is an
  explicit app-data-backup inventory item.

## Notes & Observations

- 2026-09-16: the prior live API had no media mount and its effective media
  directory did not exist. No user uploads were present, so no historical files
  needed preservation.
- A disposable, internal-only rehearsal restored the checked 2026-09-16 dump
  with all 29 migration records and the current API image. A synthetic,
  authenticated PNG survived API recreation through the mounted media path with
  an identical SHA-256. Production workers and external integrations were not
  started in that rehearsal.
- The production API was then recreated alone with the persistent media mount;
  `/health` and `/ready` passed, while the worker and web container identities
  were unchanged.

## Open Questions

- [ ] Exercise a complete representative journal-photo workflow only when a
  test image and its removal are explicitly approved.
- [ ] Include the media directory in the next dated OMV app-data backup and
  validate a recovery run once non-empty media exists.

## Change Log

- 2026-09-16: Added the persistent journal-media and recovery boundary from
  the canonical GardenKeeper manual.

- 2026-10-03: canonical `main/tools/gardenkeeper-recovery/README.md` records
  a passed synthetic PostgreSQL dump/restore with separately copied media,
  journal URL/hash verification, queued notification dispatch and worker-restart
  calendar cleanup against loopback doubles. No production checkpoint or real
  Nextcloud/ntfy acceptance; open production recovery questions remain.

- 2026-10-04: [[entities/home-operations-workbench]] supports a bounded offline
  pending-task selection using the verified live API schema. No task records
  were fetched and no GardenKeeper runtime or data changed; local import tests
  do not certify live household integration.
