---
title: DNS Resolver And Adblocking Strategy
description: AdGuard Home on docker-host, router DNS enforcement, and resilient public fallback
tags: [architecture-decision, dns, adblocking, router, docker-host, adguard]
created: 2026-05-23
modified: 2026-05-23
type: decision
status: active
---

# Decision: DNS Resolver And Adblocking Strategy

## Summary

Use **AdGuard Home on VM 103 `docker-host`** as the network-wide filtering DNS
engine.

OpenWrt remains the DHCP authority, local `home.local` DNS authority, and
firewall enforcement point. Normal clients receive their local router gateway as
DNS by DHCP. The router forwards upstream queries to AdGuard Home first and keeps
automatic public fallback resolvers so household internet survives if
docker-host or AdGuard is down.

Approved public fallback resolvers are:

1. Quad9 `9.9.9.9`
2. Cloudflare `1.1.1.1`
3. Cloudflare `1.0.0.1`

Google Public DNS is not approved for active configuration.

## Target flow

```text
Client -> local OpenWrt dnsmasq -> AdGuard Home on docker-host -> Quad9/Cloudflare
```

If AdGuard is unreachable:

```text
Client -> local OpenWrt dnsmasq -> Quad9/Cloudflare
```

This keeps local names and VLAN policy on the router while moving blocklists,
DNS filtering UI, logs, and service backup state to docker-host.

## Placement

| Component | Host | Purpose |
|---|---|---|
| DHCP | GL-MT6000 OpenWrt | Lease authority and per-VLAN DNS option delivery |
| Local DNS | GL-MT6000 OpenWrt | `home.local` records and router-local names |
| Filtering DNS | VM 103 `docker-host` | AdGuard Home blocklists, UI, query logs |
| Public fallback DNS | Router dnsmasq | Quad9 first, then Cloudflare |

AdGuard Home must live under:

```text
/opt/stacks/adguard-home/
```

## Router policy

Desired dnsmasq behavior:

- `noresolv=1` so upstreams are explicit, not inherited accidentally.
- `strictorder=1` so AdGuard is preferred before public fallback.
- `server=192.168.20.102#53` first.
- `server=9.9.9.9`, `1.1.1.1`, and `1.0.0.1` after AdGuard.

Desired DHCP behavior:

- Normal VLAN clients receive only their local router gateway as DNS.
- Restricted VLANs remain local-DNS-only.
- Guest clients also use the guest router gateway for DNS; the router handles
  upstream fallback.

Desired firewall behavior:

- Block ordinary client TCP/UDP DNS (`53`) and DNS-over-TLS (`853`) directly to
  WAN where a broad internet allow would otherwise bypass filtering.
- Allow docker-host to reach upstream DNS for AdGuard Home.
- Treat DNS-over-HTTPS blocking as best effort because it uses HTTPS (`443`).
- Keep Management VLAN as the documented emergency/admin bypass path.

## Availability model

This project chooses **resilient household mode**:

- Filtering is preferred.
- Internet access does not depend entirely on docker-host.
- If AdGuard fails, adblocking can temporarily disappear but DNS still resolves
  through the router's public fallbacks.

Strict filtering can be reconsidered later after AdGuard has monitoring, backup,
and a tested restore path.

## Options rejected for first deployment

### Pi-hole on docker-host

Pi-hole remains a reasonable alternative, but AdGuard Home is selected for the
first deployment to avoid an unresolved choice and keep docs, firewall policy,
and runbooks concrete.

### OpenWrt adblock on the router

Router-native adblocking keeps fewer moving parts, but it couples blocklist
processing, UI/reporting, and router upgrades to the routing/firewall appliance.
The GL-MT6000 should stay focused on routing, firewalling, DHCP, and local DNS.

### AdGuard Home on the router

Router-hosted AdGuard Home gives a strong UI, but it makes OpenWrt carry both the
network policy plane and the filtering application. The preferred split is
router policy plus docker-host application.

## References

- [AdGuard Home Docker wiki](https://github.com/AdguardTeam/AdGuardHome/wiki/Docker)
- [OpenWrt DNS interception guide](https://openwrt.org/docs/guide-user/firewall/fw3_configurations/intercept_dns)
- [Quad9 service addresses](https://quad9.net/service/service-addresses-and-features/)
- [Cloudflare resolver addresses](https://developers.cloudflare.com/1.1.1.1/ip-addresses/)
