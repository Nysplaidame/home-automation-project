# Handoff 2026-11-11: faster Overwatch LLM replies on the Arc iGPU

Goal: cut the LLM share of Overwatch voice latency (currently ~4.5 s for a trivial question,
~20-27 s for a web search) without losing Home Assistant tool-calling quality.

Read first: `docs/reference/current-live-state.md` (CT 114 / Voice sections),
`HANDOFF-2026-06-19-igpu-lxc-migration.md` (how the iGPU got into the LXCs),
`configs/local-ai/docker-compose.yml`, `configs/home-assistant/custom_components/llamacpp_conversation/__init__.py`.

## Key finding: the iGPU is already in use

The original request was "use the integrated GPU". It already is:

- Proxmox host: Intel Core Ultra 5 125H, Meteor Lake Arc iGPU `8086:7d55`, 62 GiB RAM shared
  with the GPU, kernel `7.0.0-3-pve`, PVE 9.1.9.
- CT 114 `llm-host` (unprivileged, 6 cores, 28 GiB) has `/dev/dri/renderD128` (gid 993) and
  `/dev/dri/card0` (gid 44) passed through. **CT 111 Frigate has the same two devices** and uses
  the GPU for OpenVINO detection (`ssdlite_mobilenet_v2`) and `preset-vaapi` decode.
- `llama-cpp` container: `ghcr.io/ggml-org/llama.cpp:server-vulkan`, model
  `/models/Qwen3-14B-128K-Q4_K_M.gguf` (9.0 GB), `--n-gpu-layers 99`, `--ctx-size 65536`,
  `--cache-type-k/v q8_0`, `--parallel 1`, `--threads 4`, `--reasoning off`, `--jinja`,
  alias `home-assistant-llm`. Log: `Vulkan0 : Intel(R) Arc(tm) Graphics (MTL) (47836 MiB)`.

Measured on that setup (llama.cpp `print_timing`, 2026-11):

| Metric | Value |
|---|---|
| Generation | **~5 tokens/s** (197 ms/token) |
| Prompt processing | 38-78 tokens/s |
| Voice run "What time is it?" | STT end 3.1 s -> LLM 4.5 s -> TTS ~1-2 s |
| Web search reply (tool call + SearXNG + one-sentence summary) | 21-27 s |

Interpretation: token generation on an iGPU is **memory-bandwidth bound**. Every token streams
the whole 9 GB of weights from shared DDR5, so ~5 tok/s is near the ceiling for a dense 14B. The
real levers are fewer bytes read per token (smaller or MoE model) and backend efficiency, not
"turning the GPU on".

## Plan

Do steps in order; benchmark each against the baseline before changing anything live.

### 0. Baseline harness (do first)

- Write `tools/llm-bench/` (or scratch) with a fixed prompt set sent to
  `http://192.168.20.104:8081/v1/chat/completions`, recording `timings` (prompt tok/s, gen tok/s)
  plus wall time. Include: a short chat answer, a HA tool-call turn (use the real tool schema
  from a `conversation/process` debug run), and the web-search summary prompt from
  `_async_summarize_web_search`.
- End-to-end check through HA with the token in `K:\Documents\Obsidian\home-automation-project\.ha-token`
  (git-ignored): websocket `conversation/process` with `agent_id`
  `conversation.llama_cpp_conversation` and `assist_pipeline/pipeline_debug/*` for stage timings
  (Overwatch pipeline id `01kvgsqj25mjtvtxqz5vza719q`).
- Record Frigate detector inference speed before and after (Frigate UI / `api/stats`), since the
  GPU is shared.

### 1. Model candidates (largest expected gain)

Run each as a **second, temporary** llama.cpp container on a spare port (e.g. 8091, bound to
127.0.0.1 inside CT 114) so production 8081 is untouched. CT 114 has **no internet egress**:
download GGUFs on the desktop and push them (`ssh root@192.168.10.10` -> `pct push 114 ...`), as
was done for the Parakeet model.

| Candidate | Why | Expected gen speed |
|---|---|---|
| **Qwen3-30B-A3B** (MoE, ~3B active), Q4_K_M ~18 GB | Bytes/token like a 3B model, quality near 14B+; strong tool calling | ~3-4x current |
| Qwen3-8B Q4_K_M (~5 GB) | Simple dense step down | ~1.8x |
| Qwen3-4B-Instruct Q4_K_M (~2.5 GB) | Fastest; check tool-call reliability | ~3x+ |

Memory check: CT 114 is 28 GiB, llama-cpp currently uses ~14 GiB; host has ~21 GiB available.
A 30B-A3B Q4 plus a smaller KV cache (drop `--ctx-size` to 16384-32768; HA prompts are a few
thousand tokens) should fit, but **verify the CT limit and do not starve Frigate (CT 111) or the
host**. Run only one big model at a time while testing.

Acceptance: correct tool calls on the HA prompt set (device control, Grocy add/list, Mealie,
SearXNG search), with no invented entities, before considering a switch.

### 2. Backend: Vulkan vs SYCL

- Try `ghcr.io/ggml-org/llama.cpp:server-intel` (SYCL/oneAPI) with the chosen model, same flags.
  SYCL is often faster than Vulkan on Intel Arc for prompt processing; generation is still
  bandwidth bound. Keep whichever wins. Check image tag age and pin by digest like the other stacks.
- Keep `--n-gpu-layers 99`. Try `--flash-attn on` if the backend supports it.

### 3. Cheap wins (independent of the above; owner approval needed for 3a)

- 3a. Overwatch pipeline: **Prefer handling commands locally** (`prefer_local_intents`) so time,
  on/off, sensors and timers skip the LLM. The owner wanted Overwatch-style wording, so pair it with
  `custom_sentences/en/` response overrides (cold/authoritative tone like the voice dataset).
  This was offered on 2026-11-11 but **not yet approved**.
- 3b. The component's direct path for obvious searches: route "search the web for ..." straight to
  the SearXNG tool without the first LLM turn (saves one LLM round in `_async_handle_chat_log`).

### 4. Switch live (only after owner approval)

- Back up `/opt/stacks/local-ai/docker-compose.yml` (`.bak-YYYYMMDD-...`), change image/model/flags,
  `docker compose up -d --no-deps llama-cpp`. Keep the alias `home-assistant-llm` so HA and Open
  WebUI need no changes. Keep the old GGUF on disk for rollback.
- Update `configs/local-ai/docker-compose.yml`, `docs/reference/current-live-state.md`, `TO-DO.md`,
  and the wiki entity `wiki/pages/entities/llm-host.md` afterwards.

## Constraints and gotchas

- Do not restart Frigate (CT 111) or other CT 114 services without need; restart only `llama-cpp`.
- The HA custom component lives in the repo at
  `configs/home-assistant/custom_components/llamacpp_conversation/` and is deployed by copying to
  `\\192.168.20.101\config\custom_components\...`. HA 2026.11 removed `voluptuous_openapi`, now
  replaced with a `probatio.to_openapi` fallback (commit `4c17cd6`). Web-search replies are one-sentence
  LLM summaries (commit `2d6674e`), with `max_tokens` 60 and a 30 s timeout.
- Access: Proxmox `ssh root@192.168.10.10`, CT 114 via `pct exec 114 -- ...`; docker-host
  `ssh root@192.168.20.102`; router `ssh home-router-lan` (key `~/.ssh/home_router_desktop_ed25519`,
  **never use a password**).
- Voice chain as of this handoff:
  - Voice PE `192.168.50.108`, wake word "Okay Nabu" (Overwatch wake word still a TO-DO).
  - Parakeet STT on 10300.
  - Overwatch pipeline -> `conversation.llama_cpp_conversation`.
  - Metrocop TTS on 10201.
  - Audio goes via `ha-media-proxy` (`http://ha-media.home.arpa:8124`, HA `internal_url`).

## Open owner decisions

1. Approve trial downloads (~18 GB for Qwen3-30B-A3B, plus optional 8B/4B).
2. Approve switching the live model/backend after the benchmark.
3. Approve 3a (local intents + Overwatch-style responses) and 3b.
