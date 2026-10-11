---
title: "Voice Mixer"
category: entity
tags: [software, voice, tts, piper, rvc, gradio, local-ai, ct-114]
created: 2026-10-11
updated: 2026-10-11
sources: [project-readme, project-todo]
status: active
---

# Voice Mixer

**Type:** service
**Status:** Operational on CT 114 (since 2026-10-11)
**Related:** [[entities/llm-host]], [[entities/homepage]], [[entities/home-assistant]], [[concepts/tailscale-remote-access]]

## Overview

Local Gradio app for tuning the Combine/Metrocop radio voice used for smart-home
announcements. The pipeline is Piper TTS (`en_GB-alba-medium`) → RVC voice
conversion (Metrocop model) → `voicefx` post-processing (pitch/speed, formant,
EQ, dynamics, radio character, bleeps, loudness). The app renders every change
live with an A/B toggle against the source and saves presets as JSON that the
CLI, and later a Wyoming playback wrapper, reuse.

## Key Properties

- Source: `main/apps/voice-mixer` (`voicefx` library, `voice_mixer` UI, 37 tests).
- Placement: CT 114 container `voice-mixer`, `/opt/stacks/voice-mixer`, port
  `7860`, CPU only (`cpus 2`, `mem_limit 4g`), per decision 09.
- Access: portal `https://homepage.home.local:8210/`; direct `192.168.20.104:7860`
  from management, LAN, monitoring and docker-host (`DOCKER-USER`); remote via the
  Tailscale host route `192.168.20.104/32`. No app-level auth.
- Presets: `voicefx.preset/1` JSON nested by stage; shipped `none`, `deep`,
  `mid` (default), `menace`; live copies in `/opt/stacks/voice-mixer/data/presets`.
- CLI: `python -m voicefx in.wav out.wav --bleeps <dir> --preset-file mid.json`,
  flag-compatible with the original `radio_fx.py`.
- Offline by design: Gradio analytics off, Hugging Face offline, RVC base
  models baked into the image (VLAN 20 has no internet egress).

## Notes & Observations

- Late-stage slider changes re-render a 5 s clip in ~15–60 ms (per-stage cache);
  pitch/speed changes redo WSOLA in well under a second.
- Piper→RVC: ~9 s on the desktop RTX 5070 Ti; ~30 s on CT 114 CPU (2 cores).
- The classic presets render within ~8 LSB of the original `radio_fx.py`.
- Sound quality has been checked by measurement only; judging it by ear is
  the purpose of the app.

## Open Questions

- [ ] Design the Wyoming playback wrapper that applies a mixer preset to Piper
  output for Home Assistant.
- [ ] Decide whether a trained Metrocop Piper voice replaces Piper→RVC at runtime.

## Change Log

- 2026-10-11: Deployed on CT 114 with Homepage portal entry and Tailscale route.
- 2026-10-10: Built and verified on the desktop; placement decision 09 approved.
