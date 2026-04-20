---
title: "Smart Plugs — VentSys VLAN 50"
category: entity
tags: [hardware, smart-plug, ventsys, vlan50, tapo, safety]
created: 2026-04-07
updated: 2026-04-07
sources: [openwrt-dhcp-config, openwrt-vlan-firewall-configs, esphome-adoption-guide]
status: active
---

# Smart Plugs — VentSys VLAN 50

**Type:** device — smart plugs (8 units, commercial)
**Status:** ⏳ Hardware pending / not yet purchased
**Related:** [[entities/ventsys]], [[entities/home-assistant]]

## Overview

Eight smart plugs on VLAN 50 (IoT) providing emergency power cutoff and energy monitoring for 3D printing equipment. Commercial units (not ESP32-based — no ESPHome API). Monitored via ping and HA integration. Tapo plugs suspected (port 9999 = Tapo local control API appears in emergency firewall rule).

## IP Allocation (all on 192.168.50.x)

| IP | Name | Device controlled |
|---|---|---|
| 192.168.50.71 | plug-fdm-printer | FDM 3D printer (emergency cutoff) |
| 192.168.50.72 | plug-sla-printer | SLA resin printer (emergency cutoff) |
| 192.168.50.73 | ventsys-plug-uv-1 | UV curing station 1 |
| 192.168.50.74 | ventsys-plug-uv-2 | UV curing station 2 |
| 192.168.50.75 | plug-wash-cure | Wash & cure machine |
| 192.168.50.76 | ventsys-plug-ultrasonic | Ultrasonic cleaner |
| 192.168.50.77 | plug-ams-ht | AMS-HT (filament dryer) |
| 192.168.50.78 | plug-esun-dryer | eSUN filament dryer |

## Notes on ESPHome Plugs

Three of these (.73, .74, .76) have ESPHome YAMLs (`ventsys_plug_uv1.yaml`, `ventsys_plug_uv2.yaml`, `ventsys_plug_ultrasonic.yaml`) — they ARE ESPHome-flashed devices, not commercial Tapo units. The remaining 5 (.71, .72, .75, .77, .78) are commercial smart plugs (likely Tapo P110 — a notes file `ventsys_plug_tapo_p110_notes.md` exists in `configs/esphome/`).

## Emergency Access

Manual firewall rule covers all 8 plugs (.71–.78, /29 subnet) via ports 80, 443, 9999 (Tapo local). Run on router when needed:
```bash
uci add firewall rule
uci set firewall.@rule[-1].name='Emergency Smart Plug Access'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].dest_ip='192.168.50.71/255.255.255.248'
uci set firewall.@rule[-1].dest_port='80,443,9999'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci commit firewall && /etc/init.d/firewall restart
```

## Safety Note

Plugs .71 and .72 (FDM and SLA printers) are the emergency cutoff points. In any fire/smoke event, VentSys automations should trigger these plugs to cut power to the printers before or alongside fan ramp-up.

## Open Questions

- [ ] Confirm plug models (.71, .72, .75, .77, .78) — Tapo P110?
- [ ] Confirm ESPHome plugs (.73, .74, .76) are flashed and adopted
- [ ] Note MAC addresses at deployment for DHCP reservations

## Change Log

- 2026-04-07: Page created from dhcp-config.conf and firewall config discovery. 3 of 8 are ESPHome-based.
