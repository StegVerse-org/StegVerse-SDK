from __future__ import annotations

import pytest

from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_bundle import (
    ADMISSIBILITY_BUNDLE_SCHEMA,
    build_admissibility_bundle,
    build_bundle_from_bridge_result,
    bundle_hash,
    verify_admissibility_bundle,
)
from stegverse.admissibility_receipts import build_admissibility_receipt_reference
from stegverse.llm_admissibility import evaluate_llm_output_admissibility
from stegverse.math_admissibility import evaluate_math_artifact_admissibility


def _packet():
    return {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "generated": "2026-06-14T00:00:00Z",
        "tester": {
            "name_or_role": "bundle tester",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": "TEST-OBJECT-BUNDLE-0001",
            "object_type": "model_response",
            "summary": "Bundle test packet.",
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


def _bundle(execution_receipt=None):
    packet = _packet()
    result = evaluate_admissibility_packet(packet)
    reference = build_admissibility_receipt_reference(result)
    return build_admissibility_bundle(
        tester_packet=packet,
        result_packet=result,
        receipt_reference=reference,
        bridge_type="generic_tester_packet",
        execution_receipt=execution_receipt,
    )


def test_build_admissibility_bundle_shape():
    bundle = _bundle()

    assert bundle["schema"] == ADMISSIBILITY_BUNDLE_SCHEMA
    assert bundle["bridge_type"] == "generic_tester_packet"
    assert bundle["execution_receipt"] is None
    assert bundle["bundle_hash"].startswith("sha256:")
    assert bundle["hashes"]["tester_packet_hash"].startswith("sha256:")
    assert bundle["hashes"]["admissibility_result_hash"].startswith("sha256:")
    assert bundle["hashes"]["admissibility_reference_hash"].startswith("sha256:")
    assert bundle["hashes"]["execution_receipt_hash"] is None


def test_verify_admissibility_bundle_passes():
    assert verify_admissibility_bundle(_bundle()) is True


def test_verify_admissibility_bundle_fails_when_packet_is_mutated():
    bundle = _bundle()
    bundle["tester_packet"]["test_object"]["summary"] = "mutated"

    assert verify_admissibility_bundle(bundle) is False


def test_verify_admissibility_bundle_fails_when_reference_is_broken():
    bundle = _bundle()
    bundle["admissibility_receipt_reference"].pop("reference_hash")

    assert verify_admissibility_bundle(bundle) is False


def test_build_admissibility_bundle_with_execution_receipt():
    execution_receipt = {
        "receipt_id": "receipt-bundle-0001",
        "decision": "allow",
        "timestamp": "2026-06-14T00:00:00Z",
    }
    bundle = _bundle(execution_receipt=execution_receipt)

    assert bundle["execution_receipt"] == execution_receipt
    assert bundle["hashes"]["execution_receipt_hash"] == bundle_hash(execution_receipt)
    assert verify_admissibility_bundle(bundle) is True


def test_build_bundle_from_llm_bridge_result():
    bridge = evaluate_llm_output_admissibility(
        provider="openai",
        model="gpt-test",
        prompt="Draft note.",
        output="Draft governance note.",
        include_receipt_reference=True,
    )
    bundle = build_bundle_from_bridge_result(bridge)

    assert bundle["bridge_type"] == "llm_output"
    assert verify_admissibility_bundle(bundle) is True


def test_build_bundle_from_math_bridge_result():
    bridge = evaluate_math_artifact_admissibility(
        formalism_id="RTG-STCM",
        artifact_type="solver_artifact",
        artifact_summary="Placeholder derivation attempt.",
        include_receipt_reference=True,
    )
    bundle = build_bundle_from_bridge_result(bridge)

    assert bundle["bridge_type"] == "math_artifact"
    assert verify_admissibility_bundle(bundle) is True


def test_build_bundle_from_bridge_result_creates_missing_reference():
    bridge = evaluate_llm_output_admissibility(
        provider="openai",
        model="gpt-test",
        prompt="Draft note.",
        output="Draft governance note.",
        include_receipt_reference=False,
    )
    bundle = build_bundle_from_bridge_result(bridge)

    assert bundle["admissibility_receipt_reference"]["reference_id"].startswith("admref-")
    assert verify_admissibility_bundle(bundle) is True


def test_build_bundle_from_bridge_result_requires_packet_and_result():
    with pytest.raises(ValueError):
        build_bundle_from_bridge_result({"schema": "broken"})
