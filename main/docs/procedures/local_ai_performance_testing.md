---
title: Local AI Performance Testing
description: Baseline and acceptance procedure for llm-host model, STT, and TTS workloads
tags: [local-ai, performance, llm, voice, monitoring, proxmox]
created: 2026-06-15
type: procedure
status: active
---

# Local AI Performance Testing

Use this procedure before calling VM 104 `llm-host` live, before increasing
context size, and before switching from the first 7B/8B model to a 14B model
after a RAM upgrade.

## Acceptance criteria

- Proxmox host does not swap during normal AI use.
- Home Assistant, DNS, monitoring, and docker-host services remain responsive.
- Frigate/camera inference remains higher priority than LLM speed.
- Voice command round trip is usable before room satellites are added.
- If pressure is high, reduce model size, quantization, context, or STT model
  before widening VM RAM on the current 32 GB host.

## Phase 1 - Baseline before AI load

Run on: Proxmox host shell.

```bash
free -h
swapon --show
qm list
pvesh get /nodes/$(hostname)/status
```

Run on: Admin laptop.

```powershell
Test-Connection 192.168.20.101 -Count 2
Test-Connection 192.168.20.102 -Count 2
Test-Connection 192.168.60.10 -Count 2
```

Record:

- host available memory
- host swap used
- VM 100/101/102/103/104 memory allocation
- whether HA, DNS, monitoring, and docker-host are responsive

## Phase 2 - 4k LLM test

Run on: llm-host over SSH.

```bash
free -h
docker stats --no-stream
time curl -s http://127.0.0.1:11434/api/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "home-assistant-llm",
    "prompt": "Summarise the current local AI architecture in three short bullets.",
    "stream": false,
    "options": {
      "num_ctx": 4096
    }
  }' >/tmp/ollama-4k-test.json
free -h
```

Run on: Proxmox host shell.

```bash
free -h
swapon --show
```

Pass condition: no meaningful host swap growth and HA remains responsive.

## Phase 3 - 8k context trial

Only run this after the 4k test passes comfortably.

Run on: llm-host over SSH.

```bash
time curl -s http://127.0.0.1:11434/api/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "home-assistant-llm",
    "prompt": "Write a concise operational checklist for testing Home Assistant voice commands safely.",
    "stream": false,
    "options": {
      "num_ctx": 8192
    }
  }' >/tmp/ollama-8k-test.json
docker stats --no-stream
free -h
```

Pass condition: keep 8k only if VM 104 and the Proxmox host both retain healthy
available memory. Otherwise keep the default alias at 4k.

## Phase 4 - Voice pipeline test

Run on: Home Assistant UI.

1. Open Assist.
2. Select the local pipeline using VM 104 Whisper, `home-assistant-llm`, and
   Piper.
3. Ask a non-critical state question.
4. Ask one harmless control command against a test helper or non-critical
   device.

Run on: llm-host over SSH during the test.

```bash
docker stats --no-stream
journalctl -u docker --since "10 minutes ago" --no-pager | tail -100
```

Pass condition: voice completes without disrupting HA UI, MQTT, DNS, or
monitoring.

## Phase 5 - Normal workload concurrency

Run the same 4k LLM and voice tests while normal services are active:

- HAOS VM 100
- docker-host VM 103 and its live containers
- monitoring VM 102
- Frigate VM 101 base services

Repeat this phase after cameras and Frigate inference are live. If Frigate or
HA performance degrades, reduce local AI model/context before reducing camera
or safety-system reliability.

## Phase 6 - Upgrade test after 64 GB RAM

After the Proxmox host is upgraded to 64 GB:

1. Resize VM 104 to 20-24 GB RAM.
2. Keep the same IP, DNS names, ports, and HA integrations.
3. Pull and test the selected 14B Q4/Q5 model.
4. Recreate `home-assistant-llm` against the larger model.
5. Repeat Phases 1-5 before calling the larger model live.

## Monitoring targets

Add Uptime Kuma checks for:

- Ollama API on `192.168.20.104:11434`
- Open WebUI on `192.168.20.104:3002`
- Piper on `192.168.20.104:10200`
- Whisper on `192.168.20.104:10300`

Add Grafana panels or dashboard annotations for:

- VM 104 CPU
- VM 104 RAM
- VM 104 disk
- container status and memory
- host available RAM and swap

## Results log template

```text
Date:
Host RAM:
VM 104 RAM:
Model alias:
Underlying model:
Context tested:
Whisper model:
Piper voice:
Host swap before/after:
VM 104 peak RAM:
Tokens/sec or response time:
Voice round-trip result:
Other services affected:
Decision:
```
