from __future__ import annotations

import pytest

from stegverse.authority_basis_bridge import AuthorityBasisBridgeError
from stegverse.evaluator_manifest_builder import (
    build_authority_bound_evaluator_governance_manifest,
)


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
            "evidence_refs": ["external:hgai:1"],
        },
        "signal": {
            "admitted_signal_refs": ["external:hgai:1"],
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
            "policy_ref": "external:hgai:policy",
            "delegation_ref": None,
            "evidence_refs": ["external:hgai:1"],
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
    }


def authority_request(role="board_member"):
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
        "authority_assertions": [{"fixture": "canonical-resolver-validates"}],
        "delegation_assertions": [],
        "delegation_required": False,
        "authority_basis_complete": True,
        "delegation_basis_complete": True,
        "authority_effect": "NONE_TEST_EVIDENCE_ONLY",
    }


def resolver(request, *, observed_at):
    assert request["actor_role"] in {"board_member", "junior_operator"}
    return {
        "schema": "stegcore.authority-basis-resolution.v1",
        "task_id": request["task_id"],
        "observed_at": observed_at,
        "actor_identity": request["actor_identity"],
        "actor_role": request.get("actor_role"),
        "candidate": dict(request["candidate"]),
        "disposition": "ALLOW",
        "actor_authority_current": True,
        "delegation_current": True,
        "authority_basis_complete": request["authority_basis_complete"],
        "delegation_basis_complete": request["delegation_basis_complete"],
        "selected_authority_assertion_id": "AUTH-001",
        "selected_delegation_assertion_id": None,
        "evidence_refs": ["authority:evidence:1"],
        "role_label_used_as_authority": False,
        "role_policy_interpreted": False,
        "authority_issued": False,
        "credential_verified": False,
        "resolution_authority": "STEGCORE_TEST_AUTHORITY_BASIS",
        "authority_effect": "NONE_RESOLUTION_ONLY",
    }


def build(role="board_member"):
    source = governance_request()
    manifest = build_authority_bound_evaluator_governance_manifest(
        data={"framework": "HGAI", "role": role},
        source_framework="HGAI",
        source_output_id=f"hgai-{role}",
        governance_request=source,
        authority_basis_request=authority_request(role),
        authority_basis_resolver=resolver,
        authority_observed_at="2026-09-17T18:00:00Z",
        evaluation_declaration={
            "what": "compare structured authority basis",
            "how": "canonical resolver binding",
            "why": "test role/authority separation",
            "expected_observation": None,
        },
        created_at="2026-09-17T18:00:00Z",
    )
    return source, manifest


def test_role_label_is_preserved_but_not_used_as_authority():
    _, board = build("board_member")
    _, junior = build("junior_operator")

    for manifest in (board, junior):
        request = manifest["extensions"]["stegverse_governance_request"]
        binding = manifest["extensions"]["authority_basis_resolution_binding"]
        assert request["execution"]["actor_authority_current"] is True
        assert request["execution"]["delegation_current"] is True
        assert binding["role_label_used_as_authority"] is False
        assert binding["role_policy_interpreted"] is False
        assert binding["authority_issued"] is False
        assert binding["credential_verified"] is False
        assert binding["sdk_resolved_authority"] is False

    assert board["extensions"]["authority_basis_request"]["actor_role"] == "board_member"
    assert junior["extensions"]["authority_basis_request"]["actor_role"] == "junior_operator"


def test_source_request_is_not_mutated():
    source, manifest = build()
    assert source["execution"]["actor_authority_current"] is None
    assert source["execution"]["delegation_current"] is None
    derived = manifest["extensions"]["stegverse_governance_request"]
    assert derived["execution"]["actor_authority_current"] is True
    assert derived["execution"]["delegation_current"] is True
    assert "authority:evidence:1" in derived["execution"]["evidence_refs"]


def test_preasserted_currentness_is_rejected():
    source = governance_request()
    source["execution"]["actor_authority_current"] = True
    with pytest.raises(AuthorityBasisBridgeError, match="must be null/unestablished"):
        build_authority_bound_evaluator_governance_manifest(
            data={"value": 1},
            source_framework="HGAI",
            source_output_id="bad-preassertion",
            governance_request=source,
            authority_basis_request=authority_request(),
            authority_basis_resolver=resolver,
            authority_observed_at="2026-09-17T18:00:00Z",
        )


def test_candidate_mismatch_fails_before_resolver():
    request = authority_request()
    request["candidate"]["scope"] = "different_scope"
    with pytest.raises(AuthorityBasisBridgeError, match="candidate must match"):
        build_authority_bound_evaluator_governance_manifest(
            data={"value": 1},
            source_framework="HGAI",
            source_output_id="candidate-mismatch",
            governance_request=governance_request(),
            authority_basis_request=request,
            authority_basis_resolver=resolver,
            authority_observed_at="2026-09-17T18:00:00Z",
        )


def test_resolver_cannot_claim_role_as_authority():
    def bad_resolver(request, *, observed_at):
        result = resolver(request, observed_at=observed_at)
        result["role_label_used_as_authority"] = True
        return result

    with pytest.raises(AuthorityBasisBridgeError, match="role label"):
        build_authority_bound_evaluator_governance_manifest(
            data={"value": 1},
            source_framework="HGAI",
            source_output_id="role-smuggle",
            governance_request=governance_request(),
            authority_basis_request=authority_request(),
            authority_basis_resolver=bad_resolver,
            authority_observed_at="2026-09-17T18:00:00Z",
        )


def test_incomplete_basis_can_remain_unknown_fail_closed():
    request = authority_request()
    request["authority_basis_complete"] = False

    def unknown_resolver(value, *, observed_at):
        result = resolver(value, observed_at=observed_at)
        result["disposition"] = "FAIL_CLOSED"
        result["actor_authority_current"] = None
        result["authority_basis_complete"] = False
        return result

    manifest = build_authority_bound_evaluator_governance_manifest(
        data={"value": 1},
        source_framework="HGAI",
        source_output_id="incomplete-basis",
        governance_request=governance_request(),
        authority_basis_request=request,
        authority_basis_resolver=unknown_resolver,
        authority_observed_at="2026-09-17T18:00:00Z",
    )
    binding = manifest["extensions"]["authority_basis_resolution_binding"]
    assert binding["disposition"] == "FAIL_CLOSED"
    assert binding["actor_authority_current"] is None
    assert binding["authority_basis_complete"] is False
    assert manifest["extensions"]["stegverse_governance_request"]["execution"]["actor_authority_current"] is None


def test_resolver_cannot_change_basis_completeness():
    request = authority_request()

    def bad_resolver(value, *, observed_at):
        result = resolver(value, observed_at=observed_at)
        result["authority_basis_complete"] = False
        return result

    with pytest.raises(AuthorityBasisBridgeError, match="must match"):
        build_authority_bound_evaluator_governance_manifest(
            data={"value": 1},
            source_framework="HGAI",
            source_output_id="basis-completeness-mismatch",
            governance_request=governance_request(),
            authority_basis_request=request,
            authority_basis_resolver=bad_resolver,
            authority_observed_at="2026-09-17T18:00:00Z",
        )
