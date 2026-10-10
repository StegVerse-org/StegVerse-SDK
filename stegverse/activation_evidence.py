"""Fail-closed activation-evidence binding for universal-entry deployments.

This module evaluates evidence. It does not deploy, activate transport, grant authority,
or create a Master-Records organization record. A deployment may use the resulting
packet as one input to a separately authorized activation decision.

Master Records records released organization batch receipts downstream. Its recording
and reconstruction are never readiness predicates: when ``organization_record_verification``
evidence (the Master Records recording check) is supplied it is reported in
``master_records_recording`` and never adds a blocker. Interlock/InTr admits transitions;
the Organization keeps its own ledger (LLMA-DECLARED-PATH-CONFORMANCE-368).

Naming migration (MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002): the packet writes only
the new names. Readers also accept the ``LEGACY_*`` names below so already-deployed
peers keep working.
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


ORGANIZATION_RECORD_EVIDENCE_KEY = "organization_record_verification"
ORGANIZATION_RECORD_INSTALLED_FIELD = "organization_record_installed"
ORGANIZATION_RECORD_NOT_VERIFIED = "MASTER_RECORDS_ORGANIZATION_RECORD_NOT_VERIFIED"
ORGANIZATION_RECORD_CLAIM_FIELD = "organization_record_claim_derived"

# Legacy names, accepted by readers only (MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002).
LEGACY_ORGANIZATION_RECORD_EVIDENCE_KEY = "custody_verification"
LEGACY_ORGANIZATION_RECORD_VERIFIED_FIELD = "custody_verified"
LEGACY_ORGANIZATION_RECORD_INSTALLED_FIELD = "master_records_installed"
LEGACY_ORGANIZATION_RECORD_NOT_VERIFIED = "MASTER_RECORDS_CUSTODY_NOT_VERIFIED"
LEGACY_ORGANIZATION_RECORD_INSTALLATION_NOT_VERIFIED = "MASTER_RECORDS_INSTALLATION_NOT_VERIFIED"
LEGACY_ORGANIZATION_RECORD_CLAIM_FIELD = "custody_claim_derived"

# Blocker codes earlier packets used for "no reconstructable Master Records record was
# shown". They are still recognized when reading old packets; evaluation no longer emits
# them because Master Records recording does not gate readiness.
ORGANIZATION_RECORD_BLOCKER_CODES = frozenset(
    {
        ORGANIZATION_RECORD_NOT_VERIFIED,
        LEGACY_ORGANIZATION_RECORD_NOT_VERIFIED,
        LEGACY_ORGANIZATION_RECORD_INSTALLATION_NOT_VERIFIED,
    }
)

_REQUIRED_EVIDENCE = (
    "sdk_validation",
    "site_validation",
    "canonical_collection",
    "provider_verification",
)
# Optional, downstream and non-gating: the Master Records recording check.
_OPTIONAL_EVIDENCE = (ORGANIZATION_RECORD_EVIDENCE_KEY,)
OWNING_EXISTING_GOAL = "LLMA-DECLARED-PATH-CONFORMANCE-368"


def is_organization_record_blocker(code: str) -> bool:
    """True when a blocker code (new or legacy) in an older packet reports a missing record."""
    return code in ORGANIZATION_RECORD_BLOCKER_CODES


def _normalize_evidence(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Map the legacy evidence key onto the new one; reject ambiguous input."""
    normalized = dict(evidence)
    legacy = normalized.pop(LEGACY_ORGANIZATION_RECORD_EVIDENCE_KEY, None)
    if legacy is not None:
        if ORGANIZATION_RECORD_EVIDENCE_KEY in normalized:
            raise ActivationEvidenceError(
                "supply organization_record_verification only; "
                "custody_verification is its legacy name"
            )
        normalized[ORGANIZATION_RECORD_EVIDENCE_KEY] = legacy
    return normalized


def _organization_record_exists(record: Mapping[str, Any]) -> bool:
    if ORGANIZATION_RECORD_INSTALLED_FIELD in record:
        return record.get(ORGANIZATION_RECORD_INSTALLED_FIELD) is True
    # Legacy evidence stays as strict as before: both legacy flags must be true.
    return (
        record.get(LEGACY_ORGANIZATION_RECORD_INSTALLED_FIELD) is True
        and record.get(LEGACY_ORGANIZATION_RECORD_VERIFIED_FIELD) is True
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


def _master_records_recording(record: Mapping[str, Any] | None) -> dict[str, Any]:
    """Report downstream Master Records recording; it never gates readiness."""
    body: dict[str, Any] = {
        "recorder_role": "DOWNSTREAM_RELEASED_BATCH_RECEIPT_RECORDING",
        "gates_readiness": False,
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
    if record is None:
        body["status"] = "NOT_SUPPLIED"
        return body
    recorded = _organization_record_exists(record)
    reconstructable = str(record.get("reconstructability_status", "")).upper() == "PASS"
    if recorded and reconstructable:
        body["status"] = "RECORDED"
        return body
    failure_code = (
        ORGANIZATION_RECORD_NOT_VERIFIED if not recorded else "RECONSTRUCTABILITY_NOT_PASS"
    )
    body.update(
        {
            "status": "NOT_RECORDED",
            "disposition": "NON_ALLOW_RECORDING_ONLY",
            "failure_code": failure_code,
            "failed_predicate": (
                "MASTER_RECORDS_RECORDED_RELEASED_BATCH_RECEIPT"
                if not recorded
                else "MASTER_RECORDS_RECONSTRUCTION_PASS"
            ),
            "required_evidence_or_repair": (
                "Optional: re-submit the released organization batch receipt to Master "
                "Records and supply its recording/reconstruction result. Readiness does not "
                "wait for it."
            ),
            "retry_entrypoint": "stegverse.activation_evidence.evaluate_activation_evidence",
            "owning_existing_goal": OWNING_EXISTING_GOAL,
            "next_attempt": "OPTIONAL_DOWNSTREAM_RECORDING_RETRY_NON_BLOCKING",
        }
    )
    return body


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
    evidence = _normalize_evidence(evidence)
    missing = [name for name in _REQUIRED_EVIDENCE if not isinstance(evidence.get(name), Mapping)]
    if missing:
        raise ActivationEvidenceError(
            f"missing activation evidence: {', '.join(missing)}"
        )

    normalized = {name: dict(evidence[name]) for name in _REQUIRED_EVIDENCE}
    for name in _OPTIONAL_EVIDENCE:
        if name in evidence:
            if not isinstance(evidence[name], Mapping):
                raise ActivationEvidenceError(f"{name} must be an object when supplied")
            normalized[name] = dict(evidence[name])
    for name, record in normalized.items():
        _require_non_authorizing(name, record)

    blockers: list[str] = []
    sdk = normalized["sdk_validation"]
    site = normalized["site_validation"]
    collection = normalized["canonical_collection"]
    provider = normalized["provider_verification"]

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
        ORGANIZATION_RECORD_CLAIM_FIELD: False,
        "blockers": blockers,
        "master_records_recording": _master_records_recording(
            normalized.get(ORGANIZATION_RECORD_EVIDENCE_KEY)
        ),
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
        )
    ):
        raise ActivationEvidenceError("activation evidence attempted escalation")
    # Packets written before the migration carry the legacy claim field instead.
    claim_field = (
        ORGANIZATION_RECORD_CLAIM_FIELD
        if ORGANIZATION_RECORD_CLAIM_FIELD in packet
        else LEGACY_ORGANIZATION_RECORD_CLAIM_FIELD
    )
    if packet.get(claim_field) is not False:
        raise ActivationEvidenceError("activation evidence attempted escalation")
    if ORGANIZATION_RECORD_CLAIM_FIELD in packet and LEGACY_ORGANIZATION_RECORD_CLAIM_FIELD in packet:
        raise ActivationEvidenceError("activation evidence carries both claim field names")
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
