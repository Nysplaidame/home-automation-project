import json
import unittest
from pathlib import Path
from jinja2.nativetypes import NativeEnvironment
import yaml

class ReferenceGuardTests(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]
        self.script=yaml.safe_load((root/'configs/home-assistant/ventsys_reference_controls.yaml').read_text(encoding='utf-8'))['script']['ventsys_record_intake_reference']
        self.seq=self.script['sequence'];self.devices=self.seq[0]['variables']['devices']
        self.env=NativeEnvironment();self.states={'input_boolean.ventsys_failsafe':'off','script.ventsys_mode_fire_safe':'off','script.ventsys_set_operating_mode':'off','script.ventsys_test_valves':'off','script.ventsys_normal_command':'off','script.ventsys_dashboard_command':'off','fan.inline_fan':'off','fan.spray_booth_fan':'off'}
        self.env.globals['is_state']=lambda key,value:self.states.get(key)==value
        self.saved={'fdm':'off','sla':'off','booth':'off','revision':2}
    def blocked(self,**updates):
        args={'target':'fdm_360','opening':50,'revision':2,'saved':self.saved,'devices':self.devices};args.update(updates)
        return self.env.from_string(self.seq[1]['if'][0]['value_template']).render(**args)
    def test_all_off_is_allowed(self): self.assertFalse(self.blocked())
    def test_active_stale_and_invalid_are_rejected(self):
        for change in ({'target':'main1'},{'opening':101},{'opening':True},{'revision':1},{'saved':self.saved|{'sla':'purge'}}):
            self.assertTrue(self.blocked(**change))
        self.states['fan.inline_fan']='unavailable';self.assertTrue(self.blocked())
    def test_inverse_mapping_and_physical_service_identity(self):
        self.assertEqual(self.devices['fdm_360']['service'],'esphome.ventsys_sla_360_valve_record_known_command')
        self.assertEqual(self.devices['sla_360']['service'],'esphome.ventsys_fdm_360_valve_record_known_command')
        raw=self.env.from_string(self.seq[2]['variables']['raw'])
        self.assertEqual([raw.render(opening=n) for n in [0,50,100]],[30,45,60])

if __name__ == '__main__': unittest.main()
