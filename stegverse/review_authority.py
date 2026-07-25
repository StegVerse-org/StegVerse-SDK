"""Fail-closed review-state governance for publicly visible artifacts.

Visibility is descriptive. It never implies claim, publication, attribution,
endorsement, compatibility, interoperability, or public-association authority.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping


class ReviewAuthorityError(ValueError):
    """Raised when a review-state object violates an authority boundary."""


def _canonical(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Mapping[str, Any]) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


VISIBILITY_STATES = {"PRIVATE", "RESTRICTED", "PUBLICLY_VISIBLE"}
PROCESS_STATES = {"DRAFT", "REVIEW_ONLY", "ADOPTED", "WITHDRAWN", "SUPERSEDED"}
AUTHORITY_FIELDS = (
    "claim_authority",
    "publication_authority",
    "attribution_authority",
    "public_association_authority",
)
CLAIM_FIELDS = ("endorsement", "compatibility", "interoperability")


def validate_review_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize a review manifest without inferring authority."""
    required = {
        "schema_version",
        "artifact_id",
        "artifact_version",
        "visibility_state",
        "process_state",
        *AUTHORITY_FIELDS,
        *CLAIM_FIELDS,
        "external_references",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise ReviewAuthorityError(f"missing required fields: {', '.join(missing)}")

    normalized = dict(manifest)
    if normalized["visibility_state"] not in VISIBILITY_STATES:
        raise ReviewAuthorityError("invalid visibility_state")
    if normalized["process_state"] not in PROCESS_STATES:
        raise ReviewAuthorityError("invalid process_state")
    for field in AUTHORITY_FIELDS:
        if not isinstance(normalized[field], bool):
            raise ReviewAuthorityError(f"{field} must be boolean")
    for field in CLAIM_FIELDS:
        if normalized[field] not in {"NONE", "ASSERTED", "AUTHORIZED"}:
            raise ReviewAuthorityError(f"invalid {field} state")
    if not isinstance(normalized["external_references"], list):
        raise ReviewAuthorityError("external_references must be a list")

    # Public visibility is never an authority source.
    if normalized["visibility_state"] == "PUBLICLY_VISIBLE" and normalized.get(
        "authority_source"
    ) == "VISIBILITY":
        raise ReviewAuthorityError("visibility cannot be an authority source")

    # Review-only artifacts must remain non-authoritative and non-claiming.
    if normalized["process_state"] == "REVIEW_ONLY":
        granted = [field for field in AUTHORITY_FIELDS if normalized[field]]
        asserted = [field for field in CLAIM_FIELDS if normalized[field] != "NONE"]
        if granted or asserted:
            raise ReviewAuthorityError(
                "review-only artifacts cannot grant authority or assert external claims"
            )

    # External association requires explicit authority for every named reference.
    for reference in normalized["external_references"]:
        if not isinstance(reference, Mapping):
            raise ReviewAuthorityError("external reference must be an object")
        if not reference.get("name"):
            raise ReviewAuthorityError("external reference requires name")
        if reference.get("association_status") not in {
            "REFERENCE_ONLY",
            "REVIEW_REQUESTED",
            "AUTHORIZED_ASSOCIATION",
        }:
            raise ReviewAuthorityError("invalid external association_status")
        if (
            reference["association_status"] == "AUTHORIZED_ASSOCIATION"
            and not normalized["public_association_authority"]
        ):
            raise ReviewAuthorityError(
                "authorized external association requires public_association_authority"
            )

    body = dict(normalized)
    supplied_hash = body.pop("manifest_sha256", None)
    computed_hash = _hash(body)
    if supplied_hash is not None and supplied_hash != computed_hash:
        raise ReviewAuthorityError("manifest hash mismatch")
    normalized["manifest_sha256"] = computed_hash
    return normalized


def build_acknowledgement_receipt(
    manifest: Mapping[str, Any],
    *,
    reviewer_id: str,
    acknowledgement: str = "UNDERSTOOD_NOT_ENDORSED",
) -> dict[str, Any]:
    """Create a deterministic acknowledgement that grants no authority."""
    validated = validate_review_manifest(manifest)
    if not reviewer_id.strip():
        raise ReviewAuthorityError("reviewer_id is required")
    if acknowledgement not in {
        "RECEIVED_ONLY",
        "UNDERSTOOD_NOT_ENDORSED",
        "FEEDBACK_PROVIDED_NOT_ENDORSED",
    }:
        raise ReviewAuthorityError("invalid acknowledgement state")
    receipt: dict[str, Any] = {
        "schema_version": "1.0.0",
        "receipt_type": "REVIEW_ACKNOWLEDGEMENT",
        "artifact_id": validated["artifact_id"],
        "artifact_version": validated["artifact_version"],
        "manifest_sha256": validated["manifest_sha256"],
        "reviewer_id": reviewer_id,
        "acknowledgement": acknowledgement,
        "authority_granted": False,
        "endorsement_granted": False,
        "attribution_granted": False,
        "public_association_granted": False,
        "interoperability_validated": False,
        "compatibility_validated": False,
    }
    receipt["receipt_sha256"] = _hash(receipt)
    return receipt


def authorize_transition(
    manifest: Mapping[str, Any],
    request: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate a review-to-publication transition, failing closed."""
    current = validate_review_manifest(manifest)
    required = {
        "transition_id",
        "target_process_state",
        "authorizer_id",
        "authorizer_authority_ref",
        "requested_authorities",
    }
    missing = sorted(required - set(request))
    if missing:
        raise ReviewAuthorityError(f"missing transition fields: {', '.join(missing)}")
    if request["target_process_state"] != "ADOPTED":
        raise ReviewAuthorityError("only explicit transition to ADOPTED is supported")
    if not str(request["authorizer_id"]).strip() or not str(
        request["authorizer_authority_ref"]
    ).strip():
        raise ReviewAuthorityError("authorizer identity and authority reference are required")
    requested = request["requested_authorities"]
    if not isinstance(requested, Mapping):
        raise ReviewAuthorityError("requested_authorities must be an object")
    if set(requested) != set(AUTHORITY_FIELDS):
        raise ReviewAuthorityError("all authority dimensions must be declared")
    if any(not isinstance(value, bool) for value in requested.values()):
        raise ReviewAuthorityError("requested authority values must be boolean")

    next_manifest = dict(current)
    next_manifest.pop("manifest_sha256", None)
    next_manifest["process_state"] = "ADOPTED"
    for field in AUTHORITY_FIELDS:
        next_manifest[field] = requested[field]
    next_manifest["authority_source"] = request["authorizer_authority_ref"]
    validated_next = validate_review_manifest(next_manifest)

    receipt: dict[str, Any] = {
        "schema_version": "1.0.0",
        "receipt_type": "REVIEW_AUTHORITY_TRANSITION",
        "transition_id": request["transition_id"],
        "artifact_id": current["artifact_id"],
        "from_manifest_sha256": current["manifest_sha256"],
        "to_manifest_sha256": validated_next["manifest_sha256"],
        "from_process_state": current["process_state"],
        "to_process_state": validated_next["process_state"],
        "authorizer_id": request["authorizer_id"],
        "authorizer_authority_ref": request["authorizer_authority_ref"],
        "visibility_was_authority_source": False,
        "requested_authorities": dict(requested),
        "decision": "ALLOW",
    }
    receipt["receipt_sha256"] = _hash(receipt)
    return {"manifest": validated_next, "receipt": receipt}
