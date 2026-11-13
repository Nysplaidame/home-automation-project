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


import datetime as _dt

TODAY = _dt.date(2026, 11, 13)
WEATHER = {  # shaped like the live weather.forecast_home entity and its daily forecast
    "current": {"condition": "partlycloudy", "temperature": 0.4, "unit": "°C"},
    "daily": [
        {"date": _dt.date(2026, 11, 12), "condition": "partlycloudy", "temperature": 0.4, "templow": 0.4, "precipitation": 0.0},
        {"date": TODAY, "condition": "cloudy", "temperature": 3.0, "templow": -1.2, "precipitation": 0.0},
        {"date": _dt.date(2026, 11, 14), "condition": "rainy", "temperature": 6.0, "templow": 2.0, "precipitation": 2.4},
        {"date": _dt.date(2026, 11, 15), "condition": "sunny", "temperature": 8.0, "templow": 3.0, "precipitation": 0.0},
    ],
}


class WeatherTests(unittest.TestCase):
    def test_questions_about_the_weather_at_home(self):
        cases = {
            "What's the weather today?": ("today", False),
            "what's the weather": ("today", False),
            " the we what's the weather today?": ("today", False),   # speech-to-text junk in front
            "What is the weather like at the moment?": ("today", False),
            "How's the weather?": ("today", False),
            "Will it rain tomorrow?": ("tomorrow", True),
            "Do I need an umbrella?": ("today", True),
            "Is it going to rain tonight?": ("today", True),
            "Is it cold outside?": ("today", False),
            "How cold is it outside?": ("today", False),
            "How cold is it out there?": ("today", False),
            "Is it cold out?": ("today", False),
            "How warm is it?": ("today", False),
            "What's the temperature outside?": ("today", False),
            "What's the weather forecast for tomorrow?": ("tomorrow", False),
        }
        for text, expected in cases.items():
            self.assertEqual(M._weather_scope(text), expected, text)

    def test_other_questions_are_left_to_the_model(self):
        for text in (
            "What's the weather like in London?", "weather in Paris today", "Will it rain on Saturday?",
            "What's the weather this weekend?", "What was the weather like yesterday?", "Is it going to rain next week?",
            "Play rain sounds", "Set the rain sensor to wet", "Add rain boots to my shopping list",
            "What is the temperature in the garage?", "What is the capital of France?", "Is the garage door open?",
            "How hot is the oven?", "Is it cold in the garage?", "How cold is it in the freezer?",
            "What is the P1S nozzle temperature?", "How warm is the FDM enclosure?",
            "Tell me everything you know about how weather forecasting models are built and trained please",
        ):
            self.assertIsNone(M._weather_scope(text), text)

    def test_today(self):
        self.assertEqual(
            M._weather_answer(("today", False), WEATHER, TODAY),
            "It is currently partly cloudy and 0 degrees Celsius. Today's high is 3 and the low is minus 1.",
        )

    def test_tomorrow(self):
        self.assertEqual(
            M._weather_answer(("tomorrow", False), WEATHER, TODAY),
            "Tomorrow's forecast is rain, with a high of 6 and a low of 2.",
        )

    def test_rain_questions(self):
        self.assertEqual(M._weather_answer(("today", True), WEATHER, TODAY), "No, no rain or snow is expected today.")
        self.assertEqual(M._weather_answer(("tomorrow", True), WEATHER, TODAY),
                         "Yes, rain is expected tomorrow, about 2.4 millimetres.")
        raining = {**WEATHER, "current": {"condition": "rainy", "temperature": 4.0, "unit": "°C"}}
        self.assertEqual(M._weather_answer(("today", True), raining, TODAY), "Yes, it is raining now.")

    def test_missing_forecast_degrades_safely(self):
        no_daily = {"current": WEATHER["current"], "daily": []}
        self.assertEqual(M._weather_answer(("today", False), no_daily, TODAY), "It is currently partly cloudy and 0 degrees Celsius.")
        self.assertIsNone(M._weather_answer(("tomorrow", False), no_daily, TODAY))  # no data: let the model try
        self.assertIsNone(M._weather_answer(("tomorrow", True), no_daily, TODAY))
        self.assertIsNone(M._weather_answer(("today", False), {"current": {}, "daily": []}, TODAY))

    def test_number_words(self):
        self.assertEqual([M._wx_number(v) for v in (0.4, 0.6, -0.4, -1.2, -1.6, 12.5, None, "x")],
                         ["0", "1", "0", "minus 1", "minus 2", "13", None, None])


class SatelliteWarmupTests(unittest.TestCase):
    class E:
        def __init__(self, domain, entity_id, device_id, disabled_by=None):
            self.domain, self.entity_id, self.device_id, self.disabled_by = domain, entity_id, device_id, disabled_by

    def test_warms_as_each_enabled_satellite(self):
        entries = [self.E("light", "light.x", "d0"), self.E("assist_satellite", "assist_satellite.b", "d2"),
                   self.E("assist_satellite", "assist_satellite.a", "d1"),
                   self.E("assist_satellite", "assist_satellite.off", "d3", disabled_by="user")]
        self.assertEqual(M._satellite_contexts_from(entries), [("d1", "assist_satellite.a"), ("d2", "assist_satellite.b")])

    def test_no_satellite_means_one_plain_warmup(self):
        self.assertEqual(M._satellite_contexts_from([self.E("light", "light.x", "d0")]), [(None, None)])
        self.assertEqual(M._satellite_contexts_from([]), [(None, None)])


class RemovedGatesTests(unittest.TestCase):
    def test_keyword_gates_are_gone(self):
        for name in ("_filter_assist_tools", "_is_direct_response_request", "_is_web_search_affirmation",
                     "_configured_api_set", "_selected_apis", "ASSIST_RE", "WEB_RE", "RECIPE_RE",
                     "HEALTH_STATUS_RE", "PRODUCTION_APP_RE"):
            self.assertFalse(hasattr(M, name), f"{name} should have been removed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
