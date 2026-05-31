---
title: Tailscale Remote Access Guide
description: Daily remote access through docker-host host routes, with WireGuard as fallback
tags: [tailscale, remote-access, docker-host, vpn]
created: 2026-05-23
modified: 2026-05-31
type: procedure
status: active
---

# Tailscale Remote Access Guide

Tailscale is the daily remote-access layer. WireGuard on OpenWrt remains a
dormant fallback.

## Design

docker-host joins the tailnet and advertises host routes only:

```bash
tailscale up --advertise-routes=192.168.20.101/32,192.168.40.50/32,192.168.60.10/32
```

Routes must be approved in the Tailscale admin console before clients can use
them.

Do not advertise broad VLAN or RFC1918 ranges.

Live state, 2026-05-28:

- Tailscale `1.98.3` is installed on docker-host.
- `tailscaled` is active.
- docker-host is authenticated into the tailnet as `100.94.122.18`.
- `tailscale up` is configured with `--accept-dns=false` and only
  `192.168.20.101/32,192.168.40.50/32`.
- The advertised routes have been approved in the Tailscale admin console.
- Local forwarding to Home Assistant has been validated from docker-host
  (`http://192.168.20.101:8123` returned `200`).
- Off-LAN client validation passed on 2026-05-28 for docker-host and routed
  Home Assistant and OMV host paths.
- docker-host keeps HTTP apt traffic through apt-cacher-ng, but HTTPS apt traffic
  is direct because apt-cacher-ng rejects HTTPS CONNECT.

Validation note, 2026-05-31:

- Mobile HA access works through Tailscale, but Grafana and Uptime Kuma on
  `192.168.60.10` are not reachable from mobile.
- LAN access to `192.168.60.10:3000` and `192.168.60.10:3001` works.
- docker-host now advertises `192.168.60.10/32` and has routed UFW allowances
  for ports `3000` and `3001`.
- Approve the new `192.168.60.10/32` route in Tailscale admin if it is pending,
  then retest from mobile data.

## Target access

| Target | Route |
|---|---|
| docker-host services | docker-host Tailscale node / MagicDNS name |
| Home Assistant | `192.168.20.101/32` routed through docker-host |
| OMV | `192.168.40.50/32` routed through docker-host |
| Grafana and Uptime Kuma | `192.168.60.10/32` routed through docker-host; expose only ports `3000` and `3001` |

## Deployment notes

1. Install Tailscale on docker-host.
2. Authenticate interactively or with a short-lived auth key stored outside the repo.
3. Enable IP forwarding on docker-host.
4. Start Tailscale with the approved host routes.
5. Approve routes in the Tailscale admin console.
6. Add Tailscale ACLs matching `docs/reference/access-matrix.md`.
7. Update docker-host UFW to allow approved service ports on `tailscale0`.
8. Test from mobile data before depending on it.

## Docker-host firewall notes

Use interface-scoped or tailnet-scoped rules. Example intent:

```bash
ufw allow in on tailscale0 to any port 22 proto tcp comment "Tailscale SSH admin"
ufw allow in on tailscale0 to any port 3001 proto tcp comment "Homepage"
ufw allow in on tailscale0 to any port 8081 proto tcp comment "Dozzle"
ufw route allow in on tailscale0 out on eth0 to 192.168.20.101 port 8123 proto tcp comment "Tailscale routed HA UI"
ufw route allow in on tailscale0 out on eth0 to 192.168.40.50 port 22 proto tcp comment "Tailscale routed OMV SSH"
ufw route allow in on tailscale0 out on eth0 to 192.168.40.50 port 80 proto tcp comment "Tailscale routed OMV HTTP"
ufw route allow in on tailscale0 out on eth0 to 192.168.40.50 port 443 proto tcp comment "Tailscale routed OMV HTTPS"
ufw route allow in on tailscale0 out on eth0 to 192.168.60.10 port 3000 proto tcp comment "Tailscale routed Grafana"
ufw route allow in on tailscale0 out on eth0 to 192.168.60.10 port 3001 proto tcp comment "Tailscale routed Uptime Kuma"
```

Routed HA/OMV/monitoring traffic uses UFW route rules, not local input-only
rules. Do not expose InfluxDB (`8086`) over Tailscale unless a separate
admin-only need is documented.

## Validation

From a Tailscale client off the home LAN:

```bash
tailscale status
ping 192.168.20.101
curl -I http://192.168.20.101:8123
ping 192.168.40.50
curl -I http://192.168.40.50/
ping 192.168.60.10
curl -I http://192.168.60.10:3000/
curl -I http://192.168.60.10:3001/
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
