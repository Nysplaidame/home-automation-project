# Wiki Index — Home Automation Project

> **LLM:** Read this file first on every query. Master catalog of all wiki content.
> Updated after every ingest, query (if filed), or lint pass.

**Stats:** 25 sources · 17 entities · 6 concepts · 1 analysis
**Last updated:** 2026-05-08

---

## Sources
*Summaries of ingested raw documents.*

### Methodology
- [[sources/llm-wiki-idea-file]] — Founding methodology doc; RAG vs Wiki pattern

### Project overview
- [[sources/project-readme]] — Project overview (Mar 2026); hardware status, system components, deployment sequence
- [[sources/project-todo]] — Full task list across 6 phases; immediate next actions
- [[sources/hardware-bom]] — Hardware BOM; £792–£1,328 total; procurement status

### Architecture & design
- [[sources/network-architecture-decision]] — 9-VLAN design decision record; evolved from 4-VLAN after Sep 2025 audit

### Configuration files
- [[sources/openwrt-vlan-firewall-configs]] — DSA bridge, all 10 VLANs, WireGuard, full firewall rules
- [[sources/openwrt-dhcp-config]] — DHCP scopes, all static reservations, local DNS; full IP allocation table
- [[sources/ha-configuration-yaml]] — HA core config; UK locale, packages, HTTP security, recorder

### Setup guides
- [[sources/router-setup-complete]] — 8-phase GL-MT6000 deployment; first-flight deployed via router-deploy toolkit
- [[sources/network-testing-guide]] — 14 pass/fail criteria for post-cutover validation; PASS=72/0/0 on first-flight
- [[sources/proxmox-setup-guide]] — Proxmox VE on MINIX; two-phase network; VM creation; backup strategy
- [[sources/ha-vm-setup-guide]] — HAOS onboarding; add-ons; package deployment; VentSys packages staged
- [[sources/frigate-vm-setup-guide]] — Debian 13 + Docker; Frigate staging; iGPU; NAS storage
- [[sources/igpu-passthrough-guide]] — Intel i3-N350 Xe → Frigate VM; VA-API + OpenVINO; 60–90% → 10–30% CPU reduction
- [[sources/pi-nas-setup-guide]] — Pi NAS on VLAN 40; NFS exports; Samba; SMART monitoring; boot from USB SSD
- [[sources/esphome-adoption-guide]] — **21-board** canonical fleet; USB flash → adoption → OTA; DS18B20/BME680 discovery
- [[sources/bambuddy-p1s-setup-guide]] — P1S LAN Only Mode; Bambuddy Docker on VM 103; MQTT; VentSys via HA automations

### VentSys deep-dive
- [[sources/ventsys-technical-specs]] — Full TLS spec: CA structure, Mosquitto config, ESPHome templates, device registry
- [[sources/ventsys-implementation-roadmap]] — 6-phase, 9-week TLS migration plan
- [[sources/ventsys-phase1-foundation]] — Weeks 1–3 detail: network validation → CA → initial device TLS; 17 boards + 8 plugs = 25 devices

### Operational reference
- [[sources/troubleshooting-reference]] — Cross-system diagnostics: MQTT, HA, Frigate, Proxmox, router, VPN, Bambuddy, NAS

---

## Entities
*Devices, hubs, integrations, vendors, services.*

### Hardware
- [[entities/minix-neo-z350]] — Fanless Intel mini PC; Proxmox host; i3-N350 + iGPU; ✅ Owned, ✅ Proxmox live
- [[entities/gl-mt6000]] — GL.iNet WiFi 6 router; OpenWrt DSA; 10-VLAN core; first-flight deployed; ✅ Live
- [[entities/tplink-ap]] — TP-Link TL-WA801N AP on lan5; extends HomeMain to VLAN 1; reservation at 192.168.1.203; ⏳ stub
- [[entities/rpi-displays]] — 2× Pi kiosk displays (.201/.202, VLAN 1); kiosk mode HA dashboard; ⏳ stub
- [[entities/bambu-p1s]] — FDM printer on VLAN 35 at 192.168.35.200; Developer Mode required; ✅ operational
- [[entities/raspberry-pi-nas]] — Pi 4 NAS on VLAN 40 at 192.168.40.50; NFS for Frigate + HA backups; ⏳ not purchased

### Infrastructure (Proxmox VMs)
- [[entities/proxmox]] — Proxmox VE 9.1.9 on MINIX; VMs 100/101/103 live; ✅ Live
- [[entities/docker-host]] — VM 103, Debian 13, VLAN 20 at 192.168.20.102; Bambuddy + apt-cache; ✅ Live
- [[entities/monitoring-vm]] — VM 102 planned (Grafana/Uptime Kuma); ⏳ not yet created

### Software / integrations
- [[entities/home-assistant]] — HAOS 2026.5.0 on VM 100 at 192.168.20.101; VentSys packages staged; ✅ Live
- [[entities/frigate]] — Frigate NVR on VM 101 at 192.168.30.20; Debian 13 live, container staged not started; ✅ VM live
- [[entities/bambuddy]] — Bambu P1S bridge; Docker on VM 103 port 8000; ✅ Running
- [[entities/ventsys]] — Fire safety ventilation; **21 ESP32 boards** + **8 smart plugs**; FDM+SLA+booth+garage; ⏳ hardware pending
- [[entities/smart-plugs-ventsys]] — 8 smart plugs .71–.78; 3 ESPHome-based (.73/.74/.76), 5 commercial Tapo; emergency cutoff
- [[entities/esphome]] — ESP32 firmware platform; HA add-on installed; manages 21 VentSys boards; ⏳ hardware pending
- [[entities/mosquitto-mqtt]] — MQTT broker on HA; pre-TLS 1883; target 8883 TLS; ✅ Running (pre-TLS)

---

## Concepts
*Protocols, patterns, architectural ideas.*

- [[concepts/rag-vs-wiki-pattern]] — RAG vs Wiki Pattern
- [[concepts/vlan-segmentation]] — 10-VLAN architecture; isolation table; port assignments; design rationale
- [[concepts/ventsys-architecture]] — ESP32→MQTT→HA; zones; 12 control modes; failsafe
- [[concepts/mqtt-tls]] — Local CA on HA; Mosquitto 8883; ESPHome cert embedding; 9-week migration (not yet started)
- [[concepts/printairpipe]] — 125mm 3D-printable ducting; servo butterfly valves; PLA-HT for filter housings
- [[concepts/wireguard-vpn]] — WireGuard on VLAN 70; VPN clients blocked from sensitive VLANs; no WAN SSH

---

## Analyses
*Filed query answers, comparisons, lint reports.*

- [[analyses/deployment-status-2026-04]] — Project snapshot (Apr 2026); pre-deployment state

---

*To add entries: follow the ingest or query workflow in `CLAUDE.md`.*
