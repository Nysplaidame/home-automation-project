import os
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from plan_layout import destination, inventory, roots_and_output


class LayoutTests(unittest.TestCase):
    def test_mapping(self):
        cases = [
            ("Y", "Print", None),
            ("Y", "Print/Models/a.stl", ("Y", "Models/a.stl")),
            ("Y", "backups/a", ("Z", "backups/a")),
            ("Y", ".hidden", ("Z", ".hidden")),
            ("Z", "Media", None),
            ("Z", "Media/books/calibre-library/metadata.db", ("Z", "calibre-library/metadata.db")),
            ("Z", "Media/books/other", ("Z", "books/other")),
            ("Z", "Media/books/calibre-library", ("Z", "calibre-library")),
            ("Z", "Media/music/A space/日本語", ("Z", "music/A space/日本語")),
            ("Z", "ISO/x", ("Z", "ISO/x")),
            ("Y", "Printable/x", ("Z", "Printable/x")),
        ]
        for volume, path, expected in cases:
            with self.subTest(path=path):
                self.assertEqual(destination(volume, path), expected)

    def test_reject_unsafe_paths(self):
        for path in ["", "/a", "../a", "Print/../a", "./a", "a//b"]:
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    destination("Y", path)
        with self.assertRaises(ValueError):
            destination("X", "a")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.y, self.z = self.root / "y", self.root / "z"
        (self.y / "Print").mkdir(parents=True)
        (self.z / "Media/books/calibre-library").mkdir(parents=True)
        self.output = self.root / "evidence.sqlite"

    def test_hidden_and_empty_directories(self):
        (self.y / "Print/.hidden").write_text("safe")
        (self.z / "Media/empty").mkdir()
        result = inventory(self.y, self.z, self.output)
        self.assertEqual(result["issues"], {})
        with closing(sqlite3.connect(self.output)) as db:
            self.assertEqual(db.execute(
                "select target from entries where relative='Print/.hidden'").fetchone()[0], ".hidden")
            self.assertEqual(db.execute(
                "select kind from entries where target='empty'").fetchone()[0], "directory")
        self.assertEqual((self.y / "Print/.hidden").read_text(), "safe")

    def test_merge_is_explicit_review(self):
        (self.y / "backups").mkdir()
        (self.z / "Media/backups").mkdir()
        self.assertEqual(inventory(self.y, self.z, self.output)["issues"],
                         {"directory-merge-review": 1})

    def test_differing_files_refused(self):
        (self.y / "same").write_text("source")
        (self.z / "Media/same").write_text("destination")
        self.assertIn("leaf-collision", inventory(self.y, self.z, self.output)["issues"])

    def test_identical_files_still_need_verification(self):
        (self.y / "same").write_text("same")
        (self.z / "same").write_text("same")
        self.assertIn("leaf-collision", inventory(self.y, self.z, self.output)["issues"])

    def test_case_collision_across_roots(self):
        (self.y / "Case").mkdir()
        (self.z / "Media/case").mkdir()
        self.assertIn("case-collision", inventory(self.y, self.z, self.output)["issues"])

    def test_file_parent_obstruction(self):
        (self.y / "books").write_text("not a directory")
        result = inventory(self.y, self.z, self.output)
        self.assertIn("leaf-collision", result["issues"])

    def test_wrong_roots_and_existing_output(self):
        with self.assertRaises(ValueError):
            roots_and_output(self.y, self.y, self.output)
        with self.assertRaises(ValueError):
            roots_and_output(self.y, self.z, self.y / "evidence.sqlite")
        self.output.write_text("retain")
        with self.assertRaises(ValueError):
            roots_and_output(self.y, self.z, self.output)
        self.assertEqual(self.output.read_text(), "retain")

    def test_missing_wrapper(self):
        (self.y / "Print").rmdir()
        with self.assertRaises(ValueError):
            inventory(self.y, self.z, self.output)
        self.assertFalse(self.output.exists())

    def test_missing_calibre_library(self):
        (self.z / "Media/books/calibre-library").rmdir()
        with self.assertRaises(ValueError):
            inventory(self.y, self.z, self.output)
        self.assertFalse(self.output.exists())

    def test_timestamps_outside_signed_64bit_are_preserved(self):
        target = self.y / "Print/old-date"
        target.write_bytes(b"x")
        original_stat = os.stat
        def modified(path, *args, **kwargs):
            value = original_stat(path, *args, **kwargs)
            if os.fspath(path) == str(target):
                fields = {name: getattr(value, name) for name in dir(value) if name.startswith("st_")}
                fields["st_mtime_ns"] = -11644473600000000000
                fields["st_ino"] = 2**64 - 1
                return SimpleNamespace(**fields)
            return value
        with patch("plan_layout.os.stat", side_effect=modified):
            inventory(self.y, self.z, self.output)
        with closing(sqlite3.connect(self.output)) as db:
            row = db.execute("select inode,mtime_ns from entries where relative='Print/old-date'").fetchone()
            self.assertEqual(row, (str(2**64 - 1), "-11644473600000000000"))

    def test_unreadable_entry_prevents_clean_result(self):
        target = self.y / "Print/unreadable"
        target.write_bytes(b"x")
        original_stat = os.stat
        def modified(path, *args, **kwargs):
            if os.fspath(path) == str(target):
                raise PermissionError("simulated read failure")
            return original_stat(path, *args, **kwargs)
        with patch("plan_layout.os.stat", side_effect=modified):
            result = inventory(self.y, self.z, self.output)
        self.assertEqual(result["issues"], {"read-error": 1})
        self.assertEqual(target.read_bytes(), b"x")

    def test_nested_mount_is_reported_not_traversed(self):
        target = self.y / "Print/nested"
        target.mkdir()
        (target / "outside").write_bytes(b"x")
        original_stat = os.stat
        def modified(path, *args, **kwargs):
            value = original_stat(path, *args, **kwargs)
            if os.fspath(path) == str(target):
                fields = {name: getattr(value, name) for name in dir(value) if name.startswith("st_")}
                fields["st_dev"] += 1
                return SimpleNamespace(**fields)
            return value
        with patch("plan_layout.os.stat", side_effect=modified):
            result = inventory(self.y, self.z, self.output)
        self.assertEqual(result["issues"], {"nested-mount": 1})
        with closing(sqlite3.connect(self.output)) as db:
            self.assertEqual(db.execute(
                "select count(*) from entries where relative like 'Print/nested%'").fetchone()[0], 0)

    @unittest.skipUnless(os.name == "posix", "Linux symlink scenario")
    def test_symlinked_wrapper_refused(self):
        (self.y / "Print").rmdir()
        (self.y / "Print").symlink_to(self.z / "Media", target_is_directory=True)
        with self.assertRaises(ValueError):
            inventory(self.y, self.z, self.output)
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(os.name == "posix", "Linux metadata scenario")
    def test_links_and_socket(self):
        import socket
        (self.y / "Print/one").write_bytes(b"x")
        os.link(self.y / "Print/one", self.y / "Print/two")
        os.symlink("one", self.y / "Print/relative")
        os.symlink("/outside", self.y / "Print/absolute")
        sock = socket.socket(socket.AF_UNIX)
        self.addCleanup(sock.close)
        sock.bind(str(self.y / "Print/socket"))
        result = inventory(self.y, self.z, self.output)
        self.assertEqual(result["issues"], {"symlink-review": 1})
        with closing(sqlite3.connect(self.output)) as db:
            rows = db.execute("select inode,links from entries where kind='file'").fetchall()
            self.assertEqual(rows[0], rows[1])
            self.assertEqual(rows[0][1], 2)
            self.assertEqual(db.execute("select count(*) from entries where kind='socket'").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
