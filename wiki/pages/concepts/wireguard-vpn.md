---
title: "WireGuard VPN"
category: concept
tags: [vpn, wireguard, remote-access, network, security]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, network-architecture-decision, troubleshooting-reference]
status: active
---

# WireGuard VPN

## Definition

WireGuard is a modern, lightweight VPN protocol built into the GL-MT6000 (OpenWrt). It provides secure remote access to Home Assistant and the management network from outside the home, without exposing HA directly to the internet.

## Relevance to This Project

The VPN is the only sanctioned external entry point into the home network. Instead of opening port 8123 on the WAN, remote access goes through WireGuard → VLAN 70 (DMZ) → firewall rule → VLAN 20 (HA). This keeps HA off the public internet entirely.

## Key Properties

- Protocol: WireGuard
- Server: GL-MT6000, VLAN 70 (DMZ), UDP port 51820
- Client IP range: `10.0.0.0/24`
- Access target: `192.168.20.101` (HA) via `HA → VPN to Home Assistant` firewall rule
- DNS: `192.168.1.1` (LAN gateway, reachable via tunnel) or `1.1.1.1` as fallback

## Firewall Rule Required

- `VPN to Home Assistant`: src 10.0.0.0/24 → dest 192.168.20.101 port 8123 (and 8883 post-TLS)

## Common Issues

- **Won't connect:** Check port 51820 UDP reachable from WAN; check `netstat -ulnp | grep 51820` on router
- **Connects but can't reach HA:** Confirm `AllowedIPs` in client config includes `192.168.20.101/32`
- **WAN IP changed:** Update client config `Endpoint` — use DDNS to avoid this
- **All traffic broken over VPN:** Usually DNS — temporarily switch client `DNS = 1.1.1.1` to diagnose
- **Handshake fails:** WireGuard is time-sensitive — sync system clock if timestamps are skewed

## Status

- Config: ✅ Written (`vlan-config.conf` includes WireGuard block, `phase_6_vpn_setup.md`)
- Deployment: ⏳ Pending router switchover
- Client setup: ⏳ 3 devices planned (see `wireguard_vpn_guide.md`)

## Key Entities Using This Concept

- [[entities/gl-mt6000]]
- [[entities/home-assistant]]

## Sources

- [[sources/network-architecture-decision]]
- [[sources/troubleshooting-reference]]
