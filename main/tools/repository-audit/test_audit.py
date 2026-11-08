import subprocess
import tempfile
import unittest
from pathlib import Path

from audit import audit


class RepositoryAuditTests(unittest.TestCase):
    def test_links_code_fences_syntax_and_nested_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "target.yaml").write_text("value: 1\n")
            (root / "notes.md").write_text(
                "[valid](target.yaml)\n[[target.yaml]]\n[missing](missing.md)\n"
                "```md\n[fenced](example.md)\n[[example]]\n```\n"
            )
            (root / ".gitignore").write_text("cache/\n")
            (root / "cache").mkdir()
            (root / "cache/broken.py").write_text("not python !")
            child = root / "recovered"
            subprocess.run(["git", "init", "-q", str(child)], check=True)
            (child / "source.py").write_text("x = 1\n")
            result = audit(root)
            self.assertEqual(result["counts"]["python_syntax"], 1)
            self.assertEqual(len(result["issues"]["broken_links"]), 1)
            self.assertEqual(result["issues"]["broken_links"][0]["target"], "missing.md")
            self.assertFalse(result["issues"].get("unresolved_wikilinks"))
            self.assertFalse(result["issues"].get("syntax"))


if __name__ == "__main__":
    unittest.main()
