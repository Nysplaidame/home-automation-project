---
title: Tailscale Remote Access Guide
description: Daily remote access through docker-host host routes, with WireGuard as fallback
tags: [tailscale, remote-access, docker-host, vpn]
created: 2026-05-23
modified: 2026-05-23
type: procedure
status: planned
---

# Tailscale Remote Access Guide

Tailscale is the daily remote-access layer. WireGuard on OpenWrt remains a
dormant fallback.

## Design

docker-host joins the tailnet and advertises host routes only:

```bash
tailscale up --advertise-routes=192.168.20.101/32,192.168.40.50/32
```

Routes must be approved in the Tailscale admin console before clients can use
them.

Do not advertise broad VLAN or RFC1918 ranges.

## Target access

| Target | Route |
|---|---|
| docker-host services | docker-host Tailscale node / MagicDNS name |
| Home Assistant | `192.168.20.101/32` routed through docker-host |
| OMV | `192.168.40.50/32` routed through docker-host |

## Deployment notes

1. Install Tailscale on docker-host.
2. Authenticate interactively or with a short-lived auth key stored outside the repo.
3. Enable IP forwarding on docker-host.
4. Start Tailscale with the two host routes.
5. Approve routes in the Tailscale admin console.
6. Add Tailscale ACLs matching `docs/reference/access-matrix.md`.
7. Update docker-host UFW to allow approved service ports on `tailscale0`.
8. Test from mobile data before depending on it.

## Docker-host firewall notes

Use interface-scoped or tailnet-scoped rules. Example intent:

```bash
ufw allow in on tailscale0 to any port 22 proto tcp comment "Tailscale SSH admin"
ufw allow in on tailscale0 to any port 8123 proto tcp comment "Routed HA"
ufw allow in on tailscale0 to any port 2283 proto tcp comment "Immich"
ufw allow in on tailscale0 to any port 3001 proto tcp comment "Homepage"
ufw allow in on tailscale0 to any port 8081 proto tcp comment "Dozzle"
```

Adjust before applying; routed HA/OMV traffic may need forwarding policy rather
than local input-only rules.

## Validation

From a Tailscale client off the home LAN:

```bash
tailscale status
ping 192.168.20.101
curl -I http://192.168.20.101:8123
ping 192.168.40.50
curl -I http://192.168.40.50/
```

Confirm blocked paths:

```bash
ping 192.168.10.10
ping 192.168.30.20
ping 192.168.35.200
ping 192.168.50.1
```

These should fail unless a future documented route/ACL explicitly allows them.

## Fallback

If Tailscale is unavailable, use the WireGuard fallback docs:

```text
scripts/setup/router/wireguard_vpn_guide.md
```

WireGuard should remain split-tunnel and host-route scoped for OMV.
