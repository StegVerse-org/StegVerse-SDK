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
    # The public request adapter validates the original wire manifest itself.
    # Derived canonical fields cannot be passed as top-level wire fields.
    request = external_manifest_to_public_request(manifest)
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


def derive_shwp_inference_state_graph(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Bind the existing SHWP request to its admitted, non-authorizing manifest.

    This graph is *intent*, not a second executor or a synthetic organization
    receipt. The Universal InTr implementation must independently compare the
    immutable original request, current Registry generation and COSV before
    calling the existing bounded parent consumer.
    """
    from .governance_navigation import canonical_sha256
    from .route_resolution import SHWP_SOVEREIGN_INFERENCE_ROUTE_ID

    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    if (route["route_id"] != SHWP_SOVEREIGN_INFERENCE_ROUTE_ID
            or route["processor_capability"] != "sovereign_inference"):
        raise ValueError("SHWP_MANIFEST_ROUTE_CAPABILITY_MISMATCH")
    binding = (manifest.get("extensions") or {}).get("stegverse_canonical_task")
    if not isinstance(binding, Mapping):
        raise ValueError("SHWP_CANONICAL_TASK_BINDING_REQUIRED")
    task_id = "SHWP-ECOSYSTEM-CHAT-INFERENCE-001"
    if binding.get("task_id") != task_id or binding.get("correlation_id") != task_id:
        raise ValueError("SHWP_CANONICAL_TASK_ID_MISMATCH")
    if binding.get("registry_repository") != "StegVerse-Labs/.github":
        raise ValueError("SHWP_CANONICAL_REGISTRY_MISMATCH")
    generation = binding.get("observed_registry_generation")
    if type(generation) is not int or generation < 1:
        raise ValueError("SHWP_REGISTRY_GENERATION_REQUIRED")
    if binding.get("cosv_task_vector") != "50000000100000":
        raise ValueError("SHWP_COSV_BINDING_MISMATCH")
    if binding.get("authority_effect") != "NONE":
        raise ValueError("SHWP_MANIFEST_MUST_NOT_GRANT_AUTHORITY")
    original = manifest.get("payload")
    if not isinstance(original, Mapping):
        raise ValueError("SHWP_UNCHANGED_ORIGINAL_REQUEST_PAYLOAD_REQUIRED")
    required = {
        "schema": "stegverse.resident-execution-request/v1",
        "request_id": "RESIDENT-EXEC-ECOSYSTEM-CHAT-PARENT-002",
        "state": "REQUESTED",
        "task_id": task_id,
        "mode": "DEDICATED_ECOSYSTEM_CHAT_PARENT",
        "entrypoint": "scripts/refresh_and_execute_resident_task.py",
        "fresh_fence_minimum_exclusive": 24,
        "credential_authority": "TV/TVC",
        "github_token_required": False,
        "github_token_runtime_authority": "NONE",
        "heartbeat_grants_execution_authority": False,
        "second_machine_required": False,
        "network_source_fetch_allowed": False,
        "request_granted_authority": False,
        "authority_effect": "NONE_REQUEST_ONLY",
    }
    for key, expected in required.items():
        if original.get(key) != expected or type(original.get(key)) is not type(expected):
            raise ValueError("SHWP_UNCHANGED_REQUEST_MISMATCH:" + key)
    return {
        "schema": "stegverse.sdk.installed-state-transition-graph/v1",
        "graph_id": "SHWP-ECOSYSTEM-CHAT-INFERENCE-001:ORIGINAL-G25",
        "canonical_task_id": task_id,
        "processing_capability": "sovereign_inference",
        "route_id": SHWP_SOVEREIGN_INFERENCE_ROUTE_ID,
        "request": {
            "original_request_id": original["request_id"],
            "original_request_sha256": canonical_sha256(original),
            "observed_registry_generation": generation,
            "cosv_task_vector": binding["cosv_task_vector"],
            "source_request_ref": "control/resident-execution-request.d/ecosystem-chat-parent-001.json",
            "authority_effect": "NONE",
        },
        "ordered_transitions": [],
        "ordered_transitions_source": "ORIGINAL_WORKERCOORDINATOR_INTR_MASTER_RECORDS",
        "requires_workercoordinator_claim_fence": True,
        "predecessor_closure_required": True,
        "adapter_executes_lifecycle": False,
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }


__all__ = [
    "derive_ecosystem_diagnostic_state_graph",
    "derive_governance_state_graph",
    "derive_shwp_inference_state_graph",
]
