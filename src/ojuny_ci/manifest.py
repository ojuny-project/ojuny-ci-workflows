"""Load and validate the Ojuny CI repository manifest."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TIERS = ("fast", "nix", "heavy")
KINDS = ("flake", "script", "missing")


class ManifestError(ValueError):
    """Raised when the manifest is invalid."""


@dataclass(frozen=True)
class Repository:
    name: str
    path: str
    kind: str
    systems: tuple[str, ...]
    checks: dict[str, tuple[str, ...]]
    hydra_jobs: str | None = None

    def checks_for(self, tier: str) -> tuple[str, ...]:
        return self.checks.get(tier, ())


@dataclass(frozen=True)
class Manifest:
    version: int
    repositories: tuple[Repository, ...]
    global_checks: dict[str, tuple[str, ...]]

    def repo(self, name: str) -> Repository:
        for repository in self.repositories:
            if repository.name == name:
                return repository
        raise KeyError(name)

    def names(self) -> tuple[str, ...]:
        return tuple(repository.name for repository in self.repositories)


def _check_list(value: Any, where: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ManifestError(f"{where} must be a list of strings")
    return tuple(value)


def _tiers(value: Any, where: str) -> dict[str, tuple[str, ...]]:
    if value is None:
        value = {}
    if not isinstance(value, dict):
        raise ManifestError(f"{where} must be an object")
    unknown = set(value) - set(TIERS)
    if unknown:
        raise ManifestError(f"{where} has unknown tiers: {sorted(unknown)}")
    return {tier: _check_list(value.get(tier), f"{where}.{tier}") for tier in TIERS}


def load_manifest(path: Path) -> Manifest:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ManifestError(f"manifest not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ManifestError(f"manifest is not valid JSON: {error}") from error

    if not isinstance(data, dict):
        raise ManifestError("manifest must be an object")
    if data.get("version") != 1:
        raise ManifestError("manifest version must be 1")

    repositories = data.get("repositories")
    if not isinstance(repositories, list):
        raise ManifestError("repositories must be a list")

    parsed: list[Repository] = []
    seen: set[str] = set()
    for index, entry in enumerate(repositories):
        where = f"repositories[{index}]"
        if not isinstance(entry, dict):
            raise ManifestError(f"{where} must be an object")
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            raise ManifestError(f"{where}.name must be a non-empty string")
        if name in seen:
            raise ManifestError(f"duplicate repository: {name}")
        seen.add(name)
        path_value = entry.get("path")
        if not isinstance(path_value, str) or not path_value:
            raise ManifestError(f"{where}.path must be a non-empty string")
        kind = entry.get("kind", "flake")
        if kind not in KINDS:
            raise ManifestError(f"{where}.kind must be one of {KINDS}")
        systems = entry.get("systems", ["x86_64-linux"])
        if not isinstance(systems, list) or not all(isinstance(item, str) for item in systems):
            raise ManifestError(f"{where}.systems must be a list of strings")
        checks = _tiers(entry.get("checks"), f"{where}.checks")
        hydra_jobs = entry.get("hydraJobs")
        if hydra_jobs is not None and not isinstance(hydra_jobs, str):
            raise ManifestError(f"{where}.hydraJobs must be a string")
        parsed.append(Repository(name, path_value, kind, tuple(systems), checks, hydra_jobs))

    global_checks = _tiers(data.get("global"), "global")
    return Manifest(version=1, repositories=tuple(parsed), global_checks=global_checks)
