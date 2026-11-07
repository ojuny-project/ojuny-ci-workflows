from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ojuny_ci.manifest import ManifestError, load_manifest

FIXTURE = Path(__file__).parent / "fixtures" / "manifest.json"


class ManifestTests(unittest.TestCase):
    def test_load_valid(self):
        manifest = load_manifest(FIXTURE)
        self.assertEqual(manifest.names(), ("alpha", "beta"))
        self.assertEqual(
            manifest.repo("alpha").checks_for("fast"),
            ("checks.x86_64-linux.alpha",),
        )
        self.assertEqual(manifest.repo("beta").kind, "script")

    def test_invalid_version(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "repos.json"
            path.write_text(json.dumps({"version": 2, "repositories": []}))
            with self.assertRaises(ManifestError):
                load_manifest(path)

    def test_duplicate_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "repos.json"
            entry = {"name": "alpha", "path": "alpha", "kind": "flake", "checks": {}}
            path.write_text(json.dumps({"version": 1, "repositories": [entry, entry]}))
            with self.assertRaises(ManifestError):
                load_manifest(path)

    def test_unknown_tier(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "repos.json"
            entry = {"name": "alpha", "path": "alpha", "kind": "flake", "checks": {"slow": []}}
            path.write_text(json.dumps({"version": 1, "repositories": [entry]}))
            with self.assertRaises(ManifestError):
                load_manifest(path)


if __name__ == "__main__":
    unittest.main()
