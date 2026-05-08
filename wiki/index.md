# Wiki Index — Home Automation Project

> **LLM:** Read this file first on every query. Master catalog of all wiki content.
> Updated after every ingest, query (if filed), or lint pass.

**Stats:** 25 sources · 16 entities · 6 concepts · 1 analysis
**Last updated:** 2026-04-07

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
- [[sources/openwrt-vlan-firewall-configs]] — DSA bridge, all 9 VLANs, WireGuard, full firewall rules; key fixes: VPN zone→wg0, ESPHome port 3232, IoT NTP dest=local, LAN→HA rule, monitoring→management rule
- [[sources/openwrt-dhcp-config]] — DHCP scopes, all static reservations (17 ESP32 + 8 plugs + infra + RPi displays + AP), local DNS; full IP allocation table
- [[sources/ha-configuration-yaml]] — HA core config; UK locale, packages, HTTP security, recorder; scripts.yaml/scenes.yaml don't exist

### Setup guides
- [[sources/router-setup-complete]] — 8-phase GL-MT6000 deployment; VLAN/DHCP/firewall/WiFi/WireGuard; lan5 recovery/AP; u* vs u DSA fix
- [[sources/network-testing-guide]] — 14 pass/fail criteria for post-cutover validation
- [[sources/proxmox-setup-guide]] — Proxmox VE on MINIX; two-phase network; VM creation; backup strategy; VM 102 monitoring discovered
- [[sources/ha-vm-setup-guide]] — HAOS onboarding; add-ons; package deployment; ventsys_ha_optional warning; Frigate integration
- [[sources/frigate-vm-setup-guide]] — Debian 12 + Docker; Frigate + Bambuddy compose; iGPU; NAS storage; UFW ports
- [[sources/igpu-passthrough-guide]] — Intel i3-N350 Xe → Frigate VM; VA-API + OpenVINO; 60–90% → 10–30% CPU reduction
- [[sources/pi-nas-setup-guide]] — Pi NAS on VLAN 40; NFS exports; Samba; SMART monitoring; boot from USB SSD
- [[sources/esphome-adoption-guide]] — **21-board** canonical fleet; USB flash → adoption → OTA; DS18B20/BME680 discovery
- [[sources/bambuddy-p1s-setup-guide]] — P1S LAN Only Mode; Bambuddy Docker; MQTT 8883; VentSys via HA automations

### VentSys deep-dive
- [[sources/ventsys-technical-specs]] — Full TLS spec: CA structure, Mosquitto config, ESPHome templates, device registry
- [[sources/ventsys-implementation-roadmap]] — 6-phase, 9-week TLS migration plan
- [[sources/ventsys-phase1-foundation]] — Weeks 1–3 detail: network validation → CA → initial device TLS; 17 boards + 8 plugs = 25 devices

### Operational reference
- [[sources/troubleshooting-reference]] — Cross-system diagnostics: MQTT, HA, Frigate, Proxmox, router, VPN, Bambuddy, NAS

---

## Entities
*Devices, hubs, integrations, vendors, services.*

- [[entities/minix-neo-z350]] — Fanless Intel mini PC; Proxmox host; i3-N350 + iGPU; ✅ Owned, ⏳ not configured
- [[entities/gl-mt6000]] — GL.iNet WiFi 6 router; OpenWrt DSA; 9-VLAN core; lan5=recovery/AP port; ✅ Owned, ⏳ not deployed
- [[entities/tplink-ap]] — TP-Link TL-WA801N AP on lan5; extends HomeMain to VLAN 1; reservation at 192.168.1.203; ⏳ stub
- [[entities/rpi-displays]] — 2× Pi kiosk displays (.201/.202, VLAN 1); kiosk mode HA dashboard; ⏳ stub
- [[entities/proxmox]] — Proxmox VE on MINIX; hosts VM100+VM101+VM102; IOMMU for iGPU; ⏳ not installed
- [[entities/monitoring-vm]] — VM 102 on VLAN 60 (192.168.60.10); planned Grafana/Zabbix; ⏳ stub
- [[entities/home-assistant]] — HAOS on VM100 at 192.168.20.101; MQTT, ESPHome, VentSys hub, local CA; ⏳ not deployed
- [[entities/frigate]] — Frigate NVR on VM101 at 192.168.30.20; 4× cameras; iGPU passthrough (VA-API + OpenVINO); ⏳ not deployed
- [[entities/bambuddy]] — Bambu Lab P1S bridge; Docker on VM101 port 8000; MQTT 8883; triggers VentSys FDM mode; ⏳ not deployed
- [[entities/bambu-p1s]] — FDM printer on VLAN 1 at 192.168.1.200; Developer Mode required; ✅ operational
- [[entities/ventsys]] — Fire safety ventilation; **21 ESP32 boards** + **8 smart plugs**; FDM+SLA+booth+garage; ⏳ hardware pending
- [[entities/smart-plugs-ventsys]] — 8 smart plugs .71–.78; 3 ESPHome-based (.73/.74/.76), 5 commercial Tapo; emergency cutoff for printers
- [[entities/esphome]] — ESP32 firmware platform; HA add-on; manages 21 VentSys boards; ⏳ not deployed
- [[entities/mosquitto-mqtt]] — MQTT broker on HA; pre-TLS 1883, target 8883 TLS; ⏳ not deployed
- [[entities/raspberry-pi-nas]] — Pi 4 NAS on VLAN 40 at 192.168.40.50; NFS for Frigate + HA backups; ⏳ not purchased

---

## Concepts
*Protocols, patterns, architectural ideas.*

- [[concepts/rag-vs-wiki-pattern]] — RAG vs Wiki Pattern
- [[concepts/vlan-segmentation]] — 9-VLAN architecture; isolation table; port assignments; design rationale
- [[concepts/ventsys-architecture]] — ESP32→MQTT→Node-RED→HA; zones; 12 control modes; failsafe
- [[concepts/mqtt-tls]] — Local CA on HA; Mosquitto 8883; ESPHome cert embedding; 9-week migration
- [[concepts/printairpipe]] — 125mm 3D-printable ducting; servo butterfly valves; PLA-HT for filter housings
- [[concepts/wireguard-vpn]] — WireGuard on VLAN 70; VPN clients blocked from sensitive VLANs; no WAN SSH

---

## Analyses
*Filed query answers, comparisons, lint reports.*

- [[analyses/deployment-status-2026-04]] — Project snapshot (Apr 2026); blocked on router deployment; hardware shopping list

---

*To add entries: follow the ingest or query workflow in `CLAUDE.md`.*
