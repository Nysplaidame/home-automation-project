# HANDOFF — iGPU/LLM Architecture Migration (Option B)

**Session date:** 2026-06-19 (continued from earlier same-day handoff)
**Carries on in:** new conversation, model Sonnet for execution (Opus only if something gets genuinely stuck — see note at bottom)
**Project root:** `E:\home-automation-project`. Proxmox node name is `proxmox`, not `pve`.

---

## 0. Latest verified state — Phase 2 and voice pipeline

### Documentation/config cleanup — 2026-06-29

- Cleaned active router/config/documentation comments so they describe the
  current CT 111/CT 114, NVR, TLS-first MQTT and managed-switch planning state
  rather than VM-era, CCTV-era or pre-TLS correction history.
- Aligned `configs/frigate/config.yml` with the current migration-safe baseline:
  `mqtt.enabled: false` and `cameras: {}` until real camera models, RTSP paths,
  credentials and MQTT material are available.
- Moved the obsolete repository bootstrapper from
  `scripts/setup/GitHub.ps1` to
  `_archive/2026-06-29-stale-bootstrap/GitHub.ps1`; it created the old
  `home-automation-safety` / 4-VLAN / CCTV-era layout and should not be run.
- Updated active MQTT examples to lead with TLS port `8883`; plaintext `1883`
  remains documented only as a deliberate temporary bootstrap/recovery
  exception.

Phase 2 is complete. The apparent Phase 2b "Wyoming integrations not loading"
blocker was a misdiagnosis and is now resolved.

### Actual fault

The Wyoming integrations were loaded and working. Their `stt`, `tts`, and
`wake_word` provider entities reporting `unknown` is normal; they are callable
providers, not sensors with a persistent value. HA had already sent real audio
to Whisper, whose logs contained successful transcriptions from the user's
tests.

Both Assist pipelines still referenced the deleted/orphaned entity
`tts.piper`. Re-adding the Wyoming Piper integration had created the live entity
as `tts.piper_2`. This stale pipeline reference caused the broken Assist UI and
TTS path.

### Repair and verification

- Backed up HA's pipeline store as
  `/config/.storage/assist_pipeline.pipelines.bak-20260619-235654`.
- Updated both pipelines through HA's supported WebSocket API to use
  `tts.piper_2` with `en_GB-alba-medium`.
- Preserved the valid wake words advertised by OpenWakeWord:
  - `Home`: `hey_mycroft`
  - `Overwatch`: `hey_jarvis`
- Confirmed all Wyoming protocol descriptors directly on VM 104:
  Piper 2.2.2, Faster Whisper 3.1.0 (`base-int8`), and OpenWakeWord 2.1.0.
- Confirmed the cached Piper `en_GB-alba-medium` model exists.
- Built-in HA conversation returned the correct current time.
- legacy local LLM runtime conversation returned a correct response using
  `llama3.1-8k:latest`.
- HA-native Assist runs completed through `intent-start` -> `intent-end` ->
  `tts-start` (`tts.piper_2`) -> `tts-end` -> `run-end`.
- Fetched generated TTS proxies successfully as valid `audio/mpeg` files
  (20–24 KB).
- `ha core check` and `docker compose config -q` both pass.

### Measured CPU baseline

The remaining limitation is latency, not correctness. A fresh legacy local LLM runtime voice
conversation takes roughly 52–54 seconds even with the model resident. HA sends
about 1,637 prompt/tool-schema tokens; CPU prompt evaluation is about 24 tokens/s,
followed by a tool-call round trip. The model itself is loaded indefinitely at
5.6 GB with a 4096 context for HA. This is the baseline the GPU migration must
beat. Removing HA tool exposure (`llm_hass_api: assist`) would reduce latency,
but changes capability and was not done.

### HA access correction

SSH to HA now works through the official `Terminal & SSH` add-on (`core_ssh`)
using workstation key `id_ed25519_codex_ha`. The failed Advanced SSH add-on is
stopped. `/config` is readable/writable and the `ha` CLI is available.

The user-visible HA app should be tested once after this repair. Infrastructure
validation is complete; do not revive the discarded "Wyoming is not loading"
hypothesis unless new evidence contradicts the successful pipeline traces.

### Overwatch web search — added 2026-06-20

Open WebUI's SearXNG settings do not apply to HA's legacy local LLM runtime conversation agent;
HA talks directly to legacy local LLM runtime. Added the local custom integration
`searxng_llm` to expose a bounded, read-only `web_search` LLM tool through HA's
native multi-API mechanism. Source is tracked under
`configs/home-assistant/custom_components/searxng_llm/` and deployed to
`/config/custom_components/searxng_llm/`.

Configuration points to `http://192.168.20.102:8087`, returns at most three
title/URL/snippet results, caps field lengths, and has a 15-second timeout. The
legacy local LLM runtime conversation subentry now selects both `assist` and `searxng_search`.
Backups were created for live `configuration.yaml` and `core.config_entries`
before deployment.

End-to-end tests through `conversation.legacy-local-llm_conversation` passed both with an
explicit web-search request and with the natural request "Give me two recipes
for chicken with tarragon and cream." Overwatch called SearXNG and returned
The Modern Proper and BBC Food recipes with direct source links. CPU latency was
approximately 106–123 seconds because search adds an extra LLM/tool round trip;
this is expected to be a key GPU benchmark.

---

## 1. Decision locked: Option B

Keep the Intel Meteor Lake iGPU on the Proxmox host (no PCI passthrough to a single VM). Share `/dev/dri/renderD128` into LXC containers so both Frigate and legacy local LLM runtime can use it concurrently. VMs cannot share a GPU this way; only LXCs can, because they share the host kernel.

**Migration shape:**
- VM 101 (frigate-nvr) and VM 104 (llm-host) get **stood down**, not deleted — `qm stop`, `onboot 0`, disks kept as rollback.
- New LXCs get fresh IDs (proposed **CT 111** = frigate, **CT 114** = llm-host) but reuse the same static IPs/DNS/VLAN tags (192.168.30.20 VLAN 30, 192.168.20.104 VLAN 20). Only one of each pair runs at a time, so no IP conflict.
- Docker-inside-LXC, **unprivileged** containers (privileged only if render-node access genuinely fails).
- GPU path is **benchmark-gated**: keep Vulkan/SYCL on legacy local LLM runtime only if it beats a tuned CPU baseline on both speed and output correctness (known legacy local LLM runtime-Vulkan gibberish bug on some Intel iGPUs). **IPEX-LLM is struck from the plan** — archived by Intel Jan 2026.
- Frigate's GPU benefit (VAAPI/OpenVINO) is real but can't be fully validated until cameras are live.
- NPU (`/dev/accel/accel0`) is out of scope.

---

## 2. Phase status

| Phase | What | Status |
|---|---|---|
| 0 | Swap/memory baseline | ✅ Done |
| 1 | SearXNG JSON fix + Open WebUI web search wiring | ✅ **Done** (this session) |
| 2 | Tune legacy local LLM runtime (keep-alive, model consolidation, context/threads) | ✅ Done |
| 2b | Voice pipeline validation and stale TTS repair | ✅ Done |
| 3 | Stand down VM 101 + VM 104 | ✅ Done; stopped, autostart disabled, snapshots retained |
| 4 | Build LXCs CT 111, CT 114 | ✅ Done |
| 5 | Wire shared Intel iGPU into both | ✅ Done; render + card nodes mapped |
| 6 | Rebuild in-guest firewall (UFW + DOCKER-USER) under unprivileged LXC | ✅ Done |
| 7 | GPU acceleration (Frigate OpenVINO/VAAPI, legacy local LLM runtime Vulkan) | ✅ Done |
| 8 | Benchmark GPU vs tuned-CPU baseline | ✅ Initial benchmark done; cold 3-token response 9s |
| 9 | Commit (delete VMs) or roll back | ⏸ Burn-in period; VMs deliberately retained |

---

## 2.1 Migration completion — 2026-06-20

The production cutover is complete and rollback remains available.

- **CT 111 (`frigate-nvr`)** now owns `192.168.30.20`, VLAN 30, with 2 vCPU,
  4 GiB RAM and a 32 GiB root disk. Frigate 0.17.1 runs with the bundled
  `ssdlite_mobilenet_v2` model on the shared Intel iGPU via OpenVINO. VA-API is
  configured globally for camera decoding. The migration-safe live config has
  MQTT and cameras disabled until real credentials, CA material and stream URLs
  are provisioned; this avoids bringing placeholder cameras into production.
- **CT 114 (`llm-host`)** now owns `192.168.20.104`, VLAN 20, with 4 vCPU,
  10 GiB RAM and a 100 GiB root disk. legacy local LLM runtime detected the Meteor Lake iGPU via
  Vulkan only after adding `OLLAMA_IGPU_ENABLE=1`; a live model load then
  offloaded **33/33 layers**, the KV cache and compute buffers to Vulkan.
- Both unprivileged LXCs receive `/dev/dri/renderD128` and `/dev/dri/card1`
  through Proxmox device passthrough. Both workloads remained healthy while
  running concurrently and after simultaneous cold reboots.
- VM 101 and VM 104 are stopped with `onboot=0`. Snapshots named
  `pre-lxc-migration-20260620` and config backups under
  `/root/migration-backups/20260620-pre-lxc/` remain the rollback points. Do not
  delete the VMs until the burn-in period is accepted.
- The final VM 104 data sync was performed with both source and destination
  stacks stopped. The one-time migration SSH key was removed from CT 114 and
  from the stopped VM using QEMU Guest Agent while its NIC was link-down.

### Validation evidence

- Frigate container healthy; `frigate.detector:ov` remains alive; UI and API
  return HTTP 200 after reboot.
- legacy local LLM runtime logs identify `Vulkan0` as `Intel(R) Graphics (MTL)` and show all model
  layers offloaded. A cold `llama3.1-8k` request returned `GPU OK` in 9 seconds;
  the prior HA voice CPU baseline was 52–54 seconds.
- Open WebUI is healthy and retained its data. HA can reach legacy local LLM runtime, Piper,
  Whisper, OpenWakeWord and SearXNG from `192.168.20.101`.
- Current `wyoming-whisper:latest` needs the `openai/whisper-tiny` tokenizer even
  with `base-int8`. VLAN 20 has no internet egress, so the tokenizer is cached
  persistently under `whisper/huggingface`, with `HF_HOME=/data/huggingface` and
  `HF_HUB_OFFLINE=1`. This was verified through another CT 114 reboot.
- CT 114's persistent DOCKER-USER policy gates ports retired-api-port, 3002, 10200, 10300
  and 10400 by source. This corrects the old VM's missing 10400 protection.

Canonical deployed compose definitions now live at
`configs/local-ai/docker-compose.yml` and `configs/frigate/docker-compose.yml`.

---

## 3. What's been verified/done — Phase 0 & earlier Phase 1 work (prior session, unchanged)

**Phase 0:**
- Root cause of 5.2GiB swap usage was `vm.swappiness=60` (Proxmox default), not real memory pressure (host had ~10Gi free out of 30Gi).
- **Fixed:** `vm.swappiness=10` set live and persisted to `/etc/sysctl.conf` on Proxmox host. Swap drains gradually, not instantly — don't be alarmed if `swapon --show` still shows old usage for a while.
- **Resolved 2026-06-20:** the stale pre-LXC `vm-configs.conf` was archived and
  replaced by `configs/proxmox/guest-configs.md`.
- ZFS ARC confirmed negligible — not used for storage, not a factor.
- VM 102 ballooning not explicitly `0` like the others — cosmetic, fix during doc pass.
- **GPU device facts confirmed on host** (needed for Phase 5 LXC cgroup mapping):
  - `/dev/dri/renderD128` → char device `226:128`, group `render`, **GID 993**
  - `/dev/dri/card1` → char device `226:1`, group `video`, **GID 44**
  - iGPU PCI address: `00:02.0` (Intel Meteor Lake-P)
- IOMMU / `intel_iommu=on` is **not required** for this approach (only needed for the old PCI-passthrough plan). Consider deprioritizing that TODO item.

**Phase 1 (initial pass, prior session):**
- Root cause confirmed: `/opt/stacks/searxng/searxng/settings.yml` only had `formats: [html]`, causing Open WebUI's JSON-format search requests to 403.
- Added `json` to `formats`, restarted the `searxng` container via `docker compose restart` on docker-host (192.168.20.102).
- `curl http://localhost:8087/search?q=test&format=json` → HTTP 200 — **but this was localhost-only and did not prove cross-host reachability.** See section 4 below; this gap was found and fixed this session.
- `limiter: false` was already set — no rate-limit concern.

---

## 4. Phase 1 — completed this session

**Goal:** wire Open WebUI (VM 104, llm-host) to SearXNG's JSON search endpoint and raise the search-model context window.

### 4.1 Open WebUI config (VM 104)
Container: `open-webui`, compose file `/opt/stacks/local-ai/docker-compose.yml`.
Backed up to `docker-compose.yml.bak-20260619-152203` before editing.
Added to the `open-webui` service's `environment:` block:
```yaml
- ENABLE_RAG_WEB_SEARCH=true
- RAG_WEB_SEARCH_ENGINE=searxng
- SEARXNG_QUERY_URL=http://192.168.20.102:8087/search?q=<query>&format=json
- RAG_WEB_SEARCH_RESULT_COUNT=3
- RAG_WEB_SEARCH_CONCURRENT_REQUESTS=10
```
Applied via `docker compose up -d open-webui` (clean recreate, came up healthy). Env vars confirmed live via `docker exec open-webui env | grep RAG_WEB`.

### 4.2 Firewall gap found and fixed (the real work this session)
The prior session's `curl localhost:8087` test never actually exercised the cross-host path. Testing for real from VM 104 → docker-host:8087 returned `curl: (28) Connection timed out` — confirmed via `-v` as a silent drop, not a closed port.

**Two layers had to be fixed, because Docker-published ports on docker-host are gated by `DOCKER-USER` iptables rules sitting in front of (independent of) UFW:**

1. **UFW** — added `ufw allow from 192.168.20.0/24 to any port 8087 proto tcp comment 'Automation to SearXNG'`. Necessary but not sufficient on its own.
2. **DOCKER-USER chain**, managed by `/usr/local/sbin/docker-host-firewall.sh` (systemd unit `docker-host-firewall.service`, `oneshot`, `RemainAfterExit=yes`, runs `iptables -F DOCKER-USER` then rebuilds the whole chain from scratch on every start/restart — **this is the actual source of truth, not live iptables state**). Original script had ports 8087 (SearXNG) and 8088 (whoogle) sharing one `for port in 8087 8088; do ... done` loop with only management/LAN/monitoring/Tailscale sources — no VLAN 20.

   **Edited the script** (not live iptables) to split 8087 and 8088 into separate blocks, adding `192.168.20.0/24` as an allowed source for **8087 only** (whoogle/8088 deliberately left untouched — nobody asked for VLAN 20 access to it).

   First attempt at this fix appended the new VLAN-20 RETURN rule *after* the loop's existing unconditional DROP for port 8087 — dead code, since iptables evaluates DOCKER-USER top-to-bottom and the DROP at rule 12 caught everything before the RETURN at rule 18 was ever reached. **Caught by re-testing rather than assuming success** — re-verify after every DOCKER-USER change, line numbers via `iptables -L DOCKER-USER -n --line-numbers`, never trust "the command ran" as proof. Corrected by giving 8087 its own clean RETURN-then-DROP block, same style as the file's other per-service blocks (ntfy, Immich, Dozzle, AdGuard).

   Applied via `systemctl restart docker-host-firewall.service` (re-flushes and rebuilds the whole chain — safe, idempotent, confirmed `active` after).

   Two backups left in place on docker-host for rollback: `/usr/local/sbin/docker-host-firewall.sh.bak-20260619-163717` (UFW-only attempt era, irrelevant) and `...-163839-fix2` (pre-correct-fix state, this is the meaningful rollback point if 8087 access ever needs to be reverted).

**End-to-end verified:** `curl http://192.168.20.102:8087/search?q=test&format=json` from VM 104 → **HTTP 200**, full real JSON result set returned. This is the first genuine proof the cross-host path works.

### 4.3 Search-model context window
Two legacy local LLM runtime models exist on VM 104: `llama3.1:8b-instruct-q4_K_M` (general purpose, no custom `num_ctx`, defaults low) and `home-assistant-llm:latest` (custom Modelfile, `num_ctx 4096`, tuned system prompt for HA voice/Assist pipeline — **deliberately left untouched**, not a bug).

User confirmed: bump context on the **general-purpose model**, not the HA one.

Created new tagged model **`llama3.1-search:latest`** (`FROM llama3.1:8b-instruct-q4_K_M` + `PARAMETER num_ctx 16384`) via `legacy-local-llm create` inside the `legacy-local-llm` container. Verified live: `legacy-local-llm show llama3.1-search:latest --parameters` → `num_ctx 16384`. Base `llama3.1:8b-instruct-q4_K_M` tag left untouched as a clean baseline.

### 4.4 Manual step still required (UI-only, not scriptable blind)
**User needs to open Open WebUI and select `llama3.1-search` as the active model** when they want web-search-augmented chat. Open WebUI has no single "default search model" env var — model choice is per-chat in the UI dropdown.

### 4.5 Access info
**Open WebUI URL:** `http://192.168.20.104:3002` (port mapping `3002:8080` in compose).
Reachability from the user's workstation/LAN was **not verified this session** — VM 104's own firewall (if any) was not checked, only docker-host's. If the user reports it's unreachable, check VM 104 for a UFW/firewall config separate from the docker-host-firewall.sh pattern (VM 104 may not have an equivalent script at all — untested).

---

## 5. Correction to prior handoff — SSH key for VM 104

**Prior handoff guessed `id_ed25519_codex_ha` would work for VM 104 (untested). This was wrong.**

**Confirmed working key for VM 104 (llm-host, 192.168.20.104): `proxmox_admin_ed25519`**, the same key used for the Proxmox host itself — not the docker-host key. Likely means VM 104 was provisioned/managed via the same admin path as the hypervisor, distinct from docker-host's separate automation key.

```powershell
& 'C:\Program Files\Git\usr\bin\ssh.exe' -i "$env:USERPROFILE\.ssh\proxmox_admin_ed25519" -o StrictHostKeyChecking=accept-new -o BatchMode=yes root@192.168.20.104 "<command>"
```
SCP equivalent (same key):
```powershell
& 'C:\Program Files\Git\usr\bin\scp.exe' -i "$env:USERPROFILE\.ssh\proxmox_admin_ed25519" -o StrictHostKeyChecking=accept-new "E:/home-automation-project/<file>" root@192.168.20.104:/tmp/<file>
```

**Also discovered:** `~/.ssh/config` on the workstation defines host aliases `proxmox` and `router` (the latter using a *third* key location entirely, outside `~/.ssh`: `E:/home-automation-project/main/tools/router-deploy/keys/router_deploy`). No alias exists yet for docker-host or llm-host — worth adding both to `~/.ssh/config` during the doc-rewrite pass to stop re-deriving the right key/host pairing each session.

**docker-host (192.168.20.102) key is unchanged from prior handoff:** `id_ed25519_codex_ha`, confirmed working again this session.

---

## 6. Access — established pattern (carried forward, still correct)

Run everything from the user's Windows workstation via Desktop Commander, shell `powershell.exe` (actually resolves to `pwsh.exe` / PowerShell 7 in practice this session — both fine).

### ⚠️ Don't do this (cost real time, prior session)
- **Don't use PowerShell's native `ssh`/`scp`** for anything with multi-line content or complex quoting — it mangles heredocs and quote escaping badly and silently produces garbled remote files.
- **Don't write multi-line scripts inline through `qm guest exec`** (Proxmox guest-agent exec) — JSON wrapping and shell layering corrupts heredocs/quotes. Guest-agent exec is fine for simple one-liners only.
- **Don't route VM access through the Proxmox host as a jump host** — the Proxmox host's own `id_rsa` is NOT authorized on docker-host or (newly confirmed) not the mechanism used for llm-host either; llm-host uses its own direct key (`proxmox_admin_ed25519`, see section 5). Go direct from the Windows workstation in all cases.
- **New this session: don't assume "command ran without error" means "the change took effect."** The dead-code DOCKER-USER rule (section 4.2) executed cleanly, returned no errors, and was still wrong. Always re-verify the actual behavior (curl test, `iptables -L --line-numbers`, etc.) after any firewall/network change — never trust exit-code-zero alone for anything touching iptables ordering.
- **MCP/Desktop Commander can hang.** `interact_with_process` hung twice in a row (4-min timeouts, dead PID) at the start of this session before a manual restart of the Desktop Commander MCP server fixed it. If this recurs: don't keep retrying the same PID — start a fresh `start_process` shell after confirming/asking the user to restart the MCP server.

### ✅ Working pattern (use this)
1. Write any script content via `Filesystem:write_file` to `E:\home-automation-project\<scriptname>.sh` (or `.Modelfile`, etc.) — avoids all shell-quoting issues entirely.
2. SCP it to the target host using **Git's bundled OpenSSH** (`C:\Program Files\Git\usr\bin\ssh.exe` / `scp.exe`), not the Windows-native one.
3. SSH in and execute it as a file (`bash /tmp/<scriptname>.sh`), never inline.
4. For anything modifying firewall/iptables state: re-verify with an actual cross-host test afterward, not just "service active" / "command succeeded."
5. Clean up `/tmp/*.sh` on remote hosts after use; leave `.bak-*` files in place for rollback (don't delete those).

### Verified working commands

**Proxmox host** (192.168.10.10, node `proxmox`) — key auth only, password auth disabled:
```powershell
& 'C:\Program Files\Git\usr\bin\ssh.exe' -i "$env:USERPROFILE\.ssh\proxmox_admin_ed25519" -o StrictHostKeyChecking=accept-new -o BatchMode=yes root@192.168.10.10 "<command>"
```

**docker-host** (192.168.20.102) — `id_ed25519_codex_ha`, direct from workstation:
```powershell
& 'C:\Program Files\Git\usr\bin\ssh.exe' -i "$env:USERPROFILE\.ssh\id_ed25519_codex_ha" -o StrictHostKeyChecking=accept-new -o BatchMode=yes root@192.168.20.102 "<command>"
```

**llm-host** (VM 104, 192.168.20.104) — **`proxmox_admin_ed25519`, confirmed this session** (corrects prior handoff guess):
```powershell
& 'C:\Program Files\Git\usr\bin\ssh.exe' -i "$env:USERPROFILE\.ssh\proxmox_admin_ed25519" -o StrictHostKeyChecking=accept-new -o BatchMode=yes root@192.168.20.104 "<command>"
```

**Proxmox API** (https://192.168.10.10:8006) — use the `root@pam`
credential stored in the password manager. Never record the password in the
repository. Prefer direct key-based SSH for routine administration.

**VM 100 (Home Assistant):** no guest agent, not reachable this session either. Not required for phases 0–2. Will matter for HA Assist pipeline config — likely a UI task, not SSH.

---

## 7. Documentation reconciliation

The canonical current-state reference, shared-iGPU decision, LXC setup guides,
service/access matrices, monitoring roadmap, architecture diagram and task list
were reconciled on 2026-06-20. Superseded VM-era material is preserved under
`_archive/2026-06-20-pre-lxc-and-handoffs/`.

**New items to fold in from this session:**
- `~/.ssh/config` on the workstation: add `Host docker-host` and `Host llm-host` aliases (with correct `IdentityFile` each) to stop re-deriving key/host pairing every session.
- Document the `docker-host-firewall.sh` / `docker-host-firewall.service` pattern properly — it's load-bearing (governs every Docker-published port on docker-host) and currently exists only as an undocumented script the prior session didn't even know existed. Should get its own short doc or a clear section in `03-docker-host-service-policy.md`, including the "DOCKER-USER sits in front of UFW for Docker-published ports" gotcha explicitly, since it cost real debugging time twice (this session and likely future ones if undocumented).
- Note whether VM 104 / llm-host has any equivalent firewall script of its own — unknown, not checked this session (see section 4.5).

Wiki syncs only after canonical docs are updated.

---

## 8. Immediate next step on resume

Phase 2 and infrastructure-level voice validation are complete. Ask the user to
perform one HA app smoke test; the provider entities continuing to display
`unknown` is not a failure signal.

After that confirmation, move to **Phase 3** using the rollback-preserving plan:
stand down VM 101 and VM 104 without deleting their disks, then build CT 111 and
CT 114. Preserve the measured 52–54 second CPU LLM voice latency as the baseline
for Phase 8 GPU comparison.

---

## 9. Model guidance

Sonnet for step-by-step execution work. Switch to Opus only if something gets genuinely stuck — e.g. unprivileged LXC refusing GPU access, Docker iptables misbehaving inside the LXC namespace (note: this session's DOCKER-USER debugging on a plain VM was already non-trivial; the same class of problem inside an LXC's network namespace in Phase 6 is flagged as a likely Opus-worthy snag), or the legacy local LLM runtime Vulkan gibberish-output bug showing up during Phase 7/8 benchmarking.
