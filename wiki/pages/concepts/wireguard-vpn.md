---
title: "WireGuard VPN"
category: concept
tags: [vpn, wireguard, remote-access, network, security]
created: 2026-04-07
updated: 2026-05-30
sources: [project-readme, network-architecture-decision, troubleshooting-reference]
status: active
---

# WireGuard VPN

## Definition

WireGuard is a lightweight VPN protocol built into the GL-MT6000/OpenWrt router.
In the current architecture it is a dormant fallback path, not the daily remote
access layer.

## Relevance to This Project

Daily remote access now uses [[concepts/tailscale-remote-access]] through
[[entities/docker-host]]. WireGuard remains useful if Tailscale is unavailable
or if router-level fallback access is needed.

## Key Properties

- Protocol: WireGuard
- Server: GL-MT6000, UDP port 51820
- Client IP range: `10.0.0.0/24`
- Split-tunnel only
- Allowed host routes include Home Assistant `192.168.20.101/32` and OMV `192.168.40.50/32`
- Broad Management, NVR, Printers, Storage, and IoT access stays blocked
- `wg0` is configured but disabled/down by default

## Firewall Rules

- `VPN to Home Assistant`: HA UI access
- `VPN to OMV NAS`: OMV host-only access
- `Block VPN to Storage`: still blocks broad VLAN 40 access after the OMV host exception

## Common Issues

- **Won't connect:** Check port 51820 UDP reachable from WAN; check router listener.
- **Connects but can't reach HA:** Confirm `AllowedIPs` includes `192.168.20.101/32`.
- **Connects but can't reach OMV:** Confirm `AllowedIPs` includes `192.168.40.50/32`, not the whole storage VLAN.
- **WAN IP changed:** Update client config endpoint or use DDNS if fallback endpoint churn matters.
- **Handshake fails:** WireGuard is time-sensitive; sync system clock if timestamps are skewed.

## Governance

Activate WireGuard only when Tailscale is unavailable for expected operator
tasks, a deliberate policy/account change freezes Tailscale use, or a planned
resilience drill has explicit start/end times. Record activation and
deactivation in the current handoff.

## Key Entities Using This Concept

- [[entities/gl-mt6000]]
- [[entities/home-assistant]]
- [[entities/openmediavault-nas]]

## Sources

- [[sources/network-architecture-decision]]
- [[sources/troubleshooting-reference]]
