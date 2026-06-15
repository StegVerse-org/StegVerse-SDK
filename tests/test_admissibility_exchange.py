from __future__ import annotations

import pytest

from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_bundle import build_admissibility_bundle
from stegverse.admissibility_exchange import (
    GAX_EXCHANGE_SCHEMA,
    build_gax_exchange,
    export_gax_json,
    load_gax_json,
    verify_gax_exchange,
)
from stegverse.admissibility_receipts import build_admissibility_receipt_reference


def _bundle():
    packet = {
        "schema": "stegverse.governed_admissibility.tester_output.v1",
        "generated": "2026-06-14T00:00:00Z",
        "tester": {
            "name_or_role": "exchange tester",
            "discipline_id": "ai_llm_systems",
            "domain_review_required": False,
        },
        "test_object": {
            "object_id": "TEST-OBJECT-GAX-0001",
            "object_type": "model_response",
            "summary": "Exchange test packet.",
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


def test_build_gax_exchange_shape():
    exchange = build_gax_exchange(
        _bundle(),
        producer_component="sdk-test",
        producer_version="1.0-test",
        notes=["unit test"],
        related_formalisms=["RTG", "STCM"],
    )

    assert exchange["schema"] == GAX_EXCHANGE_SCHEMA
    assert exchange["exchange_type"] == "bundle_export"
    assert exchange["producer"]["component"] == "sdk-test"
    assert exchange["attachments"]["notes"] == ["unit test"]
    assert exchange["attachments"]["related_formalisms"] == ["RTG", "STCM"]
    assert verify_gax_exchange(exchange) is True


def test_verify_gax_exchange_fails_for_broken_bundle():
    exchange = build_gax_exchange(_bundle())
    exchange["bundle"]["bundle_hash"] = "sha256:broken"

    assert verify_gax_exchange(exchange) is False


def test_gax_json_round_trip():
    exchange = build_gax_exchange(_bundle(), related_formalisms=["RTG"])
    payload = export_gax_json(exchange)
    loaded = load_gax_json(payload)

    assert loaded == exchange
    assert verify_gax_exchange(loaded) is True


def test_load_gax_json_requires_object():
    with pytest.raises(ValueError):
        load_gax_json("[]")
