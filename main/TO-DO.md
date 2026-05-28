---
title: Project Tasks
description: Implementation tasks by phase — updated May 2026
tags: [tasks, implementation]
aliases: [TODO, Tasks]
created: 2025-09-15
modified: 2026-05-27
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
7. [ ] Continue expanding each install phase until every command has expected output examples and every failure mode has a tested recovery path
8. [ ] Work through the comprehensive checklist in `docs/install/INSTALL-TO-DO.md`
9. [ ] Run a full dry-read from `docs/install/START-HERE.md` after the next content expansion pass

## Operational next steps

1. [x] Confirm live/source parity for valve-1 MQTT firewall state: no temporary plain-MQTT `1883` exception exists live, and source remains TLS `8883`-only for VentSys MQTT
2. [x] Close stale valve-1 plain-MQTT follow-up tasks to avoid reintroducing insecure `1883` access while VentSys migration proceeds on TLS
3. [x] Deploy Tailscale on docker-host and advertise only `192.168.20.101/32` and `192.168.40.50/32`
4. [ ] Keep WireGuard configured as a dormant fallback; update clients only after Tailscale is tested
5. [x] Clean up duplicate docker-host UFW routed DNS forward rules and keep canonical subnet-based rules for `172.20.0.0/16` (`53/udp`, `53/tcp`, `853/tcp`)
6. [x] Document temporary router WiFi uplink (`wwan_uplink`) operating policy in `docs/procedures/router_temporary_uplink_policy.md`
7. [x] Deploy `dashboards/ventsys-card-wrapper.html` to HA and verify the VentSys dashboard works inside a Lovelace iframe card
8. [x] Explicitly park embedded Grafana-in-HA work behind direct-link-only access until HTTPS/reverse proxy same-origin path is in place
9. [x] Add an external health signal for the monitoring VM so monitoring failure is visible even when Uptime Kuma itself is down
10. [ ] Configure OMV-backed Home Assistant backups once NAS storage is live, while keeping fast local Proxmox recovery on the MINIX
11. [ ] Start Frigate properly after `.env`, RTSP details, and MQTT credentials are ready; keep HTTPS/SSL and WebRTC audio as required prerequisites
12. [ ] Expand VentSys beyond valve 1: finish the MQTT TLS migration path, then flash/adopt the remaining ESPHome devices
13. [x] Deploy AdGuard Home on docker-host per `docs/decisions/04-dns-resolver-and-adblocking.md`
14. [x] Re-run router-deploy validation after the router-local NTP/deploy-tooling update
15. [x] Validate Uptime Kuma notification dispatch to ntfy (`ntfy Monitoring`): monitor #17 (Whoogle) failure was detected and ntfy `messages_published` increased (`14` -> `15`) during controlled outage on 2026-05-28
16. [x] Add repo-side Frigate credential template at `configs/frigate/frigate.env.example`
17. [x] Re-verify pre-NAS Proxmox backup policy/retention and run one archive integrity check (`zstd -t` on latest VM 100 backup)
18. [x] Draft OMV storage cutover execution checklist at `docs/procedures/omv_storage_cutover_checklist.md`
19. [x] Confirm HA-side monitoring health states from Home Assistant UI (all `on`): `binary_sensor.monitoring_stack_externally_healthy`, `binary_sensor.monitoring_vm_grafana_reachable`, `binary_sensor.monitoring_vm_influxdb_reachable`, `binary_sensor.uptime_kuma_reachable_from_ha`

---

## Docker-host app roadmap

### Tier 1 - near-term core

- [x] Validate Tailscale from an off-LAN client after docker-host auth and route approval
- [x] Deploy AdGuard Home under `/opt/stacks/adguard-home/`
- [x] Deploy Immich skeleton under `/opt/stacks/immich/` with local placeholder storage; OMV-backed real imports still blocked
- [x] Deploy Homepage under `/opt/stacks/homepage/`
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
- [ ] Evaluate Mealie under `/opt/stacks/mealie/`
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
- [ ] Review Companion App sensors and enable only useful presence, battery, network, and notification sensors
- [x] Keep Mosquitto as the required MQTT broker add-on
- [x] Keep ESPHome as the required VentSys firmware/adoption add-on
- [x] Keep Terminal & SSH available for HA-side diagnostics
- [ ] Prefer Studio Code Server for larger YAML/package edits; keep File Editor as fallback

### High-value candidates

- [ ] Install HACS only after a current HA backup exists
- [ ] Evaluate Frigate Card when Frigate and cameras are live
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
- [ ] Configure WireGuard fallback clients only after Tailscale daily access is tested
- [ ] Enable DDNS on router only if WireGuard fallback endpoint maintenance becomes annoying

---

## Phase 2 — Core infrastructure ⏳

### Proxmox
- [x] Install Proxmox VE on MINIX
- [x] Configure vmbr0 VLAN-aware bridge, trunk on enp1s0
- [x] Set static IP 192.168.10.10 on vmbr0.10
- [ ] Enable IOMMU (intel_iommu=on) for iGPU passthrough
- [ ] Run `configs/proxmox/vm-setup.sh`
- [x] Configure temporary local Proxmox daily backup (02:00, VMs 100/101/102/103, keep 2)

### Home Assistant VM (VM 100)
- [x] Start VM 100, complete HAOS onboarding wizard
- [x] Set static IP 192.168.20.101 via nmcli
- [x] Install add-ons: Mosquitto, File Editor, Terminal, ESPHome
- [x] Configure MQTT integration (`localhost:1883` for Stage 1 pre-TLS; switch to `localhost:8883` after TLS migration)
- [x] Copy `ventsys_ha_package.yaml` and `ventsys_ha_scripts.yaml` to `/config/packages/`
- [x] Do not copy `ventsys_ha_optional.yaml` yet (load only after its prerequisites are met)
- [x] Copy `dashboards/ventsys-dashboard.html` to `/config/www/ventsys-dashboard.html`
- [x] Generate Long-Lived Token → paste into `HA_CONFIG.token` in live dashboard copy
- [x] Confirm dashboard shows ◉ HA LIVE
- [x] Enable HA 2FA (TOTP)
- [x] Copy `dashboards/ventsys-card-wrapper.html` to `/config/www/ventsys-card-wrapper.html`
- [x] Add a Lovelace iframe/panel view that uses the VentSys card wrapper
- [ ] Configure NAS as backup target, set daily 03:00 schedule (14 keep)
- [x] Validate router-local NTP for non-HA-managed restricted devices

### Frigate VM (VM 101)
- [x] Create VM 101 from Debian 13 cloud image (hostname: frigate-nvr, SSH only)
- [x] Set static cloud-init IP 192.168.30.20
- [x] Note MAC and add to dhcp-config.conf (`BC:24:11:9C:25:87`)
- [x] Install Docker (official repo)
- [x] Deploy `configs/frigate/config.yml` to `/opt/frigate/config/`
- [ ] Create `/opt/frigate/.env` with FRIGATE_RTSP_PASSWORD and FRIGATE_MQTT_PASSWORD
- [x] Create host dirs: `mkdir -p /opt/frigate/db`
- [ ] Start Frigate: `docker compose up -d`
- [ ] Configure HTTPS/SSL for Frigate UI before regular use
- [ ] Confirm Frigate UI over HTTPS/SSL, not plain HTTP
- [ ] Configure WebRTC audio for camera streams
- [ ] Set up Lumen on an Apple device for camera feeds (manual user step, alongside Android UI)
- [x] Manage VM 103 as `docker-host` via `scripts/setup/proxmox/docker_host_setup_guide.md`
- [x] Deploy Bambuddy as `/opt/stacks/bambuddy` on docker-host
- [x] Confirm Bambuddy UI at http://192.168.20.102:8000
- [ ] Add Frigate integration in HA
- [ ] Copy `configs/home-assistant/bambuddy_p1s_package.yaml` to `/config/packages/` on HA
- [ ] Replace `<P1S_SERIAL>` placeholder in bambuddy_p1s_package.yaml with real serial
- [ ] Confirm `binary_sensor.p1s_printing` and print state entities appear in HA
- [ ] Enable iGPU passthrough (Phase 6 of frigate_vm_setup_guide.md) — after confirming IOMMU

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
- [x] Create remaining controller YAMLs -- ALL exist in configs/esphome/ (A5-3 fix: Fix #12 is resolved):
  ventsys_main_valve1/2, fdm/sla_branch_valve, fdm/sla_print_valve, fdm/sla_360_valve (8 valves), ventsys_booth_fan.yaml (spray fan)
- [ ] Flash FDM sensor board via USB (`ventsys_fdm_sensor.yaml`)  # A5-3: per-device YAML now exists (A4-4)
- [ ] Flash SLA sensor board via USB (`ventsys_sla_sensor.yaml`)  # A5-3: per-device YAML now exists (A4-4)
- [ ] Flash booth sensor board via USB (`ventsys_booth_sensor.yaml`)  # A5-3: per-device YAML now exists (A4-4)
- [ ] Add `mqtt_ca_cert` to both repo and HA-side ESPHome `secrets.yaml` as part of the VentSys TLS migration path
- [ ] Migrate `ventsys_main_valve1.yaml` from MQTT `1883` to `8883` with `certificate_authority: !secret mqtt_ca_cert`
- [x] Remove valve-1 temporary plain-MQTT firewall follow-up task because no live/source `1883` exception is present
- [ ] Adopt all devices in ESPHome add-on (17 ESP32 boards + plugs)  # A5-3: was 'all 4 devices' - pre-expansion count
- [ ] Verify MQTT topics publishing: `mosquitto_sub -t 'ventsys/#' -v`
- [ ] Confirm automations fire on test sensor triggers
- [ ] Test emergency power cutoff sequence end-to-end
- [ ] Evaluate `mode: restart` on the 12 VentSys HA mode scripts if rapid mode-click queueing causes oscillation in practice
- [ ] Harden the dashboard page-init valve visual calls so a future script reorder cannot publish `0` to all valve topics on refresh
- [ ] Revisit `restore_value` behavior for valve position entities so device restarts do not assume `0%` after physical movement
- [ ] Stand up the garage Pi 4 kiosk for the VentSys dashboard once the display hardware is ready

---

## Phase 4 — Storage ⏳

- [ ] Purchase or allocate OMV-capable NAS hardware and storage drive(s)
- [ ] Follow `omv_nas_setup_guide.md` phases 1–7
- [ ] Configure NFS exports (Frigate, HA, Immich, configs shares)
- [ ] Keep Frigate "live" recordings on MINIX local storage first; add NAS archiving after the NAS is online
- [ ] Mount NAS in Frigate VM (`/mnt/nas/frigate`) and update docker-compose.yml volume
- [ ] Add OMV as HA network storage → verify backup writes successfully
- [ ] Configure robocopy or rsync scheduled task for vault backup to NAS
- [ ] Enable SMART monitoring on NAS drives

---

## Phase 5 — NVR / Cameras ⏳

- [ ] Select PoE IP camera models (H.265, RTSP, compatible with Frigate)
- [ ] Purchase 4× cameras and PoE switch
- [ ] Keep LAN3 reserved for the future managed PoE camera switch; Hive placement remains parked
- [ ] Mount cameras, run CAT6 to PoE switch on VLAN 30
- [ ] Assign static IPs: cameras at 192.168.30.21–24 (MAC reservations in dhcp-config.conf)
- [ ] Update RTSP paths in `configs/frigate/config.yml` (currently placeholder `/stream1`)
- [ ] Restart Frigate, confirm all 4 camera streams visible in UI
- [ ] Test person detection notifications in HA

---

## Phase 6 — Security hardening

- [x] Set up MQTT TLS (8883) — broker listener live, CA/broker certs installed, authenticated TLS pub/sub verified
- [ ] Remove temporary 1883 firewall rule only after HA, Bambuddy, Frigate, and future ESPHome/VentSys clients are migrated to 8883
- [ ] Enable HTTPS on HA — follow `ssl_tls_guide.md` (choose Option A/B/C)
- [ ] Configure Fail2ban on Frigate VM
- [x] Deploy monitoring VM on VLAN 60 (Uptime Kuma, InfluxDB, Grafana, Telegraf)
- [x] Create baseline Uptime Kuma monitors for core infrastructure
- [x] Forward OpenWrt syslog to Telegraf/InfluxDB
- [x] Export Home Assistant state history to InfluxDB
- [x] Configure Grafana InfluxDB datasource and baseline Home Automation dashboard
- [x] Add HA Monitoring page/sidebar entry with direct links to Grafana and Kuma
- [x] Deploy internal ntfy notification service for future HA/Kuma/Grafana alerts
- [x] Prepare HA HTTPS certificate files without enabling HTTPS cutover
- [ ] Stabilize embedded Grafana view inside HA (current issue: login loop / auth behavior)
- [ ] Revisit Grafana anonymous Viewer access after same-origin HTTPS path is in place
- [ ] Add Uptime Kuma dashboard view into Home Assistant after same-origin reverse proxy/HTTPS path exists
- [ ] Add Grafana dashboard view into Home Assistant (Lovelace panel/iframe) once auth/embedding behavior is stable
- [ ] Evaluate Telegraf UI integration path (direct Telegraf has no real UI; expose Influx/Grafana views in HA instead)
- [x] Add an external health signal for monitoring VM (HA-side check) so Kuma-down is still detected
- [x] Deploy AdGuard Home on docker-host as selected DNS filtering engine
- [x] Add/validate router DNS enforcement rules for filtering coverage and public fallback
- [x] Add monitoring for the DNS filtering service before making it the only resolver path
- [x] Verify pre-NAS Proxmox local backup job and latest backups for VMs 100/101/102/103
- [ ] Add `Fail2ban` to live Linux services where exposed/internal auth surfaces justify it
- [ ] Revisit IDS/IPS only after centralized logging is live; prefer Suricata on dedicated x86 over router-hosted IDS
- [ ] Set up WireGuard DDNS if ISP IP changes frequently
- [x] Run staged core health baseline and confirm required live services are green (`health_check.sh --json`: PASS=11/FAIL=0; hardware-dependent checks skipped/unknown until devices exist)

---

## Ongoing / maintenance

- [ ] Monthly: run backup health checklist (`backup_strategy.md`)
- [ ] Monthly: check SMART status on NAS drives
- [ ] After any config change: `git add -A && git commit && git push`
- [ ] When hardware arrives: update MAC addresses in `dhcp-config.conf`
- [ ] When cameras confirmed: update RTSP URLs in `configs/frigate/config.yml`
- [ ] When sensors connected: update DS18B20 addresses in ESPHome YAML
