---
title: Router and Switch Physical Port Layout
description: Confirmed and reserved physical cabling map for the router, GS1900 switch, OMV, and CCTV rollout
tags: [network, cabling, ports, switch, cctv]
created: 2026-07-10
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

| Canonical name | Physical device | Connectivity |
|---|---|---|
| `router` | GL.iNet GL-MT6000 | WAN upstream; CAT6 to `proxmox`, `gs1900-switch`, and `omvnas`; Wi-Fi AP |
| `proxmox` | MINISFORUM M1 Pro-125H mini PC | Router `lan1` tagged trunk; hosts VMs/CTs |
| `gs1900-switch` | Zyxel GS1900-8HP | Router `lan3` tagged trunk; PoE cameras and a spare VLAN 40 access port |
| `omvnas` | OMV NAS hardware | Router `lan4` / VLAN 40 |
| `cam-01-annke-c500` | ANNKE C500 | GS1900 port 2 / VLAN 30 / PoE |
| `p1s` | Bambu Lab P1S | HomePrinters Wi-Fi / VLAN 35 |
| `operator-mobile` | Android phone | Wi-Fi locally; Tailscale off-site |

## Router: GL.iNet GL-MT6000

| Router port | Cable destination | VLAN posture | State |
|---|---|---|---|
| `wan` | Upstream internet router/modem | WAN DHCP | Live |
| `lan1` | MINISFORUM Proxmox host | Tagged trunk: 10, 20, 30, 35, 40, 50, 60, 70 | Live |
| `lan2` | None connected | Untagged VLAN 10; reserved for a temporary management device | Available, assigned |
| `lan3` | GS1900-8HP port 1 | Tagged trunk: 1, 10, 30, 40 | Live |
| `lan4` | OMV NAS | Untagged VLAN 40; `192.168.40.50` | Live |
| `lan5` | None connected | Untagged VLAN 1; reserved for a LAN or recovery laptop | Available, assigned |

Every LAN port has an assignment. There are no unassigned router LAN ports in
the current design. `lan2` and `lan5` are intentionally unplugged until
temporary management or recovery access is needed.

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
| `1` | Router `lan3` | Tagged trunk: 1, 10, 30, 40; no camera PoE | Live |
| `2` | ANNKE C500, camera 1 | Untagged VLAN 30, PVID 30, PoE; `192.168.30.21` | Live |
| `3` | Camera 2 | Reserve: untagged VLAN 30, PVID 30, PoE; `192.168.30.22` | Future |
| `4` | Camera 3 | Reserve: untagged VLAN 30, PVID 30, PoE; `192.168.30.23` | Future |
| `5` | Camera 4 | Reserve: untagged VLAN 30, PVID 30, PoE; `192.168.30.24` | Future |
| `6` | Camera 5 | Reserve: untagged VLAN 30, PVID 30, PoE; IP to allocate | Future |
| `7` | Camera 6 | Reserve: untagged VLAN 30, PVID 30, PoE; IP to allocate | Future |
| `8` | None connected | Untagged VLAN 40, PVID 40; reserved for a future storage device | Available, assigned |

## CCTV Connectivity

Each camera connects by CAT6 to its GS1900 PoE port, enters VLAN 30 untagged,
and reaches Frigate CT 111 (`192.168.30.20`) across the two tagged trunks:

```text
camera -> GS1900 port 2-7 (VLAN 30 access) -> GS1900 port 1
       -> router lan3 (VLAN 30 tagged) -> router lan1 (VLAN 30 tagged)
       -> Proxmox -> CT 111 Frigate
```

Camera 1 is the ANNKE C500 at `192.168.30.21`. Its verified RTSP paths are
`/Streaming/Channels/101` (main) and `/Streaming/Channels/102` (substream).
The other ports remain a cabling and VLAN reservation until their camera model,
MAC, field location, and tested RTSP paths are known.

## Capacity Decision

The eight-port switch has one free VLAN 40 access port now OMV is directly on
router `lan4`, but it cannot provide the planned TL-WA801N extender port
without a VLAN/access-port change. Do not repurpose a camera or the reserved
storage port for that extender without first choosing one of:

1. Keep the extender disconnected or use a separate suitable access path.
2. Add a second managed switch for the extender and future non-camera devices.
3. Replace the GS1900-8HP with a larger managed PoE switch.

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
