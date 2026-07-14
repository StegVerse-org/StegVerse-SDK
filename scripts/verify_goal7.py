#!/usr/bin/env python3
"""Verify the SDK Goal 7 repo-standards gate-record surface offline."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print("$ " + " ".join(command))
    print(result.stdout.rstrip())
    if result.returncode:
        raise SystemExit(result.returncode)


def verify_public_api() -> None:
    from stegverse import (
        REPO_STANDARDS_GATE_ALLOWED_STATES,
        REPO_STANDARDS_GATE_RECORD_SCHEMA_VERSION,
        RepoStandardsGateRecordError,
        build_repo_standards_gate_record,
        validate_repo_standards_gate_record,
    )

    assert REPO_STANDARDS_GATE_RECORD_SCHEMA_VERSION == "1.0.0"
    assert "PENDING" in REPO_STANDARDS_GATE_ALLOWED_STATES
    record = build_repo_standards_gate_record(
        record_id="goal7-verification",
        repository="StegVerse-org/StegVerse-SDK",
        gate_state="PENDING",
        source_repository="StegVerse-Labs/repo-standards",
        source_ref="release-pending",
        evidence_refs=["docs/REPO_STANDARDS_GATE_RECORD.md"],
        owner="upstream gate owner",
        next_action="wait for durable upstream gate evidence",
    )
    validate_repo_standards_gate_record(record)
    assert record["record_sha256"]
    assert record["authority_boundaries"]["sdk_validation_is_release_authority"] is False
    assert issubclass(RepoStandardsGateRecordError, ValueError)


def main() -> int:
    verify_public_api()
    run([sys.executable, "-m", "pytest", "tests/test_repo_standards_gate_record.py", "-v"])
    print("SDK_GOAL7_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
