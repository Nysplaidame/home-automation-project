# 10. Overwatch voice routing: from keyword gates to one general agent with reflexes

Status: **Phase 1 deployed and live** (2026-11-12 to 13). Phase 0 (device-state reflex) is live too; phases 2 to 4
are still proposals. Outcome on the 74 checks shared with the pre-Phase-1 baseline: **78% -> 91%** overall,
breadth questions **25% -> 70%**, recipe and general questions unchanged at 98%. The first deploy failed and
was rolled back (llama.cpp rejected the 2,000-character `confirmation_token` bound in the `garden_tasks` tool
schema with "failed to parse grammar" on every turn); the schema sanitiser, a warm-up canary and a pre-deploy
replay against llama.cpp came out of it. Model-answered turns got slower on average (6.2 s against 5.0 s) because
home-state questions are now answered correctly through a tool instead of instantly and wrongly; extending the
state reflex to area and quantity questions is the next step. Details: `HANDOFF-2026-11-11-llm-igpu-speed.md`.

## Problem

Overwatch's `llamacpp_conversation` component decides what the assistant can do with keyword regexes. Four
independent classifiers read the same utterance and can disagree: `_select_llm_hass_api` (which tool families
exist this turn), `_filter_assist_tools` (which Assist tools), `_max_tokens_for_turn`, and about fourteen
`_maybe_direct_*` shortcuts, in a hand-ordered chain, with 50 regexes in a 2,500-line file. A tool the regexes
do not name is simply not offered, so the model answers from nothing.

The owner wants Overwatch to answer a broad range of questions (weather, calendar, general topics), not only
the tasks the rules were written for. A keyword gate cannot do that: every new subject needs a new rule, and
anything unanticipated fails silently.

## Evidence (all measured 2026-11-12 on the live system)

Real Assist pipeline probe (`tools/llm-bench/pipeline_probe.py`, results in `probe-pipeline-2026-11-12.json`)
and direct agent calls, 30B model:

| Question | Result | Cause |
|---|---|---|
| What is the temperature in the garage? / How warm is it in the garage? / humidity | "I have no such device." (two garage sensors exist) | no control verb in the text, so no tools were offered |
| Is the fan on? | 20 s, "The fan is not on." (both fans are `unknown`) | tools filtered, model guesses |
| What garden tasks are due today? | "I will check the garden tasks... One moment please." and nothing happens | `gardenkeeper_ops` and `household_knowledge` are configured but `_select_llm_hass_api` can never select them |
| What's the weather like today? / Will it rain tomorrow? | "I have no such device." | no tool offered; HA has 1 `weather` entity, not exposed; no web fallback |
| What's on my calendar tomorrow? | "I have no access to your calendar." | HA has **0** calendar entities: a missing data source, not a routing fault |
| How many days until Christmas? | "68 days" (correct: 43) | no date tool offered, the model has no clock |
| Turn on the flux capacitor | 13.8 s, "I have no such device." | prefer-local did not catch it, two model calls |

Also measured: of 21 single-turn probes only time and date were answered by Home Assistant's native
sentences (`processed_locally`); the accuracy harness used so far calls the agent over REST and bypasses that
step, so it never showed this.

Prompt and cache facts: the garage-door turn read 2,250 prompt tokens, of which the model had to process
about 1,750 because the 1 GiB prompt cache evicts when turns alternate between different tool subsets.
Per-turn tool filtering therefore creates a different prefix per subset: it saves tokens on one turn and
causes cache misses on the next.

## Experiment: one stable prefix with every tool

`tools/llm-bench/alltools_exp.py`, results in `alltools-results-2026-11-12.txt`. Qwen3-30B-A3B, f16 KV,
25 tools (the 24 seen in live traffic plus `web_search`; 3,537 tool tokens), static device list, first model
call only, no tool executed.

- **Speed:** the first call is cold: 4,091 new tokens, 40.6 s. Every later call reprocessed 14 to 18 tokens
  (4,274 reused) and took about 2 to 5 s, which is generation time. With a stable prefix the size of the tool
  set costs a one-time 40 s, not a per-turn cost.
- **Tool choice, naive prompt (v1):** 22 of 36 (61%). Deterministic refusals ("I cannot provide real-time
  weather information"), a made-up time ("10:30 AM"), and the model picking HA's `todo` shopping tools
  instead of Grocy (two shopping lists exist).
- **Tool choice, routing-aware prompt (v2, 196 tokens, one line per topic: home, date and time, web, shopping,
  recipes, control, and "call a tool instead of refusing"):** 42 of 46 (91%). Remaining misses: "What time is
  it?" still fabricated a time without calling `GetDateTime` (Home Assistant answers this one natively), and
  "Who won the football match last night?" was refused instead of searched.
- Limits: 23 utterances run twice (results were identical, so effectively n=23); tool choice only, not
  end-to-end answers; `gardenkeeper_ops` and `household_knowledge` tools are not in the test (they are not in
  this repo, only on the live HA); `web_search` definition rebuilt from source.

## Proposal

Principle: **capability is never gated by keywords; speed comes from caching and reflexes.**

1. **General agent (the default path).** One system prompt and one complete tool set on every turn, so the
   prefix is byte-stable and stays in the KV cache. The prompt states routing by topic (as in v2), not by
   regex. Dynamic context (the recipe/web state hint) moves to the end of the conversation, after the
   history, so it never disturbs the prefix. Replace Home Assistant's ~200-token Assist boilerplate with a
   compact equivalent. A new capability is a new tool plus one catalog line plus one test row.
2. **Reflexes (an optimisation, never a gate).** The existing `_maybe_direct_*` shortcuts become a declarative
   table (name, matcher, handler, guard, test cases) with one uniform fall-through and trace. Kept only for
   things the model adds nothing to: device state lookups, shopping, recipe list/recall/pick, explicit web
   search. They answer in about 0.0 to 0.1 s today. A miss falls through to the general agent; it can never
   remove a capability. Home Assistant's native intents (`prefer_local_intents`) stay as layer zero for
   time, date, timers, media and lights.
3. **Guards.** Cheap post-checks for known failure modes: a reply containing a clock time or date when no date
   tool ran, or "I cannot check..." when a relevant tool exists, is re-asked with the tool forced
   (`tool_choice`), instead of being spoken.
4. **Warm cache.** One warm-up call after Home Assistant or llama.cpp starts, so the 40 s cold prefix is
   never paid by a person. With a single prefix the server slot keeps it; `--cache-ram` matters far less.
5. **Evaluation as the safety net.** Grow `alltools_exp.py` and `accuracy.py` into one labelled routing set
   (target 100+ utterances across home, web, recipes, shopping, garden, weather, calendar, chat), run through
   the real pipeline path. Every change to the prompt, tools or reflexes must keep it green. This replaces
   fixing one phrasing at a time.

Expected effect (estimates built on the measurements above): reflex turns unchanged at ~0.1 s; chat 2 to
2.5 s; a state question that needs the model about 6 to 9 s warm (was 21 s cold); a web question about 6 to
10 s; only the first turn after a restart is slow, and pre-warming removes that.

### Data gaps that routing cannot fix

- **Calendar:** no calendar integration exists in Home Assistant. Add one (Google, CalDAV or a local calendar),
  expose it, then the Assist `calendar` tool or a small custom `calendar_events` tool becomes a catalog line.
- **Weather:** expose the existing `weather` entity and add a forecast tool (`weather.get_forecasts`);
  until then `web_search` works only if the query carries the home location, so put the location in the prompt.
- **Repo drift:** `gardenkeeper_llm` and `household_hub_llm` exist only on the live Home Assistant. Bring them
  into the repo before the tool inventory and the evaluation set are built.

## Phases (each independently useful and reversible)

0. Done: device-state reflex deployed; real-pipeline probe and routing measurements recorded.
1. General agent with a stable prefix: remove `_select_llm_hass_api` gating and `_filter_assist_tools`, add the
   v2-style prompt, move the state hint to the tail, add the warm-up. Test on the trial container, then
   deploy with a backup and the evaluation set as the gate.
2. Reflex registry refactor (no behaviour change; unit tests per reflex).
3. New capabilities: weather forecast tool, calendar, home location in the prompt, garden/household in the
   evaluation set.
4. Guards (forced tool call on the two observed fabrications), then re-measure.

## Risks and open questions

- Tool-choice accuracy may fall as the tool count grows (25 tools at 91% here; garden, household, weather and
  calendar add roughly ten more). Mitigations: curate overlapping tools (drop HA `todo` if Grocy owns the
  shopping list), shorten descriptions, and only if the set passes about 40 tools consider a small number of
  fixed profiles (each its own cached prefix, about 420 MB of KV each) or an embedding router.
- The cold first call is about 40 s; the 4.3k-token prefix needs ~420 MB of KV, so memory in CT 114 (about
  3.3 GiB spare with the 30B) stays adequate.
- The 30B still invents answers when no tool applies; guards reduce this but do not remove it.
- Decision for the owner: approve Phase 1 as the next change, and choose the calendar source.
