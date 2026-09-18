from __future__ import annotations

"""Generic, non-authorizing Governance Reference Graph support.

The graph is a representation/custody surface. It preserves typed nodes,
relationships, applicability, evidence, constraint references, and scoped
coverage/completeness declarations without deciding what any relationship grants.
Canonical governance meaning remains with downstream StegCore/StegGate and
transition authority remains with Interlock/InTr.
"""

import argparse
from copy import deepcopy
import json
from typing import Any, Mapping

from .governance_navigation import canonical_sha256

GRAPH_SCHEMA = "stegverse.governance-reference-graph.v1"
RELATION_PROFILE = "stegverse.governance-relations.v1"
EXTENSION_KEY = "governance_reference_graph"

AUTHORITY_BOUNDARY = {
    "graph_representation_grants_authority": False,
    "hierarchy_grants_authority": False,
    "composition_grants_authority": False,
    "sdk_resolves_governance": False,
    "unknown_relations_grant_authority": False,
}


class GovernanceReferenceGraphError(ValueError):
    pass


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GovernanceReferenceGraphError(f"{field} is required")
    return value.strip()


def _require_text_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise GovernanceReferenceGraphError(f"{field} must be an array of strings")
    return list(dict.fromkeys(item.strip() for item in value))


def _validate_selector(value: Any, field: str) -> None:
    if value is None:
        return
    if not isinstance(value, Mapping):
        raise GovernanceReferenceGraphError(f"{field} must be an object")
    allowed = {"actions", "targets", "scopes"}
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise GovernanceReferenceGraphError(f"unknown {field} fields: " + ", ".join(unknown))
    for key in allowed:
        if key in value:
            _require_text_list(value[key], f"{field}.{key}")


def _validate_applicability(value: Any, field: str) -> None:
    if value is None:
        return
    if not isinstance(value, Mapping):
        raise GovernanceReferenceGraphError(f"{field} must be an object")
    allowed = {
        "actions",
        "targets",
        "scopes",
        "status",
        "valid_from",
        "valid_until",
        "condition_refs",
    }
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise GovernanceReferenceGraphError(f"unknown {field} fields: " + ", ".join(unknown))
    for key in ("actions", "targets", "scopes", "condition_refs"):
        if key in value:
            _require_text_list(value[key], f"{field}.{key}")
    for key in ("status", "valid_from", "valid_until"):
        if key in value and value[key] is not None:
            _require_text(value[key], f"{field}.{key}")


def governance_reference_graph_sha256(value: Mapping[str, Any]) -> str:
    body = deepcopy(dict(value))
    body.pop("graph_sha256", None)
    return canonical_sha256(body)


def validate_governance_reference_graph(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise GovernanceReferenceGraphError("governance reference graph must be an object")
    graph = deepcopy(dict(value))
    allowed = {
        "schema",
        "graph_id",
        "graph_version",
        "relation_profile",
        "graph_sha256",
        "nodes",
        "relations",
        "coverage",
        "source_refs",
        "metadata",
        "authority_boundary",
    }
    unknown = sorted(set(graph) - allowed)
    if unknown:
        raise GovernanceReferenceGraphError("unknown graph fields: " + ", ".join(unknown))
    if graph.get("schema") != GRAPH_SCHEMA:
        raise GovernanceReferenceGraphError(f"schema must be {GRAPH_SCHEMA}")
    _require_text(graph.get("graph_id"), "graph_id")
    _require_text(graph.get("graph_version"), "graph_version")
    if graph.get("relation_profile") != RELATION_PROFILE:
        raise GovernanceReferenceGraphError(f"relation_profile must be {RELATION_PROFILE}")

    nodes = graph.get("nodes")
    relations = graph.get("relations")
    coverage = graph.get("coverage")
    if not isinstance(nodes, list) or not nodes:
        raise GovernanceReferenceGraphError("nodes must be a non-empty array")
    if not isinstance(relations, list):
        raise GovernanceReferenceGraphError("relations must be an array")
    if not isinstance(coverage, list):
        raise GovernanceReferenceGraphError("coverage must be an array")

    node_ids: set[str] = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, Mapping):
            raise GovernanceReferenceGraphError(f"nodes[{index}] must be an object")
        unknown_node = sorted(set(node) - {"node_id", "class", "ref", "attributes"})
        if unknown_node:
            raise GovernanceReferenceGraphError(
                f"unknown nodes[{index}] fields: " + ", ".join(unknown_node)
            )
        node_id = _require_text(node.get("node_id"), f"nodes[{index}].node_id")
        if node_id in node_ids:
            raise GovernanceReferenceGraphError(f"duplicate node_id: {node_id}")
        node_ids.add(node_id)
        _require_text(node.get("class"), f"nodes[{index}].class")
        _require_text(node.get("ref"), f"nodes[{index}].ref")
        attributes = node.get("attributes")
        if attributes is not None and not isinstance(attributes, Mapping):
            raise GovernanceReferenceGraphError(f"nodes[{index}].attributes must be an object")

    relation_ids: set[str] = set()
    for index, relation in enumerate(relations):
        if not isinstance(relation, Mapping):
            raise GovernanceReferenceGraphError(f"relations[{index}] must be an object")
        allowed_relation = {
            "relation_id",
            "subject",
            "relation",
            "object",
            "applicability",
            "constraint_ref",
            "source_ref",
            "evidence_refs",
            "basis_refs",
            "attributes",
        }
        unknown_relation = sorted(set(relation) - allowed_relation)
        if unknown_relation:
            raise GovernanceReferenceGraphError(
                f"unknown relations[{index}] fields: " + ", ".join(unknown_relation)
            )
        relation_id = _require_text(relation.get("relation_id"), f"relations[{index}].relation_id")
        if relation_id in relation_ids:
            raise GovernanceReferenceGraphError(f"duplicate relation_id: {relation_id}")
        relation_ids.add(relation_id)
        subject = _require_text(relation.get("subject"), f"relations[{index}].subject")
        obj = _require_text(relation.get("object"), f"relations[{index}].object")
        if subject not in node_ids or obj not in node_ids:
            raise GovernanceReferenceGraphError(
                f"relations[{index}] endpoints must reference declared node_id values"
            )
        _require_text(relation.get("relation"), f"relations[{index}].relation")
        _validate_applicability(relation.get("applicability"), f"relations[{index}].applicability")
        constraint_ref = relation.get("constraint_ref")
        if constraint_ref is not None:
            _require_text(constraint_ref, f"relations[{index}].constraint_ref")
        _require_text(relation.get("source_ref"), f"relations[{index}].source_ref")
        _require_text_list(relation.get("evidence_refs"), f"relations[{index}].evidence_refs")
        _require_text_list(relation.get("basis_refs"), f"relations[{index}].basis_refs")
        attributes = relation.get("attributes")
        if attributes is not None and not isinstance(attributes, Mapping):
            raise GovernanceReferenceGraphError(f"relations[{index}].attributes must be an object")

    coverage_ids: set[str] = set()
    for index, item in enumerate(coverage):
        if not isinstance(item, Mapping):
            raise GovernanceReferenceGraphError(f"coverage[{index}] must be an object")
        allowed_coverage = {
            "coverage_id",
            "relation",
            "subject",
            "object",
            "selector",
            "complete",
            "source_ref",
            "evidence_refs",
        }
        unknown_coverage = sorted(set(item) - allowed_coverage)
        if unknown_coverage:
            raise GovernanceReferenceGraphError(
                f"unknown coverage[{index}] fields: " + ", ".join(unknown_coverage)
            )
        coverage_id = _require_text(item.get("coverage_id"), f"coverage[{index}].coverage_id")
        if coverage_id in coverage_ids:
            raise GovernanceReferenceGraphError(f"duplicate coverage_id: {coverage_id}")
        coverage_ids.add(coverage_id)
        _require_text(item.get("relation"), f"coverage[{index}].relation")
        for endpoint in ("subject", "object"):
            endpoint_value = item.get(endpoint)
            if endpoint_value is not None:
                endpoint_value = _require_text(endpoint_value, f"coverage[{index}].{endpoint}")
                if endpoint_value not in node_ids:
                    raise GovernanceReferenceGraphError(
                        f"coverage[{index}].{endpoint} must reference a declared node_id"
                    )
        _validate_selector(item.get("selector"), f"coverage[{index}].selector")
        if not isinstance(item.get("complete"), bool):
            raise GovernanceReferenceGraphError(f"coverage[{index}].complete must be boolean")
        _require_text(item.get("source_ref"), f"coverage[{index}].source_ref")
        _require_text_list(item.get("evidence_refs"), f"coverage[{index}].evidence_refs")

    _require_text_list(graph.get("source_refs"), "source_refs")
    metadata = graph.get("metadata")
    if metadata is not None and not isinstance(metadata, Mapping):
        raise GovernanceReferenceGraphError("metadata must be an object when supplied")

    boundary = graph.get("authority_boundary")
    if not isinstance(boundary, Mapping):
        raise GovernanceReferenceGraphError("authority_boundary must be an object")
    if dict(boundary) != AUTHORITY_BOUNDARY:
        raise GovernanceReferenceGraphError(
            "authority_boundary must preserve the canonical non-authorizing boundary"
        )

    expected_hash = governance_reference_graph_sha256(graph)
    actual_hash = graph.get("graph_sha256")
    if actual_hash != expected_hash:
        raise GovernanceReferenceGraphError("graph_sha256 does not match canonical graph body")
    return graph


def build_governance_reference_graph(
    *,
    graph_id: str,
    nodes: list[Mapping[str, Any]],
    relations: list[Mapping[str, Any]],
    coverage: list[Mapping[str, Any]],
    source_refs: list[str],
    graph_version: str = "1",
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    graph: dict[str, Any] = {
        "schema": GRAPH_SCHEMA,
        "graph_id": graph_id,
        "graph_version": graph_version,
        "relation_profile": RELATION_PROFILE,
        "nodes": [deepcopy(dict(item)) for item in nodes],
        "relations": [deepcopy(dict(item)) for item in relations],
        "coverage": [deepcopy(dict(item)) for item in coverage],
        "source_refs": list(source_refs),
        "metadata": deepcopy(dict(metadata or {})),
        "authority_boundary": deepcopy(AUTHORITY_BOUNDARY),
    }
    graph["graph_sha256"] = governance_reference_graph_sha256(graph)
    return validate_governance_reference_graph(graph)


def governance_reference_graph_schema() -> dict[str, Any]:
    """Return the public structural contract for a Governance Reference Graph."""
    applicability = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "actions": {"type": "array", "items": {"type": "string"}},
            "targets": {"type": "array", "items": {"type": "string"}},
            "scopes": {"type": "array", "items": {"type": "string"}},
            "status": {"type": "string"},
            "valid_from": {"type": "string"},
            "valid_until": {"type": "string"},
            "condition_refs": {"type": "array", "items": {"type": "string"}},
        },
    }
    selector = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "actions": {"type": "array", "items": {"type": "string"}},
            "targets": {"type": "array", "items": {"type": "string"}},
            "scopes": {"type": "array", "items": {"type": "string"}},
        },
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://stegverse.org/schemas/governance-reference-graph.v1.json",
        "title": "StegVerse Governance Reference Graph",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema",
            "graph_id",
            "graph_version",
            "relation_profile",
            "graph_sha256",
            "nodes",
            "relations",
            "coverage",
            "source_refs",
            "authority_boundary",
        ],
        "properties": {
            "schema": {"const": GRAPH_SCHEMA},
            "graph_id": {"type": "string", "minLength": 1},
            "graph_version": {"type": "string", "minLength": 1},
            "relation_profile": {"const": RELATION_PROFILE},
            "graph_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "nodes": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["node_id", "class", "ref"],
                    "properties": {
                        "node_id": {"type": "string", "minLength": 1},
                        "class": {"type": "string", "minLength": 1},
                        "ref": {"type": "string", "minLength": 1},
                        "attributes": {"type": "object"},
                    },
                },
            },
            "relations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "relation_id",
                        "subject",
                        "relation",
                        "object",
                        "source_ref",
                        "evidence_refs",
                        "basis_refs",
                    ],
                    "properties": {
                        "relation_id": {"type": "string", "minLength": 1},
                        "subject": {"type": "string", "minLength": 1},
                        "relation": {"type": "string", "minLength": 1},
                        "object": {"type": "string", "minLength": 1},
                        "applicability": applicability,
                        "constraint_ref": {"type": "string", "minLength": 1},
                        "source_ref": {"type": "string", "minLength": 1},
                        "evidence_refs": {"type": "array", "items": {"type": "string"}},
                        "basis_refs": {"type": "array", "items": {"type": "string"}},
                        "attributes": {"type": "object"},
                    },
                },
            },
            "coverage": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "coverage_id",
                        "relation",
                        "complete",
                        "source_ref",
                        "evidence_refs",
                    ],
                    "properties": {
                        "coverage_id": {"type": "string", "minLength": 1},
                        "relation": {"type": "string", "minLength": 1},
                        "subject": {"type": "string", "minLength": 1},
                        "object": {"type": "string", "minLength": 1},
                        "selector": selector,
                        "complete": {"type": "boolean"},
                        "source_ref": {"type": "string", "minLength": 1},
                        "evidence_refs": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "source_refs": {"type": "array", "items": {"type": "string"}},
            "metadata": {"type": "object"},
            "authority_boundary": {
                "type": "object",
                "additionalProperties": False,
                "required": list(AUTHORITY_BOUNDARY),
                "properties": {
                    key: {"const": value}
                    for key, value in AUTHORITY_BOUNDARY.items()
                },
            },
        },
    }


def governance_reference_graph_example() -> dict[str, Any]:
    """Return a human-governance-shaped example without specializing the schema."""
    return build_governance_reference_graph(
        graph_id="external-framework-governance-001",
        nodes=[
            {"node_id": "human:operator", "class": "human", "ref": "external:operator"},
            {"node_id": "role:reviewer", "class": "role", "ref": "external:role:reviewer"},
            {"node_id": "human:decision-authority", "class": "human", "ref": "external:decision-authority"},
            {"node_id": "scope:irreversible", "class": "scope", "ref": "external:scope:irreversible"},
        ],
        relations=[
            {
                "relation_id": "r-member",
                "subject": "human:operator",
                "relation": "MEMBER_OF",
                "object": "role:reviewer",
                "source_ref": "external:org-graph:v1",
                "evidence_refs": ["external:evidence:org-graph:v1"],
                "basis_refs": [],
            },
            {
                "relation_id": "r-escalates",
                "subject": "human:operator",
                "relation": "ESCALATES_TO",
                "object": "human:decision-authority",
                "applicability": {
                    "actions": ["approve"],
                    "targets": ["case:*"],
                    "scopes": ["irreversible_commitment"],
                    "condition_refs": ["condition:human-review-required"],
                },
                "constraint_ref": "stegcore:policy-shape:escalation",
                "source_ref": "external:org-graph:v1",
                "evidence_refs": ["external:evidence:org-graph:v1"],
                "basis_refs": ["r-member"],
            },
            {
                "relation_id": "r-authority",
                "subject": "human:decision-authority",
                "relation": "HAS_SCOPED_AUTHORITY",
                "object": "scope:irreversible",
                "applicability": {
                    "actions": ["approve"],
                    "targets": ["case:*"],
                    "scopes": ["irreversible_commitment"],
                    "status": "ACTIVE",
                    "valid_from": "2026-09-01T00:00:00Z",
                    "valid_until": "2026-12-31T23:59:59Z",
                    "condition_refs": [],
                },
                "source_ref": "external:authority-basis:v1",
                "evidence_refs": ["external:evidence:authority:1"],
                "basis_refs": [],
            },
        ],
        coverage=[
            {
                "coverage_id": "coverage-authority-decision-authority",
                "relation": "HAS_SCOPED_AUTHORITY",
                "subject": "human:decision-authority",
                "selector": {
                    "actions": ["approve"],
                    "targets": ["case:*"],
                    "scopes": ["irreversible_commitment"],
                },
                "complete": True,
                "source_ref": "external:authority-basis:v1",
                "evidence_refs": ["external:evidence:authority:1"],
            }
        ],
        source_refs=["external:org-graph:v1", "external:authority-basis:v1"],
        metadata={
            "example_projection": "HITL",
            "example_projection_is_canonical_schema": False,
            "unknown_relations_grant_authority": False,
        },
    )


def governance_reference_graph_summary() -> dict[str, Any]:
    return {
        "contract": GRAPH_SCHEMA,
        "relation_profile": RELATION_PROFILE,
        "manifest_extension": EXTENSION_KEY,
        "purpose": "Represent typed governed relationships without making the SDK a governance engine.",
        "supports": [
            "HITL hierarchy",
            "agent supervision",
            "data provenance",
            "quorum and policy-shape references",
            "delegation",
            "evidence authority",
            "transition-authority evidence",
            "scope and conditions",
            "temporal validity",
            "coverage/completeness",
        ],
        "authority_effect": "NONE_REPRESENTATION_ONLY",
        "unknown_relations_grant_authority": False,
        "sdk_resolves_governance": False,
        "console_schema_command": "stegverse governance-graph --schema",
        "console_example_command": "stegverse governance-graph --example",
        "console_projection_command": "stegverse governance-graph --project graph.json --action ACTION --target TARGET --scope SCOPE --observed-at RFC3339",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stegverse governance-graph",
        description="Inspect the generic non-authorizing Governance Reference Graph contract",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--schema", action="store_true", help="print the graph JSON Schema")
    mode.add_argument("--example", action="store_true", help="print a ready-to-edit HITL-shaped example")
    mode.add_argument("--all", action="store_true", help="print summary, schema, and example together")
    mode.add_argument("--project", metavar="PATH", help="project recognized relations from a GRG JSON file")
    parser.add_argument("--task-id", default="SDK-GRG-CANONICAL-PROJECTION-CONSOLE-001")
    parser.add_argument("--action")
    parser.add_argument("--target")
    parser.add_argument("--scope")
    parser.add_argument("--observed-at")
    parser.add_argument(
        "--evaluate-authority-if-available",
        action="store_true",
        help="use installed canonical StegCore authority resolver when available",
    )
    args = parser.parse_args(argv)
    if args.project:
        if not all((args.action, args.target, args.scope, args.observed_at)):
            parser.error("--project requires --action, --target, --scope, and --observed-at")
        from pathlib import Path
        from .governance_reference_projection import project_governance_reference_graph

        graph = json.loads(Path(args.project).read_text(encoding="utf-8"))
        resolver = None
        if args.evaluate_authority_if_available:
            try:
                from stegcore.authority_basis import resolve_authority_basis as resolver
            except ImportError as exc:
                parser.error(
                    "--evaluate-authority-if-available requires the canonical StegCore package"
                )
        payload = project_governance_reference_graph(
            graph,
            task_id=args.task_id,
            candidate={"action": args.action, "target": args.target, "scope": args.scope},
            observed_at=args.observed_at,
            authority_resolver=resolver,
        )
    elif args.schema:
        payload: Any = governance_reference_graph_schema()
    elif args.example:
        payload = governance_reference_graph_example()
    elif args.all:
        payload = {
            "summary": governance_reference_graph_summary(),
            "schema": governance_reference_graph_schema(),
            "example": governance_reference_graph_example(),
        }
    else:
        payload = governance_reference_graph_summary()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


__all__ = [
    "AUTHORITY_BOUNDARY",
    "EXTENSION_KEY",
    "GRAPH_SCHEMA",
    "RELATION_PROFILE",
    "GovernanceReferenceGraphError",
    "build_governance_reference_graph",
    "governance_reference_graph_sha256",
    "validate_governance_reference_graph",
    "governance_reference_graph_schema",
    "governance_reference_graph_example",
    "governance_reference_graph_summary",
    "main",
]
