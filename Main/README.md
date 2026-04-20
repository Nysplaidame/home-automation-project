---
title: Home Automation Safety Vault
description: Fire safety ventilation, CCTV, secure network, and home automation for 3D printing operations
tags: [home-automation, project-overview]
aliases: [Project Overview]
created: 2025-09-15
modified: 2026-03-07
type: project-overview
status: active
---

# Home Automation Safety Vault

Home automation system focused on fire safety and ventilation for 3D printing operations, with CCTV monitoring, secure network architecture, and AI integration.

**Repository:** https://github.com/Nysplaidame/home-automation-project  
**Index:** [[PROJECT-INDEX|Full Index]] | **Tasks:** [[TO-DO|Task list]]

---

## Project status (March 2026)

| Layer | Status | Notes |
|---|---|---|
| Network design | ✅ Complete | 9-VLAN architecture, all configs written and audited |
| Router configs | ✅ Complete | vlan/firewall/dhcp/wireless — ready to deploy |
| Router deployment | ⏳ Pending | GL-MT6000 not yet live — on existing flat network |
| Proxmox | ✅ Hardware ready | MINIX NEO Z350, Proxmox install guide complete |
| HA VM | ✅ Documented | HAOS, all packages, dashboard — ready to deploy post-router |
| Frigate VM | ✅ Documented | Debian 12 + Docker, config complete |
| Bambuddy | ✅ Documented | Runs alongside Frigate on VM 101, P1S integration complete |
| Pi NAS | ✅ Documented | Setup guide written, hardware needed |
| VentSys dashboard | ✅ Complete | ventilation_v9k.html with full HA integration layer |
| VentSys HA packages | ✅ Complete | Package YAML, scripts, automations all written |
| ESPHome sensor config | ✅ Written | printairpipe-controller.yaml ready for hardware |
| VentSys hardware | ⏳ Pending | ESP32 boards, sensors, PrintAirPipe parts not yet purchased |
| Cameras | ⏳ Pending | Models not yet selected; RTSP URLs are placeholders |
| MAC addresses | ⏳ Pending | All DHCP reservations have XX:XX placeholders |

---

## Hardware

| Device | Model | Status |
|---|---|---|
| Compute | MINIX NEO Z350-0dB (i3-N350, 16GB RAM, 512GB SSD) | ✅ Owned |
| Router | GL.iNet GL-MT6000 (OpenWrt, WiFi 6) | ✅ Owned, not yet deployed |
| Pi NAS | Raspberry Pi 4 (4GB+) | ⏳ Needed |
| PoE switch | 8-port Gigabit PoE+ | ⏳ Needed |
| IP cameras | 4× PoE (model TBD) | ⏳ Needed |
| ESP32 boards | 4× (2× sensor, 1× fan ctrl, 1× valve ctrl) | ⏳ Needed |

---

## System components

### VentSys fire safety (VLAN 50 / VLAN 20)
- Two 3D printer enclosures (FDM + SLA) with smart ventilation
- PrintAirPipe 125mm ducting with servo-controlled butterfly valves
- Multi-sensor arrays: temperature, humidity, smoke/VOC, differential pressure
- Emergency power cutoff via smart plugs
- ESPHome on isolated VLAN 50, controlled via MQTT through HA
- Full dashboard: `ventilation_v9k.html` → deploy to `/config/www/`

### Network security (9 VLANs)
| VLAN | Name | Subnet | Internet |
|---|---|---|---|
| 1 | LAN (users) | 192.168.1.0/24 | ✅ |
| 10 | Management | 192.168.10.0/24 | ✅ |
| 20 | Automation (HA) | 192.168.20.0/24 | HA only |
| 30 | CCTV (Frigate) | 192.168.30.0/24 | ❌ |
| 40 | Storage (NAS) | 192.168.40.0/24 | ❌ |
| 50 | IoT sensors | 192.168.50.0/24 | ❌ |
| 60 | Monitoring | 192.168.60.0/24 | Limited |
| 70 | DMZ | 192.168.70.0/24 | Limited |
| 99 | Guest | 192.168.99.0/24 | ✅ |

### CCTV (VLAN 30)
- Frigate NVR on Proxmox VM 101
- 4 cameras at 192.168.30.21–24
- Footage to NAS via NFS, HA integration via Frigate card

### Bambuddy / P1S printer (VLAN 30 → VLAN 1)
- Bambuddy runs on VM 101 alongside Frigate (port 8000)
- Monitors Bambu Lab P1S at 192.168.1.200 via MQTT over VLAN 1
- Publishes print state to Mosquitto; HA package in `configs/home-assistant/bambuddy_p1s_package.yaml`
- Setup guide: `scripts/setup/printers/bambuddy_p1s_setup_guide.md`

### Home Assistant (VLAN 20)
- HAOS on Proxmox VM 100 at 192.168.20.101
- Mosquitto MQTT, ESPHome, Frigate integrations
- VentSys packages in `/config/packages/`

---

## Key file locations

| What | Path |
|---|---|
| Router config | `configs/openwrt/` |
| HA config | `configs/home-assistant/` |
| Frigate config | `configs/frigate/config.yml` |
| Frigate docker-compose | `configs/frigate/docker-compose.yml` |
| Bambuddy HA package | `configs/home-assistant/bambuddy_p1s_package.yaml` |
| Bambuddy setup guide | `scripts/setup/printers/bambuddy_p1s_setup_guide.md` |
| ESPHome sensor config | `configs/esphome/printairpipe-controller.yaml` |
| VentSys ESPHome | `ventsys/ventsys_bundle_updated/` |
| VentSys dashboard | `ventilation_v9k.html` |
| Router setup (phases 1–8) | `scripts/setup/router/` |
| Proxmox + VM setup | `scripts/setup/proxmox/` |
| NAS setup | `scripts/setup/nas/pi_nas_setup_guide.md` |
| ESPHome adoption | `scripts/setup/ventsys/esphome_adoption_guide.md` |
| Wiring reference | `docs/diagrams/wiring-diagrams/ventsys_wiring_reference.md` |
| Troubleshooting | `docs/troubleshooting/troubleshooting_reference.md` |
| Backup strategy | `scripts/backup/backup_strategy.md` |
| Network testing | `scripts/setup/router/network_testing_guide.md` |
| SSL/TLS guide | `docs/procedures/ssl_tls_guide.md` |
| WireGuard VPN guide | `scripts/setup/router/wireguard_vpn_guide.md` |

---

## Deployment sequence

1. **Router** — run phases 1–8 in `router_setup_complete.md`, then test with `network_testing_guide.md`
2. **Proxmox** — follow `proxmox_setup_guide.md`, run `configs/proxmox/vm-setup.sh`
3. **HA VM** — follow `ha_vm_setup_guide.md`, copy packages and dashboard
4. **Frigate VM** — follow `frigate_vm_setup_guide.md` (includes Bambuddy deploy in Phase 3.3)
5. **Bambuddy** — configure P1S credentials in `/opt/frigate/.env`, verify HA entities appear
5. **NAS** — follow `pi_nas_setup_guide.md`
6. **VentSys hardware** — purchase parts, follow wiring reference, flash ESPHome via USB
7. **VentSys adoption** — follow `esphome_adoption_guide.md`
8. **Cameras** — fill in RTSP URLs in `configs/frigate/config.yml`, update MAC addresses
9. **VPN** — follow `wireguard_vpn_guide.md` for client setup

---

**Updated:** March 2026
