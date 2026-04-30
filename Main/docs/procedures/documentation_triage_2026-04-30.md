# Documentation Triage (2026-04-30)

Purpose: keep deployment docs safe by separating canonical deployables from templates/reference material.

## Canonical VentSys Deployable Map

| Function | Canonical file | Canonical device/IP |
|---|---|---|
| SLA print valve controller | `Main/configs/esphome/ventsys_sla_print_valve.yaml` | `ventsys-sla-print-valve` / `192.168.50.56` |
| FDM enclosure sensor board | `Main/configs/esphome/ventsys_fdm_sensor.yaml` | `ventsys-fdm-sensor` / `192.168.50.31` |
| SLA enclosure sensor board | `Main/configs/esphome/ventsys_sla_sensor.yaml` | `ventsys-sla-sensor` / `192.168.50.32` |
| Booth sensor board | `Main/configs/esphome/ventsys_booth_sensor.yaml` | `ventsys-booth-sensor` / `192.168.50.33` |
| Main inline fan | `Main/configs/esphome/ventsys_main_fan.yaml` | `ventsys-main-fan` / `192.168.50.21` |

Notes:
- `printairpipe-controller.yaml` is a shared base include, not a primary per-device deploy target.
- `Main/ventsys/ventsys_bundle_updated/*.yaml` files are treated as reference templates unless explicitly promoted.

## Archived (2026-04-30)

Moved after inbound-link cleanup:

1. `Main/_archive/20-04-30/ventsys/integration-process/ventsys_complete_implementation_plan.md`
2. `Main/_archive/20-04-30/ventsys/integration-process/ventsys_technical_specifications.md`
3. `Main/_archive/20-04-30/ventsys/integration-process/ventsys_tls_implementation_guide.md`

Reason:
- These retain useful design context, but include template-era guidance that can conflict with canonical deploy paths.

## Keep As Active

1. `Main/scripts/setup/ventsys/esphome_adoption_guide.md`
2. `Main/docs/diagrams/wiring-diagrams/ventsys_wiring_reference.md`
3. `Main/configs/esphome/*.yaml` (per-device wrappers and canonical deployables)
4. `Main/configs/openwrt/*.conf`

## Added Documentation

1. Preflight safety checklist for unattended printing:
   - `Main/docs/procedures/unattended_print_preflight_checklist.md`

## Remaining Missing Documentation

1. Optional machine-readable validation runbook:
   - single command sequence for `ha core check`, MQTT topic checks, and backup scope verification
