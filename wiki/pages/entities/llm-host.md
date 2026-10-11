---
title: "Local AI Host"
category: entity
tags: [software, local-ai, llama-cpp, wyoming, lxc, igpu, voice]
created: 2026-06-20
updated: 2026-10-11
sources: [project-readme, project-todo]
status: active
---

# Local AI Host

**Type:** service host
**Status:** Operational on CT 114
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/frigate]], [[entities/voice-mixer]], [[concepts/tailscale-remote-access]]

## Overview

Unprivileged Proxmox CT 114 at `192.168.20.104` runs llama.cpp (chat and a
separate embeddings server), Open WebUI, Wyoming Whisper, Piper and
OpenWakeWord, plus the [[entities/voice-mixer]] as its own Compose stack.
llama.cpp uses Vulkan and shares the Intel iGPU with Frigate CT 111.

## Key Properties

- 6 cores, 28 GiB RAM, 100 GiB root disk (live `pct config`, 2026-10-11).
- llama.cpp chat `8081/v1` (Qwen3-14B 64k context); embeddings `8082/v1`
  (source-scoped to docker-host); Open WebUI `3002`.
- Piper `10200`; Whisper `10300`; OpenWakeWord `10400` (HA and monitoring only).
- Voice Mixer `7860` (`/opt/stacks/voice-mixer`, CPU only, `cpus 2`, 4 GiB cap).
- Published ports are scoped by `/usr/local/sbin/llm-host-firewall.sh`
  (`DOCKER-USER`), tracked in the repo as
  `configs/local-ai/system/llm-host-firewall.sh`.
- Reachable over Tailscale through the docker-host host route
  `192.168.20.104/32` (since 2026-10-11); routed traffic arrives SNATed from
  docker-host, so only docker-host-allowed ports pass.
- Whisper model/tokenizer data is persistent and starts offline; VLAN 20 has no
  internet egress, so images are built elsewhere and loaded through Proxmox.
- VM 104 is stopped rollback material only.

## Notes & Observations

- 2026-10-11: with Qwen3-14B loaded the CT used ~16.5 of 28 GiB with no memory
  pressure, leaving room for the Voice Mixer's 4 GiB cap.

## Open Questions

- [ ] Decide whether Overwatch recipes should save to Mealie or a protected
  Obsidian ingestion service.
- [ ] Design the Metrocop Wyoming playback wrapper (Piper → voicefx preset → HA).

## Change Log

- 2026-10-11: Resources corrected to 6c / 28 GiB; embeddings endpoint, Voice
  Mixer, firewall script and Tailscale route added.
- 2026-06-20: Page created for the CT 114 migration.
