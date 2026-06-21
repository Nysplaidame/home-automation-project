---
title: Command Location Legend
description: Exact meaning of each Run on label used by the installation suite
tags: [install, commands, reference]
created: 2026-05-24
modified: 2026-05-24
type: reference
status: active
---

# Command Location Legend

| Label | Where it runs | How to recognize it |
|---|---|---|
| Admin laptop | Your local workstation on a trusted network | PowerShell, Windows Terminal, Linux shell, or browser |
| OpenWrt router over SSH | GL-MT6000 router | SSH prompt for `root@192.168.10.1` after management VLAN is live |
| OpenWrt LuCI | Router web UI | Browser at `http://192.168.10.1/` or the recovery IP during early setup |
| Proxmox host shell | MINISFORUM M1 Pro-125H Proxmox host | Shell as `root` on `192.168.10.10` or Proxmox web shell |
| Home Assistant UI | HAOS VM 100 | Browser at `http://192.168.20.101:8123/` |
| Home Assistant Terminal add-on | HAOS Terminal & SSH add-on | Shell prompt inside HA, usually `/config` available |
| Frigate CT over SSH | Debian LXC 111 | SSH prompt on `192.168.30.20` |
| docker-host over SSH | Debian VM 103 | SSH prompt on `192.168.20.102` |
| llm-host over SSH | Debian LXC 114 | SSH prompt on `192.168.20.104` |
| OMV web UI | OpenMediaVault NAS | Browser at `http://192.168.40.50/` or `http://omv.home.local/` |
| OMV shell | OMV NAS shell | SSH prompt on `192.168.40.50` if enabled |
| Tailscale admin console | Tailscale web admin | Browser session at Tailscale admin UI |

If a guide tells you to run a command but you cannot identify the matching prompt,
stop and fix the location problem before running anything.
