"""Example local receipt reference for a dynamic admissibility result."""

from __future__ import annotations

import json

from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_receipts import build_admissibility_receipt_reference


def build_result_packet():
    packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "generated": "2026-06-14T00:00:00Z",
        "tester": {
            "name_or_role": "receipt reference example",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": "TEST-OBJECT-RECEIPT-REF-EXAMPLE",
            "object_type": "model_response",
            "summary": "Example packet for local admissibility receipt reference.",
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


def main() -> None:
    result = build_result_packet()
    reference = build_admissibility_receipt_reference(result)

    print("# dynamic admissibility result")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("\n# local admissibility receipt reference")
    print(json.dumps(reference, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
