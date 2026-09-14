---
title: Router and Switch Physical Port Layout
description: Confirmed and reserved physical cabling map for the router, GS1900 switch, OMV, and CCTV rollout
tags: [network, cabling, ports, switch, cctv]
created: 2026-07-10
modified: 2026-09-10
type: reference
status: active
---

# Router and Switch Physical Port Layout

Canonical visual: [[../diagrams/network/physical-port-and-cabling|Physical port and cabling diagram]].

This is the physical layer reference: it identifies physical devices, what
plugs into each port, which VLAN that cable carries, and whether the assignment
is confirmed live or reserved for the CCTV expansion. It does not authorize
router or switch changes. Canonical device names are in
[[canonical-names|Canonical Names]].

## Physical Inventory

Owner correction, 2026-09-04: OMV connects directly to router `lan4`.
The August map incorrectly restored the older switch-port-8 attachment.
LAN2 is now Hive access on VLAN55. The switch/cameras remain deliberately
disconnected after installation; table entries describe assigned cabling.

| Canonical name | Physical device | Connectivity |
|---|---|---|
| `router` | GL.iNet GL-MT6000 | WAN upstream; CAT6 to `proxmox` and `gs1900-switch`; Wi-Fi AP; unplugged recovery access ports |
| `proxmox` | MINISFORUM M1 Pro-125H mini PC | Router `lan1` tagged trunk; hosts VMs/CTs |
| `gs1900-switch` | Zyxel GS1900-8HP | Router `lan3` tagged trunk; three PoE cameras; port 8 reserved VLAN 40 access |
| `omvnas` | OMV NAS hardware | Router `lan4` / VLAN 40 |
| `cam-01-annke-c500` | ANNKE C500 | GS1900 port 2 / VLAN 30 / PoE |
| `cam-02-gate-annke-c500` | ANNKE C500 gate camera | GS1900 port 4 / VLAN 30 / PoE |
| `cam-03-patio-annke-c500` | ANNKE C500 patio camera | GS1900 port 3 / VLAN 30 / PoE |
| `p1s` | Bambu Lab P1S | HomePrinters Wi-Fi / VLAN 35 |
| `operator-mobile` | Android phone | Wi-Fi locally; Tailscale off-site |

## Router: GL.iNet GL-MT6000

| Router port | Cable destination | VLAN posture | State |
|---|---|---|---|
| WAN socket (`eth1`; logical interface `wan`) | Openreach ONT | Zen PPPoE; no WAN VLAN tag | Owner-confirmed working 2026-09-04 |
| `lan1` | MINISFORUM Proxmox host | Tagged trunk: 10, 20, 30, 35, 40, 50, 60, 70 | Live |
| `lan2` | Hive hub | Untagged cloud IoT VLAN 55; WAN only | 100 Mbps full duplex; `192.168.55.10` leased; app offline issue remains |
| `lan3` | GS1900-8HP port 1 | Tagged trunk: 1, 10, 30, 40 | Assigned; currently unplugged |
| `lan4` | OMV NAS | Untagged VLAN 40 | Live and verified 2026-09-04 |
| `lan5` | None connected | Untagged VLAN 1; reserved for a LAN or recovery laptop | Available, assigned |

Every LAN port has a policy assignment. `lan2` is Hive/cloud IoT; `lan5`
is LAN/recovery. Manage the router through HomeAdmin; see [[../../HANDOFF-2026-07-27-portal-services]].

Use `lan5` for a normal LAN device or recovery laptop only. Do not put a
switch, camera, or NAS there: those devices belong on their assigned router
access port or the GS1900.

## Switch: Zyxel GS1900-8HP

The switch management interface is `192.168.10.12` on VLAN 10. Ports 2-7 are
the CCTV block. Set every unused future camera port to disabled until its camera
is installed and labelled; enable PoE only for the intended port during a
camera bench/mounting change.

| Switch port | Cable destination | VLAN / PoE | State |
|---|---|---|---|
| `1` | Router `lan3` | Tagged trunk: 1, 10, 30, 40; no camera PoE | Assigned; disconnected |
| `2` | ANNKE C500, camera 1 | Untagged VLAN 30, PVID 30, PoE; `192.168.30.21` | Previously proven; disconnected |
| `3` | Patio camera / camera 3 | Untagged VLAN 30, PVID 30, PoE; `192.168.30.23` | Previously proven; disconnected |
| `4` | Gate camera / camera 2 | Untagged VLAN 30, PVID 30, PoE; `192.168.30.22` | Previously proven; disconnected |
| `5` | Camera 4 | Reserve: untagged VLAN 30, PVID 30, PoE; `192.168.30.24` | Future |
| `6` | Camera 5 | Reserve: untagged VLAN 30, PVID 30, PoE; IP to allocate | Future |
| `7` | Camera 6 | Reserve: untagged VLAN 30, PVID 30, PoE; IP to allocate | Future |
| `8` | Spare storage access | Untagged VLAN 40, PVID 40 | Reserved; OMV is on router `lan4` |

## CCTV Connectivity

Each camera connects by CAT6 to its GS1900 PoE port, enters VLAN 30 untagged,
and reaches Frigate CT 111 (`192.168.30.20`) across the two tagged trunks:

```text
camera -> GS1900 port 2-7 (VLAN 30 access) -> GS1900 port 1
       -> router lan3 (VLAN 30 tagged) -> router lan1 (VLAN 30 tagged)
       -> Proxmox -> CT 111 Frigate
```

All three previously proven cameras are ANNKE C500 units and retain RTSP paths
`/Streaming/Channels/101` (main) and `/Streaming/Channels/102` (substream).
Camera 1 is `.21` on port 2, Patio is `.23` on port 3, and Gate is `.22` on
port 4. Ports 5-7 remain the future CCTV block; `.24` is reserved for the next
camera.

## Capacity Decision

The eight-port switch has three future camera ports and a spare storage
access port: port 8 remains configured for VLAN 40 even though OMV is on
router `lan4`. The planned TL-WA801N extender needs VLAN 1; plugging it into
port 8 as configured would put it on the storage network. Before connecting
the extender, choose and document one of:

1. Keep the extender disconnected or use a separate suitable access path.
2. Reconfigure spare port 8 to VLAN 1, replacing its storage-recovery role.
3. Add a second managed switch or replace the GS1900 with a larger switch.

## Cable Labels

Label both ends of every cable using the exact port pair, for example:

```text
RTR-lan3 <-> SW-p1
SW-p2 <-> CCTV-01-ANNKE
RTR-lan4 <-> OMVNAS
RTR-lan1 <-> PROXMOX
```

For new cameras, add the physical location to the label, such as
`SW-p3 <-> CCTV-02-DRIVEWAY`, only after the location plan is confirmed.
