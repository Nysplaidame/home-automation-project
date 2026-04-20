---
title: Project Tasks
description: Implementation tasks by phase — updated March 2026
tags: [tasks, implementation]
aliases: [TODO, Tasks]
created: 2025-09-15
modified: 2026-03-07
type: task-list
status: active
---

# Project Task List

**Links:** [[README|Overview]] | [[PROJECT-INDEX|Index]]

---

## Immediate next actions (unblocked right now)

- [ ] Deploy GL-MT6000 router — run `router_setup_complete.md` phases 1–8
- [ ] After router live: run `network_testing_guide.md` full pass/fail checklist
- [ ] Install Proxmox on MINIX, run `proxmox_setup_guide.md`
- [ ] Run `configs/proxmox/vm-setup.sh` to create VMs 100 and 101
- [ ] Note MAC addresses for both VMs → update `configs/openwrt/dhcp-config.conf`
- [ ] Deploy HA via `ha_vm_setup_guide.md`; copy VentSys packages + dashboard
- [ ] Deploy Frigate VM via `frigate_vm_setup_guide.md`

---

## Phase 1 — Network ✅ Configs complete / ⏳ Deployment pending

### Configuration (all complete)
- [x] 9-VLAN architecture designed ✅
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
- [ ] Flash/configure GL-MT6000 with router phases 1–8
- [ ] Run network_testing_guide.md — all 14 pass/fail criteria
- [ ] Fill in MAC addresses in dhcp-config.conf (Proxmox host, VMs, NAS)
- [ ] Configure WireGuard VPN clients (3 devices)
- [ ] Enable DDNS on router for dynamic WAN IP

---

## Phase 2 — Core infrastructure ⏳

### Proxmox
- [ ] Install Proxmox VE on MINIX
- [ ] Configure vmbr0 VLAN-aware bridge, trunk on enp1s0
- [ ] Set static IP 192.168.10.10 on vmbr0.10
- [ ] Enable IOMMU (intel_iommu=on) for iGPU passthrough
- [ ] Run `configs/proxmox/vm-setup.sh`
- [ ] Configure Proxmox daily backup (Datacenter → Backup, 02:00, VMs 100+101)

### Home Assistant VM (VM 100)
- [ ] Start VM 100, complete HAOS onboarding wizard
- [ ] Set static IP 192.168.20.101 via nmcli
- [ ] Install add-ons: Mosquitto, File Editor, Terminal, ESPHome
- [ ] Configure MQTT integration (localhost:1883)
- [ ] Copy `ventsys_ha_package.yaml`, `ventsys_ha_scripts.yaml`, `ventsys_ha_optional.yaml` to `/config/packages/`
- [ ] Copy `ventilation_v9k.html` to `/config/www/ventsys-dashboard.html`
- [ ] Generate Long-Lived Token → paste into `HA_CONFIG.token` in dashboard
- [ ] Confirm dashboard shows ◉ HA LIVE
- [ ] Enable HA 2FA (TOTP)
- [ ] Configure NAS as backup target, set daily 03:00 schedule (14 keep)

### Frigate VM (VM 101)
- [ ] Install Debian 12 (hostname: frigate-nvr, SSH only)
- [ ] Set static IP 192.168.30.20 via nmcli
- [ ] Note MAC → add to dhcp-config.conf
- [ ] Install Docker (official repo)
- [ ] Deploy `configs/frigate/config.yml` to `/opt/frigate/config/`
- [ ] Create `/opt/frigate/.env` with FRIGATE_RTSP_PASSWORD, FRIGATE_MQTT_PASSWORD, BAMBU_PRINTER_IP, BAMBU_ACCESS_CODE, BAMBU_SERIAL (HA_LONG_LIVED_TOKEN optional — can configure Bambuddy HA connection via web UI instead)
- [ ] Create host dirs: `mkdir -p /opt/frigate/{db,bambuddy/data,bambuddy/logs}`
- [ ] Start Frigate + Bambuddy: `docker compose up -d`
- [ ] Confirm Frigate UI at http://192.168.30.20:8971 (Frigate 0.14+) or :5000 (<0.14)  # A9-4 fix
- [ ] Confirm Bambuddy UI at http://192.168.30.20:8000
- [ ] Add Frigate integration in HA
- [ ] Copy `configs/home-assistant/bambuddy_p1s_package.yaml` to `/config/packages/` on HA
- [ ] Replace `<P1S_SERIAL>` placeholder in bambuddy_p1s_package.yaml with real serial
- [ ] Confirm `binary_sensor.p1s_printing` and print state entities appear in HA
- [ ] Enable iGPU passthrough (Phase 6 of frigate_vm_setup_guide.md) — after confirming IOMMU

---

## Phase 3 — VentSys fire safety ⏳ Hardware pending

### Hardware procurement
- [ ] 2× ESP32-DevKitC (sensor boards — enc-fdm, enc-sla)
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
- [ ] Adopt all devices in ESPHome add-on (17 ESP32 boards + plugs)  # A5-3: was 'all 4 devices' - pre-expansion count
- [ ] Verify MQTT topics publishing: `mosquitto_sub -t 'ventsys/#' -v`
- [ ] Confirm automations fire on test sensor triggers
- [ ] Test emergency power cutoff sequence end-to-end

---

## Phase 4 — Storage ⏳

- [ ] Purchase Raspberry Pi 4 (4GB+) and USB 3.0 storage drive(s)
- [ ] Follow `pi_nas_setup_guide.md` phases 1–6
- [ ] Configure NFS exports (Frigate, HA, configs shares)
- [ ] Mount NAS in Frigate VM (`/mnt/nas/frigate`) and update docker-compose.yml volume
- [ ] Add NAS as HA network storage → verify backup writes successfully
- [ ] Configure robocopy or rsync scheduled task for vault backup to NAS
- [ ] Enable SMART monitoring on NAS drives

---

## Phase 5 — CCTV ⏳

- [ ] Select PoE IP camera models (H.265, RTSP, compatible with Frigate)
- [ ] Purchase 4× cameras and PoE switch
- [ ] Mount cameras, run CAT6 to PoE switch on VLAN 30
- [ ] Assign static IPs: cameras at 192.168.30.21–24 (MAC reservations in dhcp-config.conf)
- [ ] Update RTSP paths in `configs/frigate/config.yml` (currently placeholder `/stream1`)
- [ ] Restart Frigate, confirm all 4 camera streams visible in UI
- [ ] Test person detection notifications in HA

---

## Phase 6 — Security hardening

- [ ] Set up MQTT TLS (8883) — follow `ventsys_tls_implementation_guide.md`
- [ ] Remove temporary 1883 firewall rule after TLS confirmed working
- [ ] Enable HTTPS on HA — follow `ssl_tls_guide.md` (choose Option A/B/C)
- [ ] Configure Fail2ban on Frigate VM
- [ ] Set up WireGuard DDNS if ISP IP changes frequently
- [ ] Run `health_check.sh --watch` and confirm all green before signing off

---

## Ongoing / maintenance

- [ ] Monthly: run backup health checklist (`backup_strategy.md`)
- [ ] Monthly: check SMART status on NAS drives
- [ ] After any config change: `git add -A && git commit && git push`
- [ ] When hardware arrives: update MAC addresses in `dhcp-config.conf`
- [ ] When cameras confirmed: update RTSP URLs in `configs/frigate/config.yml`
- [ ] When sensors connected: update DS18B20 addresses in ESPHome YAML
