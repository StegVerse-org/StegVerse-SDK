#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

FORBIDDEN_FRAGMENTS = (
    "${{ secrets.",
    "${{ github.token",
    "github-token:",
    "contents: write",
    "id-token: write",
    "packages: write",
    "actions/checkout@",
    "actions/setup-python@",
    "actions/upload-artifact@",
    "actions/download-artifact@",
    "actions/github-script@",
    "softprops/action-gh-release@",
    "gh-action-pypi-publish@",
    "twine upload",
    "git push",
    "secrets: inherit",
)

FORBIDDEN_AUTOMATIC_TRIGGERS = (
    "  push:",
    "  pull_request:",
    "  schedule:",
    "  workflow_run:",
)


def validate_workflow(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []

    if "permissions: {}" not in text:
        failures.append("permissions_not_empty")

    for fragment in FORBIDDEN_FRAGMENTS:
        if fragment in text:
            failures.append(f"forbidden_fragment:{fragment}")

    for trigger in FORBIDDEN_AUTOMATIC_TRIGGERS:
        if trigger in text:
            failures.append(f"automatic_hosted_trigger:{trigger.strip()}")

    # Hosted fallback may be manually dispatched or invoked as a non-authorizing
    # reusable validation wrapper. It must not be the canonical continuation path.
    if "workflow_dispatch:" not in text and "workflow_call:" not in text:
        failures.append("no_manual_or_reusable_entry")

    return failures


def main() -> int:
    if not WORKFLOWS.is_dir():
        raise SystemExit("GITHUB_FALLBACK_BOUNDARY_FAIL: workflows directory missing")

    results: dict[str, list[str]] = {}
    for path in sorted(WORKFLOWS.glob("*.yml")):
        failures = validate_workflow(path)
        if failures:
            results[path.relative_to(ROOT).as_posix()] = failures

    if results:
        for path, failures in results.items():
            print(f"FAIL {path}: {', '.join(failures)}")
        raise SystemExit(1)

    print("GITHUB_FALLBACK_BOUNDARY_PASS")
    print("Hosted workflows are manual/reusable fallback only, permissions-empty, non-mutating, non-publishing, non-secret-bearing, and non-authoritative.")
    print("Canonical credentials and release authority remain TV/TVC + sovereign/local tooling.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
