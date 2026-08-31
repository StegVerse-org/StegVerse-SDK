"""SDK-local falsifiers for temporal-lane versus coupled IW matrix governance.

The evaluator is side-effect free and non-authorizing. It compares supplied
execution traces against declared coupled-matrix outcomes and detects:
1) undeclared temporal order dependence; and
2) irreversible early commit before relevant coupled-manifold resolution; and
3) temporal resolution-to-effect boundary ambiguity.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

RESULT_SCHEMA = "stegverse.iw-matrix-falsifier.result.v1"


def _required_text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name}_required")
    return text


def evaluate_temporal_order_falsifier(case: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate IW-FALSIFIER-001.

    Expected:
      case_id
      governed_input_hash
      candidate_set_hash
      order_is_explicit_governed_input: bool
      runs: [{run_id, arrival_order: [...], committed_action}]
    """
    case_id = _required_text(case.get("case_id"), "case_id")
    governed_input_hash = _required_text(case.get("governed_input_hash"), "governed_input_hash")
    candidate_set_hash = _required_text(case.get("candidate_set_hash"), "candidate_set_hash")
    runs = case.get("runs")
    if not isinstance(runs, Sequence) or isinstance(runs, (str, bytes)) or len(runs) < 2:
        raise ValueError("at_least_two_runs_required")

    orders = []
    actions = []
    normalized = []
    for run in runs:
        if not isinstance(run, Mapping):
            raise ValueError("run_must_be_object")
        run_id = _required_text(run.get("run_id"), "run_id")
        order = run.get("arrival_order")
        if not isinstance(order, Sequence) or isinstance(order, (str, bytes)) or not order:
            raise ValueError("arrival_order_required")
        order_tuple = tuple(str(x) for x in order)
        action = _required_text(run.get("committed_action"), "committed_action")
        orders.append(order_tuple)
        actions.append(action)
        normalized.append({"run_id": run_id, "arrival_order": list(order_tuple), "committed_action": action})

    order_varied = len(set(orders)) > 1
    action_varied = len(set(actions)) > 1
    order_explicit = case.get("order_is_explicit_governed_input") is True
    falsified = order_varied and action_varied and not order_explicit

    return {
        "schema": RESULT_SCHEMA,
        "falsifier_id": "IW-FALSIFIER-001",
        "case_id": case_id,
        "governed_input_hash": governed_input_hash,
        "candidate_set_hash": candidate_set_hash,
        "runs": normalized,
        "order_varied": order_varied,
        "committed_action_varied": action_varied,
        "order_is_explicit_governed_input": order_explicit,
        "architecture_falsified": falsified,
        "classification": "FAIL_TEMPORAL_ORDER_DEPENDENCE" if falsified else "PASS_OR_NOT_FALSIFIED",
        "invariant": "lane_order_must_not_change_action_unless_order_is_explicitly_governed",
        "boundary": {
            "sdk_grants_execution_authority": False,
            "sdk_executes_actions": False,
            "github_actions_is_runtime_authority": False,
        },
    }


def evaluate_irreversible_early_commit_falsifier(case: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate IW-FALSIFIER-002.

    The falsifier requires coupled information to have existed before A1's
    Action boundary. This avoids turning an unknowable future fact into a test
    requirement.
    """
    case_id = _required_text(case.get("case_id"), "case_id")
    lane_action = _required_text(case.get("lane_committed_action"), "lane_committed_action")
    matrix_action = _required_text(case.get("matrix_resolved_action"), "matrix_resolved_action")

    lane_local_checks_all_passed = case.get("lane_local_checks_all_passed") is True
    coupled_information_existed_before_boundary = case.get("coupled_information_existed_before_boundary") is True
    coupled_information_within_declared_scope = case.get("coupled_information_within_declared_scope") is True
    matrix_resolution_unique = case.get("matrix_resolution_unique") is True
    lane_crossed_action_boundary = case.get("lane_crossed_action_boundary") is True
    consequence_irreversible = case.get("consequence_irreversible") is True

    preconditions = all(
        [
            lane_local_checks_all_passed,
            coupled_information_existed_before_boundary,
            coupled_information_within_declared_scope,
            matrix_resolution_unique,
            lane_crossed_action_boundary,
            consequence_irreversible,
        ]
    )
    action_mismatch = lane_action != matrix_action
    falsified = preconditions and action_mismatch

    return {
        "schema": RESULT_SCHEMA,
        "falsifier_id": "IW-FALSIFIER-002",
        "case_id": case_id,
        "lane_committed_action": lane_action,
        "matrix_resolved_action": matrix_action,
        "lane_local_checks_all_passed": lane_local_checks_all_passed,
        "coupled_information_existed_before_boundary": coupled_information_existed_before_boundary,
        "coupled_information_within_declared_scope": coupled_information_within_declared_scope,
        "matrix_resolution_unique": matrix_resolution_unique,
        "lane_crossed_action_boundary": lane_crossed_action_boundary,
        "consequence_irreversible": consequence_irreversible,
        "action_mismatch": action_mismatch,
        "architecture_falsified": falsified,
        "classification": "FAIL_IRREVERSIBLE_EARLY_COMMIT" if falsified else "PASS_OR_NOT_FALSIFIED",
        "invariant": "lane_correctness_does_not_imply_action_correctness",
        "boundary": {
            "sdk_grants_execution_authority": False,
            "sdk_executes_actions": False,
            "github_actions_is_runtime_authority": False,
        },
    }


def evaluate_temporal_boundary_ambiguity_falsifier(case: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate IW-FALSIFIER-003.

    This falsifier targets architectures that resolve admissibility before a
    later operational effect and therefore depend on a well-defined,
    commitment-consistent temporal boundary.

    It does not apply when governance resolution and Action are the same
    authoritative operation and there is no later governance commit/effect
    interval to preserve.
    """
    case_id = _required_text(case.get("case_id"), "case_id")

    temporal_gap_exists = case.get("temporal_resolution_to_effect_gap_exists") is True
    declared_boundary_well_defined = case.get("declared_boundary_well_defined") is True
    boundary_equivalence_established = case.get("boundary_equivalence_established") is True
    material_change_between_resolution_and_effect = (
        case.get("material_change_between_resolution_and_effect") is True
    )
    material_change_governance_relevant = case.get("material_change_governance_relevant") is True
    effect_used_prechange_resolution = case.get("effect_used_prechange_resolution") is True
    prevented_or_reresolved = case.get("effect_prevented_or_reresolved") is True

    applicable = temporal_gap_exists
    boundary_unproven = not (declared_boundary_well_defined and boundary_equivalence_established)
    hazardous_gap = (
        material_change_between_resolution_and_effect
        and material_change_governance_relevant
        and effect_used_prechange_resolution
        and not prevented_or_reresolved
    )
    falsified = applicable and boundary_unproven and hazardous_gap

    if not applicable:
        classification = "NOT_APPLICABLE_NO_TEMPORAL_GAP"
    elif falsified:
        classification = "FAIL_TEMPORAL_BOUNDARY_AMBIGUITY"
    else:
        classification = "PASS_OR_NOT_FALSIFIED"

    return {
        "schema": RESULT_SCHEMA,
        "falsifier_id": "IW-FALSIFIER-003",
        "case_id": case_id,
        "temporal_resolution_to_effect_gap_exists": temporal_gap_exists,
        "declared_boundary_well_defined": declared_boundary_well_defined,
        "boundary_equivalence_established": boundary_equivalence_established,
        "material_change_between_resolution_and_effect": material_change_between_resolution_and_effect,
        "material_change_governance_relevant": material_change_governance_relevant,
        "effect_used_prechange_resolution": effect_used_prechange_resolution,
        "effect_prevented_or_reresolved": prevented_or_reresolved,
        "architecture_falsified": falsified,
        "classification": classification,
        "invariant": (
            "a_temporal_resolution_to_effect_model_must_prove_its_boundary_and_"
            "preserve_or_reresolve_governance_across_material_change"
        ),
        "boundary": {
            "sdk_grants_execution_authority": False,
            "sdk_executes_actions": False,
            "github_actions_is_runtime_authority": False,
        },
    }


__all__ = [
    "RESULT_SCHEMA",
    "evaluate_temporal_order_falsifier",
    "evaluate_irreversible_early_commit_falsifier",
    "evaluate_temporal_boundary_ambiguity_falsifier",
]
