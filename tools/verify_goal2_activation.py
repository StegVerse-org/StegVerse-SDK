#!/usr/bin/env python3
"""Verify Goal 2 activation for SDK universal transition-table intake."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "universal_transition_table_intake"
RESULT = FIXTURE / "sdk_intake_result.json"

REQUIRED_FILES = [
    "README.md",
    "transition_test_package.json",
    "expected_result.json",
    "replay_packet.json",
    "commitment_candidate.json",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    for filename in REQUIRED_FILES:
        require((FIXTURE / filename).exists(), f"missing fixture file: {filename}")

    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "verify_universal_transition_table_intake_fixture.py")],
        cwd=ROOT,
        check=True,
    )

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    require(result["manifest"]["route_eligible"] is True, "manifest route eligibility must be true")
    require(result["manifest"]["commitment_candidate_present"] is True, "commitment candidate must be present")
    require(result["manifest"]["requires_fresh_standing_determination"] is True, "fresh standing determination must be required")
    require(result["commitment_candidate_receipt"]["accepted_as_non_authorizing"] is True, "candidate must be accepted as non-authorizing")
    require(result["commitment_candidate_receipt"]["authorizing"] is False, "candidate must not authorize")
    require(result["commitment_candidate_receipt"]["inherits_review_authority"] is False, "candidate must not inherit review authority")
    require(result["commitment_candidate_receipt"]["implies_standing"] is False, "candidate must not imply standing")
    require(result["route_eligibility_receipt"]["fresh_standing_determination_required"] is True, "route receipt must require fresh standing determination")

    print("PASS SDK Goal 2 fixture files present")
    print("PASS SDK Goal 2 fixture verifier passes")
    print("PASS SDK Goal 2 commitment candidate invariant holds")
    print("PASS SDK Goal 2 activation verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
