import pytest

from stegverse import (
    GovernedLLMSessionValidationError,
    validate_governed_llm_session_packet,
)


def base_session_packet():
    return {
        "provider_request": {"provider": "fixture", "model": "fixture", "messages": []},
        "provider_request_hash": "request-hash",
        "provider_response": {
            "provider": "fixture",
            "model": "fixture",
            "output": "read only output",
            "request_hash": "request-hash",
            "response_hash": "response-hash",
        },
        "continuity": {"freshness_status": "current", "evidence": []},
        "adapter_result": {
            "decision": "ALLOW",
            "admissibility_status": "allowed_read_only_candidate",
            "reconstruction": {"decision": "ALLOW"},
        },
        "action_route": {"route_status": "no_action_route_required", "action_candidates": []},
        "commitment_request": {"status": "no_commitment_request_required"},
        "authority_decision": {"decision": "NOT_REQUIRED", "authority_decision_hash": "authority-hash"},
        "execution_handoff": {"status": "not_executable", "execution_handoff_hash": "handoff-hash"},
    }


def test_read_only_governed_session_packet_allows():
    decision = validate_governed_llm_session_packet(base_session_packet())

    assert decision.decision == "ALLOW"
    assert decision.adapter_decision == "ALLOW"
    assert decision.authority_decision == "NOT_REQUIRED"
    assert decision.execution_status == "not_executable"


def test_quarantined_governed_session_packet_quarantines():
    packet = base_session_packet()
    packet["adapter_result"]["decision"] = "QUARANTINE"
    packet["adapter_result"]["admissibility_status"] = "requires_fresh_retrieval"
    packet["commitment_request"] = {"status": "requires_downstream_commit_time_standing"}
    packet["authority_decision"] = {"decision": "FAIL_CLOSED", "authority_decision_hash": "authority-hash"}

    decision = validate_governed_llm_session_packet(packet)

    assert decision.decision == "QUARANTINE"
    assert decision.reason == "adapter quarantined output before consequence"


def test_provider_hash_mismatch_raises():
    packet = base_session_packet()
    packet["provider_response"]["request_hash"] = "wrong"

    with pytest.raises(GovernedLLMSessionValidationError):
        validate_governed_llm_session_packet(packet)


def test_ready_for_external_executor_without_allow_fails_closed():
    packet = base_session_packet()
    packet["authority_decision"] = {"decision": "FAIL_CLOSED", "authority_decision_hash": "authority-hash"}
    packet["execution_handoff"] = {"status": "ready_for_external_executor", "execution_handoff_hash": "handoff-hash"}

    decision = validate_governed_llm_session_packet(packet)

    assert decision.decision == "FAIL_CLOSED"
    assert decision.reason == "execution handoff claims readiness without ALLOW authority decision"
