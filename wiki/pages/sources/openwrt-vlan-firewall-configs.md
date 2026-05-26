---
title: "OpenWrt VLAN + Firewall Configs"
category: source
tags: [openwrt, vlan, firewall, network, config]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: OpenWrt VLAN + Firewall Configs

**Original files:** `configs/openwrt/vlan-config.conf` + `configs/openwrt/firewall-config.conf`
**Date ingested:** 2026-04-07
**Type:** configuration files

## Summary

The complete OpenWrt network and firewall configuration for the GL-MT6000. `vlan-config.conf` defines the DSA bridge, all 9 VLAN interfaces, WireGuard, and physical port assignments. `firewall-config.conf` (a bash script using `uci`) defines all zones and rules — internet access policies, inter-VLAN rules, Bambuddy rules, guest/DMZ isolation, logging, and security hardening.

## Key Takeaways — VLAN Config

- **lan5 documented fully:** serves as recovery port during setup, then TP-Link AP (VLAN 1 untagged only)
- **WireGuard:** single `wg0` interface only — a former duplicate `vpn` static interface has been removed. Firewall zone `vpn_clients` references `wg0` directly (B6/B7 fix)
- **VLAN 50 device allocation documented inline:** fans .21–.22, sensors .31–.34, airflow .41–.43, valves .51–.56, 360° .61–.62, plugs .71–.78, reserved .79–.89

## Key Takeaways — Firewall Config

- **VPN clients are BLOCKED from:** Management, CCTV, Storage, and IoT VLANs — only LAN, DMZ, and HA port 8123 are accessible via VPN
- **IoT mesh rule REMOVED:** VLAN 50 → VLAN 50 L3 routing was explicitly deleted as a security risk (lateral movement if any sensor is compromised). WiFi client isolation also prevents L2 direct comms.
- **LAN → HA rule added:** VLAN 1 devices (laptops, Raspberry Pi displays at .201/.202) need port 8123 to reach HA dashboard; explicit rule added
- **ESPHome OTA port 3232:** both 6053 (native API) AND 3232 (OTA) must be open VLAN 20→VLAN 50 — without 3232, OTA pushes silently hang (FIX #6)
- **IoT NTP:** firewall uses `dest='local'` (not `dest='wan'`) — router answers NTP itself, query never leaves the router
- **SSH to router:** WAN SSH removed; accessible only from management zone + VPN clients
- **Emergency smart plug rule:** covers .71–.78 (/29 subnet), ports 80/443/9999 (Tapo local API). Not added by default — run manually when needed
- **Monitoring → Management rule:** explicitly added (was missing) for SNMP/Prometheus/SSH from Grafana/Zabbix to Proxmox at 192.168.10.10
- **Two-stage MQTT:** instructions for temporary port 1883 rule (Stage 1) and how to remove it after TLS migration are embedded in the config as comments
- **Bambuddy rules must appear BEFORE Block CCTV to Automation** — ordering matters in iptables

## Entities Mentioned

[[entities/gl-mt6000]], [[entities/home-assistant]], [[entities/ventsys]], [[entities/frigate]], [[entities/bambuddy]], [[entities/proxmox]], [[entities/openmediavault-nas]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/wireguard-vpn]], [[concepts/mqtt-tls]]

## Contradictions / Updates

VPN zone previously referenced `network='vpn'` (a stale static interface). Now correctly references `network='wg0'`. All VPN firewall rules were silently dead before this fix (B7).
