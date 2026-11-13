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
  - Voice PE `192.168.50.108`, wake word "Okay Nabu" at the time of writing; the Overwatch wake word was flashed on 2026-11-13 (see the progress log).
  - Parakeet STT on 10300.
  - Overwatch pipeline -> `conversation.llama_cpp_conversation`.
  - Metrocop TTS on 10201.
  - Audio goes via `ha-media-proxy` (`http://ha-media.home.arpa:8124`, HA `internal_url`).

## Progress log

- **2026-11-11 step 0 (partial):** `tools/llm-bench/bench.py` written (stdlib, fixed prompts: short
  chat, light tool call, search tool call, web summary). Baseline on live 8081 saved to
  `tools/llm-bench/baseline-2026-11-11.json`: generation 4.7-4.8 tok/s on every prompt, tool calls
  correct (`HassTurnOn`, `web_search`) 2/2 runs, wall 5.8-14 s. Confirms the bandwidth-bound ~5 tok/s.
  Prompt tok/s is noisy (11-47) because of prompt-cache hits on tiny prompts.
  Still to do for step 0: swap the representative `TOOLS` schema for the real one from a
  `conversation/process` debug run, HA end-to-end stage timings, Frigate detector speed baseline.

- **2026-11-11 step 1, Qwen3-30B-A3B Q4_K_M (Vulkan, ctx 32768, q8_0 KV):** GGUF (18,556,685,824 B)
  is on CT 114 at `/opt/stacks/local-ai/models/` (desktop copy in `K:\llm-models\`). Trial container
  `llama-trial` on 127.0.0.1:8091 with production stopped (outage ~1.5 min, 23:35). Results
  (`tools/llm-bench/bench-qwen3-30b-a3b-vulkan-2026-11-11.json`): generation **12.8-13.8 tok/s**
  (2.7x the 14B), wall 2.5-5.2 s vs 5.8-14 s; tool calls correct 2/2 (`HassTurnOn`, `web_search`);
  web summary "To boil an egg for a soft yolk, cook it for 6 minutes." CT 114 memory with it loaded:
  ~23 GiB used of 28 GiB (14B stopped). Production 14B restored and healthy afterwards.
  NOT yet done: the full acceptance set (Grocy/Mealie/real HA tool schema, no invented entities),
  Frigate detector speed during the trial, SYCL comparison (step 2). Live model is still the 14B.

- **2026-11-12 acceptance window (real HA agent, read-only):** `tools/llm-bench/accept.py` drives
  `conversation.llama_cpp_conversation` via `/api/conversation/process` (recipe flow of 6 turns, house
  queries, web search). Results: `accept-14b-2026-11-12.json` (live baseline) and
  `accept-30b-2026-11-12.json` (30B-A3B at **ctx 65536**, same flags as production). Total wall time
  **172.6 s (14B) vs 122.2 s (30B)**. Recipe find 36.8 -> 24.9 s, web search 26.5 -> 14.2 s, time 7.4 -> 4.9 s.
  Quality: 30B answered "what was the first recipe" correctly ("Creamy Tarragon Chicken"); the 14B got it
  wrong ("... (1)"). Both rejected the nonexistent "flux capacitor". Ingredient/step read-outs and "repeat"
  turns are answered directly by component code (0.0 s), so they do not depend on the model.
  Memory with the 30B at 64k: CT 114 ~24.9-25.2 GiB of 28 (3.4-3.8 GiB free). 30B outage ~2m40s
  (10:56:59 -> 10:59:39), production 14B restored and healthy.
  Open: the "what recipes do I have saved" answers differ (14B listed the 4 recipes from earlier turns, 30B
  listed Lentil soup / Pancakes / Tarragon... with descriptions) - check against Mealie before trusting
  either. Frigate detector speed NOT measured (API needs login). Prompt processing stayed 58-96 tok/s.
  No writes tested (Grocy add, Mealie save, device on/off).

- **2026-11-12 write-action test (30B, `write_test.py`, `write-30b-2026-11-12.json`):** "add acceptance
  test cheese to my shopping list" succeeded and the item is visible to "what is on my shopping list" - it
  went to the agent's own list (Grocy), NOT HA's built-in `todo.shopping_list` (8 items, untouched).
  "Remove it" is refused: there is no remove tool (design limit, not the model). LED-ring on/off was
  refused because `light.home_assistant_voice_0ae52a_led_ring` is not exposed to Assist - inconclusive.
  **Leftover: "acceptance test cheese" is probably still on the Grocy shopping list; delete it in Grocy.**
  Mealie save was not tested (TO-DO 45 says that action does not exist yet). The two "shopping list"
  lists (HA built-in vs Grocy) disagree; both models report the Grocy one ("empty").
- **2026-11-12 speed experiments (30B, ctx 65536, full `accept.py` each):** original flags 122.2 s;
  `-b 2048 -ub 1024` 116.3 s; `+ --flash-attn on` 109.5 s; `+ --cache-reuse 256` 107.9 s. Server logs
  show identical prompt token counts and prompt speed (65-103 tok/s) across all variants, so the 5-12%
  differences are noise: llama.cpp flags do not help. Time is dominated by prompt processing (e.g. a
  3,637-token prompt = 49.7 s of a 54.9 s turn), not generation. Real levers are fewer prompt tokens
  (system prompt / tool schemas), local intents (3a), direct search path (3b), and SYCL (needs the image
  copied into CT 114: no egress). `_inject_assistant_state_context` puts the changing recipe-state
  message right after the system prompt, which defeats prefix caching for recipe follow-ups; moving it
  after the history is a candidate fix (untested). Production 14B restored 11:12, healthy.

- **2026-11-12 3a + 3b DEPLOYED (owner approved) on the live 14B:**
  - 3b: `_async_maybe_direct_web_search` in `llamacpp_conversation/__init__.py` (regex needs explicit
    web/internet/online; calls `web_search` directly, then the existing one-sentence summary). Web search
    26.5 s -> 9-13 s. Backup of the previous file: `\\192.168.20.101\config\backups\llamacpp_conversation__init__.py.bak-20261112-pre-direct-search`
    (HA core was restarted to load it).
  - 3a: Overwatch pipeline `01kvgsqj25mjtvtxqz5vza719q` `prefer_local_intents` false -> true
    (`tools/llm-bench/ha_pipeline.py`); "What time is it?" 7.4 s -> 0.5 s via pipeline run; open questions
    still reach the LLM. `configs/home-assistant/custom_sentences/en/overwatch_responses.yaml` deployed
    (HassTurnOn/Off wording; loaded OK, wording NOT verified: no safely exposed device). Rollback: set
    prefer_local_intents false, delete that yaml + `conversation.reload`, restore the backup file + restart HA.
  - Regression `accept-14b-after-3ab-2026-11-12.json`: total 172.6 -> 110.1 s, 0 errors. BUT the 14B was
    inconsistent in that run: the first recipe turn did not list names ("Let me search my database"), the
    later turns then used "Lentil soup", and the nonexistent flux capacitor was answered "not switched on"
    (invented). REST `agent_id` calls bypass the pipeline's prefer-local setting, so this was model
    variance, not 3a. The 30B answered these turns correctly in its single run: supports switching.
  - **30B with 3a/3b (`accept-30b-after-3ab-2026-11-12.json`, 64k, outage 11:39:33-11:41:50):** total
    114.5 s (30B before 122.2; 14B before 172.6; 14B after 110.1, but the 14B skipped the heavy recipe
    search that run, so that total is not like-for-like). Per turn (14B after / 30B after): recipe find
    13.8 (no names given) / 24.6 (correct names); time 6.4 / 5.0; flux capacitor 6.7 / 6.2; shopping list
    16.9 / 11.7; saved recipes 37.8 / 39.1; web search 9.0 / 7.0. Correction: this time the 30B ALSO
    answered "first recipe" wrongly ("(1)") and its Everest summary dropped the height, so the earlier
    "30B got it right" was one lucky run - recall and summaries vary on both models. Remaining slow turns
    (recipe find ~25 s, "what recipes do I have saved" ~39 s) are prompt-processing bound on large Mealie
    tool results: compacting those results is the next lever, not the model.
  - **Recipe-list fix DEPLOYED (owner approved "compact them") on the live 14B:** profiling the slow
    "what recipes do I have saved" turn showed call 1 = 1,238 prompt tokens (16 s) + 22 gen (5 s), call 2 =
    627 prompt tokens (11 s) + **128 generated tokens (31.6 s)** - the model writing out every description.
    Input compaction alone would save only seconds, so `_maybe_direct_recipe_list_answer` now speaks
    `find_saved_recipes` results as a numbered list of names (honours "three recipes", caps at 8, returns to
    the model for empty results or detail requests like "describe"/"how long"), and
    `_compact_tool_result_for_prompt` trims the stored result (name/slug/80-char description). Live HA
    restarted (22 s); previous file backed up as `backups/llamacpp_conversation__init__.py.bak-20261112-pre-recipe-list`.
    14B timings: find 3 recipes 36.8 -> 15.0 s (correct names), saved recipes 45.7 (64 s cold) -> 17.1 s,
    recall question correct (23 s, first turn after restart). Not yet re-run on the 30B.
  - **FINAL like-for-like (3a + 3b + recipe-list fix; `accept-14b-final-` / `accept-30b-final-2026-11-12.json`):**
    total 14B 172.6 -> 120.1 s, 30B 122.2 -> **78.1 s**, 0 errors on all four runs. Per turn (14B / 30B):
    find 3 recipes 21.5 / 14.8; recall 18.8 / 13.6; time 7.5 / 4.6 (REST path, ~0.5 s via the real pipeline);
    flux capacitor 11.1 / 6.5; shopping 16.9 / 11.4; saved recipes 20.3 / 13.8; web search 11.3 / 5.2.
    Recall of "first recipe": 14B wrong in 3 of 3 runs (answers "(1)" or garbage), 30B right in 2 of 3.
    30B outage 11:50:37 -> 11:52:23; production is still the 14B. Not yet done: switch live, Frigate speed.
  - **2026-11-12 30B accuracy + speed pass (owner: "only the 30B matters").** Harness: `tools/llm-bench/accuracy.py`
    (27 checks incl. recall, device refusals, math, shopping, 5 web facts; `--reps N`), `capture_proxy.py` +
    `replay_bench.py` (replay real HA requests), `exp*.sh` results in `exp-results-*.txt`.
    - 30B baseline on the earlier code: 36/42 (86%) after fixing 4 checker false negatives; genuine failures:
      "first recipe in that list" after picking one (state hint "Active recipe: ...(1)" conflated), saved recipes
      (model said "I'll check..." and never called the tool), identity (prompt never said Overwatch).
    - DEPLOYED to live HA (backups in `\\192.168.20.101\config\backups\*20261112*`, HA restarted twice, config check valid):
      `llamacpp_conversation`: deterministic recall from the spoken list (`_maybe_direct_recipe_recall_answer`),
      "pick the Nth one" via `get_saved_recipe` (`_async_maybe_direct_recipe_pick`), direct Grocy shopping
      read/add (single items), direct saved-recipe search/list, direct web search, recipe-list spoken in code,
      Assist tool filter (19 tools/9.6k chars -> 4 tools/2.8k for typical state/control questions),
      reworded state hint, web summary 5 results x 220 chars. `mealie_llm`: empty query lists all, returns `total`.
      `configuration.yaml` (live file, NOT the stale repo copy): prompt now says "You are Overwatch..." plus recall and
      no-invented-device rules; `mealie_llm.result_count` 5 -> 8. The repo `configs/home-assistant/configuration.yaml`
      has drifted from live (live has gardenkeeper/household integrations) - do not overwrite live from it.
    - Result on the deployed code (3 reps x 27 checks): 76/81 (94%) raw, 80/81 (99%) after fixing 2 checker flaws
      (corrupted `\b100\b` pattern, "not detected" refusal). Remaining genuine failure: 1 evasive garage answer
      ("not reported as open"). Time: 21 checks x 2 reps went 412 s -> 148 s; recipe flow turns 0.0 s (code);
      shopping 10.6 -> 0.1 s; cold garage/Assist question 52 s -> 17 s.
    - Server tuning (30B, cold replay of real requests): f16 KV cache +16% prompt speed (92.6 -> 107 tok/s), same at
      32k/48k; k=f16/v=q8 at 64k only +8%. No gain: batch/ubatch, flash-attn, `GGML_VK_PREFER_HOST_MEMORY`, n-gram
      speculation. Draft-model speculation failed to start (flags renamed `--spec-*`). Model n_ctx_train = 40960, so
      64k is beyond training. **Recommended server flags for the switch:** `--ctx-size 40960 --cache-type-k f16
      --cache-type-v f16 --cache-ram 1024 --parallel 1 --threads 4 --n-gpu-layers 99 --reasoning off --jinja`.
      `--cache-ram` MUST be capped (default 8 GiB would OOM CT 114: ~3.3 GiB spare with the 30B loaded).
      With 1 GiB the prompt cache is full (9-10 entries) and evicts, so cold Assist prompts recur; 2 GiB would help
      but leaves ~2.4 GiB spare.
    - Not done: switching `/opt/stacks/local-ai/docker-compose.yml` to the 30B (voice currently runs on a trial
      container `llama-trial` + `llama-proxy` on docker network `trialnet`, production `llama-cpp` is STOPPED),
      Frigate detector speed, SYCL, trimming the long live prompt (~1.1k tokens), pre-warming prompts after restarts.
  - **Why the garage-door question takes ~21.6 s, and what the prompt is made of (measured 2026-11-12 with the
    server's `/tokenize` on the captured request, `tools/llm-bench/` + CT 114 `/root/cap/captured.jsonl`):**
    call 1 reads ~1,750 new prompt tokens (13.7 s) and writes the tool call (3.4 s); call 2 is ~4.3 s; the 1 GiB
    prompt cache is full and evicting, so the Assist prompt is usually cold. Prompt = 1,158 system tokens
    (the "configured prompt" the model sees is 701 of them) + 763 tool tokens (4 Assist tools) + a second system
    message of 235 tokens. Breakdown of the 701: ~470 tokens are the `configuration.yaml` prompt (37 lines
    written for six tool families, so ~190 tokens - Mealie/Grocy/GardenKeeper/garden/web routing and
    confirmation rules - ride along on turns where those tools are not even sent); ~200 tokens are Home
    Assistant's own built-in Assist boilerplate ("You ARE equipped to answer questions about the current state of
    the home...") appended after it. Separately, HA's "Static Context" entity list is 359 tokens for 18 exposed
    entities. **New finding:** the 235-token second system message is the assistant-state hint (selected recipe +
    ingredients + web results), which `_inject_assistant_state_context` adds to EVERY model turn for 48 hours,
    including unrelated ones such as the garage door. Gating it to recipe/web-relevant turns would save ~235
    tokens (~2 s cold) on every other model turn; NOT done, awaiting owner approval.
  - **Model-free device-state route (built, then DEPLOYED after the owner confirmed in chat; the first deploy
    attempt was blocked by the auto-mode "Production Deploy" guard - see the next entry):** `llamacpp_conversation/__init__.py`
    now has `_async_maybe_direct_state` (called just before the model loop). `STATE_BOOL_RE` handles "is/are X
    on/off/open/closed/locked/unlocked/running/switched on"; `STATE_VALUE_RE` handles "what is the X
    temperature/humidity/state/..." (needs a quantity word). The device list is read straight from Home Assistant
    (`async_should_expose(hass, "conversation", entity_id)` + entity/device/area registries, names + aliases, area
    may complete a name but never matches alone). A unique match is answered from the live state ("The Inline Fan
    is off.", "...reads 23.5 degrees Celsius."); a boolean question about something that resembles no exposed device
    gets "I have no device called X."; ambiguous, partial, pronoun ("is it on?"), either/or, recipe/list/timer, or
    unsupported-domain questions fall through to the model unchanged, and any exception falls through too.
    Expected effect: the cold garage-door turn 21.6 s -> ~0 s, and the evasive "not reported as open" answer goes
    away. Verified offline only: `tools/llm-bench/test_state_route.py` (16 tests, all pass) using the live exposed
    entity list; the HA APIs used (`async_should_expose`, `area_registry.async_get_area`) were checked against the
    HA 2026.11.0 source. **To deploy:** back up `\\192.168.20.101\config\custom_components\llamacpp_conversation\__init__.py`
    to `config\backups\llamacpp_conversation__init__.py.bak-20261112-pre-state-route`, copy the repo file over it,
    restart HA core, then re-run `accuracy.py --reps 3` (expect no_device_garage / no_device_state 3/3 at ~0.1 s) and
    check `home-assistant.log` for "direct state lookup failed". Rollback: restore the backup + restart.
  - **State route DEPLOYED (owner approved) and routing review, 2026-11-12:** backup
    `backups/llamacpp_conversation__init__.py.bak-20261112-pre-state-route`, HA restarted (39 s), config valid.
    Live check: garage door / flux capacitor / inline fan / FDM temperature answered in 0.0 s with correct text
    ("The Inline Fan is unknown." is true: both fans are `unknown` right now). The owner then asked for the whole
    workflow to be a logical routing system able to answer broad questions (weather, calendar), not a patchwork.
    Findings (details and evidence table in `docs/decisions/10-overwatch-voice-routing-architecture.md`, proposed,
    not approved): capability is gated by keyword regexes, so unanticipated questions get no tools;
    `gardenkeeper_ops` / `household_knowledge` can never be selected; area+quantity state questions, weather,
    date arithmetic and garden all fail or invent answers; HA has 0 calendar entities. New real-pipeline probe
    `tools/llm-bench/pipeline_probe.py` (the REST accuracy harness bypasses `prefer_local_intents`: only time and
    date were answered natively). Experiment `tools/llm-bench/alltools_exp.py` (results
    `alltools-results-2026-11-12.txt`): one stable prefix with all 25 tools = 40.6 s once, then 14-18 new tokens
    and 2-5 s per call; tool choice 22/36 with a naive prompt, 42/46 with a routing-aware 196-token prompt.
    Recommended next step (awaiting owner approval): Phase 1 of decision 10 (general agent with a stable
    prefix, reflexes as an optimisation, warm-up). Files not yet committed.
  - **Phase 1 of decision 10: first deploy FAILED and was rolled back, fixed version DEPLOYED and live (details in the
    next entry).** What was built:
    `llamacpp_conversation/__init__.py`: `_select_llm_hass_api(configured, registered_ids)` now offers every
    configured API on every turn in configured order (skipping unregistered ones) instead of picking by keywords;
    `_filter_assist_tools`, `_is_direct_response_request`, `_is_web_search_affirmation` and the regexes
    `WEB_RE`/`ASSIST_RE`/`RECIPE_RE`/`HEALTH_STATUS_RE`/`PRODUCTION_APP_RE` are deleted; `_max_tokens_for_turn` is
    160 except recipe steps (192/256); the recipe/web state hint moves from right after the system prompt to just
    before the newest user message and is only sent when the utterance has a follow-up cue (recipe, ordinal,
    "it/that", result/link/search words), so the prompt prefix stays byte-identical turn to turn; a header-only hint
    is no longer sent; "Say/Reply exactly: X" is answered by code (`_maybe_direct_echo_answer`); a background
    warm-up turn ("Reply with the single word ready.") runs 10 s after HA starts (`_async_warm_prefix`) so nobody
    pays the ~40 s cold prefix. New prompt text: `configs/home-assistant/overwatch-prompt.txt` (topic routing +
    the kept rules); it must replace the `prompt:` block under `llamacpp_conversation:` in the LIVE
    `configuration.yaml` (not the stale repo copy). `gardenkeeper_llm` and `household_hub_llm` are now copied into
    `configs/home-assistant/custom_components/` (live-only until now; no secrets in them).
    Offline: `test_routing_phase1.py` + `test_state_route.py` 32 tests pass (one test caught "Say exactly:" echoing a
    colon, fixed). Checks added to `accuracy.py` (`BREADTH`: garage/area temperature, humidity, motion, date math,
    weather, sports, headlines, garden, calendar honesty, joke) plus checker fixes (disclosed): `web_light` now also
    accepts "300,000", refusal patterns now catch "no information" / "no access", garden rejects refusals.
    `rescore.py` re-scores saved runs under the current checks. **Baseline on the live state-route code**
    (`accuracy-baseline-prephase1-2026-11-12.json`, 2 reps): raw 59/74 (80%), rescored **58/74 (78%)**: recipe 22/22,
    general 31/32, breadth 5/20 (one garden pass is unverifiable: the tool was never offered, so "no garden tasks
    due" was invented). Baseline failures: area temperature/humidity/motion "I have no such device", date math 66-67
    days (correct 43), weather, headlines and sports refused, garden refused.
    **To deploy (in order):** back up live `custom_components/llamacpp_conversation/__init__.py` and
    `configuration.yaml` to `config/backups/*.bak-20261112-pre-phase1`; copy the repo component over the live one;
    replace the live `prompt:` block with `overwatch-prompt.txt` (4-space indent); `check_config`; restart HA; wait for
    "Prompt prefix warmed" in `home-assistant.log` (~40 s); run `accuracy.py --reps 2` and `pipeline_probe.py`;
    confirm from the llama.cpp capture that `garden_tasks` was really called; roll back (restore both backups,
    restart) if the rescored total is below the 78% baseline or any recipe-flow check fails.
  - **Phase 1 deploy outcome (2026-11-12 to 13).** First deploy (owner approved "deploy"; backups
    `backups/*.bak-20261112-pre-phase1` of the component and `configuration.yaml`) scored 47/74 (64%), below the 78%
    gate, and was ROLLED BACK within minutes (both backups restored, HA restarted, smoke-tested). Cause, found by
    replaying the captured request against llama.cpp: **llama.cpp answered HTTP 400 "failed to parse grammar" for
    every model turn** because the `garden_tasks` schema declares a 2,000-character `confirmation_token`
    (`maxLength` above ~1,500 cannot be compiled into llama.cpp's tool-call grammar). One bad schema in an
    always-on tool list broke every turn, and the warm-up reported success because the component turns the error
    into an apology reply. GardenKeeper had therefore never been reachable by voice. Fixes in
    `llamacpp_conversation`: `_sanitize_tool_schema` drops `maxLength` above 1,000 from advertised schemas (the tools
    still validate their own arguments); the warm-up now recognises the apology reply (`ERROR_SPEECH`) and raises a
    persistent notification "Overwatch voice assistant" plus an error log, so a failure like this cannot be silent;
    today's date (not the time) is appended to the system prompt via `extra_system_prompt` and the cache is
    re-warmed at 00:01; "what time is it" is answered from the local clock (`_maybe_direct_clock_answer`); the prompt
    got a sports example. Lesson: before any deploy, replay the exact HA request (real prompt, all real tool schemas)
    against llama.cpp first; this is how the fixed version was validated (21/24 tool choices on the real 28 tools,
    cold first call 57 s with a 5.5k-token prefix, later calls 2.5-8 s).
    **Result, fixed version live (`accuracy-phase1-fixed-2026-11-12.json`, `rescore-phase1-2026-11-12.txt`):** raw
    71/78 (91%). On the 74 checks shared with the baseline: **78% -> 91%**; breadth (garage temperature/humidity,
    motion, date, weather, headlines, sports, garden, calendar, joke) **5/20 -> 14/20 (25% -> 70%)**; recipe + general
    53/54 unchanged (98%). `garden_tasks` is really called now (verified in the llama.cpp capture; GardenKeeper
    answered "No pending garden tasks due soon."). Still failing: weather (model sometimes refuses without searching),
    sports and headlines (the web summary step reports "the snippets do not include..."). Date arithmetic passed
    ("43 days to Christmas") but it was 49 in the replay, so it is unreliable without a calculator tool.
    **Timings got worse where answers got right:** model-answered turns mean 6.2 s, median 3.8 s, p90 12.2 s, max
    17.3 s (baseline 5.0 / 4.0 / 7.4 / 14.4 s); code answers 34 of 78 turns at 0.0-0.1 s. Slowest are
    GetLiveContext questions (area temperature 14 s, area humidity 17 s, motion 11 s): those used to be instant wrong
    answers ("I have no such device"). Next lever: extend the state reflex to answer area/quantity questions from the
    snapshot in code (about 0 s instead of 14-17 s). `rescore.py` now keeps recorded verdicts for time-dependent checks
    (a rescore on another day wrongly failed the date/time checks). Tools: `test_routing_phase1.py` (28 tests),
    `test_state_route.py` (16), `pipeline_probe.py`, `alltools_exp.py`, `accuracy.py` (+`BREADTH`), `rescore.py`.
  - **Voice PE flashed with the "Overwatch" wake word (2026-11-13, owner asked "flash the wakeword on pe").** Config:
    `configs/esphome/home-assistant-voice-0ae52a.yaml` (copied to `\\192.168.20.101\config\esphome\`, with the model in
    `esphome\wake_words\`). It is the stock Nabu Casa package pinned to 26.9.0 (the version the device ran) plus the model,
    `wifi: ssid/password` from the add-on's `secrets.yaml` (`wifi_ssid` is HomeIoT, `wifi_pass`), and
    `use_address: 192.168.50.108`; API `encryption: {}` is untouched so HA's key kept working. Problems found on the way:
    ESPHome 2026.10 rejects a config with no Wi-Fi SSID; the manifest `website` must be a valid URL (mine was empty,
    which would have broken any use of the model, now fixed in `voice/wakeword-micro/overwatch.json`); `model:` takes a
    plain local path, not `file://`. The Device Builder 2026.10.2 add-on is driven through HA ingress with
    `main/tools/esphome_dashboard.py` (`validate`, `compile`, `install`, `upload`; its `/ws` protocol uses string message
    ids). Build about 7 min on the HA VM (3.0 MB, 63% of the app partition free), OTA upload 21 s, device back in HA
    within 10 s. Check afterwards: satellite `idle`, wake word select offers Overwatch, no unavailable entities.
    **State:** "Wake word" = Okay Nabu, "Wake word 2" = Overwatch (both active). Not yet tested by voice. Rollback: set
    "Wake word 2" to `no_wake_word`, or remove the `micro_wake_word` block from the YAML and upload again (the stock
    firmware image is on the Voice PE release page if ever needed).
  - **Voice PE heard "Overwatch" (tone) but never answered (2026-11-13): HA `internal_url` had silently reverted.**
    Diagnosis: pipeline debug showed runs with only a `run-end` event, and the HA system log showed `HomeAssistantError:
    Unable to determine Home Assistant URL to send to device` raised from the ESPHome satellite's `on_pipeline_event`
    at `run-start`, so STT never started. `/api/config` reported `internal_url: https://192.168.20.101:8123` (IP-only
    https, which HA refuses for device media under SSL). Cause: the 11-11 proxy URL was set only in the HA UI, while
    `configuration.yaml` also had `homeassistant: internal_url: https://192.168.20.101:8123` (present in every copy I
    saved from 11-12 13:15, i.e. before my edits); the YAML overrides the UI value at every start, and my deploys
    restarted HA several times. Not caused by the wake word, the model or Phase 1. Fix: set it live with
    `config/core/update` (immediate) and in the live YAML to `http://ha-media.home.arpa:8124` (backup
    `backups/configuration.yaml.bak-20261113-pre-internal-url`, `check_config` valid, no restart needed); the repo copy and
    the `ha-media-proxy` README now say it belongs in YAML. Verified HA builds `http://ha-media.home.arpa:8124/api/tts_proxy/...`.
    Not verified by voice. Side effect is the one the README already lists (non-TTS URLs from `internal_url` 404).
  - **Voice PE test, "stuck on today's weather" (2026-11-13 00:27).** The time question worked (STT heard it, the clock
    reflex answered in 0.1 s, TTS played), so the `internal_url` fix held. The weather question took **79.9 s** and then
    the model refused ("The current weather is not available. Please check a weather service"), without searching.
    Two causes. (1) The warm-up used a plain context but a Voice PE turn carries a different prompt and tool list (35
    tools including the timer tools, no "This device is not able to start timers" line), so llama.cpp's cached prefix
    stopped matching about 500 tokens in and the whole ~6.5k-token prompt was read cold. The warm-up now runs as each
    Assist satellite (`device_id` + `satellite_id`, `_satellite_contexts`); after that a Voice PE model turn takes
    about 3.5 s (the joke test) and the warm-up after an HA restart took 1.9 s because llama.cpp kept the cache. (2) The
    model refuses weather instead of calling `web_search` (the accuracy suite showed the same, `weather_now` 0/2), so
    home weather is now answered in code from `weather.forecast_home` plus `weather.get_forecasts` (daily): today,
    tomorrow, rain/snow and "how cold is it outside" in 0.0-0.1 s (`_weather_scope`, `_weather_answer`, 53 offline
    tests); another place or a longer range goes to the model, and "weather in London" came back via web search in
    14.6 s. The weather entity is not exposed to Assist and is read directly (public information, not a device).
    Also seen: Whisper heard "the we what's the weather today?" (leading junk; the matching tolerates it).
    **Cache caveat:** each different prompt context evicts the previous one (`--cache-ram 1024` holds about one 6.5k-token
    prefix), so running `accuracy.py` (plain REST context) or using the HA chat box leaves the next spoken question
    cold (60-80 s) until the Voice PE context is warmed again; re-warm with
    `python pipeline_probe.py --token-file F --device-id 0400adefe0d3d378682adb9154ffba06 --ask "Tell me a short joke."`.
    Probe results: `probe-voicepe-2026-11-13.json`, `probe-voicepe-2026-11-13b.json`. Backups: component before this change
    `backups/llamacpp_conversation__init__.py.bak-20261113-pre-weather-warmup`. NOT yet re-run through `accuracy.py` (it
    would have evicted the Voice PE's cache while it is in use).
  - **30B IN PRODUCTION (2026-11-13, owner: "30b to production").** Why now: voice depended on `llama-trial` and
    `llama-proxy` (the request-capture proxy, also holding 8081), both with restart policy `no`, while the real
    `llama-cpp` was stopped by hand, so a CT 114 or Docker restart would have silenced voice; the proxy also wrote every
    utterance and full prompt to `/root/cap/captured.jsonl` in plain text. What was done: backed up
    `/opt/stacks/local-ai/docker-compose.yml` to `docker-compose.yml.bak-20261113-pre-30b`; edited the `llama-cpp`
    service to the trial's validated flags (`Qwen3-30B-A3B-Q4_K_M.gguf`, `--ctx-size 40960`, f16 K/V cache, `--cache-ram
    1024`, threads 4, parallel 1, ngl 99, reasoning off, jinja; alias `home-assistant-llm`, port 8081 unchanged so HA needed
    no change); validated with `docker compose config`; removed `llama-proxy`, `llama-trial` and the `trialnet` network;
    `docker compose up -d --no-deps llama-cpp`. Healthy 25 s later, `n_ctx 40960`, restart policy `unless-stopped`, ~3.5 GiB
    memory available. The repo `configs/local-ai/docker-compose.yml` is the same file. Verified as the Voice PE (first
    model answer 77 s cold, then chat 2.6-3.4 s, garden 10.6 s, web 9.4 s; weather/time/garage/shopping 0.0-0.1 s). 30B
    SHA-256 `0d003f66...a8f5`; image digest unchanged. **Rollback:** `cp docker-compose.yml.bak-20261113-pre-30b
    docker-compose.yml && docker compose up -d --no-deps llama-cpp` (about 30 s, then re-warm with the probe below).
    After ANY llama.cpp restart the first spoken question reads the prompt cold (60-80 s): run
    `python tools/llm-bench/pipeline_probe.py --token-file F --device-id 0400adefe0d3d378682adb9154ffba06 --ask "Tell me a short joke."`
    first. The capture proxy is gone, so `replay_bench.py` / `capture_proxy.py` experiments need a proxy container started
    again (see their headers); `/root/cap/captured.jsonl` (5 MB, personal utterances) is still on CT 114: delete it when no
    longer needed. STT is already Parakeet (sherpa-onnx), so there is nothing to upgrade there.
  - "acceptance test cheese" is confirmed on the agent's (Grocy) shopping list: delete it in Grocy.

## Open owner decisions

1. Approve trial downloads (~18 GB for Qwen3-30B-A3B, plus optional 8B/4B).
2. Approve switching the live model/backend after the benchmark.
3. Approve 3a (local intents + Overwatch-style responses) and 3b.
