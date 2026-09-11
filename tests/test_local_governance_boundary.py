from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.local_governance_boundary import prepare_local_governance_boundary
from tests.test_intr_posture_runtime_bridge import fake_intr_resolver


def test_local_boundary_requires_no_governance_runtime_packages():
    governance_request = {
        "candidate": {"actor_class": "external_framework", "action": "evaluate", "target": "source_native_manifest", "scope": "local-test", "parameters": {"external_side_effect": False}},
        "judgment": {"refusal_available": True, "operator_recoverability": "available", "workload_state": "supported", "time_pressure": "normal", "isolation_state": "supported", "evidence_refs": ["local:test"]},
        "signal": {"admitted_signal_refs": ["local:test"], "excluded_signal_refs": [], "transformations": [], "missing_inputs": [], "uncertainty_state": "bounded", "reference_state_hash": "a" * 64, "expected_reference_state_hash": "a" * 64, "reconstruction_available": True, "transformation_provenance_complete": True},
        "execution": {"actor_authority_current": True, "policy_current": True, "delegation_current": True, "evidence_current": True, "affected_entity_conditions_represented": True, "recoverability_profile": "recoverable", "validity_window_open": True, "policy_ref": "local-test", "delegation_ref": "local-test", "evidence_refs": ["local:test"]},
        "capability": {"allowed": True}, "continuity": {"required": False}, "approval": {"required": False}, "permission_present": True,
    }
    posture_request = {
        "schema": "stegverse.sdk.security-posture-request.v1",
        "task_id": "SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001",
        "selected_tier": None,
        "selection_present": False,
        "organization_minimum_tier": "SECURE",
        "data_class": "elan.relational-state.v1",
        "channel": "SDK_LOCAL_TEST",
        "authority_effect": "NONE_REQUEST_INPUT_ONLY",
    }
    manifest = build_evaluator_governance_manifest(
        data={"event": "local-test"},
        source_framework="LOCAL_SDK_TEST",
        source_output_id="local-sdk-boundary-001",
        governance_request=governance_request,
        evaluation_declaration={"what": "prove boundary", "how": "local sdk", "why": "establish contract", "expected_observation": None},
        security_posture_request=posture_request,
        return_depth="full-trace",
        data_class="elan.relational-state.v1",
        created_at="2026-09-10T23:00:00Z",
    )
    artifact = prepare_local_governance_boundary(
        manifest,
        intr_posture_resolver=fake_intr_resolver,
        observed_at="2026-09-10T23:00:00Z",
    )
    assert artifact["boundary_state"] == "READY_FOR_GOVERNANCE_CONSUMPTION"
    assert artifact["exact_request_preserved"] is True
    assert artifact["governance_execution_performed"] is False
    assert artifact["governance_result_claimed"] is False
    assert artifact["external_package_materialization_required"] is False
    assert artifact["third_party_evaluator_execution"] is False
    assert artifact["authority_effect"] == "NONE"
    assert artifact["intr_security_posture_binding"]["binding_verified"] is True
