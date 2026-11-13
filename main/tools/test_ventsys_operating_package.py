"""Actual generated HA templates and transition failure semantics, no devices."""
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
import yaml
from jinja2.nativetypes import NativeEnvironment
from ventsys_operating_modes import EMPTY, STATES, REQUESTS, transition, with_strength

ROOT = Path(__file__).resolve().parents[1]


class StateLookup:
    def __init__(self, mapping): self.mapping = mapping
    def __call__(self, key): return self.mapping.get(key, SimpleNamespace(state='unknown')).state
    def __getitem__(self, key): return self.mapping.get(key)


class OperatingPackageTests(unittest.TestCase):
    def setUp(self):
        self.package = yaml.safe_load((ROOT / 'configs/home-assistant/ventsys_operating_modes.yaml').read_text(encoding='utf-8'))
        self.runtime = yaml.safe_load((ROOT / 'configs/home-assistant/ventsys_ha_scripts_arbitrated.yaml').read_text(encoding='utf-8'))
        self.script = self.package['script']['ventsys_set_operating_mode']
        self.sequence = self.script['sequence']
        self.context = dict(self.sequence[0]['variables'])
        self.mapping = {}
        self.states = StateLookup(self.mapping)
        self.env = NativeEnvironment()
        self.env.filters['from_json'] = lambda value, default=None: self.parse(value, default)
        self.env.filters['to_json'] = json.dumps
        self.env.globals.update(states=self.states, is_state=lambda k, v: self.states(k) == v,
                                is_number=lambda value: str(value).replace('.', '', 1).isdigit())
        for k in ('input_boolean.ventsys_failsafe', 'script.ventsys_mode_fire_safe', 'script.ventsys_normal_command', 'script.ventsys_dashboard_command', 'script.ventsys_set_operating_mode', 'script.ventsys_test_valves', 'script.ventsys_record_intake_reference'):
            self.mapping[k] = SimpleNamespace(state='off')
        for key, device in self.context['controls'].items():
            self.mapping[next(iter(device['native']), device['entity'])] = SimpleNamespace(
                state='off' if device.get('fan') else '50', attributes={'min': device.get('expectedRange', {}).get('min', 0),
                'max': device.get('expectedRange', {}).get('max', 100), 'percentage': 50})

    @staticmethod
    def parse(value, default):
        try: return json.loads(value)
        except (ValueError, TypeError): return default

    def render(self, template, **values): return self.env.from_string(template).render(**(self.context | values))

    def test_all_generated_templates_compile(self):
        def walk(node):
            if isinstance(node, str) and ('{{' in node or '{%' in node): self.env.from_string(node)
            elif isinstance(node, dict):
                for value in node.values(): walk(value)
            elif isinstance(node, list):
                for value in node: walk(value)
        walk(self.package); walk(self.runtime)

    def test_every_generated_plan_matches_canonical_planner(self):
        for key, old in STATES.items():
            for zone, mode in REQUESTS:
                self.assertEqual(self.context['plans'][key][zone + ':' + mode], transition(old, zone, mode))

    def test_native_state_plan_revision_and_stale_requests(self):
        for raw in ['', 'unknown', json.dumps(EMPTY | {'revision': 4})]:
            self.mapping['input_text.ventsys_operating_state'] = SimpleNamespace(state=raw)
            current = self.render(self.sequence[1]['variables']['current'])
            self.assertIsInstance(current, dict)
            values = {'current': current, 'zone': 'sla', 'operation': 'print', 'revision': current['revision']}
            for key, template in self.sequence[2]['variables'].items(): values[key] = self.render(template, **values)
            self.assertFalse(self.render(self.sequence[5]['if'][0]['value_template'], **values))
            values['revision'] += 1
            self.assertTrue(self.render(self.sequence[5]['if'][0]['value_template'], **values))

    def test_preflight_blocks_missing_required_controller_and_zero_speed(self):
        expected = transition(EMPTY, 'sla', 'print')['targets']
        availability = self.sequence[8]['variables']['blocked']
        self.assertEqual(self.render(availability, expected=expected), '')
        self.mapping['number.ventsys_e2_branch_valve_valve_position'].state = 'unavailable'
        self.assertIn('unavailable', self.render(availability, expected=expected))
        guard = self.sequence[10]['if'][0]['value_template']
        self.assertFalse(self.render(guard, expected=expected))
        self.mapping['fan.inline_fan'].attributes['percentage'] = 0
        self.assertTrue(self.render(guard, expected=expected))

    def test_generated_strength_template_matches_planner_and_percentage_topic(self):
        template=self.sequence[6]['variables']['plan']
        for fdm in (2,4,6,8,10):
            for sla in (2,4,6,8,10):
                old={'fdm':'purge','sla':'purge','booth':'enclosure','fdm_strength':fdm,'sla_strength':sla}
                for zone,mode,level in [('fdm','purge',2),('sla','off',None),('both','purge',8)]:
                    key='purge|purge|enclosure'
                    actual=self.render(template,current=old,current_key=key,request_key=zone+':'+mode,zone=zone,strength=level)
                    expected=with_strength(transition({k:old[k] for k in EMPTY},zone,mode),old,zone,mode,level)
                    self.assertEqual(actual,expected)
        phase=self.sequence[13]['repeat']['sequence'][4]['data']['commands']
        self.assertEqual(self.render(phase,expected={'fan_main_speed':80}),[{'topic':'ventsys/fan/percent','payload':'80'}])

    def test_dispatcher_rejects_conflicting_batches_before_any_publish(self):
        executor = self.runtime['script']['ventsys_normal_command']['sequence']
        self.context.update(executor[0]['variables'])
        conflict = executor[2]['if'][0]['value_template']
        self.mapping['input_text.ventsys_operating_state'] = SimpleNamespace(state=json.dumps({'fdm':'print','sla':'purge','booth':'enclosure','revision':1}))
        for topic, value in [('ventsys/main/valve1/control', '0'), ('ventsys/main/valve2/control', '0'),
                             ('ventsys/fan/control', 'off'), ('ventsys/sla/360/control', '60'), ('ventsys/fan/percent', '0')]:
            self.assertTrue(self.render(conflict, commands=[{'topic':topic, 'payload':value}]))
        self.assertFalse(self.render(conflict, commands=[{'topic':'ventsys/main/valve1/control','payload':'100'}]))
        self.mapping['script.ventsys_set_operating_mode'].state='on'
        matching=[{'topic':'ventsys/main/valve1/control','payload':'100'}]
        self.assertTrue(self.render(conflict,commands=matching))
        self.assertFalse(self.render(conflict,commands=matching,operating=True))
        self.assertTrue(self.render(conflict,commands=matching,operating='true'))
        self.mapping['script.ventsys_set_operating_mode'].state='off'
        self.assertTrue(self.render(conflict,commands=matching,operating=True))
        self.mapping['input_text.ventsys_operating_state'].state=json.dumps({'fdm':'off','sla':'off','booth':'off','revision':0})
        self.mapping['script.ventsys_test_valves'].state='on'
        self.assertTrue(self.render(conflict,commands=matching))
        self.assertFalse(self.render(conflict,commands=matching,testing=True))
        self.assertTrue(self.render(conflict,commands=[{'topic':'ventsys/fan/control','payload':'on'}],testing=True))
        self.mapping['fan.inline_fan'].state='on'
        self.assertTrue(self.render(conflict,commands=matching,testing=True))
        self.mapping['fan.inline_fan'].state='off'
        self.mapping['script.ventsys_test_valves'].state='off'
        for raw in ['unavailable', '{bad', 'null', '42']:
            self.mapping['input_text.ventsys_operating_state'].state = raw
            self.assertTrue(self.render(conflict, commands=[{'topic':'ventsys/main/valve1/control','payload':'0'}]))

    def test_reference_lock_blocks_other_command_paths_and_fire_stops_it(self):
        self.mapping['script.ventsys_record_intake_reference'].state = 'on'
        self.assertTrue(self.render(self.sequence[4]['if'][0]['value_template']))
        setup=self.package['script']['ventsys_test_valves']['sequence']
        self.assertTrue(self.render(setup[3]['if'][0]['value_template']))
        dashboard=yaml.safe_load((ROOT/'configs/home-assistant/ventsys_dashboard_package.yaml').read_text(encoding='utf-8'))
        self.assertTrue(self.render(dashboard['script']['ventsys_dashboard_command']['sequence'][1]['if'][0]['value_template']))
        fire=self.runtime['script']['ventsys_mode_fire_safe']['sequence'][0]['target']['entity_id']
        self.assertIn('script.ventsys_record_intake_reference', fire)

    def test_failure_and_emergency_do_not_advance_transition(self):
        self.assertEqual(self.script['mode'], 'single')
        phases = self.sequence[13]['repeat']['sequence']
        self.assertIn('Emergency', phases[0]['then'][0]['stop'])
        self.assertEqual(phases[5]['timeout'], '00:00:08')
        failure = phases[6]['then']
        self.assertTrue(failure[-1]['error'])
        fire = self.runtime['script']['ventsys_mode_fire_safe']['sequence']
        self.assertIn('script.ventsys_set_operating_mode', fire[0]['target']['entity_id'])
        self.assertTrue(all(entry['action'] == 'mqtt.publish' for entry in fire[1:]))
        self.assertNotIn('initial', self.package['input_text']['ventsys_operating_state'])

    def test_setup_contract_rejects_fans_stale_and_active_modes(self):
        script=self.package['script']['ventsys_test_valves']; seq=script['sequence']
        self.context.update(seq[0]['variables'])
        args={'current':{'fdm':'off','sla':'off','booth':'off','revision':3},'revision':3,'request_key':'sla:enclosure','included':['sla_branch','sla_360']}
        self.assertFalse(self.render(seq[4]['if'][0]['value_template'],**args))
        self.assertFalse(self.render(seq[6]['if'][0]['value_template'],**args))
        expected=self.render(seq[7]['variables']['expected'],**args)
        self.assertEqual(expected,{'sla_branch':100,'sla_360':60})
        for included in [[],['fan_main'],['sla_branch','sla_branch'],['main2'],None,'sla_branch']:
            self.assertTrue(self.render(seq[6]['if'][0]['value_template'],**(args|{'included':included})))
        self.assertTrue(self.render(seq[4]['if'][0]['value_template'],**(args|{'revision':4})))
        self.assertTrue(self.render(seq[4]['if'][0]['value_template'],**(args|{'current':args['current']|{'fdm':'print'}})))
        self.mapping['fan.inline_fan'].state='on'
        self.assertTrue(self.render(seq[5]['if'][0]['value_template'],**args))
        self.assertFalse(any(step.get('action','').startswith('input_text.') for step in seq))
        for targets in seq[0]['variables']['test_targets'].values():
            self.assertTrue(targets); self.assertFalse(any(k.startswith('fan_') for k in targets))


if __name__ == '__main__': unittest.main()
