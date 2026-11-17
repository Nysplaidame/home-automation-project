---
title: "Local AI Host"
category: entity
tags: [software, local-ai, llama-cpp, wyoming, lxc, igpu, voice]
created: 2026-06-20
updated: 2026-11-17
sources: [project-readme, project-todo]
status: active
---

# Local AI Host

**Type:** service host
**Status:** Operational on CT 114
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/frigate]], [[entities/household-hub]], [[entities/voice-mixer]], [[concepts/tailscale-remote-access]]

## Overview

Unprivileged Proxmox CT 114 at `192.168.20.104` runs llama.cpp (chat and a
separate embeddings server), Open WebUI, Wyoming Whisper, Piper and
OpenWakeWord, plus the [[entities/voice-mixer]] as its own Compose stack.
llama.cpp uses Vulkan and shares the Intel iGPU with Frigate CT 111.

## Key Properties

- 6 cores, 28 GiB RAM, 100 GiB root disk (live `pct config`, 2026-10-11).
- llama.cpp chat `8081/v1` (Qwen3-30B-A3B Q4_K_M, 40,960-token context, f16 KV
  cache, one slot, `--cache-ram 2048`; since 2026-11-13, the 14B file is kept
  for rollback); embeddings `8082/v1` (source-scoped to docker-host); Open WebUI
  `3002`.
- Speech to text is Parakeet TDT 0.6B v2 (sherpa-onnx) behind the Wyoming
  Whisper port `10300`.
- Piper `10200`; Whisper `10300`; OpenWakeWord `10400` (HA and monitoring only).
- Voice Mixer `7860` (`/opt/stacks/voice-mixer`, CPU only, `cpus 2`, 4 GiB cap).
- Metrocop TTS `10201` (Wyoming; `metrocop-tts` in the same stack, `cpus 3.0`
  since 2026-11-13): Piper voice plus the voicefx radio preset, synthesised
  sentence by sentence when Home Assistant streams the reply.
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
- 2026-11-13: with the 30B loaded `free` shows ~25 of 28 GiB used and ~3.5 GiB
  available (page cache included), so the llama.cpp host-RAM prompt cache must
  stay capped (`--cache-ram 2048`; the 8 GiB default would OOM the CT).
- 2026-11-13: prompt processing (~85-125 tok/s on the iGPU) dominates voice
  latency, not generation (~12 tok/s). The voice assistant sends one fixed
  ~6.2k-token prompt (system text plus its tools), which llama.cpp reuses from its
  cache; a different caller context (Voice PE, HA chat box, test scripts) evicts
  it and the next voice question reads it cold (60-80 s). Details:
  `main/HANDOFF-2026-11-11-llm-igpu-speed.md`.
- 2026-11-14: the voice prompt is pinned to one version (~6,150 tokens): Home
  Assistant built two variants for the same satellite depending on whether its
  timer handler was registered, so the warm-up often primed the wrong one and the
  first spoken question read ~6.5k tokens cold (88 s). The model no longer gets
  the timer tools (timers stay with Home Assistant's local intents). Confirmed on
  2026-11-17: the first question after the 00:01 warm-up read 16 new tokens (2.8 s).
- 2026-11-14: any turn that carries earlier conversation turns costs ~9 s of
  prompt reading however short the history: llama.cpp reads it in two or three
  batches with a fixed cost each (cause unexplained). The voice component now
  sends earlier turns only when the question refers back to them.
- 2026-11-15: the streamed replies exposed that llama.cpp closes the connection
  after a stream; a request reusing it fails with "Server disconnected". The
  component uses one-shot connections for streamed requests.
- llama.cpp rejects a tool schema whose string bound exceeds ~1,500 characters
  ("failed to parse grammar", HTTP 400) for the whole request; the
  `llamacpp_conversation` component strips such bounds before sending.

## Open Questions

- October4 package/security refresh: Fail2ban absent, no HTTP APT proxy and
  stale June security metadata; client cache times out and active cache-host
  upstream metadata returns503. Prepared repair is not applied.
  [[../../../main/docs/procedures/ct114-package-path-repair]]

- Household Hub now owns recipe research/provenance and confirmation-gated
  Mealie handoff. Obsidian remains an optional export target, not the recipe
  system of record.
- [x] Design the Metrocop Wyoming playback wrapper (Piper → voicefx preset → HA):
  live as `metrocop-tts` on `10201`, streaming since 2026-11-13.
- [ ] Why llama.cpp reads conversation history in several batches with a fixed
  cost each (follow-ups that refer back still take ~11 s).
- [ ] Revisit larger models only after a host RAM upgrade and repeat benchmarks.

## Change Log

- 2026-11-17: Voice latency work of 13-15 November recorded: streamed
  sentence-by-sentence speech, Metrocop TTS `cpus 3.0`, pinned voice prompt,
  history only when referred to, one-shot streamed connections. Accuracy suite
  86/86 on 2026-11-15. Source: `main/HANDOFF-2026-11-11-llm-igpu-speed.md`.
- 2026-11-13: Production `llama-cpp` moved from Qwen3-14B (64k, q8_0 KV) to
  Qwen3-30B-A3B (40,960, f16 KV, `--cache-ram 2048`) after a trial; trial and
  capture-proxy containers removed. About 2.7x faster generation; recipe, shopping,
  weather, clock and device-state answers are now computed in code.
- 2026-10-11: Resources corrected to 6c / 28 GiB; embeddings endpoint, Voice
  Mixer, firewall script and Tailscale route added.
- 2026-06-20: Page created for the CT 114 migration.
