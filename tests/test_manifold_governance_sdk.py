import json
from pathlib import Path

import pytest

pytest.importorskip("stegcore")

from stegverse.manifold_governance import (
    PRODUCTION_RUNTIME,
    evaluate_manifold_governance,
)


FIXTURE = Path(__file__).resolve().parents[1] / "stegverse" / "demo_data" / "manifold_governance_reviewable.json"


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_sdk_calls_canonical_production_manifold_governance():
    result = evaluate_manifold_governance(load_fixture())

    assert result["production_runtime"] == PRODUCTION_RUNTIME
    assert result["parallel_evaluator"] is False
    assert result["sdk_grants_authority"] is False
    assert result["sdk_reinterprets_disposition"] is False
    assert result["external_execution_performed_by_sdk"] is False

    action = result["action"]
    assert action["state"] == "REVIEWABLE"
    assert action["continue_transition_ids"] == ("T-SENSOR-A", "T-SENSOR-B")
    assert action["review_transition_ids"] == ("T-PROTECTED-RELEASE",)
    assert action["held_transition_ids"] == ("T-AFTER-REVIEW",)
    assert action["denied_transition_ids"] == ()
    assert action["fail_closed_transition_ids"] == ()
    assert action["external_execution_performed"] is False
    assert action["authority_effect"] == "NONE_UNTIL_SEPARATE_GOVERNED_COMMIT"

    projection = action["reviewable_projection"]
    invariants = projection["governance_invariants"]
    assert invariants["human_in_the_loop_timing_is_governance_authority"] is False
    assert invariants["wall_clock_is_governance_authority"] is False
    assert invariants["heartbeat_is_governance_authority"] is False
    assert invariants["linear_transition_path_required"] is False
    assert invariants["machine_speed_internal_transitions_may_continue_inside_existing_authority"] is True
    assert invariants["protected_boundary_crossing_requires_external_authority"] is True


def test_sdk_demo_cli_uses_same_production_runtime(capsys):
    from stegverse.cli import main

    assert main(["demo", "manifold-governance"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["production_runtime"] == PRODUCTION_RUNTIME
    assert payload["action"]["state"] == "REVIEWABLE"


def test_sdk_run_cli_accepts_evaluator_packet(tmp_path, capsys):
    from stegverse.cli import main

    packet_path = tmp_path / "manifold.json"
    packet_path.write_text(json.dumps(load_fixture()), encoding="utf-8")
    assert main(["run", "manifold-governance", "--input", str(packet_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["production_runtime"] == PRODUCTION_RUNTIME
    assert payload["input_transition_count"] == 4
