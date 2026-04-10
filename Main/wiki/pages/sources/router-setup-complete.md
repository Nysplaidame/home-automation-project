---
title: "Router Setup — 8-Phase Deployment"
category: source
tags: [router, openwrt, vlan, dhcp, firewall, wireguard]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Router Setup — 8-Phase Deployment

**Original file:** `scripts/setup/router/router_setup_complete.md`
**Date ingested:** 2026-04-07
**Type:** setup guide (8-phase)

## Summary

Comprehensive 8-phase router deployment guide for the GL-MT6000 running OpenWrt DSA. Phases: Prerequisites → VLAN Infrastructure → DHCP → Firewall → Wireless → WireGuard VPN → Integration Testing → VentSys Readiness. Each phase has validation criteria and rollback procedures.

## Key Takeaways

- **lan5 is the recovery port** — always connect laptop here before Phase 2 to retain SSH access at 192.168.1.1 if VLANs break. After setup, this port is used for TP-Link TL-WA801N AP (VLAN 1 untagged). No config changes needed when transitioning from recovery to AP use.
- **u* vs u in bridge-vlan:** `u*` sets the port PVID (untagged ingress maps to VLAN). Plain `u` only controls egress — without `*`, untagged ingress is undefined and breaks untagged device connectivity. Critical fix.
- **VLAN 1 correction:** lan5 IS a physical VLAN 1 port (untagged*) — used for recovery/AP. The "WiFi-only" description applies to user devices; lan5 itself is physical VLAN 1 for infrastructure.
- **WireGuard keys:** generated in Phase 1 at `/etc/wireguard/keys/` — server + 3 client key pairs. Private keys 600 permissions. Never regenerate without also reconfiguring all clients.
- **WiFi passwords:** generated via `openssl rand` in Phase 1 — 5 SSIDs. Stored at `/etc/wireless/credentials/`
- **Backup system:** `backup_phase.sh` and `emergency_restore.sh` created in Phase 1; run backup before each phase
- **DHCP ranges:** Management .100–.149, LAN .100–.199, IoT .100–.190
- **DNS:** local domain `home.local`; entries for homeassistant.home.local (→ .20.101), frigate.home.local (→ .30.20), nas.home.local (→ .40.50), proxmox.home.local (→ .10.10)
- **VentSys-critical VLANs:** VLAN 20 (HA automation) and VLAN 50 (IoT sensors) are explicitly verified in Phase 2 validation as "VentSys Critical Interface Verification"

## Phase Summary

| Phase | Duration | Risk | Output |
|---|---|---|---|
| 1 — Prerequisites | 2–3h | Low | Packages, WG keys, WiFi passwords, backup system |
| 2 — VLAN Infrastructure | 3–4h | High | 9 VLAN interfaces, DSA bridge, port assignments |
| 3 — DHCP | 2–3h | Medium | DHCP scopes for all VLANs, DNS, static reservations |
| 4 — Firewall | 2–3h | High | Zones, inter-VLAN rules, internet access policies |
| 5 — Wireless | 1–2h | Low | 5 SSIDs, channel plan, WPA3/WPA2 |
| 6 — WireGuard VPN | 1–2h | Medium | VPN server on VLAN 70, 3 client configs |
| 7 — Integration Testing | 1h | Low | End-to-end validation all phases |
| 8 — VentSys Readiness | 30m | Low | Confirm VLANs 20+50 ready for ESPHome |

## Entities Mentioned

[[entities/gl-mt6000]], [[entities/home-assistant]], [[entities/ventsys]], [[entities/proxmox]], [[entities/frigate]], [[entities/raspberry-pi-nas]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/wireguard-vpn]]

## Contradictions / Updates

lan5 as physical VLAN 1 port (for TP-Link AP) not previously documented. Also confirms a 5th LAN port exists on the GL-MT6000 (lan1–lan5) — earlier docs only mentioned lan1–lan4.
