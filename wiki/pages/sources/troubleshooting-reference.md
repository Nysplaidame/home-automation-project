---
title: "Troubleshooting Reference"
category: source
tags: [troubleshooting, mqtt, home-assistant, frigate, proxmox, network, ventsys]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Troubleshooting Reference

**Original file:** `home-automation-safety/docs/troubleshooting/troubleshooting_reference.md`
**Date ingested:** 2026-04-07
**Type:** operational reference

## Summary

Cross-system quick-reference for the most common failure modes across all project subsystems. Covers MQTT/VentSys, Home Assistant, Frigate, Proxmox/VMs, Router/Network, WireGuard VPN, Bambuddy/P1S, and NAS. Each section provides specific shell commands for diagnosis and resolution steps.

## Key Takeaways

- **Post-TLS:** All MQTT commands use port 8883 with `--cafile /ssl/ca.crt`; pre-TLS was 1883
- **ESPHome offline:** Start with `ping 192.168.50.x`, then `nc -zv <ip> 6053` for native API port
- **HA restart loops:** Usually YAML syntax error in packages — check via Proxmox VM console
- **Frigate port:** 8971 for Frigate 0.14+; 5000 for older versions
- **Frigate MQTT rule:** Already exists in `firewall-config.conf`; don't add ad-hoc uci rules
- **VPN auth failures:** WireGuard is time-sensitive — wrong system clock will break handshakes
- **Bambuddy → P1S:** Requires Developer Mode enabled on printer + correct access code
- **DHCP conflicts:** Static reservations must use IPs below .100 for most VLANs
- **VentSys dashboard offline:** Check Long-Lived Token validity and HA at `http://192.168.20.101:8123`

## Entities Mentioned

[[entities/home-assistant]], [[entities/frigate]], [[entities/proxmox]], [[entities/gl-mt6000]], [[entities/mosquitto-mqtt]], [[entities/ventsys]], [[entities/esphome]], [[entities/bambuddy]], [[entities/bambu-p1s]], [[entities/openmediavault-nas]]

## Concepts Mentioned

[[concepts/mqtt-tls]], [[concepts/vlan-segmentation]], [[concepts/wireguard-vpn]]

## Contradictions / Updates

Some older commands reference port 1883; all should use 8883 post-TLS migration.
