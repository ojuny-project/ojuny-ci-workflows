from __future__ import annotations

import io
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from pathlib import Path

from ojuny_ci.output import github_annotations, write_json, write_junit
from ojuny_ci.runner import CheckResult


class OutputTests(unittest.TestCase):
    def test_write_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            write_json(
                path,
                [CheckResult("alpha", "check", "fast", "pass", 0.5)],
                "0.1.0",
                "start",
                "end",
            )
            payload = json.loads(path.read_text())
            self.assertEqual(payload["runner_version"], "0.1.0")
            self.assertEqual(payload["results"][0]["status"], "pass")

    def test_write_junit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "junit.xml"
            write_junit(path, [CheckResult("alpha", "check", "fast", "fail", 0.5, log="boom")])
            tree = ET.parse(path)
            self.assertEqual(tree.getroot().tag, "testsuite")
            self.assertEqual(tree.getroot().attrib["failures"], "1")

    def test_github_annotations(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            github_annotations(
                [CheckResult("alpha", "check", "fast", "fail", 0.5, message="boom")]
            )
        self.assertIn("::error", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
