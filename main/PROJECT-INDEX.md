---
title: Project Documentation Index
description: Master navigation hub for all project documentation
tags: [index, navigation, home-automation]
aliases: [Project Index, Documentation Hub]
created: 2025-09-15
modified: 2026-05-25
type: index
status: active
---

# Project Documentation Index

**Overview:** [[README|README]] | **Tasks:** [[TO-DO|TO-DO]] | **Repo:** https://github.com/Nysplaidame/home-automation-project

---

## Quick status

| Area | State |
|---|---|
| Network configs (router) | ✅ Written, audited, first-flight deployed |
| Proxmox + VM setup guides | ✅ Complete; Proxmox live |
| HA + Frigate setup guides | ✅ HA live, Frigate documented |
| Docker host + Bambuddy workload guide | ✅ Complete |
| VentSys HA packages + dashboard | ✅ Complete |
| ESPHome configs | ✅ Written (hardware IDs pending) |
| OMV NAS setup guide | ✅ Written |
| Service/ACL reference docs | ✅ Written |
| Backup strategy | ✅ Written |
| Troubleshooting reference | ✅ Written |
| Network testing guide | ✅ Written |
| SSL/TLS guide | ✅ Written |
| Tailscale remote access guide | ✅ Written |
| WireGuard fallback guide | ✅ Written |
| Wiring reference | ✅ Written |
| Physical deployment | ✅ Router, Proxmox trunk, HAOS, and docker-host live |
| Hardware procurement (sensors/cameras/NAS) | ⏳ Pending |

---

## Configuration files

### Router (OpenWrt — GL-MT6000)
- [[configs/openwrt/vlan-config.conf]] — VLAN bridge, logical interfaces, WireGuard
- [[configs/openwrt/firewall-config.conf]] — zones, inter-VLAN rules, VentSys ports
- [[configs/openwrt/dhcp-config.conf]] — DHCP scopes, static reservations, DNS
- [[configs/openwrt/wireless-config.conf]] — SSIDs, channels, WPA3/WPA2
- [[configs/openwrt/system-config.conf]] — router hostname, timezone, and router-local NTP server intent

### Home Assistant
- [[configs/home-assistant/configuration.yaml]] — core config, packages directive, HTTP
- [[configs/home-assistant/automations.yaml]] — fire safety, temp, air quality, watchdog
- [[configs/home-assistant/haos-timesyncd-router.conf]] — HAOS router-local NTP override for router-derived ESPHome time

### Frigate NVR
- [[configs/frigate/config.yml]] — cameras, MQTT, retention, detector
- [[configs/frigate/docker-compose.yml]] — Frigate service, volumes, env vars

### Bambuddy / P1S
- [[configs/home-assistant/bambuddy_p1s_package.yaml]] — HA MQTT sensors, binary sensors, automations for P1S
- [[scripts/setup/proxmox/docker_host_setup_guide.md]] — VM 103 Docker host, stack layout, Bambuddy workload
- [[scripts/setup/proxmox/bambuddy_vm_setup_guide.md]] — compatibility shim for Bambuddy-specific links

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

### Fresh rebuild manual suite
- [[docs/install/START-HERE.md]] — beginner-safe rebuild entrypoint from a blank environment
- [[docs/install/INSTALL-TO-DO.md]] — comprehensive setup-documentation completion checklist
- [[docs/diagrams/README.md]] — canonical install and architecture diagram library
- [[docs/install/reference/command-location-legend.md]] — where every command runs
- [[docs/install/reference/secrets-placeholder-ledger.md]] — central placeholder and secret ledger
- [[docs/install/reference/package-dependency-matrix.md]] — packages, hosts, install commands, verification commands
- [[docs/install/reference/decision-gates.md]] — required gates for risky or unresolved services
- [[docs/install/reference/hacs-enhancement-roadmap.md]] — Home Assistant apps, HACS, dashboard, and quality-of-life roadmap
- [[docs/install/services/README.md]] — Tier 1, Tier 2, and Tier 3 docker-host service manuals

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
- [[scripts/setup/nas/omv_nas_setup_guide.md]] — OpenMediaVault NAS, NFS/SMB, HA/Frigate/Immich storage

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
| [[docs/procedures/tailscale_remote_access_guide.md]] | Daily remote access through docker-host Tailscale host routes |
| [[scripts/monitoring/health_check.sh]] | Single-command health check for all systems |

---

## Architecture reference

- [[docs/decisions/01-network-architecture.md]] — original 9-VLAN decision, superseded by the printer VLAN update
- [[docs/decisions/02-printer-vlan-architecture.md]] — current printer VLAN 35 extension
- [[docs/decisions/03-docker-host-service-policy.md]] — VM 103 service placement policy
- [[docs/decisions/04-dns-resolver-and-adblocking.md]] — non-Google DNS and network-wide filtering strategy
- [[docs/decisions/05-self-hosted-services-remote-access.md]] — OMV, docker-host apps, Tailscale host routes, WireGuard fallback
- [[docs/reference/service-matrix.md]] — service, port, DNS, backup, monitoring, and runbook matrix
- [[docs/reference/access-matrix.md]] — OpenWrt, Tailscale, host firewall, and service auth access intent
- [[docs/diagrams/README.md]] — canonical diagram library
- [[docs/diagrams/network/current-master-architecture.mermaid]] — whole-system architecture and service placement
- [[docs/diagrams/network/vlan_architecture_clean.mermaid]] — active 10-segment VLAN topology
- [[docs/diagrams/network/remote-access-flow.mermaid]] — Tailscale daily access and WireGuard fallback flow
- [[docs/diagrams/network/dns-ntp-flow.mermaid]] — router DNS/NTP, AdGuard, and public fallback flow
- [[docs/diagrams/network/security-access-flow.mermaid]] — firewall, ACL, host firewall, and service-auth intent
- [[docs/diagrams/infrastructure/docker-host-service-placement.mermaid]] — docker-host stack layout and app tiers
- [[docs/diagrams/storage/storage-and-backup-flow.mermaid]] — OMV storage, backups, and restore flow
- [[docs/diagrams/install/install-sequence.mermaid]] — fresh rebuild phase sequence and gates
- [[docs/diagrams/ventsys/ventsys-control-and-safety-flow.mermaid]] — VentSys control, airflow, and safety flow
- [[docs/diagrams/wiring-diagrams/ventsys_wiring_reference.md]] — ESP32 wiring
- [[bill-of-materials/hardware/parts-list.md]] — hardware BOM
- [[bill-of-materials/3d-printing/parts-list.md]] — PrintAirPipe 3D print BOM

---

## VentSys deep-dive

- [[docs/procedures/ssl_tls_guide.md]] — canonical MQTT TLS + HTTPS workflow
- [[ventsys/integration-process/ventsys_implementation_roadmap.md]] — phased build plan
- [[ventsys/ventsys_bundle_updated/ventsys_ha_optional.yaml]] — optional HA entities

---

**Updated:** May 2026
