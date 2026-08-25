---
title: "Troubleshooting Reference"
category: source
tags: [troubleshooting, mqtt, home-assistant, frigate, proxmox, network, ventsys]
created: 2026-04-07
updated: 2026-08-25
status: stable
---

# Source: Troubleshooting Reference

**Original file:** `main/docs/troubleshooting/troubleshooting_reference.md`
**Date ingested:** 2026-04-07
**Type:** operational reference

## Summary

Cross-system quick-reference for current failure modes across MQTT/VentSys,
Home Assistant, Frigate, Proxmox, router/network, Tailscale/WireGuard,
docker-host services, Bambuddy/P1S and OMV. It now begins with an evidence-first
dependency workflow and distinguishes live paths from dated handoffs/audits.

## Key Takeaways

- **Post-TLS:** All MQTT commands use port 8883 with `--cafile /ssl/ca.crt`; pre-TLS was 1883
- **ESPHome offline:** Start with `ping 192.168.50.x`, then `nc -zv <ip> 6053` for native API port
- **HA restart loops:** Usually YAML syntax error in packages — check via Proxmox VM console
- **Frigate paths:** authenticated UI on `8971`; internal HA/monitoring API on
  `5000`, which remains denied through the remote host route
- **Frigate MQTT rule:** Already exists in `firewall-config.conf`; don't add ad-hoc uci rules
- **VPN auth failures:** WireGuard is time-sensitive — wrong system clock will break handshakes
- **Bambuddy → P1S:** Requires Developer Mode enabled on printer + correct access code
- **DHCP conflicts:** Static reservations must use IPs below .100 for most VLANs
- **VentSys dashboard offline:** Check token validity and native HA HTTPS at
  `https://192.168.20.101:8123`
- **Mobile Homepage:** check split DNS and the fixed `443`/`8180-8209` proxy
  grant before considering any broader route

## Entities Mentioned

[[entities/home-assistant]], [[entities/frigate]], [[entities/proxmox]], [[entities/gl-mt6000]], [[entities/mosquitto-mqtt]], [[entities/ventsys]], [[entities/esphome]], [[entities/bambuddy]], [[entities/bambu-p1s]], [[entities/openmediavault-nas]]

## Concepts Mentioned

[[concepts/mqtt-tls]], [[concepts/vlan-segmentation]], [[concepts/wireguard-vpn]]

## Contradictions / Updates

Historical source summaries and handoffs may still show HTTP HA, earlier camera
counts or earlier VM placement. The active reference uses HA HTTPS, CT 111/114,
three cameras, four Tailscale host routes and current OMV/Docker paths.
