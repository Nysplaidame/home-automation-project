---
title: Diagram Library
description: Canonical architecture, install, service, storage, and VentSys diagrams
tags: [diagrams, architecture, install]
created: 2026-05-25
modified: 2026-09-10
type: index
status: active
---

# Diagram Library

These diagrams are canonical visual references for the current rebuild-first
architecture. Prefer these source Mermaid files over exported images so the
project can keep diagrams versioned and reviewable.

For symptom-led use, the [written diagnostic walkthroughs](../troubleshooting/diagnostic-walkthroughs.md)
and [troubleshooting reference](../troubleshooting/troubleshooting_reference.md)
link the relevant view at each investigation. These documents remain available
when the troubleshooting app or the rendered viewer is unreachable.

## Architecture and network

| Diagram | Purpose |
|---|---|
| [current-master-architecture.mermaid](network/current-master-architecture.mermaid) | Whole-system placement: router, Proxmox, VMs, docker-host, OMV, services, physical integrations |
| [vlan_architecture_clean.mermaid](network/vlan_architecture_clean.mermaid) | Eleven segments, subnets and host placement; access and cabling are separate views |
| [physical-port-and-cabling.mermaid](network/physical-port-and-cabling.mermaid) | Router attachments, Wi-Fi and the disconnected switch/camera baseline |
| [remote-access-flow.mermaid](network/remote-access-flow.mermaid) | Tailscale daily access, fixed Homepage mobile proxies, narrow admin host routes, WireGuard fallback |
| [dns-ntp-flow.mermaid](network/dns-ntp-flow.mermaid) | Router DNS/NTP authority, AdGuard Home, Quad9-preferred fallback, HA/ESPHome time |
| [security-access-flow.mermaid](network/security-access-flow.mermaid) | Firewall, ACL, local AI, host firewall, service-auth, and blocked-path intent |

## Install suite and services

| Diagram | Purpose |
|---|---|
| [install-sequence.mermaid](install/install-sequence.mermaid) | Fresh rebuild phase order and validation gates |
| [docker-host-service-placement.mermaid](infrastructure/docker-host-service-placement.mermaid) | Current docker-host stacks, explicit bridge allocations, fixed HTTPS proxy, Bambuddy exception, backup/logging placement |
| [proxmox-guests-and-backups.mermaid](infrastructure/proxmox-guests-and-backups.mermaid) | Production and rollback guests, shared iGPU paths, and OMV backup schedules |
| [storage-and-backup-flow.mermaid](storage/storage-and-backup-flow.mermaid) | OMV shares, HA/Frigate/Immich storage, backups, restore drills |

The live [Mermaid Viewer](../../apps/mermaid-viewer/README.md) is generated
from every `.mermaid` source in this directory. It provides search, deep links,
pan, zoom, fit, fullscreen, and source inspection at
`https://homepage.home.local:8195/` through Homepage, with the direct LAN
endpoint retained at `http://192.168.20.102:8092/`.

## Physical integration

| Diagram | Purpose |
|---|---|
| [ventsys-control-and-safety-flow.mermaid](ventsys/ventsys-control-and-safety-flow.mermaid) | VentSys control loop, MQTT/ESPHome path, airflow, safety behavior |
| [ventsys_wiring_reference.md](wiring-diagrams/ventsys_wiring_reference.md) | ESP32 wiring, GPIO assignments, power notes, first-power checklist |

## Non-canonical helper

| File | Purpose |
|---|---|
| [excalibrain.md](mind-map/excalibrain.md) | Obsidian/ExcaliBrain helper view; not part of the rebuild path |

## Layout and interpretation

The 2026-09-10 layout pass uses the September7 recorded system baseline; it
is not a new whole-system health audit. The master is a placement overview.
Use the dedicated network, access, service and storage views for detail.
Each view groups related items and limits connectors to its own purpose.

Teal denotes core services, purple storage, gold policy or acceptance gates,
and dashed boxes deferred, disconnected or rollback components; read each
label for its exact state. Solid lines can mean attachment or association,
so only directional labelled arrows imply a particular flow. Invisible
Mermaid `~~~` links control layout only. Abbreviated `.20.101`-style addresses
use the `192.168` prefix. Backup job success does not establish restore proof.

Keep explicit line breaks, adequate wrapping width and subgraph title margins
when extending a view. Avoid adding every relationship back into the master.
After edits, rebuild the viewer and run its browser verification script;
see [viewer verification](../../apps/mermaid-viewer/README.md#verification).
