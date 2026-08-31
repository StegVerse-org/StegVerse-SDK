from stegverse.iw_matrix_falsifier import (
    evaluate_irreversible_early_commit_falsifier,
    evaluate_temporal_order_falsifier,
)


def test_temporal_order_dependence_falsifies_when_order_is_not_governed():
    result = evaluate_temporal_order_falsifier(
        {
            "case_id": "ORDER-001",
            "governed_input_hash": "sha256:GEAIW-SAME",
            "candidate_set_hash": "sha256:A1-A2-A3-SAME",
            "order_is_explicit_governed_input": False,
            "runs": [
                {"run_id": "alpha", "arrival_order": ["A1", "A2"], "committed_action": "A1"},
                {"run_id": "beta", "arrival_order": ["A2", "A1"], "committed_action": "A2"},
            ],
        }
    )
    assert result["order_varied"] is True
    assert result["committed_action_varied"] is True
    assert result["architecture_falsified"] is True
    assert result["classification"] == "FAIL_TEMPORAL_ORDER_DEPENDENCE"


def test_temporal_order_difference_is_not_failure_when_order_is_explicit_governed_input():
    result = evaluate_temporal_order_falsifier(
        {
            "case_id": "ORDER-EXPLICIT-001",
            "governed_input_hash": "sha256:GEAIW-SAME",
            "candidate_set_hash": "sha256:A1-A2-SAME",
            "order_is_explicit_governed_input": True,
            "runs": [
                {"run_id": "alpha", "arrival_order": ["A1", "A2"], "committed_action": "A1"},
                {"run_id": "beta", "arrival_order": ["A2", "A1"], "committed_action": "A2"},
            ],
        }
    )
    assert result["architecture_falsified"] is False


def test_same_matrix_resolution_across_orders_passes():
    result = evaluate_temporal_order_falsifier(
        {
            "case_id": "ORDER-MATRIX-001",
            "governed_input_hash": "sha256:GEAIW-SAME",
            "candidate_set_hash": "sha256:A1-A2-A3-SAME",
            "order_is_explicit_governed_input": False,
            "runs": [
                {"run_id": "alpha", "arrival_order": ["A1", "A2"], "committed_action": "A3"},
                {"run_id": "beta", "arrival_order": ["A2", "A1"], "committed_action": "A3"},
                {"run_id": "gamma", "arrival_order": ["A1", "A2"], "committed_action": "A3"},
            ],
        }
    )
    assert result["architecture_falsified"] is False
    assert result["committed_action_varied"] is False


def test_irreversible_early_commit_falsifies_lane_correct_but_action_wrong():
    result = evaluate_irreversible_early_commit_falsifier(
        {
            "case_id": "IRREV-001",
            "lane_committed_action": "A1",
            "matrix_resolved_action": "A3",
            "lane_local_checks_all_passed": True,
            "coupled_information_existed_before_boundary": True,
            "coupled_information_within_declared_scope": True,
            "matrix_resolution_unique": True,
            "lane_crossed_action_boundary": True,
            "consequence_irreversible": True,
        }
    )
    assert result["architecture_falsified"] is True
    assert result["classification"] == "FAIL_IRREVERSIBLE_EARLY_COMMIT"
    assert result["action_mismatch"] is True


def test_unavailable_future_information_does_not_falsify():
    result = evaluate_irreversible_early_commit_falsifier(
        {
            "case_id": "IRREV-FUTURE-001",
            "lane_committed_action": "A1",
            "matrix_resolved_action": "A3",
            "lane_local_checks_all_passed": True,
            "coupled_information_existed_before_boundary": False,
            "coupled_information_within_declared_scope": True,
            "matrix_resolution_unique": True,
            "lane_crossed_action_boundary": True,
            "consequence_irreversible": True,
        }
    )
    assert result["architecture_falsified"] is False


def test_lane_action_matching_unique_matrix_action_passes():
    result = evaluate_irreversible_early_commit_falsifier(
        {
            "case_id": "IRREV-MATCH-001",
            "lane_committed_action": "A3",
            "matrix_resolved_action": "A3",
            "lane_local_checks_all_passed": True,
            "coupled_information_existed_before_boundary": True,
            "coupled_information_within_declared_scope": True,
            "matrix_resolution_unique": True,
            "lane_crossed_action_boundary": True,
            "consequence_irreversible": True,
        }
    )
    assert result["architecture_falsified"] is False
