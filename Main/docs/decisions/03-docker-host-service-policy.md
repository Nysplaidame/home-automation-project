---
title: Docker Host Service Policy
description: Approved service classes and boundaries for VM 103 docker-host
tags: [architecture-decision, docker, services, policy]
created: 2026-05-08
type: decision
status: active
---

# Decision: Service Policy For VM 103 `docker-host`

## Summary

VM 103 is the central trusted Docker host for lightweight **internal** services.
It is not the place for camera processing, appliance-style Home Assistant, or
public/DMZ workloads.

## What belongs on docker-host

### Approved now

- internal app workloads like Bambuddy
- internal operations helpers like `Dozzle`
- internal notification or utility services like `ntfy`
- internal package/cache helpers like `apt-cacher-ng`
- lightweight dashboards such as `Homepage` or `Homarr`

### Approved later if justified

- local registry / registry mirror
- workflow helpers such as `Node-RED`
- small internal documentation or inventory tools

## What does not belong on docker-host

- Frigate / camera processing
- Home Assistant OS / Supervisor workloads
- NAS / primary storage functions
- internet-facing reverse proxies or public services by default
- DMZ workloads
- heavy GPU / transcoding / surveillance jobs

## Why this boundary exists

- VLAN 20 is a trusted internal application network, not a public service segment.
- `docker-host` should remain easy to understand, patch, and rebuild.
- Frigate already has a better architectural home on VM 101 and VLAN 30.
- HAOS remains an appliance-style system and should not be collapsed into generic Docker hosting.

## Operational guidance

### Compose layout

All Docker-host workloads should live under:

```text
/opt/stacks/<service>/
```

Examples:

- `/opt/stacks/bambuddy/`
- `/opt/stacks/apt-cacher-ng/`
- `/opt/stacks/ntfy/`

### Service requirements

A proposed workload should meet all of these:

- internal-only use case
- modest CPU / RAM / disk profile
- no hard dependency on GPU passthrough
- can be rebuilt from Compose + config
- does not require broad permanent WAN access

Host-level support services are allowed only when they directly support the
Docker host or update path itself. `apt-cacher-ng` is the current example: it may
run as a Debian service rather than a Compose workload because it supports OS
package updates even when Docker is unhealthy.

### Change control

Before adding a new docker-host service, answer:

1. Is it internal-only?
2. Does it belong on VLAN 20 rather than DMZ / NVR / storage?
3. Does it need internet access after initial deployment?
4. Can it be represented cleanly as `/opt/stacks/<service>` with env/config separation?
5. Would failure or compromise of this service create a trust problem for other VLAN 20 systems?

If any answer is uncomfortable, stop and reconsider placement.

## Recommended near-term additions

The strongest candidates not yet deployed are:

- `apt-cacher-ng`
- `Dozzle`
- `ntfy`

These improve maintainability without violating the intended trust boundary.
