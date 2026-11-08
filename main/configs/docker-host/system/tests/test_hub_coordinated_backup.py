"""Linux-only isolated transaction tests; fake engine never invokes Docker."""
import hashlib
import importlib.util
import os
import tempfile
import tarfile
import unittest
from unittest.mock import patch
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "household-hub-coordinated-backup.py"
if os.name == "posix":
    spec = importlib.util.spec_from_file_location("hub_backup", SCRIPT)
    backup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backup)


class FakeEngine:
    def __init__(self, services, fail=None):
        self.stack = Path("/isolated-stack")
        self.states = {v["id"]: v["was_running"] for v in services.values()}
        self.events = []
        self.fail = fail

    def mount(self):
        self.events.append("mount")
        if self.fail == "mount":
            raise backup.BackupError("mount lost")

    def stop(self, record):
        self.events.append("stop:" + record["id"])
        if self.fail == "stop:" + record["id"]:
            raise backup.BackupError("stop failed")
        self.states[record["id"]] = False

    def running(self, record):
        return self.states[record["id"]]

    def quiesced(self, services):
        if self.fail == "still-running" or any(self.states.values()):
            raise backup.BackupError("writer running")

    def start(self, record):
        self.events.append("start:" + record["id"])
        if self.fail == "start:" + record["id"]:
            raise backup.BackupError("restart failed")
        self.states[record["id"]] = True

    def archive(self, destination, source, members):
        self.events.append("archive:" + destination.name)
        if self.fail == "archive":
            destination.write_bytes(b"partial")
            raise backup.BackupError("archive failed")
        destination.write_bytes(b"isolated archive payload")

    def health(self, services):
        self.events.append("health")
        if self.fail == "health":
            raise backup.BackupError("health failed")


@unittest.skipUnless(os.name == "posix", "requires Linux fcntl")
class CoordinatedBackupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.stage = Path(self.tmp.name)
        self.services = {s: {"id": s, "image": "sha256:isolated", "was_running": s != "worker", "source": "/isolated/" + s}
                         for s in ("postgres", "redis", "qdrant", "api", "web", "worker")}

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self, fail=None):
        engine = FakeEngine(self.services, fail)
        if fail:
            with self.assertRaises(backup.BackupError):
                backup.checkpoint(engine, self.services, self.stage)
            self.assertFalse((self.stage / "COMPLETE").exists())
            self.assertTrue((self.stage / "original-state.json").exists())
        else:
            backup.checkpoint(engine, self.services, self.stage)
        return engine

    def test_success_order_private_files_checksums_and_stopped_worker(self):
        engine = self.invoke()
        stops = [e for e in engine.events if e.startswith("stop:")]
        self.assertEqual(stops, ["stop:web", "stop:api", "stop:postgres", "stop:redis", "stop:qdrant"])
        starts = [e for e in engine.events if e.startswith("start:")]
        self.assertEqual(starts, ["start:postgres", "start:redis", "start:qdrant", "start:api", "start:web"])
        self.assertFalse(engine.states["worker"])
        self.assertTrue((self.stage / "COMPLETE").exists())
        for line in (self.stage / "SHA256SUMS").read_text().splitlines():
            digest, name = line.split("  ")
            self.assertEqual(hashlib.sha256((self.stage / name).read_bytes()).hexdigest(), digest)
        for file in self.stage.iterdir():
            self.assertEqual(file.stat().st_mode & 0o777, 0o600)

    def test_archive_failure_resumes_originals_without_completion(self):
        engine = self.invoke("archive")
        self.assertTrue(all(engine.states[s] for s in ("postgres", "redis", "qdrant", "api", "web")))

    def test_failed_stop_never_archives_and_attempts_resume(self):
        engine = self.invoke("stop:postgres")
        self.assertFalse(any(e.startswith("archive:") for e in engine.events))
        self.assertIn("start:web", engine.events)

    def test_store_restart_failure_keeps_writers_stopped(self):
        engine = self.invoke("start:postgres")
        self.assertIn("start:redis", engine.events)
        self.assertFalse(engine.states["api"])
        self.assertFalse(engine.states["web"])

    def test_writer_restart_failure_still_resumes_other_writer(self):
        engine = self.invoke("start:api")
        self.assertTrue(engine.states["web"])

    def test_mount_loss_never_completes_but_originals_resume(self):
        engine = self.invoke("mount")
        self.assertTrue(engine.states["api"])

    def test_unstopped_writer_rejects_archival(self):
        engine = self.invoke("still-running")
        self.assertFalse(any(e.startswith("archive:") for e in engine.events))

    def test_health_failure_never_marks_complete(self):
        self.invoke("health")

    def test_original_state_flush_failure_never_stops_services(self):
        engine = FakeEngine(self.services)
        with patch.object(backup, "durable", side_effect=OSError("storage failure")):
            with self.assertRaises(OSError):
                backup.checkpoint(engine, self.services, self.stage)
        self.assertEqual(engine.events, [])
        self.assertFalse((self.stage / "COMPLETE").exists())

    def test_real_archive_round_trip_without_docker_or_network(self):
        source = self.stage / "input"
        source.mkdir()
        (source / "payload").write_bytes(b"offline checkpoint content")
        archive = self.stage / "test.tar.gz"
        engine = backup.Engine(self.stage, source)
        with patch.object(engine, "mount") as mount:
            engine.archive(archive, source, ["."])
        self.assertEqual(mount.call_count, 2)
        with tarfile.open(archive) as saved:
            self.assertEqual(saved.extractfile("./payload").read(), b"offline checkpoint content")
        self.assertEqual(archive.stat().st_mode & 0o777, 0o600)
