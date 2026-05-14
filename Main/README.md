---
title: Home Automation Safety Vault
description: Fire safety ventilation, NVR surveillance, secure network, and home automation for 3D printing operations
tags: [home-automation, project-overview]
aliases: [Project Overview]
created: 2025-09-15
modified: 2026-03-07
type: project-overview
status: active
---

# Home Automation Safety Vault

Home automation system focused on fire safety and ventilation for 3D printing operations, with NVR camera monitoring, secure network architecture, and AI integration.

**Repository:** https://github.com/Nysplaidame/home-automation-project  
**Index:** [[PROJECT-INDEX|Full Index]] | **Tasks:** [[TO-DO|Task list]]

---

## Project status (May 2026)

| Layer | Status | Notes |
|---|---|---|
| Network design | ✅ Complete | 10-segment architecture, all configs written and audited |
| Router configs | ✅ Live | vlan/firewall/dhcp/wireless deployed through router-deploy first-flight |
| Router deployment | ✅ Live | GL-MT6000 stable on management IP 192.168.10.1 |
| Proxmox | ✅ Live | MINIX NEO Z350 on 192.168.10.10, Proxmox VE 9 |
| HA VM | ✅ Live | HAOS VM 100 at 192.168.20.101, VentSys packages staged |
| Frigate VM | ✅ Live | VM 101 on VLAN 30, Debian 13 base live; Docker and Frigate staging complete |
| Docker host | ✅ Live | VM 103 on VLAN 20, central trusted Docker host; Bambuddy running as first workload |
| Pi NAS | ✅ Documented | Setup guide written, hardware needed |
| VentSys dashboard | ✅ Complete | dashboards/ventsys-dashboard.html with full HA integration layer |
| VentSys HA packages | ✅ Complete | Package YAML, scripts, automations all written |
| ESPHome sensor config | ✅ Written | printairpipe-controller.yaml ready for hardware |
| VentSys hardware | ⏳ Pending | ESP32 boards, sensors, PrintAirPipe parts not yet purchased |
| Cameras | ⏳ Pending | Models not yet selected; RTSP URLs are placeholders |
| MAC addresses | ⏳ Partial | Core VM MACs are recorded; many hardware/device placeholders remain |

---

## Hardware

| Device | Model | Status |
|---|---|---|
| Compute | MINIX NEO Z350-0dB (i3-N350, 16GB RAM, 512GB SSD) | ✅ Owned |
| Router | GL.iNet GL-MT6000 (OpenWrt, WiFi 6) | ✅ Owned and deployed |
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
- Full dashboard: `dashboards/ventsys-dashboard.html` → deploy to `/config/www/`

### Network security (10 segments)
| VLAN | Name | Subnet | Internet |
|---|---|---|---|
| 1 | LAN (users) | 192.168.1.0/24 | ✅ |
| 10 | Management | 192.168.10.0/24 | ✅ |
| 20 | Automation (HA) | 192.168.20.0/24 | HA only |
| 30 | NVR (Frigate) | 192.168.30.0/24 | ❌ |
| 35 | Printers | 192.168.35.0/24 | OTA only |
| 40 | Storage (NAS) | 192.168.40.0/24 | ❌ |
| 50 | IoT sensors | 192.168.50.0/24 | ❌ |
| 60 | Monitoring | 192.168.60.0/24 | Limited |
| 70 | DMZ | 192.168.70.0/24 | Limited |
| 99 | Guest | 192.168.99.0/24 | ✅ |

### NVR / Cameras (VLAN 30)
- Frigate NVR on Proxmox VM 101
- 4 cameras at 192.168.30.21–24
- Footage to NAS via NFS, HA integration via Frigate card

### Docker host + Bambuddy / P1S printer (VLAN 20 → VLAN 35)
- Docker host runs on VM 103 at 192.168.20.102; Bambuddy is the first Compose workload on port 8000
- Monitors Bambu Lab P1S at 192.168.35.200 via MQTT over VLAN 35
- Publishes print state to Mosquitto; HA package in `configs/home-assistant/bambuddy_p1s_package.yaml`
- Setup guide: `scripts/setup/proxmox/docker_host_setup_guide.md`

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
| Docker host setup guide | `scripts/setup/proxmox/docker_host_setup_guide.md` |
| Bambuddy workload guide | `scripts/setup/proxmox/bambuddy_vm_setup_guide.md` |
| ESPHome sensor config | `configs/esphome/printairpipe-controller.yaml` |
| VentSys ESPHome | `ventsys/ventsys_bundle_updated/` |
| VentSys dashboard | `dashboards/ventsys-dashboard.html` |
| Router setup (phases 1–8) | `scripts/setup/router/` |
| Proxmox + VM setup | `scripts/setup/proxmox/` |
| NAS setup | `scripts/setup/nas/pi_nas_setup_guide.md` |
| ESPHome adoption | `scripts/setup/ventsys/esphome_adoption_guide.md` |
| Wiring reference | `docs/diagrams/wiring-diagrams/ventsys_wiring_reference.md` |
| Troubleshooting | `docs/troubleshooting/troubleshooting_reference.md` |
| Backup strategy | `scripts/backup/backup_strategy.md` |
| Update maintenance playbook | `docs/procedures/update_maintenance_playbook.md` |
| APT cache design | `docs/procedures/apt_cacher_ng_design.md` |
| Time sync strategy | `docs/procedures/time_sync_strategy.md` |
| Docker host policy | `docs/decisions/03-docker-host-service-policy.md` |
| Monitoring roadmap | `docs/procedures/monitoring_roadmap.md` |
| Network testing | `scripts/setup/router/network_testing_guide.md` |
| SSL/TLS guide | `docs/procedures/ssl_tls_guide.md` |
| WireGuard VPN guide | `scripts/setup/router/wireguard_vpn_guide.md` |

---

## Deployment sequence

1. **Router** — run phases 1–8 in `scripts/setup/router/`, starting with `phase_1_prerequisites.md`, then test with `network_testing_guide.md`
2. **Proxmox** — follow `proxmox_setup_guide.md`, run `configs/proxmox/vm-setup.sh`
3. **HA VM** — follow `ha_vm_setup_guide.md`, copy packages and dashboard
4. **Frigate VM** — follow `frigate_vm_setup_guide.md`
5. **Docker host / Bambuddy workload** — follow `docker_host_setup_guide.md`, keep `/opt/stacks/bambuddy/.env` for bootstrap/MQTT settings, then configure P1S + HA token in the Bambuddy web UI and verify HA entities appear
6. **NAS** — follow `pi_nas_setup_guide.md`
7. **VentSys hardware** — purchase parts, follow wiring reference, flash ESPHome via USB
8. **VentSys adoption** — follow `esphome_adoption_guide.md`
9. **Cameras** — fill in RTSP URLs in `configs/frigate/config.yml`, update MAC addresses
10. **VPN** — follow `wireguard_vpn_guide.md` for client setup

---

**Updated:** May 2026
