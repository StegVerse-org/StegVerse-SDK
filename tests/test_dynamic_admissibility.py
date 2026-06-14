from __future__ import annotations

import pytest

from stegverse.admissibility import (
    evaluate_admissibility_packet,
    result_to_decision,
    stable_hash,
    validate_tester_packet,
)


def base_packet(**classification_overrides):
    classification = {
        "declared_intent": "public_claim",
        "authority_source": None,
        "evidence_posture": "draft",
        "replay_posture": "not_replayable",
        "consequence_level": "medium",
        "claim_limit": "Research-note only until authority and evidence are declared.",
    }
    classification.update(classification_overrides)
    return {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "generated": "2026-06-14T00:00:00Z",
        "tester": {
            "name_or_role": "AI / LLM systems tester",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": "TEST-OBJECT-UNIT-0001",
            "object_type": "model_response",
            "summary": "Unit test packet.",
            "source_or_reference": "pytest",
        },
        "route": {
            "recommended_route": [
                "governance_filter",
                "llm_governance_comparison",
                "fail_closed",
            ],
            "tests_run": ["governance_filter"],
            "route_deviation_reason": None,
        },
        "classification": classification,
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
    }


def test_valid_research_note_packet_allows_as_note():
    packet = base_packet()

    errors = validate_tester_packet(packet)
    result = evaluate_admissibility_packet(packet)

    assert errors == []
    assert result["schema"] == "stegverse.governed_admissibility.dynamic_demo_result.v1"
    assert result["classification"]["decision"] == "ALLOW_AS_NOTE"
    assert result["classification"]["allowed_next_state"] == "research_note"
    assert result["receipt_posture"] == "sdk_local_not_receipt_backed"
    assert result["local_receipt_hash"].startswith("sha256:")


def test_missing_authority_requires_review_for_non_high_consequence():
    packet = base_packet(
        declared_intent="research_summary",
        evidence_posture="source_backed",
        replay_posture="partially_replayable",
        consequence_level="low",
    )

    result = evaluate_admissibility_packet(packet)

    assert result["classification"]["decision"] == "REQUIRE_REVIEW"
    assert result["classification"]["allowed_next_state"] == "hold"
    assert any("authority" in item.lower() for item in result["classification"]["required_follow_up"])


def test_high_consequence_without_authority_fails_closed():
    packet = base_packet(
        declared_intent="care_decision",
        authority_source=None,
        evidence_posture="source_backed",
        replay_posture="partially_replayable",
        consequence_level="high",
    )
    packet["tester"]["discipline_id"] = "medicine_health"
    packet["tester"]["domain_review_required"] = True

    result = evaluate_admissibility_packet(packet)

    assert result["classification"]["decision"] == "FAIL_CLOSED"
    assert result["classification"]["allowed_next_state"] == "fail_closed"


def test_receipt_backed_low_consequence_with_authority_allows_with_posture():
    packet = base_packet(
        declared_intent="public_claim",
        authority_source="reviewer-authority-placeholder",
        evidence_posture="receipt_backed",
        replay_posture="receipt_backed",
        consequence_level="low",
    )

    result = evaluate_admissibility_packet(packet)
    compact = result_to_decision(result)

    assert result["classification"]["decision"] == "ALLOW_WITH_POSTURE"
    assert result["classification"]["allowed_next_state"] == "receipt_backed_claim"
    assert result["receipt_posture"] == "receipt_backed"
    assert compact.decision == "ALLOW_WITH_POSTURE"
    assert compact.allowed_next_state == "receipt_backed_claim"


def test_strict_validation_raises_on_missing_fields():
    packet = {"schema": "stegverse.governed_admissibility.tester_output.v1"}

    errors = validate_tester_packet(packet)
    assert errors

    with pytest.raises(ValueError):
        evaluate_admissibility_packet(packet, strict=True)


def test_stable_hash_is_deterministic_for_same_payload_order_independent():
    left = {"b": 2, "a": 1}
    right = {"a": 1, "b": 2}

    assert stable_hash(left) == stable_hash(right)
    assert stable_hash(left).startswith("sha256:")
