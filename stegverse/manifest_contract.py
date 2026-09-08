"""Processor-generic StegVerse ingress manifest contract.

This module validates the universal machine-to-machine envelope independently
from any particular StegVerse processor. Processor-specific requirements are
applied conditionally from the declared processing capability/route.

Structural manifest validity never grants execution authority. Runtime route
resolution and processor binding remain separate fail-closed steps.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from .governance_navigation import (
    INGRESS_PROFILE,
    canonical_sha256,
    normalize_manifest_labels,
    normalize_return_projection,
)
from .route_resolution import CANONICAL_PRODUCTION_ROUTE_ID

PROCESSING_CAPABILITY_GOVERNANCE = "governance"
PAYLOAD_COMMITMENT_PROFILE_SHA256 = "sha256"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _require_text(manifest: Mapping[str, Any], key: str) -> str:
    value = manifest.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} is required")
    return value.strip()


def _normalize_processing(
    manifest: Mapping[str, Any], route_declaration: Mapping[str, Any]
) -> dict[str, str]:
    """Normalize caller-facing processing intent separately from route mechanics.

    ``processing`` is the preferred v1 form. For backward compatibility with
    already-published v1 governance manifests, an omitted processing block is
    derived only for the canonical governed route. Future processors must declare
    their processing capability explicitly.
    """
    route_id = route_declaration.get("route_id")
    if not isinstance(route_id, str) or not route_id.strip():
        raise ValueError("extensions.stegverse_route.route_id is required")

    raw_processing = manifest.get("processing")
    if raw_processing is None:
        if route_id != CANONICAL_PRODUCTION_ROUTE_ID:
            raise ValueError(
                "processing is required for non-governance or future processor routes"
            )
        return {
            "capability": PROCESSING_CAPABILITY_GOVERNANCE,
            "route_id": route_id,
            "derived_from_legacy_v1_route": True,
        }
    if not isinstance(raw_processing, Mapping):
        raise ValueError("processing must be an object")

    allowed = {"capability", "route_id"}
    unknown = sorted(set(raw_processing) - allowed)
    if unknown:
        raise ValueError("unknown processing fields: " + ", ".join(unknown))
    capability = raw_processing.get("capability")
    declared_route_id = raw_processing.get("route_id")
    if not isinstance(capability, str) or not capability.strip():
        raise ValueError("processing.capability is required")
    if not isinstance(declared_route_id, str) or not declared_route_id.strip():
        raise ValueError("processing.route_id is required")
    if declared_route_id != route_id:
        raise ValueError("processing.route_id must match extensions.stegverse_route.route_id")
    return {
        "capability": capability.strip(),
        "route_id": declared_route_id,
        "derived_from_legacy_v1_route": False,
    }


def validate_ingress_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate/canonicalize the processor-generic ingress envelope.

    The universal envelope accepts source-native payload classes without forcing
    governance semantics. Governance-only fields become mandatory only when the
    caller selects the governance processing capability.
    """
    allowed = {
        "manifest_profile",
        "manifest_profile_version",
        "source_framework",
        "source_instance",
        "source_output_id",
        "created_at",
        "freshness",
        "payload",
        "payload_commitment",
        "payload_commitment_profile",
        "candidate",
        "declared_intent",
        "requested_consequence",
        "context_refs",
        "canonicalization_profile",
        "hashes",
        "attestation",
        "extensions",
        "processing",
        "return_projection",
        "manifest_labels",
    }
    unknown = sorted(set(manifest) - allowed)
    if unknown:
        raise ValueError("unknown top-level manifest fields: " + ", ".join(unknown))
    if manifest.get("manifest_profile") != INGRESS_PROFILE:
        raise ValueError(f"manifest_profile must be {INGRESS_PROFILE}")
    if str(manifest.get("manifest_profile_version") or "") != "1":
        raise ValueError("manifest_profile_version must be 1")

    _require_text(manifest, "source_framework")
    _require_text(manifest, "source_output_id")
    _require_text(manifest, "created_at")
    _require_text(manifest, "declared_intent")
    _require_text(manifest, "requested_consequence")

    has_payload = "payload" in manifest and manifest.get("payload") is not None
    has_commitment = isinstance(manifest.get("payload_commitment"), str) and bool(
        str(manifest.get("payload_commitment")).strip()
    )
    if has_payload == has_commitment:
        raise ValueError("provide exactly one of payload or payload_commitment")

    hashes = manifest.get("hashes")
    if not isinstance(hashes, Mapping):
        raise ValueError("hashes must be an object")

    if has_payload:
        if "payload_commitment_profile" in manifest:
            raise ValueError("payload_commitment_profile is only valid with payload_commitment")
        expected = hashes.get("payload_sha256")
        actual = canonical_sha256(manifest["payload"])
        if expected != actual:
            raise ValueError("payload_sha256 does not match canonical payload")
    else:
        profile = manifest.get("payload_commitment_profile")
        if profile != PAYLOAD_COMMITMENT_PROFILE_SHA256:
            raise ValueError(
                "payload_commitment_profile must be sha256 for the currently published commitment profile"
            )
        commitment = str(manifest["payload_commitment"]).strip().lower()
        if not _SHA256_RE.fullmatch(commitment):
            raise ValueError("sha256 payload_commitment must be 64 lowercase hexadecimal characters")

    extensions = manifest.get("extensions")
    if not isinstance(extensions, Mapping):
        raise ValueError("extensions must be an object")
    route_declaration = extensions.get("stegverse_route")
    if not isinstance(route_declaration, Mapping):
        raise ValueError("extensions.stegverse_route must be an object")

    processing = _normalize_processing(manifest, route_declaration)
    capability = processing["capability"]

    candidate = manifest.get("candidate")
    candidate_hash = hashes.get("candidate_sha256")
    if capability == PROCESSING_CAPABILITY_GOVERNANCE:
        if not isinstance(candidate, Mapping):
            raise ValueError("governance processing requires candidate")
        if canonical_sha256(candidate) != candidate_hash:
            raise ValueError("candidate_sha256 does not match canonical candidate")
        governance_request = extensions.get("stegverse_governance_request")
        if not isinstance(governance_request, Mapping):
            raise ValueError(
                "governance processing requires extensions.stegverse_governance_request"
            )
    else:
        if candidate is not None:
            if not isinstance(candidate, Mapping):
                raise ValueError("candidate must be an object when supplied")
            if canonical_sha256(candidate) != candidate_hash:
                raise ValueError("candidate_sha256 does not match canonical candidate")
        elif candidate_hash is not None:
            raise ValueError("candidate_sha256 is invalid when candidate is absent")

    canonical = dict(manifest)
    canonical.setdefault("source_instance", None)
    canonical.setdefault("freshness", {})
    canonical.setdefault("context_refs", [])
    canonical.setdefault("canonicalization_profile", "steggate.jcs.v1")
    canonical.setdefault("attestation", None)
    canonical["processing"] = processing
    canonical["return_projection"] = normalize_return_projection(
        manifest.get("return_projection")
    )
    canonical["manifest_labels"] = normalize_manifest_labels(
        manifest.get("manifest_labels")
    )
    canonical["ingress_mode"] = "external_manifest"
    canonical["external_manifest_valid"] = True
    canonical["external_manifest_grants_authority"] = False
    canonical["processing_selection_grants_authority"] = False
    canonical["master_records_transition_custody_independent_of_return_projection"] = True
    canonical["manifest_labels_change_governance"] = False
    canonical["canonical_manifest_sha256"] = canonical_sha256(canonical)
    return canonical


__all__ = [
    "PAYLOAD_COMMITMENT_PROFILE_SHA256",
    "PROCESSING_CAPABILITY_GOVERNANCE",
    "validate_ingress_manifest",
]
