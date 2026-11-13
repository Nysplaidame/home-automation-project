"""Read-only deployment comparison regression tests; no HA/MQTT connection."""
import copy
import unittest

from validate_ventsys_contract import script_drift


class ScriptDriftTests(unittest.TestCase):
    def setUp(self):
        self.source = {'mode': {'alias': 'Mode', 'sequence': [
            {'action': 'mqtt.publish', 'data': {'topic': 'ventsys/fan/control', 'payload': 'on'}},
            {'action': 'mqtt.publish', 'data': {'topic': 'ventsys/fan/percent', 'payload': '100'}}]}}

    def test_ignores_presentation_only(self):
        live = copy.deepcopy(self.source)
        live['mode'].update(alias='Renamed', description='Changed', fields={}, icon='mdi:fan')
        self.assertEqual(script_drift(self.source, live), [])

    def test_detects_missing_speed_and_changed_order(self):
        live = copy.deepcopy(self.source)
        live['mode']['sequence'].pop()
        self.assertEqual(script_drift(self.source, live), ['mode'])
        live = copy.deepcopy(self.source)
        live['mode']['sequence'].reverse()
        self.assertEqual(script_drift(self.source, live), ['mode'])

    def test_detects_missing_extra_and_concurrency_changes(self):
        self.assertEqual(script_drift(self.source, {}), ['mode'])
        self.assertEqual(script_drift({}, self.source), ['mode'])
        live = copy.deepcopy(self.source)
        live['mode']['mode'] = 'parallel'
        self.assertEqual(script_drift(self.source, live), ['mode'])


if __name__ == '__main__':
    unittest.main()
