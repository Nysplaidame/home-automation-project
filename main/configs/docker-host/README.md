---
title: Docker Host Config Templates
description: Rebuildable source templates for VM 103 docker-host stacks, host firewall, and app-data backup
tags: [docker-host, compose, firewall, backup, templates]
created: 2026-05-27
modified: 2026-07-26
type: config-reference
status: active
---

# Docker Host Config Templates

These files mirror the intended live layout on VM 103 (`docker-host`,
`192.168.20.102`). They are safe rebuild templates, not a secret backup.

VM 103 is also the expected target for future containerized AI-adjacent query
apps. Do not add a future query app template until its app-specific API,
storage, egress, monitoring, and firewall rules are approved. Local LLM, STT,
and TTS inference belongs on CT 114 `llm-host`, not here.

Live stack paths:

| Service | Live path | Template path |
|---|---|---|
| Homepage | `/opt/stacks/homepage` | `stacks/homepage/` |
| Dozzle | `/opt/stacks/dozzle` | `stacks/dozzle/` |
| AdGuard Home | `/opt/stacks/adguard-home` | `stacks/adguard-home/` |
| Immich | `/opt/stacks/immich` | `stacks/immich/` |
| ntfy | `/opt/stacks/ntfy` | `stacks/ntfy/` |
| Watchtower monitor-only | `/opt/stacks/watchtower` | `stacks/watchtower/` |
| SearXNG | `/opt/stacks/searxng` | `stacks/searxng/` |
| Whoogle | `/opt/stacks/whoogle` | `stacks/whoogle/` |
| Mealie | `/opt/stacks/mealie` | `stacks/mealie/` |
| Grocy | `/opt/stacks/grocy` | `stacks/grocy/` |
| Obsidian LiveSync | `/opt/stacks/obsidian-livesync` | `stacks/obsidian-livesync/` |
| Household Hub | `/opt/stacks/household-hub` | app repository deployment source |
| Mermaid Viewer | `/opt/stacks/mermaid-viewer` | `../../apps/mermaid-viewer/` |
| Gridfinity Layout Tool | `/opt/stacks/gridfinity-layout-tool` | `stacks/gridfinity-layout-tool/` |
| Docker-host Telegraf metrics | `/opt/stacks/telegraf` | `stacks/telegraf/` |
| GardenKeeper | `/opt/stacks/gardenkeeper` | `stacks/gardenkeeper/` |
| Jellyfin | `/opt/stacks/jellyfin` | `stacks/jellyfin/` |
| Calibre-Web | `/opt/stacks/calibre-web` | `stacks/calibre-web/` |
| Atsumeru | `/opt/stacks/atsumeru` | `stacks/atsumeru/` |
| Mullvad download gateway + qBittorrent | `/opt/stacks/download-gateway` | `stacks/download-gateway/` |
| Vaultwarden | `/opt/stacks/vaultwarden` | `stacks/vaultwarden/` |
| Docker host firewall | `/usr/local/sbin/docker-host-firewall.sh` | `system/docker-host-firewall.sh` |
| AdGuard/Tailscale boot gate | `/etc/systemd/system/adguard-home-compose.service` | `system/adguard-home-compose.service` |
| Docker host UFW routed DNS rules | `/usr/local/sbin/docker-host-ufw-route-dns.sh` | `system/docker-host-ufw-route-dns.sh` |
| Docker host UFW routed monitoring rules | `/usr/local/sbin/docker-host-ufw-route-monitoring-tailscale.sh` | `system/docker-host-ufw-route-monitoring-tailscale.sh` |
| Docker host Homepage preview UFW rules | `/usr/local/sbin/docker-host-ufw-homepage-previews.sh` | `system/docker-host-ufw-homepage-previews.sh` |
| Docker host Fail2ban SSH jail | `/etc/fail2ban/jail.d/docker-host-sshd.local` | `system/docker-host-fail2ban-sshd.local` |
| Docker host app-data backup script | `/usr/local/sbin/docker-host-app-data-backup.sh` | `system/docker-host-app-data-backup.sh` |
| Docker host app-data backup service | `/etc/systemd/system/docker-host-app-data-backup.service` | `system/docker-host-app-data-backup.service` |
| Docker host app-data backup timer | `/etc/systemd/system/docker-host-app-data-backup.timer` | `system/docker-host-app-data-backup.timer` |

The app-data backup templates target OMV `backups/docker-host` after the live
NFS mount `/mnt/omv/docker-host-backups` is installed. They are not live
evidence by themselves; prove the mount, dry-run, first backup, and restore
smoke before marking household app backups complete.

Do not commit live `.env` files, app databases, generated auth databases,
AdGuard password hashes, SearXNG secrets, or Immich database credentials.
