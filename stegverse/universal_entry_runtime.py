"""Canonical universal-entry execution wrapper with continuation and organization records."""
from __future__ import annotations

from typing import Any, Mapping

from .master_records_organization_record import MasterRecordsOrganizationRecordClient
from .universal_entry import CapabilityRegistry
from .universal_entry_dispatch import HandlerRegistry, LaneHandler, dispatch_universal_entry
from .universal_entry_events import build_dispatch_event_chain, validate_event_chain

OrganizationRecordClient = MasterRecordsOrganizationRecordClient


def run_universal_entry(
    envelope: Mapping[str, Any],
    capability_registry: CapabilityRegistry | Mapping[str, Any],
    handler_registry: HandlerRegistry | Mapping[str, LaneHandler],
    *,
    initial_context: Mapping[str, Any] | None = None,
    organization_record_client: MasterRecordsOrganizationRecordClient | None = None,
    custody_client: OrganizationRecordClient | None = None,
) -> dict[str, Any]:
    """Dispatch an entry, attach events, and optionally verify the organization record.

    Without an organization-record client the result records no organization record.
    When a client is supplied, the runtime requires an identity-matched
    organization-record receipt and reconstructability PASS before setting the
    organization-record fields.

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
    }

    if organization_record_client is not None:
        record = organization_record_client.submit_and_verify(events)
        verification = record["verification"]
        governed_return["organization_record"] = record
        governed_return["continuation"].update(
            {
                "record_submitted": True,
                "organization_record_installed": verification["organization_record_installed"],
                "reconstructability_status": verification["status"],
                "organization_record_receipt_id": record["organization_record_receipt"]["receipt_id"],
            }
        )
    return governed_return
