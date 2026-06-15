"""Verify execution receipts with and without admissibility references."""

from __future__ import annotations

import json

from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_receipts import build_admissibility_receipt_reference
from stegverse.receipts import verify_receipt


def build_admissibility_reference():
    packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "generated": "2026-06-14T00:00:00Z",
        "tester": {
            "name_or_role": "receipt verification example",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": "TEST-OBJECT-VERIFY-RECEIPT-EXAMPLE",
            "object_type": "model_response",
            "summary": "Example packet for execution receipt verification.",
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
    result = evaluate_admissibility_packet(packet)
    return build_admissibility_receipt_reference(result)


def main() -> None:
    legacy_receipt = {
        "receipt_id": "receipt-legacy-0001",
        "decision": "allow",
        "timestamp": "2026-06-14T00:00:00Z",
    }

    attached_receipt = {
        "receipt_id": "receipt-with-admissibility-0001",
        "decision": "allow",
        "timestamp": "2026-06-14T00:00:00Z",
        "admissibility_receipt_reference": build_admissibility_reference(),
    }

    output = {
        "legacy_receipt_valid": verify_receipt(legacy_receipt),
        "attached_receipt_valid": verify_receipt(attached_receipt),
        "legacy_receipt": legacy_receipt,
        "attached_receipt": attached_receipt,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
