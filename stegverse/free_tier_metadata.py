"""SDK ingestion contract for LLM-adapter free-tier trust metadata.

This module performs deterministic shape and non-claim validation only. It does
not call providers, persist records, issue receipts, export audit packets,
replay sessions, reconstruct sessions, or grant execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "preview_only",
    "bounded_live_use",
    "static_demo_only",
    "quota",
    "receipt_replay_limits",
    "trust_window",
    "upgrade_for",
    "non_claims",
}

REQUIRED_QUOTA_KEYS = {
    "status",
    "tier",
    "allowed",
    "reasons",
    "upgrade_triggers",
    "remaining",
    "non_claims",
}

REQUIRED_LIMIT_KEYS = {
    "status",
    "tier",
    "allowed",
    "reasons",
    "upgrade_triggers",
    "remaining",
    "scope",
    "non_claims",
}

REQUIRED_UPGRADE_REASONS = {
    "higher_quota",
    "private_connectors",
    "premium_models",
    "longer_retention",
    "deeper_replay",
    "deeper_reconstruction",
    "team_workspace",
    "api_access",
    "custom_policy",
    "exportable_audit_packet",
}

REQUIRED_NON_CLAIMS = {
    "free_tier_response_is_authority": False,
    "quota_allow_is_admissibility": False,
    "limit_allow_is_execution_authority": False,
    "upgrade_changes_admissibility_requirements": False,
}

REQUIRED_QUOTA_NON_CLAIMS = {
    "quota_allow_is_admissibility": False,
    "quota_allow_is_execution_authority": False,
    "provider_response_is_authority": False,
    "upgrade_changes_admissibility_requirements": False,
}

REQUIRED_LIMIT_NON_CLAIMS = {
    "limit_allow_is_admissibility": False,
    "limit_allow_is_execution_authority": False,
    "replay_grants_commit_time_standing": False,
    "reconstruction_grants_commit_time_standing": False,
    "receipt_export_is_permanent_retention": False,
}


@dataclass(frozen=True)
class FreeTierMetadataResult:
    accepted: bool
    routed_module: str
    metadata_status: str
    next_action: str
    errors: list[str]
    non_claims: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "routed_module": self.routed_module,
            "metadata_status": self.metadata_status,
            "next_action": self.next_action,
            "errors": list(self.errors),
            "non_claims": dict(self.non_claims),
        }


def validate_free_tier_metadata(metadata: Mapping[str, Any]) -> FreeTierMetadataResult:
    """Validate LLM-adapter ``free_tier_trust`` metadata for SDK ingestion."""

    errors: list[str] = []
    if not isinstance(metadata, Mapping):
        return _deny(["free_tier_trust metadata must be an object"])

    if set(metadata) != REQUIRED_TOP_LEVEL_KEYS:
        errors.append("free_tier_trust keys do not match required contract")
        return _deny(errors)

    if metadata["schema_version"] != "stegverse.ai_entry.free_tier_trust.v0.1":
        errors.append("schema_version is not supported")
    if metadata["preview_only"] is not True:
        errors.append("preview_only must be true")
    if metadata["bounded_live_use"] is not True:
        errors.append("bounded_live_use must be true")
    if metadata["static_demo_only"] is not False:
        errors.append("static_demo_only must be false")

    quota = metadata["quota"]
    limits = metadata["receipt_replay_limits"]
    if not isinstance(quota, Mapping) or set(quota) != REQUIRED_QUOTA_KEYS:
        errors.append("quota keys do not match required contract")
    else:
        errors.extend(_validate_quota(quota))
    if not isinstance(limits, Mapping) or set(limits) != REQUIRED_LIMIT_KEYS:
        errors.append("receipt_replay_limits keys do not match required contract")
    else:
        errors.extend(_validate_limits(limits))

    trust_window = metadata["trust_window"]
    if not isinstance(trust_window, Mapping):
        errors.append("trust_window must be an object")
    else:
        if "curiosity_level_meaningful_inquiries" not in trust_window:
            errors.append("trust_window missing curiosity_level_meaningful_inquiries")
        if "reliance_level_evaluation_inquiries" not in trust_window:
            errors.append("trust_window missing reliance_level_evaluation_inquiries")

    upgrade_for = metadata["upgrade_for"]
    if not isinstance(upgrade_for, list):
        errors.append("upgrade_for must be a list")
    else:
        missing = REQUIRED_UPGRADE_REASONS.difference(set(upgrade_for))
        if missing:
            errors.append("upgrade_for missing required reasons: " + ",".join(sorted(missing)))

    non_claims = metadata["non_claims"]
    if not isinstance(non_claims, Mapping):
        errors.append("non_claims must be an object")
    else:
        errors.extend(_validate_required_false(non_claims, REQUIRED_NON_CLAIMS, "non_claims"))

    if errors:
        return _deny(errors)

    return FreeTierMetadataResult(
        accepted=True,
        routed_module="StegVerse-org/SDK",
        metadata_status="accepted_for_non_authorizing_ingestion",
        next_action="Continue with governed SDK metadata compatibility review.",
        errors=[],
        non_claims={
            "sdk_ingestion_is_execution": False,
            "sdk_ingestion_is_admissibility": False,
            "sdk_ingestion_is_persistence": False,
            "sdk_ingestion_grants_commit_time_standing": False,
        },
    )


def _validate_quota(quota: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if quota["status"] not in {"ALLOW_QUOTA", "DENY_QUOTA"}:
        errors.append("quota.status is not allowed")
    if quota["tier"] != "free":
        errors.append("quota.tier must be free")
    if not isinstance(quota["allowed"], bool):
        errors.append("quota.allowed must be boolean")
    if not isinstance(quota["reasons"], list):
        errors.append("quota.reasons must be a list")
    if not isinstance(quota["upgrade_triggers"], list):
        errors.append("quota.upgrade_triggers must be a list")
    if not isinstance(quota["remaining"], Mapping):
        errors.append("quota.remaining must be an object")
    if not isinstance(quota["non_claims"], Mapping):
        errors.append("quota.non_claims must be an object")
    else:
        errors.extend(_validate_required_false(quota["non_claims"], REQUIRED_QUOTA_NON_CLAIMS, "quota.non_claims"))
    return errors


def _validate_limits(limits: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if limits["status"] not in {"ALLOW_LIMIT", "DENY_LIMIT"}:
        errors.append("receipt_replay_limits.status is not allowed")
    if limits["tier"] != "free":
        errors.append("receipt_replay_limits.tier must be free")
    if not isinstance(limits["allowed"], bool):
        errors.append("receipt_replay_limits.allowed must be boolean")
    if not isinstance(limits["reasons"], list):
        errors.append("receipt_replay_limits.reasons must be a list")
    if not isinstance(limits["upgrade_triggers"], list):
        errors.append("receipt_replay_limits.upgrade_triggers must be a list")
    if not isinstance(limits["remaining"], Mapping):
        errors.append("receipt_replay_limits.remaining must be an object")
    if not isinstance(limits["scope"], Mapping):
        errors.append("receipt_replay_limits.scope must be an object")
    if not isinstance(limits["non_claims"], Mapping):
        errors.append("receipt_replay_limits.non_claims must be an object")
    else:
        errors.extend(_validate_required_false(limits["non_claims"], REQUIRED_LIMIT_NON_CLAIMS, "receipt_replay_limits.non_claims"))
    return errors


def _validate_required_false(
    observed: Mapping[str, Any],
    expected: Mapping[str, bool],
    label: str,
) -> list[str]:
    errors: list[str] = []
    for key, value in expected.items():
        if observed.get(key) is not value:
            errors.append(f"{label}.{key} must be false")
    return errors


def _deny(errors: list[str]) -> FreeTierMetadataResult:
    return FreeTierMetadataResult(
        accepted=False,
        routed_module="StegVerse-org/SDK",
        metadata_status="rejected",
        next_action="Correct free_tier_trust metadata before SDK ingestion.",
        errors=errors,
        non_claims={
            "sdk_ingestion_is_execution": False,
            "sdk_ingestion_is_admissibility": False,
            "sdk_ingestion_is_persistence": False,
            "sdk_ingestion_grants_commit_time_standing": False,
        },
    )
