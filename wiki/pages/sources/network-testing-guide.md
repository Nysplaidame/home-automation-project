---
title: "Network Testing Guide"
category: source
tags: [network, testing, validation, vlan, firewall]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Network Testing Guide

**Original file:** `scripts/setup/router/network_testing_guide.md`
**Date ingested:** 2026-04-07
**Type:** operational reference / testing guide

## Summary

14-point pass/fail test suite to run after router VLAN cutover. Tests run from a laptop on VLAN 10 (lan2). Covers VLAN interface validation, physical port VLAN tagging, internet access controls, inter-VLAN isolation, critical service connectivity, DHCP verification, DNS resolution, WiFi SSID presence, and firewall rule hit counters.

## Key Takeaways

- **Base:** management laptop on lan2 (VLAN 10) — confirms 192.168.10.x address before running anything
- **Must block internet:** VLANs 30 (CCTV), 40 (Storage), 50 (IoT) — ping 1.1.1.1 via `ping -I br-lan.xx` from router must fail
- **Must allow internet:** VLANs 1, 10 (and 99 for guest)
- **Critical isolation checks:** Guest (99) cannot reach any internal VLAN; IoT (50) cannot reach Management (10); CCTV (30) cannot reach Automation (20) directly
- **Service connectivity:** MQTT (port 1883 or 8883) from VLAN 50 → VLAN 20; ESPHome API (6053) from VLAN 20 → VLAN 50; Frigate API (8971 for 0.14+, 5000 for older) from VLAN 20 → VLAN 30; NFS (2049) from VLANs 30+20 → VLAN 40
- **DNS entries:** homeassistant.home.local, frigate.home.local, nas.home.local, proxmox.home.local — all must resolve correctly
- **WiFi check:** `HomeMain, HomeAdmin, HomeAdmin-2G, HomeIoT, HomeGuest` should broadcast; `HomeDMZ` disabled by default
- **2.4GHz channel note:** all 2.4GHz SSIDs share radio0 on channel 6 — per-interface channel overrides not supported in OpenWrt mac80211

## 14 Pass/Fail Criteria

1. All 9 VLAN interfaces up with correct IPs
2. VLAN 1 has no physical port in `bridge vlan show` (lan5 is the exception — it IS physical VLAN 1 for AP)
3. lan2/lan3/lan4 have correct PVIDs
4. VLANs 1, 10, 99 reach internet; 30, 40, 50 do not
5. Guest (99) cannot reach any internal VLAN
6. CCTV (30) cannot reach Automation (20) directly
7. IoT (50) cannot reach Management (10)
8. Management (10) can reach all VLANs
9. MQTT port reachable from VLAN 50 → VLAN 20
10. ESPHome port 6053 reachable from VLAN 20 → VLAN 50
11. Frigate API reachable from VLAN 20 → VLAN 30 (correct port for version)
12. NAS NFS reachable from VLANs 30 and 20
13. DHCP assigning correct ranges per VLAN
14. Local DNS resolving all four .home.local hostnames

## Entities Mentioned

[[entities/gl-mt6000]], [[entities/home-assistant]], [[entities/frigate]], [[entities/ventsys]], [[entities/openmediavault-nas]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/mqtt-tls]]

## Contradictions / Updates

Note on VLAN 1 / lan5: the test criterion says "VLAN 1 has no physical port" but lan5 IS physical VLAN 1. The test verifies user devices don't end up on VLAN 1 via wrong PVIDs — lan5 is intentional and correct.
