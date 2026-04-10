# Home Automation Safety Project — Deep Dive Analysis Report

**Generated**: 2026-03-09  
**Scope**: Full project audit — all config files, setup guides, cross-system references  
**Status**: COMPLETE — pending fixes

---

## How to read this report

Each finding has:
- A sequential **ID** (F-01, F-02, …)
- A **severity** rating: 🔴 Critical / 🟡 Moderate / 🟢 Minor
- The **file(s)** affected
- The **issue** and **recommended fix**

Severity definitions:
- 🔴 **Critical** — deployment blocker, silent failure, or safety/security gap
- 🟡 **Moderate** — validation failure, incomplete coverage, inconsistency that causes misbehaviour
- 🟢 **Minor** — documentation quality, cosmetic, or low-risk inconsistency

---

## SEGMENT 1 — OpenWrt Config Files

### F-01 🔴 `dhcp-config.conf` — Only 2 of 4 VentSys controllers in static reservations

The static DHCP reservation section of `dhcp-config.conf` only includes:
- `ventsys-fan-controller` (192.168.50.21)
- `ventsys-valve-controller` (192.168.50.56)

Missing:
- `ventsys-fdm-valve` (192.168.50.83)
- `ventsys-booth-valve` (192.168.50.84)

Phase 3 setup guide (already fixed) and Phase 8 docs correctly reference all 4 boards, but the actual deployed config file only has 2. On first boot, boards .83 and .84 will receive random DHCP addresses from the .100–190 pool and the ESPHome static IP fallback in firmware (`manual_ip`) will conflict.

**Fix**: Add the two missing host entries to `dhcp-config.conf`.

---

### F-02 🟡 `dhcp-config.conf` — IoT sensor comment misnames VentSys boards

The comment in the IoT scope block reads:  
`"Valve Controller (.82), Servos (.83-.89)"`

The correct naming is: `.81` = fan-controller, `.82` = sla-valve, `.83` = fdm-valve, `.84` = booth-valve. The comment implies .83–.89 are servo boards, which is wrong and will mislead anyone reading it.

**Fix**: Replace the inline comment to reflect the 4 named ESP32 boards.

---

### F-03 🟢 `dhcp-config.conf` — Architecture summary table missing VLAN 60 and VLAN 70

The markdown table at the top of the file lists 7 VLANs but omits VLAN 60 (Monitoring) and VLAN 70 (DMZ), both of which have DHCP scopes configured in the same file.

**Fix**: Add both rows to the summary table.

---

### F-04 🟡 `wireless-config.conf` — Channel allocation strategy section is stale and contradictory

The `CHANNEL ALLOCATION STRATEGY` comment block at the bottom of the file describes a three-channel 2.4GHz plan (channel 1 for HomeMain, channel 6 for HomeIoT, channel 11 for HomeAdmin-2G and HomeGuest). This contradicts the radio0-level setting of `channel '6'` and the mac80211 single-channel architecture note already documented at the top of the file.

Additionally, the per-interface annotations on `main_2g` ("Channel 1 provides maximum separation from IoT"), `admin_2g` ("Channel 11 provides separation"), and `guest_2g` ("Channel 11 provides separation") are all factually wrong — all 2.4GHz SSIDs share channel 6.

**Fix**: Remove or rewrite the CHANNEL ALLOCATION STRATEGY section to reflect the single-channel reality. Remove the per-interface channel annotations that reference channel 1 and channel 11.

---

### F-05 🟡 `wireless-config.conf` — Redundant per-interface `option channel` entries silently ignored

`iot_2g` has `option channel '6'` set at the interface level (a no-op in mac80211). `main_5g` and `admin_5g` both have `option channel 'auto'`. These entries are silently ignored but create the false impression that per-interface channel control is possible.

**Fix**: Remove all per-interface `option channel` entries from wifi-iface blocks.

---

### F-06 🟡 `firewall-config.conf` — `Allow DHCP Requests` and `Allow Local DNS` use `src='*'` including WAN

Both rules use `src='*'` which includes the WAN zone. `Allow DHCP Requests` (port 67/68 UDP) is L2-broadcast based and won't normally arrive from WAN, but `Allow Local DNS` (port 53 TCP/UDP) with `src='*'` could permit DNS queries originating from the WAN to reach the router's dnsmasq — a potential DNS amplification surface.

**Fix**: Change `src='*'` to a list of explicit internal zones, or use a macro/set approach. At minimum restrict `Allow Local DNS` to internal zones only.

---

### F-07 🟡 `firewall-config.conf` — SSH exposed to WAN from `SSH Rate Limit` rule

The rule `SSH Rate Limit` ALLOWs SSH (port 22) from `src='wan'` with only rate limiting as protection. Remote access is managed via WireGuard VPN — exposing SSH directly to the internet is unnecessary attack surface. If the router's Dropbear SSH is breached, an attacker has root on the device that controls all VLAN routing.

**Fix**: Remove the `SSH Rate Limit` WAN rule. Add a new rule allowing SSH from `vpn_clients` zone only (or from the `management` zone for LAN admin access). Keep the rate-limit approach if WAN SSH is ever intentionally re-enabled.

---

### F-08 🟡 `vlan-config.conf` — Dual WireGuard interface config is non-standard

The file defines `config interface 'wg0'` with `proto='wireguard'` AND a second `config interface 'vpn'` with `proto='static'` pointing to `device='wg0'`. This is redundant — OpenWrt VPN zone references should point to the wireguard interface directly. The static `vpn` interface may cause routing or firewall zone mapping conflicts.

**Fix**: Remove the duplicate `vpn` static interface. Reference `wg0` directly in the firewall zone: `uci add_list firewall.@zone[-1].network='wg0'`.

---

## SEGMENT 2 — Proxmox / VM Configs

### F-09 🟡 `vm-setup.sh` / `proxmox_setup_guide.md` — No iGPU passthrough automation; performance risk for Frigate

Frigate is configured with CPU-only inference (`type: cpu, num_threads: 2`). The i3-N350 has an integrated Intel UHD GPU capable of VA-API hardware acceleration. Without iGPU passthrough, 4× 1080p/5fps detection streams will heavily load the CPU — likely saturating it. The vm-setup.sh comment says "see frigate_vm_setup_guide.md Phase 6" but Phase 6 iGPU passthrough is explicitly deferred without a timeline.

**Fix**: Flag in the vm-setup.sh and frigate_vm_setup_guide.md that iGPU passthrough should be configured as a priority immediately after Frigate first boots, not as an optional later step. Add IOMMU verification to vm-setup.sh.

---

### F-10 🟡 `proxmox_setup_guide.md` — IOMMU comment says "for USB passthrough" only

Phase C IOMMU setup describes `intel_iommu=on iommu=pt` as "needed for USB passthrough to VMs (e.g. Zigbee dongle)." It omits the equally important use case of iGPU passthrough for Frigate hardware acceleration.

**Fix**: Update the comment to mention both iGPU passthrough and USB device passthrough.

---

### F-11 🟡 `proxmox_setup_guide.md` — HAOS version hardcoded as 14.2

`HA_VERSION="14.2"` in Phase D. Current HAOS version as of early 2026 is well beyond 14.2. While the guide says "check github releases for latest", the hardcoded variable encourages copy-paste deployment without updating, which will result in deploying an outdated HAOS image.

**Fix**: Remove the hardcoded version and replace with instructions to fetch the latest version string from the GitHub releases API: `curl -s https://api.github.com/repos/home-assistant/operating-system/releases/latest | grep '"tag_name"' | cut -d'"' -f4`

---

### F-12 🟡 `proxmox_setup_guide.md` vs `vm-setup.sh` — VM 101 (Frigate) coverage gap

The Proxmox guide only creates VM 100 (HA). VM 101 is deferred to `frigate_vm_setup_guide.md`. However, `vm-setup.sh` creates both VMs in one script. A deployer following the guide may not realize the script also handles VM 101. The two paths (manual guide vs script) can diverge on disk sizes, EFI configuration, etc.

**Fix**: Add a note to `proxmox_setup_guide.md` stating that `vm-setup.sh` creates both VMs and should be used instead of manual creation for consistency.

---

### F-13 🟡 `proxmox_setup_guide.md` — Backup storage is 'local'

The backup schedule in Phase E uses storage `local`. On a default Proxmox install, `local` uses the same pool as ISO images and snippets. VM backups for HAOS can be several gigabytes each; 3 backups × ~3GB = ~9GB minimum. The 512GB SSD provides ample total space, but the storage pool usage should be explicitly planned.

**Fix**: Clarify that the 512GB SSD is used for both VMs (96GB total: 32GB HA + 64GB Frigate) and backups, and confirm that `local` has sufficient headroom.

---

## SEGMENT 3 — Home Assistant Configs

### F-14 🔴 `bambuddy_p1s_package.yaml` — `<P1S_SERIAL>` placeholder in 12 MQTT topic references

All sensor `state_topic` values, all binary sensor `state_topic` values, and all 5 automation MQTT triggers use `<P1S_SERIAL>` literally. HA will subscribe to topics like `bambuddy/printers/<P1S_SERIAL>/status` which Bambuddy will never publish to. Every P1S sensor will show "unavailable" and every print event automation will never fire.

**Fix**: Replace `<P1S_SERIAL>` with the actual P1S serial number (e.g. `01P09C411500579`) throughout the file before deploying to HA.

---

### F-15 🟡 `bambuddy_p1s_package.yaml` — `script.ventsys_mode_fdm_purge` called before VentSys is deployed

The `p1s_print_failed` automation calls `script.ventsys_mode_fdm_purge`. If VentSys hardware hasn't been purchased/wired/flashed yet, this script doesn't exist and HA will throw a "service not found" error when triggered by a print failure. The VentSys scripts are not flagged as a prerequisite anywhere in the Bambuddy setup guide.

**Fix**: Add `continue_on_error: true` to the `script.turn_on` action, or add a condition checking `script.ventsys_mode_fdm_purge` exists before calling it. Add a note in the deployment checklist that the Bambuddy package should be deployed after VentSys scripts are loaded.

---

### F-16 🟡 `configuration.yaml` — Brute-force protection disabled

`ip_ban_enabled: true` and `login_attempts_threshold: 5` are commented out in the `http:` block. Once HA has an external URL and is accessible via VPN/internet, any exposed HA login page is a brute-force target. These should be enabled pre-go-live.

**Fix**: Uncomment `ip_ban_enabled: true` and `login_attempts_threshold: 5` before opening HA to external access.

---

## SEGMENT 4 — Frigate & Bambuddy Configs

### F-17 🔴 `configs/frigate/config.yml` — RTSP stream paths `/stream1` are placeholders for all 4 cameras

Every camera entry uses `/stream1` in the RTSP URL. Different camera manufacturers use completely different stream paths (e.g. Hikvision: `/Streaming/Channels/101`, Dahua: `/cam/realmonitor?...`, Reolink: `/h264Preview_01_main`). Frigate will fail to connect to all cameras on deployment.

**Fix**: This is a known pending action (cameras not yet selected). The deployment checklist must include: look up manufacturer RTSP URL format → update all 4 paths in `config.yml`.

---

### F-18 🟡 `configs/frigate/config.yml` — CPU-only detection; performance risk for 4-camera 1080p system

All Frigate detection uses `type: cpu, num_threads: 2`. Object detection at 1080p/5fps for 4 simultaneous streams is computationally expensive. On an i3-N350 with 2 cores allocated to this VM, CPU utilisation will likely be very high and may cause dropped frames or detection lag. Both VA-API (iGPU, via passthrough) and Coral USB TPU paths are commented out.

**Fix**: Prioritise iGPU passthrough setup (Phase 6 of frigate guide) immediately after Frigate first starts. Add a warning note about this constraint to the deployment checklist.

---

### F-19 🟡 `configs/frigate/docker-compose.yml` — Bambuddy uses `image:latest`, Frigate uses `image:stable` (no version pinning)

Neither service image is pinned to a specific version. Unexpected upstream image changes could break functionality silently on container restart after a pull.

**Fix**: After first deployment, pin both images to the versions confirmed working (e.g. `ghcr.io/blakeblackshear/frigate:0.14.1`, `ghcr.io/maziggy/bambuddy:v1.x.x`). Update intentionally after testing.

---

### F-20 🟡 `configs/frigate/config.yml` + `docker-compose.yml` — MQTT on port 1883 (pre-TLS); will need updating post-TLS migration

Both Frigate's `config.yml` and Bambuddy's `docker-compose.yml` `MQTT_PORT=1883` are the pre-TLS defaults. When MQTT TLS migration happens (Phase 6), all three need to be updated simultaneously: Frigate config, Bambuddy env var, and the temp-1883 firewall rule removal. There is no single checklist that ties all three together.

**Fix**: Create a TLS migration checklist that explicitly lists all files/services requiring port change from 1883 to 8883.

---

## SEGMENT 5 — ESPHome / VentSys Configs

### F-21 🔴 Major hardware/software architecture mismatch — VentSys software assumes 8+ ESP32 boards; hardware plan has 4

This is the most significant systemic discrepancy in the project. The software layer (HA package, HA scripts, dashboard, Node-RED flows) is designed for a **10-endpoint** VentSys system:
- 2 fans (inline + spray booth)
- 9 controllable valve positions (FDM branch, FDM print valve, FDM 360 intake, SLA branch, SLA print valve, SLA 360 intake, Main valve 1, Main valve 2, Booth valve)

The hardware design only has **4 ESP32 boards**:
- `.81`: fan controller (inline fan only)
- `.82`: SLA valve (SLA print valve only)
- `.83`: FDM valve (FDM print valve only)
- `.84`: booth valve (booth valve only)

The `ventsys_valve_controller.yaml` FIX #12 comment explicitly acknowledges 7 additional ESPHome YAML files are needed but haven't been created. None of the extended topics (FDM branch, FDM 360, SLA branch, SLA 360, main valves 1/2, spray fan) have corresponding ESP32 firmware.

At deployment, the HA scripts will publish MQTT commands to topics that no device subscribes to. The Purge/Seal modes will appear to execute but most physical valves won't move.

**Fix**: Make an architectural decision: either (a) purchase 4+ additional ESP32 boards and create the 7 missing ESPHome YAML files to fulfil the full 10-endpoint design, or (b) simplify the HA package and scripts to match the 4-board hardware reality. This decision affects hardware budget, wiring, and the VentSys phase guides.

---

### F-22 🔴 All ESPHome firmwares require MQTT TLS before they can be tested

`ventsys_fan_controller.yaml`, `ventsys_valve_controller.yaml`, and `printairpipe-controller.yaml` all configure MQTT with `port: 8883` and `ca_certificate: !secret mqtt_ca_cert`. TLS setup requires a working HA + Mosquitto with a local CA — a Phase 6 activity that happens long after hardware is purchased and flashed.

When you first flash an ESP32 board and try to test it (the natural workflow), it will fail to connect to the MQTT broker because:
1. The `mqtt_ca_cert` secret doesn't exist yet
2. Mosquitto isn't yet configured for TLS

**Fix**: Create pre-TLS variants of each ESPHome YAML (e.g. `ventsys_fan_controller_pretls.yaml`) that use `port: 1883` and no `ca_certificate`. Use these for initial hardware testing; switch to the TLS version when Phase 6 is complete. Document this in the VentSys hardware deployment guide.

---

### F-23 🟡 ESPHome device names don't match DHCP hostnames

| ESPHome `name` | DHCP `option name` | mDNS hostname |
|---|---|---|
| `ventsys-fan-ctrl` | `ventsys-fan-controller` | `ventsys-fan-ctrl.local` |
| `ventsys-valve-ctrl` | `ventsys-sla-valve` | `ventsys-valve-ctrl.local` |

The mDNS hostname (from ESPHome `name`) won't match the DHCP hostname — querying `ventsys-fan-controller.local` won't resolve. This can complicate troubleshooting and ESPHome adoption via hostname.

**Fix**: Either update ESPHome `name` fields to match DHCP names, or update DHCP option names to match ESPHome names. Recommend: align on the more descriptive ESPHome names.

---

### F-24 🟡 `printairpipe-controller.yaml` — Humidity data published but never consumed by HA

The firmware publishes to `${mqtt_topic_prefix}/humidity` (e.g. `ventsys/fdm/humidity`) on every BME680 reading. No MQTT sensor entity subscribing to this topic exists in `ventsys_ha_package.yaml` or `ventsys_ha_optional.yaml`. The humidity data is lost.

**Fix**: Add humidity sensors to `ventsys_ha_package.yaml`:
```yaml
- platform: mqtt
  name: FDM Humidity
  unique_id: ventsys_fdm_humidity
  state_topic: "ventsys/fdm/humidity"
  unit_of_measurement: "%"
  device_class: humidity
```
(and equivalent for SLA)

---

### F-25 🟡 `printairpipe-controller.yaml` — DS18B20 address is placeholder `0x0000000000000000`

The 1-Wire device address must be read from the ESP32 logs after first flash. With the placeholder address, the temperature sensor entity will show "unavailable" in HA. This is documented implicitly in comments but not flagged as a deployment blocker in the adoption guide.

**Fix**: Add explicit step to `esphome_adoption_guide.md`: "After first flash, check ESPHome device logs for 'Found Dallas device with address', then replace `0x0000000000000000` with the actual address in the YAML and reflash."

---

### F-26 🟡 `dhcp-config.conf` — No static DHCP reservations for PrintAirPipe sensor boards

`printairpipe-controller.yaml` assigns static IPs 192.168.50.31 (FDM sensors) and 192.168.50.32 (SLA sensors) via `manual_ip`. However, no corresponding DHCP host entries exist in `dhcp-config.conf`. While `manual_ip` in ESPHome provides a belt-and-braces fallback, the devices won't resolve by hostname via dnsmasq and won't appear in the DHCP lease table.

**Fix**: Add DHCP host entries for `enc-fdm-sensors` (.31) and `enc-sla-sensors` (.32) to `dhcp-config.conf`.

---

### F-27 🟡 `ventsys_ha_package.yaml` — Temperature sensor `unit_of_measurement: "C"` is non-standard

Standard HA unit is `"°C"` (with degree symbol). Using bare `"C"` may work in some HA versions but won't match the `temperature` device class expected unit and may affect the Energy dashboard and statistics.

**Fix**: Change `unit_of_measurement: "C"` to `unit_of_measurement: "°C"` on both FDM and SLA temperature sensors.

---

### F-28 🟡 `ventsys_ha_package.yaml` — `FIRE_RISK` risk state has no publisher

Three sensors (`sensor.sla_risk`, `sensor.fdm_risk`, `sensor.booth_risk`) subscribe to `ventsys/{enc}/risk/state` and the `ventsys_fire_risk_cutoff` automation fires when any reaches `"FIRE_RISK"`. However, nothing in any ESPHome YAML, Node-RED flow, or HA script publishes to these risk state topics. The fire risk cutoff automation can never trigger via this path.

The `automations.yaml` fire detection automation (`fire_detection_emergency`) does trigger on `sensor.fdm_smoke → "detected"` which IS published by printairpipe-controller.yaml. But the risk state pathway is a dead end.

**Fix**: Either implement the risk state publisher (in Node-RED or as an HA template sensor that derives FIRE_RISK from multiple sensor thresholds), or remove the `ventsys_fire_risk_cutoff` automation and `ventsys_failsafe_on_sync` automation and rely entirely on the `fire_detection_emergency` automation in automations.yaml.

---

### F-29 🟡 `automations.yaml` — MQTT broker watchdog targets wrong entity ID

The `mqtt_reconnect_alert` automation triggers on `binary_sensor.mqtt_broker_online`. The sensor in `ventsys_ha_package.yaml` is named `"MQTT Broker"` with `unique_id: ventsys_mqtt_broker`. HA generates entity_id `binary_sensor.mqtt_broker` from the friendly name — NOT `binary_sensor.mqtt_broker_online`. The watchdog trigger will never fire.

**Fix**: Either rename the sensor to `"MQTT Broker Online"` (→ entity_id `binary_sensor.mqtt_broker_online`) to match the automation, or update the automation to reference `binary_sensor.mqtt_broker`.

---

### F-30 🟡 `automations.yaml` — Only 2 of 4+ ESPHome device offline monitors configured

System health monitors `binary_sensor.ventsys_fan_controller_status` (.81) and `binary_sensor.ventsys_valve_controller_status` (.82). No offline monitors exist for .83 (FDM valve), .84 (booth valve), or the sensor boards (.31, .32). A failed sensor board would go unnoticed until a safety event fails to trigger.

**Fix**: Add offline monitoring automations for all deployed ESP32 boards. This is especially important for the sensor boards which are part of the fire detection chain.

---

### F-31 🟡 `ventsys_ha_scripts.yaml` — `ventsys_mode_booth` doesn't close FDM/SLA paths

The booth mode script opens main valves 1 and 2 and turns on both fans, but doesn't explicitly close FDM and SLA valve paths. If those paths are partially open from a previous mode, spray fumes could cross-contaminate into the FDM/SLA enclosures.

**Fix**: Add explicit close commands for FDM and SLA paths at the start of `ventsys_mode_booth`:
```yaml
- action: mqtt.publish
  data: { topic: "ventsys/fdm/branch/control", payload: "0" }
- action: mqtt.publish
  data: { topic: "ventsys/sla/branch/control", payload: "0" }
```

---

## SEGMENT 6 — Setup Guides

### F-32 🟡 `ventsys_phase1_foundation.md` — References sensor IPs .31–.33 but only 2 sensor boards defined

Section 1.2 says "sensors .31-.33" but `printairpipe-controller.yaml` only defines 2 sensor boards: .31 (FDM) and .32 (SLA). A third board at .33 is implied but not documented anywhere — no ESPHome YAML, no DHCP entry, no wiring diagram.

**Fix**: If there is a third sensor enclosure (e.g. spray booth), create the ESPHome YAML and add DHCP entry. If not, update the guide to say .31–.32 only.

---

### F-33 🟡 `proxmox_setup_guide.md` — Subscription nag removal requires re-application after toolkit upgrades

Phase C includes a `sed` command to disable the Proxmox subscription popup. This is overwritten on every `proxmox-widget-toolkit` package upgrade. The guide notes this, but there's no automation or reminder mechanism.

**Fix**: Accept as a known maintenance task, or use a community Ansible role/hook that re-applies the patch post-upgrade.

---

## SEGMENT 7 — Cross-System Analysis

### F-34 🔴 MQTT TLS migration has no unified checklist

When transitioning from port 1883 (pre-TLS) to 8883 (TLS), the following items all need updating simultaneously:
1. Frigate `config.yml` → add `tls_ca_cert`, `tls_client_cert`, `tls_client_key`, change port to 8883
2. Bambuddy `docker-compose.yml` `MQTT_PORT=1883` → 8883
3. ESPHome firmwares (all boards) → already set to 8883, but `ca_certificate` secret must be populated
4. HA MQTT integration → change port in Settings → Integrations → MQTT
5. Temporary firewall rules (port 1883) → remove from router
6. `firewall-config.conf` → remove TEMP rules (if they were UCI-committed)

Missing any of these will cause partial connectivity failures that are difficult to diagnose. No single document brings them together.

**Fix**: Create a `mqtt_tls_migration_checklist.md` that lists all 6 items, or add a dedicated section to `ventsys_tls_implementation_guide.md` with a numbered pre-migration and post-migration checklist.

---

### F-35 🟡 Smart plug entity IDs assumed (`switch.fdm_printer_plug`, `switch.sla_printer_plug`)

Four safety-critical automations (`fire_detection_emergency`, `high_temp_fdm_critical`, `high_temp_sla_critical`, `ventsys_fire_risk_cutoff`) call `switch.turn_off` on `switch.fdm_printer_plug` and `switch.sla_printer_plug`. These entity IDs are assumed. The actual IDs depend on which smart plug brand/integration is used and what they're named in HA.

If the entity IDs are wrong at deployment, emergency power cutoff silently fails with no error (HA `switch.turn_off` on a non-existent entity logs at warning level but doesn't halt the automation).

**Fix**: Add a verification step to the VentSys deployment checklist: "Plug in smart plugs, confirm entity IDs in HA, update all 4 automations with actual IDs." Consider adding a startup-time check or helper alert for misconfigured entity IDs.

---

### F-36 🟡 Frigate integration port should be verified against installed Frigate version

`configuration.yaml` comment references Frigate at `http://192.168.30.20:5000`. Frigate's API has been on port 5000 for recent versions but this should be confirmed against the actual installed version via `frigate_vm_setup_guide.md`.

**Fix**: Minor — confirm port 5000 in the Frigate deployment step and document it in the HA integration setup checklist.

---

### F-37 🟡 HA `secrets.yaml` requirements not consolidated in one place

Different config files (configuration.yaml, each ESPHome YAML, bambuddy_p1s_package.yaml, ventsys_ha_package.yaml) each document their own `secrets.yaml` requirements in comments, but there is no master `secrets_reference.md` listing ALL required secrets across the full system. A deployer populating `secrets.yaml` will need to cross-reference multiple files.

Required secrets span:
- HA: `home_latitude/longitude/elevation`, `external_url`, `mqtt_username`, `mqtt_password`
- ESPHome: `wifi_ssid`, `wifi_pass`, `mqtt_user`, `mqtt_pass`, `mqtt_ca_cert`, `api_key`, `ota_password`
- Bambuddy: (env vars in .env, not secrets.yaml)

**Fix**: Create a `secrets_reference.md` in `docs/procedures/` listing every secret key, which file uses it, and an example value format.

---

### F-38 🟡 No monitoring strategy for VLAN 60 services

VLAN 60 (Monitoring) has DHCP scope, firewall rules, and management access fully configured, but no setup guide, VM, or service deployment planned. The `vlan-config.conf` comment mentions Zabbix, Grafana, ELK, and network scanner at .10–.13. Nothing in the current project scope addresses when or how these will be deployed.

**Fix**: Either add a VLAN 60 setup guide to the roadmap, or explicitly document that VLAN 60 is "reserved for future use" and set its firewall posture to block-all until intentionally deployed.

---

### F-39 🟢 Stale/duplicate files in router setup folder

- `router_setup_complete - Copy.md` exists alongside `router_setup_complete.md`
- `openwrt_complete_config_phase_2.md` and `openwrt_script_analysis.md` appear to be working documents that predate the current phase-based structure

**Fix**: Delete or archive `router_setup_complete - Copy.md`. Review `openwrt_complete_config_phase_2.md` and `openwrt_script_analysis.md` — if superseded by the phase files, archive or delete them to reduce confusion.

---

### F-40 🟢 Obsidian-flavored `[[wikilinks]]` in UCI config files

`vlan-config.conf` contains Obsidian `[[wikilinks]]` inside comment lines (e.g. `[[01-network-architecture|Network Architecture]]`). While comment syntax means these don't affect UCI parsing, they visually clutter the file and would confuse non-Obsidian tooling. Similarly, some config files begin with markdown headers (e.g. `dhcp-config.conf`).

**Fix**: Remove wikilinks from UCI config comments. Separate pure-UCI files from documentation wrapper files (e.g. use a `# Reference: see docs/...` comment instead of a wikilink).

---

## MASTER FINDINGS TABLE

| ID | Severity | File(s) | Summary |
|----|----------|---------|---------|
| F-01 | 🔴 | `dhcp-config.conf` | Only 2 of 4 VentSys controller DHCP reservations exist |
| F-02 | 🟡 | `dhcp-config.conf` | IoT comment misnames VentSys boards (.82–.89) |
| F-03 | 🟢 | `dhcp-config.conf` | Architecture table missing VLAN 60 and 70 |
| F-04 | 🟡 | `wireless-config.conf` | Channel strategy section contradicts single-channel mac80211 reality |
| F-05 | 🟡 | `wireless-config.conf` | Per-interface channel options silently ignored, misleading |
| F-06 | 🟡 | `firewall-config.conf` | DHCP/DNS rules use `src='*'` including WAN zone |
| F-07 | 🟡 | `firewall-config.conf` | SSH exposed to WAN — should require VPN |
| F-08 | 🟡 | `vlan-config.conf` | Redundant dual WireGuard interface definition |
| F-09 | 🟡 | `vm-setup.sh`, frigate guide | No iGPU passthrough; CPU-only detection is a performance risk |
| F-10 | 🟡 | `proxmox_setup_guide.md` | IOMMU comment only mentions USB passthrough, not iGPU |
| F-11 | 🟡 | `proxmox_setup_guide.md` | HAOS version hardcoded as 14.2; should be dynamically fetched |
| F-12 | 🟡 | `proxmox_setup_guide.md`, `vm-setup.sh` | VM 101 creation gap between guide and script |
| F-13 | 🟡 | `proxmox_setup_guide.md` | Backup storage 'local' — space planning needed |
| F-14 | 🔴 | `bambuddy_p1s_package.yaml` | `<P1S_SERIAL>` placeholder in 12 MQTT topics |
| F-15 | 🟡 | `bambuddy_p1s_package.yaml` | VentSys script called without checking it exists |
| F-16 | 🟡 | `configuration.yaml` | Brute-force protection commented out |
| F-17 | 🔴 | `frigate/config.yml` | RTSP `/stream1` placeholder on all 4 cameras |
| F-18 | 🟡 | `frigate/config.yml` | CPU-only detection; performance risk for 4x 1080p |
| F-19 | 🟡 | `frigate/docker-compose.yml` | No image version pinning on Frigate or Bambuddy |
| F-20 | 🟡 | `frigate/config.yml`, `docker-compose.yml` | MQTT port 1883 needs coordinated TLS migration |
| F-21 | 🔴 | VentSys (all files) | Software assumes 8+ ESP32 boards; hardware plan has 4 |
| F-22 | 🔴 | All ESPHome YAMLs | TLS required before hardware can be tested; blocks initial deployment |
| F-23 | 🟡 | ESPHome YAMLs, `dhcp-config.conf` | ESPHome device names don't match DHCP hostnames |
| F-24 | 🟡 | `printairpipe-controller.yaml`, HA package | Humidity data published but no HA sensor consumes it |
| F-25 | 🟡 | `printairpipe-controller.yaml` | DS18B20 placeholder address; adoption guide lacks clear step |
| F-26 | 🟡 | `dhcp-config.conf` | Sensor boards .31/.32 have no DHCP reservations |
| F-27 | 🟡 | `ventsys_ha_package.yaml` | Temperature `unit_of_measurement: "C"` should be `"°C"` |
| F-28 | 🟡 | `ventsys_ha_package.yaml`, `automations.yaml` | FIRE_RISK state topic has no publisher |
| F-29 | 🟡 | `automations.yaml` | MQTT broker watchdog targets wrong entity ID |
| F-30 | 🟡 | `automations.yaml` | Only 2 of 4+ ESPHome boards have offline monitoring |
| F-31 | 🟡 | `ventsys_ha_scripts.yaml` | Booth mode doesn't close FDM/SLA paths |
| F-32 | 🟡 | `ventsys_phase1_foundation.md` | References sensor .31–.33; only .31 and .32 defined |
| F-33 | 🟡 | `proxmox_setup_guide.md` | Subscription nag fix is overwritten on toolkit upgrades |
| F-34 | 🔴 | Multiple | No unified TLS migration checklist across all services |
| F-35 | 🟡 | `automations.yaml`, HA packages | Smart plug entity IDs assumed; critical automation failure risk |
| F-36 | 🟡 | `configuration.yaml` | Frigate API port 5000 should be confirmed against installed version |
| F-37 | 🟡 | Multiple | No master secrets reference document |
| F-38 | 🟡 | VLAN 60 | No monitoring service deployment plan |
| F-39 | 🟢 | Router setup folder | Stale/duplicate files present |
| F-40 | 🟢 | `vlan-config.conf`, `dhcp-config.conf` | Obsidian wikilinks in UCI config comments |

---

## Summary by severity

| Severity | Count |
|----------|-------|
| 🔴 Critical | 7 (F-01, F-14, F-17, F-21, F-22, F-34, + pre-existing router phase fixes now confirmed resolved) |
| 🟡 Moderate | 28 |
| 🟢 Minor | 3 |
| **Total** | **38** |

---

## Recommended fix priority order

**Do immediately (block deployment):**
1. F-21 — Resolve VentSys hardware/software architecture mismatch (4 boards vs 10-endpoint design)
2. F-22 — Create pre-TLS ESPHome variants for initial hardware testing
3. F-01 — Add .83 and .84 to `dhcp-config.conf` static reservations
4. F-34 — Create MQTT TLS migration checklist
5. F-14 — Replace `<P1S_SERIAL>` before deploying Bambuddy package

**Do before go-live:**
6. F-07 — Restrict SSH to VPN zone only
7. F-28 — Implement FIRE_RISK state publisher or remove dead automation path
8. F-29 — Fix MQTT broker watchdog entity ID
9. F-35 — Verify and hardcode smart plug entity IDs
10. F-17 — Update camera RTSP paths when cameras are selected
11. F-16 — Enable HA brute-force protection

**Do during hardware testing:**
12. F-25 — Scan and record DS18B20 addresses
13. F-23 — Align ESPHome device names with DHCP hostnames
14. F-26 — Add sensor board DHCP reservations (.31, .32)
15. F-15 — Add `continue_on_error` to Bambuddy VentSys script call

**Documentation / quality:**
16. F-04, F-05 — Fix wireless channel documentation
17. F-27 — Fix temperature unit of measurement
18. F-24 — Add humidity sensors to HA package
19. F-30 — Add offline monitoring for all ESP32 boards
20. F-37 — Create master secrets reference document
