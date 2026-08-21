from __future__ import annotations

import copy

from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.execution_boundary import (
    EXECUTION_BOUNDARY_CASE_SCHEMA,
    evaluate_execution_boundary_case,
)


def _packet(*, object_id: str = "T-CANDIDATE", authority: str = "AUTH-001", high: bool = False):
    discipline = "education_learning" if not high else "robotics_autonomy"
    consequence = "low" if not high else "critical"
    declared_intent = "research_summary" if not high else "motion"
    packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "tester": {
            "name_or_role": "execution-boundary-test",
            "discipline_id": discipline,
            "domain_review_required": high,
        },
        "test_object": {
            "object_id": object_id,
            "object_type": "candidate_transition",
            "summary": "Execution-boundary candidate.",
        },
        "route": {
            "recommended_route": ["transition_admissibility", "receipt_replay", "fail_closed"],
            "tests_run": ["transition_admissibility"],
            "route_deviation_reason": None,
        },
        "classification": {
            "declared_intent": declared_intent,
            "authority_source": authority,
            "evidence_posture": "receipt_backed",
            "replay_posture": "receipt_backed",
            "consequence_level": consequence,
            "claim_limit": "Execution-boundary fixture.",
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
    }
    return packet


def _result(*, high: bool = False, authority: str = "AUTH-001"):
    return evaluate_admissibility_packet(_packet(high=high, authority=authority), strict=True)


def _case(initial, boundary, *, consequence_status="pending", alterable=True):
    return {
        "schema": EXECUTION_BOUNDARY_CASE_SCHEMA,
        "case_id": "CASE-001",
        "candidate_transition": {"transition_id": "T-CANDIDATE"},
        "initial_admissibility": initial,
        "intervening_transitions": [
            {
                "transition_id": "ENV-1",
                "from_state_hash": "sha256:state-0",
                "to_state_hash": "sha256:state-1",
                "materially_relevant": True,
                "observed": True,
                "observed_at": "2026-08-21T12:00:00Z",
            }
        ],
        "boundary_admissibility": boundary,
        "consequence": {
            "status": consequence_status,
            "alterable_at_boundary": alterable,
        },
    }


def test_boundary_allow_requires_fresh_current_admissibility_not_history_alone():
    initial = _result()
    boundary = _result()

    result = evaluate_execution_boundary_case(_case(initial, boundary))

    assert result["classification"]["decision"] == "PERMIT_CONSEQUENCE"
    assert result["historical_authorization"]["held_constant"] is True
    assert result["historical_authorization"]["establishes_current_admissibility_by_itself"] is False
    assert result["boundary_reassessment"]["continuing_admissibility_established"] is True
    assert result["falsification"]["outcome"] == "PASS_MINIMUM_N1_BOUNDARY_CASE"


def test_changed_state_can_invalidate_candidate_while_authority_remains_constant():
    initial = _result()
    boundary = _result(high=True)

    # Both evaluations bind to the same candidate and the same authority source.
    # The high-consequence boundary result fails closed because its consequential
    # relation is not explicitly established.
    result = evaluate_execution_boundary_case(_case(initial, boundary, consequence_status="prevented"))

    assert initial["classification"]["decision"] == "ALLOW_WITH_POSTURE"
    assert boundary["classification"]["decision"] == "FAIL_CLOSED"
    assert result["historical_authorization"]["held_constant"] is True
    assert result["classification"]["decision"] == "PREVENT_CONSEQUENCE"
    assert result["classification"]["basis"] == "historical_authorization_does_not_establish_continuing_admissibility"
    assert result["falsification"]["outcome"] == "PASS_MINIMUM_N1_BOUNDARY_CASE"


def test_unobserved_material_transition_makes_observation_boundary_insufficient():
    initial = _result()
    boundary = _result()
    case = _case(initial, boundary)
    case["intervening_transitions"][0]["observed"] = False

    result = evaluate_execution_boundary_case(case)

    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["continuity"]["basis"] == "material_transition_not_observed"
    assert result["falsification"]["outcome"] == "INDETERMINATE_EVIDENCE_BOUNDARY"


def test_authority_change_invalidates_hold_constant_falsification_case():
    initial = _result(authority="AUTH-001")
    boundary = _result(authority="AUTH-002")

    result = evaluate_execution_boundary_case(_case(initial, boundary))

    assert result["historical_authorization"]["held_constant"] is False
    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["evidence_standard"]["independently_reconstructable"] is False


def test_tampered_boundary_receipt_fails_closed():
    initial = _result()
    boundary = _result()
    tampered = copy.deepcopy(boundary)
    tampered["classification"]["decision"] = "ALLOW_TAMPERED"

    result = evaluate_execution_boundary_case(_case(initial, tampered))

    assert result["boundary_reassessment"]["receipt_integrity_valid"] is False
    assert result["classification"]["decision"] == "FAIL_CLOSED"


def test_consequence_after_prevent_disposition_is_falsification_failure():
    initial = _result()
    boundary = _result(high=True)

    result = evaluate_execution_boundary_case(_case(initial, boundary, consequence_status="executed"))

    assert result["classification"]["decision"] == "PREVENT_CONSEQUENCE"
    assert result["consequence"]["conforms_to_boundary_disposition"] is False
    assert result["falsification"]["outcome"] == "FAIL_CONSEQUENCE_NONCONFORMANCE"


def test_irreversible_boundary_is_too_late_and_fails_closed():
    initial = _result()
    boundary = _result()

    result = evaluate_execution_boundary_case(_case(initial, boundary, alterable=False))

    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert "Evaluate before the consequence becomes safely irreversible." in result["classification"]["required_follow_up"]
