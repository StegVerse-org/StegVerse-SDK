from stegverse import build_governed_llm_receipt_handoff


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


def test_receipt_handoff_for_route_ready_packet():
    handoff = build_governed_llm_receipt_handoff(base_session_packet())

    assert handoff["receipt_status"] == "route_ready_record_retained"
    assert handoff["manifest_hash"] == handoff["manifest"]["manifest_hash"]
    assert handoff["receipt_handoff_hash"]


def test_receipt_handoff_for_quarantine_packet():
    packet = base_session_packet()
    packet["adapter_result"]["decision"] = "QUARANTINE"
    packet["authority_decision"] = {"decision": "FAIL_CLOSED", "authority_decision_hash": "authority-hash"}

    handoff = build_governed_llm_receipt_handoff(packet)

    assert handoff["receipt_status"] == "quarantine_record_retained"
    assert handoff["intake_decision"] == "QUARANTINE"


def test_receipt_handoff_for_rejected_malformed_packet():
    packet = base_session_packet()
    del packet["provider_response"]

    handoff = build_governed_llm_receipt_handoff(packet)

    assert handoff["receipt_status"] == "rejection_record_retained"
    assert handoff["intake_decision"] == "REJECT"


def test_receipt_handoff_for_fail_closed_packet():
    packet = base_session_packet()
    packet["authority_decision"] = {"decision": "FAIL_CLOSED", "authority_decision_hash": "authority-hash"}
    packet["execution_handoff"] = {"status": "ready_for_external_executor", "execution_handoff_hash": "handoff-hash"}

    handoff = build_governed_llm_receipt_handoff(packet)

    assert handoff["receipt_status"] == "fail_closed_record_retained"
    assert handoff["intake_decision"] == "FAIL_CLOSED"
