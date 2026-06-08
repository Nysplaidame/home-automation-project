---
title: Self Hosted Services And Remote Access Platform
description: OMV NAS, docker-host app platform, Tailscale host-route access, AdGuard DNS, Immich, and WireGuard fallback
tags: [architecture-decision, docker-host, omv, tailscale, wireguard, immich, adguard]
created: 2026-05-23
modified: 2026-05-28
type: decision
status: active
---

# Decision: Self Hosted Services And Remote Access Platform

## Summary

Use a split platform:

- **OpenMediaVault (OMV)** is the NAS OS at `192.168.40.50` on VLAN 40.
- **VM 103 `docker-host`** remains the trusted Docker Compose host for internal
  app services.
- **Tailscale** is the daily remote-access layer.
- **docker-host** is the Tailscale subnet router.
- **Tailscale advertises host routes only**, not broad VLAN subnets.
- **WireGuard on OpenWrt remains configured but dormant** as a fallback path.
- **AdGuard Home, Immich, Homepage, and Dozzle** are Tier 1 docker-host services.

This keeps storage, app hosting, routing, and remote access in separate roles
that can be rebuilt or debugged independently.

## Host roles

| Host | Role | Notes |
|---|---|---|
| GL-MT6000 OpenWrt | Router, DHCP, DNS policy, firewall, dormant WireGuard | Router-deploy remains router-only |
| Proxmox MINISFORUM M1 Pro-125H | VM host | Runs HAOS, Frigate, monitoring, docker-host |
| VM 100 `home-assistant` | HAOS appliance | Not collapsed into Docker |
| VM 101 `frigate-nvr` | Camera/NVR VM | Stays on VLAN 30 |
| VM 103 `docker-host` | Docker Compose app host and Tailscale subnet router | `/opt/stacks/<service>/` |
| OMV NAS | Storage appliance | Shares, users, storage health only |

## Tailscale remote access

Daily remote access uses Tailscale. docker-host joins the tailnet and advertises
only these host routes:

```text
192.168.20.101/32  # Home Assistant
192.168.40.50/32   # OMV NAS
```

Docker-host services are reached through docker-host's own Tailscale identity
and MagicDNS name rather than by advertising the whole automation VLAN.

Do not advertise broad routes such as:

```text
192.168.20.0/24
192.168.40.0/24
192.168.0.0/16
```

Tailscale ACLs should be documented in `docs/reference/access-matrix.md`.
Auth keys, node keys, and ACL JSON with secrets do not belong in the repo.

## WireGuard fallback

OpenWrt WireGuard stays available as a dormant fallback when Tailscale is
unavailable. Its client configs remain split-tunnel and should include only:

- `192.168.1.0/24` for normal LAN access.
- `192.168.20.101/32` for Home Assistant.
- `192.168.40.50/32` for OMV host access where needed.
- `192.168.70.0/24` for DMZ fallback access.
- `10.0.0.0/24` for the VPN subnet.

WireGuard must not grant broad access to Management, NVR, Printers, Storage, or
IoT networks. The OMV exception is a host route, not VLAN 40 access.

Fallback governance is documented in
`docs/procedures/wireguard_fallback_governance.md`.

## Docker-host service tiers

### Tier 1

- AdGuard Home
- Immich
- Homepage
- Dozzle
- Tailscale subnet router

### Tier 2

- Paperless-ngx
- Mealie
- ntfy
- Actual Budget
- Scrypted

### Tier 3 / evaluate

- Vaultwarden
- Portainer
- Watchtower in monitor-only mode
- local registry mirror
- Node-RED

## Storage policy

OMV is storage-focused:

- shared folders
- users and service accounts
- SMB/NFS exports
- SMART/storage health
- backup targets

OMV is not the Docker app platform. Immich runs on docker-host and consumes OMV
storage through a documented mount/share.

## Router-deploy scope

Router-deploy covers only:

- OpenWrt DHCP/DNS
- OpenWrt firewall
- OpenWrt WireGuard fallback
- OpenWrt generated validation artifacts

It must not orchestrate Docker stacks, OMV packages, Tailscale auth, Immich, or
other application deployment.

## Known blocker to resolve before live deployment

Current router policy intentionally blocks general docker-host internet after
bootstrap. Tailscale requires persistent outbound connectivity from docker-host.
AdGuard Home also needs upstream DNS egress. The router config should therefore
allow narrowly documented docker-host egress for Tailscale and AdGuard while
keeping general Docker image pulls as a manual maintenance-window action.

## References

- [Tailscale subnet routers](https://tailscale.com/kb/1019/subnets)
- [Tailscale DNS and MagicDNS](https://tailscale.com/kb/1054/dns)
- [AdGuard Home Docker wiki](https://github.com/AdguardTeam/AdGuardHome/wiki/Docker)
- [Immich install docs](https://docs.immich.app/install/)
- [Home Assistant network storage](https://www.home-assistant.io/common-tasks/os/#network-storage)
- [OpenMediaVault documentation](https://docs.openmediavault.org/)
