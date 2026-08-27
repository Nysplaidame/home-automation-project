# Wiki Index - Home Automation Project

> **LLM:** Read this file first on every query. Master catalog of all wiki content.
> Updated after every ingest, query (if filed), or lint pass.

**Stats:** 21 sources - 27 entities - 7 concepts - 8 analyses
**Last updated:** 2026-08-25

---

## Sources

### Methodology
- [[sources/llm-wiki-idea-file]] - Founding methodology doc; RAG vs Wiki pattern

### Project overview
- [[sources/project-readme]] - Project overview; current canonical docs supersede older NAS/VPN, Frigate, VentSys, and monitoring-embedding claims
- [[sources/project-todo]] - Full task list across phases; current roadmap tracks live monitoring/Grafana/exporter state and keeps OMV/Frigate/VentSys hardware gated
- [[sources/hardware-bom]] - Hardware BOM; current NAS direction is OMV

### Architecture & design
- [[sources/network-architecture-decision]] - Historical 9-VLAN design; current canonical docs supersede older NAS/VPN direction

### Configuration files
- [[sources/openwrt-vlan-firewall-configs]] - DSA bridge, 10 VLANs, WireGuard fallback, firewall rules
- [[sources/openwrt-dhcp-config]] - DHCP scopes, static reservations, local DNS
- [[sources/ha-configuration-yaml]] - HA core config; packages, HTTP security, recorder

### Setup guides
- [[sources/router-setup-complete]] - GL-MT6000 deployment; first-flight deployed via router-deploy toolkit
- [[sources/network-testing-guide]] - Post-cutover validation
- [[sources/proxmox-setup-guide]] - Proxmox VE on MINISFORUM; current VM/LXC build and backup references
- [[sources/ha-vm-setup-guide]] - HAOS onboarding and VentSys packages
- [[sources/frigate-vm-setup-guide]] - Debian + Docker + Frigate staging; iGPU; NAS storage
- [[sources/igpu-passthrough-guide]] - Intel iGPU passthrough to Frigate VM
- [[sources/pi-nas-setup-guide]] - Superseded historical Pi NAS guide; active NAS direction is [[entities/openmediavault-nas]]
- [[sources/esphome-adoption-guide]] - Canonical ESPHome fleet and adoption path
- [[sources/bambuddy-p1s-setup-guide]] - P1S LAN Only Mode; Bambuddy on VM 103

### VentSys deep-dive
- [[sources/ventsys-technical-specs]] - TLS spec, Mosquitto config, ESPHome templates
- [[sources/ventsys-implementation-roadmap]] - TLS migration roadmap
- [[sources/ventsys-phase1-foundation]] - Network validation, CA, initial device TLS

### Operational reference
- [[sources/troubleshooting-reference]] - Cross-system diagnostics

---

## Entities

### Hardware
- [[entities/minisforum-m1-pro-125h]] - Live Proxmox host; Core Ultra 5 125H, 32 GiB, shared iGPU
- [[entities/minix-neo-z350]] - Superseded early compute plan retained for source history
- [[entities/gl-mt6000]] - GL.iNet WiFi 6 router; OpenWrt DSA; 10-VLAN core
- [[entities/tplink-ap]] - Planned TP-Link TL-WA801N AP; VLAN 1 switch capacity unresolved
- [[entities/rpi-displays]] - Pi kiosk displays on VLAN 1
- [[entities/cctv-camera-fleet]] - Three-camera Frigate fleet on PoE VLAN 30 access ports
- [[entities/bambu-p1s]] - FDM printer on VLAN 35
- [[entities/openmediavault-nas]] - Live OMV NAS on VLAN 40 with five-disk SMART monitoring
- [[entities/raspberry-pi-nas]] - Deprecated historical NAS plan; superseded by OMV

### Infrastructure
- [[entities/proxmox]] - Proxmox VE on MINISFORUM; VMs 100/102/103 and CTs 111/114 live
- [[entities/docker-host]] - VM 103; live household/media services, explicit Compose networks, fixed Homepage proxy, Tailscale, Telegraf and Fail2ban
- [[entities/monitoring-vm]] - VM 102; Uptime Kuma, InfluxDB, Grafana, Telegraf, ntfy routing, infrastructure checks, dashboards, and exporters

### Software / integrations
- [[entities/home-assistant]] - HAOS on VM 100; three-camera Frigate integration and camera-health alerts live
- [[entities/frigate]] - CT 111 Frigate 0.17.1 with three cameras, MQTT TLS, shared-iGPU acceleration, and OMV recordings
- [[entities/llm-host]] - CT 114 llama.cpp/Open WebUI/Wyoming host with shared-iGPU Vulkan
- [[entities/bambuddy]] - Bambu P1S bridge on docker-host
- [[entities/adguard-home]] - Live DNS filtering/adblocking service on docker-host
- [[entities/immich]] - Live gallery/photos service with OMV-backed media storage
- [[entities/homepage]] - Live responsive HTTPS operations dashboard on docker-host
- [[entities/dozzle]] - Live Docker log viewer on docker-host
- [[entities/household-hub]] - Transcript RAG, confirmed recipe handoff, read-only Grocy, and Markdown/ICS exports on docker-host
- [[entities/qbittorrent]] - Mullvad/Gluetun-isolated authorised download staging with fail-closed proof
- [[entities/troubleshooting-dashboard]] - Staged read-only symptom-led diagnostics on management-only VM 103 port 8094
- [[entities/ventsys]] - Fire safety ventilation packages/dashboard staged; hardware rollout gated by TLS-path revalidation
- [[entities/smart-plugs-ventsys]] - VentSys smart plugs
- [[entities/esphome]] - ESP32 firmware platform; VentSys hardware adoption pending revalidation
- [[entities/mosquitto-mqtt]] - MQTT broker on HA; TLS `8883` live and plain `1883` deprecated

---

## Concepts

- [[concepts/rag-vs-wiki-pattern]] - RAG vs Wiki Pattern
- [[concepts/vlan-segmentation]] - 10-VLAN architecture
- [[concepts/ventsys-architecture]] - ESP32 to MQTT to HA
- [[concepts/mqtt-tls]] - Local CA and Mosquitto TLS state; VentSys rollout should use `8883`
- [[concepts/printairpipe]] - 125mm printable ducting and valves
- [[concepts/tailscale-remote-access]] - Daily remote access through docker-host host routes
- [[concepts/wireguard-vpn]] - Dormant fallback VPN; HA and OMV host routes only

---

## Analyses

- [[analyses/deployment-status-2026-04]] - Project snapshot from April 2026
- [[analyses/lint-2026-05-18]] - Wiki maintenance lint against May 2026 canonical docs
- [[analyses/lint-2026-05-30]] - Documentation/wiki audit after monitoring, Grafana, Fail2ban, and docker-host service updates
- [[analyses/lint-2026-07-28]] - Targeted CCTV/Frigate/MQTT state lint after the three-camera rollout
- [[analyses/lint-2026-08-01]] - Targeted maintenance/download-gateway state lint and index-count repair
- [[analyses/lint-2026-08-09]] - Targeted Household Hub recipe-workflow and ownership-boundary lint
- [[analyses/lint-2026-08-21]] - Targeted mobile Homepage proxy and Tailscale-access lint
- [[analyses/lint-2026-08-25]] - Architecture-document reconciliation and targeted wiki drift repair

---

*To add entries: follow the ingest or query workflow in `CLAUDE.md`.*
