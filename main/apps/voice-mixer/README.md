---
title: Voice Mixer
description: Local Gradio app and voicefx library for tuning the Metrocop radio voice post-processing
tags: [apps, voice, tts, piper, rvc, gradio, local-ai]
created: 2026-10-10
modified: 2026-10-10
type: app-spec
status: draft
---

# Voice Mixer

Tune the Combine/Metrocop radio voice by ear: adjust every post-processing stage, hear the
result straight away, A/B it against the source, and save presets that the CLI (and a future
Wyoming playback wrapper) load unchanged.

Pipeline: Piper TTS (`en_GB-alba-medium`) → RVC (Metrocop model) → **voicefx** post-processing
→ playback. This app covers the voicefx part and can produce Piper / Piper→RVC source clips on demand.

Placement: [[docs/decisions/09-voice-mixer-placement|Decision 09]] (CT 114 `llm-host`).
Install: [[docs/install/services/voice-mixer|voice-mixer install guide]].

## Run (desktop, `voice310` env)

```powershell
C:\Users\Admin\miniconda3\envs\voice310\python.exe main\apps\voice-mixer\voice_mixer\__main__.py
```

Open <http://127.0.0.1:7860/>. It listens on 127.0.0.1 only. The first run writes `config.json`
next to this README (git-ignored); edit it to change paths, the python used for Piper/RVC, the RVC
device or the port. PyTorch is never imported by the app: Piper and RVC run as subprocesses only
when you ask for a new source clip.

Tests: `python -m pytest main/apps/voice-mixer/tests` (37 tests, ~6 s).

## Using it

- **Source**: dataset clip (`dataset/metadata.csv`), game clip, any wav/flac/mp3/ogg, typed text
  through Piper, or typed text through Piper → RVC (`-pi`, `-pr`, `-ir` exposed). Synthesised clips
  are cached by text + settings under `cache/`.
- **Controls**: grouped by stage. `↺` on a slider returns it to its startup (`mid`) value;
  *Reset … to defaults* returns a whole group to neutral defaults.
- **Live preview**: slider release / control change re-renders and plays. Untick *Auto-render* for
  manual *Render* only. Late-stage changes re-render a 5 s clip in ~15–60 ms; pitch/speed changes
  redo WSOLA (well under a second for 5 s).
- **A/B**: *A* = source loudness-matched to the result, *B* = result. *⇄ A/B* or the `X` key
  switches at the same point *in the sentence* (bleep lead-in and speed change are mapped), space
  plays/pauses. Browsers block audio until the first click on the page, so the very first
  auto-play after loading may stay silent.
- **Meters**: duration, energy above 1.5 kHz (the muffling meter), peak/RMS, plus waveform and
  spectrogram for source and result on a shared time axis (dotted line = 1.5 kHz).
- **Presets** live in `presets/*.json`; `none`, `deep`, `mid` (default) and `menace` ship with the
  app (re-created if missing; they can be overwritten but not deleted from the UI).
- **Copy as CLI flags** prints a full-fidelity `python -m voicefx … --set …` line, the same via
  `--preset-file`, and the legacy `radio_fx.py` flags (with a note if the settings need more than
  the legacy flags can express).
- **Batch** renders a folder (inside the dataset, game clips, outputs, cache or a `batch_roots`
  entry in `config.json`) or a list of sentences through Piper / Piper→RVC into `outputs/<name>/`.

## Stages

source (peak-normalised) → pitch/speed (resample + WSOLA) → formant (cepstral envelope warp) →
EQ (treble restore, presence, low boost, 3 parametric bands, low/high cut) → dynamics (gate,
compressor, limiter) → radio (band-pass, drive, bit/sample-rate reduction, ring-mod/tremolo,
static, crackle, room, squelch tail) → bleeps/gaps → output loudness (peak or RMS) and fades.

Each stage is cached on its own parameters, so a late-stage change never recomputes WSOLA.

## Presets ↔ CLI

Preset JSON (`voicefx.preset/1`) is nested by stage; missing keys use defaults and unknown keys
are ignored with a warning, so older/newer files keep loading. Bleep clips are stored by name;
the folder comes from the host config.

```sh
# from main/apps/voice-mixer — full fidelity, flag-compatible with the original radio_fx.py
python -m voicefx in.wav out.wav --bleeps <vo dir> --seed 1 --preset-file presets/mid.json
python -m voicefx in_dir out_dir --bleeps <vo dir> --preset mid --set radio.crackle=0.2 --sr44
python radio_fx.py in.wav out.wav --bleeps <vo dir> --preset mid      # shim, same engine
```

Precedence: `--preset` < `--preset-file` < legacy flags (`--semitones` …) < `--set`.
The original `voice/tools/radio_fx.py` also accepts `--preset-file`, but applies only the classic
fields (pitch, speed, lowcut, low boost, drive, treble, presence, filter on/off).

The classic presets render identically to the original script: tests compare against a frozen
copy (`tests/legacy/radio_fx_v1.py`), and a real dataset clip with the real bleeps differed by at
most 0.00024 (≈8 LSB, from the 0.01 dB rounding of the stored low boost / levels).

Library use (future Wyoming wrapper):

```python
from voicefx import Pipeline, load_preset
params, _, _ = load_preset("presets/mid.json")
out = Pipeline(bleep_dir).render(Pipeline.prepare_source(audio_22050_mono_float32), params).audio
```

## Container (CT 114)

`Dockerfile` + `packaging/docker-compose.yml` + `packaging/config.container.json`.
`--build-arg WITH_RVC=1` adds CPU torch + rvc-python. See the install guide.

## Known limits

- Formant shift and "pitch only" use a cepstral envelope warp: fine for a character voice, can
  sound phasey at extreme settings (beyond about ±4 st).
- "LUFS-ish" output mode is plain RMS, not K-weighted LUFS.
- The bleep speed control uses WSOLA on very short clips; large changes smear the tone.
- RVC on CT 114 runs on CPU (no CUDA there): expect tens of seconds per sentence, versus ~9 s on
  the desktop RTX 5070 Ti. Results are cached.
- Sound quality has only been checked by measurement here (pitch/duration/level/spectrum);
  judging it by ear is the point of the app.
- No authentication: on CT 114 it relies on the VLAN/firewall boundary like Open WebUI.
