"""Isolated transaction/restore regression tests; no production DB or scheduler."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app


class ReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        app.DB_PATH = os.path.join(self.tmp.name, 'test.db')
        app.init_db()
        self.client = app.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def batch(self, data, versions, **extra):
        return self.client.post('/api/kv-batch', json=dict(data=data, versions=versions, **extra))

    def test_root_service_worker(self):
        response = self.client.get('/service-worker.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn('javascript', response.content_type)
        self.assertEqual(response.headers['Cache-Control'], 'no-cache')
        self.assertEqual(response.data, self.client.get('/static/service-worker.js').data)

    def test_atomic_conflict(self):
        v, _ = app.kv_set('health-log', json.dumps({'entries': {}}))
        reply = self.batch({'health': {'entries': {}}, 'workouts': {'sessions': []}}, {'health': 'stale', 'workouts': None})
        self.assertEqual(reply.status_code, 409)
        self.assertIsNone(app.kv_get('workout-log'))
        self.assertEqual(app.kv_get('health-log')['updated_at'], v)

    def test_first_writer_conflict(self):
        self.assertEqual(self.batch({'workouts': {'sessions': []}}, {'workouts': None}).status_code, 200)
        self.assertEqual(self.batch({'workouts': {'sessions': []}}, {'workouts': None}).status_code, 409)

    def test_invalid_backup_no_partial_write(self):
        reply = self.batch({'health': {'entries': {}}, 'workouts': {'sessions': [None]}}, {'health': None, 'workouts': None}, snapshot=True)
        self.assertEqual(reply.status_code, 400)
        self.assertIsNone(app.kv_get('health-log'))
        self.assertIsNone(app.kv_get('pre-import-snapshot'))

    def test_snapshot_and_clear_draft(self):
        draft = {'exercises': [], 'date': '2026-09-16'}
        v, _ = app.kv_set('active-workout', json.dumps(draft))
        reply = self.batch({'active': None, 'workouts': {'sessions': []}}, {'active': v, 'workouts': None}, snapshot=True)
        self.assertEqual(reply.status_code, 200)
        self.assertIsNone(json.loads(app.kv_get('active-workout')['value']))
        snapshot = json.loads(app.kv_get('pre-import-snapshot')['value'])
        self.assertEqual(snapshot['data']['active'], draft)

    def test_duplicate_and_malformed_sessions_rejected(self):
        session = {'id': 'one', 'date': '2026-09-16', 'exercises': []}
        for sessions in ([session, session], [None], [{}], [{'id': 'one', 'date': '2026-09-16', 'exercises': [None]}]):
            reply = self.client.post('/api/backup/validate', json={'schemaVersion': 12, 'data': {'workouts': {'sessions': sessions}}})
            self.assertEqual(reply.status_code, 400)

    def test_trash_roundtrip(self):
        session = {'id': 'one', 'date': '2026-09-16', 'exercises': []}
        data = {'sessions': [], 'trash': [{'id': 'one', 'session': session, 'deletedAt': '2026-09-16'}]}
        self.assertEqual(self.batch({'workouts': data}, {'workouts': None}).status_code, 200)
        self.assertEqual(json.loads(app.kv_get('workout-log')['value']), data)

    def test_quantity_constant_validation_and_schema_13(self):
        valid = {'constants': [{'id': 'daily-yogurt', 'name': 'Yogurt', 'foodId': 'recipe-yogurt', 'quantity': 200, 'sourceMode': 'per100'}], 'targets': {}}
        self.assertEqual(self.client.post('/api/backup/validate', json={'schemaVersion': 13, 'data': {'dietSettings': valid}}).status_code, 200)
        invalid = {'constants': [{'id': 'daily-yogurt', 'name': 'Yogurt', 'quantity': 0}], 'targets': {}}
        self.assertEqual(self.client.post('/api/backup/validate', json={'schemaVersion': 13, 'data': {'dietSettings': invalid}}).status_code, 400)
        invalid_mode = {'constants': [{'id': 'daily-yogurt', 'name': 'Yogurt', 'quantity': 200, 'sourceMode': 'unknown'}], 'targets': {}}
        self.assertEqual(self.client.post('/api/backup/validate', json={'schemaVersion': 13, 'data': {'dietSettings': invalid_mode}}).status_code, 400)

    def test_one_time_meal_validation(self):
        valid = {'days': {'2026-10-19': {'meals': {}, 'oneTimeMeals': [{'id': 'estimate-1', 'name': 'Restaurant lunch estimate', 'checked': True, 'calories': 850, 'protein': 35.5, 'carbs': 91, 'fat': 32}]}}}
        self.assertEqual(self.batch({'diet': valid}, {'diet': None}).status_code, 200)
        invalid = {'days': {'2026-10-19': {'meals': {}, 'oneTimeMeals': [{'name': 'x' * 141, 'calories': -1}]}}}
        self.assertEqual(self.client.post('/api/backup/validate', json={'schemaVersion': 13, 'data': {'diet': invalid}}).status_code, 400)


if __name__ == '__main__':
    unittest.main()
