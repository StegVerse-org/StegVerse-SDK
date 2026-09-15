from __future__ import annotations

import json

import pytest

from stegverse.manifest_builder import build_manifest
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.publisher_return_binding import assemble_publisher_return


def governance_request():
    return {
        "candidate": {"actor_class": "external_framework", "action": "test", "target": "mirror", "scope": "test", "parameters": {"external_side_effect": False}},
        "judgment": {"refusal_available": True, "operator_recoverability": "available", "workload_state": "supported", "time_pressure": "normal", "isolation_state": "supported", "evidence_refs": ["test:1"]},
        "signal": {"admitted_signal_refs": ["test:1"], "excluded_signal_refs": [], "transformations": [], "missing_inputs": [], "uncertainty_state": "bounded", "reference_state_hash": "a" * 64, "expected_reference_state_hash": "a" * 64, "reconstruction_available": True, "transformation_provenance_complete": True},
        "execution": {"actor_authority_current": True, "policy_current": True, "delegation_current": True, "evidence_current": True, "affected_entity_conditions_represented": True, "recoverability_profile": "recoverable", "validity_window_open": True, "policy_ref": "test:policy", "delegation_ref": "test:delegation", "evidence_refs": ["test:1"]},
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
    }


def publisher_return_bytes() -> bytes:
    value = {
        "schema": "stegverse.publisher.artifact-return/v1",
        "authority_effect": "NONE",
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "transfer_id": "transfer-001",
        "source_export_id": "export-001",
        "source_export_sha256": "sha256:" + "b" * 64,
        "generation_id": "generation-001",
        "manifest": {"artifacts": []},
        "artifacts": [],
    }
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def test_destination_profile_survives_manifest_validation_and_sdk_return_binding():
    manifest = build_manifest(
        data={"signal": "mirror-test"},
        source_framework="MIR_TEST",
        source_output_id="mirror-signal-001",
        processor_request=governance_request(),
        publisher_required=True,
        destination_profile="MIR",
        created_at="2026-09-14T20:46:00Z",
    )
    canonical = validate_ingress_manifest(manifest)
    assert canonical["completion"]["egress"]["destination_profile"] == "MIR"

    binding = assemble_publisher_return(
        manifest=manifest,
        manifest_receipt_id="MR-ABC123",
        publisher_return_bytes=publisher_return_bytes(),
    )
    assert binding["egress"]["destination_profile"] == "MIR"
    assert binding["communication_state"] == "READY_FOR_FINAL_STEGVERSE_EGRESS_TRANSITION"
    assert binding["interlock_intr_egress_observed"] is False
    assert binding["far_side_transition_observed"] is False


def test_destination_profile_rejects_empty_substitution():
    manifest = build_manifest(
        data={"signal": "mirror-test"},
        source_framework="MIR_TEST",
        source_output_id="mirror-signal-002",
        processor_request=governance_request(),
        publisher_required=True,
        destination_profile="MIR",
        created_at="2026-09-14T20:46:00Z",
    )
    manifest["completion"]["egress"]["destination_profile"] = "   "
    with pytest.raises(ValueError, match="destination_profile"):
        validate_ingress_manifest(manifest)
