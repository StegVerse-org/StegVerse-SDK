from __future__ import annotations

from stegverse.math_admissibility import (
    build_math_tester_packet,
    evaluate_math_artifact_admissibility,
    summarize_math_admissibility,
)


def test_build_math_tester_packet_shape():
    packet = build_math_tester_packet(
        formalism_id="RTG-STCM",
        artifact_type="solver_artifact",
        artifact_summary="Placeholder derivation attempt.",
        declared_intent="formalism_support_claim",
    )

    assert packet["schema"] == "stegverse.governed_admissibility.tester_output.v1"
    assert packet["tester"]["discipline_id"] == "mathematics_formal_methods"
    assert packet["tester"]["domain_review_required"] is True
    assert packet["test_object"]["object_type"] == "solver_artifact"
    assert packet["test_object"]["formalism_id"] == "RTG-STCM"
    assert packet["classification"]["declared_intent"] == "formalism_support_claim"
    assert packet["classification"]["evidence_posture"] == "research_note"
    assert packet["classification"]["replay_posture"] == "not_replayable"


def test_evaluate_math_artifact_default_requires_receipt_or_review_path():
    bridge = evaluate_math_artifact_admissibility(
        formalism_id="RTG-STCM",
        artifact_type="solver_artifact",
        artifact_summary="Placeholder derivation attempt.",
        declared_intent="formalism_support_claim",
    )
    summary = summarize_math_admissibility(bridge)

    assert bridge["schema"] == "stegverse.math_admissibility.bridge_result.v1"
    assert bridge["tester_packet"]["tester"]["discipline_id"] == "mathematics_formal_methods"
    assert bridge["decision"] in {"REQUIRE_REVIEW", "REQUIRE_REPLAY", "REQUIRE_RECEIPT", "ALLOW_AS_NOTE"}
    assert summary["decision"] == bridge["decision"]


def test_evaluate_math_artifact_high_consequence_without_authority_fails_closed():
    bridge = evaluate_math_artifact_admissibility(
        formalism_id="RTG-STCM",
        artifact_type="solver_artifact",
        artifact_summary="Artifact proposed for high consequence operational decision.",
        declared_intent="action_decision",
        authority_source=None,
        evidence_posture="source_backed",
        replay_posture="partially_replayable",
        consequence_level="high",
    )

    assert bridge["decision"] == "FAIL_CLOSED"
    assert bridge["allowed_next_state"] == "fail_closed"


def test_evaluate_math_artifact_receipt_backed_low_consequence_allows_with_posture():
    bridge = evaluate_math_artifact_admissibility(
        formalism_id="RTG-STCM",
        artifact_type="solver_artifact",
        artifact_summary="Receipt-backed derivation note.",
        declared_intent="public_claim",
        authority_source="formalism-review-placeholder",
        evidence_posture="receipt_backed",
        replay_posture="receipt_backed",
        consequence_level="low",
    )

    assert bridge["decision"] == "ALLOW_WITH_POSTURE"
    assert bridge["allowed_next_state"] == "receipt_backed_claim"
    assert bridge["receipt_posture"] == "receipt_backed"
