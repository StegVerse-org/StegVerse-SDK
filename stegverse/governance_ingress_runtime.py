"""Executable bindings for SDK governance options 0B and 000.

This module does not implement governance. It converts already-validated SDK
input into the canonical sovereign validation request consumed by
``stegverse.sovereign_validation_runtime``. No credential is accepted here and
no missing StegGate evidence is synthesized for an external manifest.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .governance_navigation import (
    DEMO_DATASET_PROFILE,
    INGRESS_PROFILE,
    canonical_sha256,
    demo_output_manifest_shape,
    validate_external_manifest,
)
from .route_resolution import (
    CANONICAL_PRODUCTION_ROUTE_ID,
    governance_state_hash,
    resolve_route_declaration,
    route_from_manifest,
)

GOVERNANCE_REQUEST_EXTENSION = "stegverse_governance_request"


def _execution_provenance(resolved_route: Mapping[str, Any], origin_surface: str, state_hash: str | None = None) -> dict[str, Any]:
    value = {
        "route_id": resolved_route["route_id"],
        "route_declaration_hash": resolved_route["route_declaration_hash"],
        "lane_class": resolved_route["lane_class"],
        "routing_surface": resolved_route["routing_surface"],
        "containment": resolved_route["containment"],
        "sandbox_required": resolved_route["sandbox_required"],
        "sandbox_tier": "NONE",
        "origin_surface": origin_surface,
        "external_consequence_enabled": resolved_route["external_consequence_enabled"],
        "third_party_host_required": False,
    }
    if state_hash is not None:
        value["state_binding_hash"] = state_hash
    return value


def _canonical_production_route() -> dict[str, Any]:
    return resolve_route_declaration({
        "route_id": CANONICAL_PRODUCTION_ROUTE_ID,
        "lane_class": "PRODUCTION_VALIDATION",
        "routing_surface": "CANONICAL_PRODUCTION",
        "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
        "sandbox_required": False,
        "external_consequence_enabled": False,
    })


def _bounded_request_id(prefix: str, source_output_id: str, digest: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in source_output_id)
    safe = safe.strip("-._") or "submission"
    value = f"{prefix}-{safe}-{digest[:16]}"
    return value[:80]


def _governance_request_from_manifest(
    canonical: Mapping[str, Any], resolved_route: Mapping[str, Any]
) -> tuple[dict[str, Any], str]:
    extensions = canonical.get("extensions")
    if not isinstance(extensions, Mapping):
        raise ValueError("0B executable manifest requires extensions to be an object")
    raw_request = extensions.get(GOVERNANCE_REQUEST_EXTENSION)
    if not isinstance(raw_request, Mapping):
        raise ValueError(
            "0B executable manifest requires extensions."
            f"{GOVERNANCE_REQUEST_EXTENSION} containing the complete canonical StegGate request"
        )
    request = deepcopy(dict(raw_request))
    candidate = request.get("candidate")
    if not isinstance(candidate, Mapping):
        raise ValueError("0B governance request must contain candidate")
    if canonical_sha256(candidate) != canonical_sha256(canonical["candidate"]):
        raise ValueError("0B manifest candidate does not match governance_request candidate")

    state_hash = governance_state_hash(request)
    identity = {
        "manifest_profile": canonical["manifest_profile"],
        "manifest_profile_version": canonical["manifest_profile_version"],
        "source_framework": canonical["source_framework"],
        "source_instance": canonical.get("source_instance"),
        "source_output_id": canonical["source_output_id"],
        "canonical_manifest_sha256": canonical["canonical_manifest_sha256"],
        "ingress_mode": "external_manifest",
        "authority_effect": "NONE",
    }
    route_binding = {
        "route_id": resolved_route["route_id"],
        "route_declaration_hash": resolved_route["route_declaration_hash"],
        "state_binding_hash": state_hash,
        "route_substitution_permitted": False,
    }
    context = request.get("declared_context")
    if context is None:
        context = {}
    if not isinstance(context, Mapping):
        raise ValueError("governance_request.declared_context must be an object when present")
    context = dict(context)
    existing = context.get("sdk_ingress_manifest_identity")
    if existing is not None and existing != identity:
        raise ValueError("governance_request contains conflicting sdk_ingress_manifest_identity")
    existing_route = context.get("sdk_route_binding")
    if existing_route is not None and existing_route != route_binding:
        raise ValueError("governance_request contains conflicting sdk_route_binding")
    context["sdk_ingress_manifest_identity"] = identity
    context["sdk_route_binding"] = route_binding
    request["declared_context"] = context
    return request, state_hash


def external_manifest_to_public_request(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Bind a conforming 0B manifest to the route it explicitly declares.

    Structural validity is not enough: executable 0B input must carry the full
    canonical StegGate request and a published route declaration in ``extensions``.
    The SDK resolves that declaration, binds the governance-relevant state to it,
    and rejects unknown/conflicting routes instead of silently substituting a
    default route.
    """
    canonical = validate_external_manifest(manifest)
    resolved_route = route_from_manifest(canonical)
    governance_request, state_hash = _governance_request_from_manifest(canonical, resolved_route)
    digest = canonical["canonical_manifest_sha256"]
    input_data: dict[str, Any] = {
        "ingress_manifest_identity": governance_request["declared_context"]["sdk_ingress_manifest_identity"],
        "route_binding": governance_request["declared_context"]["sdk_route_binding"],
    }
    if canonical.get("payload") is not None:
        input_data["payload"] = canonical["payload"]
    else:
        input_data["payload_commitment"] = canonical["payload_commitment"]

    return {
        "schema_version": "1.0",
        "request_id": _bounded_request_id("sdk-0b", canonical["source_output_id"], digest),
        "requester_label": canonical["source_framework"],
        "case_profile": "ordinary",
        "execution_provenance": _execution_provenance(
            resolved_route,
            "StegVerse-org/StegVerse-SDK:governance-0B",
            state_hash,
        ),
        "input": {
            "steggate_request": governance_request,
            "input_data": input_data,
            "ingress_manifest_identity": input_data["ingress_manifest_identity"],
            "route_binding": input_data["route_binding"],
        },
        "return_projection": canonical["return_projection"]["mode"],
        "manifest_labels": canonical["manifest_labels"]["mode"] != "NONE",
        "authority_claim": False,
        "notes": f"0B manifest {digest}; declared route resolved without substitution; validation does not grant authority",
    }


def build_000_public_request() -> dict[str, Any]:
    """Build the complete bounded StegGate request for the SDK-owned 000 demo."""
    shape = demo_output_manifest_shape()
    manifest = shape["canonical_manifest_example"]
    dataset = manifest["payload"]
    if dataset.get("schema") != DEMO_DATASET_PROFILE:
        raise ValueError("000 demo dataset profile mismatch")
    dataset_hash = shape["demo_dataset_processing"]["dataset_sha256"]
    candidate = {
        "actor_class": "sdk_demo",
        "action": "evaluate_demo",
        "target": "sdk-owned-governance-outcome-dataset",
        "scope": "demo",
        "parameters": {"dataset_sha256": dataset_hash, "external_side_effect": False},
    }
    steggate_request = {
        "candidate": candidate,
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": [f"sdk-demo-dataset:{dataset_hash}"],
        },
        "signal": {
            "admitted_signal_refs": [f"sdk-demo-dataset:{dataset_hash}"],
            "excluded_signal_refs": [],
            "transformations": [],
            "missing_inputs": [],
            "uncertainty_state": "bounded",
            "reference_state_hash": dataset_hash,
            "expected_reference_state_hash": dataset_hash,
            "reconstruction_available": True,
            "transformation_provenance_complete": True,
        },
        "execution": {
            "actor_authority_current": True,
            "policy_current": True,
            "delegation_current": True,
            "evidence_current": True,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": True,
            "policy_ref": "stegverse-sdk-demo:no-external-side-effect",
            "delegation_ref": "stegverse-sdk-demo:simulation-only",
            "evidence_refs": [f"sdk-demo-dataset:{dataset_hash}"],
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
        "declared_context": {
            "demo_only": True,
            "dataset_schema": DEMO_DATASET_PROFILE,
            "dataset_sha256": dataset_hash,
            "external_side_effect": False,
            "authority_effect": "NONE",
        },
    }
    resolved_route = _canonical_production_route()
    state_hash = governance_state_hash(steggate_request)
    return {
        "schema_version": "1.0",
        "request_id": f"sdk-000-{dataset_hash[:16]}",
        "requester_label": "StegVerse SDK option 000",
        "case_profile": "ordinary",
        "execution_provenance": _execution_provenance(
            resolved_route,
            "StegVerse-org/StegVerse-SDK:governance-000",
            state_hash,
        ),
        "input": {
            "steggate_request": steggate_request,
            "input_data": {
                "payload": dataset,
                "demo_dataset_sha256": dataset_hash,
                "demo_only": True,
            },
        },
        "return_projection": "ALL",
        "manifest_labels": True,
        "authority_claim": False,
        "notes": "SDK-owned 000 demonstration; simulated consequence only; no external side effect or authority grant",
    }


def run_external_manifest(
    manifest: Mapping[str, Any], *, custody_db: str, host_identity: str = "stegverse-sovereign-local"
) -> dict[str, Any]:
    from .sovereign_validation_runtime import run_sovereign_validation

    request = external_manifest_to_public_request(manifest)
    return run_sovereign_validation(request, custody_db=custody_db, host_identity=host_identity)


def run_000_demo(*, custody_db: str, host_identity: str = "stegverse-sovereign-local") -> dict[str, Any]:
    """Execute option 000 through the same canonical sovereign runtime as 0A/0B."""
    from .sovereign_validation_runtime import run_sovereign_validation

    shape = demo_output_manifest_shape()
    result = run_sovereign_validation(
        build_000_public_request(), custody_db=custody_db, host_identity=host_identity
    )
    processing = dict(shape["demo_dataset_processing"])
    processing.update({
        "canonical_processing_status": "PROCESSED_CANONICAL_RUNTIME",
        "manifest_receipt_id": result.get("manifest_receipt_id"),
        "receipt_chain_head": result.get("route_receipt_chain_head"),
        "governance_state": result.get("governance_state"),
        "chain_verified": bool(result.get("chain_verified")),
        "master_records_custody_status": result.get("master_records_custody_status"),
        "external_side_effect": result.get("external_side_effect"),
        "third_party_host_required": result.get("third_party_host_required"),
        "do_not_claim_processed_until_receipts_exist": False,
    })
    shape["demo_dataset_processing"] = processing
    shape["canonical_runtime_result"] = dict(result)
    shape["demo_grants_authority"] = False
    return shape
