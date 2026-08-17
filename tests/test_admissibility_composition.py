from __future__ import annotations

import copy

from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_composition import (
    JOINT_RELATION_SCHEMA,
    evaluate_admissibility_composition,
)


def _component(object_id: str):
    packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "tester": {
            "name_or_role": "composition-test",
            "discipline_id": "education_learning",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": object_id,
            "object_type": "model_response",
            "summary": "Individually admissible component.",
        },
        "route": {
            "recommended_route": ["transition_admissibility", "receipt_replay", "fail_closed"],
            "tests_run": ["transition_admissibility"],
            "route_deviation_reason": None,
        },
        "classification": {
            "declared_intent": "research_summary",
            "authority_source": "AUTH-STATIC-001",
            "evidence_posture": "receipt_backed",
            "replay_posture": "receipt_backed",
            "consequence_level": "low",
            "claim_limit": "Composition falsification fixture.",
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
    }
    return evaluate_admissibility_packet(packet, strict=True)


def _joint_relation():
    return {
        "schema": JOINT_RELATION_SCHEMA,
        "relation_id": "JOINT-REL-001",
        "relation_status": "validated",
        "authority_source": "JOINT-RELATION-REVIEW-001",
        "evidence_posture": "receipt_backed",
        "replay_posture": "receipt_backed",
    }


def test_two_individually_admissible_components_do_not_imply_composition_admissibility():
    a = _component("A")
    b = _component("B")

    assert a["classification"]["decision"] == "ALLOW_WITH_POSTURE"
    assert b["classification"]["decision"] == "ALLOW_WITH_POSTURE"

    result = evaluate_admissibility_composition(
        [a, b],
        composition_id="A+B",
        joint_consequence_level="critical",
    )

    assert result["all_components_individually_admissible"] is True
    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["classification"]["allowed_next_state"] == "fail_closed"
    assert result["relation"]["status"] == "unresolved"
    assert result["relation"]["maturity_class"] == "under_development"
    assert result["relation"]["basis"] == "no_explicit_composition_admissibility_relation"
    assert result["separability"]["component_admissibility_implies_composition_admissibility"] is False


def test_validated_joint_relation_is_a_distinct_positive_control_not_execution_authority():
    a = _component("A")
    b = _component("B")

    result = evaluate_admissibility_composition(
        [a, b],
        composition_id="A+B-VALIDATED",
        joint_consequence_level="low",
        joint_relation=_joint_relation(),
    )

    assert result["classification"]["decision"] == "ALLOW_WITH_POSTURE"
    assert result["classification"]["allowed_next_state"] == "composition_relation_backed_claim"
    assert result["relation"]["status"] == "resolved"
    assert result["relation"]["maturity_class"] == "known_composition_with_posture"
    assert result["joint_relation_valid"] is True
    assert result["boundary"]["does_not_grant_execution_authority"] is True
    assert result["boundary"]["does_not_execute_components"] is True


def test_tampered_component_receipt_fails_closed_even_with_joint_relation():
    a = _component("A")
    b = _component("B")
    tampered = copy.deepcopy(b)
    tampered["classification"]["allowed_next_state"] = "tampered"

    result = evaluate_admissibility_composition(
        [a, tampered],
        composition_id="A+B-TAMPERED",
        joint_consequence_level="low",
        joint_relation=_joint_relation(),
    )

    assert result["component_integrity"] is False
    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["relation"]["basis"] == "component_receipt_integrity_failure"


def test_nonadmissible_component_blocks_composition():
    a = _component("A")
    blocked_packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "tester": {
            "name_or_role": "composition-test",
            "discipline_id": "medicine_health",
            "domain_review_required": True,
        },
        "test_object": {"object_id": "BLOCKED", "object_type": "care_decision", "summary": "Blocked component."},
        "route": {"recommended_route": ["fail_closed"], "tests_run": ["fail_closed"], "route_deviation_reason": None},
        "classification": {
            "declared_intent": "care_decision",
            "authority_source": None,
            "evidence_posture": "source_backed",
            "replay_posture": "partially_replayable",
            "consequence_level": "high",
            "claim_limit": "No consequential movement.",
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
    }
    blocked = evaluate_admissibility_packet(blocked_packet, strict=True)

    result = evaluate_admissibility_composition(
        [a, blocked],
        composition_id="A+BLOCKED",
        joint_consequence_level="low",
        joint_relation=_joint_relation(),
    )

    assert result["all_components_individually_admissible"] is False
    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["relation"]["basis"] == "one_or_more_components_not_individually_admissible"
