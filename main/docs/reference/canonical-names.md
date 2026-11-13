---
title: Canonical Names
description: Authoritative names and identifiers for physical devices, compute guests, and live services
tags: [reference, naming, inventory, services]
created: 2026-07-10
modified: 2026-08-25
type: reference
status: active
---

# Canonical Names

Use these names in diagrams, documentation, labels, dashboards, and monitoring.
They are identifiers, not a request to rename working hostnames or DNS records.
The service matrix remains the authority for ports, URLs, access, and backups.

## Physical Devices

| Canonical name | Device | Network identity |
|---|---|---|
| `router` | GL.iNet GL-MT6000 OpenWrt router | `router.home.local`; VLAN gateways `.1` |
| `proxmox` | MINISFORUM M1 Pro-125H mini PC | `proxmox.home.local`; `192.168.10.10` |
| `gs1900-switch` | Zyxel GS1900-8HP managed PoE switch | `192.168.10.12` |
| `omvnas` | OpenMediaVault NAS hardware | `omv-nas.home.local`; `192.168.40.50` |
| `cam-01-annke-c500` | ANNKE C500 camera 1 | `192.168.30.21`; GS1900 port 2 |
| `cam-02-gate-annke-c500` | ANNKE C500 gate camera | `192.168.30.22`; GS1900 port 4 |
| `cam-03-patio-annke-c500` | ANNKE C500 patio camera | `192.168.30.23`; GS1900 port 3 |
| `p1s` | Bambu Lab P1S printer | `192.168.35.200`; HomePrinters Wi-Fi |
| `operator-mobile` | Operator OnePlus Android mobile device | Tailscale client `100.105.216.6`; fixed Homepage proxy grant |
| `household-admin-workstation` | Canonical admin workstation | Tailscale client `100.95.209.14`; tailnet service/SSH grant still pending |

## Proxmox Guests

| Canonical name | Guest ID | Type | Address | State |
|---|---:|---|---|---|
| `home-assistant` | 100 | VM | `192.168.20.101` | Live |
| `monitoring` | 102 | VM | `192.168.60.10` | Live |
| `docker-host` | 103 | VM | `192.168.20.102` | Live |
| `frigate-nvr` | 111 | unprivileged LXC | `192.168.30.20` | Live |
| `llm-host` | 114 | unprivileged LXC | `192.168.20.104` | Live |
| `frigate-nvr-rollback` | 101 | VM | none | Powered off rollback only |
| `llm-host-rollback` | 104 | VM | none | Powered off rollback only |

## Network identifiers

| Scope | Identifier | Notes |
|---|---|---|
| VLAN 50 OpenWrt internals | `iot_sensors` | UCI interface, DHCP scope, firewall zone, Wi-Fi attachment, and nft-chain name |
| VLAN 50 public Wi-Fi | `HomeIoT` | 2.4 GHz SSID; do not rename when changing internal UCI identifiers |

## Live Services

Use the exact service names in [service-matrix.md](service-matrix.md):
`OpenWrt router`, `Proxmox`, `Home Assistant`, `Frigate`, `Monitoring stack`,
`Docker host`, `Local AI inference`, `OMV NAS`, `OMV Transfer Portal`,
`Tailscale`, `AdGuard Home`, `Immich`, `Homepage`, `Dozzle`, `Mermaid Viewer`,
`Bambuddy`, `ntfy`, `Mealie`, `Grocy`, `Obsidian LiveSync`, `GardenKeeper`,
`Household Hub`, `Gridfinity Layout Tool`, `Recomp Tracker`, `Jellyfin`,
`Calibre-Web`, `Atsumeru`, `Vaultwarden`, `Mullvad download gateway +
qBittorrent`, `SearXNG`, `Whoogle`, `Watchtower monitor-only`,
`apt-cacher-ng`, and `Docker-host Telegraf`.

Use `Open WebUI` for the web application on `llm-host`, not `OpenWebUI`.
