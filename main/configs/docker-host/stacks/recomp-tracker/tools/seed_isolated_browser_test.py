"""Seed only the explicitly named isolated review server, never production."""
import os
import requests
if os.environ.get('RECOMP_ISOLATED_TEST') != '1':
    raise SystemExit('Refusing to replace records: set RECOMP_ISOLATED_TEST=1 only for the disposable review server.')
BASE = 'http://127.0.0.1:18421'
assert requests.get(BASE + '/healthz', timeout=5).ok
exercise = {'exerciseId': 'test-squat', 'name': 'QA squat', 'target': {'min': 1, 'max': 5, 'unit': 'reps'}, 'sets': [{'reps': '5', 'load': '', 'rpe': '', 'done': True}]}
sessions = [{'id': 'qa-' + str(i), 'date': '2026-09-16', 'routineName': 'QA pagination', 'exercises': [exercise]} for i in range(65)]
workouts = requests.get(BASE + '/api/kv/workout-log', timeout=5).json()
active = requests.get(BASE + '/api/kv/active-workout', timeout=5).json()
result = requests.post(BASE + '/api/kv-batch', json={'data': {'workouts': {'sessions': sessions, 'trash': []}, 'active': {'id': None, 'date': '2026-09-16', 'routineName': 'QA completion', 'exercises': [exercise], 'elapsedSeconds': 30}}, 'versions': {'workouts': workouts['version'], 'active': active['version']}}, timeout=5)
result.raise_for_status()
print('Isolated review fixture: 65 workouts plus active draft')
