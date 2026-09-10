"""Versioned fail-closed security posture profiles for StegVerse SDK callers.

Postures are admission requirements, not processor semantics and not authority.
They can be upgraded independently from source-native payloads or evaluator declarations.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from json import dumps
from typing import Any, Mapping

POSTURE_SCHEMA = "stegverse.sdk.security-posture.v1"
ATTESTATION_SCHEMA = "stegverse.sdk.security-posture-attestation.v1"
EXTENSION_KEY = "security_posture"

HEALTH_PII_HIGH_V1 = {
    "schema": POSTURE_SCHEMA,
    "posture_id": "stegverse.security.health-pii-high.v1",
    "version": 1,
    "supersedes": None,
    "classification": ["PII", "ePHI", "sensitive-health-data"],
    "requirements": {
        "minimum_necessary_manifest": True,
        "exact_field_scope": True,
        "purpose_binding": True,
        "approved_sink_binding": True,
        "payload_digest_binding": True,
        "encryption_in_transit": True,
        "encryption_at_rest": True,
        "audit_receipt_required": True,
        "subject_identifier_pseudonymous": True,
        "retention_max_hours": 24,
        "automatic_disposition": True,
        "fresh_runtime_root": True,
        "predecessor_authority_rejected": True,
        "credential_authority": "TV/TVC",
        "github_runtime_authority": "NONE",
        "heartbeat_execution_authority": False,
    },
    "prohibitions": {
        "secondary_use": True,
        "model_training": True,
        "advertising": True,
        "data_sale": True,
        "undeclared_sink": True,
        "raw_sensitive_data_in_audit_receipt": True,
        "runtime_secret_inheritance": True,
    },
    "upgrade_policy": {
        "allow_stronger_posture": True,
        "allow_silent_downgrade": False,
        "unknown_requirement_fails_closed": True,
    },
}

POSTURES = {HEALTH_PII_HIGH_V1["posture_id"]: HEALTH_PII_HIGH_V1}


class SecurityPostureError(ValueError):
    pass


def _canonical_digest(value: Mapping[str, Any]) -> str:
    raw = dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(raw).hexdigest()


def resolve_security_posture(posture_id: str) -> dict[str, Any]:
    try:
        posture = deepcopy(POSTURES[posture_id])
    except KeyError as exc:
        raise SecurityPostureError(f"unsupported_security_posture:{posture_id}") from exc
    posture["posture_sha256"] = _canonical_digest(posture)
    return posture


def validate_runtime_attestation(posture_id: str, attestation: Mapping[str, Any]) -> dict[str, Any]:
    posture = resolve_security_posture(posture_id)
    if attestation.get("schema") != ATTESTATION_SCHEMA:
        raise SecurityPostureError("invalid_security_posture_attestation_schema")
    if attestation.get("posture_id") != posture_id:
        raise SecurityPostureError("security_posture_id_mismatch")
    if attestation.get("posture_sha256") != posture["posture_sha256"]:
        raise SecurityPostureError("security_posture_digest_mismatch")

    observed = attestation.get("observed_requirements")
    if not isinstance(observed, Mapping):
        raise SecurityPostureError("missing_observed_requirements")
    for key, required in posture["requirements"].items():
        actual = observed.get(key)
        if isinstance(required, bool):
            if actual is not required:
                raise SecurityPostureError(f"posture_requirement_unsatisfied:{key}")
        elif key == "retention_max_hours":
            if not isinstance(actual, (int, float)) or actual > required:
                raise SecurityPostureError("posture_requirement_unsatisfied:retention_max_hours")
        elif actual != required:
            raise SecurityPostureError(f"posture_requirement_unsatisfied:{key}")

    observed_prohibitions = attestation.get("observed_prohibitions")
    if not isinstance(observed_prohibitions, Mapping):
        raise SecurityPostureError("missing_observed_prohibitions")
    for key, prohibited in posture["prohibitions"].items():
        if prohibited is True and observed_prohibitions.get(key) is not True:
            raise SecurityPostureError(f"posture_prohibition_not_enforced:{key}")

    return {
        "schema": "stegverse.sdk.security-posture-admission.v1",
        "posture_id": posture_id,
        "posture_sha256": posture["posture_sha256"],
        "status": "POSTURE_SATISFIED",
        "silent_downgrade_allowed": False,
        "authority_effect": "NONE_ADMISSION_EVIDENCE_ONLY",
    }


def attach_security_posture(manifest: Mapping[str, Any], posture_id: str) -> dict[str, Any]:
    """Attach only a posture reference/digest; do not add experiment-specific fields."""
    result = deepcopy(dict(manifest))
    extensions = result.setdefault("extensions", {})
    if not isinstance(extensions, dict):
        raise SecurityPostureError("manifest_extensions_must_be_object")
    posture = resolve_security_posture(posture_id)
    extensions[EXTENSION_KEY] = {
        "posture_id": posture_id,
        "posture_sha256": posture["posture_sha256"],
        "version": posture["version"],
    }
    return result
