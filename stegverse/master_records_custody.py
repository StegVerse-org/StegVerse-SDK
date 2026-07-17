"""Authenticated custody submission and reconstruction verification for universal-entry events.

Local continuation-event creation is not custody. This module submits a validated
chain to an external Master-Records service, requires an identity-matched custody
receipt, and independently verifies the reconstructed event chain returned by the
service before a caller may describe the chain as recorded.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Mapping, Sequence

from .universal_entry_events import UniversalEntryEventError, validate_event_chain


class MasterRecordsCustodyError(RuntimeError):
    """Raised when custody or reconstruction evidence violates the contract."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


def build_custody_submission(events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    try:
        normalized = validate_event_chain(events)
    except UniversalEntryEventError as exc:
        raise MasterRecordsCustodyError(f"custody submission event chain invalid: {exc}") from exc
    if not normalized:
        raise MasterRecordsCustodyError("continuation event chain is empty")
    first = normalized[0]
    last = normalized[-1]
    body = {
        "schema": "stegverse.universal_entry_custody_submission.v0.1",
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
        "custody_requested": True,
    }
    body["submission_id"] = _digest(body)
    return body


def validate_custody_receipt(
    submission: Mapping[str, Any], receipt: Mapping[str, Any]
) -> dict[str, Any]:
    if receipt.get("schema") != "stegverse.master_records_custody_receipt.v0.1":
        raise MasterRecordsCustodyError("unsupported custody receipt schema")
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
        raise MasterRecordsCustodyError(
            "custody receipt identity mismatch: " + ", ".join(mismatched)
        )
    if receipt.get("custody_recorded") is not True:
        raise MasterRecordsCustodyError("custody receipt does not record custody")
    if receipt.get("reconstruction_available") is not True:
        raise MasterRecordsCustodyError("custody receipt lacks reconstruction availability")
    if receipt.get("authorizing") is not False:
        raise MasterRecordsCustodyError("custody receipt attempted authority escalation")
    if receipt.get("execution_authority_granted") is not False:
        raise MasterRecordsCustodyError("custody receipt attempted execution escalation")
    if receipt.get("admissibility_determined") is not False:
        raise MasterRecordsCustodyError("custody receipt attempted admissibility escalation")
    normalized = dict(receipt)
    receipt_id = normalized.pop("receipt_id", None)
    if receipt_id != _digest(normalized):
        raise MasterRecordsCustodyError("custody receipt digest mismatch")
    return dict(receipt)


def verify_reconstruction(
    submission: Mapping[str, Any], reconstruction: Mapping[str, Any]
) -> dict[str, Any]:
    if reconstruction.get("schema") != "stegverse.master_records_reconstruction.v0.1":
        raise MasterRecordsCustodyError("unsupported reconstruction schema")
    if reconstruction.get("submission_id") != submission.get("submission_id"):
        raise MasterRecordsCustodyError("reconstruction submission identity mismatch")
    events = reconstruction.get("events")
    if not isinstance(events, list):
        raise MasterRecordsCustodyError("reconstruction events must be a list")
    try:
        normalized = validate_event_chain(events)
    except UniversalEntryEventError as exc:
        raise MasterRecordsCustodyError(f"reconstruction event chain invalid: {exc}") from exc
    if len(normalized) != submission.get("event_count"):
        raise MasterRecordsCustodyError("reconstruction event count mismatch")
    if _digest(normalized) != submission.get("events_digest"):
        raise MasterRecordsCustodyError("reconstruction event digest mismatch")
    if normalized[0]["event_id"] != submission.get("first_event_id"):
        raise MasterRecordsCustodyError("reconstruction first event mismatch")
    if normalized[-1]["event_id"] != submission.get("last_event_id"):
        raise MasterRecordsCustodyError("reconstruction last event mismatch")
    if reconstruction.get("reconstructability_status") != "PASS":
        raise MasterRecordsCustodyError("reconstructability did not pass")
    if reconstruction.get("authorizing") is not False:
        raise MasterRecordsCustodyError("reconstruction attempted authority escalation")
    return {
        "status": "PASS",
        "submission_id": submission["submission_id"],
        "event_count": len(normalized),
        "first_event_id": normalized[0]["event_id"],
        "last_event_id": normalized[-1]["event_id"],
        "events_digest": submission["events_digest"],
        "custody_verified": True,
        "master_records_installed": True,
        "authorizing": False,
        "execution_authority_granted": False,
        "admissibility_determined": False,
    }


@dataclass(frozen=True)
class MasterRecordsCustodyClient:
    """Transport-neutral custody client.

    The transport callable owns authentication and endpoint configuration and must
    return a mapping. Browser entry adapters must never own these credentials.
    """

    submit_transport: Callable[[Mapping[str, Any]], Mapping[str, Any]]
    reconstruct_transport: Callable[[str], Mapping[str, Any]]

    def submit_and_verify(self, events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        submission = build_custody_submission(events)
        receipt = validate_custody_receipt(
            submission, dict(self.submit_transport(submission))
        )
        reconstruction = dict(self.reconstruct_transport(str(receipt["receipt_id"])))
        verification = verify_reconstruction(submission, reconstruction)
        return {
            "submission": submission,
            "custody_receipt": receipt,
            "reconstruction": reconstruction,
            "verification": verification,
        }
