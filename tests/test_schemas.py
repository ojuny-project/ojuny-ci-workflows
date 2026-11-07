from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


class SchemaTests(unittest.TestCase):
    def test_schemas_are_json_objects(self):
        for path in sorted(SCHEMAS.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(data, dict, path)
            self.assertIn("$schema", data, path)
            self.assertIn("title", data, path)

    def test_manifest(self):
        data = json.loads((ROOT / "repos.json").read_text(encoding="utf-8"))
        names = [repo["name"] for repo in data["repositories"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(
            all(repo["kind"] in {"flake", "script", "missing"} for repo in data["repositories"])
        )

    def test_install_report_example(self):
        example = json.loads(
            (SCHEMAS / "examples" / "install-report.json").read_text(encoding="utf-8")
        )
        for key in ("version", "generated_at", "iso", "template", "environment", "phases"):
            self.assertIn(key, example)
        self.assertIn("closure_hash", example["iso"])
        self.assertIn("cpu", example["environment"])

    def test_acceptance_inventory(self):
        data = json.loads((ROOT / "acceptance-inventory.json").read_text(encoding="utf-8"))
        names = [flow["name"] for flow in data["flows"]]
        self.assertEqual(len(names), len(set(names)))
        for flow in data["flows"]:
            self.assertIn(flow["status"], {"draft", "active"})
            if flow["status"] == "active":
                self.assertTrue(flow["strings"], flow["name"])


if __name__ == "__main__":
    unittest.main()
