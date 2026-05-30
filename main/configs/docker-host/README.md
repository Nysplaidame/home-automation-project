---
title: Docker Host Config Templates
description: Rebuildable source templates for VM 103 docker-host stacks and host firewall
tags: [docker-host, compose, firewall, templates]
created: 2026-05-27
modified: 2026-05-28
type: config-reference
status: active
---

# Docker Host Config Templates

These files mirror the intended live layout on VM 103 (`docker-host`,
`192.168.20.102`). They are safe rebuild templates, not a secret backup.

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
| Docker-host Telegraf metrics | `/opt/stacks/telegraf` | `stacks/telegraf/` |
| Docker host firewall | `/usr/local/sbin/docker-host-firewall.sh` | `system/docker-host-firewall.sh` |
| Docker host UFW routed DNS rules | `/usr/local/sbin/docker-host-ufw-route-dns.sh` | `system/docker-host-ufw-route-dns.sh` |
| Docker host Fail2ban SSH jail | `/etc/fail2ban/jail.d/docker-host-sshd.local` | `system/docker-host-fail2ban-sshd.local` |

Do not commit live `.env` files, app databases, generated auth databases,
AdGuard password hashes, SearXNG secrets, or Immich database credentials.
