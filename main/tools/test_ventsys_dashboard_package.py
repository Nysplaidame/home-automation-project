"""Exercise command guards without HA, MQTT or physical devices."""
import unittest
from pathlib import Path
from types import SimpleNamespace
import yaml
from jinja2.nativetypes import NativeEnvironment
from generate_ventsys_dashboard_contract import expected_modes

ROOT = Path(__file__).resolve().parents[1]

class States:
    def __init__(self, mapping): self.mapping = mapping
    def __getitem__(self, key): return self.mapping.get(key)
    def __call__(self, key): return self.mapping.get(key, SimpleNamespace(state='unknown')).state

class CommandPackageTests(unittest.TestCase):
    def setUp(self):
        self.script = yaml.safe_load((ROOT/'configs/home-assistant/ventsys_dashboard_package.yaml').read_text(encoding='utf-8'))['script']['ventsys_dashboard_command']
        self.sequence = self.script['sequence'][2:]; self.variables = self.sequence[0]['variables']
        self.mapping = {}
        for key, device in self.variables['controls'].items():
            self.mapping[next(iter(device['native']),device['entity'])] = SimpleNamespace(state='off' if device.get('fan') else '50',attributes={'min':0,'max':100,'percentage':50})
        self.states = States(self.mapping)
        self.env = NativeEnvironment()
        self.env.globals.update(states=self.states, is_state=lambda id,value: self.states(id)==value,
                                is_number=lambda value: str(value).replace('.','',1).replace('-','',1).isdigit())
    def render(self, template, **variables):
        return self.env.from_string(template).render(**self.variables, **variables)
    def invalid_value(self, **variables): return self.render(self.sequence[3]['if'][0]['value_template'],**variables)
    def blocked(self, expected): return str(self.render(self.sequence[5]['variables']['blocked'],expected=expected)).strip()
    def test_exact_mode_contract(self): self.assertEqual(self.variables['mode_expected'],expected_modes())
    def test_360_confirmation_entities_and_topics_follow_current_roles(self):
        fdm=self.variables['controls']['fdm_360'];sla=self.variables['controls']['sla_360']
        self.assertEqual(fdm['native'],['number.ventsys_sla_360_intake_valve_valve_position'])
        self.assertEqual(sla['native'],['number.ventsys_fdm_360_intake_valve_valve_position'])
        self.assertEqual(fdm['topic'],'ventsys/sla/360/control')
        self.assertEqual(sla['topic'],'ventsys/fdm/360/control')
        self.assertEqual(fdm['expectedRange'],{'min':30,'max':60})
        self.assertEqual(self.variables['mode_expected']['sealed']['fdm_360'],30)
        self.assertEqual(self.variables['mode_expected']['purge']['sla_360'],60)

    def test_partial_mode_is_frozen_to_exact_reviewed_keys_and_topics(self):
        args={'kind':'mode','target':'purge','scope':'available','included':['fdm_360','sla_branch']}
        self.assertFalse(self.render(self.sequence[2]['if'][0]['value_template'],**args))
        expected=self.render(self.sequence[4]['variables']['expected'],**args)
        self.assertEqual(expected,{'fdm_360':60,'sla_branch':100})
        commands=self.render(self.sequence[7]['default'][0]['data']['commands'],expected=expected)
        self.assertEqual(commands,[{'topic':'ventsys/sla/360/control','payload':'60'},{'topic':'ventsys/sla/branch/control','payload':'100'}])
        self.assertNotIn('ventsys/fan/control',[c['topic'] for c in commands])
        self.mapping[self.variables['controls']['fdm_360']['native'][0]].state='unavailable'
        self.assertIn('unavailable',self.blocked(expected))

    def test_partial_scope_rejects_missing_empty_unknown_or_wrong_kind_keys(self):
        template=self.sequence[2]['if'][0]['value_template']
        for included in [None,[],['arbitrary'],['fdm_360','fdm_360'],'fdm_360']:
            self.assertTrue(self.render(template,kind='mode',target='purge',scope='available',included=included))
        self.assertTrue(self.render(template,kind='position',target='main1',scope='available',included=['main1']))
        self.assertTrue(self.render(template,kind='mode',target='purge',scope='full',included=['main1']))
    def test_single_dispatcher_and_nonretained_publish(self):
        self.assertEqual(self.script['mode'],'single')
        self.assertEqual(self.sequence[7]['default'][0]['action'], 'script.ventsys_normal_command')
        self.assertEqual(self.sequence[-1]['timeout'],'00:00:08')
        self.assertFalse(self.sequence[-1]['continue_on_timeout'])
    def test_rejects_arbitrary_targets_and_kinds(self):
        template=self.sequence[2]['if'][0]['value_template']
        for kind,target in [('mqtt','main1'),('mode','fire_safe'),('position','__proto__'),('mode','script.unrelated')]:
            self.assertTrue(self.render(template,kind=kind,target=target,value=0))
    def test_rejects_invalid_percentages_and_wrong_device_kind(self):
        for value in [True,False,None,-1,101,0.5,'100','NaN']:
            self.assertTrue(self.invalid_value(kind='position',target='main1',value=value),repr(value))
        self.assertTrue(self.invalid_value(kind='fan',target='main1',value='on'))
        self.assertTrue(self.invalid_value(kind='speed',target='main1',value=50))
        self.assertTrue(self.invalid_value(kind='fan',target='fan_main',value='toggle'))
    def test_valid_percentages_including_full_travel(self):
        for value in [0,25,50,75,100]: self.assertFalse(self.invalid_value(kind='position',target='main1',value=value))
        self.assertFalse(self.invalid_value(kind='fan',target='fan_main',value='off'))
        self.assertFalse(self.invalid_value(kind='speed',target='fan_main',value=100))
    def test_failsafe_unknown_and_on_both_lock(self):
        template=self.sequence[1]['if'][0]['value_template']
        self.assertTrue(self.render(template))
        self.mapping['input_boolean.ventsys_failsafe']=SimpleNamespace(state='on')
        self.assertTrue(self.render(template))
        self.mapping['input_boolean.ventsys_failsafe'].state='off'
        self.assertFalse(self.render(template))
    def test_unavailable_native_cannot_use_retained_alias(self):
        self.mapping['number.ventsys_main_duct_valve_1_valve_position'].state='unavailable'
        self.mapping['number.main_duct_valve_1']=SimpleNamespace(state='100',attributes={})
        self.assertIn('unavailable',self.blocked({'main1':100}))
    def test_range_and_unadopted_guards(self):
        self.mapping['number.ventsys_main_duct_valve_1_valve_position'].attributes['max']=60
        self.assertIn('firmware range',self.blocked({'main1':100}))
        self.mapping.pop('number.ventsys_main_duct_valve_1_valve_position')
        self.mapping['number.main_duct_valve_1']=SimpleNamespace(state='100',attributes={})
        self.assertIn('not adopted',self.blocked({'main1':100}))
    def test_bad_report_is_blocked(self):
        self.mapping['number.ventsys_main_duct_valve_1_valve_position'].state='broken'
        self.assertIn('Invalid position',self.blocked({'main1':100}))
    def test_wait_requires_all_expected_reports(self):
        template=self.sequence[-1]['wait_template']
        self.assertFalse(self.render(template,expected={'main1':100,'main2':100}))
        self.mapping['number.ventsys_main_duct_valve_1_valve_position'].state='100'
        self.assertFalse(self.render(template,expected={'main1':100,'main2':100}))
        self.mapping['number.garage_ventsys_main_duct_valve_2_valve_position'].state='100'
        self.assertTrue(self.render(template,expected={'main1':100,'main2':100}))

if __name__=='__main__': unittest.main()
