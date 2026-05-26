---
title: "Raspberry Pi NAS (Deprecated Plan)"
category: entity
tags: [deprecated, nas, raspberry-pi, storage]
created: 2026-04-07
updated: 2026-05-23
sources: [project-readme, hardware-bom, troubleshooting-reference]
status: stable
---

# Raspberry Pi NAS (Deprecated Plan)

**Type:** deprecated storage plan
**Status:** Superseded by [[entities/openmediavault-nas]]
**Related:** [[entities/openmediavault-nas]], [[entities/frigate]], [[entities/home-assistant]], [[entities/proxmox]]

## Overview

This page preserves the older Raspberry Pi NAS plan for historical context. It
is no longer the active storage direction. The current canonical plan uses
OpenMediaVault at `192.168.40.50` on VLAN 40; see [[entities/openmediavault-nas]].

## Current Replacement

- Platform: OpenMediaVault
- IP: `192.168.40.50`
- VLAN: 40 (Storage)
- Setup guide: `main/scripts/setup/nas/omv_nas_setup_guide.md`
- Remote access: host route `192.168.40.50/32`, not broad VLAN access

## Change Log

- 2026-05-23: Marked deprecated; active storage plan moved to [[entities/openmediavault-nas]].
- 2026-04-07: Page created from project-wide ingest.
