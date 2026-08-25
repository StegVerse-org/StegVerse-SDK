from __future__ import annotations

import importlib.metadata
import re
from typing import Any, Iterable, Mapping

DEPENDENCY_ALIGNMENT_SCHEMA = "stegverse.sdk.release-dependency-alignment.v1"
EXPECTED_GOVERNED_DEPENDENCIES = {
    "stegcore": "StegVerse-Labs/StegCore",
    "stegverse-core-lite": "Data-Continuation/core-lite",
    "stegverse-master-records": "master-records/orchestration",
}
_GIT_PIN = re.compile(
    r"^\s*([A-Za-z0-9_.-]+)\s*@\s*git\+https://github\.com/([^/@\s]+/[^/@\s]+)\.git@([0-9a-fA-F]{40})(?:\s*;.*)?$"
)


def _release_component_executable_commits(release_receipt: Mapping[str, Any]) -> dict[str, str]:
    components = release_receipt.get("components")
    if not isinstance(components, list):
        return {}
    result: dict[str, str] = {}
    for item in components:
        if not isinstance(item, Mapping):
            continue
        repository = str(item.get("repository") or "").strip()
        executable = str(
            item.get("source_parent_commit")
            or item.get("source_parent_commit_sha")
            or item.get("commit_sha")
            or item.get("commit")
            or ""
        ).strip().lower()
        if repository and len(executable) == 40 and all(ch in "0123456789abcdef" for ch in executable):
            result[repository] = executable
    return result


def parse_governed_test_git_pins(requirements: Iterable[str]) -> dict[str, dict[str, str]]:
    pins: dict[str, dict[str, str]] = {}
    for raw in requirements:
        text = str(raw or "").strip()
        if "extra == \"governed-test\"" not in text and "extra == 'governed-test'" not in text and "extra == \"governed_test\"" not in text:
            continue
        match = _GIT_PIN.match(text)
        if not match:
            continue
        package, repository, commit = match.groups()
        pins[package.lower()] = {
            "package": package,
            "repository": repository,
            "commit_sha": commit.lower(),
        }
    return pins


def verify_governed_test_dependency_alignment(
    requirements: Iterable[str],
    release_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    pins = parse_governed_test_git_pins(requirements)
    expected_commits = _release_component_executable_commits(release_receipt)
    reasons: list[str] = []
    observations: list[dict[str, Any]] = []

    for package, repository in EXPECTED_GOVERNED_DEPENDENCIES.items():
        pin = pins.get(package)
        expected = expected_commits.get(repository)
        if pin is None:
            reasons.append(f"{package}:governed_test_git_pin_missing")
            continue
        if pin["repository"] != repository:
            reasons.append(f"{package}:repository_mismatch")
        if expected is None:
            reasons.append(f"{package}:release_component_missing")
        elif pin["commit_sha"] != expected:
            reasons.append(f"{package}:commit_mismatch")
        observations.append(
            {
                "package": package,
                "repository": repository,
                "installed_pin_commit_sha": pin["commit_sha"],
                "release_executable_commit_sha": expected,
                "aligned": expected is not None and pin["repository"] == repository and pin["commit_sha"] == expected,
            }
        )

    unexpected = sorted(set(pins) - set(EXPECTED_GOVERNED_DEPENDENCIES))
    if unexpected:
        reasons.extend(f"unexpected_governed_test_git_pin:{name}" for name in unexpected)

    return {
        "schema": DEPENDENCY_ALIGNMENT_SCHEMA,
        "verified": not reasons,
        "reasons": reasons or ["ok"],
        "observations": observations,
        "authority_effect": "NONE",
    }


def verify_installed_governed_test_dependency_alignment(
    release_receipt: Mapping[str, Any],
    *,
    distribution_name: str = "stegverse-sdk",
) -> dict[str, Any]:
    try:
        requirements = importlib.metadata.requires(distribution_name)
    except importlib.metadata.PackageNotFoundError as exc:
        raise RuntimeError("installed_stegverse_sdk_distribution_not_found") from exc
    if requirements is None:
        requirements = []
    return verify_governed_test_dependency_alignment(requirements, release_receipt)


__all__ = [
    "DEPENDENCY_ALIGNMENT_SCHEMA",
    "EXPECTED_GOVERNED_DEPENDENCIES",
    "parse_governed_test_git_pins",
    "verify_governed_test_dependency_alignment",
    "verify_installed_governed_test_dependency_alignment",
]
