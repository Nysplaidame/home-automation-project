---
title: Project Tasks
description: Implementation tasks, operational evidence and owner-gated follow-ups
tags: [tasks, implementation]
aliases: [TODO, Tasks]
created: 2025-09-15
modified: 2026-11-13
type: task-list
status: active
---

# Project Task List


**Links:** [[README|Overview]] | [[PROJECT-INDEX|Index]]

Completed items (364 as of 2026-11-13) live in
[[2026-11-13-todo-completed|the completed-items archive]]; only open work and
items with open sub-tasks remain here.

**Known open items outside this list** (from the 2026-11-13 audit and
[[HANDOFF-2026-11-13-branch-merge-and-audit]]):

- [ ] Owner: rotate the Obsidian Local REST API key and certificate, then
  `git rm --cached` `.obsidian/plugins/obsidian-local-rest-api/data.json` and gitignore it.
- [ ] Deploy the Filebrowser HTTPS listener (port 8212): reload the Homepage
  nginx and run `docker-host-ufw-homepage-previews.sh` on VM 103, then check the card.
- [ ] Verify merged sources against live hosts before deploying: Homepage
  (`services.yaml`, `nginx.conf`, `custom.js`), SearXNG compose, router
  `dhcp-config.conf`, CT 114 `llm-host-firewall.sh`, `llamacpp_conversation`
  (test a recipe/web-search follow-up), Tailscale routes (four vs five).
- [ ] Rebuild the Mermaid Viewer and redeploy `/opt/stacks/mermaid-viewer/dist`.
- [ ] Decide fate of unmerged local branches (`claude/mermaid-diagram-cleanup-ec1358`
  has six wiring diagrams; `llm-igpu-speed-handoff` was discarded by the owner).
- [ ] Docs drift: add ~95 missing files to `PROJECT-INDEX.md`; wiki pages for Solar
  Observatory and Obico; decision numbering gap (06) and unnumbered decisions;
  refresh stale `modified:` dates on READMEs and reference matrices.
- [ ] Repo weight: drop `worktree-file-inventory.csv` and the Tesseract binaries
  under `recomp-tracker/static/ocr/`; untrack `main/.obsidian/`; remove root
  `cam_01_latest_check.jpg`; add CI for the four apps with tests.

- [ ] Fix confirmed interrupted mode-release recovery: desired intent is saved
  before valve closures; retry can omit the released valves and shared paths.
  Preserve pending ownership durably; replace misleading retry guidance.
- [ ] Decide normal-mode fan speed after the last purge ends; current planner
  leaves the last purge speed in place while another mode remains active.
- [ ] Implement and verify commissioned-node ntfy alerts, dashboard stale-state
  improvements, no-motion reference UI and automatic firmware-update checks;
  November4 mode review documented in dashboard manual, not yet implementation.
- [ ] On the next normal HA restart or E2 reconnect, verify E2's HA host stays
  `.52` and the stale `esphome/discover/ventsys-main-valve-1` topic is not
  republished. Server monitor now checks ongoing identity; normal restart
  persistence still awaits that event.
- [ ] Physically test both external360 touch inputs, loaded travel and all other
  boards' restart retention. Require pre/post native-value acceptance on every OTA.
- [ ] Add dashboard/other-valve manual reference UI (bounded no-motion API exists
  for360 intakes only); calibration action: no
  PWM on acknowledgement, label operator-reported state, preserve unknown physical
  position status; map actual closed/open pulse endpoints before future motion.
- [ ] Verify FDM print touch, remote actuation and sustained operation under servo load
  when available; owner confirms its physical/display endpoints are 0–100%.
- [ ] Physically retest corrected remote control routing and mode transitions
  after required controllers are available; local E2 touch response is owner reported.
- [ ] Commission expected-open AND expected-closed airflow baselines for VentSys,
  agree danger thresholds and deploy deduplicated ntfy incidents with phone proof.


## Next project steps

- [ ] Physically diagnose SLA pipe CO output/wiring before commissioning: after
  warm-up ADC remained near 3.3 V, briefly settled near 1.03 V after a power
  cycle, then returned to 3.307 V with CO detection and fault active. Confirm
  wiring/output stability; capture a clean-air baseline only when valid.
  November 8: owner removed packaging cover and possible signal-to-VCC wire
  strand; voltage then about 0.300 V with detection/fault off, latch still on.
  Watch stability and verify physical wiring before baseline capture.
- [ ] Correct installed FDM enclosure air sensor `.32` CO channel: owner
  identified the fitted component as CO on November 8, but flashed firmware,
  HA and dashboard still label GPIO3 as smoke and use an uncalibrated raw
  threshold. Candidate `configs/esphome/ventsys_fdm_sensor_co.yaml` now uses
  the SLA CO/BME680 pinout and compiled under ESPHome 2026.9.1. On November 8
  HA still reported the board offline, `.32` did not answer, and Windows had no
  USB serial device; no flash occurred. Connect the MAC `CC:BA:97:F0:D0:C0`
  board, verify its actual status LED wiring, flash and validate native CO/BME
  readings, then correct dashboard and HA entity references and alarm rules.
- [ ] Induce a controlled VentSys board dropout/recovery and verify the dashboard,
  HA log, maintenance suppression and ntfy delivery after the phone subscription
  is connected.
- [ ] Complete the severity matrix and durable incident manager in the VentSys
  dashboard manual. Frontend `20261107-4` now displays live orange/red incidents
  and source outlines; HA publishes SLA CO hardware fault and failsafe transitions
  to ntfy. Validate phone delivery after reconnecting its subscription, then
  commission remaining rules, deduplication and bounded reminders.
- [ ] Make invalid CO ADC readings report fault before detection in firmware;
  bench-verify both paths. SLA dashboard `20261107-4` now uses adopted BME680
  IDs and labels the channel CO.

- [ ] Verify HA adoption/entity naming after airflow MAC/role reassignment,
  MQTT broker delivery and physical pulse response. See current-live-state.

- [ ] Physical retest after repair: verify each 360 separately in both directions,
  E2 actuation, and an available-controller mode subset. Earlier tests only proved
  UI/policy behaviour and missed the wrong runtime topics. No actuation was sent
  during diagnosis/repair. Keep 360 firmware/endpoints unchanged.
- [ ] Verify touch view on the physical seven-inch screen; software tested at
  800×480 and 1024×600. Use `/dashboard-ventsys/touch`, optional Full screen.
- [ ] Continue installation as planned and physical sequence/commissioning
  acceptance separately. Direct MQTT/native controls bypass script arbitration.
  The accepted 360 firmware and firmware/HA role swap remain unchanged.

- [ ] Execute the staged CA migration after signer/backup and additional
  Windows/Android/device trust are prepared; MQTT firmware dependencies and
  Frigate maintenance remain deferred. No live certificate changed in planning.


- [ ] Verify resource-monitor alert presentation on the subscribed phone;
  October11 labelled alert/recovery received HTTP200, but owner received neither.
  ntfy reported zero subscribers; phone is on mobile data with Tailscale connected
  and its ntfy subscription disconnected. Diagnose its connection error before
  repeating the background-notification test. See ntfy service manual.


- [ ] Continue Solar Observatory with authenticated host acceptance,
  complete orbital coverage/orientations/assets and actual Pi performance
  gates before broad catalogue expansion or deployment.


- [ ] Deploy the hardened TransferPortal app/helper/policy together after refreshed
  idle-state/checkpoint checks. Live OMV still runs the older vulnerable helper.
- [ ] Accept VentSys endpoint/power-cut/sensor coverage before enabling safety
  automations; review socket/NAS privilege and upstream Mealie fetch boundaries.

- [ ] Accept a manual generation/isolated restore and recurring Hub schedule in
  an approved maintenance window. Prepared source is not deployed or enabled.


- [ ] Confirm phone receipt of the September17 corrected Watchtower report. Server
  delivery is proven: the04:02:49 UTC cached report says31 scanned,2 updates
  available,0 updated,0 failed and8 skipped, matching the04:02:48 UTC scan.
- [ ] Prove full-system/integration and real-user GardenKeeper upload recovery.
  The first scheduled OMV media-inventory check is queued; it will prove path
  coverage, not a production journal-entry or external-integration recovery. Hub's
  coordinated checkpoint remains one-off; recurring coverage is a separate task.


- [ ] Apply the prepared exact hosts mappings for Home Assistant, Frigate,
  Grafana, and Uptime Kuma from an elevated PC shell; verify each local HTTPS
  name while Mullvad remains connected. See the DNS resolver decision and
  `scripts/setup/windows/set-local-core-service-names.ps1`.


- [ ] Apply the approval-gated IPv6 reconciliation for the pre-existing
  DOCKER-USER Tailscale exception on port8094. The dashboard remains IPv4-only
  with bridge IPv6 disabled; follow
  `docs/procedures/troubleshooting-dashboard-ipv6-publication-guard.md` before
  any IPv6 publication or firewall change.


- [ ] Restore CT114's approved package path in a bounded maintenance change:
  October2 confirms no proxy, native cache-host UFW rejection and upstream503;
  security/update indexes expired June26. The prepared repair procedure retains
  the maintenance gate. Refresh signed metadata before trusting candidates,
  then simulate/review Fail2ban installation; no blind full upgrade.
- [ ] Implement and review the VentSys authenticated card/page bridge against
  `docs/procedures/ventsys-card-page-bridge-contract.md` before any dashboard
  deployment. Local startup error is fixed and five browser tests pass; public
  credentials remain prohibited and the page stays offline. The draft card is
  not connected to the page and is not accepted.

- [ ] Investigate HomeAdmin Wi-Fi throughput after fibre cutover: workstation
  measured 172 Mbps HTTPS versus 558-699 Mbps from the wired monitoring VM.
  Authenticated 2026-09-04 checks show OpenWrt 24.10.3, auto channel selecting
  100/HE80, PC signal around -76 dBm and current download PHY 432 Mbps. Compare
  local wired/Wi-Fi throughput and evaluate the AX210 driver update; plan the
  OpenWrt 25.12 upgrade separately and verify full WAN speed with a wired Zen test.
  See the current handoff for measurements and test limitations.
- [ ] Resolve Hive's existing app/account offline issue: owner still sees it
  offline despite established internet connections. Try the vendor's app
  force-close workaround, then check model/LED and Manage → Devices status.
- [ ] Reconnect Zyxel and cameras when ready, then rerun CCTV acceptance.

1. [x] Add the Installation Manual Suite v1 canonical entrypoint under `docs/install/START-HERE.md`
2. [x] Add numbered fresh-rebuild phase manuals under `docs/install/phases/`
3. [x] Add central install references for command locations, state, secrets, dependencies, versions, and decision gates
4. [x] Add draft docker-host service manuals for Tier 1, Tier 2, and Tier 3/evaluate services
5. [x] Add the companion setup-documentation checklist at `docs/install/INSTALL-TO-DO.md`
6. [x] Replace stale static diagrams with canonical Mermaid sources for architecture, install sequence, DNS/NTP, access, storage, docker-host services, and VentSys safety flow
7. [x] Deploy the reconciled 48-entry `home.local` domain inventory from `configs/openwrt/dhcp-config.conf` to live OpenWrt, restart dnsmasq, and pass `scripts/validation/validate-home-local-dns.ps1` against `192.168.10.1` (completed 2026-07-29)
8. [ ] Continue expanding each install phase until every command has expected output examples and every failure mode has a tested recovery path
   - Second September10 continuation adds download-gateway/Recomp operating
     manuals and MediaMTX recovery guidance, corrects legacy authentication/
     host-context advice, and repairs VM103/VM102 creation and pre-NAS phase
     dependencies. Household Hub source/migration/database restore and MediaMTX
     configuration-backup coverage remain explicit gaps in INSTALL-TO-DO.
   - 2026-09-10 continuation: reconciled router, operator, Proxmox, OMV and
     final-validation instructions with the September network/state records.
     Added `docs/troubleshooting/diagnostic-walkthroughs.md` for the app's five
     symptoms with Mermaid links and evidence boundaries, plus
     `docs/install/services/media-libraries.md` for three media services.
     Corrected stale recovery ports, disconnected-device claims and DNS wording;
     incorporated the separate September10 app deployment record. This is a
     documentation/source pass, not fresh hardware or restore acceptance.
   - 2026-08-24 continuation: expanded Mealie, Grocy and Obsidian LiveSync with
     pre-start/promotion gates, operator flows, consistent backups,
     loopback-only isolated restores, updates and version/data rollback. Added a
     last-safe-stop matrix for all 23 service manuals.
9. [ ] Work through the comprehensive checklist in `docs/install/INSTALL-TO-DO.md`
   - 2026-08-24 pass closed package/dependency, volatile-version,
     decision-gate, placeholder, command-label and per-service promotion-boundary
     coverage. Service/access-matrix review and live acceptance gates remain.
10. [ ] Run a full dry-read from `docs/install/START-HERE.md` after the next content expansion pass
    - 2026-08-24 structural dry-read passed 50-document link navigation, 52
      documented placeholders, 311 shell blocks and 66 PowerShell blocks. The
      full dry-run was blocked by a router invariant at that time. September
      recovery lint and compiler regression tests pass; an actual credentialed
      full rebuild and blank-hardware acceptance remain unproven.
11. [x] Deploy and document shared-iGPU CT 111 Frigate and CT 114 local AI architecture
12. [x] Reconcile the canonical architecture documentation on 2026-08-25:
    update current-state/service/access/name/cabling references, active setup
    guides, troubleshooting, monitoring and all affected Mermaid sources;
    rebuild the Mermaid Viewer and pass all 11 browser-side Mermaid parses.
13. [x] Build the read-only troubleshooting-dashboard proof of concept around
    five initial symptoms: Homepage access, Home Assistant availability, one
    camera path, P1S telemetry and backup freshness. Keep arbitrary shell and
    automatic remediation out of v1. Completed locally on 2026-08-25 with
    health-JSON import, honest unknown states, guided evidence collection,
    incident-report copy, nine model tests and desktop/mobile browser smoke.
14. [ ] Promote the troubleshooting dashboard from POC to a controlled live
    service: review the diagnostic wording, add collector-side backup detail to
    Windows if needed, approve DNS/Homepage exposure, deploy on staged port
    `8094`, and complete operator acceptance before calling it operational.
    - 2026-08-25 staged live on VM 103 at management-only
      `http://192.168.20.102:8094/`. Real Windows 13/13 snapshot import,
      desktop/mobile browser flow, container hardening, VLAN-10 allow,
      LAN/Tailscale/IPv6 denial and stop/start rollback all passed.
    - Remaining gate: authorize a workstation key on the Proxmox host and
      accept a real Proxmox JSON snapshot for backup freshness.
    - 2026-09-11 owner approved and deployed Homepage Tools > Troubleshooting,
      with Preview/Open tab at `/portal-preview/troubleshooting/` over existing
      Homepage HTTPS. No new DNS alias or firewall rule; mobile preview passed.
15. [x] Deploy MediaMTX `1.20.1` on VM 103 as an authenticated RTSP-over-TCP
    relay/recorder for the garage phone stream. The HomeAdmin-only firewall,
    separate publisher/viewer accounts, live relay and OMV recording validation
    passed on 2026-08-27.
    - [ ] Configure Larix on the OnePlus and the garage Pi player, then accept a
      real 30-minute session.
    - [ ] Choose a recording retention period before unattended/frequent use;
      automatic deletion is deliberately disabled meanwhile.

Planning baseline until explicitly revalidated:

- Treat OMV and Proxmox NFS backups as live. On 2026-07-05, Proxmox reported
  `omv-backups` active at 54.21% used, so the old 86-87% md0 high-water warning
  is cleared; keep normal monthly backup and SMART checks.
- Treat Frigate CT 111 as reachable with three previously proven cameras
  deliberately disconnected. Reconnect the Zyxel/cameras and rerun stream,
  recording/playback and notification acceptance before calling CCTV live.
- Treat Home Assistant native HTTPS as live at
  `https://192.168.20.101:8123` with the local `Home Local CA`. HTTP on
  port `8123` is no longer the active HA UI.
- Treat VentSys entities as unbuilt for implementation planning.

## Hardening and resilience roadmap

1. [x] Plan the whole-system hardening run before changing credentials or access paths: inventory all admin surfaces, service accounts, API tokens, SSH keys, certificates, Tailscale/WireGuard paths, OpenWrt rules, host firewalls, and password-manager records. See `docs/procedures/hardening-resilience-planning-runbook.md` (2026-09-18).
2. [x] Plan the whole-system resilience run before live drills: define recovery goals, access routes, trusted backups, restore order, and stop/ask gates for Mini PC, OMV, router, Home Assistant, docker-host, Frigate, llm-host, monitoring, Tailscale, local CA, and credential-loss scenarios. See `docs/procedures/hardening-resilience-planning-runbook.md` (2026-09-18).
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
38. [x] Complete the controlled docker-host patch window for Docker/containerd,
    Compose/Buildx, Python 3.13 and Tailscale candidates; completed 2026-08-01
    with fresh pre/post NAS backups, no reboot required, no pending upgrades and
    all 33 existing containers/endpoints healthy
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
52. [x] Approve and validate the Tailscale `192.168.30.20/32` Frigate host route
    for off-WiFi Frigate PWA access. On 2026-07-29 the route appeared in
    docker-host `PrimaryRoutes`/`AllowedIPs`, the authenticated HTTPS path
    returned the expected `401`, the unauthenticated API on `5000` remained
    blocked, and the workstation Tailscale state was restored after testing.

---

## Docker-host app roadmap

### Household, workshop and operations product roadmap

- [ ] Deliver the phased [[docs/procedures/household-workshop-operations-roadmap|Household, Workshop and Operations Product Roadmap]]. The read-only Today at Home/recovery-release contract is prepared in `docs/procedures/read-only-product-release-plan.md`; the owner-authorized local Hub recovery repository now provides the source baseline, while historical Git provenance remains unknown (see `docs/procedures/household-hub-source-recovery-register.md`). Obtain a bounded deployment decision before live adapters. Keep system-of-record ownership, confirmation gates and VentSys safety boundaries intact.

### Tier 1 - near-term core

- [ ] Deploy the prepared Transfer Portal transfer-grid canvas through the OMV
  native-service deployment route once OMV management access is available
- [ ] Complete Vaultwarden owner onboarding after live `vault.home.local` DNS is
  deployed: temporarily enable sign-up for the owner account only, disable it
  immediately afterward, then record the 2FA/recovery-code and owner-controlled
  emergency-access policy outside Git.
- [ ] Execute the approved 14 TB SMB case-collision recovery plan only after
  owner approval and preflight evidence. Server-side inspection on 2026-08-02 proved `Media` is the
  populated canonical library and `media` is a distinct, empty wrapper created
  eight minutes earlier that contains only `media/Media`. Windows SMB
  case-insensitive lookup aliases both spellings to the populated `Media`
  object, causing intermittent Explorer failures. OMV proved `/export/media`
  correctly bind-mounts only the canonical `Media` path, and no active
  NFS/systemd/fstab configuration references the stray wrapper. Do not delete
  or rename either path until the rollback path in
  `docs/procedures/smb-media-case-collision-recovery-plan.md` is reviewed and
  approved.
- [ ] Implement the allow-listed Immich album exporter into
  `jellyfin/immich-curated` with a manifest and review queue. Immich remains the
  photo system of record; do not mount its live library into Jellyfin. The
  non-destructive source, service/timer templates and contract tests are staged;
  a selected test album plus live Jellyfin/review/backup proof remain required.
- [ ] Apply the 2026-08-11 docker-host network/firewall remediation in a
  maintenance window: migrate automatic bridges to the explicit CIDR map,
  recreate the shared alerting network only with all dependants stopped, move
  Bambuddy from host networking to its scoped bridge, load the IPv6/8000
  firewall policy, and prove each service/denial path. Source and a preflight
  allocation table are ready. Live execution on 2026-08-21 completed every
  explicit bridge recreation, including Household Hub's shared dependency
  networks and `local-alerting`; Compose, health, HTTP, storage, dependency,
  VPN-egress, allowed/denied and firewall-persistence checks passed. Bambuddy
  alone remains on host networking because the P1S ports are unreachable from
  VM 103 itself. Restore that path, migrate Bambuddy to `10.240.23.0/24`, and
  obtain a zero-exit security audit before checking off this parent item.
- [ ] Add Homepage service widgets where an approved, least-privilege credential
  path exists. Prioritise already deployed Home Assistant, Frigate, Immich,
  Mealie, Grocy, AdGuard Home, Grafana, Uptime Kuma, Proxmox, OpenWrt and
  Tailscale; evaluate complementary Beszel/Netdata, APC UPS, Scrutiny,
  Speedtest Tracker, Authentik and Backrest only if their supporting services
  are deliberately adopted.

### Tier 2 - roadmap candidates

- [ ] Evaluate Paperless-ngx under `/opt/stacks/paperless-ngx/`
- [ ] Parked: Self-hosted LiveSync client rollout; backend/client prep exists, but Obsidian is no longer part of the near-term path
- [ ] Evaluate Actual Budget under `/opt/stacks/actual-budget/`
- [ ] Evaluate Scrypted under `/opt/stacks/scrypted/`

### Tier 3 - evaluate carefully

- [ ] Evaluate Portainer only if its convenience beats the added admin surface
- [ ] Revisit local registry mirror after more Compose workloads exist
- [ ] Evaluate Node-RED only if HA native automations are insufficient

## Home Assistant apps and enhancement roadmap

Companion App, ESPHome, Mosquitto, Terminal & SSH, and Studio Code Server/File
Editor are core Home Assistant tools. HACS remains optional and non-critical.
Safety paths, MQTT, firewall policy, backups, and VentSys emergency behavior
must work without HACS.

### Core HA tools

- [ ] Review Companion App sensors and enable only useful presence, battery, network, and notification sensors
- [ ] Prefer Studio Code Server for larger YAML/package edits; keep File Editor as fallback

### High-value candidates

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

### P1S expansion (after Bambuddy baseline)

- [ ] Evaluate [BambUI](https://github.com/fidoriel/BambUI) as a docker-host
  (`/opt/stacks/bambui/`) LAN-only, mobile-friendly P1S console after Bambuddy
  telemetry, MQTT TLS and the HA package have passed their baseline checks.
  Keep Bambuddy/HA as the safety and automation authority; verify that the two
  direct printer clients remain stable before retaining BambUI, use Tailscale
  for remote access, and add its data/backup, firewall and Uptime Kuma design
  before deployment.
- [ ] Evaluate [BambuHelper](https://github.com/Keralots/BambuHelper) as an
  optional physical ESP32 status display beside the P1S. Scope its Wi-Fi/VLAN
  placement and least-privilege path to the printer first; use it for local
  read-only status and optionally local smart-plug energy display, with any
  power control disabled until the VentSys and emergency-cutoff safety policy
  explicitly permits it.
- [ ] Research [bambu-printer-mcp](https://github.com/DMontgomery40/bambu-printer-mcp)
  for a future operator-assist workflow only. Confirm current P1S firmware,
  LAN-only/Developer Mode and Bambu access-code requirements; assess the
  project's maintenance, MQTT/FTPS command surface, file-storage permissions,
  network rules and secret handling. Design confirmation-gated, auditable
  print/pause/cancel actions with read-only status as the default. Do not
  deploy it, give an LLM autonomous printer control, or connect it to a safety
  or emergency-power path without an approved threat model and live test plan.

### Risk-gated automation candidates

- [ ] Keep Node-RED Tier 3/evaluate unless HA native automations become insufficient
- [ ] Evaluate AppDaemon only if Python automation apps are justified for non-critical logic
- [ ] Evaluate pyscript only for non-critical helper logic after a rollback plan exists
- [ ] Keep Claude/MCP or other AI automation as future advisory-only work; do not let it replace safety-critical HA/ESPHome/MQTT logic

---

## Immediate next actions (unblocked right now)

- [ ] Create `/opt/frigate/.env` after camera RTSP and MQTT credentials/certs are ready
  (review 2026-11-13: Frigate CT 111 is live with cameras disabled pending
  acceptance, so this may be obsolete; confirm against the Frigate section)
- [ ] Keep Docker registry mirror parked as Tier 3/evaluate until more Compose workloads exist

---

## Phase 1 — Network ✅ First-flight live / source follow-up pending

### Configuration (all complete)

### Deployment
- [ ] Fill in MAC addresses in dhcp-config.conf (Proxmox host, VMs, NAS)
- [ ] Keep WireGuard fallback clients unrolled unless Tailscale daily-access posture changes or resilience drills require activation
- [ ] Enable DDNS on router only if WireGuard fallback endpoint maintenance becomes annoying

---

## Phase 2 — Core infrastructure ⏳

### Proxmox
- [ ] Run full CT 114 post-upgrade validation for the Qwen3-14B 64k profile: Home Assistant Assist text/voice, SearXNG search, Mealie recipe save/display/readout workflow, Open WebUI, host swap, and Frigate concurrency
- [ ] Find why Frigate's main process grew to ~5.3 GB RSS (3 cameras) before it recurs at the 6 GiB limit (consider a persistent `pct set 111 -memory 8192`); watch CT 111 memory, and add a Grafana/Kuma alert on CT memory near its limit and on host I/O pressure
- [ ] After the `main`/`codex/portal-refinement` merge lands: rebuild the Mermaid Viewer and redeploy `/opt/stacks/mermaid-viewer/dist` (live already runs the codex generator); compare the merged Homepage, SearXNG, OpenWrt DHCP and llm-host firewall sources against the live hosts before deploying from them
- [ ] Reconcile `configs/openwrt/firewall-config.conf` with the live router: the repo LAN → docker-host rule lists no Homepage portal ports (`8180`–`8210`)
- [ ] HA: add Wyoming Protocol integration `192.168.20.104:10201` and set the Overwatch pipeline TTS to `metrocop`; add Uptime Kuma TCP monitor for `10201`
- [ ] Recreate the `voice-mixer` container so the web UI picks up the gap fix (image `voice-mixer:local` already patched; rollback tag `voice-mixer:pre-metrocop-tts`)
- [ ] HA: reload the Wyoming openWakeWord integration and set the Overwatch pipeline wake word to `overwatch` (custom model live on CT 114)
- [x] Voice PE re-tested by voice after the 2026-11-13 `internal_url` fix: "Overwatch", a time question and a weather question were heard, answered and spoken (if it ever goes silent again, check Settings > System > Logs for `Unable to determine Home Assistant URL`)
- [x] Overwatch speed 3a/3b deployed 2026-11-12: Overwatch pipeline prefers local intents; direct web-search route in `llamacpp_conversation` (web search 26.5 s -> ~10 s, time 7.4 s -> 0.5 s)
- [x] Qwen3-30B-A3B is the production model on CT 114 (2026-11-13): compose switched (40960 ctx, f16 KV, `--cache-ram 2048` since the same day, `restart: unless-stopped`), trial and capture-proxy containers removed, voice verified through the Voice PE pipeline; 14B GGUF and `docker-compose.yml.bak-20261113-pre-30b` kept for rollback. See `HANDOFF-2026-11-11-llm-igpu-speed.md`
- [ ] Still untested from the LLM speed work: Frigate detector speed, SYCL backend
- [x] Model-free device-state route deployed 2026-11-12 (`llamacpp_conversation`): "is X on/open?" and "what is the X temperature?" answered in code (~21 s -> 0.0 s); unknown devices get "I have no device called X"
- [x] Phase 1 of `docs/decisions/10-overwatch-voice-routing-architecture.md` deployed 2026-11-12/13: every tool on every turn, stable cached prefix, new prompt, warm-up with failure canary (78% -> 91% on the shared checks; first deploy rolled back, see handoff)
- [x] Overwatch weather at home answered in code from `weather.forecast_home` (today, tomorrow, rain; 0.0-0.1 s) and the warm-up now runs as the Voice PE so its first spoken question is no longer cold (79.9 s -> ~3.5 s), 2026-11-13
- [x] Overwatch breadth work deployed 2026-11-13 (accuracy 86/86 on the harness, was 58/74 before Phase 1): area/multi-device state answers in code (garage temperature/humidity/motion 11-17 s -> 0.0 s, "is the fan on" reads both fans), `calculate` and `date_info` tools (tip, split, conversion, days until, weekday; a birthday asked in a past year now gets the next occurrence), `web_search` news mode (headlines and sports read out three stories, ~15 s), a retry when the model describes a tool call instead of making it, merged `mealie_llm` URL hardening. Caveats: the checks are partly lenient (a clarifying question or any non-refusal passes the sports check); trivial sums such as "two plus two times three" now go through `calculate` and take ~10 s instead of 2.6 s
- [ ] Overwatch: decision 10 phase 2 (turn the ~15 `_maybe_direct_*` shortcuts into one declarative reflex table with uniform fall-through) and the calendar are the remaining parts; weather for another place works through web search (about 15 s)
- [x] Overwatch branch `claude/llm-igpu-speed-handoff-d9cffa` fast-forwarded into `main` on 2026-11-13 (it already contained `main`'s tip `377dd29`; restore tag `pre-ff/main-20261113` marks the old `main`). `codex/portal-refinement` no longer exists. Nothing has been pushed from this repository.
- [ ] Delete `/root/cap/captured.jsonl` (5 MB of personal voice requests and prompts from the 2026-11 experiments) on CT 114 when no longer needed
- [x] Voice cache: different prompt contexts (Voice PE, HA chat box, accuracy.py) evicted each other in llama.cpp (1 GiB `--cache-ram` held one ~620 MB prompt, causing 56-91 s cold stalls); raised to 2048 on 2026-11-13 (CT 114 memory available ~2-3 GB afterwards; watch it)
- [x] Voice PE speech-to-text: checked 2026-11-13, CT 114 already runs Parakeet TDT 0.6B v2 (sherpa-onnx), not a small Whisper, so the occasional leading junk ("the we what's the weather today") is audio onset noise, not model size; the weather matching tolerates it
- [ ] Choose a calendar source for Overwatch (HA has no calendar integration), and expose the existing `weather` entity plus a forecast tool (decision 10, phase 3)
- [ ] Delete the leftover "acceptance test cheese" item from the Grocy shopping list (left by the 2026-11-12 write-action test)
- [ ] Test "Overwatch" by voice on the Voice PE (model only tested on synthetic clips): if it misses, lower `probability_cutoff` (0.9 -> 0.7) or raise `tensor_arena_size` in `voice/wakeword-micro/overwatch.json`, rebuild with `tools/esphome_dashboard.py`; once happy, set "Wake word" (slot 1) to Overwatch and "Wake word 2" to `no_wake_word`
- [ ] Garage voice satellite: buy a Home Assistant Voice Preview Edition (chosen over the Waveshare ESP32-S3-AUDIO-Board for its XMOS echo cancellation and noise suppression, line out and official support); feed a wired powered speaker from its 3.5 mm line out (avoids Bluetooth wake-up clipping); keep the `overwatch` wake word, either by streaming to HA openWakeWord or by training a microWakeWord model; add an optional ~0.5 s output lead-in only if the final speaker clips

### Home Assistant VM (VM 100)

### Frigate (CT 111; VM 101 retained only for rollback)
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

---

## Phase 3 — VentSys fire safety ⏳ Boards flashed and under supervised testing; not commissioned

### Hardware procurement
> Review 2026-11-13: boards are flashed and running, so many boxes below are
> probably already satisfied, but nothing has been checked against actual
> inventory. Owner to tick or delete against what is physically on hand.

- [ ] 2× ESP32-DevKitC (sensor boards — ventsys-fdm-sensor, ventsys-sla-sensor)
- [ ] 1× ESP32-DevKitC (fan controller — already wired to GPIO23)
- [ ] Feedback-capable classic ESP32 valve controllers for the standard valves
  (ESP32 D1 Mini/carrier design; GPIO16 PWM and GPIO35/ADC1_CH7 feedback)
- [ ] 4× DS18B20 waterproof temperature probe
- [ ] 2× BME680 I2C breakout (temp/humidity/pressure/IAQ gas)
- [ ] 2× MQ-135 (VOC / air quality)
- [ ] 2× MQ-2 (smoke detection)
- [ ] 2× differential pressure sensor (for duct airflow)
- [ ] Feedback-capable analog servos for the standard butterfly valves (confirm
  four-wire feedback lead, travel range and supply voltage before purchase)
- [ ] 1× 125mm inline duct fan with PWM control
- [ ] PrintAirPipe STL files (€29, nerdiy.de)
- [ ] 2kg PLA+ filament + 1kg PLA-HT (fire-retardant)
- [ ] 2× smart plugs with energy monitoring (VLAN 50 compatible)
- [ ] Resistors/capacitors: 4.7kΩ (DS18B20/I2C pull-ups); one 10kΩ series
  resistor, 20kΩ ADC-to-GND resistor and 100nF ADC-to-GND capacitor per
  standard-valve feedback channel; 470uF–1000uF bulk capacitor at each servo
  power split
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
- [ ] Wire each feedback-capable standard valve controller: GPIO16 PWM plus feedback lead through
  the 10k/20k/100nF network to GPIO35/ADC1_CH7; measure the ADC node at full travel
  and confirm it remains at or below 3.3V before connection. The E2 branch now
  uses a normal three-wire servo and has no feedback lead or ADC network.
- [ ] Bench-calibrate each feedback-capable standard valve's raw feedback-voltage range against
  physical closed/open stops before using it as a position measurement or safety input
- [ ] With E2 branch installed on its pipe and under load, supervise an
  intermediate-position holding test. The 2026-10-05 firmware holds PWM at
  1–99 until another command or power loss; 0/100 detach after one second.
  Check sustained sound, temperature, supply stability, and post-reset
  behavior before accepting this as an unattended operating mode.
- [ ] Note DS18B20 addresses after first flash, update ESPHome YAML
- [ ] MQ sensor 24–48h burn-in before calibrating thresholds

### ESPHome flashing and adoption
- [ ] Flash fan controller via USB (`ventsys_fan_controller.yaml`)
- [ ] Flash each standard valve controller via USB using its dedicated active
  `configs/esphome/ventsys_*_valve.yaml` file; do not use the historical bundle
  `ventsys_valve_controller.yaml` as the production source
  - [ ] Bench-calibrate E1's physical closed/open stops with the free horn
    under direct observation, then verify its linked valve range. The copied
    940–2000 µs window and fresh-board displayed value 50 are provisional.
  - [ ] Verify E1's GPIO33 touch toggle under supervision. The earlier serial
    watch repeatedly commanded 50% because both targets were seeded at 50;
    the operator may have touched GPIO33, so false triggering is unproven.
    Investigate the later serial-port closure and Wi-Fi inactivity dropout
    before linking the valve.
  - [ ] Bench-calibrate MAIN-2's physical open and closed stops under direct
    observation before linking 0–100 to valve travel. Current 940–2000 µs
    range is copied from E2 and remains provisional for MAIN-2.
  - [ ] Bench-calibrate MAIN-1's physical stops with the free horn before
    linking the valve. Its 940–2000 µs window is provisional.
- [ ] Flash FDM sensor board via USB (`ventsys_fdm_sensor.yaml`)  # A5-3: per-device YAML now exists (A4-4)
- [ ] Flash SLA sensor board via USB (`ventsys_sla_sensor.yaml`)  # A5-3: per-device YAML now exists (A4-4)
- [ ] Flash booth sensor board via USB (`ventsys_booth_sensor.yaml`)  # A5-3: per-device YAML now exists (A4-4)
- [ ] Add `mqtt_ca_cert` to both repo and HA-side ESPHome `secrets.yaml` as part of the VentSys TLS migration path
- [ ] Bench-calibrate the 360 intake v2 Nerdiy candidates before deployment. The board previously labeled FDM at `.61` (MAC `CC:BA:97:F0:E3:EC`, now assigned SLA) was reflashed on 2026-10-09 to remove a raw LEDC `turn_on()` full-duty transient; its Open/Close directions were confirmed under the old label. Endpoint travel still needs calibration. Current firmware defaults are closed=30/open=60; servo PWM GPIO0, LED data GPIO1, endpoint detach after 1s. Local touch toggle is parked until C6-compatible input wiring is confirmed.
- [ ] Confirm SLA 360 physical Open/Close direction and endpoint travel.
- [ ] Resolve installed SLA .32 versus planned FDM array 2 address conflict before deployment.
- [ ] Validate MAIN-2 repeated cold starts and sustained operation on independent supply with actual servo load. One software restart passed in 7.7 s with saved settings/PWM inactive; USB reset/power cause remains unproven. Reset/heap/loop diagnostics flashed.
- [ ] Adopt all devices in ESPHome add-on (17 ESP32 boards + plugs)
- [ ] Once no printer job relies on the intake control, OTA the swapped identities in place: FDM `.62`/`A0:85:E3:AE:5B:C8`, SLA `.61`/`CC:BA:97:F0:E3:EC`. Both live boards still run their old name/topic and were offline in Builder at the last check. OTA each at its existing IP, then verify HA names, IPs, MACs, and MQTT topics before using either valve.
- [ ] After the collision-safe FDM/SLA 360 firmware reassignment, test Power Off on FDM only after confirming no active printer/process relies on its valve; then physically reset/power-cycle and verify reconnect. VentSys remains uncommissioned and under testing.
- [ ] Build and flash the board-management firmware to remaining offline boards; six online devices updated on 2026-10-10; verify awake-state buttons and physical restart. Do not shut down boards while relying on their sensing or actuator control.
- [ ] Verify MQTT topics publishing: `mosquitto_sub -t 'ventsys/#' -v`
- [ ] Confirm automations fire on test sensor triggers
- [ ] Test emergency power cutoff sequence end-to-end
- [ ] Evaluate `mode: restart` on the 12 VentSys HA mode scripts if rapid mode-click queueing causes oscillation in practice
- [ ] Verify E2 branch restores a deliberately commanded non-100 position
  after power loss once its physical range is calibrated; its `restore_value`
  firmware and 100 first-boot seed are deployed, but the non-100 test is open.
- [ ] Stand up the garage Pi 5 desktop/kiosk for the VentSys dashboard using `docs/install/garage-pi-desktop-setup-guide.md` once the display hardware is ready

---

## Phase 4 — Storage ⏳

- [ ] Configure the scheduled vault backup only after an explicit approval,
  first manual `-Execute` copy, and restore-to-temporary-folder proof

---

## Phase 5 — NVR / Cameras ⏳

- [ ] Before production camera re-enable, perform physical unavailable/recovered
  RTSP, VA-API decode, sustained memory/recording/playback and HA acceptance.
  The bounded synthetic test does not certify long-term real-stream load.

- [ ] Select the model and requirements for the remaining camera rollout.
  Three ANNKE C500 cameras are already proven with Frigate; keep H.265, RTSP,
  PoE budget and Frigate compatibility as selection gates.
- [ ] Purchase and commission the remaining fourth camera when its model is
  selected; the GS1900 PoE switch and three ANNKE C500 cameras are live.
- [ ] Record sourced camera and smart PoE switch model numbers, firmware lines, RTSP/substream paths, PoE budget, management VLAN behavior, and reset procedures in `docs/procedures/frigate_camera_preflight_checklist.md`
- [ ] Bench-test one camera at a time using `docs/procedures/frigate_camera_preflight_checklist.md` before permanent mounting
- [ ] Test person detection notifications in HA

---

## Phase 6 — Security hardening

- [ ] Add least-privilege central collectors for Proxmox task/backup logs, HA,
  Frigate and CT 114 service logs; do not widen guest access just for Grafana
- [ ] Prepare the OMV host/SMART/RAID/filesystem/service collector and replace
  the NAS dashboard shell after bounded collector/deployment review.
  October2 host-local JSON source/six tests/live one-off read-only proof are
  complete; scheduled least-privilege production, metrics shipping and dashboard
  acceptance remain open. See [[docs/procedures/omv-health-collector-preparation]].
- [ ] Re-open Grafana/Uptime Kuma embedding work only after same-origin HTTPS/reverse-proxy path and auth model are approved
- [ ] Add Uptime Kuma dashboard view into Home Assistant after same-origin reverse proxy/HTTPS path exists
- [ ] Add Grafana dashboard view into Home Assistant (Lovelace panel/iframe) once auth/embedding behavior is stable
- [ ] Evaluate Telegraf UI integration path (direct Telegraf has no real UI; expose Influx/Grafana views in HA instead)
- [ ] Extend `Fail2ban` beyond the live docker-host and Frigate SSH baselines
  to other applicable Linux service hosts
- [ ] Execute IDS/IPS progression Phase A (`docs/procedures/ids_ips_progression_plan.md`): monitor Fail2ban jails/bans and tune policy after live observation
- [ ] After at least 30 days of baseline security-event data, decide CrowdSec pilot vs defer and document the decision
- [ ] Add a scoped internal penetration-testing pass after hardening + update governance stabilize; record findings and remediation evidence
- [ ] Set up WireGuard DDNS if ISP IP changes frequently

---

## Ongoing / maintenance

- [ ] Verify Pocketry8211 over mobile data; review narrow Tailscale grant if
  blocked. Real-tool physical-fit acceptance is separate.

- [ ] Confirm the first unattended Bambuddy staging/install window; manual
  end-to-end update and Task Scheduler no-update run are the initial proof.

- [ ] Perform a controlled VM103 reboot proof for DNS, Homepage, browser `8207`, native `8181`.

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
- [ ] Weekly: append an entry to `docs/procedures/update_review_log.md` (Watchtower monitor-only signals + host package candidates + planned patch window)
- [ ] Next patch window: update docker-host packages from the current candidate list, reboot if kernel package changes, and rerun router/health/Grafana checks
- [ ] Repair docker-host's missing default `docker0` bridge for normal dependency
  builds. Recomp Tracker no longer depends on a running-container hotfix.
- [ ] After any config change: `git add -A && git commit && git push`
- [ ] When hardware arrives: update MAC addresses in `dhcp-config.conf`
- [ ] When cameras confirmed: update RTSP URLs in `configs/frigate/config.yml`
- [ ] When sensors connected: update DS18B20 addresses in ESPHome YAML


- [ ] After VentSys installation, execute [[docs/procedures/ventsys-relative-airflow-baselines|relative airflow baseline matrix]]: verify trunk routing/endpoints and fan-step mapping, then nine configurations at ten speeds with repeats; add mixed/booth configurations when used.

- [ ] Revert temporary November10 Mosquitto debug logging and server diagnostic capture after conflict investigation; follow docs/procedures/ventsys-temporary-mqtt-logging.md.

- [ ] FDM CO firmware OTA succeeded November 10; after warm-up capture and verify a clean-air baseline and test the complete alert path. Resolve planned FDM-array-2 `.32` conflict before adoption. CO is qualitative; the removed smoke-labelled channel was not a smoke sensor.
