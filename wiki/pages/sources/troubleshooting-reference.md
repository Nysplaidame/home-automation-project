---
title: "Troubleshooting Reference"
category: source
tags: [troubleshooting, mqtt, home-assistant, frigate, proxmox, network, ventsys]
created: 2026-04-07
updated: 2026-09-11
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
- **DHCP conflicts:** Compare reservations with the actual subnet range;
  `.101`, `.102` and planned `.200` are legitimate project assignments.
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

## September 10 reconciliation

Canonical written troubleshooting now includes five offline walkthroughs with
Mermaid source links, execution hosts, expected results and evidence-age rules.
The app complements the manuals. Its freshness update is deployed, while the
installed Proxmox collector update and fresh backup/mount proof remain open.
See [[entities/troubleshooting-dashboard]].

Recovery uses LAN5 or HomeAdmin; LAN2 belongs to Hive/cloud IoT VLAN55. OMV is
directly on LAN4 and Proxmox on the LAN1 trunk. The three cameras remain
deliberately disconnected and P1S uncommissioned in the recorded baseline.
The media operating manual now distinguishes application backups from library
content, stopped checkpoints from raw live copies, and restart from restore
proof. Remaining legacy-command and complete-rebuild verification is explicit
in the canonical installation checklist.

## September 10 second documentation pass

The canonical manuals now include download-gateway and Recomp lifecycle
procedures, expanded MediaMTX recovery, and explicit Household Hub source/
database-backup gaps. The troubleshooting reference removes public dashboard
token and password-in-command advice, distinguishes ping/listener/transport
failures, and names shell contexts. VM103/VM102 creation and pre-NAS return
checkpoints are explicit; validation is source-only, not live rebuild proof.

## September 11 service lifecycle review

Canonical ntfy, Watchtower, SearXNG and Whoogle manuals now cover update,
backup, isolated restore and rollback with Mermaid links. The SearXNG effective
settings/template recovery gap remains open. Watchtower's error40014 and phone
notification acceptance are unresolved; documented procedures are not live
restore proof. See [[project-todo]] for the remaining source/backup dependencies.
