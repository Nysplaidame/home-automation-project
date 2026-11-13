import unittest
from ventsys_operating_modes import EMPTY, STATES, REQUESTS, requirements, transition, with_strength


class OperatingModesTests(unittest.TestCase):
    def test_every_transition_preserves_other_intents_and_shared_paths(self):
        for old in STATES.values():
            for zone, mode in REQUESTS:
                plan = transition(old, zone, mode)
                new = plan['desired']
                for other in EMPTY:
                    if zone not in (other, 'all') and not (zone == 'both' and other != 'booth'):
                        self.assertEqual(old[other], new[other])
                self.assertEqual({k: plan['targets'][k] for k in requirements(new)}, requirements(new))
                self.assertEqual({k: v for p in plan['phases'] for k, v in p.items()}, plan['targets'])
                if new['sla'] != 'off' or new['booth'] != 'off':
                    self.assertEqual(plan['targets']['main1'], 100)
                if new['booth'] != 'off':
                    self.assertEqual(plan['targets']['main2'], 100)

    def test_every_phase_preserves_resources_required_by_other_active_intents(self):
        # Prove the transition never sends a conflicting value, including in
        # intermediate batches, for any owner outside the requested zone.
        for old in STATES.values():
            for zone, mode in REQUESTS:
                plan = transition(old, zone, mode)
                other = dict(old)
                changed = ('fdm', 'sla') if zone == 'both' else tuple(EMPTY) if zone == 'all' else (zone,)
                for item in changed:
                    other[item] = 'off'
                protected = requirements(other)
                for phase in plan['phases']:
                    for resource, expected in protected.items():
                        if resource in phase:
                            self.assertEqual(phase[resource], expected, (old, zone, mode, resource, phase))

    def test_opposite_enclosure_modes_remain_independent(self):
        for left in ('enclosure', 'print', 'purge'):
            for right in ('enclosure', 'print', 'purge'):
                old = {'fdm': left, 'sla': right, 'booth': 'enclosure'}
                plan = transition(old, 'fdm', 'off')
                self.assertEqual(plan['desired']['sla'], right)
                self.assertEqual(plan['targets']['sla_360'], 60 if right in ('enclosure', 'purge') else 30)
                self.assertEqual(plan['targets']['sla_print'], 100 if right in ('print', 'purge') else 0)
                self.assertEqual(plan['targets']['main1'], 100)
                self.assertEqual(plan['targets']['main2'], 100)
                self.assertEqual(plan['targets']['fan_main'], 'on')

    def test_documents_interrupted_release_retry_gap(self):
        # Current behavior: the manager saves desired intents before all phases.
        # Once SLA is saved off, a plain retry no longer owns its old targets.
        first = transition({'fdm':'print','sla':'purge','booth':'off'}, 'sla', 'off')
        retry = transition(first['desired'], 'sla', 'off')
        self.assertEqual(first['targets']['sla_branch'], 0)
        self.assertNotIn('sla_branch', retry['targets'])
        self.assertNotIn('sla_print', retry['targets'])
        self.assertNotIn('sla_360', retry['targets'])

    def test_selected_modes_have_correct_inlets(self):
        for mode, intake, printer in [('enclosure', 60, 0), ('print', 30, 100), ('purge', 60, 100)]:
            for zone in ('fdm', 'sla'):
                targets = transition(EMPTY, zone, mode)['targets']
                self.assertEqual(targets[zone + '_360'], intake)
                self.assertEqual(targets[zone + '_print'], printer)
                self.assertEqual(targets[zone + '_branch'], 100)

    def test_starting_fdm_never_closes_unmanaged_other_paths(self):
        targets = transition(EMPTY, 'fdm', 'print')['targets']
        for item in ('sla_branch', 'sla_360', 'sla_print', 'main1', 'main2', 'fan_booth'):
            self.assertNotIn(item, targets)

    def test_stop_sla_preserves_booth_and_fdm(self):
        plan = transition({'fdm': 'print', 'sla': 'purge', 'booth': 'enclosure'}, 'sla', 'off')
        self.assertEqual(plan['targets']['main1'], 100)
        self.assertEqual(plan['targets']['main2'], 100)
        self.assertEqual(plan['targets']['fan_main'], 'on')
        self.assertEqual(plan['targets']['sla_branch'], 0)

    def test_open_before_closing_old_inlet_and_stop_fan_before_sealing(self):
        plan = transition({'fdm': 'enclosure', 'sla': 'off', 'booth': 'off'}, 'fdm', 'print')
        self.assertEqual(plan['phases'][0]['fdm_print'], 100)
        self.assertEqual(plan['phases'][-1]['fdm_360'], 30)
        plan = transition({'fdm': 'print', 'sla': 'off', 'booth': 'off'}, 'fdm', 'off')
        self.assertEqual(plan['phases'][0], {'fan_main': 'off'})

    def test_invalid_states_and_requests(self):
        for state, zone, mode in [({}, 'fdm', 'print'), (EMPTY, 'booth', 'purge'), (EMPTY, 'all', 'purge'),
                                  (EMPTY, 'unknown', 'print'), (EMPTY, 'fdm', 'fire')]:
            with self.assertRaises(ValueError):
                transition(state, zone, mode)

    def test_purge_strength_maximum_is_owned_per_enclosure(self):
        old = {'fdm':'purge','sla':'purge','booth':'enclosure','fdm_strength':4,'sla_strength':10}
        base = {k: old[k] for k in EMPTY}
        for level in (2,4,6,8,10):
            plan = with_strength(transition(base,'fdm','purge'),old,'fdm','purge',level)
            self.assertEqual(plan['targets']['fan_main_speed'],100)
            self.assertEqual(plan['desired']['sla_strength'],10)
            self.assertEqual(plan['desired']['fdm_strength'],level)
            self.assertEqual(plan['phases'][0]['main2'],100)
            fan_phase=next(p for p in plan['phases'] if 'fan_main' in p)
            self.assertEqual(next(iter(fan_phase)),'fan_main_speed')
        plan=with_strength(transition(base,'sla','off'),old,'sla','off')
        self.assertEqual(plan['targets']['fan_main_speed'],40)
        for level in (None,True,3,11,'6'):
            with self.assertRaises(ValueError): with_strength(transition(EMPTY,'both','purge'),EMPTY,'both','purge',level)


if __name__ == '__main__':
    unittest.main()
