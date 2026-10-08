"""Manifest binding for the SVG governance-cycle benchmark under the existing canonical owner.

This module derives request intent only. It does not execute StegCore, mint a
WorkerCoordinator claim/fence, admit Interlock/InTr, grant credentials, commit a
consequence, or create an organization record or a Master Records organization record.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import SVG_GOVERNANCE_CYCLE_ROUTE_ID, route_from_manifest

PROCESSING_CAPABILITY = "svg_governance_cycle"
ROUTE_ID = SVG_GOVERNANCE_CYCLE_ROUTE_ID
REQUEST_EXTENSION = "stegverse_svg_governance_cycle_request"
REQUEST_SCHEMA = "stegverse.sdk.svg-governance-cycle.v1"
OWNER_TASK_ID = "STEGVERSE-CANONICAL-WORK-COORDINATION-001"
OWNER_COSV = "10100000100000"
NATIVE_EVALUATOR = "stegcore.three_layer.evaluate_three_layer"
GOVERNANCE_SCHEMA_REF = "StegVerse-Labs/Governance/schemas/admissibility_stage_vector.schema.json"


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value.strip()


def validate_svg_governance_cycle_request(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("svg_governance_cycle processor_request must be an object")
    if value.get("schema") != REQUEST_SCHEMA:
        raise ValueError(f"svg_governance_cycle request schema must be {REQUEST_SCHEMA}")
    if value.get("task_id") != OWNER_TASK_ID or value.get("correlation_id") != OWNER_TASK_ID:
        raise ValueError("SVG_CANONICAL_OWNER_BINDING_MISMATCH")
    if value.get("cosv_task_vector") != OWNER_COSV:
        raise ValueError("SVG_COSV_BINDING_MISMATCH")
    if value.get("native_evaluator") != NATIVE_EVALUATOR:
        raise ValueError("SVG_NATIVE_EVALUATOR_BINDING_MISMATCH")
    if value.get("governance_schema_ref") != GOVERNANCE_SCHEMA_REF:
        raise ValueError("SVG_GOVERNANCE_SCHEMA_BINDING_MISMATCH")
    if value.get("authority_effect") != "NONE_MANIFEST_REQUEST_ONLY":
        raise ValueError("SVG_MANIFEST_REQUEST_MUST_NOT_GRANT_AUTHORITY")
    benchmark_profile = _text(value.get("benchmark_profile"), "benchmark_profile")
    transition_subject = _text(value.get("transition_subject"), "transition_subject")
    expected = value.get("expected_evidence")
    if not isinstance(expected, list) or not expected or not all(isinstance(x, str) and x for x in expected):
        raise ValueError("expected_evidence must be a non-empty array of strings")
    return {
        "schema": REQUEST_SCHEMA,
        "task_id": OWNER_TASK_ID,
        "correlation_id": OWNER_TASK_ID,
        "cosv_task_vector": OWNER_COSV,
        "benchmark_profile": benchmark_profile,
        "transition_subject": transition_subject,
        "native_evaluator": NATIVE_EVALUATOR,
        "governance_schema_ref": GOVERNANCE_SCHEMA_REF,
        "expected_evidence": list(dict.fromkeys(expected)),
        "authority_effect": "NONE_MANIFEST_REQUEST_ONLY",
    }


def derive_state_graph(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    if route.get("route_id") != ROUTE_ID or route.get("processor_capability") != PROCESSING_CAPABILITY:
        raise ValueError("SVG_MANIFEST_ROUTE_CAPABILITY_MISMATCH")
    request = validate_svg_governance_cycle_request(
        (canonical.get("extensions") or {}).get(REQUEST_EXTENSION)
    )
    return {
        "schema": "stegverse.sdk.installed-state-transition-graph/v1",
        "graph_id": OWNER_TASK_ID + ":SVG-GOVERNANCE-CYCLE",
        "canonical_task_id": OWNER_TASK_ID,
        "processing_capability": PROCESSING_CAPABILITY,
        "route_id": ROUTE_ID,
        "request": deepcopy(request),
        "ordered_transitions": [],
        "ordered_transitions_source": "EXISTING_INTR_WORKERCOORDINATOR_ORGANIZATION_MASTER_RECORDS",
        "requires_workercoordinator_claim_fence": True,
        "predecessor_closure_required": True,
        "adapter_executes_lifecycle": False,
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }


__all__ = [
    "PROCESSING_CAPABILITY", "ROUTE_ID", "REQUEST_EXTENSION", "REQUEST_SCHEMA",
    "OWNER_TASK_ID", "OWNER_COSV", "validate_svg_governance_cycle_request",
    "derive_state_graph",
]
