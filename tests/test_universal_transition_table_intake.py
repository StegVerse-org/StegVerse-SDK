from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from stegverse.universal_transition_table_cli import main as intake_cli_main
from stegverse.universal_transition_table_intake import (
    UniversalTransitionTableIntakeError,
    handle_universal_transition_table_package,
)

ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def make_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    package = {
        "package_id": "canonical-only-package-001",
        "canonical_cells": ["BOUNDARY_REVIEW", "RECEIPT_REQUIREMENT"],
        "receipt_requirements": ["term_resolution_receipt", "package_construction_receipt"],
        "human_readable_result_required": True,
        "machine_replay_required": True,
    }
    expected = {
        "package_id": "canonical-only-package-001",
        "expected_construction_status": "CONSTRUCTED",
        "expected_route_eligibility": True,
    }
    replay = {
        "package_id": "canonical-only-package-001",
        "sdk_route_eligible": True,
        "blocked_reasons": [],
    }

    package_path = tmp_path / "transition_test_package.json"
    expected_path = tmp_path / "expected_result.json"
    replay_path = tmp_path / "replay_packet.json"
    write_json(package_path, package)
    write_json(expected_path, expected)
    write_json(replay_path, replay)
    return package_path, expected_path, replay_path


def make_commitment_candidate(tmp_path: Path) -> Path:
    candidate = {
        "package_id": "canonical-only-package-001",
        "candidate_type": "COMMITMENT_CANDIDATE",
        "authorizing": False,
        "inherits_review_authority": False,
        "implies_standing": False,
        "requires_fresh_standing_determination": True,
        "bounded_scope": "sdk-intake-proof-path-only",
        "actor": "review_subject",
        "target": "sdk_boundary",
        "action": "present_reviewed_transition_for_standing_check",
        "review_ref": "review-artifact-001",
        "evidence_refs": ["evidence-packet-001"],
        "policy_context": "policy-context-current",
        "delegation_context": "delegation-context-current",
        "validity_window": {"not_before": "2026-01-01T00:00:00Z", "not_after": "2026-01-02T00:00:00Z"},
        "execution_context": "sdk-intake-boundary",
        "recoverability_profile": "recoverable-no-runtime-execution",
    }
    candidate_path = tmp_path / "commitment_candidate.json"
    write_json(candidate_path, candidate)
    return candidate_path


def run_tool(tool_name: str) -> str:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / tool_name)],
        cwd=str(ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def test_universal_transition_table_intake_accepts_constructed_package(tmp_path: Path) -> None:
    package_path, expected_path, replay_path = make_fixture(tmp_path)

    result = handle_universal_transition_table_package(package_path, expected_path, replay_path)

    assert result["manifest"]["package_id"] == "canonical-only-package-001"
    assert result["manifest"]["route_eligible"] is True
    assert result["intake_receipt"]["accepted_for_intake"] is True
    assert result["route_eligibility_receipt"]["route_eligible"] is True


def test_universal_transition_table_intake_accepts_non_authorizing_candidate(tmp_path: Path) -> None:
    package_path, expected_path, replay_path = make_fixture(tmp_path)
    candidate_path = make_commitment_candidate(tmp_path)

    result = handle_universal_transition_table_package(
        package_path,
        expected_path,
        replay_path,
        candidate_path,
    )

    assert result["commitment_candidate_receipt"]["accepted_as_non_authorizing"] is True
    assert result["commitment_candidate_receipt"]["authorizing"] is False
    assert result["commitment_candidate_receipt"]["inherits_review_authority"] is False
    assert result["commitment_candidate_receipt"]["implies_standing"] is False
    assert result["route_eligibility_receipt"]["fresh_standing_determination_required"] is True


def test_universal_transition_table_intake_rejects_authorizing_candidate(tmp_path: Path) -> None:
    package_path, expected_path, replay_path = make_fixture(tmp_path)
    candidate_path = make_commitment_candidate(tmp_path)
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["authorizing"] = True
    write_json(candidate_path, candidate)

    with pytest.raises(UniversalTransitionTableIntakeError):
        handle_universal_transition_table_package(package_path, expected_path, replay_path, candidate_path)


def test_universal_transition_table_intake_rejects_blocked_package(tmp_path: Path) -> None:
    package_path, expected_path, replay_path = make_fixture(tmp_path)
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    replay["blocked_reasons"] = ["adjacent_term_unconfirmed"]
    write_json(replay_path, replay)

    with pytest.raises(UniversalTransitionTableIntakeError):
        handle_universal_transition_table_package(package_path, expected_path, replay_path)


def test_universal_transition_table_cli_writes_output(tmp_path: Path) -> None:
    package_path, expected_path, replay_path = make_fixture(tmp_path)
    candidate_path = make_commitment_candidate(tmp_path)
    out_path = tmp_path / "sdk_intake_result.json"

    status = intake_cli_main(
        [
            "--package",
            str(package_path),
            "--expected",
            str(expected_path),
            "--replay",
            str(replay_path),
            "--commitment-candidate",
            str(candidate_path),
            "--out",
            str(out_path),
        ]
    )

    result = json.loads(out_path.read_text(encoding="utf-8"))
    assert status == 0
    assert result["manifest"]["route_eligible"] is True
    assert result["intake_receipt"]["accepted_for_intake"] is True
    assert result["commitment_candidate_receipt"]["accepted_as_non_authorizing"] is True


def test_universal_transition_table_repo_fixture_verifier_passes() -> None:
    stdout = run_tool("verify_universal_transition_table_intake_fixture.py")

    assert "PASS universal transition-table intake fixture verified" in stdout
    assert "PASS wrote SDK intake result" in stdout


def test_sdk_goal2_activation_verifier_passes() -> None:
    stdout = run_tool("verify_goal2_activation.py")

    assert "PASS SDK Goal 2 fixture files present" in stdout
    assert "PASS SDK Goal 2 commitment candidate invariant holds" in stdout
    assert "PASS SDK Goal 2 activation verified" in stdout
