---
title: "Local AI Host"
category: entity
tags: [software, local-ai, llama-cpp, wyoming, lxc, igpu]
created: 2026-06-20
updated: 2026-10-04
sources: [project-readme, project-todo]
status: active
---

# Local AI Host

**Type:** service host
**Status:** Operational on CT 114
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/frigate]], [[entities/household-hub]]

## Overview

Unprivileged Proxmox CT 114 at `192.168.20.104` runs llama.cpp, Open WebUI,
Wyoming Whisper, Piper and OpenWakeWord. llama.cpp uses Vulkan and shares the
Intel iGPU with Frigate CT 111.

## Key Properties

- 6 cores, 28 GiB RAM, no swap (October4 read-only Proxmox configuration);
  100 GiB root disk from separately recorded acceptance.
- llama.cpp API 8081; Open WebUI 3002.
- Piper 10200; Whisper 10300; OpenWakeWord 10400.
- Host UFW and Docker `DOCKER-USER` both scope access.
- Whisper model/tokenizer data is persistent and starts offline.
- VM 104 is stopped rollback material only.

## Open Questions

- October4 package/security refresh: Fail2ban absent, no HTTP APT proxy and
  stale June security metadata; client cache times out and active cache-host
  upstream metadata returns503. Prepared repair is not applied.
  [[../../../main/docs/procedures/ct114-package-path-repair]]

- Household Hub now owns recipe research/provenance and confirmation-gated
  Mealie handoff. Obsidian remains an optional export target, not the recipe
  system of record.
- [ ] Revisit larger models only after a host RAM upgrade and repeat benchmarks.
