---
title: Project Documentation Index
description: Master navigation hub for all project documentation
tags: [index, navigation, home-automation]
aliases: [Project Index, Documentation Hub]
created: 2025-09-15
modified: 2026-07-13
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
| HA + Frigate setup guides | ✅ HA live; CT 111 Frigate baseline live |
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
| Docker-host service templates | ✅ Written for live VM 103 stacks, host firewall, and app-data backup templates |
| Local AI / voice inference | ✅ CT 114 live with shared-iGPU llama.cpp and HA voice/search migration pending |
| Hardware procurement (sensors/cameras/NAS) | ⏳ Pending |

---

## Configuration files

### Router (OpenWrt — GL-MT6000)
- [[configs/openwrt/vlan-config.conf]] — VLAN bridge, logical interfaces, WireGuard
- [[configs/openwrt/firewall-config.conf]] — zones, inter-VLAN rules, VentSys ports
- [[configs/openwrt/dhcp-config.conf]] — DHCP scopes, static reservations, DNS
- [[scripts/validation/validate-home-local-dns.ps1]] — canonical/live
  `home.local` alias validation against the service matrix
- [[configs/openwrt/wireless-config.conf]] — SSIDs, channels, WPA3/WPA2
- [[configs/openwrt/system-config.conf]] — router hostname, timezone, and router-local NTP server intent

### Home Assistant
- [[configs/home-assistant/configuration.yaml]] — core config, packages directive, HTTP
- [[configs/home-assistant/automations.yaml]] — fire safety, temp, air quality, watchdog
- [[configs/home-assistant/haos-timesyncd-router.conf]] — HAOS router-local NTP override for router-derived ESPHome time

### Frigate NVR
- [[configs/frigate/config.yml]] — cameras, MQTT, retention, detector
- [[configs/frigate/docker-compose.yml]] — Frigate service, volumes, env vars
- [[configs/frigate/frigate.env.example]] — required environment keys for RTSP and MQTT credentials
- [[configs/frigate/system/frigate-nvr-fail2ban-sshd.local]] — CT 111 Fail2ban SSH jail baseline

### Local AI
- [[configs/local-ai/docker-compose.yml]] — CT 114 llama.cpp, Open WebUI and Wyoming services

### Monitoring VM
- [[configs/monitoring/system/monitoring-firewall.sh]] — VM 102 source-scoped
  `DOCKER-USER` policy for docker-host Homepage access to Grafana and Uptime Kuma
- [[configs/monitoring/system/monitoring-firewall.service]] — rebuilds the
  monitoring firewall policy after Docker starts

### Docker Host
- [[configs/docker-host/README.md]] — rebuildable source templates for VM 103 Compose stacks and host firewall
- [[configs/docker-host/system/docker-host-firewall.sh]] — canonical `DOCKER-USER` source for docker-host published-port scoping
- [[configs/docker-host/system/docker-host-app-data-backup.sh]] — live NAS backup for household application state, including media apps and SQLite-consistent Vaultwarden/ntfy staging
- [[configs/docker-host/system/docker-host-app-data-backup.service]] — systemd service template for the docker-host app-data backup job
- [[configs/docker-host/system/docker-host-app-data-backup.timer]] — daily timer template for the docker-host app-data backup job
- [[configs/docker-host/stacks/]] — non-secret Compose/config templates for live docker-host services
- [[configs/docker-host/stacks/jellyfin/README.md]] — live read-only OMV media library service
- [[configs/docker-host/stacks/calibre-web/README.md]] — live dedicated ebook library service
- [[configs/docker-host/stacks/atsumeru/README.md]] — live dedicated comics/manga backend
- [[configs/docker-host/stacks/download-gateway/README.md]] — installed Mullvad/Gluetun/qBittorrent containment stack and acceptance gate
- [[configs/docker-host/stacks/vaultwarden/README.md]] — live HTTPS Vaultwarden foundation and onboarding gate

- [[docs/install/services/gridfinity-layout-tool.md]] — live local Gridfinity Layout Tool portal

### Monitoring / Grafana
- [[configs/grafana/README.md]] — rebuildable source exports for Grafana dashboards
- [[configs/grafana/dashboards/]] — architecture dashboard JSON exports
- [[configs/home-assistant/lovelace/monitoring-grafana-links.yaml]] — HA Lovelace direct-link snippet for Grafana/Kuma

### Bambuddy / P1S
- [[configs/home-assistant/bambuddy_p1s_package.yaml]] — HA MQTT sensors, binary sensors, automations for P1S
- [[scripts/setup/proxmox/docker_host_setup_guide.md]] — VM 103 Docker host, stack layout, Bambuddy workload
- [[scripts/setup/proxmox/bambuddy_vm_setup_guide.md]] — compatibility shim for Bambuddy-specific links

### ESPHome
- [[configs/esphome/ventsys_air_sensor_base.yaml]] — shared enclosure sensor-board package (temperature, smoke, VOC, pressure)
- [[configs/esphome/ventsys_fdm_360_valve_v2_nerdiy.yaml]] — 360 intake v2 candidate for ESP32-C6 Zero using GPIO0 servo PWM, GPIO1 LED data, Nerdiy one-sided servo mapping limited to `0-35`, and 1s endpoint PWM detach
- [[configs/esphome/ventsys_sla_360_valve_v2_nerdiy.yaml]] — 360 intake v2 candidate for ESP32-C6 Zero using GPIO0 servo PWM, GPIO1 LED data, Nerdiy one-sided servo mapping limited to `0-35`, and 1s endpoint PWM detach
- [[ventsys/ventsys_bundle_updated/ventsys_fan_controller.yaml]] — fan PWM control
- [[ventsys/ventsys_bundle_updated/ventsys_valve_controller.yaml]] — valve servo control
- [[ventsys/ventsys_bundle_updated/ventsys_ha_package.yaml]] — HA entities + automations
- [[ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml]] — 12 ventilation mode scripts

### Proxmox
- [[configs/proxmox/guest-configs.md]] — canonical live VM/LXC inventory
- [[scripts/setup/proxmox/llm_host_setup_guide.md]] — CT 114 local AI compatibility entrypoint
- [[docs/reference/current-live-state.md]] — canonical deployed-state inventory

---

## Setup guides (in deployment order)

### Fresh rebuild manual suite
- [[docs/install/START-HERE.md]] — beginner-safe rebuild entrypoint from a blank environment
- [[docs/install/INSTALL-TO-DO.md]] — comprehensive setup-documentation completion checklist
- [[docs/install/garage-pi-desktop-setup-guide.md]] — garage Raspberry Pi 5 desktop, NVMe, OLED, project access, and optional AI readiness
- [[docs/install/oled-screen-setup-guide.md]] — 52Pi/GeeekPi case OLED setup and `minitower_oled.service`
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

### 2. Proxmox + VMs/LXCs
- [[scripts/setup/proxmox/proxmox_setup_guide.md]] — MINISFORUM M1 Pro-125H hardware, network config, IOMMU
- [[scripts/setup/proxmox/ha_vm_setup_guide.md]] — HAOS onboarding through VentSys integration
- [[scripts/setup/proxmox/frigate_vm_setup_guide.md]] — CT 111 Frigate compatibility entrypoint
- [[scripts/setup/proxmox/llm_host_setup_guide.md]] — CT 114 local AI compatibility entrypoint
- [[scripts/setup/proxmox/igpu_passthrough_guide.md]] — shared Intel render/card device mapping for unprivileged LXCs

### 3. Storage
- [[scripts/setup/nas/omv_nas_setup_guide.md]] — OpenMediaVault NAS, NFS/SMB, HA/Frigate/Immich storage
- [[docs/install/services/immich-curated-exporter.md]] — allow-listed, non-destructive Immich album export into Jellyfin
- [[docs/install/services/transferportal.md]] — native OMV Transfer Portal service for guarded local rsync jobs
- [[apps/transferportal/README.md]] — FastAPI app, root helper, tests, and packaging source

### 4. VentSys
- [[scripts/setup/ventsys/esphome_adoption_guide.md]] — first USB flash, HA adoption, MQTT verify
- [[docs/diagrams/wiring-diagrams/ventsys_wiring_reference.md]] — GPIO pins, power, sensor wiring

---

## Operational docs

| Document | Purpose |
|---|---|
| [[scripts/backup/backup_strategy.md]] | All backup layers, restore procedures, monthly checklist |
| [[scripts/backup/proxmox-lxc-backup-guard.sh]] | Proxmox-host audit/apply guard for stale CT backup locks and leftover `vzdump` snapshots |
| [[docs/troubleshooting/troubleshooting_reference.md]] | Per-system quick diagnosis for common failures |
| [[docs/procedures/ssl_tls_guide.md]] | HTTPS for HA, local CA, Let's Encrypt via DuckDNS |
| [[docs/procedures/router_temporary_uplink_policy.md]] | Operating policy for temporary GL-MT6000 `wwan_uplink` staging mode |
| [[docs/procedures/omv_storage_cutover_checklist.md]] | Cutover checklist for HA/Immich/Frigate storage once OMV is live |
| [[docs/procedures/omv_cutover_execution_runbook.md]] | Command-by-command OMV cutover runbook with validation gates and rollback |
| [[docs/procedures/tailscale_remote_access_guide.md]] | Daily remote access through docker-host Tailscale host routes |
| [[docs/procedures/wireguard_fallback_governance.md]] | Activation/deactivation governance for dormant WireGuard fallback |
| [[docs/procedures/ids_ips_progression_plan.md]] | Phased IDS/IPS and host hardening progression plan |
| [[docs/procedures/monitoring_roadmap.md]] | Monitoring stack rollout, direct-link posture, and IDS/IPS progression |
| [[docs/procedures/proxmox_grafana_metrics.md]] | Native Proxmox metrics into InfluxDB and Grafana dashboard state |
| [[docs/procedures/grafana_architecture_dashboards.md]] | Architecture-level Grafana dashboards and lightweight Influx exporters |
| [[docs/procedures/home_assistant_companion_app_guide.md]] | HA Companion App phone onboarding, push test, actionable notification test, and sensor policy |
| [[docs/procedures/frigate_camera_preflight_checklist.md]] | Pre-arrival and bench checklist for PoE cameras, managed PoE switch, RTSP validation, and Frigate activation gates |
| [[docs/procedures/frigate_apple_pwa_guide.md]] | Apple iPhone/iPad Frigate PWA setup, including local CA trust and Tailscale access |
| [[docs/procedures/update_maintenance_playbook.md]] | Update windows, caching/offline patterns, and update-monitoring posture |
| [[docs/procedures/update_review_log.md]] | Weekly update-candidate review execution log and follow-up tracking |
| [[docs/procedures/docker_host_patch_window_runbook.md]] | Command-by-command docker-host package/container patch window |
| [[docs/procedures/household-services-implementation-plan.md]] | Decision-gated Vaultwarden, media-library and download-automation implementation plan |
| [[docs/procedures/garage_admin_pi_setup_guide.md]] | Raspberry Pi setup for a trusted garage admin workstation on HomeAdmin |
| [[docs/procedures/local_ai_performance_testing.md]] | Baseline, model/context, voice, and upgrade tests for CT 114 local AI |
| [[scripts/monitoring/health_check.sh]] | Single-command health check for all systems |
| [[scripts/monitoring/export_uptime_kuma_to_influx.py]] | Lightweight Uptime Kuma monitor-state export into InfluxDB |
| [[scripts/monitoring/export_fail2ban_to_influx.sh]] | Lightweight docker-host Fail2ban counter export into InfluxDB |

---

## Architecture reference

- [[docs/decisions/01-network-architecture.md]] — original 9-VLAN decision, superseded by the printer VLAN update
- [[docs/decisions/02-printer-vlan-architecture.md]] — current printer VLAN 35 extension
- [[docs/decisions/03-docker-host-service-policy.md]] — VM 103 service placement policy
- [[docs/decisions/08-household-knowledge-recipes-and-inventory.md]] — boundaries between Obsidian, Mealie, Grocy, HA, and Overwatch
- [[docs/decisions/04-dns-resolver-and-adblocking.md]] — non-Google DNS and network-wide filtering strategy
- [[docs/decisions/05-self-hosted-services-remote-access.md]] — OMV, docker-host apps, Tailscale host routes, WireGuard fallback
- [[docs/decisions/07-shared-igpu-lxc-infrastructure.md]] — deployed CT 111/114 shared-iGPU architecture and rollback boundary
- [[docs/reference/service-matrix.md]] — service, port, DNS, backup, monitoring, and runbook matrix
- [[docs/reference/access-matrix.md]] — OpenWrt, Tailscale, host firewall, and service auth access intent
- [[docs/diagrams/README.md]] — canonical diagram library
- [[docs/diagrams/network/current-master-architecture.mermaid]] — whole-system architecture and service placement
- [[docs/diagrams/network/vlan_architecture_clean.mermaid]] — active 10-segment VLAN topology
- [[docs/diagrams/network/physical-port-and-cabling.mermaid]] — live router, trunks, switch ports, camera, NAS, and Wi-Fi cabling
- [[docs/diagrams/network/remote-access-flow.mermaid]] — Tailscale daily access and WireGuard fallback flow
- [[docs/diagrams/network/dns-ntp-flow.mermaid]] — router DNS/NTP, AdGuard, and public fallback flow
- [[docs/diagrams/network/security-access-flow.mermaid]] — firewall, ACL, host firewall, and service-auth intent
- [[docs/diagrams/infrastructure/docker-host-service-placement.mermaid]] — docker-host stack layout and app tiers
- [[docs/diagrams/infrastructure/proxmox-guests-and-backups.mermaid]] — production and rollback guests, shared iGPU paths, and backup schedules
- [[apps/mermaid-viewer/README.md]] — generated live viewer for all canonical Mermaid sources
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

**Updated:** July 2026
