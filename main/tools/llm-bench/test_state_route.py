#!/usr/bin/env python3
"""Offline tests for the model-free device-state route in llamacpp_conversation.

Loads the component with stubbed Home Assistant imports and exercises the pure helpers against the
exposed-entity list captured from the live Assist prompt (2026-11-12). Run:

  python test_state_route.py
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

COMPONENT = (
    Path(__file__).resolve().parents[2]
    / "configs/home-assistant/custom_components/llamacpp_conversation/__init__.py"
)


def load_component():
    for name in (
        "aiohttp", "voluptuous", "voluptuous_openapi", "probatio", "homeassistant",
        "homeassistant.components", "homeassistant.components.conversation",
        "homeassistant.components.conversation.agent_manager",
        "homeassistant.components.conversation.const", "homeassistant.const", "homeassistant.core",
        "homeassistant.exceptions", "homeassistant.helpers",
        "homeassistant.helpers.aiohttp_client", "homeassistant.helpers.typing",
        "homeassistant.helpers.event", "homeassistant.util", "homeassistant.util.dt",
    ):
        sys.modules.setdefault(name, MagicMock())
    spec = importlib.util.spec_from_file_location("llamacpp_under_test", COMPONENT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


M = load_component()


def ent(names, domain, state, area="", **attrs):
    names = [names] if isinstance(names, str) else names
    return {"entity_id": f"{domain}.x", "domain": domain, "names": names, "area": area,
            "state": state, "attrs": attrs}


# The 18 entities exposed to the voice assistant, as listed in the live Assist prompt.
HOME = [
    ent("Cam 01 Annke C500 Motion", "binary_sensor", "off", "Outdoors / CCTV", device_class="motion"),
    ent("Cam 02 Gate Motion", "binary_sensor", "on", device_class="motion"),
    ent("Cam 03 Patio Motion", "binary_sensor", "off", device_class="motion"),
    ent("FDM Enclosure Sensor FDM Enclosure Sensor Humidity", "sensor", "41.26", "Garage",
        unit_of_measurement="%"),
    ent("FDM Enclosure Sensor FDM Enclosure Sensor Temperature", "sensor", "23.5", "Garage",
        unit_of_measurement="°C"),
    ent("Home Assistant Voice 0ae52a Media Player", "media_player", "idle"),
    ent("Inline Fan", "fan", "off"),
    ent("P1S Bed Temperature", "sensor", "unavailable", unit_of_measurement="°C"),
    ent("P1S Chamber Temperature", "sensor", "28", unit_of_measurement="°C"),
    ent("P1S Nozzle Temperature", "sensor", "25", unit_of_measurement="°C"),
    ent("Spray Booth Fan", "fan", "on"),
    ent("VentSys Booth Airflow Sensor Light On-Off", "switch", "off"),
    ent("VentSys FDM Airflow Sensor Light On-Off", "switch", "on", "Garage"),
    ent("VentSys SLA Airflow Sensor", "switch", "on", "Garage"),
    ent("VentSys SLA Airflow Sensor Light On-Off", "switch", "off", "Garage"),
    ent("VentSys SLA Pipe Air Sensor humidity", "sensor", "55", "Garage", unit_of_measurement="%"),
    ent("VentSys SLA Pipe Air Sensor temperature", "sensor", "21.04", "Garage",
        unit_of_measurement="°C"),
]


def answer(text, entities=HOME):
    return M._direct_state_answer(text, entities)


class StateRouteTests(unittest.TestCase):
    # --- the two accuracy checks that motivated the route
    def test_unknown_device_is_a_clear_no(self):
        self.assertEqual(answer("Is the garage door open?"), "I have no device called garage door.")
        self.assertEqual(
            answer("Is the flux capacitor switched on?"), "I have no device called flux capacitor."
        )

    def test_unknown_device_phrasing_variants(self):
        for text in (
            "is the garage door open",
            "Is the garage door open right now?",
            "Is the garage door currently open?",
            "hey overwatch, is the garage door open?",
            "Is my garage door open?",
        ):
            self.assertEqual(answer(text), "I have no device called garage door.", text)

    # --- real devices
    def test_binary_state(self):
        self.assertEqual(answer("Is the inline fan on?"), "The Inline Fan is off.")
        self.assertEqual(answer("Is the spray booth fan running?"), "The Spray Booth Fan is on.")
        self.assertEqual(answer("Is the VentSys SLA airflow sensor on?"), "The VentSys SLA Airflow Sensor is on.")
        self.assertEqual(
            answer("Are the VentSys FDM airflow sensor lights on?"),
            "The VentSys FDM Airflow Sensor Light On-Off is on.",
        )

    def test_motion_sensor_wording(self):
        self.assertEqual(answer("Is Cam 02 Gate Motion on?"), "The Cam 02 Gate Motion is detecting motion.")
        self.assertEqual(answer("Is cam 03 patio motion on?"), "The Cam 03 Patio Motion is clear.")

    def test_values_and_units(self):
        self.assertEqual(
            answer("What is the FDM enclosure temperature?"),
            "The FDM Enclosure Sensor Temperature reads 23.5 degrees Celsius.",
        )
        self.assertEqual(
            answer("What's the P1S chamber temperature?"), "The P1S Chamber Temperature reads 28 degrees Celsius."
        )
        self.assertEqual(
            answer("What is the SLA pipe air sensor humidity?"),
            "The VentSys SLA Pipe Air Sensor humidity reads 55 percent.",
        )

    def test_unavailable_state_is_reported(self):
        self.assertEqual(answer("What is the P1S bed temperature?"), "The P1S Bed Temperature is unavailable.")

    def test_door_cover_uses_real_state(self):
        home = [*HOME, ent("Garage Door", "cover", "open", "Garage", device_class="garage")]
        self.assertEqual(answer("Is the garage door closed?", home), "The Garage Door is open.")

    def test_alias_matches(self):
        home = [*HOME, ent(["Cellar Light", "basement lamp"], "light", "on")]
        self.assertEqual(answer("Is the basement lamp on?", home), "The Cellar Light is on.")

    def test_area_completes_a_name(self):
        home = [*HOME, ent("Ceiling Fan", "fan", "on", "Bedroom")]
        self.assertEqual(answer("Is the bedroom ceiling fan on?", home), "The Ceiling Fan is on.")

    # --- leave to the model
    def test_ambiguous_goes_to_model(self):
        for text in (
            "Is the fan on?",
            "Is the light on?",
            "What is the temperature?",
            "What is the temperature in the garage?",
            "Is the garage fan on?",
            "Is the garage light on?",
        ):
            self.assertIsNone(answer(text), text)

    def test_not_a_state_question(self):
        for text in (
            "What is the capital of France?",
            "What is the speed of light?",
            "Who are you?",
            "Is it on?",
            "Is that open?",
            "Is everything off?",
            "Is the door open or closed?",
            "Is the shopping list empty?",
            "Is the recipe on the second step?",
            "Turn on the inline fan.",
            "What time is it?",
            "Search the web for whether the shop is open.",
        ):
            self.assertIsNone(answer(text), text)

    def test_value_question_never_claims_no_device(self):
        self.assertIsNone(answer("What is the reading on the flux capacitor?"))
        self.assertIsNone(answer("What is the state of the union?"))

    def test_empty_home_is_a_clear_no(self):
        self.assertEqual(answer("Is the inline fan on?", []), "I have no device called inline fan.")

    def test_unknown_domain_goes_to_model(self):
        home = [ent("Heat Pump", "climate", "heat")]
        self.assertIsNone(answer("Is the heat pump on?", home))

    # --- internals
    def test_spoken_name_dedupes_prefix(self):
        self.assertEqual(
            M._spoken_state_name("FDM Enclosure Sensor FDM Enclosure Sensor Humidity"),
            "FDM Enclosure Sensor Humidity",
        )
        self.assertEqual(M._spoken_state_name("Inline Fan"), "Inline Fan")
        self.assertEqual(M._spoken_state_name("Test Test Light"), "Test Light")

    def test_tokens_fold_plurals(self):
        self.assertEqual(M._state_tokens("the Lights"), {"light"})
        self.assertEqual(M._state_tokens("Dave's printer"), {"dave", "printer"})
        self.assertEqual(M._state_tokens("glass"), {"glass"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
