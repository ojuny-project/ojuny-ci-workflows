from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ojuny_ci.cli import main

FIXTURE = str(Path(__file__).parent / "fixtures" / "manifest.json")


class CliTests(unittest.TestCase):
    def test_list(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = main(["list", "--repos-file", FIXTURE])
        self.assertEqual(code, 0)
        self.assertIn("alpha", stream.getvalue())

    def test_dry_run(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = main(
                [
                    "run",
                    "--repos-file",
                    FIXTURE,
                    "--tier",
                    "fast",
                    "--repo",
                    "alpha",
                    "--dry-run",
                ]
            )
        self.assertEqual(code, 0)
        self.assertIn("checks.x86_64-linux.alpha", stream.getvalue())

    def test_unknown_repo(self):
        code = main(
            [
                "run",
                "--repos-file",
                FIXTURE,
                "--repo",
                "missing",
                "--dry-run",
            ]
        )
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
