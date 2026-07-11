# Wiki Log — Home Automation Project

> Append-only. One entry per operation.
> Format: `## [YYYY-MM-DD] <operation> | <title>`
> Quick tail: `grep "^## \[" log.md | tail -10`

---

## [2026-04-07] schema | Wiki initialized

- Schema written to `CLAUDE.md` (v1.0)
- `index.md` and `log.md` created
- Folder structure established: `raw/assets/`, `pages/entities/`, `pages/concepts/`, `pages/sources/`, `pages/analyses/`
- Domain: Home Automation Project
- Status: Ready for first ingest.

## [2026-04-07] ingest | LLM Wiki — Idea File

- Source: `raw/llm-wiki-idea-file.md`
- Pages created: [[sources/llm-wiki-idea-file]], [[concepts/rag-vs-wiki-pattern]]
- Pages updated: [[index]]
- Stub pages flagged (not yet created): [[entities/obsidian]], [[entities/qmd]], [[entities/marp]], [[concepts/personal-knowledge-management]], [[concepts/memex]]
- Notes: First ingest. Founding methodology document. Establishes the RAG vs Wiki distinction that governs how this entire knowledge base operates.

## [2026-04-07] ingest | Batch — Home Automation Project Documentation (8 sources)

**Sources ingested:**
- `home-automation-safety/README.md` → [[sources/project-readme]]
- `home-automation-safety/docs/decisions/01-network-architecture.md` → [[sources/network-architecture-decision]]
- `home-automation-safety/bill-of-materials/hardware/parts-list.md` → [[sources/hardware-bom]]
- `home-automation-safety/ventsys/integration-process/ventsys_technical_specifications.md` → [[sources/ventsys-technical-specs]]
- `home-automation-safety/ventsys/integration-process/ventsys_implementation_roadmap.md` → [[sources/ventsys-implementation-roadmap]]
- `home-automation-safety/docs/troubleshooting/troubleshooting_reference.md` → [[sources/troubleshooting-reference]]
- `home-automation-safety/TO-DO.md` → [[sources/project-todo]]
- `home-automation-safety/dashboards/main-project-dashboard.md` (synthesised into above)

**Pages created:**
- Sources (7): project-readme, network-architecture-decision, hardware-bom, ventsys-technical-specs, ventsys-implementation-roadmap, troubleshooting-reference, project-todo
- Entities (11): minix-neo-z350, gl-mt6000, proxmox, home-assistant, frigate, bambuddy, bambu-p1s, ventsys, esphome, mosquitto-mqtt, raspberry-pi-nas
- Concepts (5): vlan-segmentation, ventsys-architecture, mqtt-tls, printairpipe, wireguard-vpn
- Analyses (1): deployment-status-2026-04

**Pages updated:** [[index]], [[log]]

**Key findings:**
- Project is fully documented but not yet physically deployed — blocked on router switchover
- Critical contradiction resolved: BOM says MINIX has 32GB RAM; README says 16GB — flagged as open question
- Stale device names in older docs (ventsys-fan-controller, ventsys-sla-valve) corrected to canonical names per dhcp-config.conf
- 17 ESP32 boards total in VentSys fleet — all YAMLs exist, none yet flashed
- Hardware failsafe relay recommended for fan circuit (safety-critical gap identified)

## [2026-04-07] ingest | Configs & Setup Guides — 9 sources

**Sources ingested:**
- `scripts/setup/proxmox/proxmox_setup_guide.md` → [[sources/proxmox-setup-guide]]
- `scripts/setup/proxmox/ha_vm_setup_guide.md` → [[sources/ha-vm-setup-guide]]
- `scripts/setup/proxmox/frigate_vm_setup_guide.md` → [[sources/frigate-vm-setup-guide]]
- `scripts/setup/nas/pi_nas_setup_guide.md` → [[sources/pi-nas-setup-guide]]
- `scripts/setup/router/router_setup_complete.md` → [[sources/router-setup-complete]]
- `scripts/setup/router/network_testing_guide.md` → [[sources/network-testing-guide]]
- `scripts/setup/ventsys/esphome_adoption_guide.md` → [[sources/esphome-adoption-guide]]
- `scripts/setup/printers/bambuddy_p1s_setup_guide.md` → [[sources/bambuddy-p1s-setup-guide]]

**Pages created:**
- Sources (8): proxmox-setup-guide, ha-vm-setup-guide, frigate-vm-setup-guide, pi-nas-setup-guide, router-setup-complete, network-testing-guide, esphome-adoption-guide, bambuddy-p1s-setup-guide
- Entities (2): monitoring-vm (VM 102 — newly discovered), tplink-ap (lan5 AP — newly discovered)

**Pages updated:**
- [[entities/ventsys]] — fleet count corrected from 17 to **21 boards**; full canonical table replaced
- [[entities/gl-mt6000]] — lan5 recovery/AP port documented
- [[index]], [[log]]

**Key findings from this ingest:**
1. **21 ESP32 boards, not 17** — adoption guide has full canonical fleet including plugs (.73–.76) and airflow sensors (.41–.43) not previously counted
2. **VM 102** (monitoring, VLAN 60, 192.168.60.10) exists in Proxmox guide but not in README or TO-DO — undocumented entity created
3. **lan5 is physical VLAN 1** — GL-MT6000 has 5 LAN ports; lan5 is the recovery/AP port (VLAN 1 untagged). Previous wiki described VLAN 1 as WiFi-only — corrected
4. **TP-Link TL-WA801N AP** — used on lan5 after setup stabilises; entity stub created
5. **VentSys/Bambuddy MQTT port is 8883 throughout** — NOT 1883. docker-compose.yml, firewall rule, and Bambuddy settings all use 8883. Any pre-TLS commands at 1883 are temporary stage-1 only
6. **VentSys trigger from P1S** is via HA automations on `binary_sensor.p1s_printing` — NOT Bambuddy smart plug entries (FIX #25)
7. **ventsys_ha_optional.yaml has "DO NOT LOAD YET" header** — do not deploy until all sensor boards are live
8. **Backup strategy** for VM 101 (Frigate): do NOT use local daily snapshots — video data fills SSD. Use NAS for VM 101 only
9. **DS18B20 one-wire addresses** are placeholders in YAMLs — must be discovered per board after first flash
10. **Proxmox subscription nag** auto-reapplied after upgrades via apt hook installed in setup guide

## [2026-04-07] ingest | OpenWrt configs, HA config, iGPU guide, VentSys Phase 1 — 6 sources

**Sources ingested:**
- `configs/openwrt/vlan-config.conf` + `configs/openwrt/firewall-config.conf` → [[sources/openwrt-vlan-firewall-configs]]
- `configs/openwrt/dhcp-config.conf` → [[sources/openwrt-dhcp-config]]
- `configs/home-assistant/configuration.yaml` → [[sources/ha-configuration-yaml]]
- `scripts/setup/proxmox/igpu_passthrough_guide.md` → [[sources/igpu-passthrough-guide]]
- `scripts/setup/ventsys/ventsys_phase1_foundation.md` → [[sources/ventsys-phase1-foundation]]

**Pages created:**
- Sources (6): openwrt-vlan-firewall-configs, openwrt-dhcp-config, ha-configuration-yaml, igpu-passthrough-guide, ventsys-phase1-foundation
- Entities (2): rpi-displays (192.168.1.201/202), smart-plugs-ventsys (8 plugs, .71–.78)

**Pages updated:**
- [[entities/frigate]] — iGPU passthrough section added
- [[index]], [[log]]

**Key findings from this ingest:**
1. **Smart plugs are 8 total** (not previously counted): 3 are ESPHome-based (.73 UV-1, .74 UV-2, .76 ultrasonic); 5 are commercial Tapo P110 (.71 FDM, .72 SLA, .75 wash/cure, .77 AMS-HT, .78 eSUN dryer). New entity created.
2. **Raspberry Pi display units** (192.168.1.201, .202) — 2 kiosk displays on VLAN 1; new entity stub created
3. **TP-Link AP DHCP reservation** at 192.168.1.203 (`homeextender`) — confirms AP exists in DHCP config
4. **VPN clients are BLOCKED from Management, CCTV, Storage, IoT** — only LAN + DMZ + HA port 8123 accessible via WireGuard. Critical security detail not previously captured.
5. **IoT mesh rule explicitly REMOVED** from firewall — VLAN 50→50 L3 routing was a lateral movement risk; WiFi client isolation also prevents L2 comms
6. **LAN→HA UI firewall rule** — VLAN 1 devices (including RPi displays at .201/.202) need explicit port 8123 rule; without it all VLAN 1→HA traffic is dropped
7. **ESPHome OTA port 3232** must be open (VLAN 20→50) alongside 6053; without it OTA pushes silently hang — was FIX #6 in firewall config
8. **WireGuard zone fix:** vpn_clients zone previously referenced stale `network='vpn'` interface; corrected to `network='wg0'`. All VPN firewall rules were silently dead before this fix.
9. **Automation DHCP pool starts at .110** (not .100) — .101–.109 reserved for HA and future services
10. **history:/logbook: keys deprecated** in HA since 2024.6 — still functional but log deprecation warnings on startup; recorder handles filtering instead
11. **scripts.yaml and scenes.yaml do not exist** — including them in configuration.yaml causes hard startup error (FIX #2)
12. **iGPU passthrough** fully documented: PCI 00:02.0, x-vga=0 critical, VA-API + OpenVINO; expect 60–90%→10–30% CPU

## [2026-05-08] update | Sync to live deployment state (May 2026)

**Context:** Wiki was last updated 2026-04-07, before any physical deployment. All infrastructure is now live. This entry records the May 2026 sync.

**Pages updated:**

- [[entities/gl-mt6000]] — Status: deployed and stable. 10-VLAN table, all ports physically validated, router-deploy first-flight applied (PASS=72/0/0). Temp rule cleanup noted.
- [[entities/proxmox]] — Status: live (PVE 9.1.9, kernel 7.0.0-3-pve). VM table corrected: VM 102 was never created, VM 103 is docker-host. Known good HA backup slug recorded.
- [[entities/home-assistant]] — Status: live (HAOS 2026.5.0). VentSys packages staged and config-checked. MQTT pre-TLS on 1883. 2FA enabled.
- [[entities/frigate]] — Status: VM 101 live on Debian 13; Frigate image pulled and staged; container not yet started (blocked on .env, cameras, MQTT TLS). Bambuddy no longer on this VM.
- [[entities/bambuddy]] — Status: running on VM 103 at http://192.168.20.102:8000. Compose/env details added. P1S integration parked pending serial.
- [[entities/monitoring-vm]] — Clarified: VM 102 never created; planning still deferred.

**Pages created:**

- [[entities/docker-host]] — New entity: VM 103, Debian 13, VLAN 20, running Bambuddy + apt-cacher-ng.

**Index updated:** entity statuses, stats (17 entities), docker-host added.

**Key corrections vs April wiki:**
1. **VM 102 never created** — monitoring VM is still planned only; docker-host is VM 103
2. **Bambuddy runs on VM 103**, not VM 101 — separate trusted Docker host on VLAN 20
3. **Router is live** — first-flight deployed, 10 VLANs not 9 (VLAN 35 printers added)
4. **HA is live** — core 2026.5.0, VentSys packages staged, MQTT running pre-TLS
5. **MQTT is still 1883** — TLS migration not yet done; 8883 target remains pending
6. **Frigate VM is Debian 13**, not Debian 12 as originally planned

## [2026-05-18] lint | Wiki maintenance sync to May 2026 canonical state

- Sources checked: `main/README.md`, `main/PROJECT-INDEX.md`, `main/TO-DO.md`, current handoffs, and shared `agent-ops` wiki-maintenance docs.
- Pages created: [[analyses/lint-2026-05-18]]
- Pages updated: [[entities/gl-mt6000]], [[entities/proxmox]], [[entities/home-assistant]], [[entities/monitoring-vm]], [[entities/mosquitto-mqtt]], [[entities/bambuddy]], [[entities/ventsys]], [[entities/esphome]], [[concepts/mqtt-tls]], [[index]]
- Notes: Repaired stale wiki state for live monitoring VM, MQTT TLS mixed-mode state, Bambuddy TLS migration, live `ventsys-main-valve-1`, current router validation counts, and the live-only valve-1 plain-MQTT firewall exception risk.

## [2026-05-23] update | Self-hosted services and remote access architecture

- Canonical project docs now select OMV NAS, Tailscale daily remote access, AdGuard Home DNS, Immich, Homepage, Dozzle, and WireGuard fallback.
- Pages created: [[entities/openmediavault-nas]], [[entities/adguard-home]], [[entities/immich]], [[entities/homepage]], [[entities/dozzle]], [[concepts/tailscale-remote-access]]
- Pages updated: [[entities/raspberry-pi-nas]], [[entities/docker-host]], [[entities/frigate]], [[entities/proxmox]], [[entities/gl-mt6000]], [[concepts/wireguard-vpn]], [[concepts/vlan-segmentation]], [[index]]
- Notes: Deprecated the old Raspberry Pi NAS direction, recorded host-route-only Tailscale access, and reframed WireGuard as dormant fallback.
## [2026-05-25] update | Documentation consolidation sync
- Updated wiki summaries after canonical docs removed old prompt-era sub-project files and stale dashboard/kanban files.
- Current canonical docs now use the fresh rebuild manual, 10-segment network, OMV NAS, docker-host service tiers, Tailscale daily access, and WireGuard fallback.
- Pages updated: [[sources/project-readme]], [[sources/network-architecture-decision]], [[concepts/vlan-segmentation]], [[index]]

## [2026-05-30] lint | Documentation and wiki audit after monitoring/Grafana updates

- Sources checked: `main/README.md`, `main/PROJECT-INDEX.md`, `main/TO-DO.md`, `main/HANDOFF-2026-05-28-preflight-next.md`, new monitoring/Grafana procedure docs, and active wiki pages.
- Pages created: [[analyses/lint-2026-05-30]]
- Pages updated: [[sources/project-readme]], [[sources/project-todo]], [[entities/docker-host]], [[entities/monitoring-vm]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/frigate]], [[entities/proxmox]], [[entities/adguard-home]], [[entities/immich]], [[entities/homepage]], [[entities/dozzle]], [[entities/ventsys]], [[entities/esphome]], [[concepts/mqtt-tls]], [[concepts/tailscale-remote-access]], [[concepts/wireguard-vpn]], [[analyses/lint-2026-05-18]], [[index]]
- Notes: Synced docker-host Tier 1 live state, Grafana architecture dashboards, exporters, docker-host Fail2ban baseline, TLS-oriented MQTT posture, Frigate staging guardrails, and direct-link monitoring posture.

## [2026-05-30] update | Frigate Fail2ban hardening

- Canonical docs now include a docker-host patch-window runbook and a Frigate Fail2ban SSH jail template.
- Pages updated: [[entities/frigate]]
- Notes: VM 101 now has Fail2ban installed/enabled with an active `sshd` jail; Frigate app state remains unbuilt for regular use.

## [2026-05-31] update | Mobile monitoring access and Grafana metric labels

- docker-host now advertises `192.168.60.10/32` as a Tailscale host route for Grafana/Uptime Kuma mobile access only, with routed UFW allowances for ports `3000` and `3001`.
- Grafana datasource validation showed high unlabeled VM percentages are Proxmox guest-memory values, not CPU or disk saturation; `Proxmox Resource Overview` was re-exported and relabelled live.
- Pages updated: [[concepts/tailscale-remote-access]], [[entities/docker-host]], [[entities/monitoring-vm]], [[entities/proxmox]], [[sources/project-todo]]
- Notes: Mobile clients may still need the new route approved in Tailscale admin before they can use it.
## [2026-06-20] update | Shared-iGPU LXC migration
- Canonical project state now uses CT 111 for Frigate and CT 114 for local AI.
- Updated: [[entities/proxmox]], [[entities/frigate]], [[entities/home-assistant]], [[entities/llm-host]], [[index]]
- Notes: VM 101 and VM 104 are rollback-only; Overwatch search is live but recipe saving is not implemented.

## [2026-06-29] update | Config and documentation cleanup sync
- Canonical docs/configs were cleaned for stale router, MQTT, Frigate, VentSys, and local-AI references.
- Pages updated: [[entities/gl-mt6000]], [[entities/frigate]], [[entities/mosquitto-mqtt]], [[index]]
- Notes: Router wiki now matches the managed-switch port topology; Frigate wiki records the `mqtt.enabled: false` / `cameras: {}` baseline; MQTT wiki treats plaintext `1883` as a documented temporary recovery/bootstrap exception only.

## [2026-07-10] update | VLAN 50 router source/live reconciliation
- Canonical router source now uses the live internal `iot_sensors` identifier for VLAN 50 while preserving the public `HomeIoT` SSID.
- Pages updated: [[entities/gl-mt6000]]
- Notes: Full-profile read-only router validation passed; no router deployment occurred.

## [2026-07-10] update | Docker published-port enforcement
- Docker-host and monitoring Docker-published ports now use persistent, source-scoped `DOCKER-USER` policies with rollback snapshots and representative allow/deny proofs.
- Pages updated: [[entities/docker-host]], [[entities/monitoring-vm]]
- Notes: Tailscale identity/ACL proof remains owner-supervised; no broad port exposure was introduced.
