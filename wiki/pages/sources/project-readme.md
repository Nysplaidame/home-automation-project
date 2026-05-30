---
title: "Project README - Home Automation Safety Vault"
category: source
tags: [project-overview, hardware, status, deployment]
created: 2026-04-07
updated: 2026-05-30
status: stable
---

# Source: Project README - Home Automation Safety Vault

**Original file:** `main/README.md`
**Date ingested:** 2026-04-07; refreshed after documentation consolidation on 2026-05-25; audited against May 30 docs on 2026-05-30
**Type:** project overview doc

## Summary

Home automation system focused on fire safety and ventilation for 3D printing
operations, layered with NVR monitoring, a 10-segment OpenWrt network, Proxmox
virtualisation, Home Assistant, docker-host services, monitoring dashboards,
and planned OMV-backed storage. Canonical docs now use the fresh rebuild manual
under `main/docs/install/`; old prompt-era dashboards and sub-project prompts
have been removed.

## Key Takeaways

- Primary compute: [[entities/minix-neo-z350]] - Proxmox host
- Router: [[entities/gl-mt6000]] - owned and first-flight deployed
- [[entities/home-assistant]] runs on Proxmox VM 100 at 192.168.20.101
- [[entities/frigate]] has a live VM shell on VM 101, but the Frigate app remains unbuilt for regular use
- [[entities/docker-host]] runs on VM 103 at 192.168.20.102 and hosts Bambuddy, Tier 1 app pre-flight services, ntfy, Watchtower monitor-only, Tailscale, Telegraf, and Fail2ban
- [[entities/monitoring-vm]] runs architecture dashboards and exporters for Proxmox, docker-host, Uptime Kuma, DNS, and security posture
- [[entities/openmediavault-nas]] remains planned at 192.168.40.50
- Daily remote access is [[concepts/tailscale-remote-access]] through docker-host host routes
- [[concepts/wireguard-vpn]] remains a dormant fallback

## Entities Mentioned

[[entities/minix-neo-z350]], [[entities/gl-mt6000]], [[entities/home-assistant]],
[[entities/proxmox]], [[entities/frigate]], [[entities/docker-host]],
[[entities/bambuddy]], [[entities/bambu-p1s]], [[entities/ventsys]],
[[entities/openmediavault-nas]], [[entities/esphome]], [[entities/mosquitto-mqtt]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/ventsys-architecture]],
[[concepts/printairpipe]], [[concepts/tailscale-remote-access]],
[[concepts/wireguard-vpn]]

## Contradictions / Updates

Old dashboard/prompt files referenced 4-VLAN or 9-VLAN planning states. They
were deleted in the May 2026 documentation consolidation; current canonical docs
use the 10-segment architecture, OMV NAS, AdGuard Home, Tailscale host routes,
docker-host app tiers, direct-link monitoring posture, and Grafana/Kuma
embedding parked behind a future same-origin HTTPS path.
