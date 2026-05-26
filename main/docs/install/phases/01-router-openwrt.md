---
title: Phase 01 - Router OpenWrt
description: Fresh OpenWrt baseline, VLANs, DHCP, DNS, firewall, and WireGuard fallback
tags: [install, router, openwrt]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: active
---

# Phase 01 - Router OpenWrt

## Purpose

Build the GL-MT6000 network foundation: VLANs, DHCP reservations, local DNS,
firewall policy, router-local NTP, AdGuard-first DNS forwarding with
Quad9/Cloudflare fallback, and dormant WireGuard fallback.

Router-deploy remains router-only. It must not deploy containers, OMV packages,
Tailscale auth, or app stacks.

## Runs on

- OpenWrt router over SSH.
- Admin laptop for repository validation and deployment tooling.

## Prerequisites

- Phase 00 complete.
- Router reachable in recovery or management mode.
- `configs/openwrt/` reviewed, including `system-config.conf` for router-local NTP intent.
- Secrets ledger populated for router password, WiFi passwords, and WireGuard keys.

## Inputs

- `<ROUTER_ROOT_PASSWORD>`
- `<WIFI_MAIN_PASSWORD>`
- `<WIFI_IOT_PASSWORD>`
- `<WIFI_GUEST_PASSWORD>`
- `<WIREGUARD_SERVER_PRIVATE_KEY>`

## Commands

Run on: OpenWrt router over SSH.

```sh
opkg update
opkg install wireguard-tools qrencode tcpdump iperf3
wg --version
```

Run on: Admin laptop from repository root.

```powershell
cd main
python tools/router-deploy/lint.py
python tools/router-deploy/compile.py --profile first-flight
```

## Explanation

The router packages support fallback VPN and diagnostics. The router-deploy
checks prove the desired UCI/firewall artifacts compile before anything is
applied to a router.

## Expected result

- VLANs and DHCP scopes match `configs/openwrt/`.
- Clients receive the router as DNS.
- The router prefers AdGuard on docker-host, then public fallback.
- The router runs local NTP for restricted/internal VLANs.
- WireGuard exists but is treated as dormant fallback.

## Validation

Run on: Admin laptop.

```powershell
cd main
python tools/router-deploy/lint.py
python tools/router-deploy/compile.py --profile first-flight
```

Run on: OpenWrt router over SSH after deployment.

```sh
uci show network | grep -E 'vlan|interface'
uci show dhcp | grep -E 'server|domain|host'
uci show firewall | grep -E 'AdGuard|Tailscale|WireGuard|Storage'
uci show system.ntp
/etc/init.d/sysntpd status
```

## Failure recovery

- If management access is lost, use the documented recovery port/path in
  `scripts/setup/router/phase_1_prerequisites.md`.
- If DNS fails but routing works, check AdGuard reachability and fallback
  public DNS entries.
- If a firewall rule blocks a required path, do not broaden VLAN access; add the
  narrow host/port rule and rerun lint/compile.

## Completion checklist

- [ ] Router packages installed.
- [ ] Router-deploy lint passes.
- [ ] First-flight compile passes.
- [ ] Router reachable at `192.168.10.1`.
- [ ] Local hostnames resolve.
- [ ] Router-local NTP is enabled and `sysntpd` is running.
- [ ] WireGuard is configured but not the daily remote access layer.
