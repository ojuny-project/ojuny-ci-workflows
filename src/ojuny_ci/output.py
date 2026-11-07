"""Human, JSON, JUnit and GitHub output for the Ojuny CI runner."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from .runner import CheckResult


def write_json(
    path: Path,
    results: list[CheckResult],
    runner_version: str,
    started_at: str,
    finished_at: str,
) -> None:
    payload = {
        "runner_version": runner_version,
        "started_at": started_at,
        "finished_at": finished_at,
        "results": [result.as_dict() for result in results],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_junit(path: Path, results: list[CheckResult]) -> None:
    failures = sum(1 for result in results if result.status == "fail")
    errors = sum(1 for result in results if result.status == "error")
    skipped = sum(1 for result in results if result.status == "skip")
    suite = ET.Element(
        "testsuite",
        name="ojuny-ci",
        tests=str(len(results)),
        failures=str(failures),
        errors=str(errors),
        skipped=str(skipped),
    )
    for result in results:
        case = ET.SubElement(
            suite,
            "testcase",
            classname=f"{result.repo}.{result.tier}",
            name=result.check,
            time=f"{result.duration_seconds:.3f}",
        )
        if result.status in ("fail", "error"):
            tag = "failure" if result.status == "fail" else "error"
            element = ET.SubElement(case, tag, message=result.message or result.status)
            element.text = result.log
        elif result.status == "skip":
            ET.SubElement(case, "skipped", message=result.message)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def github_annotations(results: list[CheckResult]) -> None:
    for result in results:
        if result.status in ("fail", "error"):
            message = result.message or (result.log.splitlines()[-1] if result.log else result.status)
            print(f"::error title={result.repo}/{result.check}::{message}")
        elif result.status == "skip":
            print(f"::notice title={result.repo}/{result.check}::{result.message}")


def print_summary(results: list[CheckResult]) -> None:
    if not results:
        print("no checks selected")
        return
    for result in results:
        print(
            f"{result.status.upper():5} {result.repo:24} {result.tier:5} "
            f"{result.check} ({result.duration_seconds:.1f}s)"
        )
    passed = sum(1 for result in results if result.status == "pass")
    failed = sum(1 for result in results if result.status in ("fail", "error"))
    skipped = sum(1 for result in results if result.status == "skip")
    print(f"\n{len(results)} checks, {passed} passed, {failed} failed, {skipped} skipped")
