"""Downstream Master Records recording and reconstruction verification for universal-entry events.

Local continuation-event creation does not create an organization record. This module
sends a released, validated chain to an external Master-Records service for downstream
recording, requires an identity-matched recording receipt, and independently verifies
the reconstructed event chain returned by the service before a caller may describe the
chain as recorded there.

The Organization owns custody of its runtime history in its own ledger; Master Records
only records released organization batch receipts for cross-organization
reconstruction. Interlock/InTr admits transitions. Nothing in this module admits, gates
or authorizes anything, and callers must treat its failures as non-gating
(LLMA-DECLARED-PATH-CONFORMANCE-368).

Naming migration (MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002): writers emit only the
new organization-record names. Readers also accept the ``LEGACY_*`` names below so
already-deployed peers keep working.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Mapping, Sequence

from .universal_entry_events import UniversalEntryEventError, validate_event_chain


ORGANIZATION_RECORD_REQUEST_SCHEMA = "stegverse.universal_entry_organization_record_request.v0.1"
ORGANIZATION_RECORD_RECEIPT_SCHEMA = "stegverse.master_records_organization_record_receipt.v0.1"
RECONSTRUCTION_SCHEMA = "stegverse.master_records_reconstruction.v0.1"

# Legacy names accepted by readers only (MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002).
LEGACY_ORGANIZATION_RECORD_RECEIPT_SCHEMA = "stegverse.master_records_custody_receipt.v0.1"
LEGACY_RECEIPT_RECORDED_FIELD = "custody_recorded"

_RECEIPT_SCHEMAS = frozenset(
    {ORGANIZATION_RECORD_RECEIPT_SCHEMA, LEGACY_ORGANIZATION_RECORD_RECEIPT_SCHEMA}
)


class MasterRecordsOrganizationRecordError(RuntimeError):
    """Raised when organization-record or reconstruction evidence violates the contract."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


def build_organization_record_request(events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Build the request that asks Master Records to keep the chain as an organization record."""
    try:
        normalized = validate_event_chain(events)
    except UniversalEntryEventError as exc:
        raise MasterRecordsOrganizationRecordError(
            f"organization-record request event chain invalid: {exc}"
        ) from exc
    if not normalized:
        raise MasterRecordsOrganizationRecordError("continuation event chain is empty")
    first = normalized[0]
    last = normalized[-1]
    body = {
        "schema": ORGANIZATION_RECORD_REQUEST_SCHEMA,
        "session_id": first["session_id"],
        "message_id": first["message_id"],
        "transition_id": first["transition_id"],
        "run_id": first["run_id"],
        "first_event_id": first["event_id"],
        "last_event_id": last["event_id"],
        "event_count": len(normalized),
        "events_digest": _digest(normalized),
        "events": normalized,
        "authorizing": False,
        "execution_authority_granted": False,
        "admissibility_determined": False,
        "record_requested": True,
    }
    body["submission_id"] = _digest(body)
    return body


def _organization_record_recorded(receipt: Mapping[str, Any]) -> bool:
    if "organization_record_recorded" in receipt:
        return receipt.get("organization_record_recorded") is True
    return receipt.get(LEGACY_RECEIPT_RECORDED_FIELD) is True


def validate_organization_record_receipt(
    submission: Mapping[str, Any], receipt: Mapping[str, Any]
) -> dict[str, Any]:
    if receipt.get("schema") not in _RECEIPT_SCHEMAS:
        raise MasterRecordsOrganizationRecordError(
            "unsupported organization-record receipt schema"
        )
    expected_identity = {
        "submission_id": submission.get("submission_id"),
        "session_id": submission.get("session_id"),
        "message_id": submission.get("message_id"),
        "transition_id": submission.get("transition_id"),
        "run_id": submission.get("run_id"),
        "first_event_id": submission.get("first_event_id"),
        "last_event_id": submission.get("last_event_id"),
        "event_count": submission.get("event_count"),
        "events_digest": submission.get("events_digest"),
    }
    mismatched = [
        key for key, value in expected_identity.items() if receipt.get(key) != value
    ]
    if mismatched:
        raise MasterRecordsOrganizationRecordError(
            "organization-record receipt identity mismatch: " + ", ".join(mismatched)
        )
    if not _organization_record_recorded(receipt):
        raise MasterRecordsOrganizationRecordError(
            "organization-record receipt does not record the organization record"
        )
    if receipt.get("reconstruction_available") is not True:
        raise MasterRecordsOrganizationRecordError(
            "organization-record receipt lacks reconstruction availability"
        )
    if receipt.get("authorizing") is not False:
        raise MasterRecordsOrganizationRecordError(
            "organization-record receipt attempted authority escalation"
        )
    if receipt.get("execution_authority_granted") is not False:
        raise MasterRecordsOrganizationRecordError(
            "organization-record receipt attempted execution escalation"
        )
    if receipt.get("admissibility_determined") is not False:
        raise MasterRecordsOrganizationRecordError(
            "organization-record receipt attempted admissibility escalation"
        )
    normalized = dict(receipt)
    receipt_id = normalized.pop("receipt_id", None)
    if receipt_id != _digest(normalized):
        raise MasterRecordsOrganizationRecordError("organization-record receipt digest mismatch")
    return dict(receipt)


def verify_reconstruction(
    submission: Mapping[str, Any], reconstruction: Mapping[str, Any]
) -> dict[str, Any]:
    if reconstruction.get("schema") != RECONSTRUCTION_SCHEMA:
        raise MasterRecordsOrganizationRecordError("unsupported reconstruction schema")
    if reconstruction.get("submission_id") != submission.get("submission_id"):
        raise MasterRecordsOrganizationRecordError("reconstruction request identity mismatch")
    events = reconstruction.get("events")
    if not isinstance(events, list):
        raise MasterRecordsOrganizationRecordError("reconstruction events must be a list")
    try:
        normalized = validate_event_chain(events)
    except UniversalEntryEventError as exc:
        raise MasterRecordsOrganizationRecordError(
            f"reconstruction event chain invalid: {exc}"
        ) from exc
    if len(normalized) != submission.get("event_count"):
        raise MasterRecordsOrganizationRecordError("reconstruction event count mismatch")
    if _digest(normalized) != submission.get("events_digest"):
        raise MasterRecordsOrganizationRecordError("reconstruction event digest mismatch")
    if normalized[0]["event_id"] != submission.get("first_event_id"):
        raise MasterRecordsOrganizationRecordError("reconstruction first event mismatch")
    if normalized[-1]["event_id"] != submission.get("last_event_id"):
        raise MasterRecordsOrganizationRecordError("reconstruction last event mismatch")
    if reconstruction.get("reconstructability_status") != "PASS":
        raise MasterRecordsOrganizationRecordError("reconstructability did not pass")
    if reconstruction.get("authorizing") is not False:
        raise MasterRecordsOrganizationRecordError("reconstruction attempted authority escalation")
    return {
        "status": "PASS",
        "submission_id": submission["submission_id"],
        "event_count": len(normalized),
        "first_event_id": normalized[0]["event_id"],
        "last_event_id": normalized[-1]["event_id"],
        "events_digest": submission["events_digest"],
        "organization_record_installed": True,
        "authorizing": False,
        "execution_authority_granted": False,
        "admissibility_determined": False,
    }


@dataclass(frozen=True)
class MasterRecordsOrganizationRecordClient:
    """Transport-neutral client for Master Records organization records.

    The transport callable owns authentication and endpoint configuration and must
    return a mapping. Browser entry adapters must never own these credentials.
    """

    submit_transport: Callable[[Mapping[str, Any]], Mapping[str, Any]]
    reconstruct_transport: Callable[[str], Mapping[str, Any]]

    def submit_and_verify(self, events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        submission = build_organization_record_request(events)
        receipt = validate_organization_record_receipt(
            submission, dict(self.submit_transport(submission))
        )
        reconstruction = dict(self.reconstruct_transport(str(receipt["receipt_id"])))
        verification = verify_reconstruction(submission, reconstruction)
        return {
            "submission": submission,
            "organization_record_receipt": receipt,
            "reconstruction": reconstruction,
            "verification": verification,
        }


__all__ = [
    "LEGACY_ORGANIZATION_RECORD_RECEIPT_SCHEMA",
    "LEGACY_RECEIPT_RECORDED_FIELD",
    "ORGANIZATION_RECORD_RECEIPT_SCHEMA",
    "ORGANIZATION_RECORD_REQUEST_SCHEMA",
    "RECONSTRUCTION_SCHEMA",
    "MasterRecordsOrganizationRecordClient",
    "MasterRecordsOrganizationRecordError",
    "build_organization_record_request",
    "validate_organization_record_receipt",
    "verify_reconstruction",
]
