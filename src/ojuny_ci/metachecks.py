"""Per-repository meta-checks for the Ojuny CI runner."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _nix(args: list[str], repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["nix", *args], cwd=repo, text=True, capture_output=True)


def check_inventory(repo: Path) -> int:
    failures = []
    for attribute in ("checks", "apps.ci", "hydraJobs"):
        completed = _nix(["eval", "--json", f".#{attribute}"], repo)
        if completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip()
            failures.append(f"missing or invalid .#{attribute}: {message}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("check-inventory: ok")
    return 0


def flake_outputs_eval(repo: Path) -> int:
    failures = []
    for attribute in ("checks", "packages", "apps"):
        completed = _nix(["eval", "--json", f".#{attribute}"], repo)
        if completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip()
            failures.append(f".#{attribute} does not evaluate: {message}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("flake-outputs-eval: ok")
    return 0


def check_default_aggregate(repo: Path) -> int:
    checks = _nix(["eval", "--raw", ".#checks.default"], repo)
    if checks.returncode != 0:
        print("checks.default does not evaluate", file=sys.stderr)
        return 1
    packages = _nix(["eval", "--raw", ".#packages.default"], repo)
    if packages.returncode != 0:
        print("check-default-aggregate: ok (no packages.default)")
        return 0
    if checks.stdout.strip() == packages.stdout.strip():
        print("checks.default is the package build; make it the aggregate suite", file=sys.stderr)
        return 1
    print("check-default-aggregate: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ojuny-ci-metacheck")
    parser.add_argument(
        "check",
        choices=["check-inventory", "flake-outputs-eval", "check-default-aggregate"],
    )
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.repo.is_dir():
        print(f"repository not found: {args.repo}", file=sys.stderr)
        return 2
    return {
        "check-inventory": check_inventory,
        "flake-outputs-eval": flake_outputs_eval,
        "check-default-aggregate": check_default_aggregate,
    }[args.check](args.repo)


if __name__ == "__main__":
    raise SystemExit(main())
