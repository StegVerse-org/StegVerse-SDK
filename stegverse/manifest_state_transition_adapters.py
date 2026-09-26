"""Derivation-only adapters for the universal manifest state-transition runtime."""
from __future__ import annotations

from typing import Any, Mapping

from .ecosystem_diagnostic_runtime import (
    PROCESSING_CAPABILITY as DIAGNOSTIC_CAPABILITY,
    REQUEST_EXTENSION as DIAGNOSTIC_REQUEST_EXTENSION,
    validate_diagnostic_request,
)
from .governance_ingress_runtime import external_manifest_to_public_request
from .manifest_contract import validate_ingress_manifest
from .route_resolution import route_from_manifest


def derive_governance_state_graph(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    # The public request adapter validates the ORIGINAL wire manifest itself.\n    # Passing the derived canonical view reintroduces computed fields as illegal\n    # wire fields and rejects an otherwise valid governance manifest.\n    request = external_manifest_to_public_request(manifest)
    return {
        "schema": "stegverse.sdk.installed-state-transition-graph/v1",
        "graph_id": "RTC-GOVERNED-PROCESSING-002",
        "canonical_task_id": None,
        "processing_capability": route["processor_capability"],
        "route_id": route["route_id"],
        "request": request,
        "ordered_transitions": [],
        "ordered_transitions_source": "INSTALLED_RUNTIME_CANONICAL_GRAPH",
        "requires_workercoordinator_claim_fence": False,
        "predecessor_closure_required": True,
        "adapter_executes_lifecycle": False,
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }


def derive_ecosystem_diagnostic_state_graph(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    processing = canonical.get("processing") or {}
    if processing.get("capability") != DIAGNOSTIC_CAPABILITY:
        raise ValueError("manifest processing capability does not select ecosystem_diagnostic")
    request = validate_diagnostic_request(
        (canonical.get("extensions") or {}).get(DIAGNOSTIC_REQUEST_EXTENSION)
    )
    return {
        "schema": "stegverse.sdk.installed-state-transition-graph/v1",
        "graph_id": "RTC-GOVERNED-PROCESSING-002:ECOSYSTEM_DIAGNOSTIC",
        "canonical_task_id": None,
        "processing_capability": DIAGNOSTIC_CAPABILITY,
        "route_id": route["route_id"],
        "request": request,
        "ordered_transitions": [],
        "ordered_transitions_source": "INSTALLED_RUNTIME_CANONICAL_GRAPH",
        "requires_workercoordinator_claim_fence": False,
        "predecessor_closure_required": True,
        "adapter_executes_lifecycle": False,
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }


__all__ = [
    "derive_ecosystem_diagnostic_state_graph",
    "derive_governance_state_graph",
]
