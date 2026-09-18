from __future__ import annotations

from copy import deepcopy

import pytest

from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.governance_reference_graph import (
    GovernanceReferenceGraphError,
    build_governance_reference_graph,
    governance_reference_graph_sha256,
    validate_governance_reference_graph,
)
from stegverse.manifest_contract import validate_ingress_manifest


def graph_fixture():
    return build_governance_reference_graph(
        graph_id="external-framework-governance-001",
        nodes=[
            {"node_id": "actor:operator", "class": "human", "ref": "external:operator"},
            {"node_id": "role:reviewer", "class": "role", "ref": "external:role:reviewer"},
            {"node_id": "role:decision-authority", "class": "role", "ref": "external:role:decision-authority"},
            {"node_id": "system:agent", "class": "ai", "ref": "external:agent"},
            {"node_id": "evidence:case", "class": "dataset", "ref": "external:evidence:case"},
            {"node_id": "constraint:quorum", "class": "constraint", "ref": "stegcore:policy-shape:quorum"},
        ],
        relations=[
            {
                "relation_id": "rel-membership",
                "subject": "actor:operator",
                "relation": "MEMBER_OF",
                "object": "role:reviewer",
                "applicability": {"scopes": ["case:123"]},
                "constraint_ref": None,
                "source_ref": "external:org-chart:v1",
                "evidence_refs": ["evidence:org-chart:v1"],
                "basis_refs": [],
            },
            {
                "relation_id": "rel-escalation",
                "subject": "role:reviewer",
                "relation": "ESCALATES_TO",
                "object": "role:decision-authority",
                "applicability": {"actions": ["approve"], "scopes": ["case:123"]},
                "constraint_ref": None,
                "source_ref": "external:governance:v1",
                "evidence_refs": ["evidence:governance:v1"],
                "basis_refs": ["rel-membership"],
            },
            {
                "relation_id": "rel-supervision",
                "subject": "system:agent",
                "relation": "SUPERVISED_BY",
                "object": "role:reviewer",
                "applicability": {"scopes": ["case:123"]},
                "constraint_ref": None,
                "source_ref": "external:governance:v1",
                "evidence_refs": ["evidence:governance:v1"],
                "basis_refs": [],
            },
            {
                "relation_id": "rel-provenance",
                "subject": "system:agent",
                "relation": "DERIVED_FROM",
                "object": "evidence:case",
                "applicability": {"scopes": ["case:123"]},
                "constraint_ref": None,
                "source_ref": "external:provenance:v1",
                "evidence_refs": ["evidence:case:hash"],
                "basis_refs": [],
            },
            {
                "relation_id": "rel-quorum",
                "subject": "role:decision-authority",
                "relation": "REQUIRES_CONSTRAINT",
                "object": "constraint:quorum",
                "applicability": {"actions": ["approve"], "targets": ["case:123"], "scopes": ["case:123"]},
                "constraint_ref": "stegcore:policy-shape:quorum",
                "source_ref": "external:governance:v1",
                "evidence_refs": ["evidence:quorum:v1"],
                "basis_refs": [],
            },
            {
                "relation_id": "rel-domain-context",
                "subject": "actor:operator",
                "relation": "EXTERNAL_FRAMEWORK_CONTEXT_LINK",
                "object": "system:agent",
                "applicability": {"scopes": ["case:123"]},
                "constraint_ref": None,
                "source_ref": "external:framework:v1",
                "evidence_refs": ["evidence:framework:v1"],
                "basis_refs": [],
                "attributes": {"meaning_owned_by": "external_framework"},
            },
        ],
        coverage=[
            {
                "coverage_id": "coverage-authority-operator",
                "relation": "HAS_SCOPED_AUTHORITY",
                "subject": "actor:operator",
                "object": None,
                "selector": {"actions": ["approve"], "targets": ["case:123"], "scopes": ["case:123"]},
                "complete": False,
                "source_ref": "external:authority-register:v1",
                "evidence_refs": ["evidence:authority-register:v1"],
            }
        ],
        source_refs=["external:governance:v1", "external:org-chart:v1"],
        metadata={"projection": "generic-test-fixture"},
    )


def governance_request():
    return {
        "candidate": {
            "actor_class": "external_framework",
            "action": "approve",
            "target": "case:123",
            "scope": "case:123",
            "parameters": {"external_side_effect": False},
        },
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": ["external:test:1"],
        },
        "signal": {
            "admitted_signal_refs": ["external:test:1"],
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
            "policy_ref": "external:test-policy",
            "delegation_ref": None,
            "evidence_refs": ["external:test:1"],
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
    }


def test_generic_graph_is_hash_bound_and_non_authorizing():
    graph = graph_fixture()
    assert graph["graph_sha256"] == governance_reference_graph_sha256(graph)
    assert graph["authority_boundary"] == {
        "graph_representation_grants_authority": False,
        "hierarchy_grants_authority": False,
        "composition_grants_authority": False,
        "sdk_resolves_governance": False,
        "unknown_relations_grant_authority": False,
    }


def test_unknown_relation_is_preserved_without_becoming_authority():
    graph = validate_governance_reference_graph(graph_fixture())
    relation = next(item for item in graph["relations"] if item["relation_id"] == "rel-domain-context")
    assert relation["relation"] == "EXTERNAL_FRAMEWORK_CONTEXT_LINK"
    assert graph["authority_boundary"]["unknown_relations_grant_authority"] is False


def test_graph_endpoint_must_reference_declared_node():
    graph = graph_fixture()
    graph["relations"][0]["object"] = "role:missing"
    graph["graph_sha256"] = governance_reference_graph_sha256(graph)
    with pytest.raises(GovernanceReferenceGraphError, match="declared node_id"):
        validate_governance_reference_graph(graph)


def test_graph_tamper_breaks_hash_binding():
    graph = graph_fixture()
    graph["relations"][0]["relation"] = "REPORTS_TO"
    with pytest.raises(GovernanceReferenceGraphError, match="graph_sha256"):
        validate_governance_reference_graph(graph)


def test_coverage_requires_explicit_completeness():
    graph = graph_fixture()
    del graph["coverage"][0]["complete"]
    graph["graph_sha256"] = governance_reference_graph_sha256(graph)
    with pytest.raises(GovernanceReferenceGraphError, match="complete must be boolean"):
        validate_governance_reference_graph(graph)


def test_evaluator_manifest_preserves_graph_without_resolving_it():
    graph = graph_fixture()
    request = governance_request()
    manifest = build_evaluator_governance_manifest(
        data={"framework": "external", "observation": "fixture"},
        source_framework="EXTERNAL_FRAMEWORK",
        source_output_id="graph-fixture-001",
        governance_request=request,
        governance_reference_graph=graph,
        created_at="2026-09-18T05:00:00Z",
    )
    assert manifest["extensions"]["governance_reference_graph"] == graph
    assert manifest["extensions"]["stegverse_governance_request"] == request
    assert manifest["extensions"]["stegverse_governance_request"]["execution"]["actor_authority_current"] is None
    assert manifest["extensions"]["stegverse_governance_request"]["execution"]["delegation_current"] is None
    canonical = validate_ingress_manifest(manifest)
    assert canonical["external_manifest_grants_authority"] is False


def test_graph_change_changes_canonical_manifest_binding():
    first_graph = graph_fixture()
    first = build_evaluator_governance_manifest(
        data={"value": 1},
        source_framework="EXTERNAL_FRAMEWORK",
        source_output_id="graph-fixture-a",
        governance_request=governance_request(),
        governance_reference_graph=first_graph,
        created_at="2026-09-18T05:00:00Z",
    )
    second_graph = deepcopy(first_graph)
    second_graph["metadata"]["revision_note"] = "changed"
    second_graph["graph_sha256"] = governance_reference_graph_sha256(second_graph)
    second = build_evaluator_governance_manifest(
        data={"value": 1},
        source_framework="EXTERNAL_FRAMEWORK",
        source_output_id="graph-fixture-a",
        governance_request=governance_request(),
        governance_reference_graph=second_graph,
        created_at="2026-09-18T05:00:00Z",
    )
    assert validate_ingress_manifest(first)["canonical_manifest_sha256"] != validate_ingress_manifest(second)["canonical_manifest_sha256"]
