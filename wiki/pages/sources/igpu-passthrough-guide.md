---
title: "Shared Intel iGPU Mapping Guide"
category: source
tags: [igpu, proxmox, frigate, openvino, vaapi, hardware-acceleration]
created: 2026-04-07
updated: 2026-08-25
status: stable
---

# Source: iGPU Passthrough Guide

**Original file:** `scripts/setup/proxmox/igpu_passthrough_guide.md`
**Date ingested:** 2026-04-07
**Type:** setup guide

## Summary

Production guide for sharing the MINISFORUM host's Meteor Lake iGPU with
unprivileged CT 111 and CT 114 through DRM device mappings.

## Key Takeaways

- Host devices are `/dev/dri/renderD128` and `/dev/dri/card0`.
- Map both into CT 111 and CT 114 with `pct set`; production group IDs are
  render `993` and video `44`.
- Both containers require `nesting=1,keyctl=1` for Docker.
- Validate with `vainfo`; then verify Frigate OpenVINO and llama.cpp Vulkan
  concurrently.
- Do not revive the archived exclusive PCI-passthrough procedure for VM 101.

## Entities Mentioned

[[entities/frigate]], [[entities/llm-host]], [[entities/proxmox]], [[entities/minisforum-m1-pro-125h]]

## Contradictions / Updates

The April exclusive-VM passthrough design is superseded by shared device mapping
for the two production LXCs.
