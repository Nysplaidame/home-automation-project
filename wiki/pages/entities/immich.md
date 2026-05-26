---
title: "Immich"
category: entity
tags: [photos, gallery, docker, docker-host, omv]
created: 2026-05-23
updated: 2026-05-23
sources: [project-readme, project-todo]
status: active
---

# Immich

**Type:** service - photo/gallery application
**Status:** Planned Tier 1 docker-host service
**Related:** [[entities/docker-host]], [[entities/openmediavault-nas]]

## Overview

Immich is the planned self-hosted photo/gallery service. It runs on
[[entities/docker-host]], not OMV. Bulk media storage should be backed by
[[entities/openmediavault-nas]].

## Key Properties

- Stack path: `/opt/stacks/immich/`
- Planned port: 2283/tcp
- DNS name: `immich.home.local`
- Storage: OMV-backed `immich` share, plus database backup plan before import

## Change Log

- 2026-05-23: Page created from self-hosted services roadmap.
