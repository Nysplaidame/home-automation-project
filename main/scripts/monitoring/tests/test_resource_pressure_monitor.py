import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import json
import tempfile
import subprocess

spec = importlib.util.spec_from_file_location('monitor', Path(__file__).parents[1] / 'resource_pressure_monitor.py')
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


class PressureTests(unittest.TestCase):
    def test_empty_kernel_grep_is_healthy_but_errors_are_not(self):
        with patch.object(monitor.subprocess, 'run', return_value=SimpleNamespace(
                returncode=1, stdout='', stderr='')):
            self.assertEqual(monitor.command(['journalctl'], allow_empty=True), '')
        with patch.object(monitor.subprocess, 'run', return_value=SimpleNamespace(
                returncode=1, stdout='', stderr='permission denied')):
            with self.assertRaises(RuntimeError):
                monitor.command(['journalctl'], allow_empty=True)

    def test_debounce_recovery_and_repeat(self):
        bad = [('host:io', True, 'stall', False)]
        states, messages = monitor.transition(bad, {}, 100)
        self.assertEqual(messages, [])
        states, messages = monitor.transition(bad, states, 160)
        self.assertEqual(messages, [])
        states, messages = monitor.transition(bad, states, 220)
        self.assertEqual(len(messages), 1)
        states['host:io'].update(active=True, last_sent=220)
        states, messages = monitor.transition(bad, states, 280)
        self.assertEqual(messages, [])
        states, messages = monitor.transition(bad, states, 3820)
        self.assertEqual(messages[0][-1], 'alert')
        for now in (3880, 3940, 4000):
            states, messages = monitor.transition([('host:io', False, 'healthy', False)], states, now)
        self.assertEqual(messages[0][-1], 'recover')

    def test_oom_failed_delivery_retry(self):
        states, messages = monitor.transition([('111:oom', True, 'new OOM', True)], {}, 100)
        self.assertEqual(messages[0][-1], 'event')
        states, messages = monitor.transition([('111:oom', False, 'zero', True)], states, 160)
        self.assertEqual(messages[0][2], 'new OOM')

    def test_historical_and_reset_oom_do_not_alert(self):
        sample = dict(available_pct=50, available_mib=1000, memory_psi=0, io_psi=0,
                      oom=2, disk_pct=40)
        snapshot = dict(samples={'111': sample}, blocked=0, load=0, cpus=8,
                        thin_pct=27, thin_metadata_pct=1, expected=['111'], errors={})
        self.assertFalse(next(c for c in monitor.evaluate(snapshot, {}) if c[0] == '111:oom')[1])
        old = {'samples': {'111': dict(sample, oom=3)}}
        self.assertFalse(next(c for c in monitor.evaluate(snapshot, old) if c[0] == '111:oom')[1])
        old['samples']['111']['oom'] = 1
        self.assertTrue(next(c for c in monitor.evaluate(snapshot, old) if c[0] == '111:oom')[1])


class ErrorHandlingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.state_patch = patch.object(monitor, 'STATE', Path(self.directory.name))
        self.state_patch.start()
        self.config = {}

    def tearDown(self):
        self.state_patch.stop()
        self.directory.cleanup()

    def snapshot(self, now, oom=2, bad=False, missing=False):
        return dict(timestamp=now, boot_id='same-boot', samples={} if missing else
                    {'111':dict(available_pct=5 if bad else 50, available_mib=100 if bad else 1000,
                                memory_psi=0, io_psi=0, oom=oom, disk_pct=40)},
                    expected=['111'], errors={'111':'unavailable'} if missing else {},
                    inventory=[], load=0, cpus=8, blocked=0, thin_pct=27,
                    thin_metadata_pct=1, kernel_warning=None)

    def test_failure_debounce_cooldown_and_recovery(self):
        with patch.object(monitor, 'notify') as send:
            for now in (100,160):
                monitor.collector_health({}, 'TimeoutExpired', now=now)
            send.assert_not_called()
            monitor.collector_health({}, 'TimeoutExpired', now=220)
            self.assertEqual(send.call_count,1)
            monitor.collector_health({}, 'TimeoutExpired', immediate=True, now=280)
            self.assertEqual(send.call_count,1)
            result=monitor.collector_health({}, now=300)
            self.assertEqual(send.call_count,2)
            self.assertFalse(result['active'])
            self.assertNotIn('pending',result)
            self.assertIn('recovered',send.call_args.args[1])

    def test_health_delivery_retry_reports_recovered_incident(self):
        with patch.object(monitor, 'notify', side_effect=OSError('offline')):
            result=monitor.collector_health({},'TimeoutExpired',immediate=True,now=100)
            self.assertTrue(result['delivery_error'])
        with patch.object(monitor,'notify') as send:
            result=monitor.collector_health({},now=160)
            self.assertIn('incident recovered',send.call_args.args[1])
            self.assertNotIn('pending',result)
            self.assertNotIn('delivery_error',result)

    def test_collection_failure_does_not_fake_fresh_sample(self):
        original=self.snapshot(100)
        monitor.atomic_json(monitor.STATE/'state.json',{'snapshot':original,'checks':{}})
        monitor.atomic_json(monitor.STATE/'latest.json',original)
        with patch.object(monitor,'collect',side_effect=subprocess.TimeoutExpired('pvesh',10)):
            monitor.run_check({})
        self.assertEqual(json.loads((monitor.STATE/'latest.json').read_text()),original)
        self.assertEqual(json.loads((monitor.STATE/'collector-health.json').read_text())['failures'],1)

    def test_failed_resource_alert_survives_condition_recovery(self):
        checks={'111:memory':dict(bad_count=2,bad_since=100)}
        monitor.atomic_json(monitor.STATE/'state.json',{'snapshot':self.snapshot(160),'checks':checks})
        with patch.object(monitor,'collect',return_value=self.snapshot(220,bad=True)), \
                patch.object(monitor,'notify',side_effect=OSError('offline')):
            monitor.run_check({})
        state=json.loads((monitor.STATE/'state.json').read_text())
        self.assertIn('undelivered',state['checks']['111:memory'])
        with patch.object(monitor,'collect',return_value=self.snapshot(280)), \
                patch.object(monitor,'notify') as send:
            monitor.run_check({})
            self.assertIn('incident recovered',send.call_args.args[1])
        state=json.loads((monitor.STATE/'state.json').read_text())
        self.assertFalse(state['checks']['111:memory']['active'])
        self.assertNotIn('undelivered',state['checks']['111:memory'])
        self.assertEqual(state['delivery_errors'],[])

    def test_oom_baseline_survives_missing_guest_sample(self):
        monitor.atomic_json(monitor.STATE/'state.json',{'snapshot':self.snapshot(100),'checks':{}})
        with patch.object(monitor,'collect',return_value=self.snapshot(160,missing=True)):
            monitor.run_check({})
        with patch.object(monitor,'collect',return_value=self.snapshot(220,oom=3)), \
                patch.object(monitor,'notify') as send:
            monitor.run_check({})
            self.assertEqual(send.call_args.args[1],'OOM detected')
            self.assertIn('1 new OOM',send.call_args.args[2])

    def test_inventory_timeout_keeps_fresh_host_data_and_marks_coverage(self):
        raw=('MemTotal: 1048576 kB\nMemAvailable: 524288 kB\n__MEMPSI__\n'
             'some avg60=0\n__IOPSI__\nsome avg60=0\n__VMSTAT__\noom_kill 0\n'
             '__DISK__\nFilesystem blocks used available capacity mount\n/dev/root 100 40 60 40% /\n')
        def run(args,**kwargs):
            if args[0]=='pvesh': raise subprocess.TimeoutExpired('pvesh',10)
            if args[0]=='/bin/sh': return raw
            if args[0]=='lvs': return '27 1'
            if args[0]=='journalctl': return ''
            raise AssertionError(args)
        with patch.object(monitor,'command',side_effect=run):
            result=monitor.collect({'expected_guests':[]})
        self.assertIn('host',result['samples'])
        self.assertFalse(result['inventory_valid'])
        self.assertIn('collector:inventory',result['errors'])


if __name__ == '__main__':
    unittest.main()
