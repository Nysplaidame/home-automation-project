---
title: Rebuild State Matrix
description: Standard lifecycle states for every host, service, and phase
tags: [install, rebuild, state]
created: 2026-05-24
modified: 2026-08-09
type: reference
status: active
---

# Rebuild State Matrix

| State | Meaning | Required proof |
|---|---|---|
| Blank | Hardware or VM exists but no project configuration is applied | Inventory record only |
| Prepared | OS/network baseline is ready, backups or restore point exist | IP reachable, admin access works, restore path known |
| Installed | Packages or services are installed | Version command, package list, or container image present |
| Configured | Project-specific settings are applied | Config file, UI setting, or Compose stack present |
| Validated | The component works in isolation and over intended network paths | Validation commands pass |
| Live | The component is depended on by another live component or user workflow | Monitoring, backup, and rollback notes exist |

No service may be considered `live` until it has:

- a backup or restore note,
- an access-control note,
- a monitoring or health-check note,
- a troubleshooting entry,
- and a recorded owner decision for any unresolved risk gate.

## Phase-to-state map

Each phase advances only the component it owns. A checked phase-documentation
task does not advance live infrastructure state.

| Phase | Owned component | Entry state | Maximum state proved inside phase | Additional proof required for `Live` |
|---|---|---|---|---|
| 00 | Operator workspace, inventory, addressing, secret names | Blank | Prepared | Repository/tool checks, complete inventory and recovery contacts remain current |
| 01 | OpenWrt router/network policy | Blank or clean firmware | Validated | Clean lint/full compile, live positive/denial tests, snapshot and `lan5` recovery proof, monitoring |
| 02 | Proxmox host and empty guest shells | Blank host | Validated | Storage/management monitoring, backup, local-console rollback, and dependent guest proof |
| 03 | Home Assistant VM/appliance | Prepared VM shell | Validated | HTTPS/MQTT/Companion workflows, current backup plus isolated restore, monitoring, approved integrations |
| 04 | Frigate CT and NVR service | Prepared CT | Validated | Camera-by-camera privacy/stream tests, OMV recording proof, auth/firewall denial, backup/restore and monitoring |
| 05 | docker-host VM runtime/firewall/Tailscale | Prepared VM | Validated | Restart-persistent firewall, exact route approval/ACL denials, backup mount, monitoring and at least one dependent workflow |
| 05A | CT 114 local AI and voice endpoints | Blank or restored CT | Validated | Model/image digests, concurrent-load performance, harmless HA workflow, denial tests, reboot/offline proof and isolated restore |
| 06 | OMV OS, filesystems and exports | Blank OS or preserved data | Validated | SMART/array alerting, consumer write/deny tests, scheduled backups and isolated restore proofs |
| 07 | AdGuard, Immich, Homepage and Dozzle | Blank per stack | Validated per service | Each service's backup/restore, source denial, monitor outage/recovery and rollback evidence |
| 08 | Tier 2 services | Blank, live-existing or candidate per service | Validated only for approved services | Per-service gate, backup/restore, monitoring, access/auth and rollback evidence; candidates may remain Prepared |
| 09 | Tier 3/admin-risk candidates | Parked by default | Validated only after explicit approval | Security/owner gate plus service-specific backup, denial, monitoring and rollback evidence; no automatic graduation |
| 10 | Backup, monitoring and maintenance controls | Configured consumers/services | Validated | Successful schedules, rotating isolated restores, alert outage/recovery and maintenance-window evidence |
| 11 | Each camera, printer, ESPHome/VentSys device | Blank physical item | Validated per device | Safe bench/first-flash proof, identity reservation, integration, monitoring and harmless fail-safe test; physical acceptance is item-by-item |
| 12 | Whole-system acceptance record | Prior components at explicit states | Validated or Blocked | All completion checks and evidence rows pass; only then may the recorded component advance to Live |

## How to use the map

1. Record the component, not merely the phase number. Phase 08/09/11 can contain
   components in different states at the same time.
2. Attach the required proof named in the phase manual and Phase 12 acceptance
   row.
3. If any proof is missing, retain the last proven state or mark the row
   `Blocked`; never infer `Live` from a running process alone.
4. A restored component returns at most to `Configured` until isolation,
   intended-network, monitoring, and user-workflow validation are repeated.
