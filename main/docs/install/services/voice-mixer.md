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

> Status 2026-10-10: steps 1 (build, verified offline), 2 (layout + assets) and
> 3 (firewall) done. Image load, start (4), Tailscale route (3b) and Homepage
> (5) pending: the image load was aborted while CT 111 was saturating the shared
> NVMe (see current-live-state incident note). Do the load in a quiet period;
> it writes ~3.6 GB.

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

Without an intermediate file (CT 114 has no SSH key path; go through Proxmox):

```sh
docker save voice-mixer:local | gzip -1 | ssh root@192.168.10.10 'pct exec 114 -- sh -c "gunzip | docker load"'
```

Check host I/O first (`cat /proc/pressure/io` on Proxmox); abort if
`some avg10` climbs above ~50: VMs 100/103 share the same NVMe.

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

Published container ports on CT 114 are governed by the `DOCKER-USER` chain,
rebuilt by `/usr/local/sbin/llm-host-firewall.sh` whenever Docker starts
(`docker.service.d/firewall.conf`). The repo copy
`configs/local-ai/system/llm-host-firewall.sh` contains the `7860` block
(docker-host, management, LAN, monitoring; DROP for everyone else).

```sh
cp /usr/local/sbin/llm-host-firewall.sh /usr/local/sbin/llm-host-firewall.sh.bak-$(date +%Y%m%d-%H%M%S)-pre-voice-mixer
install -m 0755 llm-host-firewall.sh /usr/local/sbin/llm-host-firewall.sh   # repo copy
/usr/local/sbin/llm-host-firewall.sh
iptables -S DOCKER-USER | grep 7860       # 4 RETURN rules + 1 DROP
```

## 3b. Tailscale route (docker-host)

```sh
tailscale set --advertise-routes=192.168.20.101/32,192.168.30.20/32,192.168.40.50/32,192.168.60.10/32,192.168.20.104/32
```

Approve the new `192.168.20.104/32` route for `docker-host` in the Tailscale
admin console, then confirm on docker-host:

```sh
tailscale status --json | python3 -c "import json,sys; print(json.load(sys.stdin)['Self'].get('PrimaryRoutes'))"
```

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

The live portal on VM 103 differs from the repo template
(`configs/docker-host/stacks/homepage/` is stale), so edit the live files in
place, with backups, following the Open WebUI pattern (`8200` → CT 114 `3002`):

1. `/opt/stacks/homepage/preview-proxy/nginx.conf`, next free port `8210`:

   ```nginx
   server { listen 8210 ssl; include /etc/nginx/tls-common.conf; location / { include /etc/nginx/proxy-common.conf; proxy_pass http://192.168.20.104:7860; } }
   ```

   `proxy-common.conf` already sets HTTP/1.1, Upgrade headers and
   `proxy_buffering off`, which Gradio's streaming needs. Reload with
   `docker exec homepage-preview-proxy nginx -t && docker exec homepage-preview-proxy nginx -s reload`.
   The proxy reaches CT 114 from `192.168.20.102`, which step 3 allows.
2. `/opt/stacks/homepage/config/services.yaml`, group **Workshop & Knowledge**:

   ```yaml
       - Voice Mixer:
           id: portal-voice-mixer
           icon: mdi-waveform
           href: https://homepage.home.local:8210/
           description: Metrocop radio voice tuning
           siteMonitor: http://192.168.20.104:7860/
   ```

3. Confirm docker-host's host firewall admits `8210` from the same clients as
   the other portal ports (`8180`–`8209`).

## Backups

CT 114 is in the daily Proxmox LXC backup. `data/presets` is the only state
worth keeping; also copy tuned presets back into `main/apps/voice-mixer/presets/`
in the repo when they become canonical.

## Rollback

```sh
cd /opt/stacks/voice-mixer && docker compose down
```

Remove the `7860` UFW/DOCKER-USER rules and the Homepage entry.
