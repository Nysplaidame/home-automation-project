---
title: "Immich"
category: entity
tags: [photos, gallery, docker, docker-host, omv]
created: 2026-05-23
updated: 2026-08-25
sources: [project-readme, project-todo]
status: active
---

# Immich

**Type:** service - photo/gallery application
**Status:** Live Tier 1 docker-host service with OMV-backed media storage
**Related:** [[entities/docker-host]], [[entities/openmediavault-nas]]

## Overview

Immich is the live self-hosted photo/gallery service on
[[entities/docker-host]]. Application/database state stays on VM 103 while the
approved media library is mounted from [[entities/openmediavault-nas]].

## Key Properties

- Stack path: `/opt/stacks/immich/`
- Port: 2283/tcp
- DNS name: `immich.home.local`
- Storage: uploads/library on the OMV-backed Immich mount; PostgreSQL state is
  local to the stack and covered by protected backup procedures
- Current image remained on v2.7.5 during the 2026-08-21 network-only
  recreation; staged v3.1.0 images were deliberately not promoted
- Immich curated-album exporter remains a separately gated follow-up

## Change Log

- 2026-08-25: Replaced the obsolete skeleton/local-placeholder claim with the
  live OMV-backed architecture and recorded the deliberate version hold.
- 2026-05-30: Updated from planned to live skeleton; real imports remain blocked by OMV/backup readiness.
- 2026-05-23: Page created from self-hosted services roadmap.
