from stegverse import build_governed_llm_manifest


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


def test_manifest_binds_allowed_session_packet():
    manifest = build_governed_llm_manifest(base_session_packet())

    assert manifest["manifest_type"] == "governed_llm_session"
    assert manifest["intake_decision"] == "ROUTE"
    assert manifest["route"] == "route_read_only_or_external_executor_handoff"
    assert manifest["manifest_hash"]
    assert manifest["intake"]["retain_record"] is True


def test_manifest_binds_quarantined_session_packet():
    packet = base_session_packet()
    packet["adapter_result"]["decision"] = "QUARANTINE"
    packet["authority_decision"] = {"decision": "FAIL_CLOSED", "authority_decision_hash": "authority-hash"}

    manifest = build_governed_llm_manifest(packet)

    assert manifest["intake_decision"] == "QUARANTINE"
    assert manifest["route"] == "quarantine_before_consequence"
    assert manifest["manifest_hash"]


def test_manifest_retains_malformed_session_packet_rejection():
    packet = base_session_packet()
    del packet["provider_response"]

    manifest = build_governed_llm_manifest(packet)

    assert manifest["intake_decision"] == "REJECT"
    assert manifest["route"] == "reject_malformed_packet"
    assert manifest["intake"]["validation_decision"] == "ERROR"
    assert manifest["retain_record"] is True
