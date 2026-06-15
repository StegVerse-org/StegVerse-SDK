"""Check a Governed Admissibility Bundle."""

from __future__ import annotations

import json

from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_bundle import build_admissibility_bundle
from stegverse.admissibility_receipts import build_admissibility_receipt_reference
from stegverse.admissibility_replay import replay_admissibility_bundle


def main() -> None:
    packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "generated": "2026-06-14T00:00:00Z",
        "tester": {
            "name_or_role": "bundle check example",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": "TEST-OBJECT-BUNDLE-CHECK-DEMO",
            "object_type": "model_response",
            "summary": "Example packet for governed admissibility bundle check.",
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
    reference = build_admissibility_receipt_reference(result)
    bundle = build_admissibility_bundle(
        tester_packet=packet,
        result_packet=result,
        receipt_reference=reference,
        bridge_type="generic_tester_packet",
    )
    check = replay_admissibility_bundle(bundle)
    print(json.dumps({"bundle": bundle, "check": check}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
