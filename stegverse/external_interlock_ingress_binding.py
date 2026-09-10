"""Bind canonical ingress manifests to the existing external Interlock transport contract.

This module keeps `stegverse.ingress-manifest.v1` as the universal manifested-data
envelope. The external-organization interaction object remains transport/control
metadata around that canonical ingress object; it is not a competing payload class.

The helpers validate and hash-bind the exact ingress wire manifest before transport.
Validator-derived/internal fields are not serialized back into the universal envelope.
The helpers do not perform InTr transport, mint receipts, grant authority, or claim
delivery.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .external_interlock_bootstrap import (
    REQUEST_SCHEMA,
    REQUEST_CLASS,
    TRANSPORT,
    build_external_interaction_manifest,
)
from .governance_navigation import canonical_sha256
from .manifest_contract import validate_ingress_manifest

BINDING_PROFILE = "stegverse.external-interlock-ingress-binding.v1"


def _validated_wire_manifest(ingress_manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(ingress_manifest, Mapping):
        raise ValueError("ingress_manifest must be an object")
    wire = deepcopy(dict(ingress_manifest))
    validate_ingress_manifest(wire)
    return wire


def build_ingress_bound_interlock_request(
    *,
    ingress_manifest: Mapping[str, Any],
    source_organization_id: str,
    target_organization_id: str,
    operation: str,
    authority_ref: str,
    experiment_id: str | None = None,
) -> dict[str, Any]:
    """Wrap the exact validated ingress wire manifest in external Interlock control metadata."""
    authority = str(authority_ref or "").strip()
    if not authority:
        raise ValueError("authority_ref is required")

    wire_ingress = _validated_wire_manifest(ingress_manifest)
    ingress_hash = canonical_sha256(wire_ingress)
    interaction = build_external_interaction_manifest(
        source_organization_id=source_organization_id,
        target_organization_id=target_organization_id,
        operation=operation,
        payload={
            "binding_profile": BINDING_PROFILE,
            "canonical_ingress_manifest": wire_ingress,
            "canonical_ingress_sha256": ingress_hash,
        },
        experiment_id=experiment_id,
    )

    return {
        "schema_version": REQUEST_SCHEMA,
        "request_class": REQUEST_CLASS,
        "operation": interaction["operation"],
        "authority_ref": authority,
        "transport": TRANSPORT,
        "payload": {"manifest": interaction},
        "bindings": {
            "experiment_id": interaction["experiment_id"],
            "source_organization_id": source_organization_id,
            "target_organization_id": target_organization_id,
            "interaction_manifest_id": interaction["manifest_id"],
            "interaction_manifest_sha256": interaction["manifest_sha256"],
            "canonical_ingress_profile": wire_ingress["manifest_profile"],
            "canonical_ingress_sha256": ingress_hash,
        },
        "authority_transfer": False,
        "sdk_mints_intr_receipt": False,
        "sdk_claims_delivery": False,
        "canonical_ingress_grants_transport_authority": False,
        "authority_effect_resolution": "DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS",
    }


def validate_ingress_bound_interlock_request(request: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the control envelope and exact nested canonical-ingress wire binding."""
    if not isinstance(request, Mapping):
        raise ValueError("request must be an object")
    expected = {
        "schema_version": REQUEST_SCHEMA,
        "request_class": REQUEST_CLASS,
        "transport": TRANSPORT,
        "authority_transfer": False,
        "sdk_mints_intr_receipt": False,
        "sdk_claims_delivery": False,
        "canonical_ingress_grants_transport_authority": False,
        "authority_effect_resolution": "DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS",
    }
    for key, value in expected.items():
        if request.get(key) != value:
            raise ValueError(f"{key} mismatch")
    if not str(request.get("authority_ref") or "").strip():
        raise ValueError("authority_ref is required")

    payload = request.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("request payload missing")
    interaction = payload.get("manifest")
    if not isinstance(interaction, Mapping):
        raise ValueError("interaction manifest missing")
    if interaction.get("operation") != request.get("operation"):
        raise ValueError("operation mismatch")
    if interaction.get("authority_transfer") is not False:
        raise ValueError("interaction authority transfer prohibited")

    body = dict(interaction)
    claimed_interaction_hash = str(body.pop("manifest_sha256", ""))
    if claimed_interaction_hash != canonical_sha256(body):
        raise ValueError("interaction manifest SHA-256 mismatch")

    interaction_payload = interaction.get("payload")
    if not isinstance(interaction_payload, Mapping):
        raise ValueError("interaction payload missing")
    if interaction_payload.get("binding_profile") != BINDING_PROFILE:
        raise ValueError("canonical ingress binding profile mismatch")
    nested = interaction_payload.get("canonical_ingress_manifest")
    if not isinstance(nested, Mapping):
        raise ValueError("canonical ingress manifest missing")
    wire_ingress = _validated_wire_manifest(nested)
    actual_ingress_hash = canonical_sha256(wire_ingress)
    if interaction_payload.get("canonical_ingress_sha256") != actual_ingress_hash:
        raise ValueError("canonical ingress SHA-256 mismatch")

    bindings = request.get("bindings")
    if not isinstance(bindings, Mapping):
        raise ValueError("request bindings missing")
    expected_bindings = {
        "experiment_id": interaction.get("experiment_id"),
        "source_organization_id": (interaction.get("source_organization") or {}).get("organization_id"),
        "target_organization_id": (interaction.get("target") or {}).get("organization_id"),
        "interaction_manifest_id": interaction.get("manifest_id"),
        "interaction_manifest_sha256": claimed_interaction_hash,
        "canonical_ingress_profile": wire_ingress.get("manifest_profile"),
        "canonical_ingress_sha256": actual_ingress_hash,
    }
    for key, value in expected_bindings.items():
        if bindings.get(key) != value:
            raise ValueError(f"bindings.{key} mismatch")

    return deepcopy(dict(request))


__all__ = [
    "BINDING_PROFILE",
    "build_ingress_bound_interlock_request",
    "validate_ingress_bound_interlock_request",
]
