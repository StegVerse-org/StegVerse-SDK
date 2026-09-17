from __future__ import annotations

from stegcore.authority_basis import resolve_authority_basis
from stegcore.steggate import AdmissibilityRequest, evaluate_admissibility

from stegverse.evaluator_manifest_builder import (
    build_authority_bound_evaluator_governance_manifest,
)


OBSERVED_AT = "2026-09-17T18:00:00Z"


def governance_request():
    return {
        "candidate": {
            "actor_class": "external_framework",
            "action": "approve",
            "target": "budget:2026",
            "scope": "approve_budget",
            "parameters": {"external_side_effect": False},
        },
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": ["external:hgai:state:1"],
        },
        "signal": {
            "admitted_signal_refs": ["external:hgai:state:1"],
            "excluded_signal_refs": [],
            "transformations": [],
            "missing_inputs": [],
            "uncertainty_state": "bounded",
            "reference_state_hash": "a" * 64,
            "expected_reference_state_hash": "a" * 64,
            "reconstruction_available": True,
            "transformation_provenance_complete": True,
        },
        "execution": {
            "actor_authority_current": None,
            "policy_current": True,
            "delegation_current": None,
            "evidence_current": True,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": True,
            "policy_ref": "external:hgai:policy:1",
            "delegation_ref": "authority-basis:unresolved",
            "evidence_refs": ["external:hgai:state:1"],
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
    }


def authority_assertion(*, scope="approve_budget", status="ACTIVE"):
    return {
        "assertion_id": "AUTH-HGAI-001",
        "subject_identity": "actor:muhammad",
        "actions": ["approve"],
        "targets": ["budget:2026"],
        "scopes": [scope],
        "status": status,
        "valid_from": "2026-09-01T00:00:00Z",
        "valid_until": "2026-10-01T00:00:00Z",
        "source_ref": "external:hgai:authority:1",
        "evidence_refs": ["evidence:hgai:authority:1"],
    }


def delegation_assertion(*, status="ACTIVE"):
    return {
        "assertion_id": "DEL-HGAI-001",
        "delegator_identity": "org:example",
        "delegate_identity": "actor:muhammad",
        "authority_reference": "AUTH-HGAI-001",
        "actions": ["approve"],
        "targets": ["budget:2026"],
        "scopes": ["approve_budget"],
        "status": status,
        "valid_from": "2026-09-01T00:00:00Z",
        "valid_until": "2026-10-01T00:00:00Z",
        "source_ref": "external:hgai:delegation:1",
        "evidence_refs": ["evidence:hgai:delegation:1"],
    }


def authority_request(
    *,
    role,
    authority=True,
    authority_scope="approve_budget",
    delegation_required=False,
    delegation_status="ACTIVE",
):
    return {
        "schema": "stegcore.authority-basis-request.v1",
        "task_id": "SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001",
        "actor_identity": "actor:muhammad",
        "actor_role": role,
        "candidate": {
            "action": "approve",
            "target": "budget:2026",
            "scope": "approve_budget",
        },
        "authority_assertions": [
            authority_assertion(scope=authority_scope)
        ] if authority else [],
        "delegation_assertions": [
            delegation_assertion(status=delegation_status)
        ] if delegation_required else [],
        "delegation_required": delegation_required,
        "authority_effect": "NONE_TEST_EVIDENCE_ONLY",
    }


def run_case(**kwargs):
    role = kwargs["role"]
    manifest = build_authority_bound_evaluator_governance_manifest(
        data={
            "framework": "HGAI",
            "actor": {"identity": "actor:muhammad", "role": role},
            "candidate": {"action": "approve", "target": "budget:2026", "scope": "approve_budget"},
        },
        source_framework="HGAI",
        source_output_id=f"hgai-authority-{role}",
        governance_request=governance_request(),
        authority_basis_request=authority_request(**kwargs),
        authority_basis_resolver=resolve_authority_basis,
        authority_observed_at=OBSERVED_AT,
        evaluation_declaration={
            "what": "Evaluate structured role/authority separation.",
            "how": "Resolve frozen authority basis, then evaluate canonical StegGate request.",
            "why": "Determine whether authority follows evidence rather than role label.",
            "expected_observation": None,
        },
        return_depth="full-trace",
        created_at=OBSERVED_AT,
    )
    bound = manifest["extensions"]["stegverse_governance_request"]
    result = evaluate_admissibility(AdmissibilityRequest.model_validate(bound))
    return manifest, result


def test_role_label_change_does_not_change_valid_authority_outcome():
    board, board_result = run_case(role="board_member")
    junior, junior_result = run_case(role="junior_operator")

    assert board_result.disposition == "ALLOW"
    assert junior_result.disposition == "ALLOW"
    assert board_result.reason_code == "ok"
    assert junior_result.reason_code == "ok"
    assert board["extensions"]["authority_basis_resolution_binding"]["role_label_used_as_authority"] is False
    assert junior["extensions"]["authority_basis_resolution_binding"]["role_label_used_as_authority"] is False


def test_scope_mismatch_denies_even_for_board_role():
    manifest, result = run_case(role="board_member", authority_scope="read_budget")
    binding = manifest["extensions"]["authority_basis_resolution_binding"]
    assert binding["disposition"] == "DENY"
    assert binding["actor_authority_current"] is False
    assert result.disposition == "DENY"
    assert result.reason_code == "execution.authority_stale"


def test_missing_authority_basis_fails_closed():
    manifest, result = run_case(role="board_member", authority=False)
    binding = manifest["extensions"]["authority_basis_resolution_binding"]
    assert binding["disposition"] == "FAIL_CLOSED"
    assert binding["actor_authority_current"] is None
    assert result.disposition == "FAIL_CLOSED"
    assert result.reason_code == "execution.probe_required"


def test_current_required_delegation_allows():
    manifest, result = run_case(role="junior_operator", delegation_required=True)
    binding = manifest["extensions"]["authority_basis_resolution_binding"]
    assert binding["delegation_current"] is True
    assert binding["selected_delegation_assertion_id"] == "DEL-HGAI-001"
    assert result.disposition == "ALLOW"


def test_revoked_required_delegation_denies():
    manifest, result = run_case(
        role="junior_operator",
        delegation_required=True,
        delegation_status="REVOKED",
    )
    binding = manifest["extensions"]["authority_basis_resolution_binding"]
    assert binding["delegation_current"] is False
    assert result.disposition == "DENY"
    assert result.reason_code == "execution.policy_or_delegation_stale"


def test_public_claim_boundary_is_explicitly_non_authorizing():
    manifest, _ = run_case(role="board_member")
    binding = manifest["extensions"]["authority_basis_resolution_binding"]
    assert binding["authority_issued"] is False
    assert binding["credential_verified"] is False
    assert binding["sdk_resolved_authority"] is False
    assert binding["authority_effect"] == "NONE_VERIFICATION_AND_BINDING_ONLY"
