from stegverse import intake_governed_llm_session_packet


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


def test_intake_routes_allowed_read_only_packet():
    result = intake_governed_llm_session_packet(base_session_packet())

    assert result.intake_decision == "ROUTE"
    assert result.route == "route_read_only_or_external_executor_handoff"
    assert result.retain_record is True


def test_intake_quarantines_quarantined_packet():
    packet = base_session_packet()
    packet["adapter_result"]["decision"] = "QUARANTINE"
    packet["authority_decision"] = {"decision": "FAIL_CLOSED", "authority_decision_hash": "authority-hash"}

    result = intake_governed_llm_session_packet(packet)

    assert result.intake_decision == "QUARANTINE"
    assert result.route == "quarantine_before_consequence"


def test_intake_rejects_malformed_packet():
    packet = base_session_packet()
    del packet["provider_response"]

    result = intake_governed_llm_session_packet(packet)

    assert result.intake_decision == "REJECT"
    assert result.route == "reject_malformed_packet"
    assert result.validation_decision == "ERROR"


def test_intake_fails_closed_unresolved_execution_readiness():
    packet = base_session_packet()
    packet["authority_decision"] = {"decision": "FAIL_CLOSED", "authority_decision_hash": "authority-hash"}
    packet["execution_handoff"] = {"status": "ready_for_external_executor", "execution_handoff_hash": "handoff-hash"}

    result = intake_governed_llm_session_packet(packet)

    assert result.intake_decision == "FAIL_CLOSED"
    assert result.route == "fail_closed_unresolved_session"
