---
title: Phase 05A - Local AI Inference
description: llm-host LXC for shared-iGPU llama.cpp, Open WebUI, and Home Assistant voice inference
tags: [install, local-ai, llm, voice, home-assistant]
created: 2026-06-15
modified: 2026-06-26
type: install-guide
status: active
---

# Phase 05A - Local AI Inference

## Purpose

Build CT 114 `llm-host` as the dedicated local AI inference host. This keeps
model, STT, and TTS workloads away from VM 103 `docker-host` while preserving a
clean upgrade path from the current 32 GB host to a later 64 GB / 14B model
setup.

## Runs on

- Proxmox host shell.
- llm-host over SSH at `192.168.20.104`.
- Home Assistant UI.
- Admin laptop.

## Prerequisites

- Phase 02 complete.
- Phase 03 complete if testing Home Assistant Assist immediately.
- Phase 05 complete if Tailscale/MagicDNS and docker-host remote access are in use.
- Router firewall and DNS policy can be updated for CT 114.

## Inputs

- `<7B_OR_8B_Q4_GGUF_MODEL>`
- chosen Piper voice
- Home Assistant admin access

## Commands

Follow the full guide:

- `scripts/setup/proxmox/llm_host_setup_guide.md`

Run on: llm-host over SSH after Docker Compose is installed.

```sh
cd /opt/stacks/local-ai
docker compose config
docker compose up -d
docker compose ps
```

Run on: Home Assistant UI.

1. Add the llama.cpp/OpenAI-compatible backend at `http://192.168.20.104:8081/v1`
   where the client supports OpenAI-compatible local endpoints.
2. Add Wyoming Piper at `192.168.20.104:10200`.
3. Add Wyoming Whisper at `192.168.20.104:10300`.
4. Add Wyoming OpenWakeWord at `192.168.20.104:10400`.
5. If Home Assistant still requires its native Ollama integration, keep Ollama
   installed as rollback and treat Assist migration as a separate validation
   gate.

## Explanation

The first AI phase is sized for the current 32 GB MINISFORUM host:

- CT 114 currently has 10 GiB RAM.
- The first model is a 7B/8B Q4-class model.
- Context starts at 4k.
- 8k context and 14B models are gated by performance tests.

Keep the model alias `home-assistant-llm` stable. Open WebUI and any
OpenAI-compatible clients should point to that alias rather than a specific
model filename so the later 64 GB upgrade can retarget the alias without
reworking client configuration.

VM 103 remains the expected host for future containerized query apps, but this
phase does not define any future app-specific ports, APIs, schemas, MCP
contracts, or firewall rules.

## Expected result

- CT 114 is reachable at `192.168.20.104`.
- llama.cpp, Open WebUI, Wyoming Whisper, Piper and OpenWakeWord containers run.
- `home-assistant-llm` responds through llama.cpp on `8081`.
- Home Assistant can reach the llama.cpp and Wyoming endpoints; any remaining
  native Ollama dependency is explicitly recorded as a rollback/migration gap.
- No host swap occurs during the initial AI performance tests.

## Validation

Run on: Admin laptop.

```powershell
Test-NetConnection 192.168.20.104 -Port 11434
Test-NetConnection 192.168.20.104 -Port 8081
Test-NetConnection 192.168.20.104 -Port 3002
Test-NetConnection 192.168.20.104 -Port 10200
Test-NetConnection 192.168.20.104 -Port 10300
```

Run on: llm-host over SSH.

```sh
docker compose -f /opt/stacks/local-ai/docker-compose.yml ps
curl -s http://127.0.0.1:8081/v1/models
free -h
```

Then run:

- `docs/procedures/local_ai_performance_testing.md`

## Failure recovery

- If host swap appears, reduce model size, context, or STT model before
  allocating more RAM on the 32 GB host.
- If HA becomes slow, disable the local Assist pipeline and stop the CT 114
  Compose stack.
- If a port is reachable from the wrong VLAN, fix OpenWrt and CT 114 firewall
  rules before treating the service as live.
- If voice latency is poor, keep room satellites parked and test smaller STT
  models first.

## Completion checklist

- [x] CT 114 created and documented in Proxmox reference.
- [x] DNS aliases created for `llm-host`, `ollama`, and `openwebui`.
- [x] llama.cpp and Open WebUI running; Ollama retained stopped as rollback.
- [x] Wyoming Whisper, Piper and OpenWakeWord running.
- [ ] HA Assist migrated away from native Ollama dependency.
- [x] HA Wyoming integrations connect.
- [x] Home and Overwatch Assist commands validated.
- [x] Vulkan GPU offload and concurrent Frigate use validated.
- [x] Monitoring checks added for core CT 114 services.
