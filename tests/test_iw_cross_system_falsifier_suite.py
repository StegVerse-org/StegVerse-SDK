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
        }
    }
    result = evaluate_suite(_suite(), observed)
    by_id = {r["falsifier_id"]: r for r in result["results"]}
    assert by_id["IW-FALSIFIER-001"]["classification"] == "FAIL_TEMPORAL_ORDER_DEPENDENCE"
    assert by_id["IW-FALSIFIER-002"]["classification"] == "FAIL_IRREVERSIBLE_EARLY_COMMIT"
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
        }
    }
    try:
        evaluate_suite(_suite(), observed)
    except ValueError as exc:
        assert "arrival_order_changed" in str(exc)
    else:
        raise AssertionError("changed fixture order must fail closed")
