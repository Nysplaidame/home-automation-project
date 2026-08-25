---
title: Tailscale Remote Access Guide
description: Daily remote access through docker-host host routes, with WireGuard as fallback
tags: [tailscale, remote-access, docker-host, vpn]
created: 2026-05-23
modified: 2026-08-21
type: procedure
status: active
---

# Tailscale Remote Access Guide

Tailscale is the daily remote-access layer. WireGuard on OpenWrt remains a
dormant fallback.

## Design

docker-host joins the tailnet and advertises host routes only:

```bash
tailscale up --accept-dns=false --hostname=docker-host --advertise-routes=192.168.20.101/32,192.168.30.20/32,192.168.40.50/32,192.168.60.10/32
```

Routes must be approved in the Tailscale admin console before clients can use
them.

Do not advertise broad VLAN or RFC1918 ranges.

Live state, 2026-07-02:

- Tailscale `1.98.3` is installed on docker-host.
- `tailscaled` is active.
- docker-host is authenticated into the tailnet as `100.94.122.18`.
- `tailscale up` is configured with `--accept-dns=false`,
  `--hostname=docker-host`, and only host routes:
  `192.168.20.101/32,192.168.30.20/32,192.168.40.50/32,192.168.60.10/32`.
- The HA, OMV, monitoring, and Frigate routes are approved. On 2026-07-29
  docker-host reported all four under both `PrimaryRoutes` and `AllowedIPs`.
- Local forwarding to Home Assistant has been validated from docker-host
  (`https://192.168.20.101:8123` returned `200` after HA native HTTPS cutover).
- Off-LAN client validation passed on 2026-05-28 for docker-host and routed
  Home Assistant and OMV host paths.
- docker-host keeps HTTP apt traffic through apt-cacher-ng, but HTTPS apt traffic
  is direct because apt-cacher-ng rejects HTTPS CONNECT.
- Stale broad route preference `192.168.20.0/24` was removed from docker-host
  Tailscale prefs on 2026-07-02. Do not reintroduce broad VLAN routes.

Validation note, 2026-05-31:

- Mobile HA access works through Tailscale, and Grafana/Uptime Kuma on
  `192.168.60.10` were confirmed reachable from mobile after route approval.
- LAN access to `192.168.60.10:3000` and `192.168.60.10:3001` works.
- docker-host now advertises `192.168.60.10/32` and has routed UFW allowances
  for ports `3000` and `3001`.
- OpenWrt now allows docker-host `192.168.20.102` to reach the monitoring VM
  only on Grafana/Kuma ports `3000` and `3001` for this routed path.
- The new `192.168.60.10/32` route is approved in Tailscale admin.
- During validation, the GL-MT6000 temporary `wwan_uplink` was found missing;
  restoring it and restarting `tailscaled` on docker-host restored Tailscale
  control/DERP sync.

Validation note, 2026-07-02:

- Home Assistant native HTTPS now uses the same routed HA path:
  `https://192.168.20.101:8123`.
- Operator Android Companion App worked over Tailscale after the local HA CA
  was trusted, but Tailscale connection state showed DERP relay rather than
  direct UDP.
- HA logs showed intermittent Companion App websocket drops from the
  docker-host route address (`192.168.20.102`) with `No PONG received after
  27.5 seconds` while the phone was using the relay path.
- A five-minute mobile-data watch after removing the stale broad route was
  clean, but a later WiFi-with-Tailscale-on test produced another websocket
  drop. Direct HomeAdmin WiFi with Tailscale off was clean.
- At home, use direct HomeMain/HomeAdmin WiFi with Tailscale off. Use Tailscale
  for off-WiFi remote access.
- Optional future direct-connect improvement: forward UDP `41641` from the
  upstream internet router to the GL-MT6000 uplink address, then forward UDP
  `41641` on the GL-MT6000 to docker-host `192.168.20.102`. Do this only as a
  deliberate network-change window.

Validation note, 2026-07-05:

- Direct Frigate PWA off-WiFi access uses a narrow host route.
  docker-host now advertises `192.168.30.20/32`, has a UFW route allowance from
  `tailscale0` to `192.168.30.20:8971`, and OpenWrt allows only docker-host
  `192.168.20.102` to Frigate `192.168.30.20:8971`.
- Frigate's internal unauthenticated API on `192.168.30.20:5000` remains
  unadvertised and is not part of the mobile route.
- Live docker-host validation reached `https://192.168.30.20:8971/api/version`
  and received HTTP `401`, which is the expected auth challenge.
- On 2026-07-29 the existing workstation Tailscale identity was enabled only
  for the validation window. Frigate HTTPS on `8971` returned the expected
  authenticated `401` challenge while port `5000` remained unreachable. The
  workstation was returned to its prior stopped Tailscale state afterward.

Homepage canonical-name note, updated 2026-08-21:

- The OnePlus phone has identity-scoped grants to docker-host
  `100.94.122.18` on HTTPS `tcp/443`, fixed Homepage proxy ports
  `tcp/8180-8209`, and split DNS `tcp/53,udp/53` only.
- Tailscale split DNS sends the `home.local` suffix to AdGuard on
  `100.94.122.18`. AdGuard rewrites only `homepage.home.local` to that tailnet
  address, while router dnsmasq remains authoritative on home WiFi and returns
  the LAN address `192.168.20.102`.
- This split-horizon arrangement gives the phone Homepage and every
  user-facing card's fixed proxy URL without advertising a broad VLAN route.
  Homepage cards use `https://homepage.home.local/` or a fixed
  `https://homepage.home.local:<proxy-port>/` route; qBittorrent uses the
  fixed same-origin `/portal-preview/qbittorrent/` route.
- The same Homepage links remain valid on home WiFi with Tailscale off because
  router DNS returns `192.168.20.102` and the proxy firewall allows LAN
  clients. The mobile-data acceptance test must use Tailscale because no public
  Internet exposure was added.

## Target access

| Target | Route |
|---|---|
| docker-host services | docker-host Tailscale node / MagicDNS name |
| Home Assistant | `192.168.20.101/32` routed through docker-host |
| Frigate PWA | `192.168.30.20/32` routed through docker-host; expose only authenticated HTTPS port `8971` |
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
ufw allow in on tailscale0 to any port 8180:8209 proto tcp comment "Homepage fixed proxies"
ufw allow in on tailscale0 to any port 53 proto tcp comment "Tailscale split DNS TCP"
ufw allow in on tailscale0 to any port 53 proto udp comment "Tailscale split DNS UDP"
ufw allow in on tailscale0 to any port 8081 proto tcp comment "Dozzle"
ufw route allow in on tailscale0 out on eth0 to 192.168.20.101 port 8123 proto tcp comment "Tailscale routed HA UI"
ufw route allow in on tailscale0 out on eth0 to 192.168.40.50 port 22 proto tcp comment "Tailscale routed OMV SSH"
ufw route allow in on tailscale0 out on eth0 to 192.168.40.50 port 80 proto tcp comment "Tailscale routed OMV HTTP"
ufw route allow in on tailscale0 out on eth0 to 192.168.40.50 port 443 proto tcp comment "Tailscale routed OMV HTTPS"
ufw route allow in on tailscale0 out on eth0 to 192.168.30.20 port 8971 proto tcp comment "Tailscale routed Frigate HTTPS"
ufw route allow in on tailscale0 out on eth0 to 192.168.60.10 port 3000 proto tcp comment "Tailscale routed Grafana"
ufw route allow in on tailscale0 out on eth0 to 192.168.60.10 port 3001 proto tcp comment "Tailscale routed Uptime Kuma"
```

Routed HA/OMV/monitoring traffic uses UFW route rules, not local input-only
rules. Do not expose InfluxDB (`8086`) over Tailscale unless a separate
admin-only need is documented.

OpenWrt must also allow the narrow routed monitoring path from docker-host to
the monitoring VM:

```text
192.168.20.102 -> 192.168.60.10 tcp/3000,3001
```

OpenWrt must also allow the narrow routed Frigate PWA path from docker-host to
the Frigate host:

```text
192.168.20.102 -> 192.168.30.20 tcp/8971
```

## Validation

From a Tailscale client off the home LAN:

```bash
tailscale status
ping 192.168.20.101
curl -k -I https://192.168.20.101:8123
ping 192.168.40.50
curl -I http://192.168.40.50/
ping 192.168.60.10
curl -I http://192.168.60.10:3000/
curl -I http://192.168.60.10:3001/
curl -k -I https://192.168.30.20:8971/
```

Confirm blocked paths:

```bash
ping 192.168.10.10
curl -I http://192.168.30.20:5000/
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
