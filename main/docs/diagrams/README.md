---
title: Diagram Library
description: Canonical architecture, install, service, storage, and VentSys diagrams
tags: [diagrams, architecture, install]
created: 2026-05-25
modified: 2026-05-25
type: index
status: active
---

# Diagram Library

These diagrams are canonical visual references for the current rebuild-first
architecture. Prefer these source Mermaid files over exported images so the
project can keep diagrams versioned and reviewable.

## Architecture and network

| Diagram | Purpose |
|---|---|
| [current-master-architecture.mermaid](network/current-master-architecture.mermaid) | Whole-system placement: router, Proxmox, VMs, docker-host, OMV, services, physical integrations |
| [vlan_architecture_clean.mermaid](network/vlan_architecture_clean.mermaid) | VLANs, subnets, router role, physical ports, local AI, remote-access placement |
| [remote-access-flow.mermaid](network/remote-access-flow.mermaid) | Tailscale daily access, docker-host host routes, WireGuard fallback |
| [dns-ntp-flow.mermaid](network/dns-ntp-flow.mermaid) | Router DNS/NTP authority, AdGuard Home, Quad9-preferred fallback, HA/ESPHome time |
| [security-access-flow.mermaid](network/security-access-flow.mermaid) | Firewall, ACL, local AI, host firewall, service-auth, and blocked-path intent |

## Install suite and services

| Diagram | Purpose |
|---|---|
| [install-sequence.mermaid](install/install-sequence.mermaid) | Fresh rebuild phase order and validation gates |
| [docker-host-service-placement.mermaid](infrastructure/docker-host-service-placement.mermaid) | docker-host stack layout, Tier 1-3 services, future query-app boundary, backup/logging placement |
| [storage-and-backup-flow.mermaid](storage/storage-and-backup-flow.mermaid) | OMV shares, HA/Frigate/Immich storage, backups, restore drills |

## Physical integration

| Diagram | Purpose |
|---|---|
| [ventsys-control-and-safety-flow.mermaid](ventsys/ventsys-control-and-safety-flow.mermaid) | VentSys control loop, MQTT/ESPHome path, airflow, safety behavior |
| [ventsys_wiring_reference.md](wiring-diagrams/ventsys_wiring_reference.md) | ESP32 wiring, GPIO assignments, power notes, first-power checklist |

## Non-canonical helper

| File | Purpose |
|---|---|
| [excalibrain.md](mind-map/excalibrain.md) | Obsidian/ExcaliBrain helper view; not part of the rebuild path |
