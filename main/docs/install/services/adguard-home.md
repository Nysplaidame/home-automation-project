---
title: AdGuard Home Install Manual
description: Tier 1 docker-host DNS filtering service
tags: [install, docker-host, adguard, dns]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
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
      - "53:53/tcp"
      - "53:53/udp"
      - "3000:3000/tcp"
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

The first-run UI uses port 3000. After setup, the admin UI is mapped to 8080 so
port 80 on docker-host stays free for other future patterns.

## Expected result

AdGuard first-run UI loads at `http://192.168.20.102:3000/`, then admin UI at
`http://adguard.home.local:8080/`.

## Validation

Run on: Admin laptop.

```powershell
nslookup example.com 192.168.20.102
nslookup example.com 192.168.10.1
```

## Backup

Back up `/opt/stacks/adguard-home/conf` and `/opt/stacks/adguard-home/work`.

## Failure recovery

- If port 53 fails, run `ss -tulnp | grep ':53'` on docker-host.
- If household DNS breaks, router fallback should still resolve public DNS.
- If filtering is wrong, disable blocklists in AdGuard before changing router DNS.

## Completion checklist

- [ ] Compose config passes.
- [ ] DNS query to docker-host works.
- [ ] Router query works with AdGuard first.
- [ ] Admin password stored.
