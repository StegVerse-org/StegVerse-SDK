from __future__ import annotations

from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_bundle import build_admissibility_bundle
from stegverse.admissibility_receipts import build_admissibility_receipt_reference
from stegverse.admissibility_replay import REPLAY_RESULT_SCHEMA, replay_admissibility_bundle


def _bundle():
    packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "generated": "2026-06-14T00:00:00Z",
        "tester": {
            "name_or_role": "replay tester",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": "TEST-OBJECT-REPLAY-0001",
            "object_type": "model_response",
            "summary": "Replay test packet.",
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
    return build_admissibility_bundle(
        tester_packet=packet,
        result_packet=result,
        receipt_reference=reference,
    )


def test_replay_admissibility_bundle_success():
    replay = replay_admissibility_bundle(_bundle())

    assert replay["schema"] == REPLAY_RESULT_SCHEMA
    assert replay["bundle_valid"] is True
    assert replay["replay_success"] is True
    assert replay["classification_match"]["decision"] is True
    assert replay["classification_match"]["allowed_next_state"] is True
    assert replay["hash_match"]["tester_packet_hash"] is True


def test_replay_admissibility_bundle_detects_mutated_packet():
    bundle = _bundle()
    bundle["tester_packet"]["classification"]["consequence_level"] = "high"

    replay = replay_admissibility_bundle(bundle)

    assert replay["bundle_valid"] is False
    assert replay["replay_success"] is False


def test_replay_admissibility_bundle_missing_packet_fails():
    replay = replay_admissibility_bundle({"schema": "broken"})

    assert replay["schema"] == REPLAY_RESULT_SCHEMA
    assert replay["bundle_valid"] is False
    assert replay["replay_success"] is False
    assert replay["reason"] == "bundle missing tester_packet"
