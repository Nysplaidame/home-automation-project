---
title: Voice Mixer Placement
description: Where the Metrocop Voice Mixer (voicefx + Piper/RVC sources) is hosted and why
tags: [architecture-decision, local-ai, voice, tts, ct-114, docker]
created: 2026-10-10
modified: 2026-10-10
type: decision
status: proposed
---

# Decision: Host the Voice Mixer on CT 114 `llm-host`

## Summary

The Voice Mixer (`apps/voice-mixer`) runs as its own Compose stack on CT 114
`llm-host` (`192.168.20.104`, VLAN 20) at `/opt/stacks/voice-mixer/`, port
`7860`, CPU only, with Homepage linking to it. The desktop (RTX 5070 Ti) remains
the development and fast-RVC environment, running the same code from the repo.

Status: **proposed**. The app is built and tested on the desktop; the CT 114
deployment, firewall rules and Homepage entry are not live yet.

## Why CT 114

- [[03-docker-host-service-policy|Decision 03]] keeps local TTS / STT /
  wake-word inference off VM 103 `docker-host` and assigns it to CT 114. The
  mixer synthesises with Piper and converts with RVC, so it is a TTS workload.
- CT 114 already runs `wyoming-piper` with the same `en_GB-alba-medium` voice;
  the mixer mounts that voice read-only instead of keeping a second copy.
- The future Metrocop playback path (a Wyoming wrapper that applies a mixer
  preset to Piper output) belongs beside `wyoming-piper` on CT 114. Presets
  tuned in the mixer will be consumed on the same host by the same `voicefx` code.
- VLAN 20 has no internet egress, which matches the app's offline design
  (Gradio analytics off, no CDN/fonts, Hugging Face offline).

## Why not the alternatives

| Option | Verdict |
|---|---|
| VM 103 `docker-host` | Rejected: TTS inference is excluded by Decision 03. Only the DSP part would fit, and splitting it out would need a new Piper/RVC API on CT 114 for no benefit. |
| Desktop only (Windows, GPU) | Kept for development and GPU RVC, but not as the Homepage target: not always on and outside the managed infrastructure. |
| New LXC/VM | Rejected for now: no isolation benefit worth the extra guest, backups and firewall surface. |
| `local-ai` Compose stack | Rejected: a separate `/opt/stacks/voice-mixer` stack keeps mixer rebuilds from touching llama.cpp and Wyoming. |

## Guardrails

- CPU only. No `/dev/dri` mapping: the iGPU stays with llama.cpp and Frigate.
- `cpus: 2.0`, `mem_limit: 4g`; RVC loads PyTorch only inside a short-lived
  subprocess when a new Piper→RVC clip is requested, and results are cached.
- Unprivileged container user `1000:1000`; models, clips and the Piper voice
  are mounted read-only; writes go to `/opt/stacks/voice-mixer/data` only.
- No authentication in the app. Port `7860` is scoped by CT 114 UFW and the
  persistent `DOCKER-USER` policy to the same sources as Open WebUI `3002`
  (management `192.168.10.0/24`, LAN `192.168.1.0/24`, monitoring
  `192.168.60.10`). No public or Tailscale exposure is implied; Tailscale
  currently advertises no route to `192.168.20.104`.
- Batch mode can only read folders under configured roots and only writes
  under `data/outputs`.
- Not safety-relevant: like the rest of local AI it is advisory/non-critical.

## Consequences

- RVC on CT 114 is CPU-bound: tens of seconds per sentence instead of ~9 s on
  the desktop GPU. Acceptable because source clips are generated rarely and
  cached; heavy RVC work (dataset generation) stays on the desktop.
- The image must be built off-VLAN and transferred (`docker save` / `docker load`).
- CT 114 memory headroom must be checked before enabling RVC there
  (Qwen3-14B 64k context already uses most of the guest's memory).

## Rollback

`docker compose down` in `/opt/stacks/voice-mixer`, remove the `7860` UFW and
`DOCKER-USER` entries and the Homepage link. Nothing else depends on it.
