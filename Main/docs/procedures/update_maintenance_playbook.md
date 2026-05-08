# Update Maintenance Playbook

---
title: Update Maintenance Playbook
description: Temporary WAN access, local caching, and offline update patterns for restricted VLAN hosts
tags: [operations, updates, firewall, docker-host, frigate, maintenance]
created: 2026-05-08
type: procedure
status: active
---

## Purpose

This project deliberately keeps several VLANs and hosts off the internet by
default. That is the right security posture, but it means software updates need
an intentional operational pattern.

This document defines the chosen strategy:

- **Short term:** manual, host-scoped maintenance windows using temporary WAN rules
- **Preferred medium term:** a local package cache on `docker-host`
- **Use when caching is impractical:** offline artifact transfer (`docker save/load`,
  copied packages, manual firmware upload)
- **Not the default today:** broad permanent WAN access for restricted hosts

## Current policy by network / host

| Scope | Current WAN posture | Update method |
|---|---|---|
| VLAN 10 management | Full internet | Normal package updates |
| HA VM `192.168.20.101` | Allowed | Normal add-on / integration updates |
| Docker host `192.168.20.102` | Blocked except maintenance window | Temporary WAN rule now; cache later |
| Frigate VM `192.168.30.20` | Blocked except maintenance window | Temporary WAN rule now; offline image transfer or cache later |
| Printers VLAN 35 | `443` only | Vendor OTA only |
| Storage VLAN 40 | Blocked | Manual / local-only maintenance |
| IoT VLAN 50 | Blocked | Local OTA only; no general internet updates |

## Chosen long-term strategy

### Default operational model

1. Keep restricted hosts blocked from the internet by default.
2. Use **manual, narrow maintenance windows** for hosts that truly need upstream access.
3. Add a **local APT cache** as the first quality-of-life improvement.
4. Use **offline Docker image transfer** before introducing a registry mirror.
5. Add a **registry mirror** only if container count and pull frequency justify the extra moving parts.

### Why this hybrid model

- It keeps the day-1 security posture strong.
- It avoids building a complex mirror stack before there is real operational pain.
- It still gives a clear path to reducing maintenance friction over time.

## Temporary WAN rules

These are the only temporary internet rules that should routinely exist in this
project.

### Docker host maintenance window

Add:

```sh
uci add firewall rule
uci set firewall.@rule[-1].name='TEMP Docker Host Update Access'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].src_ip='192.168.20.102'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].dest_port='80 443'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci commit firewall
/etc/init.d/firewall restart
```

Remove:

```sh
for section in $(uci show firewall | sed -n "s/^\(firewall\.[^.]*\)=rule$/\1/p"); do
    [ "$(uci -q get ${section}.name)" = "TEMP Docker Host Update Access" ] && uci delete "${section}"
done
uci commit firewall
/etc/init.d/firewall restart
```

Typical use:

- `apt-get update && apt-get upgrade`
- `docker compose pull`
- base package install for approved internal workloads

### Frigate maintenance window

Add:

```sh
uci add firewall rule
uci set firewall.@rule[-1].name='TEMP Frigate Update Access'
uci set firewall.@rule[-1].src='nvr'
uci set firewall.@rule[-1].src_ip='192.168.30.20'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].dest_port='80 443'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci commit firewall
/etc/init.d/firewall restart
```

Remove:

```sh
for section in $(uci show firewall | sed -n "s/^\(firewall\.[^.]*\)=rule$/\1/p"); do
    [ "$(uci -q get ${section}.name)" = "TEMP Frigate Update Access" ] && uci delete "${section}"
done
uci commit firewall
/etc/init.d/firewall restart
```

Typical use:

- `docker compose pull`
- security updates to the Debian base on VM 101

### Printers

Do **not** create an extra generic printer update rule unless there is a specific
vendor need. VLAN 35 already has a standing `443/tcp` OTA allowance.

### IoT / VentSys

Do **not** create broad temporary WAN rules for VLAN 50 as a normal practice.
Use local OTA via Home Assistant / ESPHome only.

## Local update methods that avoid WAN rules

### Home Assistant

Home Assistant can already push or coordinate several local-only changes:

- ESPHome OTA firmware updates
- package and dashboard deployment
- local integration configuration

This is the preferred method for VentSys devices and other HA-managed nodes.

### Docker images without WAN on target host

Pull on an internet-enabled machine:

```sh
docker pull ghcr.io/blakeblackshear/frigate:stable
docker save ghcr.io/blakeblackshear/frigate:stable -o frigate-stable.tar
```

Copy the tarball to the restricted host, then:

```sh
docker load -i frigate-stable.tar
```

This is the preferred non-WAN update method for Frigate until a registry mirror
is clearly justified.

### Debian packages via local cache

Preferred next improvement: run `apt-cacher-ng` as an internal service on
`docker-host`.

Intended use:

- `docker-host` itself
- `frigate-nvr`
- future Debian/Ubuntu utility VMs

This reduces WAN exposure windows, but still assumes **some** host periodically
refreshes upstream package metadata.

Design reference:

```text
docs/procedures/apt_cacher_ng_design.md
```

Planned cache endpoint:

```text
apt-cacher-ng.home.local -> 192.168.20.102:3142
```

Keep Docker image updates separate; `apt-cacher-ng` is for APT package traffic,
not container image layers.

## Recommended next implementation order

### Phase A — now

- Keep manual maintenance windows as the live operational method.
- Use offline Docker image transfer for Frigate when convenient.

### Phase B — first improvement

- Deploy `apt-cacher-ng` on `docker-host`.
- Add tightly scoped firewall rules so approved managed hosts can reach only the
  cache service, not the internet broadly.
- Start with `frigate-nvr` as the first restricted client.

### Phase C — only if needed

- Consider a Docker registry mirror or local registry.
- Only do this once there are multiple recurring Compose workloads and update
  friction is real.

## Maintenance checklist

Before update:

- confirm you are in a scheduled maintenance window
- take a manual backup/snapshot if the change is meaningful
- enable only the host-specific temporary rule you need

During update:

- run updates
- verify application health
- confirm the service actually came back cleanly

After update:

- remove the temporary rule immediately
- confirm internet is blocked again from that host
- note the change in handoff / TODO if it affected architecture or operations

## Decision summary

- The project chooses a **hybrid update model**
- **Default today:** temporary host-scoped WAN access
- **Preferred medium term:** local APT cache
- **Fallback when easier:** offline artifact transfer
- **Later only if justified:** Docker registry mirror
