---
title: Local AI Infrastructure
description: Dedicated local LLM, STT, and TTS inference host with 32 GB first phase and 64 GB upgrade path
tags: [architecture-decision, local-ai, llm, voice, home-assistant, proxmox]
created: 2026-06-15
type: decision
status: active
---

# Decision: Local AI Infrastructure

## Summary

Add a dedicated local AI inference VM while the Proxmox host still has 32 GB
RAM. The first phase uses a smaller 7B/8B quantized model and conservative
voice settings. The architecture keeps stable service names and Home Assistant
integration points so a later 64 GB RAM upgrade can move to a 14B model without
reworking the network or integrations.

## Host roles

| Host | Role | Notes |
|---|---|---|
| VM 104 `llm-host` | Local LLM, STT, and TTS inference | VLAN 20, `192.168.20.104`; owns Ollama, Open WebUI, Wyoming Whisper, and Wyoming Piper |
| VM 103 `docker-host` | Internal Docker app and future query-tool host | Future AI-adjacent query apps belong here unless they need heavy model inference |
| VM 100 `home-assistant` | Voice/control client | Uses Ollama and Wyoming integrations pointed at VM 104 |
| VM 101 `frigate-nvr` | Camera inference and NVR | Keeps priority for camera workloads and iGPU planning |

Do not run model weights, Ollama, STT, or TTS inference on VM 103. Keep the
Docker host easy to rebuild and reserve it for application services.

## VM 104 baseline

Current 32 GB host phase:

- VM ID: `104`
- Hostname: `llm-host`
- VLAN/IP: VLAN 20, `192.168.20.104`
- DNS aliases: `llm-host.home.local`, `ollama.home.local`, `openwebui.home.local`
- RAM: 8 GB
- CPU: 4 cores
- Disk: 120-180 GB thin-provisioned local-lvm
- First model class: 7B/8B Q4
- Stable Ollama alias: `home-assistant-llm`

Later 64 GB host phase:

- Resize the same VM to 20-24 GB RAM.
- Keep IP, DNS aliases, ports, HA integrations, and monitoring names unchanged.
- Retarget `home-assistant-llm` to a 14B Q4/Q5 model after performance testing.

## Home Assistant and voice posture

Home Assistant uses VM 104 through official integrations:

- Ollama API: `http://192.168.20.104:11434`
- Wyoming STT/TTS services on VM 104

Use HA Assist first. Start with HA Assist UI and the Home Assistant Companion
App before planning room satellites. Room satellites remain a roadmap item
until latency, wake-word behavior, and room hardware are validated.

Expose only approved entities to the LLM. VentSys and other safety-critical
actions must remain behind explicit scripts, confirmation patterns, and the
existing Home Assistant and ESPHome safety behavior.

## Future agents and query apps

Hermes Agent is roadmap-only until the core local LLM and voice path are
stable, monitored, and operationally boring. Its first role should be
advisory/tooling, not autonomous control of home safety systems.

Future containerized query apps, including the planned YouTube transcript
query app, should target VM 103 unless a later design proves they require
heavy inference on VM 104. This decision records only that boundary. It does
not define app-specific ports, APIs, schemas, MCP contracts, Compose files, or
firewall rules.

## Required validation

Before treating the AI stack as live:

- Run the local AI performance test procedure.
- Confirm no Proxmox host swap during normal use.
- Confirm HA, DNS, monitoring, docker-host, and Frigate baseline services stay
  responsive.
- Confirm STT + LLM + TTS voice round trip is usable.
- Reduce model size or context before compromising HA, Frigate, DNS, or
  monitoring responsiveness.
