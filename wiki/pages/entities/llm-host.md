---
title: "Local AI Host"
category: entity
tags: [software, local-ai, ollama, wyoming, lxc, igpu]
created: 2026-06-20
updated: 2026-06-20
sources: [project-readme, project-todo]
status: active
---

# Local AI Host

**Type:** service host
**Status:** Operational on CT 114
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/frigate]]

## Overview

Unprivileged Proxmox CT 114 at `192.168.20.104` runs Ollama, Open WebUI,
Wyoming Whisper, Piper and OpenWakeWord. Ollama uses Vulkan and shares the Intel
iGPU with Frigate CT 111.

## Key Properties

- 4 cores, 10 GiB RAM, 100 GiB root disk.
- Ollama API 11434; Open WebUI 3002.
- Piper 10200; Whisper 10300; OpenWakeWord 10400.
- Host UFW and Docker `DOCKER-USER` both scope access.
- Whisper model/tokenizer data is persistent and starts offline.
- VM 104 is stopped rollback material only.

## Open Questions

- [ ] Decide whether Overwatch recipes should save to Mealie or a protected
  Obsidian ingestion service.
- [ ] Revisit larger models only after a host RAM upgrade and repeat benchmarks.
