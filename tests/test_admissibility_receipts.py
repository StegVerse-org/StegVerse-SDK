from __future__ import annotations

from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_receipts import (
    ADMISSIBILITY_RECEIPT_REFERENCE_SCHEMA,
    build_admissibility_receipt_reference,
    verify_admissibility_receipt_reference,
)


def _result_packet():
    packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "generated": "2026-06-14T00:00:00Z",
        "tester": {
            "name_or_role": "receipt reference tester",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": "TEST-OBJECT-RECEIPT-REF-0001",
            "object_type": "model_response",
            "summary": "Receipt reference test packet.",
        },
        "route": {
            "recommended_route": ["governance_filter", "llm_governance_comparison", "fail_closed"],
            "tests_run": ["governance_filter"],
            "route_deviation_reason": None,
        },
        "classification": {
            "declared_intent": "research_note",
            "authority_source": None,
            "evidence_posture": "draft",
            "replay_posture": "not_replayable",
            "consequence_level": "medium",
            "claim_limit": "Research-note only.",
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
    }
    return evaluate_admissibility_packet(packet)


def test_build_admissibility_receipt_reference_shape():
    result = _result_packet()
    reference = build_admissibility_receipt_reference(result)

    assert reference["schema"] == ADMISSIBILITY_RECEIPT_REFERENCE_SCHEMA
    assert reference["reference_id"].startswith("admref-")
    assert reference["result_hash"].startswith("sha256:")
    assert reference["reference_hash"].startswith("sha256:")
    assert reference["decision"] == result["classification"]["decision"]
    assert reference["allowed_next_state"] == result["classification"]["allowed_next_state"]
    assert reference["boundary"]["does_not_create_execution_proof"] is True


def test_verify_admissibility_receipt_reference():
    reference = build_admissibility_receipt_reference(_result_packet())

    assert verify_admissibility_receipt_reference(reference) is True

    broken = dict(reference)
    broken.pop("reference_hash")
    assert verify_admissibility_receipt_reference(broken) is False


def test_custom_reference_id_and_source_are_preserved():
    reference = build_admissibility_receipt_reference(
        _result_packet(),
        reference_id="admref-custom",
        source="unit-test",
    )

    assert reference["reference_id"] == "admref-custom"
    assert reference["source"] == "unit-test"
    assert verify_admissibility_receipt_reference(reference) is True
