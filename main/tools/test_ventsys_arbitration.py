"""Arbitration policy tests using actual generated templates; no HA/MQTT calls.

These do not establish HA's runtime cancellation/parallel scheduling semantics.
"""
import copy
import unittest
import yaml
from jinja2.nativetypes import NativeEnvironment
from generate_ventsys_arbitration import SOURCE, ROOT, EXECUTOR, FIRE, build, build_dashboard, commands


class ArbitrationTests(unittest.TestCase):
    def setUp(self):
        self.source = yaml.safe_load(SOURCE.read_text(encoding='utf-8'))
        self.scripts = build(self.source)['script']
        self.executor = self.scripts[EXECUTOR]
        self.states = {'input_boolean.ventsys_failsafe': 'off', 'script.' + FIRE: 'off'}
        self.env = NativeEnvironment()
        self.env.globals['is_state'] = lambda key, value: self.states.get(key) == value

    def invalid(self, batch):
        return self.env.from_string(self.executor['sequence'][1]['if'][0]['value_template']).render(
            **self.executor['sequence'][0]['variables'], commands=batch)

    def blocked(self):
        return self.env.from_string(self.executor['sequence'][2]['repeat']['sequence'][0]['if'][0]['value_template']).render()

    def test_all_normal_modes_preserve_command_recipes_and_use_one_dispatcher(self):
        for name, recipe in self.source['script'].items():
            if not name.startswith('ventsys_mode_') or name == FIRE:
                continue
            call = self.scripts[name]['sequence']
            self.assertEqual(len(call), 1)
            self.assertEqual(call[0]['action'], 'script.' + EXECUTOR)
            self.assertEqual(call[0]['data']['commands'], commands(recipe['sequence']))
            self.assertFalse(self.invalid(call[0]['data']['commands']), name)
        self.assertEqual(self.executor['mode'], 'single')

    def test_fail_closed_before_every_publish(self):
        self.assertFalse(self.blocked())
        for state in ['on', 'unknown', 'unavailable', None]:
            self.states['input_boolean.ventsys_failsafe'] = state
            self.assertTrue(self.blocked(), state)
        self.states['input_boolean.ventsys_failsafe'] = 'off'
        for state in ['on', 'unknown', 'unavailable', None]:
            self.states['script.' + FIRE] = state
            self.assertTrue(self.blocked(), state)

    def test_failsafe_transition_between_commands_blocks_remaining_batch(self):
        published = []
        batch = commands(self.source['script']['ventsys_mode_purge']['sequence'])
        for index, command in enumerate(batch):
            if index == 1:
                self.states['input_boolean.ventsys_failsafe'] = 'on'
            if self.blocked():
                break
            published.append(command)
        self.assertEqual(published, batch[:1])

    def test_fire_stops_normal_paths_before_direct_nonretained_commands(self):
        sequence = self.scripts[FIRE]['sequence']
        self.assertEqual(sequence[0]['action'], 'script.turn_off')
        targets = sequence[0]['target']['entity_id']
        self.assertIn('script.' + EXECUTOR, targets)
        self.assertIn('script.ventsys_dashboard_command', targets)
        self.assertNotIn('script.' + FIRE, targets)
        for name in self.scripts:
            if name != FIRE:
                self.assertIn('script.' + name, targets)
        self.assertTrue(all(action['action'] == 'mqtt.publish' for action in sequence[1:]))
        self.assertTrue(all(action['data']['retain'] is False for action in sequence[1:]))
        self.assertEqual([{k: a['data'][k] for k in ('topic','payload')} for a in sequence[1:]],
                         commands(self.source['script'][FIRE]['sequence']))

    def test_rejects_invalid_batches_before_publish(self):
        for batch in [None, [], {}, 'bad', [{}], [None], [{'topic': 'other', 'payload': '100'}],
                      [{'topic':'ventsys/fan/control','payload':'toggle'}]]:
            self.assertTrue(self.invalid(batch), repr(batch))
        for value in [True, False, 100.0, '101', '-1', '1.5', '01', 'nan', '100.0']:
            self.assertTrue(self.invalid([{'topic':'ventsys/main/valve1/control','payload':value}]), repr(value))
        valid = {'topic':'ventsys/main/valve1/control','payload':'100'}
        self.assertTrue(self.invalid([valid] * 13))
        self.assertFalse(self.invalid([valid]))
        # HA renders numeric templates natively, even after a string filter.
        self.assertFalse(self.invalid([{**valid, 'payload': 100}]))
        self.assertTrue(self.invalid([{**valid, 'retain': True}]))

    def test_unknown_recipe_flow_is_rejected(self):
        for sequence in [[{'delay': 1}], [{'if': [], 'then': []}], [{'action': 'script.unrelated'}]]:
            with self.assertRaises(ValueError):
                commands(sequence)

    def test_dashboard_and_legacy_helper_route_through_dispatcher(self):
        dashboard = yaml.safe_load((ROOT / 'configs/home-assistant/ventsys_dashboard_package.yaml').read_text(encoding='utf-8'))
        candidate = build_dashboard(dashboard)
        dispatch = next(step for step in candidate['script']['ventsys_dashboard_command']['sequence'] if 'choose' in step)
        self.assertEqual(dispatch['default'][0]['action'], 'script.' + EXECUTOR)
        self.assertEqual(self.scripts['ventsys_ramp_valve']['sequence'][0]['action'], 'script.' + EXECUTOR)
        self.assertEqual(candidate, dashboard)

    def test_probe_has_only_isolated_targets_and_generated_release_matches(self):
        from generate_ventsys_arbitration_probe import probe
        probe()  # Recursive service/target allowlist audit is mandatory at generation.
        runtime = yaml.safe_load((ROOT / 'configs/home-assistant/ventsys_ha_scripts_arbitrated.yaml').read_text(encoding='utf-8'))
        self.assertEqual(set(runtime['script']), set(self.scripts))
        self.assertEqual(runtime['script']['ventsys_ramp_valve'], self.scripts['ventsys_ramp_valve'])
        for name, recipe in runtime['script'].items():
            if name.startswith('ventsys_mode_') and name != FIRE:
                self.assertEqual(recipe['sequence'][0]['action'], 'script.ventsys_set_operating_mode')


if __name__ == '__main__':
    unittest.main()
