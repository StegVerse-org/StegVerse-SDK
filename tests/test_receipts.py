#!/usr/bin/env python3
"""Tests for receipt verification."""

from stegverse import verify_receipt
from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_receipts import build_admissibility_receipt_reference


def _admissibility_reference():
    packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "generated": "2026-06-14T00:00:00Z",
        "tester": {
            "name_or_role": "execution receipt reference tester",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": "TEST-OBJECT-EXEC-RECEIPT-0001",
            "object_type": "model_response",
            "summary": "Execution receipt reference test packet.",
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
    return build_admissibility_receipt_reference(evaluate_admissibility_packet(packet))


def test_valid_receipt():
    receipt = {
        "receipt_id": "r-001",
        "decision": "allow",
        "timestamp": "2026-04-28T18:18:00Z",
    }
    assert verify_receipt(receipt) is True


def test_invalid_receipt_missing_field():
    receipt = {
        "receipt_id": "r-002",
        "decision": "deny",
        # missing timestamp
    }
    assert verify_receipt(receipt) is False


def test_empty_receipt():
    assert verify_receipt({}) is False


def test_valid_receipt_with_admissibility_reference():
    receipt = {
        "receipt_id": "r-003",
        "decision": "allow",
        "timestamp": "2026-06-14T00:00:00Z",
        "admissibility_receipt_reference": _admissibility_reference(),
    }
    assert verify_receipt(receipt) is True


def test_invalid_receipt_with_broken_admissibility_reference():
    reference = _admissibility_reference()
    reference.pop("reference_hash")
    receipt = {
        "receipt_id": "r-004",
        "decision": "allow",
        "timestamp": "2026-06-14T00:00:00Z",
        "admissibility_receipt_reference": reference,
    }
    assert verify_receipt(receipt) is False


def test_invalid_receipt_with_malformed_admissibility_reference():
    receipt = {
        "receipt_id": "r-005",
        "decision": "allow",
        "timestamp": "2026-06-14T00:00:00Z",
        "admissibility_receipt_reference": "not-a-reference",
    }
    assert verify_receipt(receipt) is False


if __name__ == "__main__":
    test_valid_receipt()
    test_invalid_receipt_missing_field()
    test_empty_receipt()
    test_valid_receipt_with_admissibility_reference()
    test_invalid_receipt_with_broken_admissibility_reference()
    test_invalid_receipt_with_malformed_admissibility_reference()
    print("\nALL RECEIPT TESTS PASSED")
