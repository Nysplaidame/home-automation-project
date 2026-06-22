---
title: VentSys Main Inline Fan Firmware Pointer
description: Device identity and authoritative ESPHome firmware location
status: active
---

# VentSys Main Inline Fan Controller

- Device: `ventsys-main-fan`
- IP: `192.168.50.21`
- VLAN: `50`
- Authoritative firmware: `ventsys/ventsys_bundle_updated/ventsys_fan_controller.yaml`

The firmware uses `ventsys/fan/control` and `ventsys/fan/percent` for commands,
and publishes `ventsys/fan/state` and `ventsys/fan/percent_state`. Flash the
authoritative bundle file; this document is not an ESPHome configuration.

The canonical firmware uses MQTT TLS on port `8883`. Follow the ESPHome
adoption guide for serial first flash and certificate provisioning.
