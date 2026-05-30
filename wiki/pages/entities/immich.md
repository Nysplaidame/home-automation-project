---
title: "Immich"
category: entity
tags: [photos, gallery, docker, docker-host, omv]
created: 2026-05-23
updated: 2026-05-30
sources: [project-readme, project-todo]
status: active
---

# Immich

**Type:** service - photo/gallery application
**Status:** Live skeleton / pre-flight Tier 1 docker-host service
**Related:** [[entities/docker-host]], [[entities/openmediavault-nas]]

## Overview

Immich is the self-hosted photo/gallery service candidate. A skeleton deployment
runs on [[entities/docker-host]], not OMV. Do not import a real photo library
until [[entities/openmediavault-nas]] storage and backup/restore procedures are
ready.

## Key Properties

- Stack path: `/opt/stacks/immich/`
- Port: 2283/tcp
- DNS name: `immich.home.local`
- Storage: local placeholder only until OMV-backed `immich` share exists
- Gate: backup/security review before real media import

## Change Log

- 2026-05-30: Updated from planned to live skeleton; real imports remain blocked by OMV/backup readiness.
- 2026-05-23: Page created from self-hosted services roadmap.
