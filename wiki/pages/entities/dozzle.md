---
title: "Dozzle"
category: entity
tags: [logs, docker, docker-host]
created: 2026-05-23
updated: 2026-05-23
sources: [project-readme, project-todo]
status: active
---

# Dozzle

**Type:** service - Docker log viewer
**Status:** Planned Tier 1 docker-host service
**Related:** [[entities/docker-host]]

## Overview

Dozzle is the planned internal Docker log viewer for [[entities/docker-host]].
It should stay admin/internal only and must not be exposed to Guest or DMZ.

## Key Properties

- Stack path: `/opt/stacks/dozzle/`
- Planned port: 8081/tcp
- DNS name: `dozzle.home.local`

## Change Log

- 2026-05-23: Page created from self-hosted services roadmap.
