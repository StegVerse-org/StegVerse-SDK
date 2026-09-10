"""Versioned fail-closed security posture profiles for StegVerse SDK callers.

Postures are admission requirements, not processor semantics and not authority.
They can be upgraded independently from source-native payloads or evaluator declarations.
Task-scoped posture instances are ephemeral: they are bound to one task and expire.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from json import dumps
from typing import Any, Mapping

POSTURE_SCHEMA = "stegverse.sdk.security-posture.v1"
ATTESTATION_SCHEMA = "stegverse.sdk.security-posture-attestation.v1"
INSTANCE_SCHEMA = "stegverse.sdk.security-posture-instance.v1"
EXTENSION_KEY = "security_posture"

SECURE_V1 = {
    "schema": POSTURE_SCHEMA,
    "posture_id": "stegverse.security.secure.v1",
    "version": 1,
    "tier": "SECURE",
    "tier_rank": 1,
    "supersedes": None,
    "classification": ["general-sensitive"],
    "requirements": {
        "payload_digest_binding": True,
        "encryption_in_transit": True,
        "audit_receipt_required": True,
        "credential_authority": "TV/TVC",
        "github_runtime_authority": "NONE",
        "heartbeat_execution_authority": False,
    },
    "prohibitions": {
        "undeclared_sink": True,
        "runtime_secret_inheritance": True,
    },
    "upgrade_policy": {
        "allow_stronger_posture": True,
        "allow_silent_downgrade": False,
        "unknown_requirement_fails_closed": True,
    },
}

HIGH_V1 = {
    "schema": POSTURE_SCHEMA,
    "posture_id": "stegverse.security.high.v1",
    "version": 1,
    "tier": "HIGH",
    "tier_rank": 2,
    "supersedes": None,
    "classification": ["regulated", "PII", "confidential"],
    "requirements": {
        "minimum_necessary_manifest": True,
        "exact_field_scope": True,
        "purpose_binding": True,
        "approved_sink_binding": True,
        "payload_digest_binding": True,
        "encryption_in_transit": True,
        "encryption_at_rest": True,
        "audit_receipt_required": True,
        "automatic_disposition": True,
        "credential_authority": "TV/TVC",
        "github_runtime_authority": "NONE",
        "heartbeat_execution_authority": False,
    },
    "prohibitions": {
        "secondary_use": True,
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

HEALTH_PII_HIGH_V1 = {
    "schema": POSTURE_SCHEMA,
    "posture_id": "stegverse.security.health-pii-high.v1",
    "version": 1,
    "tier": "HIGHEST",
    "tier_rank": 3,
    "supersedes": None,
    "classification": ["PII", "ePHI", "sensitive-health-data", "KV-SKAP"],
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

POSTURES = {
    SECURE_V1["posture_id"]: SECURE_V1,
    HIGH_V1["posture_id"]: HIGH_V1,
    HEALTH_PII_HIGH_V1["posture_id"]: HEALTH_PII_HIGH_V1,
}

TIER_TO_POSTURE = {
    "SECURE": SECURE_V1["posture_id"],
    "HIGH": HIGH_V1["posture_id"],
    "HIGHEST": HEALTH_PII_HIGH_V1["posture_id"],
}

CHANNEL_MINIMUM_TIER = {
    "KV-SKAP": "HIGHEST",
    "SKAP-KV": "HIGHEST",
}

DATA_CLASS_MINIMUM_TIER = {
    "PII": "HIGH",
    "ePHI": "HIGHEST",
    "sensitive-health-data": "HIGHEST",
}


class SecurityPostureError(ValueError):
    pass


def _canonical_digest(value: Mapping[str, Any]) -> str:
    raw = dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(raw).hexdigest()


def _parse_time(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise SecurityPostureError("invalid_security_posture_instance_time") from exc
    if result.tzinfo is None:
        raise SecurityPostureError("security_posture_instance_time_must_be_timezone_aware")
    return result.astimezone(timezone.utc)


def resolve_security_posture(posture_id: str) -> dict[str, Any]:
    try:
        posture = deepcopy(POSTURES[posture_id])
    except KeyError as exc:
        raise SecurityPostureError(f"unsupported_security_posture:{posture_id}") from exc
    posture["posture_sha256"] = _canonical_digest(posture)
    return posture


def _tier_rank(tier: str) -> int:
    try:
        return int(POSTURES[TIER_TO_POSTURE[tier]]["tier_rank"])
    except KeyError as exc:
        raise SecurityPostureError(f"unsupported_security_posture_tier:{tier}") from exc


def select_effective_posture(
    *,
    requested_tier: str = "SECURE",
    organization_minimum_tier: str = "SECURE",
    data_class: str | None = None,
    channel: str | None = None,
) -> dict[str, Any]:
    """Select the strongest required posture; no caller may lower a mandatory floor."""
    candidates = [requested_tier, organization_minimum_tier]
    if data_class in DATA_CLASS_MINIMUM_TIER:
        candidates.append(DATA_CLASS_MINIMUM_TIER[data_class])
    if channel in CHANNEL_MINIMUM_TIER:
        candidates.append(CHANNEL_MINIMUM_TIER[channel])
    effective_tier = max(candidates, key=_tier_rank)
    posture = resolve_security_posture(TIER_TO_POSTURE[effective_tier])
    return {
        "requested_tier": requested_tier,
        "organization_minimum_tier": organization_minimum_tier,
        "data_class_minimum_tier": DATA_CLASS_MINIMUM_TIER.get(data_class),
        "channel_minimum_tier": CHANNEL_MINIMUM_TIER.get(channel),
        "effective_tier": effective_tier,
        "posture_id": posture["posture_id"],
        "posture_sha256": posture["posture_sha256"],
        "silent_downgrade_allowed": False,
    }


def instantiate_task_security_posture(
    *,
    task_id: str,
    requested_tier: str = "SECURE",
    organization_minimum_tier: str = "SECURE",
    data_class: str | None = None,
    channel: str | None = None,
    issued_at: str,
    ttl_seconds: int = 900,
) -> dict[str, Any]:
    """Materialize a non-transferable, task-scoped, expiring posture instance."""
    if not task_id:
        raise SecurityPostureError("security_posture_task_id_required")
    if not isinstance(ttl_seconds, int) or ttl_seconds <= 0 or ttl_seconds > 3600:
        raise SecurityPostureError("security_posture_ttl_out_of_bounds")
    issued = _parse_time(issued_at)
    selected = select_effective_posture(
        requested_tier=requested_tier,
        organization_minimum_tier=organization_minimum_tier,
        data_class=data_class,
        channel=channel,
    )
    expires = issued + timedelta(seconds=ttl_seconds)
    material = {
        "task_id": task_id,
        "posture_id": selected["posture_id"],
        "posture_sha256": selected["posture_sha256"],
        "effective_tier": selected["effective_tier"],
        "issued_at": issued.isoformat().replace("+00:00", "Z"),
        "expires_at": expires.isoformat().replace("+00:00", "Z"),
        "channel": channel,
        "data_class": data_class,
    }
    return {
        "schema": INSTANCE_SCHEMA,
        "instance_id": f"SP-{_canonical_digest(material)[:24]}",
        **material,
        "requested_tier": selected["requested_tier"],
        "organization_minimum_tier": selected["organization_minimum_tier"],
        "data_class_minimum_tier": selected["data_class_minimum_tier"],
        "channel_minimum_tier": selected["channel_minimum_tier"],
        "ttl_seconds": ttl_seconds,
        "transferable": False,
        "reusable_across_tasks": False,
        "authority_effect": "NONE_ADMISSION_EVIDENCE_ONLY",
    }


def validate_task_security_posture_instance(
    instance: Mapping[str, Any], *, task_id: str, observed_at: str
) -> dict[str, Any]:
    if instance.get("schema") != INSTANCE_SCHEMA:
        raise SecurityPostureError("invalid_security_posture_instance_schema")
    if instance.get("task_id") != task_id:
        raise SecurityPostureError("security_posture_instance_task_mismatch")
    if instance.get("transferable") is not False or instance.get("reusable_across_tasks") is not False:
        raise SecurityPostureError("security_posture_instance_reuse_forbidden")
    posture = resolve_security_posture(str(instance.get("posture_id")))
    if instance.get("posture_sha256") != posture["posture_sha256"]:
        raise SecurityPostureError("security_posture_instance_digest_mismatch")
    observed = _parse_time(observed_at)
    if observed < _parse_time(str(instance.get("issued_at"))):
        raise SecurityPostureError("security_posture_instance_not_yet_valid")
    if observed >= _parse_time(str(instance.get("expires_at"))):
        raise SecurityPostureError("security_posture_instance_expired")
    return {
        "schema": "stegverse.sdk.security-posture-instance-admission.v1",
        "instance_id": instance["instance_id"],
        "task_id": task_id,
        "posture_id": posture["posture_id"],
        "effective_tier": posture["tier"],
        "status": "INSTANCE_ACTIVE",
        "authority_effect": "NONE_ADMISSION_EVIDENCE_ONLY",
    }


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
        "tier": posture["tier"],
    }
    return result
