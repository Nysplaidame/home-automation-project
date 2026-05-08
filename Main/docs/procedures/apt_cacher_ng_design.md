---
title: apt-cacher-ng Design
description: Local APT package cache design for restricted Debian hosts
tags: [operations, updates, apt, docker-host, firewall]
created: 2026-05-08
type: procedure
status: live
---

# apt-cacher-ng Design

## Summary

Use `docker-host` (`192.168.20.102`) as the local APT cache point for Debian-based
systems that otherwise should not have broad internet access.

Target service:

```text
apt-cacher-ng.home.local -> 192.168.20.102:3142
```

This improves package update hygiene for restricted VMs without opening broad
WAN access to those VMs.

## Live state

As of 2026-05-08, `apt-cacher-ng` is deployed directly on `docker-host` as a
Debian service, not as a container.

- Service: `apt-cacher-ng`, enabled and active
- Listener: `192.168.20.102:3142/tcp`
- Docker-host UFW: allows `192.168.30.20` to port `3142/tcp`
- Router firewall: `Frigate to APT Cache` is present before `Block NVR to Automation`
- Router firewall: `TEMP Docker Host Update Access` is removed outside maintenance
- Client proof: both `docker-host` and `frigate-nvr` ran `apt-get update` through the cache

## What this solves

`apt-cacher-ng` helps with:

- Debian base package updates
- repeated package downloads across Debian VMs
- reducing how often `frigate-nvr` needs temporary WAN access for OS updates
- creating a single place to observe and control package-fetch behavior

It does **not** solve:

- Docker image pulls
- Home Assistant add-on updates
- vendor firmware updates
- arbitrary HTTPS downloads that cannot be cached

For Docker images, keep using either temporary host-scoped WAN windows or
offline `docker save` / `docker load` until a registry mirror is justified.

## Placement decision

### Host

Run the cache on:

```text
VM 103 docker-host
192.168.20.102
VLAN 20 Automation / trusted app services
```

Why:

- already live and trusted for lightweight internal services
- stable IP and DNS
- reachable from management and approved internal hosts
- avoids adding a separate VM before the service needs one

### Deployment method

Preferred initial deployment:

- install `apt-cacher-ng` as a Debian package on `docker-host`

Reason:

- update infrastructure should keep working even if Docker itself has a problem
- it avoids choosing and maintaining a third-party container image for a core
  update path
- it is simple to operate with `systemctl`

This is a narrow exception to the normal `/opt/stacks/<service>/` Compose layout
because `apt-cacher-ng` supports the host OS update path itself.

If a container deployment is preferred later, use:

```text
/opt/stacks/apt-cacher-ng/
```

and verify the image source before deployment.

## Network access model

### Listener

`apt-cacher-ng` listens on:

```text
192.168.20.102:3142/tcp
```

### Allowed clients

Initial allowed clients:

| Client | IP | Reason |
|---|---|---|
| docker-host | `127.0.0.1` / `192.168.20.102` | self-update through cache |
| frigate-nvr | `192.168.30.20` | Debian security/base updates without broad WAN |

Later allowed clients:

- monitoring VM `192.168.60.10`
- NAS `192.168.40.50` if it is Debian-based and update policy allows it
- future Debian/Ubuntu utility VMs

Do not allow whole VLANs by default. Add host-specific firewall rules.

## Firewall design

### Required cross-VLAN rule

Frigate needs a route from VLAN 30 to the cache on VLAN 20:

```sh
uci add firewall rule
uci set firewall.@rule[-1].name='Frigate to APT Cache'
uci set firewall.@rule[-1].src='nvr'
uci set firewall.@rule[-1].src_ip='192.168.30.20'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].dest_ip='192.168.20.102'
uci set firewall.@rule[-1].dest_port='3142'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci commit firewall
/etc/init.d/firewall restart
```

### Docker-host WAN access

The cache host still needs upstream access when fetching packages that are not
already cached.

Keep the existing policy:

- no broad permanent WAN access for `docker-host`
- use `TEMP Docker Host Update Access` during cache warm-up / update windows
- remove the temp rule immediately after maintenance

This means `apt-cacher-ng` reduces WAN exposure for client VMs, but it does not
make the whole update path permanently internet-free.

## Client configuration

### docker-host

Use local loopback:

```sh
cat >/etc/apt/apt.conf.d/01proxy <<'EOF'
Acquire::http::Proxy "http://127.0.0.1:3142";
Acquire::https::Proxy "http://127.0.0.1:3142";
EOF
```

The Debian mirror files were switched from `https://deb.debian.org/...` to
`http://deb.debian.org/...` so signed Debian packages can be cached normally.

### frigate-nvr

Use the cache host:

```sh
cat >/etc/apt/apt.conf.d/01proxy <<'EOF'
Acquire::http::Proxy "http://192.168.20.102:3142";
Acquire::https::Proxy "http://192.168.20.102:3142";
EOF
```

The Debian mirror files were switched from `https://deb.debian.org/...` to
`http://deb.debian.org/...`. The Docker APT repo remains HTTPS.

### Important HTTPS note

APT repositories that are configured as `https://` may not be meaningfully
cached because the content is encrypted end-to-end. Prefer standard Debian
`http://` mirrors through the cache where package signatures provide integrity.

For vendor repos that must remain HTTPS, either:

- allow a temporary host-scoped WAN maintenance window, or
- download/install packages manually during a controlled maintenance window

Live implementation note: `apt-cacher-ng` has a narrow `PassThroughPattern` for
`download.docker.com:443` so Frigate and docker-host can refresh Docker APT
metadata through the cache host during maintenance. This passes encrypted HTTPS
traffic through; it does not cache Docker repo contents in the same useful way
as standard Debian HTTP package traffic.

## Update workflow after cache deployment

### Frigate OS package update

1. Enable `TEMP Docker Host Update Access` for the cache host.
2. On `frigate-nvr`, run:

```sh
apt-get update
apt-get upgrade
```

3. Confirm traffic succeeds through `192.168.20.102:3142`.
4. Remove `TEMP Docker Host Update Access`.
5. Confirm Frigate still has no direct WAN access.

### Docker image update

`apt-cacher-ng` does not cache Docker images. Keep using:

- `TEMP Frigate Update Access` for direct image pulls, or
- offline `docker save` / `docker load`

## Validation checklist

After deployment:

- [x] `apt-cacher-ng` service is running on `docker-host`
- [x] `docker-host` can update via `127.0.0.1:3142`
- [x] `frigate-nvr` can reach `192.168.20.102:3142`
- [x] `frigate-nvr` can run `apt-get update` without direct WAN access
- [x] `TEMP Docker Host Update Access` is removed after maintenance
- [x] direct WAN from `frigate-nvr` remains blocked

## Decision summary

- Deploy local APT caching on `docker-host`
- Use port `3142/tcp`
- Allow clients by host IP, not by whole VLAN
- Cache Debian package updates first
- Keep Docker image updates separate
- Keep temporary WAN access as the fallback and cache warm-up mechanism
