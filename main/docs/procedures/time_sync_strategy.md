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

- **Time authority:** OpenWrt router-local NTP on each VLAN gateway
- **Home Assistant OS:** router-local NTP on Automation gateway `192.168.20.1`
- **ESPHome / VentSys boards:** Home Assistant time via native API, which is
  therefore router-derived when HAOS uses router NTP
- **Other restricted devices that need NTP:** router-local NTP
- **General Linux infrastructure:** router-local NTP on each host's local VLAN
  gateway

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

When HAOS uses router-local NTP, this chain is:

```text
OpenWrt router NTP on 192.168.20.1
  -> HAOS system time
  -> ESPHome native API time
  -> VentSys device clocks
```

That means ESPHome/VentSys devices are router-time-aligned without becoming
direct NTP clients.

### Home Assistant OS

Primary time source:

- router-local NTP on `192.168.20.1`

Configuration artifact:

- `configs/home-assistant/haos-timesyncd-router.conf`

Target on HAOS:

- `/etc/systemd/timesyncd.conf`

Apply using a Home Assistant OS `CONFIG` import or the HAOS host shell. This is
OS-level configuration; it does not belong in normal Home Assistant Core YAML
under `/config`.

### Other restricted devices

Primary time source:

- router NTP on UDP `123`

Why:

- simplest local source for devices that cannot use Home Assistant time
- keeps time sync inside the trust boundary
- supports TLS validation for devices that need accurate clocks

This is why the firewall contains router-input NTP rules for restricted VLANs
that need local time, including Automation, NVR, Monitoring, Storage, Printers,
and IoT Sensors.

### Infrastructure hosts

For Proxmox, docker-host, Frigate, and future NAS/monitoring hosts:

- Proxmox uses its normal host time sync.
- Debian VMs should prefer their local VLAN gateway as NTP.
- Current validated examples:
  - `docker-host` -> `192.168.20.1`
  - `frigate-nvr` -> `192.168.30.1`
  - `monitoring` -> `192.168.60.1`

That keeps internal infrastructure less dependent on direct external time queries.

## Current stage

### Already explicit in repo

- ESPHome boards are expected to use Home Assistant time
- router NTP server is enabled
- router NTP allowance exists for restricted VLANs that need it
- docker-host, Frigate, and monitoring have been validated against router-local NTP
- HAOS router-derived time now has a repo artifact at
  `configs/home-assistant/haos-timesyncd-router.conf`

### Still worth validating later

- apply and validate the HAOS router-NTP override on the live HA VM
- add NAS to the router-local NTP pattern when it is live
- document any exceptions for devices that insist on vendor/cloud time sync

## Practical rule

If a device can use Home Assistant time cleanly, prefer that.
If it cannot, prefer router-local NTP before allowing wider external time access.

For HA-managed ESPHome devices, prefer this wording:

> The router is the local NTP authority. HAOS syncs from the router, and
> ESPHome/VentSys devices sync from Home Assistant over the native API.
