from copy import deepcopy
from hashlib import sha256
import json

from stegverse.system_boundary_round_trip import validate_system_boundary_round_trip


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sample_declaration():
    declaration = {
        "schema_version": "0.1",
        "declaration_id": "pending",
        "system_id": "stegverse-llm-adapter",
        "generated_at": "2026-07-14T12:00:00Z",
        "surfaces": {
            "model": {"present": True, "state_kind": "transient", "persistence": "invocation", "mutable_by_inference": False, "storage_refs": []},
            "orchestration": {"present": True, "state_kind": "session", "persistence": "session", "mutable_by_inference": True, "storage_refs": ["session://session-001"]},
            "session": {"present": True, "state_kind": "session", "persistence": "session", "mutable_by_inference": True, "storage_refs": ["session://session-001"]},
            "memory": {"present": True, "state_kind": "durable", "persistence": "cross-session", "mutable_by_inference": False, "storage_refs": ["memory://governed-record-store"]},
            "environment": {"present": True, "state_kind": "external", "persistence": "indefinite", "mutable_by_inference": False, "storage_refs": ["environment://tool-observation-receipts"]},
        },
        "continuity": {
            "prior_state_can_affect_future_transition": True,
            "feedback_paths": [
                "model-output->orchestration-state",
                "orchestration-state->future-model-input",
                "environment-observation->session-continuity",
            ],
            "trajectory_dependent": True,
            "reconstructable": True,
            "evidence_refs": [
                "transition://transition-001",
                "run://run-001",
                "final-receipt:001",
                "gateway-receipt:001",
            ],
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
            "scope_note": "This declaration describes operational state and authority boundaries only.",
        },
    }
    identity_keys = {
        "schema_version", "system_id", "surfaces", "continuity", "authority", "claims_boundary"
    }
    content = {key: declaration[key] for key in sorted(identity_keys)}
    declaration["declaration_id"] = "sbd:sha256:" + sha256(canonical_json(content).encode("utf-8")).hexdigest()
    return declaration


def sample_tuple():
    declaration = sample_declaration()
    identity_keys = {
        "schema_version", "system_id", "surfaces", "continuity", "authority", "claims_boundary"
    }
    content = {key: declaration[key] for key in sorted(identity_keys)}
    declaration_hash = "sha256:" + sha256(canonical_json(content).encode("utf-8")).hexdigest()
    body = {
        "schema_version": "system_boundary_declaration_receipt.v1",
        "declaration_id": declaration["declaration_id"],
        "declaration_hash": declaration_hash,
        "system_id": declaration["system_id"],
        "evidence_refs": list(declaration["continuity"]["evidence_refs"]),
        "source_commit": "4bf4027df724fd5fd8be128009cef31d8b036396",
        "previous_receipt_hash": None,
        "authority_boundary": {
            "receipt_is_execution_authority": False,
            "receipt_is_admissibility": False,
            "receipt_is_custody": False,
            "declaration_proves_consciousness": False,
        },
    }
    receipt = {
        **body,
        "receipt_hash": "sha256:" + sha256(canonical_json(body).encode("utf-8")).hexdigest(),
    }
    reference = {
        "algorithm": "sha256",
        "digest": declaration_hash.removeprefix("sha256:"),
        "declaration_id": declaration["declaration_id"],
        "receipt_hash": receipt["receipt_hash"],
        "authorizing": False,
        "custody_transferred": False,
        "admissibility_determined": False,
        "production_binding_enabled": False,
    }
    return declaration, receipt, reference


def test_accepts_adapter_declaration_receipt_reference_round_trip():
    declaration, receipt, reference = sample_tuple()
    result = validate_system_boundary_round_trip(declaration, receipt, reference)

    assert result.accepted is True
    assert result.status == "accepted_for_non_authorizing_receipt_handoff"
    assert result.declaration_id == declaration["declaration_id"]
    assert result.receipt_hash == receipt["receipt_hash"]
    assert result.non_claims["sdk_round_trip_is_execution_authority"] is False
    assert result.non_claims["production_binding_enabled"] is False


def test_identical_replay_produces_identical_sdk_result():
    declaration, receipt, reference = sample_tuple()
    first = validate_system_boundary_round_trip(declaration, receipt, reference).to_dict()
    second = validate_system_boundary_round_trip(declaration, receipt, reference).to_dict()
    assert first == second


def test_rejects_declaration_tamper_and_digest_drift():
    declaration, receipt, reference = sample_tuple()
    tampered = deepcopy(declaration)
    tampered["continuity"]["feedback_paths"].append("unreceipted-path")

    result = validate_system_boundary_round_trip(tampered, receipt, reference)
    assert result.accepted is False
    assert "declaration_id does not match canonical content" in result.errors


def test_rejects_receipt_reconstruction_mismatch():
    declaration, receipt, reference = sample_tuple()
    receipt["source_commit"] = "different-commit"

    result = validate_system_boundary_round_trip(declaration, receipt, reference)
    assert result.accepted is False
    assert "system-boundary receipt reconstruction mismatch" in result.errors


def test_rejects_reference_authority_or_production_escalation():
    declaration, receipt, reference = sample_tuple()
    reference["authorizing"] = True
    reference["production_binding_enabled"] = True

    result = validate_system_boundary_round_trip(declaration, receipt, reference)
    assert result.accepted is False
    assert "system_boundary_declaration_ref.authorizing must be false" in result.errors
    assert "system_boundary_declaration_ref.production_binding_enabled must be false" in result.errors


def test_rejects_consciousness_reclassification():
    declaration, receipt, reference = sample_tuple()
    declaration["claims_boundary"]["consciousness_claim"] = "confirmed"

    result = validate_system_boundary_round_trip(declaration, receipt, reference)
    assert result.accepted is False
    assert "consciousness_claim must remain not_evaluated" in result.errors
