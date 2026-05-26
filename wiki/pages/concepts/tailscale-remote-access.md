---
title: "Tailscale Remote Access"
category: concept
tags: [tailscale, vpn, remote-access, subnet-router]
created: 2026-05-23
updated: 2026-05-23
sources: [project-readme, project-todo]
status: active
---

# Tailscale Remote Access

## Definition

Tailscale is the project's daily remote-access layer. docker-host joins the
tailnet and advertises host routes only, not broad VLAN subnets.

## Relevance to This Project

Daily remote access should use docker-host's Tailscale node identity/MagicDNS
for docker-host services, plus two approved host routes:

- `192.168.20.101/32` for Home Assistant
- `192.168.40.50/32` for OMV

## Trade-offs / Considerations

- Simpler mobile access than maintaining WAN WireGuard endpoint changes.
- Requires persistent docker-host outbound connectivity.
- Does not replace OpenWrt firewall policy.
- Must not advertise Management, NVR, Printers, IoT, or broad Storage VLANs.

## Key Entities Using This Concept

- [[entities/docker-host]]
- [[entities/home-assistant]]
- [[entities/openmediavault-nas]]
- [[entities/gl-mt6000]]

## Sources

- Current canonical project decisions and reference docs in `main/docs/`.
