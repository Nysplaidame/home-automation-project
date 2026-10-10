---
title: Voice Mixer
description: Install the Metrocop Voice Mixer on CT 114 llm-host and link it from Homepage
tags: [install, local-ai, ct-114, voice, piper, rvc, homepage]
created: 2026-10-10
modified: 2026-10-10
type: install-guide
status: draft
---

# Voice Mixer (CT 114)

App source and usage: [[apps/voice-mixer/README|apps/voice-mixer]].
Placement rationale: [[docs/decisions/09-voice-mixer-placement|Decision 09]].

> Status: not deployed. Steps below are the intended procedure; the image
> build and CT 114 run have not been executed yet.

## Placement

- Host: CT 114 `llm-host`, `192.168.20.104`, VLAN 20.
- Stack: `/opt/stacks/voice-mixer/` (separate from `/opt/stacks/local-ai`).
- Port: `7860/tcp`, internal only.
- Homepage: link from VM 103 Homepage, group **Local AI**.

## 1. Build the image (desktop / any machine with internet)

```sh
cd main/apps/voice-mixer
docker build -t voice-mixer:local --build-arg WITH_RVC=1 .   # omit the arg for a Piper-only image
docker save voice-mixer:local | gzip > voice-mixer.tar.gz
```

Copy `voice-mixer.tar.gz` to CT 114 (VLAN 20 has no internet egress) and load it:

```sh
gunzip -c voice-mixer.tar.gz | docker load
```

## 2. Lay out the stack on CT 114

```text
/opt/stacks/voice-mixer/
  docker-compose.yml        <- main/apps/voice-mixer/packaging/docker-compose.yml
  data/                     <- config.json (created on first start), presets, cache, outputs
  models/                   <- combine_soldierv2.pth, added_IVF292_Flat_nprobe_1_combine_s2_v2.index
  clips/vo/                 <- on1.wav, on2.wav, off1-4.wav (+ other metropolice clips)
  dataset/                  <- optional: wav/ + metadata.csv
```

```sh
mkdir -p /opt/stacks/voice-mixer/{data,models,clips,dataset}
chown -R 1000:1000 /opt/stacks/voice-mixer/data
ls /opt/stacks/local-ai/piper/en_GB-alba-medium.onnx*   # must show .onnx and .onnx.json
```

Before enabling RVC, check memory headroom with llama.cpp loaded:

```sh
free -h
docker stats --no-stream
```

RVC needs roughly 2–3 GB while converting. If headroom is short, keep the
Piper-only image on CT 114 and generate RVC clips on the desktop.

## 3. Firewall (CT 114)

Mirror the Open WebUI `3002` scoping for `7860`:

```sh
ufw allow from 192.168.10.0/24 to any port 7860 proto tcp comment "Management to Voice Mixer"
ufw allow from 192.168.1.0/24  to any port 7860 proto tcp comment "LAN to Voice Mixer"
ufw allow from 192.168.60.10   to any port 7860 proto tcp comment "Monitoring to Voice Mixer"
```

Add the matching rules to CT 114's persistent `DOCKER-USER` policy (same
pattern as port 3002: RETURN for those three sources, then DROP for 7860).

## 4. Start and verify

```sh
cd /opt/stacks/voice-mixer
docker compose up -d
docker compose logs --tail 20 voice-mixer      # "[voice-mixer] config /data/config.json; serving http://0.0.0.0:7860/"
curl -sI http://127.0.0.1:7860/ | head -1     # HTTP/1.1 200 OK
```

From a LAN/management client open `http://192.168.20.104:7860/`, load a
dataset clip, move a Radio slider and confirm it re-renders, then try
*Piper* and (if built with RVC) *Piper + RVC*.

## 5. Homepage

The entry is in `configs/docker-host/stacks/homepage/config/services.yaml`
under **Local AI**. Copy that file to `/opt/stacks/homepage/config/` on VM 103;
Homepage reloads it automatically. Homepage only links to the mixer; the
browser connects to CT 114 directly, so step 3 must allow the client's subnet.

## Backups

CT 114 is in the daily Proxmox LXC backup. `data/presets` is the only state
worth keeping; also copy tuned presets back into `main/apps/voice-mixer/presets/`
in the repo when they become canonical.

## Rollback

```sh
cd /opt/stacks/voice-mixer && docker compose down
```

Remove the `7860` UFW/DOCKER-USER rules and the Homepage entry.
