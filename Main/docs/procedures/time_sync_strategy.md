---
title: Time Sync Strategy
description: Intended time sources for infrastructure, Home Assistant, and restricted devices
tags: [ntp, time-sync, home-assistant, router, esphome]
created: 2026-05-08
type: procedure
status: active
---

# Time Sync Strategy

## Summary

The project does **not** use one single time source for every device class.
The intended model is:

- **ESPHome / VentSys boards:** Home Assistant time via native API
- **Other restricted devices that need NTP:** router-local NTP
- **General Linux infrastructure:** normal OS time sync, preferably against the
  router once a local-first pattern is validated

This matches the current repo intent and keeps restricted devices simple.

## Device-class intent

### VentSys ESPHome boards

Primary time source:

- `time: platform: homeassistant`

Why:

- they already depend on Home Assistant
- no direct internet access is required
- no separate NTP client configuration is needed in the normal case

This is why DHCP option 42 is intentionally absent for VLAN 50 in
`configs/openwrt/dhcp-config.conf`.

### Other restricted devices

Primary time source:

- router NTP on UDP `123`

Why:

- simplest local source for devices that cannot use Home Assistant time
- keeps time sync inside the trust boundary
- supports TLS validation for devices that need accurate clocks

This is why the firewall contains the `IoT to Router NTP` rule.

### Infrastructure hosts

For Proxmox, docker-host, Frigate, and future NAS/monitoring hosts:

- short term: existing OS time sync is acceptable
- preferred direction: document and validate a local-first pattern using the router as the internal reference point

That keeps internal infrastructure less dependent on direct external time queries.

## Current stage

### Already explicit in repo

- ESPHome boards are expected to use Home Assistant time
- router NTP allowance exists for restricted devices that need it

### Still worth validating later

- confirm OpenWrt local NTP service behavior end-to-end
- decide whether all Linux hosts should explicitly prefer router time
- document any exceptions for devices that insist on vendor/cloud time sync

## Practical rule

If a device can use Home Assistant time cleanly, prefer that.
If it cannot, prefer router-local NTP before allowing wider external time access.
