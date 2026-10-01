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
from .source_observation import PROFILE as SOURCE_OBSERVATION_PROFILE, validate_source_observation

PROCESSING_CAPABILITY_GOVERNANCE = "governance"
PAYLOAD_COMMITMENT_PROFILE_SHA256 = "sha256"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _require_text(manifest: Mapping[str, Any], key: str) -> str:
    value = manifest.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} is required")
    return value.strip()


def _require_exact_fields(value: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError("unknown " + label + " fields: " + ", ".join(unknown))


def _normalize_processing(
    manifest: Mapping[str, Any], route_declaration: Mapping[str, Any]
) -> dict[str, Any]:
    route_id = route_declaration.get("route_id")
    if not isinstance(route_id, str) or not route_id.strip():
        raise ValueError("extensions.stegverse_route.route_id is required")

    raw_processing = manifest.get("processing")
    if raw_processing is None:
        if route_id != CANONICAL_PRODUCTION_ROUTE_ID:
            raise ValueError(
                "unsupported manifest route for legacy v1 manifest; processing is required "
                "for non-governance or future processor routes"
            )
        return {
            "capability": PROCESSING_CAPABILITY_GOVERNANCE,
            "route_id": route_id,
            "derived_from_legacy_v1_route": True,
        }
    if not isinstance(raw_processing, Mapping):
        raise ValueError("processing must be an object")

    _require_exact_fields(raw_processing, {"capability", "route_id"}, "processing")
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


def _normalize_publisher_destination(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("completion.publisher.destination must be an object")
    destination_type = value.get("type")
    if destination_type not in {"SDK_CONSOLE_SESSION", "ECOSYSTEM_CHAT_SESSION", "KV"}:
        raise ValueError("completion.publisher.destination.type is not an installed destination type")
    if destination_type == "KV":
        _require_exact_fields(value, {"type", "kv_class", "kv_context_ref"}, "completion.publisher.destination")
        kv_class = value.get("kv_class")
        if kv_class not in {"MyKV", "OrgKV", "OrgMemberKV", "CompanyKV", "CompanyEmployeeKV"}:
            raise ValueError("completion.publisher.destination.kv_class is not an admitted KV class")
        context = value.get("kv_context_ref")
        if not isinstance(context, str) or not context.strip():
            raise ValueError("completion.publisher.destination.kv_context_ref is required")
        return {"type": "KV", "kv_class": kv_class, "kv_context_ref": context.strip()}
    _require_exact_fields(value, {"type", "session_ref"}, "completion.publisher.destination")
    session_ref = value.get("session_ref")
    if not isinstance(session_ref, str) or not session_ref.strip():
        raise ValueError("completion.publisher.destination.session_ref is required")
    return {"type": destination_type, "session_ref": session_ref.strip()}


def _normalize_completion(manifest: Mapping[str, Any]) -> dict[str, Any] | None:
    """Validate the governed southbound lifecycle and optional Publisher delivery."""
    raw = manifest.get("completion")
    if raw is None:
        return None
    if not isinstance(raw, Mapping):
        raise ValueError("completion must be an object")
    _require_exact_fields(raw, {"direction", "initiator", "publisher", "egress"}, "completion")
    if raw.get("direction") != "SOUTH":
        raise ValueError("completion.direction must be SOUTH")

    initiator = raw.get("initiator")
    if not isinstance(initiator, Mapping):
        raise ValueError("completion.initiator must be an object")
    _require_exact_fields(initiator, {"class", "ref"}, "completion.initiator")
    initiator_class, initiator_ref = initiator.get("class"), initiator.get("ref")
    if not isinstance(initiator_class, str) or not initiator_class.strip():
        raise ValueError("completion.initiator.class is required")
    if not isinstance(initiator_ref, str) or not initiator_ref.strip():
        raise ValueError("completion.initiator.ref is required")

    normalized_publisher = None
    publisher = raw.get("publisher")
    if publisher is not None:
        if not isinstance(publisher, Mapping):
            raise ValueError("completion.publisher must be an object")
        legacy_fields = {"stage", "required", "package_profile"}
        destination_fields = {"stage", "package_profile", "destination"}
        fields = frozenset(publisher)
        if fields not in {frozenset(legacy_fields), frozenset(destination_fields)}:
            _require_exact_fields(publisher, destination_fields | legacy_fields, "completion.publisher")
            raise ValueError("completion.publisher must use either legacy required or explicit destination semantics")
        if publisher.get("stage") != "PUBLISHER":
            raise ValueError("completion.publisher.stage must be PUBLISHER")
        package_profile = publisher.get("package_profile")
        if not isinstance(package_profile, str) or not package_profile.strip():
            raise ValueError("completion.publisher.package_profile is required")
        if "destination" in publisher:
            normalized_publisher = {
                "stage": "PUBLISHER",
                "package_profile": package_profile.strip(),
                "destination": _normalize_publisher_destination(publisher.get("destination")),
            }
        else:
            if not isinstance(publisher.get("required"), bool):
                raise ValueError("completion.publisher.required must be boolean in legacy v1 manifests")
            normalized_publisher = {
                "stage": "PUBLISHER",
                "required": publisher["required"],
                "package_profile": package_profile.strip(),
            }

    egress = raw.get("egress")
    if not isinstance(egress, Mapping):
        raise ValueError("completion.egress must be an object")
    _require_exact_fields(egress, {"final_stegverse_transition_surface", "transport", "far_side_transition_required", "destination_profile"}, "completion.egress")
    surface = egress.get("final_stegverse_transition_surface")
    if not isinstance(surface, str) or not surface.strip():
        raise ValueError("completion.egress.final_stegverse_transition_surface is required")
    if egress.get("transport") != "INTERLOCK_INTR":
        raise ValueError("completion.egress.transport must be INTERLOCK_INTR")
    if egress.get("far_side_transition_required") is not True:
        raise ValueError("completion.egress.far_side_transition_required must be true")
    destination_profile = egress.get("destination_profile")
    if destination_profile is not None and (not isinstance(destination_profile, str) or not destination_profile.strip()):
        raise ValueError("completion.egress.destination_profile must be a non-empty string when supplied")
    normalized = {
        "direction": "SOUTH",
        "initiator": {"class": initiator_class.strip(), "ref": initiator_ref.strip()},
        "egress": {"final_stegverse_transition_surface": surface.strip(), "transport": "INTERLOCK_INTR", "far_side_transition_required": True},
    }
    if normalized_publisher is not None:
        normalized["publisher"] = normalized_publisher
    if destination_profile is not None:
        normalized["egress"]["destination_profile"] = destination_profile.strip()
    return normalized


def validate_ingress_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate/canonicalize the processor-generic ingress envelope."""
    allowed = {
        "manifest_profile", "manifest_profile_version", "source_framework",
        "source_instance", "source_output_id", "created_at", "freshness",
        "payload", "payload_commitment", "payload_commitment_profile", "candidate",
        "declared_intent", "requested_consequence", "context_refs",
        "canonicalization_profile", "hashes", "attestation", "extensions",
        "processing", "return_projection", "completion", "manifest_labels",
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

    # Optional generic source-attribution profile: fail before the installed
    # processing route sees a forged native output. Other source-native payload
    # classes remain untouched and never acquire fabricated observations.
    if isinstance(manifest.get("payload"), Mapping) and manifest["payload"].get("profile") == SOURCE_OBSERVATION_PROFILE:
        validate_source_observation(manifest["payload"])

    hashes = manifest.get("hashes")
    if not isinstance(hashes, Mapping):
        raise ValueError("hashes must be an object")

    if has_payload:
        if "payload_commitment_profile" in manifest:
            raise ValueError("payload_commitment_profile is only valid with payload_commitment")
        if hashes.get("payload_sha256") != canonical_sha256(manifest["payload"]):
            raise ValueError("payload_sha256 does not match canonical payload")
    else:
        if manifest.get("payload_commitment_profile") != PAYLOAD_COMMITMENT_PROFILE_SHA256:
            raise ValueError("payload_commitment_profile must be sha256 for the currently published commitment profile")
        commitment = str(manifest["payload_commitment"]).strip().lower()
        if not _SHA256_RE.fullmatch(commitment):
            raise ValueError("sha256 payload_commitment must be 64 lowercase hexadecimal characters")

    extensions = manifest.get("extensions")
    if not isinstance(extensions, Mapping):
        raise ValueError("extensions must be an object")
    route_declaration = extensions.get("stegverse_route")
    if not isinstance(route_declaration, Mapping):
        raise ValueError("manifest requires extensions.stegverse_route declaring a published route")

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
                "governance processing requires extensions.stegverse_governance_request "
                "containing the complete canonical StegGate request"
            )
    else:
        if candidate is not None:
            if not isinstance(candidate, Mapping):
                raise ValueError("candidate must be an object when supplied")
            if canonical_sha256(candidate) != candidate_hash:
                raise ValueError("candidate_sha256 does not match canonical candidate")
        elif candidate_hash is not None:
            raise ValueError("candidate_sha256 is invalid when candidate is absent")

    completion = _normalize_completion(manifest)

    canonical = dict(manifest)
    canonical.setdefault("source_instance", None)
    canonical.setdefault("freshness", {})
    canonical.setdefault("context_refs", [])
    canonical.setdefault("canonicalization_profile", "steggate.jcs.v1")
    canonical.setdefault("attestation", None)
    canonical["processing"] = processing
    canonical["return_projection"] = normalize_return_projection(manifest.get("return_projection"))
    canonical["completion"] = completion
    canonical["manifest_labels"] = normalize_manifest_labels(manifest.get("manifest_labels"))
    canonical["ingress_mode"] = "external_manifest"
    canonical["external_manifest_valid"] = True
    canonical["external_manifest_grants_authority"] = False
    canonical["processing_selection_grants_authority"] = False
    canonical["master_records_transition_custody_independent_of_return_projection"] = True
    canonical["manifest_labels_change_governance"] = False
    canonical["complete_communication_manifest"] = completion is not None
    canonical["publisher_is_manifest_stage"] = completion is not None and "publisher" in completion
    canonical["communication_terminal_state_requires_far_side_intr_transition"] = completion is not None
    canonical["canonical_manifest_sha256"] = canonical_sha256(canonical)
    return canonical


__all__ = [
    "PAYLOAD_COMMITMENT_PROFILE_SHA256",
    "PROCESSING_CAPABILITY_GOVERNANCE",
    "validate_ingress_manifest",
]
