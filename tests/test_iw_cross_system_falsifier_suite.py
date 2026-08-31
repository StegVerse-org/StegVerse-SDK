import json
from pathlib import Path

from scripts.run_iw_cross_system_falsifier_suite import evaluate_suite

FIXTURE = Path("inspection/examples/iw-cross-system-falsifier-suite-v0.1.json")


def _suite():
    return json.loads(FIXTURE.read_text())


def test_cross_system_suite_falsifies_temporal_order_dependence_and_early_commit():
    observed = {
        "cases": {
            "IW-X-ORDER-001": {
                "runs": [
                    {"run_id": "alpha", "arrival_order": ["A1", "A2"], "committed_action": "A1"},
                    {"run_id": "beta", "arrival_order": ["A2", "A1"], "committed_action": "A2"},
                ]
            },
            "IW-X-IRREV-001": {
                "lane_committed_action": "A1",
            },
            "IW-X-TEMPORAL-BOUNDARY-001": {
                "effect_used_prechange_resolution": True,
                "effect_prevented_or_reresolved": False,
            },
        }
    }
    result = evaluate_suite(_suite(), observed)
    by_id = {r["falsifier_id"]: r for r in result["results"]}
    assert by_id["IW-FALSIFIER-001"]["classification"] == "FAIL_TEMPORAL_ORDER_DEPENDENCE"
    assert by_id["IW-FALSIFIER-002"]["classification"] == "FAIL_IRREVERSIBLE_EARLY_COMMIT"
    assert by_id["IW-FALSIFIER-003"]["classification"] == "FAIL_TEMPORAL_BOUNDARY_AMBIGUITY"
    assert result["architecture_falsified"] is True


def test_cross_system_suite_accepts_matrix_stable_controls():
    observed = {
        "cases": {
            "IW-X-ORDER-001": {
                "runs": [
                    {"run_id": "alpha", "arrival_order": ["A1", "A2"], "committed_action": "A3"},
                    {"run_id": "beta", "arrival_order": ["A2", "A1"], "committed_action": "A3"},
                ]
            },
            "IW-X-IRREV-001": {
                "lane_committed_action": "A3",
            },
            "IW-X-TEMPORAL-BOUNDARY-001": {
                "temporal_resolution_to_effect_gap_exists": False,
                "effect_used_prechange_resolution": False,
                "effect_prevented_or_reresolved": False,
            },
        }
    }
    result = evaluate_suite(_suite(), observed)
    assert all(r["architecture_falsified"] is False for r in result["results"])
    assert result["architecture_falsified"] is False


def test_cross_system_suite_rejects_changed_arrival_order_fixture():
    observed = {
        "cases": {
            "IW-X-ORDER-001": {
                "runs": [
                    {"run_id": "alpha", "arrival_order": ["A2", "A1"], "committed_action": "A1"},
                    {"run_id": "beta", "arrival_order": ["A1", "A2"], "committed_action": "A2"},
                ]
            },
            "IW-X-IRREV-001": {"lane_committed_action": "A1"},
            "IW-X-TEMPORAL-BOUNDARY-001": {
                "effect_used_prechange_resolution": True,
                "effect_prevented_or_reresolved": False,
            },
        }
    }
    try:
        evaluate_suite(_suite(), observed)
    except ValueError as exc:
        assert "arrival_order_changed" in str(exc)
    else:
        raise AssertionError("changed fixture order must fail closed")


def test_cross_system_temporal_boundary_control_passes_when_boundary_is_proven_and_reresolved():
    observed = {
        "cases": {
            "IW-X-ORDER-001": {
                "runs": [
                    {"run_id": "alpha", "arrival_order": ["A1", "A2"], "committed_action": "A3"},
                    {"run_id": "beta", "arrival_order": ["A2", "A1"], "committed_action": "A3"},
                ]
            },
            "IW-X-IRREV-001": {"lane_committed_action": "A3"},
            "IW-X-TEMPORAL-BOUNDARY-001": {
                "temporal_resolution_to_effect_gap_exists": True,
                "declared_boundary_well_defined": True,
                "boundary_equivalence_established": True,
                "effect_used_prechange_resolution": False,
                "effect_prevented_or_reresolved": True,
            },
        }
    }
    result = evaluate_suite(_suite(), observed)
    by_id = {r["falsifier_id"]: r for r in result["results"]}
    assert by_id["IW-FALSIFIER-003"]["architecture_falsified"] is False
    assert by_id["IW-FALSIFIER-003"]["classification"] == "PASS_OR_NOT_FALSIFIED"
