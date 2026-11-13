---
title: Command Location Legend
description: Exact meaning of each Run on label used by the installation suite
tags: [install, commands, reference]
created: 2026-05-24
modified: 2026-08-09
type: reference
status: active
---

# Command Location Legend

| Label | Where it runs | How to recognize it |
|---|---|---|
| Admin laptop | Your local workstation on a trusted network | PowerShell/Windows Terminal or browser; the step says explicitly when elevation is required |
| OpenWrt router over SSH | GL-MT6000 router | SSH prompt for `root@192.168.10.1` after management VLAN is live |
| OpenWrt LuCI | Router web UI | Browser at `http://192.168.10.1/` or the recovery IP during early setup |
| GL-MT6000 firmware/recovery UI | Router-local stock or recovery interface | Laptop directly on `lan5`; use only the exact verified image and the vendor-supported local workflow |
| Proxmox host shell | MINISFORUM M1 Pro-125H Proxmox host | Shell as `root` on `192.168.10.10` or Proxmox web shell |
| Proxmox local console | Keyboard/display or out-of-band console that does not depend on the network being changed | Required during bridge/VLAN rollback and unsafe to substitute with SSH |
| Home Assistant UI | HAOS VM 100 | Browser at `https://192.168.20.101:8123/` with `Home Local CA` trusted |
| Home Assistant Terminal & SSH app | HAOS Terminal & SSH app | Shell prompt inside HA, usually with `/config` available; not the Proxmox host shell |
| Home Assistant Companion App | Approved phone/tablet app | UI-only onboarding, notification and sensor permission steps; no shell |
| ESPHome Device Builder UI | Home Assistant ESPHome app | Browser dashboard for compile/install/adoption/logs; USB first flash may still run on the named laptop/Pi shell |
| Frigate CT over SSH | Debian LXC 111 | SSH prompt on `192.168.30.20` |
| Frigate CT console | Proxmox console attached to CT 111 | Recovery prompt independent of Frigate network reachability |
| docker-host over SSH | Debian VM 103 | SSH prompt on `192.168.20.102` |
| docker-host local console | Proxmox console attached to VM 103 | Recovery prompt used before/while changing UFW, Docker, or Tailscale |
| llm-host over SSH | Debian LXC 114 | SSH prompt on `192.168.20.104` |
| llm-host local console | Proxmox console attached to CT 114 | Recovery prompt used while changing DRM/firewall/runtime state |
| OMV web UI | OpenMediaVault NAS | Browser at `http://192.168.40.50/` or `http://omv.home.local/` |
| OMV shell | OMV NAS shell | SSH prompt on `192.168.40.50` if enabled |
| Tailscale admin console | Tailscale web admin | Browser session at Tailscale admin UI |
| Approved Tailscale client | Named enrolled laptop/phone whose identity is allowed by tailnet ACLs | `tailscale status` plus protocol tests from the client; do not substitute a LAN client |
| Guest/DMZ or intentionally unapproved client | Test device connected to the exact denied source network/identity | Must retain public connectivity while internal protocol tests fail, preventing false-pass results |
| Managed-switch UI | Switch's Management VLAN address | UI-only PVID/tagged/untagged membership changes while a local recovery path remains open |
| Service first-run UI | Browser from an explicitly approved source | Account creation and bounded owner configuration for the named service; passwords are typed here, not into docs/commands |
| Unpowered physical bench | Labelled device, meter and disconnected supply | UI/shell-free inspection, continuity and wiring checks before energising hardware |
| Current-limited low-voltage bench | Device under controlled first power | Physical observation and measured voltage/current; disconnect immediately at a Phase 11 stop condition |

If a guide tells you to run a command but you cannot identify the matching prompt,
stop and fix the location problem before running anything.
