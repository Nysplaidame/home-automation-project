---
title: Project Tasks
description: Implementation tasks by phase — updated June 2026
tags: [tasks, implementation]
aliases: [TODO, Tasks]
created: 2025-09-15
modified: 2026-07-26
type: task-list
status: active
---

# Project Task List

**Links:** [[README|Overview]] | [[PROJECT-INDEX|Index]]

---

## Next project steps

1. [x] Add the Installation Manual Suite v1 canonical entrypoint under `docs/install/START-HERE.md`
2. [x] Add numbered fresh-rebuild phase manuals under `docs/install/phases/`
3. [x] Add central install references for command locations, state, secrets, dependencies, versions, and decision gates
4. [x] Add draft docker-host service manuals for Tier 1, Tier 2, and Tier 3/evaluate services
5. [x] Add the companion setup-documentation checklist at `docs/install/INSTALL-TO-DO.md`
6. [x] Replace stale static diagrams with canonical Mermaid sources for architecture, install sequence, DNS/NTP, access, storage, docker-host services, and VentSys safety flow
7. [ ] Deploy the reconciled 47-entry `home.local` domain inventory from `configs/openwrt/dhcp-config.conf` to live OpenWrt, restart dnsmasq, remove the temporary workstation hosts entry for Home Assistant, and pass `scripts/validation/validate-home-local-dns.ps1` against `192.168.10.1`
8. [ ] Continue expanding each install phase until every command has expected output examples and every failure mode has a tested recovery path
9. [ ] Work through the comprehensive checklist in `docs/install/INSTALL-TO-DO.md`
10. [ ] Run a full dry-read from `docs/install/START-HERE.md` after the next content expansion pass
11. [x] Deploy and document shared-iGPU CT 111 Frigate and CT 114 local AI architecture

Planning baseline until explicitly revalidated:

- Treat OMV and Proxmox NFS backups as live. On 2026-07-05, Proxmox reported
  `omv-backups` active at 54.21% used, so the old 86-87% md0 high-water warning
  is cleared; keep normal monthly backup and SMART checks.
- Treat Frigate as live with one bench camera ingest on CT 111; keep HA
  integration, source cleanup, and broader camera rollout as the remaining
  work.
- Treat Home Assistant native HTTPS as live at
  `https://192.168.20.101:8123` with the local `Home Local CA`. HTTP on
  port `8123` is no longer the active HA UI.
- Treat VentSys entities as unbuilt for implementation planning.

## Hardening and resilience roadmap

1. [ ] Plan the whole-system hardening run before changing credentials or access paths: inventory all admin surfaces, service accounts, API tokens, SSH keys, certificates, Tailscale/WireGuard paths, OpenWrt rules, host firewalls, and password-manager records.
2. [ ] Plan the whole-system resilience run before live drills: define recovery goals, access routes, trusted backups, restore order, and stop/ask gates for Mini PC, OMV, router, Home Assistant, docker-host, Frigate, llm-host, monitoring, Tailscale, local CA, and credential-loss scenarios.
3. [ ] Prove backup and restore readiness before broad credential rotation: Proxmox VM/LXC restore evidence, HA backup restore path, OMV export/config recovery path, and repo/config backup coverage. Docker-host app-data backup/restore smoke passed on 2026-07-07.
4. [ ] Execute hardening run in a controlled window: rotate infrastructure passwords, API tokens, long-lived HA tokens, app bootstrap credentials, SSH keys, and service secrets; validate each dependent service before revoking old credentials.
5. [ ] Execute resilience tabletop scenarios before disruptive tests: document what still works, what fails, first diagnostic commands, recovery route, rollback path, and "do not touch" boundaries for each major failure scenario.
6. [ ] Execute only low-risk live resilience drills first: stop non-critical services or simulate dependency loss where rollback is immediate; defer Mini PC, router, OMV, and broad network failure drills until a dedicated maintenance window.
7. [ ] Update canonical docs after each pass: `docs/reference/current-live-state.md`, `docs/reference/access-matrix.md`, `docs/reference/service-matrix.md`, `scripts/backup/backup_strategy.md`, and relevant procedures/handoffs.
8. [ ] Define log retention and analysis policy for the whole assistant stack: set 48-hour retention defaults for structured assistant state, compact conversation traces, tool summaries, and performance timings; explicitly exclude raw audio, full prompt/tool dumps, secrets, and unbounded verbose logs unless temporarily enabled for debugging with rotation and review gates.

## Operational next steps

1. [x] Confirm live/source parity for valve-1 MQTT firewall state: no temporary plain-MQTT `1883` exception exists live, and source remains TLS `8883`-only for VentSys MQTT
2. [x] Close stale valve-1 plain-MQTT follow-up tasks to avoid reintroducing insecure `1883` access while VentSys migration proceeds on TLS
3. [x] Deploy Tailscale on docker-host and advertise only selected host routes: `192.168.20.101/32`, `192.168.30.20/32`, `192.168.40.50/32`, and `192.168.60.10/32`; stale `192.168.20.0/24` advertised-route preference removed on 2026-07-02, and the Frigate host route was added on 2026-07-05 for direct PWA use
4. [x] Keep WireGuard configured as a dormant fallback (confirmed `wg0` disabled/down on 2026-05-28); do not roll out fallback clients unless Tailscale daily-access posture changes
5. [x] Clean up duplicate docker-host UFW routed DNS forward rules and keep canonical subnet-based rules for `172.20.0.0/16` (`53/udp`, `53/tcp`, `853/tcp`)
6. [x] Document temporary router WiFi uplink (`wwan_uplink`) operating policy in `docs/procedures/router_temporary_uplink_policy.md`
7. [x] Deploy `dashboards/ventsys-card-wrapper.html` to HA and verify the VentSys dashboard works inside a Lovelace iframe card
8. [x] Explicitly park embedded Grafana-in-HA work behind direct-link-only access until HTTPS/reverse proxy same-origin path is in place
9. [x] Add an external health signal for the monitoring VM so monitoring failure is visible even when Uptime Kuma itself is down
10. [x] Configure OMV-backed Home Assistant backup mount and verify a manual backup write, while keeping fast local Proxmox recovery on the MINISFORUM host
11. [x] Start the migration-safe Frigate baseline on CT 111; later superseded by the first-camera live baseline with MQTT/HA integration
12. [ ] Expand VentSys beyond valve 1: finish the MQTT TLS migration path, then flash/adopt the remaining ESPHome devices
13. [x] Deploy AdGuard Home on docker-host per `docs/decisions/04-dns-resolver-and-adblocking.md`
14. [x] Re-run router-deploy validation after the router-local NTP/deploy-tooling update
15. [x] Validate Uptime Kuma notification dispatch to ntfy (`ntfy Monitoring`): monitor #17 (Whoogle) failure was detected and ntfy `messages_published` increased (`14` -> `15`) during controlled outage on 2026-05-28
16. [x] Add repo-side Frigate credential template at `configs/frigate/frigate.env.example`
17. [x] Move active-guest Proxmox backups to OMV md0 NFS storage `omv-backups`, retain 7 daily and 6 monthly generations, run a fresh VM 102 write test, and keep the prior restore drill evidence
18. [x] Draft OMV storage cutover execution checklist at `docs/procedures/omv_storage_cutover_checklist.md`
19. [x] Confirm HA-side monitoring health states from Home Assistant UI (all `on`): `binary_sensor.monitoring_stack_externally_healthy`, `binary_sensor.monitoring_vm_grafana_reachable`, `binary_sensor.monitoring_vm_influxdb_reachable`, `binary_sensor.uptime_kuma_reachable_from_ha`
20. [ ] Parked: add Mullvad egress path for SearXNG/Whoogle on docker-host (privacy hardening), only after current Frigate + OMV pre-flight blockers are cleared
21. [x] Add command-by-command OMV execution runbook at `docs/procedures/omv_cutover_execution_runbook.md` for fast cutover when OMV hardware is ready
22. [x] Add explicit WireGuard fallback governance at `docs/procedures/wireguard_fallback_governance.md` (activation criteria, guardrails, and rollback)
23. [x] Add IDS/IPS progression planning at `docs/procedures/ids_ips_progression_plan.md` aligned to current monitoring maturity
24. [x] Align monitoring posture docs to direct-link operations and keep HA embedding parked until same-origin HTTPS path is ready
25. [x] Deploy docker-host Fail2ban SSH hardening baseline (`/etc/fail2ban/jail.d/docker-host-sshd.local`) and add repo rebuild template at `configs/docker-host/system/docker-host-fail2ban-sshd.local`
26. [x] Expand update governance with explicit update-monitoring posture in `docs/procedures/update_maintenance_playbook.md` (monitor-only alerts + planned patch windows)
27. [x] Add weekly update-review execution log at `docs/procedures/update_review_log.md` and record initial docker-host-only baseline entry
28. [x] Enable Proxmox native metrics export to InfluxDB bucket `proxmox` and add Grafana dashboard `Proxmox Resource Overview`
29. [x] Rework `Proxmox Resource Overview` into the shared wallboard visual style
30. [x] Add planned Grafana shell `NAS Resource Overview` for the future NAS-focused dashboard
31. [x] Deploy docker-host Telegraf metrics under `/opt/stacks/telegraf`, add InfluxDB bucket `dockerhost`, and fold Docker-host/container panels into `Proxmox Resource Overview`
32. [x] Fix `health_check.sh` Proxmox storage usage parsing so `local` and `local-lvm` report real percentages
33. [x] Add architecture Grafana dashboards: `Service Availability`, `Network DNS`, and `Security Posture`
34. [x] Add lightweight exporters for Uptime Kuma monitor snapshots and docker-host Fail2ban counters
35. [x] Apply `configs/home-assistant/lovelace/monitoring-grafana-links.yaml` to the live HA Monitoring dashboard through the HA UI; confirmed visible in a dashboard tab on 2026-06-01
36. [x] Approve and retest mobile Tailscale monitoring access: docker-host now advertises `192.168.60.10/32` and has routed UFW allowances for Grafana `3000` and Uptime Kuma `3001`; route approved in Tailscale admin and mobile access to HA/Grafana/Kuma confirmed working on 2026-05-31
37. [x] Re-export `Proxmox Resource Overview` and apply explicit labels (`Guest RAM`, `RAM Pressure`, `Root Disk`) to live/source panels; 2026-05-31 datasource check found high HA/docker-host/monitoring percentages are guest-memory values, not CPU/disk saturation
38. [ ] Schedule controlled docker-host patch window for Docker engine/component and kernel package candidates from `docs/procedures/update_review_log.md`
39. [x] Add first NAS telemetry using existing docker-host Telegraf -> InfluxDB -> Grafana pattern by exposing the OMV-backed Immich mount to Telegraf
40. [x] Build CT 114 `llm-host` after confirming Proxmox RAM pressure was healthy enough for the local-AI workload
41. [x] Deploy llama.cpp, Open WebUI, Wyoming Whisper, Wyoming Piper, and OpenWakeWord on CT 114 per `scripts/setup/proxmox/llm_host_setup_guide.md`
42. [x] Configure HA llama.cpp/Wyoming integrations and validate Home Assist pipeline
43. [x] Validate CT 114 Vulkan inference, 33/33 layer offload and concurrent Frigate OpenVINO use
44. [x] Add Uptime Kuma/Grafana monitoring for CT 114 AI services; add OpenWakeWord monitor as follow-up
45. [ ] Add a scoped, confirmation-gated Overwatch action for saving recipes to Mealie
45. [ ] Keep Hermes Agent roadmap-only until local LLM, STT, TTS, monitoring, and safety gates are stable
46. [ ] Keep future YouTube transcript/query app architecture undecided; VM 103 is only the expected target for future containerized query apps
47. [x] Add Frigate camera/PoE switch pre-flight checklist at `docs/procedures/frigate_camera_preflight_checklist.md`
48. [x] Configure Zyxel GS1900-8HP managed switch baseline: router `lan3` tagged trunk for VLANs 1/10/30/40, switch management on VLAN 10 (`192.168.10.12`), first camera on untagged VLAN 30, and OMV on switch port 8 untagged VLAN 40; TL-WA801N VLAN 1 access port remains future work
49. [x] Enable Home Assistant native HTTPS with the local CA on 2026-07-02; validate browser, Companion App, CCTV mobile views, Frigate integration, VentSys static assets, Grafana/Kuma direct links, and rollback path
50. [ ] Optional only if mobile access becomes flaky: improve Tailscale direct connectivity for off-WiFi mobile access by adding explicit UDP `41641` forwarding through the upstream router and GL-MT6000 to docker-host; current user validation on 2026-07-03 found CCTV feeds working on both home WiFi and mobile data with Tailscale
51. [x] Restore OMV/VLAN 40 reachability, recreate the HA Supervisor backup mount `nas_backups`, and confirm Proxmox storage `omv-backups` is active again; fixed by moving OMV to GS1900 port 8 untagged VLAN 40 and converting router `lan3` to the planned trunk on 2026-07-03
52. [ ] Approve and validate the new Tailscale `192.168.30.20/32` Frigate host route for off-WiFi Frigate PWA access; docker-host route advertisement, docker-host UFW routed allow, and OpenWrt docker-host-to-Frigate HTTPS rule were staged on 2026-07-05

---

## Docker-host app roadmap

### Tier 1 - near-term core

- [x] Validate Tailscale from an off-LAN client after docker-host auth and route approval
- [x] Deploy AdGuard Home under `/opt/stacks/adguard-home/`
- [x] Deploy Immich under `/opt/stacks/immich/` with OMV-backed upload/library storage at `/mnt/omv/immich`
- [x] Deploy Homepage under `/opt/stacks/homepage/`
- [x] Upgrade Homepage into the `Home Operations` portal with Home, Tools,
  Infrastructure, Monitoring, Storage, Media and Operations tabs; all
  user-facing services, live Docker workload status, reference links, quick
  search, header resource status, responsive layout, local visual assets and
  explicit host validation are deployed and desktop/mobile verified on
  2026-07-24
- [x] Add visible portal-card preview controls and an inline embedded workspace
  below the active tab's portal cards, with a contained split/work area and an
  `Open tab` fallback; deployed and refined 2026-07-25
- [x] Repair Homepage preview toolbar delegation, use a real external link,
  stop the MutationObserver from continuously detaching/re-appending the iframe,
  make narrow cards grow into a dedicated Preview action row, and strengthen
  tab navigation states; Household Hub and Mermaid Viewer visibly rendered and
  Reload/Close live-verified 2026-07-26
- [x] Close the embedded workspace before Homepage tab changes and place it as
  a sibling after the complete active card grid; live-verified on Home, Tools
  and Infrastructure 2026-07-26
- [x] Double the responsive embedded-workspace height on desktop and mobile so
  framed applications have a larger scrollable work area; deployed and
  live-verified 2026-07-26
- [x] Add a fixed-target, UFW-scoped Homepage preview proxy and restore framed
  GardenKeeper, Bambuddy and Whoogle views; live-verified 2026-07-26
- [x] Deploy narrow OpenWrt rules for docker-host preview/status access to
  Proxmox `8006`, router/switch HTTP, Frigate API `5000`, monitoring
  `3000/3001`, and OMV/Transfer `80/8088`; Proxmox/OpenWrt/Zyxel/Frigate/OMV/
  Transfer paths and proxy ports `8183`/`8184`/`8185`/`8187` verified live on
  2026-07-26
- [ ] Permit docker-host `192.168.20.102` to reach Grafana `3000/tcp` and Uptime
  Kuma `3001/tcp` in the monitoring VM host firewall, then verify proxy `8186`
  and both Homepage status dots. OpenWrt forwarding is already live; the VM
  refuses SSH and the admin LAN can reach both apps, isolating the remaining
  block to the monitoring host.
- [x] Replace Mermaid Viewer placeholders with all 11 canonical sources and add
  search, deep links, pan, zoom, fit, 100% view and fullscreen; deployed and
  render-verified 2026-07-24
- [x] Apply subject-specific, code-native backgrounds to the custom portal,
  Mermaid Viewer, GardenKeeper and Household Hub; portal motion respects
  reduced-motion preferences, deployed 2026-07-24
- [ ] Deploy the prepared Transfer Portal transfer-grid canvas through the OMV
  native-service deployment route once OMV management access is available
- [ ] Decide and deploy a password manager only with native HTTPS, a documented
  backup/restore path and an owner-controlled emergency-access policy; do not
  expose a vault over the current HTTP-only portal links
- [ ] Audit every portal for both direct navigation and embedded-preview
  behaviour. Record service health, HTTPS/mixed-content, authentication and
  `X-Frame-Options`/CSP framing results; fix reachability or use the normal
  link rather than weakening a service's frame protections. Mermaid Viewer and
  Household Hub are confirmed directly embeddable after repairing the portal's
  iframe re-parent loop. GardenKeeper, Bambuddy, Whoogle, Proxmox, OpenWrt,
  Zyxel and OMV are confirmed via the fixed-target proxy. Continue with the
  monitoring VM host-firewall exception, then test the remaining portals.
- [ ] Design the Jellyfin media library using the existing OMV-backed Immich
  storage. Do not claim that Jellyfin can consume Immich albums directly:
  decide whether a scheduled, read-only Immich API/export job should curate
  approved album assets into a separate Jellyfin library path, including
  ownership, duplicate handling, video format/transcode policy and backup.
- [ ] Design the OMV download/media stack before deployment. Prefer
  qBittorrent plus an isolated VPN/kill-switch path for authorised torrent
  downloads; make NZBGet conditional on an approved Usenet provider; keep
  aria2 as an optional direct-download utility rather than a primary library
  manager. All need approved storage paths, user/group ownership, backup scope
  and OMV Docker management access.
- [ ] Evaluate Autobrr only as a complement to an approved qBittorrent/NZBGet
  workflow: it listens to authorised indexer IRC/RSS announcements and dispatches
  matching releases; it is not a replacement downloader. Require tracker policy,
  credentials outside version control, categories/save paths and notification
  rules before deployment.
- [ ] Deploy Calibre-Web and Atsumeru only after book/comic source directories,
  write policy, library metadata backup and OMV Docker management access are
  approved; then add their Homepage widgets and Media-tab cards.
- [ ] Add Homepage service widgets where an approved, least-privilege credential
  path exists. Prioritise already deployed Home Assistant, Frigate, Immich,
  Mealie, Grocy, AdGuard Home, Grafana, Uptime Kuma, Proxmox, OpenWrt and
  Tailscale; evaluate complementary Beszel/Netdata, APC UPS, Scrutiny,
  Speedtest Tracker, Authentik and Backrest only if their supporting services
  are deliberately adopted.
- [x] Deploy Dozzle under `/opt/stacks/dozzle/`
- [x] Add docker-host `DOCKER-USER` guard so Dozzle is management-only despite Docker published-port forwarding
- [x] Add Uptime Kuma checks for Homepage and Dozzle
- [x] Add Uptime Kuma checks for AdGuard DNS and UI
- [x] Add Uptime Kuma check for Immich UI
- [x] Add docker-host `DOCKER-USER` guard for Immich UI on `2283`
- [x] Expand docker-host VM disk to 32 GiB
- [x] Add repo-side rebuild templates for live docker-host stacks and host firewall

### Tier 2 - roadmap candidates

- [ ] Evaluate Paperless-ngx under `/opt/stacks/paperless-ngx/`
- [x] Deploy Mealie under `/opt/stacks/mealie/` (live 2026-06-21)
- [x] Deploy Grocy for pantry/fridge/freezer stock and expiry tracking
- [x] Seed Grocy household data model with core locations, quantity units, and product groups; service health reconfirmed on 2026-07-07 (`HTTP/1.1 302 Found` login redirect), database checkpoint created, and OMV app-data backup run `20260707T125454Z` captured the change
- [x] Add Grocy voice shopping-list support to Home Assistant Assist with add/list-only LLM tools, dedicated Grocy API key, HA/dockerd firewall allowances, direct HA-to-Grocy API proof, and OMV app-data backup run `20260707T132647Z`
- [ ] Parked: Self-hosted LiveSync client rollout; backend/client prep exists, but Obsidian is no longer part of the near-term path
- [x] Install and prove docker-host app-data backup to OMV `backups/docker-host` covers Mealie, Grocy, Obsidian LiveSync, and GardenKeeper dumps; completed on 2026-07-07 after deploying the live OpenWrt `Docker Host to OMV NFS` rule, mounting `/mnt/omv/docker-host-backups`, running backup `20260706T231304Z`, restore-smoking to `/tmp`, and enabling the daily `03:45` systemd timer
- [x] Deploy ntfy internal-only under `/opt/stacks/ntfy/`
- [x] Configure Uptime Kuma ntfy notifications through a dedicated write-only topic
- [ ] Evaluate Actual Budget under `/opt/stacks/actual-budget/`
- [ ] Evaluate Scrypted under `/opt/stacks/scrypted/`
- [x] Deploy SearXNG direct-access pre-flight under `/opt/stacks/searxng/`
- [x] Deploy Whoogle direct-access pre-flight under `/opt/stacks/whoogle/`

### Tier 3 - evaluate carefully

- [ ] Evaluate Vaultwarden only after a backup/security review
- [ ] Evaluate Portainer only if its convenience beats the added admin surface
- [x] Deploy Watchtower in monitor-only mode only
- [ ] Revisit local registry mirror after more Compose workloads exist
- [ ] Evaluate Node-RED only if HA native automations are insufficient

## Home Assistant apps and enhancement roadmap

Companion App, ESPHome, Mosquitto, Terminal & SSH, and Studio Code Server/File
Editor are core Home Assistant tools. HACS remains optional and non-critical.
Safety paths, MQTT, firewall policy, backups, and VentSys emergency behavior
must work without HACS.

### Core HA tools

- [x] Install Home Assistant Companion App on operator phones using `docs/procedures/home_assistant_companion_app_guide.md`
- [x] Test push notifications and actionable notification acknowledgements
- [x] Trust the local Home Assistant CA on the operator Android phone and confirm the app connects to `https://192.168.20.101:8123`
- [ ] Review Companion App sensors and enable only useful presence, battery, network, and notification sensors
- [x] Keep Mosquitto as the required MQTT broker add-on
- [x] Keep ESPHome as the required VentSys firmware/adoption add-on
- [x] Keep Terminal & SSH available for HA-side diagnostics
- [ ] Prefer Studio Code Server for larger YAML/package edits; keep File Editor as fallback

### High-value candidates

- [x] Install HACS only after a current HA backup exists
- [x] Evaluate Advanced Camera Card / former Frigate Card with the first live
  Frigate camera; manual HACS-layout asset install is live under
  `/config/www/community/advanced-camera-card`. The CCTV dashboard now uses it
  as the primary first-camera card, with the HA image provider plus Frigate
  status/toggle entities exposed beside it.
- [ ] Evaluate Mushroom Cards for general dashboards, room views, service status, printer state, and VentSys summaries
- [ ] Evaluate apexcharts-card for temperature, VOC, airflow, pressure, power, and IAQ history
- [ ] Evaluate auto-entities for dynamic maintenance views such as unavailable ESPHome devices or low batteries
- [ ] Evaluate Watchman before and after major dashboard/entity refactors

### Quality-of-life candidates

- [ ] Evaluate Bubble Card for mobile-friendly popups and compact controls
- [ ] Evaluate browser_mod for garage kiosk / wall display behavior after the display hardware exists
- [ ] Evaluate button-card for polished custom controls after core dashboard layout stabilizes
- [ ] Evaluate card-mod sparingly for styling once layout is stable
- [ ] Evaluate Scheduler Card / scheduler-component if native schedules feel awkward
- [ ] Evaluate Adaptive Lighting only if smart lighting enters project scope
- [ ] Revisit Bambu Lab / printer HACS integrations only after P1S details are confirmed and Bambuddy overlap is understood

### Risk-gated automation candidates

- [ ] Keep Node-RED Tier 3/evaluate unless HA native automations become insufficient
- [ ] Evaluate AppDaemon only if Python automation apps are justified for non-critical logic
- [ ] Evaluate pyscript only for non-critical helper logic after a rollback plan exists
- [ ] Keep Claude/MCP or other AI automation as future advisory-only work; do not let it replace safety-critical HA/ESPHome/MQTT logic

---

## Immediate next actions (unblocked right now)

- [x] Create `/opt/stacks/bambuddy/.env` on docker-host from `.env.example`
- [x] Add the real MQTT password
- [x] Start Bambuddy with `docker compose up -d` from `/opt/stacks/bambuddy`
- [x] Confirm Bambuddy UI at `http://192.168.20.102:8000`
- [ ] Keep P1S integration parked until printer details are available
- [ ] Add P1S details and Home Assistant token in the Bambuddy web UI when physically available
- [ ] Do not deploy `configs/home-assistant/bambuddy_p1s_package.yaml` until `<P1S_SERIAL>` is replaced and MQTT topics are confirmed
- [x] Remove deprecated InfluxDB connection/auth keys from HA YAML after confirming the UI-managed Influx connection
- [ ] Create `/opt/frigate/.env` after camera RTSP and MQTT credentials/certs are ready
- [x] Design `apt-cacher-ng` on docker-host for package caching
- [x] Deploy `apt-cacher-ng` on docker-host and test with frigate-nvr
- [x] Move Bambuddy MQTT relay from 1883 to TLS 8883 and verify retained `bambuddy/status`
- [ ] Keep Docker registry mirror parked as Tier 3/evaluate until more Compose workloads exist

---

## Phase 1 — Network ✅ First-flight live / source follow-up pending

### Configuration (all complete)
- [x] 10-segment architecture designed ✅
- [x] `vlan-config.conf` — bridge, VLANs, interfaces, WireGuard ✅
- [x] `firewall-config.conf` — zones, inter-VLAN rules, VentSys ports ✅
- [x] `dhcp-config.conf` — scopes, reservations, DNS ✅
- [x] `wireless-config.conf` — 5 SSIDs, channel plan, WPA3/WPA2 ✅
- [x] Router setup phases 1–8 documented ✅
- [x] Network testing guide written ✅
- [x] WireGuard fallback guide written ✅
- [x] MQTT 1883→8883 deployment note added to firewall config ✅
- [x] VLAN 1 port assignment bug fixed in Phase 2 script ✅
- [x] Country code corrected GB in Phase 5 script ✅
- [x] PVID notation (u vs u*) fixed in Phase 2 script ✅

### Deployment
- [x] Flash/configure GL-MT6000 with router phases 1–8
- [x] Run router validation/tests from management IP (`test.ps1`: PASS=62/WARN=0/FAIL=0; `test-connectivity.ps1`: PASS=74/WARN=0/FAIL=0)
- [ ] Fill in MAC addresses in dhcp-config.conf (Proxmox host, VMs, NAS)
- [x] Confirm no live valve-1 temporary plain-MQTT firewall exception exists; keep source as TLS `8883`-only for VentSys MQTT
- [x] Remove stale valve-1 firewall-source drift items after parity verification
- [ ] Keep WireGuard fallback clients unrolled unless Tailscale daily-access posture changes or resilience drills require activation
- [ ] Enable DDNS on router only if WireGuard fallback endpoint maintenance becomes annoying

---

## Phase 2 — Core infrastructure ⏳

### Proxmox
- [x] Install Proxmox VE on MINISFORUM M1 Pro-125H
- [x] Configure vmbr0 VLAN-aware bridge, trunk on enp1s0
- [x] Set static IP 192.168.10.10 on vmbr0.10
- [x] Retire PCI iGPU passthrough/IOMMU requirement in favour of shared LXC device mapping
- [x] Retire the pre-LXC `vm-setup.sh`; `guest-configs.md` holds the current inventory
- [x] Move VMs 100/102/103 and CTs 111/114 to `omv-backups` with `keep-daily=7,keep-monthly=6`; 2026-07-05 check shows VM backups current, `omv-backups` at 54.21% used, and the LXC backup job fixed with `tmpdir=/var/tmp` after NFS temp-dir permission failures; manual CT 111 and CT 114 proofs passed on 2026-07-05/06
- [x] Replace VM 104 with CT 114 `llm-host` at 192.168.20.104; retain stopped VM as rollback
- [x] Keep `llm-host` and `openwebui` DNS aliases on 192.168.20.104
- [x] After the 64GB RAM upgrade, resize CT 114 and move `home-assistant-llm` to Qwen3-14B-128K Q4_K_M with a 64k context; API smoke test passed on 2026-07-07
- [ ] Run full CT 114 post-upgrade validation for the Qwen3-14B 64k profile: Home Assistant Assist text/voice, SearXNG search, Mealie recipe save/display/readout workflow, Open WebUI, host swap, and Frigate concurrency

### Home Assistant VM (VM 100)
- [x] Start VM 100, complete HAOS onboarding wizard
- [x] Set static IP 192.168.20.101 via nmcli
- [x] Install add-ons: Mosquitto, File Editor, Terminal, ESPHome
- [x] Configure MQTT integration on TLS (`localhost:8883`); keep plaintext `1883` only for explicit bootstrap exceptions
- [x] Copy `ventsys_ha_package.yaml` and `ventsys_ha_scripts.yaml` to `/config/packages/`
- [x] Do not copy `ventsys_ha_optional.yaml` yet (load only after its prerequisites are met)
- [x] Copy `dashboards/ventsys-dashboard.html` to `/config/www/ventsys-dashboard.html`
- [x] Generate Long-Lived Token → paste into `HA_CONFIG.token` in live dashboard copy
- [x] Confirm dashboard shows ◉ HA LIVE
- [x] Enable HA 2FA (TOTP)
- [x] Copy `dashboards/ventsys-card-wrapper.html` to `/config/www/ventsys-card-wrapper.html`
- [x] Add a Lovelace iframe/panel view that uses the VentSys card wrapper
- [x] Configure NAS as HA backup mount and verify manual backup write to OMV
- [x] Set HA automatic backup schedule: daily 03:00, keep 14, location `nas_backups`
- [x] Validate router-local NTP for non-HA-managed restricted devices
- [x] Stage HACS custom integration `2.0.5` manually at `/config/custom_components/hacs`
- [x] Restart Home Assistant after staging HACS and verify the HACS setup flow opens
- [x] Complete HACS setup in HA and finish GitHub device authentication

### Frigate (CT 111; VM 101 retained only for rollback)
- [x] Create VM 101 from Debian 13 cloud image (hostname: frigate-nvr, SSH only)
- [x] Set static cloud-init IP 192.168.30.20
- [x] Note MAC and add to dhcp-config.conf (`BC:24:11:9C:25:87`)
- [x] Install Docker (official repo)
- [x] Deploy `configs/frigate/config.yml` to `/opt/frigate/config/`
- [x] Stage `/opt/frigate/.env` from template with `FRIGATE_MQTT_PASSWORD` set and secure permissions (`600`)
- [x] Set current bench-camera `FRIGATE_RTSP_PASSWORD` in `/opt/frigate/.env`; replace later if camera credentials are rotated
- [x] Stage MQTT CA trust for Frigate at `/opt/frigate/certs/ca-cert.pem` and verify TLS (`Verify return code: 0`)
- [x] Create host dirs: `mkdir -p /opt/frigate/db`
- [x] Start Frigate 0.17.1 on CT 111; first-camera live baseline now supersedes the original no-camera migration-safe baseline
- [x] Update source-controlled `configs/frigate/config.yml` from the accepted
  first-camera live config without embedding RTSP or MQTT secrets
- [x] Configure HTTPS/SSL for Frigate UI before regular use
- [x] Confirm Frigate UI over HTTPS/SSL: `https://192.168.30.20:8971/api/version` requires auth and plain HTTP to port `8971` is rejected
- [x] Configure initial go2rtc/WebRTC/audio behavior for the first camera:
  named main/sub restreams are live, Advanced Camera Card uses the Frigate
  go2rtc provider, and the browser negotiates WebRTC with video plus PCMU audio
- [x] Replace Lumen-first Apple viewing plan with HA Companion App + Frigate PWA first, with Lumen/Viewu/Kapal as optional later evaluations only
- [x] Stage Frigate HA custom integration `v5.15.4` manually at `/config/custom_components/frigate`
- [x] Restart Home Assistant after staging Frigate and verify the Frigate setup flow opens
- [x] Complete Frigate setup in HA at API URL `http://192.168.30.20:5000`
- [x] Enable Frigate MQTT over TLS to HA Mosquitto so Frigate HA entities are live
- [x] Add first-camera IR-cut mode controls in HA using ANNKE/Hikvision ISAPI
  digest auth, with `day`, `night`, `auto`, and `schedule` options exposed on
  the CCTV dashboard
- [x] Add first-camera supplemental light and guarded two-way audio settings to
  the CCTV dashboard. Supplemental light exposes mode plus white/IR brightness;
  two-way audio exposes enable plus speaker/microphone volume, but actual
  browser talkback still requires HTTPS/secure-context testing.
- [x] Manage VM 103 as `docker-host` via `scripts/setup/proxmox/docker_host_setup_guide.md`
- [x] Deploy Bambuddy as `/opt/stacks/bambuddy` on docker-host
- [x] Confirm Bambuddy UI at http://192.168.20.102:8000
- [x] Add Frigate integration in HA
- [x] Remove stale ONVIF integration entry for the first camera from HA; use
  the Frigate entity path for the CCTV dashboard
- [x] Read-only inspect current Frigate review/event/motion history for
  `cam_01_annke_c500` before tuning. On 2026-07-07, Codex confirmed the
  `proxmox` SSH profile reaches CT 111 and Frigate API `0.17.1`; object
  detection is currently disabled, the event table has no object events,
  review history contains only three historical alert segments, and all current
  recording segments are motion-marked with zero object segments. CT-local
  Frigate storage was near full; the OMV recording cutover is now complete, so
  broader tuning can proceed with detection/zone re-enable tests.
- [ ] Define the exterior CCTV camera/zone standard for the eventual six-camera
  rollout: driveway, front door/garden, back door/patio/back garden, side
  garden, plus a possible second front door/garden view. Keep the garage
  interior camera as test-only and do not plan internal production cameras.
- [ ] Draft Frigate zone and object rules with driveway treated as the most
  complex view: separate road, sidewalk, driveway, property-boundary and
  approach zones; use zone-required alerts/detections, object filters,
  inertia, loitering and masks to avoid vegetation, shadow, pet, bird and road
  traffic false positives.
- [ ] Set CCTV object-detection scope for exterior security and convenience:
  `person` as the primary alert class, `car` with LPR/known-plate handling,
  `package` for parcel notifications, and `dog`/`cat` for neighbour-pet
  notifications. Keep birds and other small objects out of alert paths unless
  later testing proves they add value.
- [ ] Design alert severity rules before automation: daytime person outdoors is
  an alert; 21:00-07:00 person events are high severity; nobody-home state
  raises severity; driveway/front-door camera audio/flashing alarms are allowed
  only night/away; back-door and side-garden alarms may run at any time if the
  event threshold is met; camera offline is an alert.
- [ ] Define special security behaviors for fence/hedge crossing, under-hedge
  movement, flashlight-at-night events, sidewalk loitering, and vehicles
  slowing/stopping near the property. Use a 60-second sidewalk loitering
  threshold before alerting unless the person enters a property zone.
- [ ] Implement final event-only recording policy on OMV-backed Frigate
  storage. The OMV recording mount is live as of 2026-07-07; next tune main
  streams for recordings, substreams for detect/mobile viewing, audio in
  recordings, no steady-state CT-local recording, and an initial two-week
  retention cap for alert, detection, and motion recordings while false
  positives are being tuned. Extend retention only after OMV capacity and
  Frigate cleanup behavior are verified against real five-camera usage.
- [ ] Define face-recognition authorization policy: household and visiting
  family only. Suppress alerts only when an authorized person is confidently
  recognized; keep recordings for 14 days if only authorized people are
  present, and retain the full detection period if any unrecognized person is
  present or recognition confidence is insufficient.
- [ ] Design Home Assistant CCTV policy dashboard controls for retention
  targets, event-only recording status, motion/detection clip counts, camera
  health, stricter/relaxed profile, home/away profile, alarm enablement, known
  person and known vehicle handling, while keeping auditable rules in source
  config rather than only in UI state.
- [ ] Copy `configs/home-assistant/bambuddy_p1s_package.yaml` to `/config/packages/` on HA
- [ ] Replace `<P1S_SERIAL>` placeholder in bambuddy_p1s_package.yaml with real serial
- [ ] Confirm `binary_sensor.p1s_printing` and print state entities appear in HA
- [x] Map shared Intel render/card devices into unprivileged CT 111 and CT 114; PCI passthrough/IOMMU is not required

---

## Phase 3 — VentSys fire safety ⏳ Hardware pending

### Hardware procurement
- [ ] 2× ESP32-DevKitC (sensor boards — ventsys-fdm-sensor, ventsys-sla-sensor)
- [ ] 1× ESP32-DevKitC (fan controller — already wired to GPIO23)
- [ ] 1× ESP32-DevKitC (valve controller — already wired to GPIO18)
- [ ] 4× DS18B20 waterproof temperature probe
- [ ] 2× BME680 I2C breakout (temp/humidity/pressure/IAQ gas)
- [ ] 2× MQ-135 (VOC / air quality)
- [ ] 2× MQ-2 (smoke detection)
- [ ] 2× differential pressure sensor (for duct airflow)
- [ ] 4× MG90S servo (butterfly valves — check if already in PrintAirPipe kit)
- [ ] 1× 125mm inline duct fan with PWM control
- [ ] PrintAirPipe STL files (€29, nerdiy.de)
- [ ] 2kg PLA+ filament + 1kg PLA-HT (fire-retardant)
- [ ] 2× smart plugs with energy monitoring (VLAN 50 compatible)
- [ ] Resistors: 4.7kΩ (DS18B20 pull-ups, I2C pull-ups), 10kΩ/20kΩ (ADC voltage dividers)
- [ ] Fan driver MOSFET (e.g. IRLZ44N) or dedicated PWM fan controller board

### 3D printing
- [ ] Print all PrintAirPipe pipe segments (PLA+)
- [ ] Print servo valve housings (PLA+)
- [ ] Print sensor housings (PLA+)
- [ ] Print filter housings (PLA-HT — fire-retardant mandatory)
- [ ] Test-fit all components before installation

### Wiring
- [ ] Wire FDM sensor board per `ventsys_wiring_reference.md`
- [ ] Wire SLA sensor board per `ventsys_wiring_reference.md`
- [ ] Wire fan controller (GPIO23 → MOSFET → fan)
- [ ] Wire valve controller servos
- [ ] Note DS18B20 addresses after first flash, update ESPHome YAML
- [ ] MQ sensor 24–48h burn-in before calibrating thresholds

### ESPHome flashing and adoption
- [ ] Flash fan controller via USB (`ventsys_fan_controller.yaml`)
- [ ] Flash valve controller via USB (`ventsys_valve_controller.yaml`)
- [x] Create remaining controller YAMLs -- all exist in `configs/esphome/`:
  ventsys_main_valve1/2, fdm/sla_branch_valve, fdm/sla_print_valve, fdm/sla_360_valve (8 valves), ventsys_booth_fan.yaml (spray fan)
- [ ] Flash FDM sensor board via USB (`ventsys_fdm_sensor.yaml`)  # A5-3: per-device YAML now exists (A4-4)
- [ ] Flash SLA sensor board via USB (`ventsys_sla_sensor.yaml`)  # A5-3: per-device YAML now exists (A4-4)
- [ ] Flash booth sensor board via USB (`ventsys_booth_sensor.yaml`)  # A5-3: per-device YAML now exists (A4-4)
- [ ] Add `mqtt_ca_cert` to both repo and HA-side ESPHome `secrets.yaml` as part of the VentSys TLS migration path
- [ ] Migrate `ventsys_main_valve1.yaml` from MQTT `1883` to `8883` with `certificate_authority: !secret mqtt_ca_cert`
- [x] Remove valve-1 temporary plain-MQTT firewall follow-up task because no live/source `1883` exception is present
- [ ] Bench-calibrate the 360 intake v2 Nerdiy candidates before deployment: current latest profile uses ESP32-C6, servo PWM on GPIO0, LED data on GPIO1, Nerdiy one-sided servo mapping limited to `0-35`, logical `open=35` / `closed=0`, forced servo writes for buttons/MQTT/direct number changes, and 1s PWM detach at fully open or fully closed; local touch toggle is parked until C6-compatible input wiring is confirmed
- [ ] Adopt all devices in ESPHome add-on (17 ESP32 boards + plugs)
- [ ] Verify MQTT topics publishing: `mosquitto_sub -t 'ventsys/#' -v`
- [ ] Confirm automations fire on test sensor triggers
- [ ] Test emergency power cutoff sequence end-to-end
- [ ] Evaluate `mode: restart` on the 12 VentSys HA mode scripts if rapid mode-click queueing causes oscillation in practice
- [x] Harden dashboard page-init to use command-free renderers; static/mock contract tests prove initialization cannot enter an MQTT publish path
- [ ] Revisit `restore_value` behavior for valve position entities so device restarts do not assume `0%` after physical movement
- [ ] Stand up the garage Pi 5 desktop/kiosk for the VentSys dashboard using `docs/install/garage-pi-desktop-setup-guide.md` once the display hardware is ready

---

## Phase 4 — Storage ⏳

- [x] Migrate live OMV hardware/storage to VLAN 40 at `192.168.40.50`; capacity warning cleared by the 2026-07-05 `omv-backups` check at 54.21% used, and the managed-switch recable/trunk path is live
- [x] Follow `omv_nas_setup_guide.md` storage/user/share/export setup while preserving existing SMB shares
- [x] Configure NFS exports (Frigate, HA, Immich, configs shares)
- [x] Warm Frigate OMV export for future unprivileged CT cutover: allow Proxmox host `192.168.10.10` to mount `/export/frigate` and verify temporary write/read/delete/unmount
- [x] Keep Frigate "live" recordings on MINISFORUM local storage first during first-camera proving; superseded by the 2026-07-07 OMV recording cutover
- [x] Mount OMV Frigate export on Proxmox, bind-mount it into CT 111 at `/mnt/nas/frigate`, update docker-compose.yml volume, add the required UID `100000` ACL for the unprivileged CT root mapping, recreate Frigate, and verify fresh recordings write to OMV
- [x] Add OMV as HA network storage → verify backup writes successfully
- [ ] Configure robocopy or rsync scheduled task for vault backup to NAS
- [ ] Enable SMART monitoring on NAS drives

---

## Phase 5 — NVR / Cameras ⏳

- [ ] Select PoE IP camera models (H.265, RTSP, compatible with Frigate)
- [ ] Purchase 4× cameras and PoE switch
- [ ] Record sourced camera and smart PoE switch model numbers, firmware lines, RTSP/substream paths, PoE budget, management VLAN behavior, and reset procedures in `docs/procedures/frigate_camera_preflight_checklist.md`
- [ ] Bench-test one camera at a time using `docs/procedures/frigate_camera_preflight_checklist.md` before permanent mounting
- [x] Bench-test first camera on the Zyxel switch: ANNKE C500 (`I51HJ`, firmware `v5.8.10 build 250917`) now reserved at `192.168.30.21`, with verified RTSP `/Streaming/Channels/101` and `/Streaming/Channels/102`, router-local NTP, and cloud access disabled
- [x] Deploy router `lan3` as the managed-switch trunk after the GS1900 baseline was configured; keep future switch access-port changes gated and labelled
- [ ] Mount cameras, run CAT6 to PoE switch access ports on VLAN 30
- [ ] Assign static IPs: camera 1 is reserved at `192.168.30.21`; future cameras remain planned at `192.168.30.22-24`
- [ ] Update RTSP paths in `configs/frigate/config.yml` (currently placeholder `/stream1`)
- [ ] Restart Frigate, confirm all 4 camera streams visible in UI
- [ ] Test person detection notifications in HA

---

## Phase 6 — Security hardening

- [x] Set up MQTT TLS (8883) — broker listener live, CA/broker certs installed, authenticated TLS pub/sub verified
- [x] Keep router source TLS-oriented for MQTT: no valve-specific `1883` exception exists, and remaining clients should migrate to `8883` without reintroducing plain-MQTT router rules
- [ ] Enable HTTPS on HA — follow `ssl_tls_guide.md` (choose Option A/B/C)
- [x] Configure Fail2ban on docker-host (`sshd` jail baseline live at `/etc/fail2ban/jail.d/docker-host-sshd.local`)
- [x] Configure Fail2ban on Frigate VM (`sshd` jail baseline live at `/etc/fail2ban/jail.d/frigate-nvr-sshd.local`)
- [x] Deploy monitoring VM on VLAN 60 (Uptime Kuma, InfluxDB, Grafana, Telegraf)
- [x] Create baseline Uptime Kuma monitors for core infrastructure
- [x] Forward OpenWrt syslog to Telegraf/InfluxDB
- [x] Export Home Assistant state history to InfluxDB
- [x] Configure Grafana InfluxDB datasource and baseline Home Automation dashboard
- [x] Configure Proxmox native metrics export to InfluxDB and add `Proxmox Resource Overview` Grafana dashboard
- [x] Deploy docker-host Telegraf host/container metrics to InfluxDB bucket `dockerhost`
- [x] Add Docker-host/container panels to `Proxmox Resource Overview`
- [x] Add `Service Availability`, `Network DNS`, and `Security Posture` Grafana dashboards
- [x] Export Uptime Kuma monitor state to InfluxDB bucket `uptimekuma`
- [x] Export docker-host Fail2ban counters to InfluxDB bucket `dockerhost`
- [x] Add HA Monitoring page/sidebar entry with direct links to Grafana and Kuma
- [x] Deploy internal ntfy notification service for future HA/Kuma/Grafana alerts
- [x] Prepare HA HTTPS certificate files without enabling HTTPS cutover
- [x] Keep monitoring operational posture as direct-link access from HA, with embedding intentionally parked for now
- [ ] Re-open Grafana/Uptime Kuma embedding work only after same-origin HTTPS/reverse-proxy path and auth model are approved
- [ ] Add Uptime Kuma dashboard view into Home Assistant after same-origin reverse proxy/HTTPS path exists
- [ ] Add Grafana dashboard view into Home Assistant (Lovelace panel/iframe) once auth/embedding behavior is stable
- [ ] Evaluate Telegraf UI integration path (direct Telegraf has no real UI; expose Influx/Grafana views in HA instead)
- [x] Add an external health signal for monitoring VM (HA-side check) so Kuma-down is still detected
- [x] Deploy AdGuard Home on docker-host as selected DNS filtering engine
- [x] Add/validate router DNS enforcement rules for filtering coverage and public fallback
- [x] Add monitoring for the DNS filtering service before making it the only resolver path
- [x] Verify historical pre-NAS Proxmox local backup job for VMs 100/101/102/103; current recurring guest backups now use OMV `omv-backups`
- [ ] Extend `Fail2ban` from docker-host baseline to Frigate and other applicable Linux service hosts
- [ ] Execute IDS/IPS progression Phase A (`docs/procedures/ids_ips_progression_plan.md`): monitor Fail2ban jails/bans and tune policy after live observation
- [ ] After at least 30 days of baseline security-event data, decide CrowdSec pilot vs defer and document the decision
- [ ] Add a scoped internal penetration-testing pass after hardening + update governance stabilize; record findings and remediation evidence
- [ ] Set up WireGuard DDNS if ISP IP changes frequently
- [x] Run staged core health baseline and confirm required live services are green (`health_check.sh --json`: PASS=11/FAIL=0; hardware-dependent checks skipped/unknown until devices exist)

---

## Ongoing / maintenance

- [ ] Rotate infrastructure passwords, API credentials and SSH keys together;
  update password-manager records and validate every dependent service before
  revoking old credentials

- [ ] Monthly: run backup health checklist (`backup_strategy.md`)
- [ ] Monthly: check SMART status on NAS drives
- [ ] After any failed CT backup or Proxmox `CT is locked` event: run
  `scripts/backup/proxmox-lxc-backup-guard.sh` in read-only mode, clear stale
  backup locks only if no active backup/snapshot task exists, then rerun the
  affected CT backup proof
- [ ] Add a long-session continuity workflow for Codex/LLM work: find a way for
  the agent to measure or report its current context-window usage, define the
  command pattern for intentionally resetting into a new chat, and write a
  reusable handoff-document procedure so active tasks, evidence, and next
  commands can be carried into the new chat without relying on chat memory alone
- [x] Verify CT 111/114 backup behavior after adding `tmpdir=/var/tmp` to the
  Proxmox LXC backup job; CT 111 manual proof passed on 2026-07-05 and CT 114
  manual proof passed on 2026-07-06
- [ ] Weekly: append an entry to `docs/procedures/update_review_log.md` (Watchtower monitor-only signals + host package candidates + planned patch window)
- [ ] Next patch window: update docker-host packages from the current candidate list, reboot if kernel package changes, and rerun router/health/Grafana checks
- [ ] After any config change: `git add -A && git commit && git push`
- [ ] When hardware arrives: update MAC addresses in `dhcp-config.conf`
- [ ] When cameras confirmed: update RTSP URLs in `configs/frigate/config.yml`
- [ ] When sensors connected: update DS18B20 addresses in ESPHome YAML
