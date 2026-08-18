"""Generic preformatted-manifest ingress for governed SDK execution.

This module accepts user- or machine-supplied manifests conforming to the
published ``stegverse.ingress-manifest.v1`` profile, performs deterministic
normalization that does not add authority or invent routing, and converts the
accepted manifest into the ordinary public-inspection request consumed by the
canonical sovereign runtime.

The ingress decision is deliberately tri-state:

* ``ACCEPT`` — the supplied manifest is already canonical enough to execute;
* ``NORMALIZE`` — only deterministic, non-authorizing defaults/canonical forms
  were applied before execution;
* ``REJECT`` — the manifest is structurally invalid, asks for unsupported
  execution behavior, or cannot be represented without inventing semantics.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .public_inspection import (
    PublicInspectionRequestError,
    validate_public_inspection_request,
)

INGRESS_PROFILE = "stegverse.ingress-manifest.v1"
INGRESS_PROFILE_VERSION = "1.0"
INGRESS_DECISIONS = {"ACCEPT", "NORMALIZE", "REJECT"}


class ManifestIngressError(ValueError):
    """Raised when a supplied manifest cannot enter the canonical runtime."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _canonical_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestIngressError(f"{field} must be an object")
    return value


def _normalize_projection(value: Any) -> tuple[Any, bool]:
    """Normalize the published manifest projection shape to option-0 semantics."""
    changed = False
    if isinstance(value, str):
        return value.upper(), value != value.upper()
    if isinstance(value, Mapping):
        mode = value.get("mode")
        if not isinstance(mode, str):
            raise ManifestIngressError("return_projection.mode must be a string")
        normalized = mode.upper()
        changed = normalized != mode
        # The public-inspection execution surface currently consumes the mode;
        # selected transition classes remain manifest metadata and are not
        # silently converted into a different execution request.
        return normalized, changed
    raise ManifestIngressError("return_projection must be a string or object")


def _normalize_manifest_labels(value: Any) -> tuple[bool, bool]:
    """Map published explanatory-label projection into the current option-0 flag.

    ``ALL`` requests labels; ``NONE`` does not. ``SELECTED`` cannot be faithfully
    represented by the current public-inspection request and is therefore
    rejected rather than approximated.
    """
    if value is None:
        return False, True
    if isinstance(value, bool):
        return value, False
    if not isinstance(value, Mapping):
        raise ManifestIngressError("manifest_labels must be a boolean or object")
    mode = value.get("mode")
    if not isinstance(mode, str):
        raise ManifestIngressError("manifest_labels.mode must be a string")
    normalized = mode.upper()
    if normalized == "ALL":
        return True, mode != normalized
    if normalized == "NONE":
        return False, mode != normalized
    if normalized == "SELECTED":
        raise ManifestIngressError(
            "manifest_labels SELECTED is not executable through the current canonical option-0 projection"
        )
    raise ManifestIngressError("unsupported manifest_labels.mode")


def normalize_ingress_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Accept/normalize/reject one published preformatted manifest.

    The returned ``request`` is the exact object passed to the existing canonical
    sovereign runtime. No evaluator-specific processor, route, capability, or
    authority is introduced here.
    """
    original = dict(_require_mapping(manifest, "manifest"))
    profile = original.get("manifest_profile")
    if profile != INGRESS_PROFILE:
        raise ManifestIngressError(f"manifest_profile must be {INGRESS_PROFILE}")
    version = original.get("manifest_profile_version", INGRESS_PROFILE_VERSION)
    if str(version) != INGRESS_PROFILE_VERSION:
        raise ManifestIngressError("unsupported manifest_profile_version")

    changed = "manifest_profile_version" not in original

    routing = original.get("routing")
    if routing is None:
        # Backward-compatible published manifests may place execution provenance
        # directly at top level. We may normalize shape, but never invent route.
        routing = original.get("execution_provenance")
    routing = dict(_require_mapping(routing, "routing"))

    evaluation = original.get("evaluation_declaration")
    if evaluation is not None:
        evaluation = dict(_require_mapping(evaluation, "evaluation_declaration"))

    payload = original.get("payload")
    if payload is None:
        payload = original.get("input")
    if payload is None:
        raise ManifestIngressError("manifest must provide payload/input")
    payload = dict(_require_mapping(payload, "payload"))

    projection, projection_changed = _normalize_projection(original.get("return_projection", "ALL"))
    labels, labels_changed = _normalize_manifest_labels(original.get("manifest_labels"))
    changed = changed or projection_changed or labels_changed or "return_projection" not in original

    request_id = original.get("request_id") or original.get("source_output_id")
    if not isinstance(request_id, str) or not request_id.strip():
        raise ManifestIngressError("manifest must provide request_id or source_output_id")
    request_id = request_id.strip()

    case_profile = original.get("case_profile", "custom-declarative")
    if case_profile != original.get("case_profile"):
        changed = True

    authority_claim = original.get("authority_claim", False)
    if authority_claim is not False:
        raise ManifestIngressError("authority_claim must be false")

    request = {
        "schema_version": "1.0",
        "request_id": request_id,
        "requester_label": original.get("requester_label"),
        "case_profile": case_profile,
        "evaluation_declaration": evaluation,
        "execution_provenance": routing,
        "input": payload,
        "return_projection": projection,
        "manifest_labels": labels,
        "authority_claim": False,
        "notes": original.get("notes"),
    }

    try:
        validated = validate_public_inspection_request(request)
    except PublicInspectionRequestError as exc:
        raise ManifestIngressError(str(exc)) from exc

    normalized_manifest = dict(original)
    normalized_manifest["manifest_profile_version"] = INGRESS_PROFILE_VERSION
    normalized_manifest["routing"] = routing
    normalized_manifest["payload"] = payload
    normalized_manifest["return_projection"] = projection
    normalized_manifest["manifest_labels"] = {"mode": "ALL" if labels else "NONE"}
    normalized_manifest["authority_claim"] = False
    normalized_manifest.setdefault("case_profile", case_profile)
    normalized_manifest.setdefault("request_id", request_id)

    decision = "NORMALIZE" if changed or _canonical_json(normalized_manifest) != _canonical_json(original) else "ACCEPT"
    return {
        "schema": "stegverse.manifest-ingress-decision.v1",
        "decision": decision,
        "manifest_profile": INGRESS_PROFILE,
        "submitted_manifest_hash": _canonical_hash(original),
        "normalized_manifest_hash": _canonical_hash(normalized_manifest),
        "normalized_manifest": normalized_manifest,
        "request": validated,
        "authority_effect": "NONE",
        "route_invented": False,
        "evaluator_specific_processing": False,
    }


def prepare_ingress_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Non-throwing ingress decision suitable for UI/API callers."""
    try:
        return normalize_ingress_manifest(manifest)
    except ManifestIngressError as exc:
        return {
            "schema": "stegverse.manifest-ingress-decision.v1",
            "decision": "REJECT",
            "manifest_profile": manifest.get("manifest_profile") if isinstance(manifest, Mapping) else None,
            "reason": str(exc),
            "authority_effect": "NONE",
            "route_invented": False,
            "evaluator_specific_processing": False,
        }
