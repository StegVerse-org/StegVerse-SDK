from __future__ import annotations

import stegverse


def test_dynamic_admissibility_helpers_are_exported():
    assert callable(stegverse.evaluate_admissibility_packet)
    assert callable(stegverse.validate_tester_packet)
    assert callable(stegverse.result_to_decision)
    assert callable(stegverse.stable_hash)
    assert stegverse.TESTER_OUTPUT_SCHEMA == "stegverse.governed_admissibility.tester_output.v1"
    assert stegverse.DYNAMIC_RESULT_SCHEMA == "stegverse.governed_admissibility.dynamic_demo_result.v1"


def test_public_api_evaluates_basic_packet():
    packet = {
        "schema": stegverse.TESTER_OUTPUT_SCHEMA,
        "generated": "2026-06-14T00:00:00Z",
        "tester": {
            "name_or_role": "public api tester",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": "TEST-OBJECT-PUBLIC-API-0001",
            "object_type": "model_response",
            "summary": "Public API import test.",
        },
        "route": {
            "recommended_route": ["governance_filter", "llm_governance_comparison", "fail_closed"],
            "tests_run": ["governance_filter"],
            "route_deviation_reason": None,
        },
        "classification": {
            "declared_intent": "public_claim",
            "authority_source": None,
            "evidence_posture": "draft",
            "replay_posture": "not_replayable",
            "consequence_level": "medium",
            "claim_limit": "Research-note only until authority and evidence are declared.",
        },
        "boundary": {
            "does_not_certify_domain_correctness": True,
            "does_not_replace_domain_review": True,
            "does_not_create_proof_authority": True,
        },
    }

    result = stegverse.evaluate_admissibility_packet(packet)
    compact = stegverse.result_to_decision(result)

    assert result["classification"]["decision"] == "ALLOW_AS_NOTE"
    assert compact.decision == "ALLOW_AS_NOTE"
    assert result["local_receipt_hash"].startswith("sha256:")
