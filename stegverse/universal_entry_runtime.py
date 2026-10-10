"""Canonical universal-entry execution wrapper with continuation events.

Master Records recording of the released event chain is optional, downstream and
non-gating: a recording or reconstruction failure is reported as a six-field
non-ALLOW in ``continuation["master_records_recording"]`` and never changes the
governed return (LLMA-DECLARED-PATH-CONFORMANCE-368).
"""
from __future__ import annotations

from typing import Any, Mapping

from .master_records_http import MasterRecordsHTTPError
from .master_records_organization_record import (
    MasterRecordsOrganizationRecordClient,
    MasterRecordsOrganizationRecordError,
)
from .universal_entry import CapabilityRegistry
from .universal_entry_dispatch import HandlerRegistry, LaneHandler, dispatch_universal_entry
from .universal_entry_events import build_dispatch_event_chain, validate_event_chain

OrganizationRecordClient = MasterRecordsOrganizationRecordClient
OWNING_EXISTING_GOAL = "LLMA-DECLARED-PATH-CONFORMANCE-368"
_RECORDING_FAILURES = (
    MasterRecordsOrganizationRecordError,
    MasterRecordsHTTPError,
    OSError,
    KeyError,
    TypeError,
    ValueError,
)


def _recording_non_allow(exc: BaseException) -> dict[str, Any]:
    """Six-field non-ALLOW for a downstream Master Records recording that did not complete."""
    return {
        "status": "NOT_RECORDED",
        "disposition": "NON_ALLOW_RECORDING_ONLY",
        "gates_return": False,
        "failure_code": "MASTER_RECORDS_RECORDING_NOT_COMPLETED",
        "failed_predicate": "MASTER_RECORDS_RECORDED_AND_RECONSTRUCTED_RELEASED_EVENT_CHAIN",
        "failure_detail": f"{type(exc).__name__}: {exc}",
        "required_evidence_or_repair": (
            "Optional: re-submit the released continuation event chain to Master Records "
            "and verify its reconstruction. The governed return already stands."
        ),
        "retry_entrypoint": "stegverse.master_records_organization_record.MasterRecordsOrganizationRecordClient.submit_and_verify",
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "next_attempt": "OPTIONAL_DOWNSTREAM_RECORDING_RETRY_NON_BLOCKING",
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }


def run_universal_entry(
    envelope: Mapping[str, Any],
    capability_registry: CapabilityRegistry | Mapping[str, Any],
    handler_registry: HandlerRegistry | Mapping[str, LaneHandler],
    *,
    initial_context: Mapping[str, Any] | None = None,
    organization_record_client: MasterRecordsOrganizationRecordClient | None = None,
    custody_client: OrganizationRecordClient | None = None,
) -> dict[str, Any]:
    """Dispatch an entry, attach events, and optionally record them downstream.

    Without an organization-record client nothing is sent to Master Records. When a
    client is supplied, the released event chain is submitted after the governed
    return exists; the organization-record fields are set only for an
    identity-matched receipt with reconstructability PASS. Any recording failure is
    reported as a six-field non-ALLOW and the governed return is unchanged.

    ``custody_client`` is the deprecated name of ``organization_record_client`` and is
    accepted only so pinned callers keep working.
    """
    if custody_client is not None:
        if organization_record_client is not None:
            raise TypeError(
                "pass organization_record_client only; custody_client is its deprecated name"
            )
        organization_record_client = custody_client
    governed_return = dispatch_universal_entry(
        envelope,
        capability_registry,
        handler_registry,
        initial_context=initial_context,
    )
    events = validate_event_chain(build_dispatch_event_chain(envelope, governed_return))
    governed_return["continuation_events"] = events
    governed_return["continuation"] = {
        "event_count": len(events),
        "first_event_id": events[0]["event_id"] if events else None,
        "last_event_id": events[-1]["event_id"] if events else None,
        "record_submitted": False,
        "organization_record_installed": False,
        "reconstructability_status": "NOT_SUBMITTED",
        "master_records_recording": {
            "status": "NOT_REQUESTED",
            "gates_return": False,
            "authority_effect": "NONE_EVIDENCE_ONLY",
        },
    }

    if organization_record_client is not None:
        try:
            record = organization_record_client.submit_and_verify(events)
        except _RECORDING_FAILURES as exc:
            governed_return["continuation"].update(
                {
                    "record_submitted": True,
                    "reconstructability_status": "NOT_VERIFIED",
                    "master_records_recording": _recording_non_allow(exc),
                }
            )
            return governed_return
        verification = record["verification"]
        governed_return["organization_record"] = record
        governed_return["continuation"].update(
            {
                "record_submitted": True,
                "organization_record_installed": verification["organization_record_installed"],
                "reconstructability_status": verification["status"],
                "organization_record_receipt_id": record["organization_record_receipt"]["receipt_id"],
                "master_records_recording": {
                    "status": "RECORDED",
                    "gates_return": False,
                    "authority_effect": "NONE_EVIDENCE_ONLY",
                },
            }
        )
    return governed_return
