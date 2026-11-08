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

## [2026-07-28] update | Three-camera CCTV fleet and health alerts
- Pages created: [[entities/cctv-camera-fleet]]
- Pages updated: [[entities/frigate]], [[entities/home-assistant]], [[concepts/vlan-segmentation]], [[index]]
- Notes: Synced the wiki to canonical three-camera Frigate state, confirmed all three as ANNKE C500 `I51HJ` on firmware `v5.8.10 build 250917`, saved Zyxel ports 2-7 as CCTV VLAN 30 access ports, and recorded Home Assistant FPS-based offline/recovery alerts.

## [2026-07-28] lint | CCTV and Frigate state sync
- Report: [[analyses/lint-2026-07-28]]
- Pages repaired: [[entities/mosquitto-mqtt]] and the active CCTV/Frigate/HA entity set
- Notes: Historical source summaries remain historical; active entity pages now match canonical live state.

## [2026-07-29] update | DNS, Homepage, remote Frigate, and NAS operations
- Canonical project state now has all 48 `home.local` aliases deployed and validated on OpenWrt.
- Homepage exact-width regressions were repaired at 956 px and 489 px.
- Off-WiFi Frigate HTTPS access was validated through the narrow Tailscale host route while port 5000 remained blocked.
- OMV SMART monitoring was verified globally and on all five physical disks; the vault backup helper remains dry-run-only and no schedule was created.
- Pages updated: [[entities/gl-mt6000]], [[entities/homepage]], [[entities/openmediavault-nas]], [[index]].

## [2026-07-29] update | Homepage split-horizon mobile DNS
- Added an identity-gated AdGuard listener on docker-host's Tailscale address and an enabled rewrite for `homepage.home.local`.
- Added Tailscale split DNS for `home.local` plus phone-only DNS and HTTPS grants, preserving OpenWrt's LAN answer while using the tailnet answer remotely.
- The user confirmed the same `https://homepage.home.local/` bookmark works on mobile data and home WiFi.
- Pages updated: [[entities/adguard-home]], [[entities/homepage]], [[concepts/tailscale-remote-access]].

## [2026-07-29] update | Kuma storage and CCTV monitoring expansion
- Canonical state updated first in `main/TO-DO.md`, OpenWrt firewall source, and the current live-state reference.
- Pages updated: [[entities/monitoring-vm]], [[entities/openmediavault-nas]], [[entities/cctv-camera-fleet]], [[index]].
- Notes: Added host-scoped VLAN 60 paths and live ntfy-enabled checks for OMV web/NFS and all three cameras; recorded the remaining Frigate host-firewall, Grafana alerting, and ntfy mobile-subscriber gaps.
- Staged the OMV aggregate SMART push service and Kuma monitor without enabling
  either; VM 102's narrow host-firewall exception remains the activation gate.

## [2026-07-29] update | Monitoring alerting and ntfy backup completion
- Activated the OMV SMART push heartbeat and confirmed all five disks healthy.
- Added and live-tested Grafana's authenticated ntfy contact point, default
  policy, and initial docker-host/Proxmox disk-pressure alerts.
- Created the read-only ntfy mobile subscriber and validated authenticated
  polling; Android notification acceptance remains user-side.
- Deployed the SQLite-consistent ntfy app-data backup, completed a fresh NAS
  run, and passed a temporary restore/integrity smoke for both databases.
- Pages updated: [[entities/monitoring-vm]], [[entities/docker-host]].

## [2026-08-01] update | Docker-host maintenance and Mullvad download gateway
- Completed the controlled Docker/containerd/Compose/Python/Tailscale package
  window with no reboot required and all existing services healthy.
- Activated qBittorrent behind Gluetun/Mullvad, proved tunnel identity and
  interface-drop/full-provider-stop fail-closed behavior, and restored its
  configuration from the NAS backup in isolation.
- Pages created: [[entities/qbittorrent]].
- Pages updated: [[entities/docker-host]], [[entities/homepage]],
  [[entities/gl-mt6000]], [[entities/openmediavault-nas]], [[index]].

## [2026-08-01] lint | Maintenance and download-gateway state sync
- Report: [[analyses/lint-2026-08-01]].
- No stale stopped/gated Mullvad state or superseded VPN-rule name remained.
- Corrected the pre-existing index source count from 25 to the actual 21 and
  refreshed the analysis count to 5.

## [2026-08-01] update | Docker-host backup freshness monitoring
- Pages updated: [[entities/docker-host]], [[entities/monitoring-vm]].
- Notes: Kuma monitor 36 now receives the docker-host app-data backup heartbeat
  only after the existing backup service completes successfully; its first live
  delivery was accepted.

## [2026-08-01] update | Frigate API monitoring recovery
- Pages updated: [[entities/monitoring-vm]].
- Notes: CT 111 accepted the narrow monitoring-VM TCP 5000 exception; Kuma
  monitor 28 was re-enabled and returned `200 - OK`.

## [2026-08-09] update | Household Hub recipe workflow
- Created [[entities/household-hub]] for the live transcript RAG, recipe
  research and persisted confirmation-gated Mealie workflow.
- Updated [[entities/docker-host]], [[entities/llm-host]] and
  [[entities/home-assistant]] to reflect current service and ownership
  relationships.
- Updated [[index]] to 25 entities.

## [2026-08-09] lint | Household Hub state sync
- Report: [[analyses/lint-2026-08-09]].
- Confirmed the new Household Hub entity has inbound links and current ownership
  claims match canonical project state.
- Updated [[index]] to 6 analyses.

## [2026-08-09] update | Household Hub household integrations
- Added a dedicated-key, read-only Grocy overview and recorded its five-location
  live proof with empty stock and shopping-list state.
- Activated the persistent Obsidian Markdown staging outbox without writing raw
  LiveSync CouchDB documents.
- Required a matching persisted confirmation UUID for every Markdown write and
  proved an unconfirmed live request cannot create a file.
- Added downloadable `.ics` output for Nextcloud-compatible dry-runs while
  keeping live CalDAV upload disabled because Nextcloud is not deployed.
- Extended the NAS app-data job and completed backup run `20260809T130054Z` for
  the new Grocy key state and persistent Markdown outbox.
- Pages updated: [[entities/household-hub]], [[entities/docker-host]],
  [[analyses/lint-2026-08-09]], [[index]].
- Targeted changed-page links and index counts passed; the lint report records
  older unresolved knowledge-tool links for a later full-wiki cleanup.

## [2026-08-21] update | Homepage mobile fixed-proxy access
- Pages updated: [[entities/homepage]], [[entities/docker-host]],
  [[concepts/tailscale-remote-access]], [[index]].
- Notes: All user-facing Homepage cards now use fixed HTTPS proxy routes;
  Recomp Tracker was added at `8209`; the approved OnePlus identity receives
  only DNS, `tcp:443`, and `tcp:8180-8209` to docker-host.

## [2026-08-21] lint | Mobile Homepage proxy and Tailscale access
- Report: [[analyses/lint-2026-08-21]].
- Confirmed the updated Homepage, docker-host, and Tailscale pages agree with
  the canonical access matrix and retain the no-broad-subnet boundary.

## [2026-08-21] update | Mobile Homepage acceptance completed
- Phone-side mobile-data acceptance passed after reconnecting Tailscale and
  opening cards from every Homepage tab.
- Updated [[analyses/lint-2026-08-21]] so the completed acceptance is no longer
  reported as an open follow-up.

## [2026-08-21] update | Docker-host explicit network remediation
- Recreated every project Docker bridge at its canonical explicit allocation,
  including Household Hub's shared dependency networks and `local-alerting`.
- Application, storage, dependency, VPN-egress, allowed/denied and firewall
  checks passed. Bambuddy remains the only exception because the P1S path is
  unreachable from VM 103; its scoped bridge and firewall rules are prepared.
- Page updated: [[entities/docker-host]].

## [2026-08-25] lint | Architecture documentation reconciliation
- Report: [[analyses/lint-2026-08-25]].
- Repaired current topology, Tailscale routes, P1S/Bambuddy placement, OMV
  SMART/physical state, Immich storage and docker-host workload claims.
- Pages updated: [[entities/docker-host]], [[entities/openmediavault-nas]],
  [[entities/gl-mt6000]], [[entities/bambu-p1s]], [[entities/bambuddy]],
  [[entities/immich]], [[entities/homepage]], [[entities/tplink-ap]],
  [[entities/rpi-displays]], [[entities/minisforum-m1-pro-125h]],
  [[entities/minix-neo-z350]], [[entities/proxmox]],
  [[concepts/vlan-segmentation]], [[concepts/rag-vs-wiki-pattern]], [[sources/project-readme]],
  [[sources/proxmox-setup-guide]], [[sources/igpu-passthrough-guide]], [[index]].
- Notes: Historical sources/audits remain dated evidence; active wiki pages now
  match the canonical project references reconciled on 2026-08-25.

## [2026-08-25] update | Troubleshooting Dashboard staged acceptance
- Created [[entities/troubleshooting-dashboard]] and updated
  [[entities/docker-host]], [[sources/project-readme]], [[sources/project-todo]]
  and [[index]].
- Notes: Management-only port `8094`, explicit Docker network, real Windows
  snapshot, desktop/mobile flow and rollback proof are live; Proxmox backup
  snapshot acceptance and DNS/Homepage exposure remain open.

## [2026-08-25] lint | Troubleshooting Dashboard state sync
- Updated [[analyses/lint-2026-08-25]] and confirmed the new entity has inbound
  links from the index, docker-host and canonical source summaries.
- Confirmed access claims match the canonical service/access matrices and that
  missing Proxmox evidence remains an explicit open gate.

## [2026-09-04] update | Owner-confirmed NAS cabling and pending Hive LAN2
- Updated [[entities/gl-mt6000]], [[entities/openmediavault-nas]] and [[index]]
  after correcting the canonical cabling reference and network diagram sources.
- Owner confirmed OMV on router LAN4 / VLAN 40; GS1900 port 8 is spare storage
  access. This supersedes the incorrect August reconciliation claim.
- Recorded fibre-installation outage and pending Hive LAN2 research from
  [[../main/HANDOFF-2026-07-27-portal-services]]. LAN2 remains management VLAN 10;
  no live router change or availability verification was performed.
- Targeted consistency check: router and NAS entity tables agree with the
  corrected canonical physical map. Historical source/audit entries remain
  dated evidence. No new wiki page or index-count change was needed.

## [2026-09-04] update | Zen/Openreach WAN restored
- Updated [[entities/gl-mt6000]] from owner confirmation and LuCI screenshots:
  logical `wan`, physical `eth1`, PPPoE; Openreach requires no WAN VLAN tag.
- Canonical live state, cabling table, handoff and task list record the working
  mapping and the stale deployment-template gap. No credentials were copied.
- Proxmox restoration, IPv6 and old Wi-Fi-uplink retirement remain unverified.

## [2026-09-04] update | Post-fibre connectivity audit
- Updated [[entities/gl-mt6000]] and [[entities/docker-host]] against the
  authenticated router/Proxmox evidence in the canonical current handoff.
- IPv4 internet, 48 local DNS aliases, production guests and NAS backup
  storage are accessible. VM 103 has only 1 GiB configured with full swap and
  several failed app endpoints; all 2.4 GHz APs are down; IPv6 is not up.
- Hive is on management VLAN 10 pending isolation. Switch/cameras are
  intentionally disconnected. No live repairs were applied; endpoint replies
  are not full authenticated workflow or backup-write validation.

## [2026-09-04] update | Router SSH key and authenticated firmware/Wi-Fi check
- Updated [[entities/gl-mt6000]] and [[index]] from the canonical handoff and
  [[../main/docs/reference/current-live-state]]. Dedicated workstation key login
  is verified, with the existing laptop key preserved; no private key entered
  the vault.
- Confirmed vanilla OpenWrt 24.10.3/kernel 6.6.104 and live HomeAdmin channel
  100/HE80, approximately -76 dBm PC signal and 432 Mbps download PHY. Firmware
  reporting/counter quirks and upgrade candidates are in the canonical handoff.
- Later observed 2.4 GHz recovery and Hive on cloud-IoT VLAN 55 supersede the
  earlier audit's state; this task did not implement or accept those repairs.
- Targeted consistency check: wiki version/key/radio observations match the
  canonical follow-up; no firmware update or radio tuning was performed.

## 2026-09-04 — Post-fibre repair reconciliation

Updated router, Docker host and segmentation pages after canonical recovery
records: VM103 6 GiB and services restored; radio0 APs restored; WAN eth1 PPPoE;
LAN2 cloud VLAN55 / Hive .55.10 with WAN-only forwarding; NAS direct LAN4.
Targeted consistency review removed stale 1 GiB/current-down and ten-segment
claims in these pages. Index updated; no new pages or raw sources added.
Open: Zen IPv6 NoPrefixAvail, Hive app/account status, P1S setup, unplugged
switch/cameras, weak HomeAdmin radio signal. Sources are current-live-state,
physical cabling reference, guest inventory and the current portal handoff.

## [2026-09-05] analysis | Household, Workshop and Operations Product Roadmap

- Created [[analyses/household-workshop-operations-roadmap-2026-09]] and
  updated [[sources/project-todo]] and [[index]].
- The canonical roadmap starts with read-only evidence, then sequences Today
  at Home, recovery/diagnostic evidence, food workflow, workshop inventory and
  hardware-gated VentSys commissioning.
- It records complementary performance, drift, maintenance, capacity, document,
  job-state and power-continuity ideas as individually gated work. No service,
  credential, automation, inventory or safety state changed.
- Corrected the current summary in [[sources/project-todo]] so live OMV/Frigate
  foundations and disconnected or uncommissioned physical integrations remain
  distinct.

## [2026-09-06] create | Home Operations Workbench proof of concept

- Created [[entities/home-operations-workbench]] and updated
  [[analyses/household-workshop-operations-roadmap-2026-09]] and [[index]].
- The canonical implementation is `main/apps/home-operations-workbench/`: a
  local schema-1.0 evidence viewer with Today, possible shared dependencies,
  recovery evidence, meal availability and a visual-only VentSys checklist.
- Model tests and desktop/mobile browser smoke checks passed. It has no live
  connection, deployment, credential, control, persistence or source-system
  write path; this operation did not change home-automation state.

## [2026-09-07] reconcile | Project health and offline evidence adapters

- Canonical README/current-state/task/update-review and recovery test-card documents reconciled before wiki updates.
- Updated `pages/sources/project-todo.md`, `pages/entities/home-operations-workbench.md` and index: offline health imports, freshness and restore boundaries, CT114 package-access and Watchtower notification gaps.
- No live deployment, physical acceptance or fresh Proxmox/OMV proof inferred from historical records.


## [2026-09-10] update | Documentation and troubleshooting reconciliation

- Updated [[sources/troubleshooting-reference]], [[sources/project-todo]],
  [[entities/troubleshooting-dashboard]] and [[index]] after canonical manuals,
  references, task list and current handoff were updated.
- Written offline walkthroughs cover the five app symptoms and link canonical
  Mermaid views. A shared media operating manual distinguishes configuration,
  libraries, stopped checkpoints and isolated restore proof.
- Corrected LAN2 recovery, NAS attachment, disconnected-camera/P1S and DHCP
  assumptions. Incorporated the separately recorded deployed freshness update,
  Windows evidence, blocked Proxmox collector update and IPv6 discrepancy.
- Targeted wiki consistency review only: matched these claims to canonical
  state and app deployment records. No raw sources changed, no new pages,
  no full-wiki lint or new live-system verification claimed.


## [2026-09-10] update | Service lifecycle and rebuild sequencing

- Updated [[sources/troubleshooting-reference]] and [[sources/project-todo]]
  after canonical gateway/Recomp/MediaMTX manuals and phase dependencies.
- Household Hub's mirrored Compose is not a complete application build or
  database recovery source; documented the missing separate-repository contract.
- Corrected authenticated dashboard guidance and diagnostic interpretation.
  Targeted source consistency only; no live rebuild, notification or restore.

## [2026-09-11] update | Search and notification lifecycle manuals

- Updated [[sources/project-todo]] and [[sources/troubleshooting-reference]]
  after canonical ntfy/Watchtower/SearXNG/Whoogle manuals and task/handoff changes.
- Recorded SearXNG missing settings/template and separate configuration-backup
  requirement; retained Watchtower notification failure and phone/restore gates.
- Targeted consistency review against canonical source only; no raw changes,
  new pages, full-wiki lint or live-service acceptance.

## [2026-09-11] update | Rebuild dependency follow-up

- Updated [[sources/project-todo]] after Phase07/08 and START-HERE sequencing
  repairs, MediaMTX checkpoint documentation and Hub recovery-lead links.
- Canonical source consistency checked; no raw changes or live acceptance.


## [2026-09-11] update | Extended diagnostic routes

- Updated [[entities/troubleshooting-dashboard]] after canonical app/hand-off
  recorded 27 deployed routes and their generated offline companion.
- Targeted consistency check corrected the five-route claim; existing source
  links retained. No raw changes, new wiki pages or whole-wiki lint.

## 2026-09-11 — Zen IPv6 accepted live

Zen portal allocations were reconciled with live packet evidence. After PPPoE
release/reconnect, DHCPv6-PD offered the supplied `/48`; prefix-only mode avoids
Zen's expected IA_NA `NoAddrsAvail`. Added the supplied ND `/64` router address
and link-local default route. Both interfaces survived reload; IPv4 and IPv6
internet tests pass. Canonical current state, handoff, router source/compiler
and router wiki entity were updated. Restricted VLAN IPv6 policy was unchanged.

## [2026-09-11] update | Backup phase prerequisites and recovery checks

- Updated [[sources/project-todo]] from canonical Phase10/checklist/handoff.
- Recorded heartbeat installation dependencies, dated-run recovery selection
  and VM/CT isolation checks. No raw changes or live acceptance claimed.

## [2026-09-11] update | Final-phase dependency review

- Updated [[sources/project-todo]] after canonical Phase09/11/12 corrections.
- Preserved disconnected-camera and uncommissioned-printer status, separate
  Watchtower configuration recovery and partial-acceptance limits. No raw changes.

## [2026-09-11] update | Consolidated service documentation audit

- Updated [[sources/project-todo]] after canonical 42-entry coverage table,
  START-HERE/index navigation and task/handoff updates.
- Distinguished written procedures, nine review rows, missing artifacts and
  candidates; no whole-system rebuild or live acceptance claimed. No raw changes.

- 2026-09-11: Updated [[entities/troubleshooting-dashboard]] for owner-approved Homepage Tools preview; direct management access and outstanding Proxmox evidence gate retained. Source: portal services handoff.

## [2026-09-11] update | Nine remaining documentation reviews completed

- Updated [[sources/project-todo]] from canonical service/phase lifecycle changes.
- Counts now 32 Written, 0 Review, 4 missing source/configuration, 6 Candidates.
- GardenKeeper source/dump defect and VM103 SSH denial remain explicit;
  no raw changes, authentication changes or live restore evidence claimed.

## [2026-09-11] update | Docker-host SSH identity correction

- Updated [[sources/project-todo]] to correct the earlier access-blocker claim.
- Existing alias/key works; local IP pattern now selects it too. Both verified;
  no server authentication or firewall changes. Source recovery remains open.

- 2026-09-11: Updated [[entities/troubleshooting-dashboard]] with DNS/TLS findings and bounded collector failure categories; canonical portal handoff records the Vaultwarden routing repair.

## [2026-09-11] update | Live application migration contracts

- Updated [[sources/project-todo]] from read-only VM103 source/schema inspection.
- GardenKeeper reset migrations and Hub startup migration boundary documented;
  provenance/off-host artifacts and restore proof remain open. No raw changes.

## [2026-09-11] update | Protected source and settings checkpoints

- Updated [[sources/project-todo]] after source/settings hash verification.
- Recovery files remain outside the vault under restricted workstation ACLs;
  no live service change or full restore acceptance claimed. No raw changes.

- 2026-09-12: Recorded owner Mullvad/local-name decision in [[entities/troubleshooting-dashboard]] from the canonical DNS resolver decision; elevated hosts application remains pending.

## [2026-09-14] update | Recovery implementation and isolated acceptance

- Updated [[sources/project-todo]] after canonical backup/restore/source-build
  evidence, SearXNG semantic review and MediaMTX owner retention decision.
- No raw changes or full-system certification; archive paths stay in canonical
  runbooks and secret-bearing artifacts remain outside the vault.

- 2026-09-14: Homepage Vaultwarden direct card deployed and normal browser HTTPS verified; canonical portal handoff records GardenKeeper success and the persistent Proxmox SSH evidence gate.

- 2026-09-14: Updated [[entities/troubleshooting-dashboard]] from the canonical handoff: Proxmox SSH unblocked and fresh evidence validated; browser import and archive restore remain distinct gates.

- 2026-09-15: Reconciled [[entities/troubleshooting-dashboard]] and canonical task/app records with successful real Proxmox JSON browser import. VM102 isolated restore preflight documented separately.

## [2026-09-15] update | Notification and recovery proof

Updated [[sources/project-todo]] from canonical service runbooks, task list and
handoff: bounded Watchtower notification accepted by ntfy, coordinated Hub
checkpoint restored, ten offline images loaded and checked. Phone delivery,
source builds and full-system proof remain separate. No raw files changed.

- 2026-09-16: Recorded all five September15 Proxmox archive verification passes in the canonical handoff/task list. CT114 recheck exit0 is retained on-host; isolated guest restore remains open.

## [2026-09-16] update | Offline source builds and report semantics

Updated [[sources/project-todo]] after canonical runbooks/handoff: all six builds
passed offline; scheduled ntfy delivery succeeded; Watchtower available-update
count corrected and regression-tested. Preserved remaining phone/full-system
acceptance limits. No raw material changed.

## [2026-09-16] update | Recovery handoff ownership

Updated canonical handoff with remaining tasks, acceptance criteria and owner/agent
responsibility; reflected ownership in [[sources/project-todo]]. Phone receipt is
owner input; technical recovery follow-up remains agent work. No raw files changed.

## [2026-09-16] update | GardenKeeper journal-media persistence

- Created [[entities/gardenkeeper]] and updated [[sources/project-todo]] after
  the canonical service manual recorded the persistent media mount and OMV
  backup inventory.
- The production API was the only recreated container; its health and readiness
  checks passed. The isolated proof used a synthetic image only, so no user
  photo or full integration recovery is claimed.
- No files under `wiki/raw/` changed.

## [2026-09-18] update | Household Hub recovery repository

- Updated [[entities/household-hub]] after canonical source-recovery records
  documented the owner-authorized local recovery repository and initial commit.
- The repository is seeded from a protected verified archive, has no remote,
  and does not restore the original Git provenance. No files under `wiki/raw/`
  changed.

## [2026-09-27] update | Wired admin PC on router LAN5

- Updated [[concepts/vlan-segmentation]] after canonical OpenWrt source and
  current-live-state recorded LAN5 tagged VLAN 10 plus untagged VLAN 1 recovery.
- The PC obtained management DHCP over Ethernet. LAN3 retained the managed-switch
  trunk role. Corrected the initial NAS dependency claim: OMV is directly on
  router LAN4, and the disconnected switch does not carry its current path.
- No files under `wiki/raw/` changed.

## [2026-09-27] update | Main Duct Valve 1 bench controller

- Updated [[entities/ventsys]] and [[entities/esphome]] from the canonical
  current-live-state record after a new ESP32 D1 Mini was flashed as Valve 1
  and registered in HA. Its servo remains disconnected and uncalibrated.
- Corrected the historical Valve 1 MAC so it is not mistaken for the new board.
- No files under `wiki/raw/` changed.
## [2026-09-28] update | OMV workstation SMB access

- Updated [[entities/openmediavault-nas]] after canonical NAS manual and live
  state recorded full `nasadmin` filesystem ACLs on the `NAS` and `14tb` SMB
  share trees, with OMV-side write probes and pre-change ACL backups.
- No files under `wiki/raw/` changed.

## [2026-09-30] update | Homepage mobile access contract

- Updated [[entities/homepage]] and [[concepts/tailscale-remote-access]] after
  canonical docs recorded standalone/proxy routing parity, separate Bambuddy
  listener ownership, historical failure classes and the regression gate.
- No files under `wiki/raw/` changed.

## [2026-09-30] update | Recurring-incident troubleshooting routes

- Updated [[entities/troubleshooting-dashboard]] from the canonical app manual
  and live-state inventory after deployment of 37 routes, guidance search,
  investigation-only deep links and corrected commissioned P1S/FTPS context.
- Regenerated offline routes from maintained source. No `wiki/raw/` files changed.

## [2026-09-30] update | OMV desktop SSH access

- Updated [[entities/openmediavault-nas]] from the canonical OMV manual and current-live-state after verifying desktop root key login. No passwords or private keys recorded; no wiki/raw files changed.


## [2026-09-30] update | SMB backing storage

- Updated [[entities/openmediavault-nas]] with verified separate backing devices for NAS and 14tb; canonical filesystem UUID mapping is in the OMV manual.

## [2026-10-02] update | Roadmap, code and file audit

- Reconciled [[pages/analyses/household-workshop-operations-roadmap-2026-09]] and
  [[sources/project-todo]] with the canonical October2 audit and task list:
  37-route diagnostics, accepted historical Proxmox import, commissioned P1S
  baseline, fresh OMV SMART, tested Hub read-only Grocy source and remaining
  product/physical gates. No raw sources changed; no new live feature claimed.

## [2026-10-02] update | CT114 package-path diagnosis

- Updated [[sources/project-todo]] from the canonical repair procedure/log:
  confirmed absent Fail2ban, expired indexes and distinct client-firewall/proxy/
  upstream boundaries. Prepared source is tested; no live deployment claimed.

## [2026-10-02] update | Curated local recovery evidence

- Updated [[entities/home-operations-workbench]] and [[sources/project-todo]]
  after seven historical records passed local import/export and desktop/320px
  checks. Partial restores remain scoped, backup observations stale and live
  deployment absent. No raw wiki sources changed.


## [2026-10-02] update | Bambuddy staged offline updates

- Updated [[entities/bambuddy]] from the canonical update procedure and live-state inventory: owner-approved workstation staging, idle-gated VM103 installation, NAS checkpoints and first manual 1.2.5.6 proof. Watchtower remains monitor-only; no raw sources changed.

## [2026-10-02] update | Recurring Hub backup preparation

- Updated [[entities/household-hub]] and [[sources/project-todo]] after ten
  isolated tests, unit-template verification and successful live read-only
  preflight. Source is undeployed; one-off backup proof is separate from new-job
  generation/restore and scheduled acceptance. No raw sources changed.

## [2026-10-02] update | Saved Grocy overview conversion

- Updated [[entities/home-operations-workbench]] and [[sources/project-todo]]
  from the canonical release contract/manual after sixteen unit tests and
  desktop/320px fresh/stale/unavailable imports passed. Synthetic acceptance
  remains separate from real inventory, authenticated adapters and deployment.
  No raw sources changed.

## [2026-10-02] update | Direct saved Grocy imports

- Updated [[entities/home-operations-workbench]] from the canonical release
  contract: the existing picker accepts saved Grocy envelopes directly with
  freshness calculated at import. Desktop/320px BOM, error and Clear checks
  pass; no live source access or deployment occurred.

## [2026-10-02] update | Portable selected recovery runbooks

- Updated [[entities/home-operations-workbench]] and [[sources/project-todo]]
  after seven systems/13 documents passed portable-pack, checksum/tamper,
  path/overwrite, credential-candidate and Windows junction checks. Twenty unit
  tests pass;54 omitted references and full-estate/data/image recovery remain
  explicit. No raw wiki sources or live systems changed.

## [2026-10-02] update | Dashboard IPv6 read-only preflight

- Updated [[entities/troubleshooting-dashboard]] and [[sources/project-todo]]
  from fresh binding/bridge/rule/counter inspection and two failed client probes.
  Source-only denial passes an isolated recording-executable test;16 system tests
  pass. No live firewall change or complete denial acceptance is claimed.

## [2026-10-02] update | OMV host-local collector preparation

- Updated [[entities/openmediavault-nas]] and [[sources/project-todo]] after six
  isolated tests and a live read-only JSON snapshot. Current RAID sync is idle;
  SMART passed coexists with explicit lifetime CRC/history warnings. Scheduled
  collector, metric shipping and NAS dashboard remain undeployed. No raw wiki
  sources, credentials or NAS policy changed.

## [2026-10-02] update | Verified audit source remediation

- Updated [[entities/openmediavault-nas]] from canonical audit remediation and
  read-only live helper inspection. Source tests pass; production deployment
  and isolated restore acceptance remain open. No raw sources changed.

## [2026-10-02] update | TransferPortal recovery gate accepted

- Updated [[entities/openmediavault-nas]] from canonical evidence. Protected
  stopped NAS checkpoint and saved/repaired-generation no-NIC restore/preview/
  copy/helper-denial tests passed; disposable VM/media removed. Live generation
  unchanged and still awaiting hardened replacement. No raw sources changed.

## [2026-10-03] update | GardenKeeper synthetic recovery rehearsal

- Updated [[entities/gardenkeeper]] from canonical tooling/runbook and passed
  isolated PostgreSQL/media acceptance. Live and full-system recovery gates
  remain open. No raw sources changed.

## [2026-10-04] update | OMV atomic snapshot handoff preparation

- Updated [[entities/openmediavault-nas]] from the canonical collector contract:
  atomic publisher and restricted unit templates pass11 Linux tests and unit
  syntax checks. Dedicated group/device/capability/cadence acceptance and all
  installation/shipping remain open. No raw sources or live NAS state changed.

## [2026-10-04] update | OMV snapshot metrics conversion preparation

- Updated [[entities/openmediavault-nas]] after canonical procedure and task
  updates. Stdout conversion preserves missing/invalid/stale and unknown states;
  all18 Linux tests pass. Integration and live shipping remain open. No raw
  sources or live NAS state changed.

## [2026-10-04] update | OMV Telegraf parser rehearsal

- Updated [[entities/openmediavault-nas]] after canonical procedure/task updates.
  Five isolated synthetic cases match exact metric tags/fields/values against
  Telegraf1.38.3; no output or production configuration was used. Prepared
  OMV-local input remains undeployed. No raw sources changed.

## [2026-10-04] update | OMV current-state query and failure preparation batch

- Updated [[entities/openmediavault-nas]] from the canonical query/input and
  acceptance contract. Nineteen synthetic cases pass32 actual Flux executions
  with no bucket access; old healthy values, expired observations and unknown
  units remain distinct. Live delivery and UI/alert acceptance are still open.
  No raw sources or production configuration changed.

## [2026-10-04] repair | Monitoring roadmap current-state reconciliation

- Updated [[entities/monitoring-vm]] after canonical roadmap repairs: camera
  checks remain historical while cameras are disconnected; OMV administration
  is available but new metrics delivery remains prepared; Homepage preview is
  distinct from parked HA embedding. No live services or raw sources changed.

## [2026-10-04] repair | Local AI host allocated resources and package blockers

- Updated [[entities/llm-host]] after canonical manual/current-state updates.
  Read-only Proxmox configuration confirms6 cores/28 GiB/no swap, superseding
  conflicting4-core/10–20 GiB descriptions. Package/security blockers remain
  observed; no resource allocation, firewall, packages or services changed.

## [2026-10-04] repair | Historical wiki navigation and methodology

- Created the seven missing source-backed stubs: [[entities/obsidian]],
  [[entities/qmd]], [[entities/marp]], [[entities/dataview-plugin]],
  [[entities/obsidian-web-clipper]], [[concepts/personal-knowledge-management]]
  and [[concepts/memex]]. Optional tool adoption remains unverified.
- Qualified links in [[sources/llm-wiki-idea-file]] and
  [[concepts/rag-vs-wiki-pattern]], updated the index and actual page counts.
  Corrected the broad claim that RAG has no durable knowledge, using the original
  RAG paper and canonical Hub state. Raw sources and historical log entries
  remain unchanged; no tools were installed.

## [2026-10-04] update | Solar Observatory local foundations

- Updated [[entities/ventsys]] from the canonical screensaver procedure:
  tested astronomy/camera/safety-protocol foundations and local cache exist,
  but renderer, HA browser integration and Pi acceptance remain open. Corrected
  the historical public-token configuration claim to the current token-free
  bridge contract. No raw sources or live deployments changed.

## [2026-10-04] update | Solar Observatory geometry preview

- Updated [[entities/ventsys]] after the local single-renderer preview passed
  build, 26 unit and seven Chromium browser tests. Earth/Moon, Jupiter/Io and
  Saturn views exist; final imagery, HA host integration and Pi acceptance are
  still open. No live dashboard, HA configuration or raw sources changed.

## [2026-10-04] update | Saved GardenKeeper task import

- Updated [[entities/home-operations-workbench]] and [[entities/gardenkeeper]]
  after the canonical release plan and roadmap: bounded pending-task selection,
  explicit freshness and UTC due times, no private notes or source writes.
  Twenty-five unit tests and three desktop/mobile browser suites pass. The
  schema-only live read does not establish a real-data pilot or deployed adapter.

## [2026-10-04] update | Workbench import-state audit

- Updated [[entities/home-operations-workbench]] after the canonical release
  plan: pending reads cannot undo Clear, demonstration or newer imports;
  dependency counters state their scope. All25 unit tests and three browser
  suites pass, including controlled delayed reads at desktop/mobile sizes.
  This is local verification; live hosting and genuine source acceptance remain open.

## [2026-10-04] update | Strict saved evidence time

- Updated [[entities/home-operations-workbench]] from the canonical release
  plan: shared strict calendar/clock/offset validation across health, Grocy and
  GardenKeeper. Slightly future health records and24:00 rollover stay unknown,
  including backup freshness. All28 unit tests and three desktop/mobile browser
  suites pass. No live services, raw sources or collection schedules changed.

## [2026-10-04] update | Solar Observatory read-only mock host

- Updated [[entities/ventsys]] from the canonical screensaver procedure:
  local candidate host forwards only fixed display state, expires lost delivery
  and latches failsafe interruption across reloads with session storage.
  Build, 29 unit tests and 14 browser tests pass. The host remains simulated;
  authenticated HA acceptance, final assets and Pi performance remain open.
  Existing dashboard/card and live deployments are unchanged.

## [2026-10-04] update | Saved Mealie meal-plan import

- Updated [[entities/home-operations-workbench]] after the canonical roadmap
  and release plan. Explicit calendar selection and bounded private-field-free
  meal display are locally verified with33 unit tests and three browser suites.
  Public schema metadata was the only live read. Ingredient availability,
  household pilot and live release remain unaccepted; raw sources unchanged.

## [2026-10-04] update | Solar Observatory first imagery pass

- Updated [[entities/ventsys]] from the canonical screensaver procedure: local
  NASA Earth/Moon surface maps and an attributed ESO Milky Way photograph now
  replace part of the proof imagery. Orientation is illustrative, not live
  surface attitude; remaining bodies retain proof geometry. Build, 29 unit
  tests and 17 browser tests pass, including image failures and bounded texture
  counts. No HA deployment or physical-device performance claim was made.

## [2026-10-04] update | Combined saved household sources

- Updated [[entities/home-operations-workbench]] after the canonical release
  plan and roadmap: explicit three-source composition, independent freshness,
  unavailable isolation, atomic rejection and reserved source observations.
  All38 unit tests and three browser suites pass; household pilot, Recomp and
  live release remain open. No source API calls, writes or raw-source edits.

## [2026-10-04] update | Recomp and four-source Today composition

- Updated [[entities/home-operations-workbench]] after the canonical release
  plan: weekday and one-off routine projection, privacy and unknown completion/
  readiness; explicit four-source bundle with older format compatibility.
  All45 unit tests and three browser suites pass. No live personal records,
  source writes or raw-source edits; household pilot/live release remain open.

## [2026-10-04] update | Solar Observatory body attitude

- Updated [[entities/ventsys]] from the canonical screensaver procedure:
  approximate IAU Earth/Moon attitude, independent of orbital paths, now uses
  bounded UTC-to-TDB conversion. Sixteen SPICE samples validate the text-PCK
  model, not precision navigation accuracy. Build, 49 unit tests and19 browser
  tests pass; unsupported attitude dates retain an explicit fallback and safety
  display. Remaining assets, live HA acceptance and Pi verification stay open.

## [2026-10-04] update | Main Valve 2 identity and servo state

- Updated [[entities/ventsys]] and the index from the canonical Valve 2 YAML
  and current live-state reference. COM4 MAC `EC:E3:34:B4:79:7C` belongs to
  Valve 2; its normal three-wire servo firmware removes feedback entities,
  restores the displayed last command, and republishes MQTT state after
  connection. HA shows the device online at 100. Physical position and a
  non-100 power-loss restoration remain unverified.

## [2026-10-06] update | VentSys E2 and MAIN-2 board assignments

- Updated [[entities/ventsys]] from the canonical live-state and valve wiring reference. MAC `EC:E3:34:B4:79:7C` is E2 at `.52`; MAC `EC:E3:34:67:A0:18` is the newly flashed MAIN-2 at `.57`. HA native and MQTT controls are online for MAIN-2 with command 50, while mechanical travel remains uncalibrated. The old MAIN-1 board association was retired; no installed MAIN-1 board was verified.

## [2026-10-10] update | FDM intake board power-control test

- Updated [[entities/ventsys]] and [[index]] from canonical current-live-state,
  TO-DO and procedure docs. FDM 360 intake `.61` was flashed over COM8 with the
  shared ESPHome board controls; esptool confirmed base MAC
  `cc:ba:97:f0:e3:ec` and verified written data. HA later showed `-55 dBm`
  Wi-Fi telemetry. At 09:52:11, HA logged the new Restart Board entity changing
  from `Unavailable` to `Unknown` and displayed “Pressed”; activity details
  record no cause, so this is not evidence of button activation. No valve
  movement was commanded. Power Off and
  physical reset/power-cycle wake acceptance remain open; VentSys is still
  uncommissioned. The HA Builder compile attempt stalled during ESP-IDF setup
  and was stopped; the verified COM8 flash used the local ESPHome 2026.4.5 CLI.

## 2026-10-10 — VentSys OTA rollout and hardware correction

- Updated VentSys entity from canonical power-control procedure/current-live-state: six online OTA updates, production persistence, archived SLA 0x77 wiring correction and successful MAIN-2 independent-supply software restart. Physical acceptance and reset root cause remain open.

## [2026-10-10] update | FDM/SLA 360 intake identity correction

- The owner requested swapping the 360 intake identities. HA device details
  verified the old FDM record at `.61` was MAC `CC:BA:97:F0:E3:EC` and old SLA
  record at `.62` was MAC `A0:85:E3:AE:5B:C8`. The role names are swapped while
  the observed IP/MAC pairs stay together: FDM `.62` / `A0:85:E3:AE:5B:C8`,
  SLA `.61` / `CC:BA:97:F0:E3:EC`.
- Updated canonical DHCP source/setup instructions, all 360 profile IPs, and
  VentSys current-state, adoption, and power-control records. Synced and
  SHA-256 checked the two HA Builder configs. HA labels and live firmware topics
  still use the previous identities; Builder reported both boards offline and
  the P1S dashboard showed a running print, so OTA was deferred. Apply each
  profile at its existing IP later, then verify HA names and MQTT topics before
  valve use.
- Updated [[entities/ventsys]], [[sources/openwrt-dhcp-config]],
  [[sources/esphome-adoption-guide]], and [[index]].

## [2026-10-10] update | Frigate memory incident recovery

- Corrected [[entities/frigate]] from stale live-camera status to the canonical
  disconnected/disabled state. Recorded the confirmed idle ZeroMQ publisher
  retention mechanism, 12 GiB CT allocation, pinned existing image, healthy
  service recovery, and lifecycle-fix gate before camera re-enable. Evidence
  and rollback live in `main/docs/install/phases/04-frigate.md` and
  `main/docs/reference/current-live-state.md`.
- Targeted consistency check also repaired stale live-camera claims in
  [[entities/proxmox]], [[entities/cctv-camera-fleet]] and [[index]]. Camera
  reservations remain preserved; physical reconnection and sustained lifecycle
  acceptance remain open.

## [2026-10-10] update | Whole-host resource audit and pressure alerts

- Canonical [[../main/docs/procedures/resource_pressure_monitor]] records all
  eight guest inspections, VM102's historical Grafana OOM and applied6GiB
  allocation, VM103's online64→128GiB root expansion, and remaining host capacity.
- Updated [[entities/proxmox]], [[entities/monitoring-vm]] and
  [[entities/docker-host]] to current allocations. The Proxmox minute timer
  independently samples six systems and routes actual pressure/OOM/stall alerts
  through authenticated ntfy. An hourly Codex watchdog checks collector health.
  Four tests and recurring live coverage pass; handset presentation remains open.

## [2026-10-10] update | Frigate permanent local lifecycle repair

- Updated [[entities/frigate]], [[entities/proxmox]], [[entities/cctv-camera-fleet]]
  and [[index]] after canonical source/deployment and RAM reassessment.
- The pinned-image read-only overlay gives the configuration PUB socket one
  owner thread, serialized multipart publishing and idle lifecycle cleanup.
  Three functional tests,3600-reconnect tests and12000 live reconnects passed;
  live main RSS grew only1.6MiB. Separate synthetic three720p/10fps OpenVINO
  and recording load used~1.2GiB and recovered after two FFmpeg interruptions.
- CT111 returned12→6GiB, healthy at~670MiB working memory, with no new OOM.
  Test container/media removed. Cameras stay disabled pending physical and
  sustained real-stream acceptance. Canonical evidence, operations and rollback:
  [[../main/docs/install/phases/04-frigate]].

## [2026-10-11] update | Resource monitor error handling

- Updated [[entities/monitoring-vm]] against canonical monitor procedure/live
  state: partial inventory-timeout coverage, debounced collection failures,
  durable cooldown/recovery and queued delivery through condition recovery.
  Removed the notifier's start-limit latch and cleared historical failed state.
- Ten tests and six-system live collection pass. Watchdog uses supported
  `--status`, including health and pending delivery, without temporary helpers.
  Guest allocations/services were not changed. Phone presentation remains open.

## [2026-10-11] update | Resource Health and interactive troubleshooting

- Updated [[entities/troubleshooting-dashboard]] from the canonical service
  manual and current-live-state: live Homepage Resource Health, independent
  one-way metrics publication, bounded VM103 ping/DNS/TCP/HTTP console,
  incident-report evidence and preserved imported-status semantics.
- Reconciled obsolete no-probes wording;20 model/10 API tests and live guided
  and HTTPS desktop/mobile flows passed. No new guest or general SSH access.

## [2026-10-11] update | Certificate checks, bundles and incident timeline

- Updated [[entities/troubleshooting-dashboard]] against its canonical manual
  and current-live-state: four TLS targets, nine cancellable bundles for37
  routes, and30-day/1,000-event history with timed Grafana/log links.
-28 backend tests and desktop/mobile extension checks passed. Live checks found
  missing Home Local CA key-usage extension; strict failure stays visible,
  while separate legacy chain/name/date trust passes. Planned CA maintenance
  is recorded in canonical TLS procedure/task list.

## [2026-10-12] update | MAIN-1 three-wire board adoption

- Updated [[entities/ventsys]] from the canonical firmware and live-state
  record: MAIN-1 MAC `EC:E3:34:67:8C:9C` at `.51` is flashed and adopted in HA.
  Its normal servo has no feedback entities; physical travel remains
  uncalibrated and VentSys remains uncommissioned.

## [2026-10-11] update | E1 branch board adoption

- Updated [[entities/ventsys]] from the canonical firmware and live-state
  record: E1 MAC `EC:E3:34:67:0D:28` at `.53` is flashed and adopted in HA.
  Its normal servo remains uncalibrated; VentSys is not commissioned.

## [2026-10-11] update | Resource alert phone delivery failure

- Updated [[entities/monitoring-vm]] from canonical ntfy manual/live state:
  accepted test alert/recovery did not reach the phone; zero server subscribers
  and a disconnected ntfy subscription despite active Tailscale. Endpoint
  HTTPS and ACL checks passed; phone connection diagnosis remains open.
- CA migration dependency/rollback plan prepared; production certificates and
  Frigate remain unchanged.

## [2026-10-18] update | Pocketry Homepage integration
- Updated [[entities/homepage]] from canonical Pocketry service manual/live state: local cutout-bin app and shared Tools card; browser-local backups and unverified mobile port recorded.


## [2026-10-18] update | VentSys dashboard range and audit

- Updated [[entities/ventsys]] from the canonical audit/live-state record: full
  0–100 dashboard and mode-script range deployed; physical calibration unchanged.
- Corrected live/candidate distinction and recorded public credential exposure
  and state/sensor findings. VentSys remains uncommissioned.

## [2026-10-19] update | Authenticated VentSys dashboard

- Updated [[entities/ventsys]] and index from the canonical dashboard manual/live
  state: direct HA card deployed, public credential removed and dedicated token
  revoked; reviewed requests, explicit unknown/stale state and corrected sensors.
- Recorded software/browser/live HA verification without physical actuation and
  retained the 360 firmware range/identity/commissioning gates.

## [2026-10-19] update | Homepage VentSys entry

- Updated [[entities/ventsys]] and [[entities/homepage]] from the canonical
  manuals: Home & Security Open tab uses the existing authenticated HA proxy.
- Recorded desktop/mobile viewport and served-asset verification; no new
  credential, control iframe, network listener or firewall rule was added.

## [2026-10-19] correction | 360 firmware accepted; dashboard legacy IDs

- Updated [[entities/ventsys]] and index from owner clarification plus registry
  MACs/Builder substitutions: firmware and logical topics are already correct.
- Dashboard legacy entity prefixes are reversed relative to current physical
  roles. Corrected candidate/read-confirmation contract is prepared and tested;
  activation awaits normal HA sign-in. Missing hardware is expected during setup.

## 2026-10-19 — VentSys role correction activated

- Reconciled canonical manual, current live state and VentSys entity after normal
  HA sign-in activated release `20261019-1`. Both intake ranges and no-command
  state verified; 53 tests passed. Firmware and command topics unchanged.
- Targeted wiki reconciliation: removed stale open role-reassignment claim;
  physical commissioning remains separate. No raw sources changed.

## 2026-10-19 — VentSys shared command arbitration

- Reconciled VentSys entity/index with canonical backend revision
  `20261019-arbitration-1`: named normal scripts share a dispatcher; fire response
  preempts normal execution and includes explicit main-fan 100%.
- Eight policy, 11 backend and three drift tests plus isolated real HA no-MQTT
  contention/preemption/failsafe probe passed. Temporary probe removed; production
  loaded idle without actuator commands. Direct/native bypass limits and separate
  physical commissioning retained. Targeted authority/link reconciliation passed;
  raw sources unchanged.

## 2026-10-19 — SLA airflow controller adoption

- Reconciled [[pages/entities/ventsys|VentSys]] with canonical live-state record:
  SLA airflow ESP32-C6 `CC:BA:97:F0:D3:10` was flashed and adopted in HA Garage
  at `192.168.50.42`. Physical airflow and pulse response remain untested.
- Corrected the installed SLA airflow GPIO pair to GPIO0 Hall pulse and GPIO1
  external LED data after owner wiring clarification; reflashed and verified.

## 2026-10-19 — VentSys touch view

- Reconciled entity/index with canonical frontend `20261019-4`: separate touch
  route, pop-up controls, original-style title/header and bottom status strip;
  standard view and diagram coordinates retained. Current source/status replaces
  original demo airflow/fixed uptime. Two highlight overruns fixed, logs enlarged.
- 30 browser tests and live popup/config/hash acceptance passed without actuator
  commands. Physical seven-inch acceptance remains separate. Targeted authority/
  relationship reconciliation completed; raw sources unchanged.

## [2026-10-19] update | Recomp Tracker one-time meal estimates

- Updated [[entities/docker-host]] from the canonical Recomp Tracker service
  manual and current live state: r16 stores manual one-time meal estimates only
  on their selected diet day, outside the Food Library and outside copied days.
- Recorded the healthy release/checkpoint boundary; no raw sources changed.

## 2026-10-19 — VentSys owner-test failure and command repair

- Corrected canonical/wiki claims after owner physical testing exposed crossed
  intake command routing, strict full-mode blocking and stale E2 HA host.
- Actual running-firmware logs, not differing Builder YAML, now establish intake
  topics. E2 native connection recovered at `.52`; explicit available subsets and
  resend semantics deployed. Frontend `20261019-5`, backend command-repair-1.
- Software/HA read-only checks passed without actuation; physical retest remains
  open. Earlier UI acceptance was not physical acceptance. Targeted entity/source
  authority reconciliation completed; raw sources unchanged.

## [2026-10-20] update | Admin desktop printer routing

- Updated [[entities/bambu-p1s]] from canonical desktop route inventory and live TCP probes; corrected stale VM103 reachability and FTPS port claims. HomePrinters disconnect explains prior direct path; application acceptance remains pending. Raw sources unchanged.


## [2026-10-20] update | VentSys independent operating modes

- Updated [[entities/ventsys]] from the canonical dashboard manual/current state:
  independent intents, shared paths/maximum purge request, single confirmation,
  frontend20261020-3, backend guards and actual test/deployment limits.
- Corrected stale E2 availability and iframe/restart-mode suggestions. Added both
  required-open and unwanted-open report faults; physical jam detection, ntfy
  delivery and commissioning remain open. Raw sources unchanged.

## [2026-10-21] update | FDM airflow USB flash and duplicate identity

- Updated [[entities/ventsys]] from canonical current-live-state: E3:DC USB flash verified; existing D0:A0 also answers at .41. Replacement intent and new-board network acceptance remain pending. Raw sources unchanged.

## [2026-10-21] update | FDM replacement and Booth reassignment

- Updated [[entities/ventsys]] from canonical live-state: FDM E3:DC at .41 and Booth D0:A0 at .43 independently verified over encrypted APIs. Address collision resolved; HA adoption, MQTT delivery and physical pulse checks remain pending.

## [2026-10-21] update | Print / Media migration started

- Updated [[entities/openmediavault-nas]] and index from canonical audit/current-live-state: fourth-disk extended test passed, new one-member Media RAID1 managed through OMV, original-Z warm copy running under systemd. Existing shares and Y RAID remain unchanged. Targeted relationship lint confirms expected degraded new array, intact original Z and pending cold-copy/service acceptance; owner recovery waiver preserved. Raw sources unchanged.

## [2026-10-23] update | Print / Media cold verification

- Reconciled [[entities/openmediavault-nas]] and index with canonical audit/current-live-state: warm copy passed, source Z now read-only with media writers/Filebrowser/TransferPortal paused, cold final-sync/hash runner started. Shares have not switched and original Z remains intact. Raw sources unchanged.

## [2026-10-25] update | Media cutover and second mirror member

- Reconciled [[entities/openmediavault-nas]] and index from canonical audit/live-state: Z maps Media, scoped NFS/Calibre service paths active, storage/recording tests and owner application confirmation recorded. Original Z retired after unchanged-generation proof and added as second mirror member; no independent rollback remains, owner-waived. Y/md0 unchanged; Y warm copy waits for healthy mirror. Targeted relationship lint corrects the earlier paused-services/intact-old-Z claims. Raw sources unchanged.


## [2026-10-27] update | E2 native dashboard reporting recovered

- Updated [[entities/ventsys]] from canonical dashboard/current-state evidence:
  COM4 identity, correct firmware, MQTT TLS `.52`, stale HA host corrected and
  native report recovered. Corrected inference from ICMP/WAN-block logging;
  remote actuation and mechanical acceptance remain open. Raw sources unchanged.

## [2026-10-27] update | Print/Media cutover live

- Reconciled [[pages/entities/openmediavault-nas]] and index from canonical migration proof: both mirrors healthy, Y/Print root flattened, Media service data/scoped backups live, owner access confirmed and fresh backups/isolated restores passed. Private retained originals/quarantines remain pending retirement. Raw sources unchanged.



## [2026-10-27] update | VentSys explicit valve setup tests live

- Synced [[entities/ventsys]] with canonical release20261027-1: opt-in available
  valve tests, exact subset confirmation, fan exclusion/intent locks, deployment
  and test evidence. Normal mode full-path checks remain; no actuation sent.

## [2026-10-27] update | Storage migration retirement complete

- Reconciled [[pages/entities/openmediavault-nas]] from canonical final proof: exact retained-source and staging retirement passed, roughly654GiB freed on Y, active script/monitoring paths corrected. Offline/native binary acceptance remains bounded; user Telegram deletion preserved. Raw sources unchanged.


## [2026-10-29] update | FDM print valve installation

- Updated [[pages/entities/ventsys]] from canonical installation evidence: normal
  three-wire `.55`/MAC `EC:E3:34:B4:76:A4` flashed/adopted October28, native
  reporting verified without actuation. Board now unplugged; physical calibration
  and loaded operation remain pending. Raw sources unchanged.

## [2026-10-29] update | SLA print valve installation

- Synced [[pages/entities/ventsys]] with canonical `.56`/MAC `EC:E3:34:1B:DB:2C`
  normal three-wire USB flash, full recovery backup and HA Garage adoption.
  Native/MQTT reporting verified without actuation; physical acceptance pending.

## [2026-11-04] update | VentSys device and dashboard corrections

- Updated [[pages/entities/ventsys]] from canonical procedures: FDM sensor identity, E2 reservation and monitoring, 360 touch and retention evidence, normalized UI and flow indicators.

## [2026-11-04] correction | Valve endpoints and monitor

- Synced [[pages/entities/ventsys]] with owner-confirmed standard valve physical/display0–100% travel and the stopped E2 monitor. Older bench calibration notes are historical.

## [2026-11-04] update | PlatformIO core migration

- Updated [[pages/entities/esphome]] from canonical firmware-build evidence:
  PlatformIO Core, packages, tools and the ESP-IDF environment are now at
  `K:\PlatformIO`; the original C: core was removed only after a clean
  ESP-IDF/Arduino rebuild passed. Historical spaced-path copies remain inactive.

- 2026-11-06: Updated [[ventsys]] SLA pipe air board identity, BME680 wiring and uncommissioned CO fault from canonical live-state and wiring docs.
- 2026-11-07: Updated [[ventsys]] with the live Clear alarms popup, recurring SLA pipe CO fault and proposed severity/ntfy design from the canonical dashboard manual.
- 2026-11-07: Updated [[ventsys]] with live dashboard `20261107-4` incident display and the HA ntfy publisher for CO hardware fault and failsafe transitions; phone delivery remains unverified.
- 2026-11-07: Added [[ventsys]] live read-only Diagnostics tab (`20261107-6`) covering 294 exposed HA entity reports, including CO voltage and board statistics.
- 2026-11-07: Added [[ventsys]] SLA pipe board dropout/recovery rule and dashboard connection warning (`20261107-7`); other nodes await an expected-online roster.
- 2026-11-07: Updated [[ventsys]] from the canonical dashboard manual with the 12-board expected-online roster, per-board maintenance controls, and general dropout notifications (`20261107-8`).
- 2026-11-08: Corrected [[ventsys]] FDM .32 physical gas-channel identity to owner-observed CO; archived/flashed smoke naming remains an open firmware and dashboard mismatch.
- 2026-11-08: Added [[ventsys]] CO-only FDM candidate build status from canonical live state; compiled but not flashed because the board was unreachable and no USB serial port was present.
