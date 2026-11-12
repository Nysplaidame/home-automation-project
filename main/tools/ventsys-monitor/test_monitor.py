import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import monitor


class MonitorTests(unittest.TestCase):
    def test_wrong_identity_and_unknown_mac(self):
        roster = {'ece334b4797c': {'name': 'ventsys-sla-branch-valve', 'ip': '192.168.50.52'}}
        good = {'mac': 'EC:E3:34:B4:79:7C', 'name': 'ventsys-sla-branch-valve', 'ip': '192.168.50.52'}
        self.assertIsNone(monitor.mismatch(good, roster))
        self.assertIn('Discovery conflict', monitor.mismatch(dict(good, ip='192.168.50.51'), roster))
        self.assertIn('Unknown', monitor.mismatch(dict(good, mac='abcdef'), roster))

    def test_incident_dedup_retry_persistence_and_recovery(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(monitor, 'ROOT', Path(folder)):
            config = {'ca': '', 'roster': []}
            with patch.object(monitor.ssl, 'create_default_context'):
                instance = monitor.Monitor(config)
                with patch.object(instance, 'notify') as notify:
                    instance.incident('offline', 'down', 2)
                    notify.assert_not_called()
                    instance.incident('offline', 'down', 2)
                    instance.incident('offline', 'down', 2)
                    notify.assert_called_once_with('down')
                resumed = monitor.Monitor(config)
                with patch.object(resumed, 'notify') as notify:
                    resumed.incident('offline', 'down', 2)
                    notify.assert_not_called()
                    resumed.incident('offline', None)
                    resumed.incident('offline', None)
                    notify.assert_called_once_with('Recovered: down')
                with patch.object(resumed, 'notify', side_effect=OSError):
                    resumed.incident('conflict', 'bad identity')
                self.assertNotIn('sent', resumed.state['conflict'])
                with patch.object(resumed, 'notify') as notify:
                    resumed.incident('conflict', 'bad identity')
                    notify.assert_called_once_with('bad identity')

    def test_transient_discovery_not_lost_between_ticks(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(monitor, 'ROOT', Path(folder)):
            config = {'ca': '', 'roster': [{'mac': 'aa', 'name': 'right', 'ip': '1'}]}
            with patch.object(monitor.ssl, 'create_default_context'):
                instance = monitor.Monitor(config)
            instance.pending = [('esphome/discover/test', json.dumps({'mac': 'aa', 'name': 'wrong', 'ip': '1'})),
                                ('esphome/discover/test', json.dumps({'mac': 'aa', 'name': 'right', 'ip': '1'}))]
            with patch.object(instance, 'notify') as notify:
                instance.reconcile_discovery()
                self.assertEqual(notify.call_count, 2)
                self.assertTrue(notify.call_args.args[0].startswith('Recovered:'))

if __name__ == '__main__':
    unittest.main()
