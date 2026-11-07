from __future__ import annotations

import unittest
from pathlib import Path

from ojuny_ci.manifest import Manifest, Repository
from ojuny_ci.runner import CheckResult, _command, run_checks


class RunnerTests(unittest.TestCase):
    def test_check_result_dict(self):
        result = CheckResult("alpha", "checks.x", "fast", "pass", 1.234)
        payload = result.as_dict()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["duration_seconds"], 1.234)

    def test_command_mapping(self):
        repository = Repository("alpha", "alpha", "flake", ("x86_64-linux",), {})
        self.assertEqual(_command(repository, "checks.x86_64-linux.alpha")[:2], ["nix", "build"])
        self.assertIn("ojuny_ci.metachecks", _command(repository, "meta:check-inventory"))
        self.assertEqual(_command(repository, "script:true")[:2], ["bash", "-c"])
        self.assertEqual(_command(repository, "hydraJobs")[:2], ["nix", "eval"])

    def test_missing_repository_is_skipped(self):
        repository = Repository(
            "alpha",
            "alpha",
            "flake",
            ("x86_64-linux",),
            {"fast": ("checks.x",)},
        )
        manifest = Manifest(1, (repository,), {})
        results = run_checks(manifest, Path("/nonexistent"), ("fast",))
        self.assertEqual(results[0].status, "skip")


if __name__ == "__main__":
    unittest.main()
