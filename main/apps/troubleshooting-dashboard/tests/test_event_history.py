import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))
import event_history as events


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'events.sqlite3'
        self.now = time.time()

    def tearDown(self):
        self.directory.cleanup()

    def sample(self, timestamp=None, active=None):
        return {'snapshot': {'timestamp': timestamp or self.now, 'boot_id': 'boot-one', 'errors': {}},
                'status': {'active_or_pending': active or {}, 'delivery_errors': [], 'collector_health': {}}}

    def test_baseline_duplicates_and_clear(self):
        data = self.sample(active={'111:memory': {'active': True}})
        events.record_monitor(data, self.path)
        events.record_monitor(data, self.path)
        self.assertEqual(events.history(self.path)['total'], 2)
        titles = [row['title'] for row in events.history(self.path)['events']]
        self.assertTrue(any('Present at history start' in title for title in titles))
        events.record_monitor(self.sample(timestamp=self.now + 60), self.path)
        self.assertEqual(events.history(self.path)['total'], 3)
        self.assertTrue(events.history(self.path)['events'][0]['title'].startswith('Cleared'))

    def test_older_publication_cannot_claim_recovery(self):
        events.record_monitor(self.sample(active={'host:io': {'active': True}}), self.path)
        events.record_monitor(self.sample(timestamp=self.now - 60), self.path)
        self.assertEqual(events.history(self.path)['total'], 2)

    def test_delivery_acceptance_is_recorded_once(self):
        data = self.sample()
        data['recent_notifications'] = {'host:oom': self.now - 1000}
        events.record_monitor(data, self.path)
        data['snapshot']['timestamp'] += 60
        data['recent_notifications']['host:oom'] = time.time() + 1
        events.record_monitor(data, self.path)
        events.record_monitor(data, self.path)
        rows = events.history(self.path)['events']
        self.assertEqual(sum(row['title'].startswith('Notification accepted') for row in rows), 1)

    def test_viewer_problem_recovery_and_deduplication(self):
        events.record_viewer(None, self.path)
        events.record_viewer('Stale', self.path)
        events.record_viewer('Stale', self.path)
        events.record_viewer(None, self.path)
        self.assertEqual(events.history(self.path)['total'], 2)

    def test_retention_and_count_cap(self):
        with patch.object(events, 'MAX_EVENTS', 3):
            with events.database(self.path) as connection:
                events.append(connection, 'diagnostic', 'old', 'pass', 'Old', timestamp=self.now - 31 * 86400)
                for index in range(5):
                    events.append(connection, 'diagnostic', str(index), 'pass', str(index))
            result = events.history(self.path)
            self.assertEqual(result['total'], 3)
            self.assertEqual([row['title'] for row in result['events']], ['4', '3', '2'])

    def test_probe_summary_is_bounded(self):
        events.record_probe({'command': 'ping docker', 'ok': False, 'duration_ms': 50, 'output': 'x' * 6000, 'timestamp': self.now}, self.path)
        self.assertLessEqual(len(events.history(self.path)['events'][0]['detail']), 800)

    def test_same_sample_can_publish_new_delivery_state(self):
        data = self.sample(active={'111:memory': {'active': True, 'undelivered': ['queued']}})
        events.record_monitor(data, self.path)
        data['status']['active_or_pending']['111:memory'].pop('undelivered')
        events.record_monitor(data, self.path)
        self.assertTrue(any(row['title'] == 'Cleared: Notification queued: 111:memory' for row in events.history(self.path)['events']))


if __name__ == '__main__':
    unittest.main()
