"""Safety gates and rollback contract; run on Linux, never touches live Docker."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('updater', Path(__file__).with_name('bambuddy-offline-update.py'))
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)

GOOD = '''bambuddy_printers_total 1
bambuddy_printers_connected 1
bambuddy_queue_pending 0
bambuddy_queue_printing 0
bambuddy_printer_connected{printer_id="2"} 1
bambuddy_printer_state{printer_id="2"} 1
bambuddy_bed_target_celsius{printer_id="2"} 0
bambuddy_nozzle_target_celsius{printer_id="2",nozzle="0"} 0
'''

def manifest():
    return {'schema': 1, 'version': '1.2.5.6', 'image_id': 'sha256:' + 'a'*64, 'config_digest': 'sha256:' + 'a'*64,
            'local_tag': 'bambuddy-staged:1.2.5.6-' + 'a'*12,
            'archive_sha256': 'b'*64, 'archive_bytes': 1024,
            'upstream_digest': 'ghcr.io/maziggy/bambuddy@sha256:' + 'c'*64}

class Gates(unittest.TestCase):
    def test_idle_and_finished(self):
        self.assertEqual(u.require_idle(u.metrics(GOOD)), {'2'})
        self.assertEqual(u.require_idle(u.metrics(GOOD.replace('printer_state{printer_id="2"} 1', 'printer_state{printer_id="2"} 4'))), {'2'})

    def test_busy_unknown_disconnected_missing_queue_and_heaters(self):
        variants = [GOOD.replace('printer_state{printer_id="2"} 1', f'printer_state{{printer_id="2"}} {x}') for x in (0, 2, 3, 5, 6, 7, 8)]
        variants += [GOOD.replace('printers_connected 1', 'printers_connected 0'),
                     GOOD.replace('queue_pending 0', 'queue_pending 1'),
                     GOOD.replace('queue_printing 0', 'queue_printing 1'),
                     GOOD.replace('bambuddy_queue_pending 0\n', ''),
                     GOOD.replace('bed_target_celsius{printer_id="2"} 0', 'bed_target_celsius{printer_id="2"} 50'),
                     GOOD.replace('bambuddy_nozzle_target_celsius{printer_id="2",nozzle="0"} 0\n', '')]
        for text in variants:
            with self.subTest(text=text):
                with self.assertRaises(RuntimeError):
                    u.require_idle(u.metrics(text))

    def test_release_validation(self):
        self.assertEqual(u.validate_manifest(manifest())['version'], '1.2.5.6')
        for field, value in [('version', '../x'), ('local_tag', 'evil:latest'), ('archive_bytes', -1), ('image_id', 'latest'), ('upstream_digest', 'evil@sha256:' + 'c'*64)]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                u.validate_manifest(dict(manifest(), **{field: value}))

    def test_corrupt_bundle(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            (directory / 'image.tar').write_bytes(b'x'*1024)
            with self.assertRaises(ValueError):
                u.check_archive(directory, manifest())

    def test_interrupted_transaction_blocks_all_mutations(self):
        with tempfile.TemporaryDirectory() as name, patch.object(u, 'ROOT', Path(name)), patch.object(u, 'compose') as compose:
            (u.ROOT / 'transaction.json').write_text('{}')
            with self.assertRaises(RuntimeError):
                u.apply()
            compose.assert_not_called()

    def test_queue_nonterminal_blocks(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as name, patch.object(u, 'STACK', Path(name)):
            (u.STACK / 'data').mkdir()
            with sqlite3.connect(u.STACK / 'data/bambuddy.db') as db:
                db.execute('create table print_queue (status text)')
                db.execute("insert into print_queue values ('scheduled')")
            with self.assertRaises(RuntimeError):
                u.queue_clear()

    def test_rollback_restores_matching_data_and_preserves_failed_data(self):
        with tempfile.TemporaryDirectory() as name:
            base = Path(name)
            stack, root, checkpoint = base / 'stack', base / 'runtime', base / 'backup'
            for directory in (stack, root, checkpoint, stack / 'data', stack / 'logs'):
                directory.mkdir()
            import sqlite3
            with sqlite3.connect(stack / 'data/bambuddy.db') as db:
                db.execute('create table original (id integer)')
            (stack / 'docker-compose.yml').write_text('old compose')
            (stack / '.env').write_text('test-only')
            with patch.object(u, 'STACK', stack), patch.object(u, 'ROOT', root), patch.object(u, 'OVERRIDE', stack / 'docker-compose.override.yml'):
                u.save_checkpoint_files(checkpoint)
                (stack / 'data/bambuddy.db').write_text('migrated failed database')
                failed = u.restore_checkpoint(checkpoint)
                self.assertEqual((failed / 'data/bambuddy.db').read_text(), 'migrated failed database')
                u.sqlite_check(stack / 'data')
                self.assertEqual((stack / '.env').read_text(), 'test-only')

    def test_failed_candidate_health_rolls_back_and_blocks_retries(self):
        import sqlite3
        from contextlib import ExitStack
        with tempfile.TemporaryDirectory() as name, ExitStack() as mocks:
            base = Path(name)
            stack, root, nas = base / 'stack', base / 'runtime', base / 'nas'
            for directory in (stack, root, nas, stack / 'data', stack / 'logs', root / 'ready'):
                directory.mkdir()
            with sqlite3.connect(stack / 'data/bambuddy.db') as db:
                db.execute('create table original (id integer)')
            (stack / 'docker-compose.yml').write_text('original')
            m = manifest()
            (root / 'ready.json').write_text(json.dumps(m))
            old = {'State': {'Running': True}, 'Image': 'sha256:'+'d'*64,
                   'Mounts': [{'Type': 'bind', 'Destination': '/app/'+x, 'Source': str(stack / x)} for x in ('data', 'logs')],
                   'HostConfig': {'NetworkMode': 'host'}}
            for field, value in [('STACK', stack), ('ROOT', root), ('NAS', nas), ('BACKUPS', nas / 'bambuddy-updates'), ('OVERRIDE', stack / 'docker-compose.override.yml')]:
                mocks.enter_context(patch.object(u, field, value))
            mocks.enter_context(patch.object(u, 'check_archive'))
            mocks.enter_context(patch.object(u, 'get_json', return_value={'version': '1.2.5.5'}))
            mocks.enter_context(patch.object(u, 'get_metrics', return_value=u.metrics(GOOD)))
            mocks.enter_context(patch.object(u, 'queue_clear'))
            mocks.enter_context(patch.object(u, 'current_image', side_effect=[old, dict(old, State={'Running': False})]))
            mocks.enter_context(patch.object(u.time, 'sleep'))
            from types import SimpleNamespace
            mocks.enter_context(patch.object(u.shutil, 'disk_usage', return_value=SimpleNamespace(free=50*1024**3)))
            mocks.enter_context(patch.object(u, 'probe'))
            def fake_run(*args, **kwargs):
                if args[0] == 'findmnt':
                    return 'nfs'
                if args[:3] == ('docker', 'image', 'inspect'):
                    return json.dumps([{'Id': m['image_id'], 'Architecture': 'amd64', 'Os': 'linux'}])
                if args[:3] == ('docker', 'image', 'save'):
                    Path(args[4]).write_bytes(b'old image')
                return ''
            mocks.enter_context(patch.object(u, 'run', side_effect=fake_run))
            compose = mocks.enter_context(patch.object(u, 'compose', side_effect=lambda *args: json.dumps({'services': {'bambuddy': {}}}) if args == ('config', '--format', 'json') else ''))
            health = mocks.enter_context(patch.object(u, 'health', side_effect=[RuntimeError('candidate unhealthy'), None]))
            with self.assertRaisesRegex(RuntimeError, 'old version recovered'):
                u.apply()
            self.assertTrue((root / 'blocked.json').exists())
            self.assertFalse((root / 'transaction.json').exists())
            self.assertIn(old['Image'], (stack / 'docker-compose.override.yml').read_text())
            health.assert_called_with('1.2.5.5', {'2'})
            starts = [call.args for call in compose.call_args_list if call.args and call.args[0] == 'up']
            self.assertEqual(len(starts), 2)
            self.assertTrue(all('--pull' in call and 'never' in call for call in starts))
            u.sqlite_check(stack / 'data')

if __name__ == '__main__':
    unittest.main()
