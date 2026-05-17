---
title: Project Tasks
description: Implementation tasks by phase — updated May 2026
tags: [tasks, implementation]
aliases: [TODO, Tasks]
created: 2025-09-15
modified: 2026-05-14
type: task-list
status: active
---

# Project Task List

**Links:** [[README|Overview]] | [[PROJECT-INDEX|Index]]

---

## Next 10 project steps

1. [ ] Add the live `ventsys-main-valve-1` plain-MQTT firewall exception to `configs/openwrt/firewall-config.conf` so router redeploys do not wipe it before TLS migration
2. [ ] Run router validation after the valve-1 firewall-source change (`python tools/router-deploy/lint.py` and `python tools/router-deploy/compile.py --profile first-flight`)
3. [ ] Configure WireGuard VPN clients for the first 3 devices and test real remote access
4. [ ] Enable DDNS on the router if WAN IP churn makes WireGuard endpoint updates annoying
5. [x] Deploy `dashboards/ventsys-card-wrapper.html` to HA and verify the VentSys dashboard works inside a Lovelace iframe card
6. [ ] Stabilize embedded Grafana view inside HA or explicitly park it behind direct-link-only access until HTTPS/reverse proxy work is done
7. [ ] Add an external health signal for the monitoring VM so monitoring failure is visible even when Uptime Kuma itself is down
8. [ ] Configure NAS-backed Home Assistant backups once NAS storage is live, while keeping fast local Proxmox recovery on the MINIX
9. [ ] Start Frigate properly after `.env`, RTSP details, and MQTT credentials are ready; keep HTTPS/SSL and WebRTC audio as required prerequisites
10. [ ] Expand VentSys beyond valve 1: finish the MQTT TLS migration path, then flash/adopt the remaining ESPHome devices

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
- [ ] Decide whether a Docker registry mirror is justified after more Compose workloads exist

---

## Phase 1 — Network ✅ Configs complete / ⏳ Deployment pending

### Configuration (all complete)
- [x] 10-segment architecture designed ✅
- [x] `vlan-config.conf` — bridge, VLANs, interfaces, WireGuard ✅
- [x] `firewall-config.conf` — zones, inter-VLAN rules, VentSys ports ✅
- [x] `dhcp-config.conf` — scopes, reservations, DNS ✅
- [x] `wireless-config.conf` — 5 SSIDs, channel plan, WPA3/WPA2 ✅
- [x] Router setup phases 1–8 documented ✅
- [x] Network testing guide written ✅
- [x] WireGuard VPN guide written ✅
- [x] MQTT 1883→8883 deployment note added to firewall config ✅
- [x] VLAN 1 port assignment bug fixed in Phase 2 script ✅
- [x] Country code corrected GB in Phase 5 script ✅
- [x] PVID notation (u vs u*) fixed in Phase 2 script ✅

### Deployment
- [x] Flash/configure GL-MT6000 with router phases 1–8
- [x] Run router validation/tests from management IP (`test.ps1`: PASS=62/WARN=0/FAIL=0; `test-connectivity.ps1`: PASS=74/WARN=0/FAIL=0)
- [ ] Fill in MAC addresses in dhcp-config.conf (Proxmox host, VMs, NAS)
- [ ] Add the live valve-1 temporary plain-MQTT exception to `configs/openwrt/firewall-config.conf` in source, ordered before `Block IoT to Automation`
- [ ] Re-deploy/validate router config after the valve-1 firewall-source change so live state matches repo state again
- [ ] Configure WireGuard VPN clients (3 devices)
- [ ] Enable DDNS on router for dynamic WAN IP

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
- [ ] Remove the valve-1 temporary plain-MQTT firewall rule after `ventsys-main-valve-1` is confirmed working on TLS MQTT
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

- [ ] Purchase Raspberry Pi 4 (4GB+) and USB 3.0 storage drive(s)
- [ ] Follow `pi_nas_setup_guide.md` phases 1–6
- [ ] Configure NFS exports (Frigate, HA, configs shares)
- [ ] Keep Frigate "live" recordings on MINIX local storage first; add NAS archiving after the NAS is online
- [ ] Mount NAS in Frigate VM (`/mnt/nas/frigate`) and update docker-compose.yml volume
- [ ] Add NAS as HA network storage → verify backup writes successfully
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
- [ ] Stabilize embedded Grafana view inside HA (current issue: login loop / auth behavior)
- [ ] Revisit Grafana anonymous Viewer access after same-origin HTTPS path is in place
- [ ] Add Uptime Kuma dashboard view into Home Assistant after same-origin reverse proxy/HTTPS path exists
- [ ] Add Grafana dashboard view into Home Assistant (Lovelace panel/iframe) once auth/embedding behavior is stable
- [ ] Evaluate Telegraf UI integration path (direct Telegraf has no real UI; expose Influx/Grafana views in HA instead)
- [ ] Add an external health signal for monitoring VM (HA-side check) so Kuma-down is still detected
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
