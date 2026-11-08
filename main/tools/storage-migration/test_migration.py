import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import migration


@unittest.skipUnless(os.name == "posix" and shutil.which("rsync"), "Linux rsync session fixture")
class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.y, self.z, self.target = [self.base / n for n in ("y", "z", "new-array")]
        (self.y / "Print/Models").mkdir(parents=True)
        (self.y / "Print/Models/model.stl").write_text("print data")
        (self.y / "backups/proxmox").mkdir(parents=True)
        (self.y / "backups/proxmox/backup").write_text("backup data")
        (self.y / "_codex_diagnostics/focused-20261001-213336").mkdir(parents=True)
        (self.y / "_codex_diagnostics/focused-20261001-213336/from-y").write_text("Y")
        (self.z / "Media/books/calibre-library").mkdir(parents=True)
        (self.z / "Media/books/calibre-library/metadata.db").write_text("calibre fixture")
        (self.z / "Media/books/other").write_text("other book")
        (self.z / "Media/music").mkdir()
        (self.z / "Media/music/song").write_text("music")
        (self.z / "ISO").mkdir()
        (self.z / "ISO/file.iso").write_text("ISO")
        (self.z / ".hidden").write_text("hidden")
        (self.z / "Media/backups/personal").mkdir(parents=True)
        (self.z / "Media/backups/personal/retained").write_text("Z")
        (self.z / "_codex_diagnostics/focused-20261001-213336").mkdir(parents=True)
        (self.z / "_codex_diagnostics/focused-20261001-213336/from-z").write_text("Z")
        self.target.mkdir()
        self.state = self.base / "evidence"
        migration.create_session(self.state, self.y, self.z, self.target, "fixture-session", [None, None, None])
        self.session = migration.Session(self.state, fixture=True)

    def phase(self, phase):
        self.session.prepare_phase(phase)
        self.session.apply_phase(phase)

    def z_phases(self):
        self.session.copy("z", execute=True, final=True)
        self.assertEqual(self.session.verify_stage("z")["issues"], 0)
        self.phase("flatten-z")
        self.phase("publish-z")

    def test_complete_disposable_sequence(self):
        self.z_phases()
        self.assertEqual(self.session.final_verify("z")["issues"], 0)
        self.assertEqual((self.target / "calibre-library/metadata.db").read_text(), "calibre fixture")
        self.assertEqual((self.target / "books/other").read_text(), "other book")
        self.assertFalse((self.target / "Media").exists())
        self.session.copy("y", execute=True, final=True)
        self.assertEqual(self.session.verify_stage("y")["issues"], 0)
        self.phase("publish-y")
        self.assertEqual(self.session.final_verify("combined")["issues"], 0)
        self.assertEqual((self.target / "backups/proxmox/backup").read_text(), "backup data")
        self.assertEqual((self.target / "backups/personal/retained").read_text(), "Z")
        self.assertEqual((self.target / "_codex_diagnostics/focused-20261001-213336/from-y").read_text(), "Y")
        self.assertEqual((self.target / "_codex_diagnostics/focused-20261001-213336/from-z").read_text(), "Z")
        self.phase("retain-y")
        self.phase("flatten-print")
        self.session.remove_print_wrapper()
        self.assertFalse((self.y / "Print").exists())
        self.assertEqual((self.y / "Models/model.stl").read_text(), "print data")
        # Cross-disk originals survive the entire fixture; cleanup is a later gate.
        self.assertTrue((self.z / "Media/books/calibre-library/metadata.db").exists())
        self.assertFalse((self.y / "backups").exists())
        retained = self.y / ".household-retained/fixture-session/backups/proxmox/backup"
        self.assertEqual(retained.read_text(), "backup data")

    def test_stage_change_after_verification_refused(self):
        self.session.copy("z", execute=True, final=True)
        self.session.verify_stage("z")
        stage = self.target / self.session.stage("z")
        (stage / "Media/books/calibre-library/metadata.db").write_text("changed")
        with self.assertRaises(ValueError):
            self.session.prepare_phase("flatten-z")
        self.assertTrue((stage / "Media/books/calibre-library/metadata.db").exists())

    def test_copy_resume_after_failure(self):
        with patch("migration.subprocess.run", return_value=type("Result", (), {
                "returncode": 23, "stdout": "", "stderr": "injected failure"})()):
            with self.assertRaises(RuntimeError):
                self.session.copy("z", execute=True, final=True)
        with self.assertRaises(ValueError):
            self.session.verify_stage("z")
        self.session.copy("z", execute=True, final=True)
        self.assertEqual(self.session.verify_stage("z")["issues"], 0)

    def test_source_deletion_during_staging_blocks_verification(self):
        self.session.copy("z", execute=True, final=True)
        (self.z / "Media/music/song").unlink()
        self.session.copy("z", execute=True, final=True)
        self.assertGreater(self.session.verify_stage("z")["issues"], 0)
        with self.assertRaises(ValueError):
            self.session.prepare_phase("flatten-z")

    def test_source_deletion_and_type_change_reconcile_without_data_deletion(self):
        self.session.copy("z", execute=True, final=True)
        (self.z / "Media/music/song").unlink()
        (self.z / "ISO/file.iso").unlink()
        (self.z / "ISO/file.iso").mkdir()
        (self.z / "ISO/file.iso/new").write_text("new type")
        result = self.session.reconcile_extras("z")
        held = self.target / result["prefix"]
        self.assertEqual((held / "Media/music/song").read_text(), "music")
        self.assertEqual((held / "ISO/file.iso").read_text(), "ISO")
        with self.assertRaises(ValueError):
            self.session.verify_stage("z")
        self.session.copy("z", execute=True, final=True)
        self.assertEqual(self.session.verify_stage("z")["issues"], 0)
        self.phase("flatten-z"); self.phase("publish-z")
        self.assertEqual(self.session.final_verify("z")["issues"], 0)
        self.assertTrue((held / "ISO/file.iso").exists())

    def test_changed_quarantine_seal_blocks_final_verification(self):
        self.session.copy("z", execute=True, final=True)
        (self.z / "Media/music/song").unlink()
        result = self.session.reconcile_extras("z")
        self.session.copy("z", execute=True, final=True); self.session.verify_stage("z")
        self.phase("flatten-z"); self.phase("publish-z")
        (self.target / result["prefix"] / "Media/music/song").write_text("changed hold")
        with self.assertRaises(ValueError):
            self.session.final_verify("z")

    def test_copy_disallowed_after_transform_is_sealed(self):
        self.session.copy("z", execute=True, final=True)
        self.session.verify_stage("z")
        self.session.prepare_phase("flatten-z")
        with self.assertRaises(ValueError):
            self.session.copy("z", execute=True, final=True)

    def test_whole_session_namespace_rollback(self):
        self.z_phases()
        self.session.apply_phase("publish-z", reverse=True)
        self.session.apply_phase("flatten-z", reverse=True)
        stage = self.target / self.session.stage("z")
        self.assertTrue((stage / "Media/books/calibre-library/metadata.db").exists())
        self.assertEqual((stage / "ISO/file.iso").read_text(), "ISO")

    def test_activation_prevents_automatic_rollback(self):
        self.z_phases()
        self.session.final_verify("z")
        self.session.activate("publish-z")
        with self.assertRaises(ValueError):
            self.session.apply_phase("publish-z", reverse=True)
        self.session.copy("y", execute=True, final=True)
        self.assertEqual(self.session.verify_stage("y")["issues"], 0)

    def test_activation_requires_final_mapped_verification(self):
        self.z_phases()
        with self.assertRaises(ValueError):
            self.session.activate("publish-z")

    def test_corruption_after_publish_blocks_final_verification(self):
        self.z_phases()
        path = self.target / "calibre-library/metadata.db"
        value = path.stat()
        path.write_bytes(b"x" * value.st_size)
        os.utime(path, ns=(value.st_atime_ns, value.st_mtime_ns))
        self.assertGreater(self.session.final_verify("z")["issues"], 0)

    def test_maintenance_cannot_hide_unpublished_data(self):
        self.z_phases()
        (self.target / self.session.stage("y") / "unexpected").write_text("must not be hidden")
        self.assertGreater(self.session.final_verify("z")["issues"], 0)

    def test_low_free_space_prevents_copy(self):
        with patch("migration.shutil.disk_usage", return_value=type("Usage", (), {"free": 0})()):
            with self.assertRaises(ValueError):
                self.session.copy("z", execute=True, final=True)

    def test_fixture_session_cannot_be_opened_as_production(self):
        with self.assertRaises(ValueError):
            migration.Session(self.state)

    def test_warm_copy_cannot_authorize_verification(self):
        self.session.copy("z", execute=True)
        with self.assertRaises(ValueError):
            self.session.verify_stage("z")

    def test_original_z_change_is_detected_before_disk_retirement(self):
        self.z_phases()
        self.assertTrue(self.session.check_original_z()["original_z_unchanged"])
        (self.z / "Media/music/song").write_text("late original write")
        with self.assertRaises(ValueError):
            self.session.check_original_z()

    def test_live_z_changes_are_preserved_by_later_y_merge(self):
        self.z_phases()
        self.session.final_verify("z")
        self.session.activate("publish-z")
        (self.target / "calibre-library/metadata.db").write_text("legitimate new library version")
        (self.target / "new-media-file").write_text("new after activation")
        self.session.copy("y", execute=True, final=True)
        self.session.verify_stage("y")
        self.session.snapshot_live_z()
        self.phase("publish-y")
        self.assertEqual(self.session.final_verify("combined")["issues"], 0)
        self.assertEqual((self.target / "new-media-file").read_text(), "new after activation")

    def test_changes_after_live_baseline_are_blocking(self):
        self.z_phases()
        self.session.final_verify("z")
        self.session.activate("publish-z")
        self.session.copy("y", execute=True, final=True)
        self.session.verify_stage("y")
        self.session.snapshot_live_z()
        (self.target / "music/song").write_text("writer violated freeze")
        self.phase("publish-y")
        self.assertGreater(self.session.final_verify("combined")["issues"], 0)
        with self.assertRaises(ValueError):
            self.session.prepare_phase("retain-y")
        self.assertTrue((self.y / "backups/proxmox/backup").exists())

    def test_changed_live_baseline_blocks_merge_preparation(self):
        self.z_phases()
        self.session.final_verify("z")
        self.session.activate("publish-z")
        self.session.copy("y", execute=True, final=True)
        self.session.verify_stage("y")
        result = self.session.snapshot_live_z()
        with open(result["report"], "a", encoding="utf-8") as stream:
            stream.write("\n")
        with self.assertRaisesRegex(ValueError, "baseline changed"):
            self.session.prepare_phase("publish-y")

    def test_changed_final_receipt_blocks_original_retention(self):
        self.z_phases()
        self.session.copy("y", execute=True, final=True)
        self.session.verify_stage("y")
        self.phase("publish-y")
        result = self.session.final_verify("combined")
        with open(result["report"], "a", encoding="utf-8") as stream:
            stream.write("\n")
        with self.assertRaisesRegex(ValueError, "receipt changed"):
            self.session.prepare_phase("retain-y")
        self.assertTrue((self.y / "backups/proxmox/backup").exists())

    def test_retention_can_be_reversed_before_print_flattening(self):
        self.z_phases()
        self.session.copy("y", execute=True, final=True)
        self.session.verify_stage("y")
        self.phase("publish-y")
        self.session.final_verify("combined")
        self.phase("retain-y")
        self.assertFalse((self.y / "backups").exists())
        self.session.apply_phase("retain-y", reverse=True)
        self.assertEqual((self.y / "backups/proxmox/backup").read_text(), "backup data")

    def test_cli_verification_failure_has_nonzero_status(self):
        import sys
        from contextlib import redirect_stdout
        from io import StringIO
        with patch.object(sys, "argv", ["migration.py", "--state", "unused", "--writers-stopped", "verify", "z"]), patch("migration.Session") as fake:
            fake.return_value.verify_stage.return_value = {"issues": 1}
            with redirect_stdout(StringIO()):
                self.assertEqual(migration.main(), 2)

    def test_checksum_repair_recovers_same_size_same_time_corruption(self):
        self.session.copy("z", execute=True, final=True)
        file = self.target / self.session.stage("z") / ".hidden"
        info = file.stat()
        file.write_bytes(b"x" * info.st_size)
        os.utime(file, ns=(info.st_atime_ns, info.st_mtime_ns))
        self.assertGreater(self.session.verify_stage("z")["issues"], 0)
        self.session.copy("z", execute=True, final=True, checksum_repair=True)
        self.assertEqual(self.session.verify_stage("z")["issues"], 0)

    def test_merge_retains_y_parent_acl_and_z_child_acl(self):
        import subprocess
        subprocess.run(["setfacl", "-m", "u:100000:r-x", str(self.y / "backups")], check=True)
        child = self.z / "Media/backups/personal"
        subprocess.run(["setfacl", "-m", "u:1007:r--", str(child)], check=True)
        old_child = os.getxattr(child, "system.posix_acl_access")
        wanted_parent = os.getxattr(self.y / "backups", "system.posix_acl_access")
        self.z_phases()
        self.session.copy("y", execute=True, final=True)
        self.session.verify_stage("y")
        self.phase("publish-y")
        self.assertEqual(os.getxattr(self.target / "backups", "system.posix_acl_access"), wanted_parent)
        self.assertEqual(os.getxattr(self.target / "backups/personal", "system.posix_acl_access"), old_child)
        self.assertEqual(self.session.final_verify("combined")["issues"], 0)


if __name__ == "__main__":
    unittest.main()
