"""Execute the checks declared in the Ojuny CI manifest."""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from .manifest import Manifest, Repository


@dataclass
class CheckResult:
    repo: str
    check: str
    tier: str
    status: str
    duration_seconds: float
    log: str = ""
    message: str = ""
    artifacts: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "repo": self.repo,
            "check": self.check,
            "tier": self.tier,
            "status": self.status,
            "duration_seconds": round(self.duration_seconds, 3),
            "log": self.log or None,
            "message": self.message,
            "artifacts": self.artifacts,
        }


def _command(repository: Repository, check: str) -> list[str]:
    if check.startswith("meta:"):
        return [
            sys.executable,
            "-m",
            "ojuny_ci.metachecks",
            check[len("meta:") :],
            "--repo",
            ".",
        ]
    if check.startswith("script:"):
        return ["bash", "-c", check[len("script:") :]]
    if check.startswith("hydraJobs"):
        return ["nix", "eval", "--json", f".#{check}"]
    return ["nix", "build", "--no-link", "--print-out-paths", f".#{check}"]


def _run_one(
    repository: Repository,
    check: str,
    tier: str,
    cwd: Path,
    timeout: int | None,
) -> CheckResult:
    started = time.monotonic()
    if not cwd.is_dir():
        return CheckResult(repository.name, check, tier, "skip", 0.0, message=f"repository not found: {cwd}")
    if shutil.which("nix") is None and not check.startswith("script:"):
        return CheckResult(repository.name, check, tier, "skip", 0.0, message="nix is not on PATH")
    command = _command(repository, check)
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        duration = time.monotonic() - started
        output = (completed.stdout + completed.stderr).strip()
        status = "pass" if completed.returncode == 0 else "fail"
        return CheckResult(repository.name, check, tier, status, duration, log=output[-4000:])
    except subprocess.TimeoutExpired:
        duration = time.monotonic() - started
        return CheckResult(repository.name, check, tier, "fail", duration, message=f"timeout after {timeout}s")
    except FileNotFoundError as error:
        duration = time.monotonic() - started
        return CheckResult(repository.name, check, tier, "error", duration, message=str(error))


def run_checks(
    manifest: Manifest,
    repos_dir: Path,
    tiers: tuple[str, ...],
    repo_names: tuple[str, ...] | None = None,
    jobs: int = 1,
    timeout: int | None = None,
) -> list[CheckResult]:
    repositories = [
        repository
        for repository in manifest.repositories
        if repo_names is None or repository.name in repo_names
    ]
    tasks: list[tuple[Repository, str, str]] = []
    for repository in repositories:
        for tier in tiers:
            for check in repository.checks_for(tier):
                tasks.append((repository, check, tier))

    results: list[CheckResult] = []
    if jobs <= 1:
        for repository, check, tier in tasks:
            results.append(_run_one(repository, check, tier, repos_dir / repository.path, timeout))
    else:
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            futures = [
                pool.submit(_run_one, repository, check, tier, repos_dir / repository.path, timeout)
                for repository, check, tier in tasks
            ]
            for future in as_completed(futures):
                results.append(future.result())
    results.sort(key=lambda result: (result.repo, result.tier, result.check))
    return results
