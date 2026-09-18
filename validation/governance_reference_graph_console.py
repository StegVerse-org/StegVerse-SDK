from __future__ import annotations

import json

from stegverse import build_governance_reference_graph
from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.manifest_contract import validate_ingress_manifest


def main() -> int:
    graph = build_governance_reference_graph(
        graph_id="external-hitl-projection-001",
        nodes=[
            {"node_id": "agent:analysis", "class": "ai", "ref": "external:agent:analysis"},
            {"node_id": "human:reviewer", "class": "human", "ref": "external:human:reviewer"},
            {"node_id": "human:decision-authority", "class": "human", "ref": "external:human:decision-authority"},
            {"node_id": "evidence:case", "class": "dataset", "ref": "external:evidence:case"},
            {"node_id": "constraint:quorum", "class": "constraint", "ref": "stegcore:policy-shape:quorum"},
        ],
        relations=[
            {
                "relation_id": "r-supervision",
                "subject": "agent:analysis",
                "relation": "SUPERVISED_BY",
                "object": "human:reviewer",
                "applicability": {"actions": ["recommend"], "targets": ["case:42"], "scopes": ["case:42"]},
                "constraint_ref": None,
                "source_ref": "external:framework-governance:v1",
                "evidence_refs": ["external:evidence:supervision"],
                "basis_refs": [],
            },
            {
                "relation_id": "r-escalation",
                "subject": "human:reviewer",
                "relation": "ESCALATES_TO",
                "object": "human:decision-authority",
                "applicability": {"actions": ["approve"], "targets": ["case:42"], "scopes": ["case:42"]},
                "constraint_ref": None,
                "source_ref": "external:framework-governance:v1",
                "evidence_refs": ["external:evidence:escalation"],
                "basis_refs": ["r-supervision"],
            },
            {
                "relation_id": "r-provenance",
                "subject": "agent:analysis",
                "relation": "DERIVED_FROM",
                "object": "evidence:case",
                "applicability": {"scopes": ["case:42"]},
                "constraint_ref": None,
                "source_ref": "external:framework-provenance:v1",
                "evidence_refs": ["external:evidence:case"],
                "basis_refs": [],
            },
            {
                "relation_id": "r-quorum",
                "subject": "human:decision-authority",
                "relation": "REQUIRES_CONSTRAINT",
                "object": "constraint:quorum",
                "applicability": {"actions": ["approve"], "targets": ["case:42"], "scopes": ["case:42"]},
                "constraint_ref": "stegcore:policy-shape:quorum",
                "source_ref": "external:framework-governance:v1",
                "evidence_refs": ["external:evidence:quorum"],
                "basis_refs": [],
            },
            {
                "relation_id": "r-external-context",
                "subject": "agent:analysis",
                "relation": "EXTERNAL_FRAMEWORK_CONTEXT_LINK",
                "object": "human:reviewer",
                "applicability": {"scopes": ["case:42"]},
                "constraint_ref": None,
                "source_ref": "external:framework-native:v1",
                "evidence_refs": ["external:evidence:framework-native"],
                "basis_refs": [],
                "attributes": {"semantic_owner": "external_framework"},
            },
        ],
        coverage=[
            {
                "coverage_id": "c-authority",
                "relation": "HAS_SCOPED_AUTHORITY",
                "subject": "human:decision-authority",
                "object": None,
                "selector": {"actions": ["approve"], "targets": ["case:42"], "scopes": ["case:42"]},
                "complete": False,
                "source_ref": "external:authority-register:v1",
                "evidence_refs": ["external:evidence:authority-register"],
            }
        ],
        source_refs=[
            "external:framework-governance:v1",
            "external:framework-provenance:v1",
            "external:authority-register:v1",
        ],
        metadata={"example": "generic_hitl_projection", "framework_specific_semantics_preserved": True},
    )

    governance_request = {
        "candidate": {
            "actor_class": "external_framework",
            "action": "approve",
            "target": "case:42",
            "scope": "case:42",
            "parameters": {"external_side_effect": False},
        },
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": ["external:evidence:case"],
        },
        "signal": {
            "admitted_signal_refs": ["external:evidence:case"],
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
            "policy_ref": "external:policy:v1",
            "delegation_ref": None,
            "evidence_refs": ["external:evidence:case"],
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
    }

    manifest = build_evaluator_governance_manifest(
        data={"source_native": {"case": 42}},
        source_framework="EXTERNAL_FRAMEWORK",
        source_output_id="external-hitl-projection-001",
        governance_request=governance_request,
        governance_reference_graph=graph,
        created_at="2026-09-18T05:00:00Z",
    )
    canonical = validate_ingress_manifest(manifest)

    graph_out = manifest["extensions"]["governance_reference_graph"]
    request_out = manifest["extensions"]["stegverse_governance_request"]

    assert graph_out["graph_sha256"] == graph["graph_sha256"]
    assert graph_out["authority_boundary"]["hierarchy_grants_authority"] is False
    assert graph_out["authority_boundary"]["sdk_resolves_governance"] is False
    assert graph_out["authority_boundary"]["unknown_relations_grant_authority"] is False
    assert any(r["relation"] == "SUPERVISED_BY" for r in graph_out["relations"])
    assert any(r["relation"] == "ESCALATES_TO" for r in graph_out["relations"])
    assert any(r["relation"] == "DERIVED_FROM" for r in graph_out["relations"])
    assert any(r["constraint_ref"] == "stegcore:policy-shape:quorum" for r in graph_out["relations"])
    assert any(r["relation"] == "EXTERNAL_FRAMEWORK_CONTEXT_LINK" for r in graph_out["relations"])
    assert graph_out["coverage"][0]["complete"] is False
    assert request_out["execution"]["actor_authority_current"] is None
    assert request_out["execution"]["delegation_current"] is None
    assert canonical["external_manifest_grants_authority"] is False

    print(json.dumps({
        "status": "GOVERNANCE_REFERENCE_GRAPH_CONSOLE_PASS",
        "graph_schema": graph_out["schema"],
        "graph_sha256": graph_out["graph_sha256"],
        "canonical_manifest_sha256": canonical["canonical_manifest_sha256"],
        "node_classes": sorted({node["class"] for node in graph_out["nodes"]}),
        "relation_types": [item["relation"] for item in graph_out["relations"]],
        "coverage_complete": graph_out["coverage"][0]["complete"],
        "hierarchy_grants_authority": graph_out["authority_boundary"]["hierarchy_grants_authority"],
        "sdk_resolves_governance": graph_out["authority_boundary"]["sdk_resolves_governance"],
        "actor_authority_current": request_out["execution"]["actor_authority_current"],
        "delegation_current": request_out["execution"]["delegation_current"],
        "external_manifest_grants_authority": canonical["external_manifest_grants_authority"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
