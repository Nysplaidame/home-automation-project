---
title: AdGuard Home Install Manual
description: Tier 1 docker-host DNS filtering service
tags: [install, docker-host, adguard, dns]
created: 2026-05-24
modified: 2026-05-27
type: install-guide
status: preflight-live
---

# AdGuard Home Install Manual

## Purpose

Provide network-wide DNS filtering while keeping the router as DHCP, local DNS,
firewall, and fallback-DNS authority.

## Runs on

docker-host over SSH at `192.168.20.102`; admin UI from Management network.

## Prerequisites

- docker-host phase complete.
- Router DNS policy points to docker-host first and public fallback after.
- Port 53 is not already bound on docker-host.

## Inputs

- `<ADGUARD_ADMIN_PASSWORD>`

## Current live state

- Live at `/opt/stacks/adguard-home` on docker-host.
- DNS is bound to `192.168.20.102:53/tcp+udp` for router/monitoring queries and
  `100.94.122.18:53/tcp+udp` for identity-gated Tailscale split DNS.
- Admin UI: `http://adguard.home.local:8080/`.
- Uptime Kuma monitors `AdGuard DNS` and `AdGuard UI` are live.
- Router DNS prefers AdGuard first, with public fallback retained on the router.
- Tailscale split DNS sends only the `home.local` suffix to the tailnet listener.
  The live AdGuard config has an enabled rewrite for
  `homepage.home.local -> 100.94.122.18`; OpenWrt still answers the same name as
  `192.168.20.102` for clients on home WiFi.
- Admin password is stored on docker-host at `/root/adguard-home-admin-password.txt`; copy it to Bitwarden.
- Rebuildable Compose template: `configs/docker-host/stacks/adguard-home/`.

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/adguard-home/{work,conf}
cd /opt/stacks/adguard-home
cat > docker-compose.yml <<'COMPOSE'
services:
  adguard-home:
    image: adguard/adguardhome:latest
    container_name: adguard-home
    restart: unless-stopped
    ports:
      - "192.168.20.102:53:53/tcp"
      - "192.168.20.102:53:53/udp"
      - "8080:80/tcp"
    volumes:
      - ./work:/opt/adguardhome/work
      - ./conf:/opt/adguardhome/conf
COMPOSE
docker compose config
docker compose up -d
docker compose logs --tail=80
```

## Explanation

Bind DNS to `192.168.20.102:53`, not `0.0.0.0:53`, because Debian's local
resolver may already own loopback DNS. The first-run UI may temporarily use port
3000, but the steady-state admin UI is mapped to 8080 so port 80 on docker-host
stays free for other future patterns.

Docker-published ports can bypass UFW's normal `INPUT` path. The live host uses
`docker-host-firewall.service` / `DOCKER-USER` so only the router and monitoring
VM can query AdGuard DNS directly; ordinary clients should query router-local
DNS instead.

## Expected result

AdGuard admin UI loads at `http://adguard.home.local:8080/`.

## Validation

Run on: Admin laptop.

```powershell
nslookup example.com 192.168.10.1
Test-NetConnection 192.168.20.102 -Port 8080
```

Run direct `nslookup example.com 192.168.20.102` from the router or monitoring
VM, not from arbitrary clients, because direct client DNS bypass is intentionally
blocked.

## Backup

Back up `/opt/stacks/adguard-home/conf` and `/opt/stacks/adguard-home/work`.

## Failure recovery

- If port 53 fails, run `ss -tulnp | grep ':53'` on docker-host.
- If household DNS breaks, router fallback should still resolve public DNS.
- If filtering is wrong, disable blocklists in AdGuard before changing router DNS.

## Completion checklist

- [x] Compose config passes.
- [x] DNS query to docker-host works from router/monitoring.
- [x] Router query works with AdGuard first.
- [x] Admin password stored.
- [x] Uptime Kuma monitors added for DNS and UI.
