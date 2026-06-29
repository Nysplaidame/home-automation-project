---
title: Home Automation Safety Vault
description: Fire safety ventilation, NVR surveillance, secure network, and home automation for 3D printing operations
tags: [home-automation, project-overview]
aliases: [Project Overview]
created: 2025-09-15
modified: 2026-06-21
type: project-overview
status: active
---

# Home Automation Safety Vault

Home automation system focused on fire safety and ventilation for 3D printing operations, with NVR camera monitoring, secure network architecture, and AI integration.

**Repository:** https://github.com/Nysplaidame/home-automation-project  
**Index:** [[PROJECT-INDEX|Full Index]] | **Tasks:** [[TO-DO|Task list]] | **Fresh rebuild manual:** [[docs/install/START-HERE|Start here]]

---

## Project status

Canonical details: [[docs/reference/current-live-state|Current Live State]].

| Layer | Status | Notes |
|---|---|---|
| Network design | ✅ Complete | 10-segment architecture, all configs written and audited |
| Router configs | ✅ Live | vlan/firewall/dhcp/wireless deployed through router-deploy first-flight |
| Router deployment | ✅ Live | GL-MT6000 stable on management IP 192.168.10.1 |
| Proxmox | ✅ Live | MINISFORUM M1 Pro-125H on 192.168.10.10, Proxmox VE 9 |
| HA VM | ✅ Live | HAOS VM 100 at 192.168.20.101, VentSys packages staged |
| Frigate | ✅ LXC baseline live | CT 111 runs Frigate 0.17.1 with shared-iGPU OpenVINO; cameras and MQTT remain deliberately disabled |
| Docker host | ✅ Live | VM 103 on VLAN 20 with a 64 GiB disk; Mealie, Grocy and Obsidian LiveSync join the existing internal services |
| Local AI | ✅ LXC + local inference live | CT 114 runs GPU-backed llama.cpp, Open WebUI, Whisper, Piper and OpenWakeWord |
| OMV NAS | ⏳ Planned | OpenMediaVault at 192.168.40.50 on VLAN 40; hardware/storage needed |
| Remote access | ✅ Live | Tailscale daily access via docker-host host routes; WireGuard kept dormant as fallback |
| VentSys dashboard | ✅ Written / staged | dashboards/ventsys-dashboard.html with full HA integration layer; entities remain hardware-dependent |
| VentSys HA packages | ✅ Written / staged | Package YAML, scripts, automations all written; do not treat VentSys entities as live until hardware is adopted |
| ESPHome sensor configs | ✅ Written / validation ongoing | Production VentSys files live under `configs/esphome/`; hardware adoption remains gated |
| VentSys hardware | ⏳ Pending | ESP32 boards, sensors, PrintAirPipe parts not yet purchased |
| Cameras | ⏳ Pending | Models not yet selected; RTSP URLs are placeholders |
| MAC addresses | ⏳ Partial | Core VM MACs are recorded; many hardware/device placeholders remain |

---

## Hardware

| Device | Model | Status |
|---|---|---|
| Compute | MINISFORUM M1 Pro-125H (Intel Core Ultra 5 125H, 32GB RAM, 1TB NVMe) | ✅ Owned |
| Router | GL.iNet GL-MT6000 (OpenWrt, WiFi 6) | ✅ Owned and deployed |
| NAS | OMV-capable storage host | ⏳ Needed |
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
- Frigate baseline runs on unprivileged CT 111 with shared Intel iGPU acceleration
- 4 future cameras at 192.168.30.21–24
- Future footage path to NAS via NFS after NAS and cameras are built
- HA integration and Frigate card remain planned until cameras are live

### Docker host + Bambuddy / P1S printer (VLAN 20 → VLAN 35)
- Docker host runs on VM 103 at 192.168.20.102; Bambuddy is live on port 8000
- Monitors Bambu Lab P1S at 192.168.35.200 via MQTT over VLAN 35
- Publishes print state to Mosquitto; HA package in `configs/home-assistant/bambuddy_p1s_package.yaml`
- Setup guide: `scripts/setup/proxmox/docker_host_setup_guide.md`

### Self-hosted services and remote access
- OpenMediaVault is the NAS OS at 192.168.40.50; OMV is storage-focused, not the Docker app platform
- docker-host runs internal Compose stacks under `/opt/stacks/<service>/`
- docker-host is the expected target for future containerized AI-adjacent query apps; no YouTube transcript app architecture, ports, APIs, MCP contract, or firewall rules are defined yet
- Tier 1 docker-host services are pre-flight live: AdGuard Home, Immich, Homepage, Dozzle, plus Bambuddy
- Tier 2/Tier 3 pre-flight services are live: ntfy internal alerts and Watchtower monitor-only
- Rebuildable docker-host templates live in `configs/docker-host/`; live secrets and app databases stay on VM 103, not in git
- Tailscale is daily remote access through docker-host with host routes only: `192.168.20.101/32` and `192.168.40.50/32`
- WireGuard remains configured as a dormant split-tunnel fallback

### Monitoring and dashboards (VLAN 60)
- Monitoring VM 102 is live at 192.168.60.10 with Uptime Kuma, InfluxDB, Grafana, and Telegraf
- Grafana dashboards cover home automation baseline, Proxmox/docker-host resources, service availability, DNS, and security posture
- Docker-host Telegraf and lightweight Uptime Kuma/Fail2ban exporters feed InfluxDB buckets for architecture dashboards
- CT 114 local AI checks are live in Uptime Kuma for llama.cpp, Open WebUI,
  Wyoming Piper, and Wyoming Whisper; the Kuma-to-Influx export path includes
  the new monitors.
- Home Assistant monitoring uses direct Grafana/Kuma links for now; embedding remains parked until same-origin HTTPS/reverse proxy is deliberate

### Home Assistant (VLAN 20)
- HAOS on Proxmox VM 100 at 192.168.20.101
- Mosquitto MQTT, ESPHome, Terminal & SSH and File Editor add-ons are live; Frigate integration remains planned
- VentSys packages in `/config/packages/`
- Treat Frigate app state, OMV storage, and VentSys hardware entities as unbuilt
  until explicitly revalidated.

### Local AI / voice (VLAN 20)
- CT 114 `llm-host` at 192.168.20.104 runs llama.cpp, Open WebUI, Wyoming
  Whisper, Piper and OpenWakeWord.
- llama.cpp uses Vulkan on the shared Intel iGPU and serves
  `home-assistant-llm` on `192.168.20.104:8081/v1`.
- The Home Assist pipeline uses Home Assistant's built-in conversation agent.
  The Overwatch pipeline points at the `llamacpp_conversation` integration and
  still needs a live UI/voice validation before it is certified.
- The bounded read-only SearXNG search API is installed for local LLM agents.
- Mealie is live for recipes and meal planning; Overwatch recipe saving is not yet implemented.
- Obsidian remains the durable project/household knowledge and runbook layer;
  Self-hosted LiveSync provides central multi-device freshness while Git keeps
  deliberate version history.
- Grocy is live for pantry/fridge/freezer stock and expiry tracking.
- Hermes Agent remains roadmap-only.

---

## Key file locations

| What | Path |
|---|---|
| Router config | `configs/openwrt/` |
| HA config | `configs/home-assistant/` |
| Frigate config | `configs/frigate/config.yml` |
| Frigate docker-compose | `configs/frigate/docker-compose.yml` |
| Docker-host rebuild templates | `configs/docker-host/` |
| Bambuddy HA package | `configs/home-assistant/bambuddy_p1s_package.yaml` |
| Docker host setup guide | `scripts/setup/proxmox/docker_host_setup_guide.md` |
| Grafana source dashboards | `configs/grafana/` |
| Grafana architecture dashboards | `docs/procedures/grafana_architecture_dashboards.md` |
| Proxmox/docker-host metrics guide | `docs/procedures/proxmox_grafana_metrics.md` |
| Fresh rebuild entrypoint | `docs/install/START-HERE.md` |
| Install phases | `docs/install/phases/` |
| Install references | `docs/install/reference/` |
| Diagram library | `docs/diagrams/README.md` |
| Docker-host service manuals | `docs/install/services/` |
| Shared iGPU/local AI decision | `docs/decisions/07-shared-igpu-lxc-infrastructure.md` |
| LLM host setup guide | `scripts/setup/proxmox/llm_host_setup_guide.md` |
| Local AI performance testing | `docs/procedures/local_ai_performance_testing.md` |
| Bambuddy workload guide | `scripts/setup/proxmox/bambuddy_vm_setup_guide.md` |
| ESPHome production configs | `configs/esphome/` |
| VentSys ESPHome | `ventsys/ventsys_bundle_updated/` |
| VentSys dashboard | `dashboards/ventsys-dashboard.html` |
| Router setup (phases 1–8) | `scripts/setup/router/` |
| Proxmox + VM/LXC setup | `scripts/setup/proxmox/` |
| Canonical current state | `docs/reference/current-live-state.md` |
| NAS setup | `scripts/setup/nas/omv_nas_setup_guide.md` |
| OMV Transfer Portal app | `apps/transferportal/` |
| OMV Transfer Portal runbook | `docs/install/services/transferportal.md` |
| ESPHome adoption | `scripts/setup/ventsys/esphome_adoption_guide.md` |
| Wiring reference | `docs/diagrams/wiring-diagrams/ventsys_wiring_reference.md` |
| Troubleshooting | `docs/troubleshooting/troubleshooting_reference.md` |
| Service matrix | `docs/reference/service-matrix.md` |
| ACL/access matrix | `docs/reference/access-matrix.md` |
| Backup strategy | `scripts/backup/backup_strategy.md` |
| Update maintenance playbook | `docs/procedures/update_maintenance_playbook.md` |
| APT cache design | `docs/procedures/apt_cacher_ng_design.md` |
| Time sync strategy | `docs/procedures/time_sync_strategy.md` |
| Docker host policy | `docs/decisions/03-docker-host-service-policy.md` |
| Monitoring roadmap | `docs/procedures/monitoring_roadmap.md` |
| Network testing | `scripts/setup/router/network_testing_guide.md` |
| SSL/TLS guide | `docs/procedures/ssl_tls_guide.md` |
| Tailscale remote access | `docs/procedures/tailscale_remote_access_guide.md` |
| WireGuard fallback guide | `scripts/setup/router/wireguard_vpn_guide.md` |

---

## Deployment sequence

For a full beginner-safe rebuild from zero, start with `docs/install/START-HERE.md`.
The older setup guides remain deep-dive appendices for individual systems.

1. **Operator basics** — read `docs/install/phases/00-operator-basics.md`
2. **Router** — follow `docs/install/phases/01-router-openwrt.md`, then the router phase appendices in `scripts/setup/router/`
3. **Proxmox** — follow `docs/install/phases/02-proxmox-host.md`, then `scripts/setup/proxmox/proxmox_setup_guide.md`
4. **HA VM** — follow `docs/install/phases/03-home-assistant.md`
5. **Frigate LXC** — follow `docs/install/phases/04-frigate.md`
6. **Docker host / Tailscale** — follow `docs/install/phases/05-docker-host.md`
6A. **Local AI inference LXC** — follow `docs/install/phases/05a-local-ai.md`
7. **NAS** — follow `docs/install/phases/06-omv-nas.md`
8. **Tier 1 apps** — follow `docs/install/phases/07-tier1-apps.md`
9. **Tier 2 drafts** — follow `docs/install/phases/08-tier2-apps.md`
10. **Tier 3/evaluate drafts** — follow `docs/install/phases/09-tier3-evaluate.md`
11. **Backups and maintenance** — follow `docs/install/phases/10-backups-monitoring-maintenance.md`
12. **Physical integrations** — follow `docs/install/phases/11-physical-integrations.md`
13. **Validation** — finish with `docs/install/phases/12-validation-troubleshooting.md`

---

**Updated:** 2026-06-21
