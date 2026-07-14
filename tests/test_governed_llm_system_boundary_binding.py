from copy import deepcopy

import pytest

from stegverse import build_governed_llm_manifest, build_governed_llm_receipt_handoff


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


def system_boundary_declaration():
    return {
        "schema_version": "0.1",
        "declaration_id": "sbd-adapter-manifest-001",
        "system_id": "stegverse-llm-adapter",
        "generated_at": "2026-07-14T12:00:00Z",
        "surfaces": {
            "model": {"present": True, "state_kind": "transient", "persistence": "invocation", "mutable_by_inference": False, "storage_refs": []},
            "orchestration": {"present": True, "state_kind": "session", "persistence": "session", "mutable_by_inference": True, "storage_refs": ["orchestrator/session-state"]},
            "session": {"present": True, "state_kind": "session", "persistence": "session", "mutable_by_inference": True, "storage_refs": ["session/continuity-packet"]},
            "memory": {"present": True, "state_kind": "durable", "persistence": "cross-session", "mutable_by_inference": False, "storage_refs": ["memory/governed-record-store"]},
            "environment": {"present": True, "state_kind": "external", "persistence": "indefinite", "mutable_by_inference": False, "storage_refs": ["environment/tool-observation-receipts"]},
        },
        "continuity": {
            "prior_state_can_affect_future_transition": True,
            "feedback_paths": ["model-output->orchestrator-state", "orchestrator-state->future-model-input"],
            "trajectory_dependent": True,
            "reconstructable": True,
            "evidence_refs": ["receipt://adapter/001"],
        },
        "authority": {
            "model_has_execution_authority": False,
            "commit_boundary": "governed-transition/commitment-request",
            "decision_source": "policy-engine",
            "policy_refs": ["policy://governed-llm/default"],
            "delegation_refs": [],
        },
        "claims_boundary": {
            "consciousness_claim": "not_evaluated",
            "personhood_claim": "not_evaluated",
            "welfare_claim": "not_evaluated",
            "scope_note": "Operational state and authority boundaries only.",
        },
    }


def test_manifest_and_receipt_preserve_adapter_reference():
    packet = base_session_packet()
    packet["system_boundary_declaration"] = system_boundary_declaration()

    first_manifest = build_governed_llm_manifest(packet)
    packet["system_boundary_declaration_ref"] = first_manifest["system_boundary_declaration_ref"]
    manifest = build_governed_llm_manifest(packet)
    receipt = build_governed_llm_receipt_handoff(packet)

    reference = manifest["system_boundary_declaration_ref"]
    assert reference["algorithm"] == "sha256"
    assert reference["digest"]
    assert reference["declaration_id"] == "sbd-adapter-manifest-001"
    assert reference["authorizing"] is False
    assert reference["custody_transferred"] is False
    assert reference["admissibility_determined"] is False
    assert receipt["system_boundary_declaration_ref"] == reference
    assert receipt["manifest"]["system_boundary_declaration_ref"] == reference


def test_legacy_packet_remains_compatible_without_boundary_fields():
    manifest = build_governed_llm_manifest(base_session_packet())
    receipt = build_governed_llm_receipt_handoff(base_session_packet())

    assert "system_boundary_declaration" not in manifest
    assert "system_boundary_declaration_ref" not in manifest
    assert "system_boundary_declaration_ref" not in receipt


def test_rejects_reference_without_declaration():
    packet = base_session_packet()
    packet["system_boundary_declaration_ref"] = {"declaration_id": "orphan"}

    with pytest.raises(ValueError, match="cannot be supplied without"):
        build_governed_llm_manifest(packet)


def test_rejects_reference_digest_drift():
    packet = base_session_packet()
    packet["system_boundary_declaration"] = system_boundary_declaration()
    reference = build_governed_llm_manifest(packet)["system_boundary_declaration_ref"]
    bad_ref = deepcopy(reference)
    bad_ref["digest"] = "0" * 64
    packet["system_boundary_declaration_ref"] = bad_ref

    with pytest.raises(ValueError, match="does not match declaration"):
        build_governed_llm_manifest(packet)


def test_rejects_model_authority_escalation_before_manifest_binding():
    packet = base_session_packet()
    declaration = system_boundary_declaration()
    declaration["authority"]["model_has_execution_authority"] = True
    packet["system_boundary_declaration"] = declaration

    with pytest.raises(ValueError, match="model execution authority must be false"):
        build_governed_llm_manifest(packet)
