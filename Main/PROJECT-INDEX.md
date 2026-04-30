---
title: Project Documentation Index
description: Master navigation hub for all project documentation
tags: [index, navigation, home-automation]
aliases: [Project Index, Documentation Hub]
created: 2025-09-15
modified: 2026-03-07
type: index
status: active
---

# Project Documentation Index

**Overview:** [[README|README]] | **Tasks:** [[TO-DO|TO-DO]] | **Repo:** https://github.com/Nysplaidame/home-automation-project

---

## Quick status

| Area | State |
|---|---|
| Network configs (router) | ✅ Written, audited, not yet deployed |
| Proxmox + VM setup guides | ✅ Complete |
| HA + Frigate setup guides | ✅ Complete |
| Bambuddy setup guide | ✅ Complete |
| VentSys HA packages + dashboard | ✅ Complete |
| ESPHome configs | ✅ Written (hardware IDs pending) |
| NAS setup guide | ✅ Written |
| Backup strategy | ✅ Written |
| Troubleshooting reference | ✅ Written |
| Network testing guide | ✅ Written |
| SSL/TLS guide | ✅ Written |
| WireGuard VPN guide | ✅ Written |
| Wiring reference | ✅ Written |
| Physical deployment | ⏳ Router not yet switched over |
| Hardware procurement (sensors/cameras/NAS) | ⏳ Pending |

---

## Configuration files

### Router (OpenWrt — GL-MT6000)
- [[configs/openwrt/vlan-config.conf]] — VLAN bridge, logical interfaces, WireGuard
- [[configs/openwrt/firewall-config.conf]] — zones, inter-VLAN rules, VentSys ports
- [[configs/openwrt/dhcp-config.conf]] — DHCP scopes, static reservations, DNS
- [[configs/openwrt/wireless-config.conf]] — SSIDs, channels, WPA3/WPA2

### Home Assistant
- [[configs/home-assistant/configuration.yaml]] — core config, packages directive, HTTP
- [[configs/home-assistant/automations.yaml]] — fire safety, temp, air quality, watchdog

### Frigate NVR
- [[configs/frigate/config.yml]] — cameras, MQTT, retention, detector
- [[configs/frigate/docker-compose.yml]] — Frigate service, volumes, env vars

### Bambuddy / P1S
- [[configs/home-assistant/bambuddy_p1s_package.yaml]] — HA MQTT sensors, binary sensors, automations for P1S
- [[scripts/setup/proxmox/bambuddy_vm_setup_guide.md]] — Bambuddy VM deploy, P1S pairing, HA integration

### ESPHome
- [[configs/esphome/printairpipe-controller.yaml]] — enclosure sensor board (temperature, smoke, VOC, pressure)
- [[ventsys/ventsys_bundle_updated/ventsys_fan_controller.yaml]] — fan PWM control
- [[ventsys/ventsys_bundle_updated/ventsys_valve_controller.yaml]] — valve servo control
- [[ventsys/ventsys_bundle_updated/ventsys_ha_package.yaml]] — HA entities + automations
- [[ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml]] — 12 ventilation mode scripts

### Proxmox
- [[configs/proxmox/vm-configs.conf]] — expected qm config output for VMs 100, 101, and 103
- [[configs/proxmox/vm-setup.sh]] — shell script to create VMs 100, 101, and 103

---

## Setup guides (in deployment order)

### 1. Router
- [[scripts/setup/router/phase_1_prerequisites.md]] — start of phases 1–8 router setup sequence
- [[scripts/setup/router/phase_6_vpn_setup.md]] — WireGuard server setup detail
- [[scripts/setup/router/network_testing_guide.md]] — post-deployment validation
- [[scripts/setup/router/wireguard_vpn_guide.md]] — client setup and key management

### 2. Proxmox + VMs
- [[scripts/setup/proxmox/proxmox_setup_guide.md]] — MINIX hardware, network config, IOMMU
- [[scripts/setup/proxmox/ha_vm_setup_guide.md]] — HAOS onboarding through VentSys integration
- [[scripts/setup/proxmox/frigate_vm_setup_guide.md]] — Debian + Docker + Frigate + iGPU

### 3. Storage
- [[scripts/setup/nas/pi_nas_setup_guide.md]] — Pi NAS, NFS, Samba, HA backup target

### 4. VentSys
- [[scripts/setup/ventsys/esphome_adoption_guide.md]] — first USB flash, HA adoption, MQTT verify
- [[docs/diagrams/wiring-diagrams/ventsys_wiring_reference.md]] — GPIO pins, power, sensor wiring

---

## Operational docs

| Document | Purpose |
|---|---|
| [[scripts/backup/backup_strategy.md]] | All backup layers, restore procedures, monthly checklist |
| [[docs/troubleshooting/troubleshooting_reference.md]] | Per-system quick diagnosis for common failures |
| [[docs/procedures/ssl_tls_guide.md]] | HTTPS for HA, local CA, Let's Encrypt via DuckDNS |
| [[scripts/monitoring/health_check.sh]] | Single-command health check for all systems |

---

## Architecture reference

- [[docs/decisions/01-network-architecture.md]] — original 9-VLAN decision, superseded by the printer VLAN update
- [[docs/decisions/02-printer-vlan-architecture.md]] — current printer VLAN 35 extension
- [[docs/diagrams/network/network-diagram.md]] — visual network topology
- [[docs/diagrams/wiring-diagrams/ventsys_wiring_reference.md]] — ESP32 wiring
- [[bill-of-materials/hardware/parts-list.md]] — hardware BOM
- [[bill-of-materials/3d-printing/parts-list.md]] — PrintAirPipe 3D print BOM

---

## VentSys deep-dive

- [[docs/procedures/ssl_tls_guide.md]] — canonical MQTT TLS + HTTPS workflow
- [[docs/procedures/documentation_triage_2026-04-30.md]] — canonical-vs-template map and archive queue
- [[ventsys/integration-process/ventsys_implementation_roadmap.md]] — phased build plan
- [[ventsys/ventsys_bundle_updated/ventsys_ha_optional.yaml]] — optional HA entities

---

**Updated:** March 2026
