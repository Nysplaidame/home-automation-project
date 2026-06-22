# Unattended Print Preflight Checklist

Purpose: verify safety-critical dependencies before allowing unattended print jobs.

## 1) Home Assistant Config Health

1. Run HA config validation:
   - `ha core check`
2. Confirm automations are loaded without YAML errors:
   - `settings -> system -> logs` (or HA CLI logs)

## 2) Emergency Power-Cut Entities

1. Confirm both entities exist:
   - `switch.fdm_printer_plug`
   - `switch.sla_printer_plug`
2. Toggle each once from Developer Tools and verify real hardware power state changes.
3. If either entity is missing, unattended printing stays blocked.

## 3) VentSys Risk Signal Reality Check

1. Verify whether these topics are actually being published:
   - `ventsys/fdm/risk/state`
   - `ventsys/sla/risk/state`
   - `ventsys/booth/risk/state`
2. If not published yet, treat risk sensors as informational only and rely on direct smoke/temp automation triggers.

## 4) Canonical Firmware Mapping Confirmation

1. Confirm board-to-file mapping before flashing:
   - SLA print valve: `main/configs/esphome/ventsys_sla_print_valve.yaml`
   - FDM pipe air sensor: `main/configs/esphome/ventsys_fdm_pipe_air_sensor.yaml`
   - SLA pipe air sensor: `main/configs/esphome/ventsys_sla_pipe_air_sensor.yaml`
   - Garage air sensor: `main/configs/esphome/ventsys_garage_air_sensor.yaml`
   - FDM sensor arrays: `main/configs/esphome/ventsys_fdm_array_1.yaml`, `main/configs/esphome/ventsys_fdm_array_2.yaml`
   - SLA sensor arrays: `main/configs/esphome/ventsys_sla_array_1.yaml`, `main/configs/esphome/ventsys_sla_array_2.yaml`
   - Main inline fan firmware pointer: `main/configs/esphome/ventsys_main_fan.md`
   - Authoritative firmware: `main/ventsys/ventsys_bundle_updated/ventsys_fan_controller.yaml`
2. Confirm expected IP reservations match `main/configs/openwrt/dhcp-config.conf`.
3. Do not flash from template/reference docs in `main/ventsys/integration-process/`.

## 5) Bambuddy Readiness Gate

1. Replace all `<P1S_SERIAL>` placeholders in:
   - `main/configs/home-assistant/bambuddy_p1s_package.yaml`
2. Verify Bambuddy reachability:
   - `http://192.168.20.102:8000`
3. Verify MQTT publish path is working for printer status topics.

## 6) Backup and Recovery Gate

1. In Proxmox Datacenter backup job, confirm VM scope includes:
   - `100` (HA)
   - `101` (Frigate)
   - `103` (Bambuddy)
2. Confirm at least one successful backup run after latest config changes.

## 7) Final Go/No-Go

All gates above must be green before unattended print mode is allowed.
