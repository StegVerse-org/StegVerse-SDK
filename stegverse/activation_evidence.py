"""Fail-closed activation-evidence binding for universal-entry deployments.

This module evaluates evidence. It does not deploy, activate transport, grant authority,
or create Master-Records custody. A deployment may use the resulting packet as one
input to a separately authorized activation decision.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


class ActivationEvidenceError(ValueError):
    """Raised when activation evidence is malformed or attempts escalation."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


_REQUIRED_EVIDENCE = (
    "sdk_validation",
    "site_validation",
    "canonical_collection",
    "provider_verification",
    "custody_verification",
)


def _require_non_authorizing(name: str, record: Mapping[str, Any]) -> None:
    forbidden_true = (
        "authorizing",
        "execution_authority_granted",
        "admissibility_determined",
        "deployment_authorized",
        "release_authorized",
    )
    if any(record.get(field) is True for field in forbidden_true):
        raise ActivationEvidenceError(f"{name} attempted authority escalation")


def _status(record: Mapping[str, Any]) -> str:
    return str(record.get("status", record.get("result", ""))).upper()


def evaluate_activation_evidence(
    evidence: Mapping[str, Mapping[str, Any]],
    *,
    required_entry_points: Sequence[str] = (
        "site_chat",
        "sdk",
        "api",
        "portable_node",
        "stegtalk",
        "agent",
        "external_actor_gateway",
    ),
) -> dict[str, Any]:
    """Build a deterministic readiness packet from externally supplied evidence."""
    missing = [name for name in _REQUIRED_EVIDENCE if not isinstance(evidence.get(name), Mapping)]
    if missing:
        raise ActivationEvidenceError(
            f"missing activation evidence: {', '.join(missing)}"
        )

    normalized = {name: dict(evidence[name]) for name in _REQUIRED_EVIDENCE}
    for name, record in normalized.items():
        _require_non_authorizing(name, record)

    blockers: list[str] = []
    sdk = normalized["sdk_validation"]
    site = normalized["site_validation"]
    collection = normalized["canonical_collection"]
    provider = normalized["provider_verification"]
    custody = normalized["custody_verification"]

    if _status(sdk) not in {"PASS", "SUCCESS", "COMPLETED"}:
        blockers.append("SDK_CURRENT_MAIN_VALIDATION_NOT_PASS")
    if _status(site) not in {"PASS", "SUCCESS", "COMPLETED"}:
        blockers.append("SITE_CURRENT_MAIN_VALIDATION_NOT_PASS")
    if collection.get("schema") != "stegverse.canonical_source_collection.v0.1":
        blockers.append("CANONICAL_COLLECTION_SCHEMA_NOT_VERIFIED")
    if not str(collection.get("collection_id", "")).startswith("sha256:"):
        blockers.append("CANONICAL_COLLECTION_ID_MISSING")
    if collection.get("source_count", 0) <= 0 or collection.get("projection_count", 0) <= 0:
        blockers.append("CANONICAL_COLLECTION_EMPTY")

    if provider.get("provider_used") is not True:
        blockers.append("LIVE_PROVIDER_RESULT_NOT_VERIFIED")
    if not provider.get("provider_receipt_id"):
        blockers.append("PROVIDER_RECEIPT_MISSING")
    if provider.get("usage_event_verified") is not True:
        blockers.append("PROVIDER_USAGE_EVENT_NOT_VERIFIED")
    if provider.get("provider_output_is_authority") is not False:
        blockers.append("PROVIDER_AUTHORITY_BOUNDARY_NOT_VERIFIED")

    if custody.get("custody_verified") is not True:
        blockers.append("MASTER_RECORDS_CUSTODY_NOT_VERIFIED")
    if custody.get("master_records_installed") is not True:
        blockers.append("MASTER_RECORDS_INSTALLATION_NOT_VERIFIED")
    if str(custody.get("reconstructability_status", "")).upper() != "PASS":
        blockers.append("RECONSTRUCTABILITY_NOT_PASS")

    observed_entries = set(site.get("verified_entry_points", []) or [])
    missing_entries = sorted(set(required_entry_points) - observed_entries)
    if missing_entries:
        blockers.append("ENTRY_POINT_PARITY_NOT_VERIFIED:" + ",".join(missing_entries))

    ready = not blockers
    body = {
        "schema": "stegverse.universal_entry_activation_evidence.v0.1",
        "ready_for_separate_activation_decision": ready,
        "activation_performed": False,
        "deployment_authorized": False,
        "release_authorized": False,
        "authorizing": False,
        "execution_authority_granted": False,
        "admissibility_determined": False,
        "custody_claim_derived": False,
        "blockers": blockers,
        "evidence_digests": {
            name: _digest(record) for name, record in normalized.items()
        },
        "verified_entry_points": sorted(observed_entries),
    }
    body["evidence_packet_id"] = _digest(body)
    return body


def validate_activation_evidence(packet: Mapping[str, Any]) -> dict[str, Any]:
    if packet.get("schema") != "stegverse.universal_entry_activation_evidence.v0.1":
        raise ActivationEvidenceError("unsupported activation evidence schema")
    if any(
        packet.get(field) is not False
        for field in (
            "activation_performed",
            "deployment_authorized",
            "release_authorized",
            "authorizing",
            "execution_authority_granted",
            "admissibility_determined",
            "custody_claim_derived",
        )
    ):
        raise ActivationEvidenceError("activation evidence attempted escalation")
    blockers = packet.get("blockers")
    if not isinstance(blockers, list):
        raise ActivationEvidenceError("activation blockers must be a list")
    ready = packet.get("ready_for_separate_activation_decision")
    if ready is not (len(blockers) == 0):
        raise ActivationEvidenceError("activation readiness/blocker mismatch")
    expected = dict(packet)
    packet_id = expected.pop("evidence_packet_id", None)
    if packet_id != _digest(expected):
        raise ActivationEvidenceError("activation evidence digest mismatch")
    return dict(packet)
