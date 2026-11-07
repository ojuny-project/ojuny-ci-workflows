"""Command line interface for the Ojuny CI runner."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .manifest import Manifest, ManifestError, load_manifest
from .output import github_annotations, print_summary, write_json, write_junit
from .runner import run_checks

TIERS = ("fast", "nix", "heavy")


def default_manifest() -> Path:
    override = os.environ.get("OJUNY_CI_MANIFEST")
    if override:
        return Path(override)
    installed = Path(sys.prefix) / "share" / "ojuny-ci" / "repos.json"
    if installed.exists():
        return installed
    return Path(__file__).resolve().parents[2] / "repos.json"


def _changed_repo_names(manifest: Manifest, repos_dir: Path) -> tuple[str, ...]:
    names: list[str] = []
    for repository in manifest.repositories:
        path = repos_dir / repository.path
        if not path.is_dir():
            continue
        for base in ("origin/main", "HEAD~1"):
            completed = subprocess.run(
                ["git", "-C", str(path), "diff", "--quiet", f"{base}...HEAD"],
                text=True,
                capture_output=True,
            )
            if completed.returncode == 0:
                break
            if completed.returncode == 1:
                names.append(repository.name)
                break
        else:
            names.append(repository.name)
    return tuple(names)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ojuny-ci", description="Run Ojuny CI checks")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="run checks")
    run.add_argument("--tier", action="append", choices=[*TIERS, "all"], default=None)
    run.add_argument("--repo", action="append", default=None)
    run.add_argument("--all", action="store_true")
    run.add_argument("--changed", action="store_true")
    run.add_argument(
        "--repos-dir",
        type=Path,
        default=Path(os.environ.get("OJUNY_REPOS", Path.home() / "repos")),
    )
    run.add_argument("--repos-file", type=Path, default=None)
    run.add_argument("--jobs", type=int, default=1)
    run.add_argument("--timeout", type=int, default=None)
    run.add_argument("--json", action="store_true")
    run.add_argument("--json-file", type=Path, default=None)
    run.add_argument("--junit", type=Path, default=None)
    run.add_argument("--github-annotations", action="store_true")
    run.add_argument("--dry-run", action="store_true")

    listing = subparsers.add_parser("list", help="list repositories and checks")
    listing.add_argument("--repos-file", type=Path, default=None)

    explain = subparsers.add_parser("explain", help="show one repository")
    explain.add_argument("--repo", required=True)
    explain.add_argument("--repos-file", type=Path, default=None)

    subparsers.add_parser("check", help="run the runner selftest")
    return parser


def _run(args: argparse.Namespace, manifest: Manifest) -> int:
    tiers = args.tier or ["all"]
    selected_tiers = TIERS if "all" in tiers else tuple(dict.fromkeys(tiers))

    repo_names = tuple(args.repo) if args.repo else None
    if args.all:
        repo_names = None
    if args.changed:
        changed = _changed_repo_names(manifest, args.repos_dir)
        if repo_names is None:
            repo_names = changed
        else:
            repo_names = tuple(name for name in repo_names if name in changed)

    if repo_names is not None:
        unknown = sorted(set(repo_names) - set(manifest.names()))
        if unknown:
            print(f"ojuny-ci: unknown repositories: {', '.join(unknown)}", file=sys.stderr)
            return 2

    if args.dry_run:
        for repository in manifest.repositories:
            if repo_names is not None and repository.name not in repo_names:
                continue
            for tier in selected_tiers:
                for check in repository.checks_for(tier):
                    print(f"{repository.name}\t{tier}\t{check}")
        return 0

    started_at = datetime.now(timezone.utc).isoformat()
    results = run_checks(
        manifest=manifest,
        repos_dir=args.repos_dir,
        tiers=selected_tiers,
        repo_names=repo_names,
        jobs=args.jobs,
        timeout=args.timeout,
    )
    finished_at = datetime.now(timezone.utc).isoformat()

    if args.json_file:
        write_json(args.json_file, results, __version__, started_at, finished_at)
    if args.junit:
        write_junit(args.junit, results)
    if args.github_annotations:
        github_annotations(results)
    if args.json:
        payload = {
            "runner_version": __version__,
            "started_at": started_at,
            "finished_at": finished_at,
            "results": [result.as_dict() for result in results],
        }
        print(json.dumps(payload, indent=2))
    else:
        print_summary(results)

    if any(result.status in ("fail", "error") for result in results):
        return 1
    if results and all(result.status == "skip" for result in results):
        return 4
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        root = Path(__file__).resolve().parents[2]
        return subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=root,
        ).returncode

    manifest_path = args.repos_file or default_manifest()
    try:
        manifest = load_manifest(manifest_path)
    except ManifestError as error:
        print(f"ojuny-ci: {error}", file=sys.stderr)
        return 2

    if args.command == "list":
        for repository in manifest.repositories:
            systems = ", ".join(repository.systems)
            print(f"{repository.name} ({repository.kind}, {systems})")
            for tier in TIERS:
                checks = repository.checks_for(tier)
                if checks:
                    print(f"  {tier}: {', '.join(checks)}")
        return 0

    if args.command == "explain":
        try:
            repository = manifest.repo(args.repo)
        except KeyError:
            print(f"ojuny-ci: unknown repository: {args.repo}", file=sys.stderr)
            return 2
        print(f"name: {repository.name}")
        print(f"path: {repository.path}")
        print(f"kind: {repository.kind}")
        print(f"systems: {', '.join(repository.systems)}")
        print(f"hydraJobs: {repository.hydra_jobs or '(none)'}")
        for tier in TIERS:
            print(f"{tier}:")
            for check in repository.checks_for(tier):
                print(f"  {check}")
        return 0

    if args.command == "run":
        return _run(args, manifest)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
