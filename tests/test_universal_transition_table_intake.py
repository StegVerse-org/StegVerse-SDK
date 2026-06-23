from __future__ import annotations

import json
from pathlib import Path

import pytest

from stegverse.universal_transition_table_cli import main as intake_cli_main
from stegverse.universal_transition_table_intake import (
    UniversalTransitionTableIntakeError,
    handle_universal_transition_table_package,
)


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
    replay_path = tmp_path / "machine_replay_packet.json"
    write_json(package_path, package)
    write_json(expected_path, expected)
    write_json(replay_path, replay)
    return package_path, expected_path, replay_path


def test_universal_transition_table_intake_accepts_constructed_package(tmp_path: Path) -> None:
    package_path, expected_path, replay_path = make_fixture(tmp_path)

    result = handle_universal_transition_table_package(package_path, expected_path, replay_path)

    assert result["manifest"]["package_id"] == "canonical-only-package-001"
    assert result["manifest"]["route_eligible"] is True
    assert result["intake_receipt"]["accepted_for_intake"] is True
    assert result["route_eligibility_receipt"]["route_eligible"] is True


def test_universal_transition_table_intake_rejects_blocked_package(tmp_path: Path) -> None:
    package_path, expected_path, replay_path = make_fixture(tmp_path)
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    replay["blocked_reasons"] = ["adjacent_term_unconfirmed"]
    write_json(replay_path, replay)

    with pytest.raises(UniversalTransitionTableIntakeError):
        handle_universal_transition_table_package(package_path, expected_path, replay_path)


def test_universal_transition_table_cli_writes_output(tmp_path: Path) -> None:
    package_path, expected_path, replay_path = make_fixture(tmp_path)
    out_path = tmp_path / "sdk_intake_result.json"

    status = intake_cli_main(
        [
            "--package",
            str(package_path),
            "--expected",
            str(expected_path),
            "--replay",
            str(replay_path),
            "--out",
            str(out_path),
        ]
    )

    result = json.loads(out_path.read_text(encoding="utf-8"))
    assert status == 0
    assert result["manifest"]["route_eligible"] is True
    assert result["intake_receipt"]["accepted_for_intake"] is True
