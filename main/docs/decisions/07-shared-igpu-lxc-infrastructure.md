---
title: Shared iGPU LXC Infrastructure
description: Durable decision for CT 111 Frigate and CT 114 local AI sharing the Intel iGPU
tags: [decision, proxmox, lxc, igpu, frigate, local-ai]
created: 2026-06-20
modified: 2026-06-20
type: decision
status: active
---

# Shared iGPU LXC Infrastructure

## Decision

Keep the Intel Meteor Lake iGPU owned by the Proxmox host. Map
`/dev/dri/renderD128` and `/dev/dri/card1` into unprivileged CT 111 and CT
114 using Proxmox device entries.

CT 111 runs Frigate/OpenVINO/VA-API on VLAN 30. CT 114 runs
Ollama/Vulkan/Open WebUI/Wyoming on VLAN 20.

## Why

- PCI passthrough grants the GPU to only one VM.
- LXCs share the host kernel and can use the DRM devices concurrently.
- Testing proved Frigate OpenVINO and Ollama Vulkan remain healthy together.
- It avoids a second accelerator and reduces CPU inference latency.

## Guardrails

- Both LXCs remain unprivileged.
- Docker requires `nesting=1,keyctl=1`.
- Host UFW and `DOCKER-USER` both scope published services.
- Production IPs belong to the LXCs. Retired VM 101/104 must not run
  concurrently with their replacements.
- Frigate cameras/MQTT remain disabled until real hardware and credentials exist.
- Local AI is advisory/non-critical and must never control safety logic.

## Rollback

VM 101 and VM 104 are stopped with `onboot=0` and retain migration snapshots.
Rollback requires stopping the replacement LXC before restoring the VM network
identity.

## Superseded design

`_archive/2026-06-20-pre-lxc-and-handoffs/06-local-ai-infrastructure-vm-era.md`
preserves the former VM 104 CPU-first design. This decision and
`docs/reference/current-live-state.md` are authoritative.
