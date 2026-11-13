#!/usr/bin/env python3
"""Offline tests for decision 10, phase 1: every API on every turn, a stable prompt prefix, no gates.

  python test_routing_phase1.py
"""
from __future__ import annotations

import unittest

from test_state_route import M  # the component loaded with stubbed Home Assistant imports

CONFIGURED = ["assist", "searxng_search", "mealie_recipes", "grocy_household", "gardenkeeper_ops",
              "household_knowledge"]
STATE_WITH_RECIPE = {"active_recipe": {"name": "Ultimate Chicken Soup", "slug": "ultimate-chicken-soup"},
                     "active_recipe_details": {"ingredients": ["2 tablespoons olive oil"], "steps": ["a", "b"]},
                     "trace": []}


def sys_msg(text="SYSTEM"):
    return {"role": "system", "content": text}


def user(text):
    return {"role": "user", "content": text}


def asst(text):
    return {"role": "assistant", "content": text}


class ApiSelectionTests(unittest.TestCase):
    def test_every_configured_api_in_configured_order(self):
        self.assertEqual(M._select_llm_hass_api(CONFIGURED), CONFIGURED)

    def test_no_keyword_can_hide_an_api(self):
        # The signature takes no utterance at all: availability cannot depend on the words spoken.
        self.assertEqual(M._select_llm_hass_api(CONFIGURED, set(CONFIGURED)), CONFIGURED)

    def test_single_string_and_none(self):
        self.assertEqual(M._select_llm_hass_api("assist"), "assist")
        self.assertIsNone(M._select_llm_hass_api(None))
        self.assertIsNone(M._select_llm_hass_api([]))

    def test_duplicates_are_dropped_keeping_order(self):
        self.assertEqual(M._select_llm_hass_api(["assist", "searxng_search", "assist"]),
                         ["assist", "searxng_search"])

    def test_unregistered_apis_are_skipped_not_fatal(self):
        registered = {"assist", "searxng_search"}
        self.assertEqual(M._select_llm_hass_api(CONFIGURED, registered), ["assist", "searxng_search"])
        self.assertEqual(M._select_llm_hass_api(CONFIGURED, {"assist"}), "assist")
        self.assertIsNone(M._select_llm_hass_api(CONFIGURED, set()))


class PromptPrefixTests(unittest.TestCase):
    def test_no_hint_for_unrelated_questions(self):
        msgs = [sys_msg(), user("Is the garage door open?")]
        self.assertEqual(M._trim_messages(msgs, 8, STATE_WITH_RECIPE), msgs)
        msgs = [sys_msg(), user("What is the weather like today?")]
        self.assertEqual(M._trim_messages(msgs, 8, STATE_WITH_RECIPE), msgs)

    def test_hint_goes_right_before_the_newest_user_message(self):
        msgs = [sys_msg(), user("Hello"), asst("Hi"), user("How much salt does it need?")]
        out = M._trim_messages(msgs, 8, STATE_WITH_RECIPE)
        self.assertEqual(out[:3], msgs[:3])  # system prompt and history untouched
        self.assertEqual(out[3]["role"], "system")
        self.assertIn("Ultimate Chicken Soup", out[3]["content"])
        self.assertEqual(out[4], msgs[3])
        self.assertEqual(len(out), 5)

    def test_prefix_is_identical_across_turns(self):
        turn1 = M._trim_messages([sys_msg(), user("Is the fan on?")], 8, STATE_WITH_RECIPE)
        turn2 = M._trim_messages(
            [sys_msg(), user("Is the fan on?"), asst("It is off."), user("And the garage light?")],
            8, STATE_WITH_RECIPE)
        self.assertEqual(turn2[: len(turn1)], turn1)

    def test_hint_survives_the_tool_loop_in_the_same_place(self):
        base = [sys_msg(), user("Read me the ingredients for it")]
        first = M._trim_messages(base, 8, STATE_WITH_RECIPE)
        later = M._trim_messages([*base, asst("calling"), {"role": "tool", "content": "{}"}], 8, STATE_WITH_RECIPE)
        self.assertEqual(later[: len(first)], first)

    def test_empty_state_or_header_only_adds_nothing(self):
        msgs = [sys_msg(), user("How much salt does it need?")]
        self.assertEqual(M._trim_messages(msgs, 8, None), msgs)
        self.assertEqual(M._trim_messages(msgs, 8, {"trace": []}), msgs)
        self.assertEqual(M._assistant_state_prompt({"trace": []}), "")

    def test_history_is_trimmed_but_system_prompt_kept(self):
        msgs = [sys_msg(), *[user(f"q{i}") if i % 2 == 0 else asst(f"a{i}") for i in range(12)]]
        out = M._trim_messages(msgs, 4, None)
        self.assertEqual(out[0], sys_msg())
        self.assertEqual(out[1:], msgs[-4:])

    def test_no_system_message(self):
        msgs = [user("a"), asst("b"), user("c")]
        self.assertEqual(M._trim_messages(msgs, 2, None), msgs[-2:])


class EchoAndBudgetTests(unittest.TestCase):
    def test_echo(self):
        self.assertEqual(M._maybe_direct_echo_answer("Say exactly: the quick brown fox."), "the quick brown fox.")
        self.assertEqual(M._maybe_direct_echo_answer('Reply exactly "all systems nominal"'), "all systems nominal")
        self.assertEqual(M._maybe_direct_echo_answer("repeat verbatim: one two three"), "one two three")

    def test_echo_leaves_other_requests_alone(self):
        for text in ("Say hello to the neighbours", "Repeat step two.", "Read me the ingredient list",
                     "Please say what the weather is", "Reply with the single word ready.", "Say exactly:"):
            self.assertIsNone(M._maybe_direct_echo_answer(text), text)

    def test_token_budget(self):
        self.assertEqual(M._max_tokens_for_turn("Repeat all the steps", 256), 256)
        self.assertEqual(M._max_tokens_for_turn("How many ingredients are there", 256), 192)
        self.assertEqual(M._max_tokens_for_turn("Tell me a joke", 256), 160)
        self.assertEqual(M._max_tokens_for_turn("Tell me a joke", 100), 100)


GARDEN_TASKS_SCHEMA = {  # exactly as advertised live; llama.cpp rejected it ("failed to parse grammar")
    "type": "object",
    "properties": {
        "transcript": {"type": "string", "minLength": 2, "maxLength": 1000},
        "confirmation_token": {"type": "string", "minLength": 10, "maxLength": 2000},
    },
    "required": ["transcript"],
    "additionalProperties": False,
}


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for item in node:
            yield from walk(item)


class SchemaSanitizerTests(unittest.TestCase):
    def test_the_schema_that_broke_every_turn(self):
        clean = M._sanitize_tool_schema(GARDEN_TASKS_SCHEMA)
        self.assertNotIn("maxLength", clean["properties"]["confirmation_token"])
        self.assertEqual(clean["properties"]["confirmation_token"]["minLength"], 10)
        self.assertEqual(clean["properties"]["transcript"]["maxLength"], 1000)  # at the limit: kept
        self.assertEqual(clean["required"], ["transcript"])
        self.assertIs(clean["additionalProperties"], False)

    def test_original_is_not_mutated(self):
        M._sanitize_tool_schema(GARDEN_TASKS_SCHEMA)
        self.assertEqual(GARDEN_TASKS_SCHEMA["properties"]["confirmation_token"]["maxLength"], 2000)

    def test_nested_arrays_and_unions(self):
        schema = {"type": "object", "properties": {
            "tags": {"type": "array", "items": {"type": "string", "maxLength": 5000}},
            "either": {"anyOf": [{"type": "string", "maxLength": 1001}, {"type": "string", "maxLength": 50}]},
        }}
        clean = M._sanitize_tool_schema(schema)
        self.assertEqual([n["maxLength"] for n in walk(clean) if "maxLength" in n], [50])

    def test_a_property_named_maxlength_survives(self):
        schema = {"type": "object", "properties": {"maxLength": {"type": "integer", "maximum": 9999}}}
        self.assertEqual(M._sanitize_tool_schema(schema), schema)

    def test_no_oversized_bound_survives_anywhere(self):
        for node in walk(M._sanitize_tool_schema(GARDEN_TASKS_SCHEMA)):
            value = node.get("maxLength")
            self.assertTrue(value is None or value <= M.MAX_GRAMMAR_STRING_LENGTH)


class WarmupCanaryTests(unittest.TestCase):
    def test_result_speech_reads_plain_speech(self):
        class R:  # shaped like a ConversationResult
            class response:
                speech = {"plain": {"speech": "Ready."}}
        self.assertEqual(M._result_speech(R), "Ready.")

    def test_result_speech_tolerates_odd_shapes(self):
        self.assertEqual(M._result_speech(object()), "")
        self.assertEqual(M._result_speech(None), "")

        class Empty:
            class response:
                speech = {}
        self.assertEqual(M._result_speech(Empty), "")

    def test_error_speech_is_the_apology_the_canary_looks_for(self):
        self.assertTrue(M.ERROR_SPEECH.startswith("I could not complete that request."))


class ClockAndDateTests(unittest.TestCase):
    def at(self, hour, minute):
        import datetime
        return datetime.datetime(2026, 11, 12, hour, minute)

    def test_time_questions_use_the_local_clock(self):
        for text in ("What time is it?", "what's the time", "What is the current time?", "Hey Overwatch, what time is it right now?",
                     "Tell me the time please", "Do you have the time?"):
            self.assertEqual(M._maybe_direct_clock_answer(text, self.at(20, 3)), "It is 8:03 PM.", text)

    def test_twelve_hour_formatting(self):
        self.assertEqual(M._maybe_direct_clock_answer("What time is it?", self.at(0, 5)), "It is 12:05 AM.")
        self.assertEqual(M._maybe_direct_clock_answer("What time is it?", self.at(9, 7)), "It is 9:07 AM.")
        self.assertEqual(M._maybe_direct_clock_answer("What time is it?", self.at(12, 0)), "It is 12:00 PM.")
        self.assertEqual(M._maybe_direct_clock_answer("What time is it?", self.at(23, 59)), "It is 11:59 PM.")

    def test_other_time_words_are_not_clock_questions(self):
        for text in ("What time does the shop open?", "What time is the match tonight?", "Set a timer for five minutes",
                     "What is the time zone in Tokyo?", "Is it time to eat?", "What's the weather this time of year?"):
            self.assertIsNone(M._maybe_direct_clock_answer(text, self.at(20, 3)), text)

    def test_date_line_is_ground_truth_and_changes_daily(self):
        line = M._date_line(self.at(20, 3))
        self.assertTrue(line.startswith("Today's date is Thursday, 12 November 2026."))
        self.assertNotIn("20:03", line)  # the time of day must never be in the cached prompt
        self.assertEqual(line, M._date_line(self.at(6, 45)))  # same all day, so the prefix stays cached


class RemovedGatesTests(unittest.TestCase):
    def test_keyword_gates_are_gone(self):
        for name in ("_filter_assist_tools", "_is_direct_response_request", "_is_web_search_affirmation",
                     "_configured_api_set", "_selected_apis", "ASSIST_RE", "WEB_RE", "RECIPE_RE",
                     "HEALTH_STATUS_RE", "PRODUCTION_APP_RE"):
            self.assertFalse(hasattr(M, name), f"{name} should have been removed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
