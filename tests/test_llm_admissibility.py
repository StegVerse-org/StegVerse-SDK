from __future__ import annotations

from stegverse.llm_admissibility import (
    build_llm_tester_packet,
    evaluate_llm_output_admissibility,
    summarize_llm_admissibility,
)


def test_build_llm_tester_packet_shape():
    packet = build_llm_tester_packet(
        provider="openai",
        model="gpt-test",
        prompt="Explain governed admissibility.",
        output="Governed admissibility classifies allowed next state.",
        declared_intent="public_claim",
    )

    assert packet["schema"] == "stegverse.governed_admissibility.tester_output.v1"
    assert packet["tester"]["discipline_id"] == "ai_llm_systems"
    assert packet["test_object"]["object_type"] == "model_response"
    assert packet["test_object"]["provider"] == "openai"
    assert packet["test_object"]["model"] == "gpt-test"
    assert packet["classification"]["declared_intent"] == "public_claim"
    assert packet["classification"]["evidence_posture"] == "draft"
    assert packet["classification"]["replay_posture"] == "not_replayable"


def test_evaluate_llm_output_admissibility_research_note_default():
    bridge = evaluate_llm_output_admissibility(
        provider="openai",
        model="gpt-test",
        prompt="Draft a governance note.",
        output="This is a draft governance note.",
        declared_intent="research_note",
    )
    summary = summarize_llm_admissibility(bridge)

    assert bridge["schema"] == "stegverse.llm_admissibility.bridge_result.v1"
    assert bridge["tester_packet"]["tester"]["discipline_id"] == "ai_llm_systems"
    assert bridge["admissibility_result"]["classification"]["decision"] == "ALLOW_AS_NOTE"
    assert summary["decision"] == "ALLOW_AS_NOTE"
    assert summary["allowed_next_state"] == "research_note"


def test_evaluate_llm_output_admissibility_high_consequence_without_authority_fails_closed():
    bridge = evaluate_llm_output_admissibility(
        provider="openai",
        model="gpt-test",
        prompt="What should happen next?",
        output="A high consequence action should happen.",
        declared_intent="action_decision",
        authority_source=None,
        evidence_posture="source_backed",
        replay_posture="partially_replayable",
        consequence_level="high",
    )

    assert bridge["decision"] == "FAIL_CLOSED"
    assert bridge["allowed_next_state"] == "fail_closed"


def test_evaluate_llm_output_admissibility_receipt_backed_low_consequence_allows_with_posture():
    bridge = evaluate_llm_output_admissibility(
        provider="openai",
        model="gpt-test",
        prompt="Summarize receipt-backed evidence.",
        output="The summary references the receipt-backed evidence.",
        declared_intent="public_claim",
        authority_source="reviewer-authority-placeholder",
        evidence_posture="receipt_backed",
        replay_posture="receipt_backed",
        consequence_level="low",
    )

    assert bridge["decision"] == "ALLOW_WITH_POSTURE"
    assert bridge["allowed_next_state"] == "receipt_backed_claim"
    assert bridge["receipt_posture"] == "receipt_backed"
