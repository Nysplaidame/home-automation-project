---
title: Phase 05A - Local AI Inference
description: Rebuild CT 114 shared-iGPU llama.cpp, embeddings, Open WebUI, and Home Assistant voice inference
tags: [install, local-ai, llm, voice, home-assistant]
created: 2026-06-15
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 05A - Local AI Inference

## Purpose

Build unprivileged CT 114 `llm-host` as the dedicated local AI inference host.
It serves llama.cpp chat and embeddings, Open WebUI, Wyoming Whisper, Piper, and
OpenWakeWord while sharing the Intel iGPU with Frigate without assigning the PCI
device exclusively to either workload.

## Current-state callout

CT 114 is live at `192.168.20.104` with 4 vCPU, 10240 MiB RAM, a 100 GiB root
disk, and no swap. Current tracked Compose serves:

- `Qwen3-14B-128K-Q4_K_M.gguf` as `home-assistant-llm` with 65536-token context,
  Q8 KV cache, reasoning disabled, and Vulkan offload;
- `bge-small-en-v1.5-q8_0.gguf` as 384-dimensional
  `home-assistant-embedding`;
- Open WebUI plus offline-cached Whisper, Piper, and OpenWakeWord.

Earlier 7B/8B-at-4k language in this phase is obsolete. A smaller model/context
remains the pressure-recovery path, not the claimed live target. VM 104 is a
stopped rollback artifact and must never run while CT 114 owns the same address.

## Runs on

- Proxmox host shell for CT creation, device mapping, backup, and rollback.
- llm-host console/SSH at `192.168.20.104` as `root`.
- Admin laptop from repository root to stage tracked Compose/firewall source.
- Home Assistant UI and Terminal & SSH add-on for integration checks.

## Stop conditions

- Retired VM 104 is running or still set to start automatically.
- `/dev/dri/renderD128` and the approved Intel card node are not identified on
  the Proxmox host.
- CT 114 would need to become privileged for convenience.
- A model digest does not match its recorded expected digest.
- The host swaps materially, Frigate inference degrades, or HA/DNS/monitoring
  becomes unresponsive under load.
- A local AI port is reachable from a source not allowed in the access matrix.
- A proposed voice action is destructive, ambiguous, or safety-critical.

## Prerequisites

- Phases 02, 03, and 05 are complete.
- Frigate's shared-iGPU baseline is healthy before adding a second GPU user.
- Router/OpenWrt and CT-local policy allow only the approved HA, docker-host,
  Management/LAN, and monitoring paths.
- The exact Debian 13 LXC template, model files, and SHA-256 digests are staged
  through an approved maintenance or offline transfer path.
- A Proxmox host memory/swap baseline and a CT 114 rollback archive are planned.

## Inputs

- `<DEBIAN_13_LXC_TEMPLATE>`
- `<LOCAL_AI_CHAT_MODEL_PATH>`
- `<LOCAL_AI_CHAT_MODEL_SHA256>`
- `<LOCAL_AI_EMBED_MODEL_PATH>`
- `<LOCAL_AI_EMBED_MODEL_SHA256>`
- chosen Piper voice, recorded in the Compose review
- Home Assistant administrator access

## 1. Prove identity exclusivity and host capacity

Run on: Proxmox host shell.

```sh
qm status 104
qm set 104 --onboot 0
pct status 114 2>/dev/null || true
free -h
swapon --show
ls -l /dev/dri
lspci -nnk -s 00:02.0
```

Expected result: VM 104 is `stopped` with `onboot: 0`; a pre-existing CT 114 is
identified rather than overwritten; host memory/swap is recorded; and the Intel
GPU plus `/dev/dri/renderD128` and one `card*` node exist.

Recovery: stop VM 104 and disable its autostart. If CT 114 already exists, use
the rebuild/restore decision rather than `pct create`. If DRM nodes are absent,
repair host graphics support before creating or modifying the CT.

## 2. Create the unprivileged CT shell

Skip creation when rebuilding an already restored CT 114. Confirm the selected
template name from `pveam available` before substituting it.

Run on: Proxmox host shell.

```sh
pveam update
pveam available --section system | grep 'debian-13-standard'
pveam download local '<DEBIAN_13_LXC_TEMPLATE>'
pct create 114 "local:vztmpl/<DEBIAN_13_LXC_TEMPLATE>" \
  --hostname llm-host \
  --unprivileged 1 \
  --features nesting=1,keyctl=1 \
  --cores 4 \
  --memory 10240 \
  --swap 0 \
  --rootfs local-lvm:100 \
  --net0 name=eth0,bridge=vmbr0,tag=20,ip=192.168.20.104/24,gw=192.168.20.1 \
  --nameserver 192.168.20.1 \
  --searchdomain home.local \
  --ssh-public-keys /root/proxmox-admin.pub \
  --onboot 1 \
  --startup order=4
```

Expected result: the template downloads without error and `pct create` reports
creation of CT 114. It must remain unprivileged, use VLAN 20, have no swap, and
own the documented address only while VM 104 is stopped.

Recovery: destroy nothing automatically after a partial create. Inspect
`pct config 114`; correct a stopped empty shell with `pct set`, or remove it only
after confirming it contains no migrated data and VM 104 remains stopped.

## 3. Map the shared Intel DRM devices

The card-node number can change across host/kernel enumeration. Confirm the
actual Intel card under `/dev/dri` and update both the `pct set` command and
Compose device path together. The current tracked target is `card0`.

Run on: Proxmox host shell after confirming the current device paths.

```sh
pct set 114 --dev0 path=/dev/dri/renderD128,gid=993,mode=0660
pct set 114 --dev1 path=/dev/dri/card0,gid=44,mode=0660
pct config 114 | grep -E '^(unprivileged|features|dev0|dev1):'
pct start 114
pct exec 114 -- ls -l /dev/dri
```

Expected result: config prints `unprivileged: 1`, nesting/keyctl, and both
device mappings; inside CT 114 the DRM nodes are character devices with render
and video group access.

Recovery: stop CT 114, correct only the device path/GID mapping, and restart.
Do not switch the entire CT to privileged mode. If Frigate loses GPU access,
stop CT 114 and restore Frigate priority before further AI work.

## 4. Install the container and GPU baseline

Run on: llm-host over SSH while bounded maintenance egress is active.

```sh
apt-get update
apt-get install -y ca-certificates curl gnupg ufw fail2ban \
  mesa-vulkan-drivers vulkan-tools vainfo intel-gpu-tools jq
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
. /etc/os-release
printf '%s\n' \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $VERSION_CODENAME stable" \
  >/etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker fail2ban
```

Expected result: signed packages install cleanly and both services are active.

Run on: llm-host over SSH.

```sh
docker --version
docker compose version
vulkaninfo --summary
vainfo --display drm --device /dev/dri/renderD128
```

Expected result: Docker/Compose versions print; Vulkan identifies Intel Meteor
Lake graphics; and VA-API capabilities print without permission errors.

Recovery: confirm device mapping, group IDs, Mesa packages, and CT restart.
Repair signed-repository or DRM access directly; do not add privileged container
flags to Compose as a blanket workaround.

## 5. Stage tracked source and model files

Run on: Admin laptop from repository root in PowerShell.

```powershell
scp -r .\main\configs\local-ai root@192.168.20.104:/tmp/local-ai-source
scp '<LOCAL_AI_CHAT_MODEL_PATH>' root@192.168.20.104:/tmp/Qwen3-14B-128K-Q4_K_M.gguf
scp '<LOCAL_AI_EMBED_MODEL_PATH>' root@192.168.20.104:/tmp/bge-small-en-v1.5-q8_0.gguf
```

Expected result: all transfers finish without error. Model transfer can take a
long time; compare size and digest rather than assuming completion from elapsed
time.

Run on: llm-host over SSH.

```sh
install -d -m 0755 /opt/stacks/local-ai/{models,open-webui,whisper,piper,openwakeword}
install -m 0644 /tmp/local-ai-source/docker-compose.yml /opt/stacks/local-ai/docker-compose.yml
install -m 0644 /tmp/Qwen3-14B-128K-Q4_K_M.gguf /opt/stacks/local-ai/models/Qwen3-14B-128K-Q4_K_M.gguf
install -m 0644 /tmp/bge-small-en-v1.5-q8_0.gguf /opt/stacks/local-ai/models/bge-small-en-v1.5-q8_0.gguf
sha256sum /opt/stacks/local-ai/models/*.gguf
```

Expected result: the chat digest exactly equals
`<LOCAL_AI_CHAT_MODEL_SHA256>` and the embedding digest exactly equals
`<LOCAL_AI_EMBED_MODEL_SHA256>`. Record image tags/digests before live use;
`:main` and `:latest` tags are mutable candidate inputs, not reproducibility
proof.

Recovery: remove only the mismatched copied model and transfer it again. Never
start llama.cpp against a partial model and never “correct” the recorded digest
to match an untrusted file.

## 6. Apply both host and Docker firewall layers

Run on: llm-host local console or SSH.

```sh
ufw default deny incoming
ufw default allow outgoing
ufw default deny routed
ufw allow from 192.168.10.0/24 to any port 22 proto tcp comment 'Management SSH'
for source in 192.168.20.101 192.168.20.102 192.168.10.0/24 192.168.1.0/24 192.168.60.10; do
  ufw allow from "$source" to any port 8081 proto tcp
done
for source in 192.168.20.102 192.168.10.0/24 192.168.1.0/24 192.168.60.10; do
  ufw allow from "$source" to any port 3002 proto tcp
done
ufw allow from 192.168.20.102 to any port 8082 proto tcp
for port in 10200 10300 10400; do
  ufw allow from 192.168.20.101 to any port "$port" proto tcp
  ufw allow from 192.168.60.10 to any port "$port" proto tcp
done
ufw --force enable
install -m 0755 /tmp/local-ai-source/system/llm-host-firewall.sh /usr/local/sbin/llm-host-firewall.sh
install -d -m 0755 /etc/systemd/system/docker.service.d
install -m 0644 /tmp/local-ai-source/system/docker.service.d/firewall.conf \
  /etc/systemd/system/docker.service.d/firewall.conf
systemctl daemon-reload
systemctl restart docker
```

Expected result: Docker restart invokes the tracked `ExecStartPost` script,
which rebuilds `DOCKER-USER` with source allows followed by per-port drops.

Run on: llm-host local console or SSH.

```sh
ufw status verbose
systemctl status docker --no-pager
iptables -S DOCKER-USER
```

Expected result: UFW is active, Docker is active, chat/Open WebUI/embedding/
Wyoming rules match the access matrix, and each published port has a denying
rule after its approved sources.

Recovery: use the CT console, stop Docker, disable UFW temporarily only if
necessary, correct tracked policy, then re-enable/restart and repeat denial
tests. Do not expose the embedding endpoint beyond docker-host merely to debug
an integration.

## 7. Validate Compose before starting inference

Run on: llm-host over SSH.

```sh
cd /opt/stacks/local-ai
docker compose config --quiet
docker compose pull
docker compose up -d
docker compose ps
```

Expected result: config exits silently with `0`; pulls complete within the
maintenance window; and all six services become `Up`. If offline policy is
already restored, pre-pulled images must exist and `pull` should be skipped,
not worked around with broad egress.

Recovery: use `docker compose logs --tail=120 <service>` for the first failing
service. Stop the stack if models, offline Whisper cache, DRM, or firewall
prerequisites are incomplete.

## 8. Prove chat, embeddings, web, and voice endpoints

Run on: llm-host over SSH.

```sh
cd /opt/stacks/local-ai
curl -fsS http://127.0.0.1:8081/v1/models | jq -e '.data[] | select(.id == "home-assistant-llm")'
curl -fsS http://127.0.0.1:8081/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer sk-no-key-required' \
  -d '{"model":"home-assistant-llm","messages":[{"role":"user","content":"Reply with exactly: LOCAL AI OK"}],"max_tokens":16,"stream":false}' \
  | jq -r '.choices[0].message.content'
curl -fsS http://127.0.0.1:8082/v1/embeddings \
  -H 'Content-Type: application/json' \
  -d '{"model":"home-assistant-embedding","input":"local embedding check"}' \
  | jq -e '.data[0].embedding | length == 384'
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3002/
for port in 10200 10300 10400; do nc -zvw3 127.0.0.1 "$port"; done
```

Expected result: model lookup succeeds; chat returns `LOCAL AI OK` without a
reasoning preamble; embedding assertion returns `true`; Open WebUI returns
`200` or its documented redirect; and all three Wyoming ports connect.

Run on: llm-host over SSH.

```sh
docker logs llama-cpp 2>&1 | grep -E 'Vulkan|model loaded|server is listening' | tail -n 20
docker stats --no-stream
free -h
```

Expected result: logs identify Vulkan/model load/listening state, containers
have bounded memory, and CT 114 is not swapping.

Recovery: for malformed output, confirm the correct alias/model, reasoning-off
flag, prompt template, and digest. For OOM/pressure, stop the stack and reduce
context or return to the previously accepted smaller model before allocating
more host memory.

## 9. Configure Home Assistant integrations

Run on: Home Assistant UI.

1. Install or restore the tracked `llamacpp_conversation` custom component.
2. Configure its local OpenAI-compatible base URL as
   `http://192.168.20.104:8081/v1` with alias `home-assistant-llm`.
3. Add Wyoming Piper at `192.168.20.104:10200`.
4. Add Wyoming Whisper at `192.168.20.104:10300`.
5. Add Wyoming OpenWakeWord at `192.168.20.104:10400`.
6. Build a local Assist pipeline and expose only explicitly approved entities.
7. Ask one state-only question, then control only a disposable test helper or
   non-critical light.

Expected result: each integration connects, the state answer is correct, the
harmless action is confirmed in HA history, and no safety-critical entity is
available to the conversation agent.

Run on: Home Assistant Terminal & SSH add-on.

```sh
ha core check
ha core info
```

Expected result: configuration is valid and Core remains `running`.

Recovery: switch the Assist pipeline back to its last known-good agent or
disable the local pipeline; do not uninstall the existing working voice path
while diagnosing CT 114.

## 10. Prove access denial and concurrent iGPU safety

Run on: an intentionally unapproved Guest/DMZ client in PowerShell.

```powershell
Test-NetConnection 192.168.20.104 -Port 8081
Test-NetConnection 192.168.20.104 -Port 8082
Test-NetConnection 192.168.20.104 -Port 3002
Test-NetConnection 192.168.20.104 -Port 10300
```

Expected result: every test reports `TcpTestSucceeded : False` while the same
client still reaches the public internet.

Run the [local AI performance procedure](../../procedures/local_ai_performance_testing.md)
with Frigate and normal services active. Record host/CT memory, host swap,
response latency, voice round trip, and Frigate health before and after.

Expected result: no meaningful host swap growth, no Frigate/HA/DNS/monitoring
regression, and accepted response latency. Current 14B/65536 settings remain
live only while those criteria continue to pass.

Recovery: stop or scale down local AI first. Frigate and home-automation
reliability take priority over model size or context length.

## 11. Prove reboot, backup, and rollback

Run on: Proxmox host shell during a maintenance window.

```sh
pct reboot 114
sleep 20
pct status 114
pct exec 114 -- docker compose -f /opt/stacks/local-ai/docker-compose.yml ps
vzdump 114 --mode snapshot --compress zstd --storage omv-backups
```

Expected result: CT 114 returns `running`, all services recover including
offline Whisper, and `vzdump` ends in `TASK OK`. Validate the archive with the
Phase 10 isolated LXC restore drill before calling it restorable.

Rollback to VM 104 is emergency-only: stop CT 114, disable its autostart,
confirm its address is no longer present, verify VM 104's NIC and snapshot, then
start VM 104 during a recorded maintenance window. Never run both simultaneously.
Return by stopping VM 104 before re-enabling CT 114.

## End-of-phase validation

Run on: Proxmox host shell.

```sh
pct config 114
pct status 114
qm status 104
free -h
swapon --show
```

Expected result: CT 114 is running with the approved unprivileged config, VM 104
is stopped, host memory has headroom, and swap is empty or unchanged from the
recorded healthy baseline.

Run on: llm-host over SSH.

```sh
cd /opt/stacks/local-ai
docker compose config --quiet
docker compose ps
sha256sum models/*.gguf
iptables -S DOCKER-USER
systemctl --failed --no-pager
```

Expected result: CT 114 is unprivileged/running, VM 104 is stopped, host
capacity is healthy, Compose and all services pass, model digests match the
record, source-deny rules persist, and no unexplained unit is failed.

## Failure recovery matrix

| Symptom | Nearest checks | Bounded recovery | Do not do |
|---|---|---|---|
| Duplicate IP | `pct/qm status`, ARP/MAC | stop VM 104 or CT 114; keep only approved owner | run both rollback and production |
| DRM permission failure | host nodes/GIDs, `pct config`, CT nodes | stop CT; correct mapping; restart | make CT privileged |
| Model will not load | size/digest, filename, logs, RAM | retransmit trusted file or revert accepted smaller model | accept changed digest |
| Whisper fails offline | persistent cache and `HF_HUB_OFFLINE` logs | restore cache from backup during maintenance | grant permanent broad egress |
| HA cannot connect | local listener, host firewall, OpenWrt source rule | restore exact HA-to-port rule | expose port to VLAN 20 broadly |
| Guest reaches service | UFW and `DOCKER-USER` counter/order | stop stack; narrow/reload both layers | rely on UI auth alone |
| Host swap/Frigate regression | Proxmox memory, `docker stats`, Frigate health | stop AI; reduce context/model/STT load | reduce safety/camera reliability |
| Bad voice action | exposed entities, trace/history | disable pipeline; restrict entities; retest harmless helper | expose safety-critical controls |
| Reboot loses firewall | Docker drop-in and script status | reinstall tracked files, restart Docker, retest denial | start apps before policy returns |

## Completion checklist

- [ ] VM 104 is stopped/onboot-disabled and CT 114 is the sole address owner.
- [ ] CT 114 is unprivileged with exact resources, no swap, and shared DRM mappings.
- [ ] Docker, Vulkan, and VA-API checks pass without privileged workarounds.
- [ ] Both model digests and deployed image digests are recorded.
- [ ] Chat alias/output, 384-dimensional embeddings, Open WebUI, and Wyoming ports pass.
- [ ] UFW and persistent `DOCKER-USER` policy pass allowed and denied tests.
- [ ] Home Assistant local conversation and Wyoming integrations pass harmless workflow tests.
- [ ] Concurrent Frigate/local-AI load meets memory, swap, latency, and reliability gates.
- [ ] Offline Whisper and firewall policy survive CT/Docker reboot.
- [ ] Backup has `TASK OK` and an isolated restore proof from Phase 10.
