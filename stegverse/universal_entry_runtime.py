"""Canonical universal-entry execution wrapper with continuation and custody."""
from __future__ import annotations

from typing import Any, Mapping

from .master_records_custody import MasterRecordsCustodyClient
from .universal_entry import CapabilityRegistry
from .universal_entry_dispatch import HandlerRegistry, LaneHandler, dispatch_universal_entry
from .universal_entry_events import build_dispatch_event_chain, validate_event_chain


def run_universal_entry(
    envelope: Mapping[str, Any],
    capability_registry: CapabilityRegistry | Mapping[str, Any],
    handler_registry: HandlerRegistry | Mapping[str, LaneHandler],
    *,
    initial_context: Mapping[str, Any] | None = None,
    custody_client: MasterRecordsCustodyClient | None = None,
) -> dict[str, Any]:
    """Dispatch an entry, attach events, and optionally verify external custody.

    Without a custody client the result remains explicitly non-custodial. When a
    client is supplied, the runtime requires an identity-matched custody receipt
    and reconstructability PASS before setting custody or installation fields.
    """
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
        "custody_submitted": False,
        "custody_verified": False,
        "master_records_installed": False,
        "reconstructability_status": "NOT_SUBMITTED",
    }

    if custody_client is not None:
        custody = custody_client.submit_and_verify(events)
        verification = custody["verification"]
        governed_return["custody"] = custody
        governed_return["continuation"].update(
            {
                "custody_submitted": True,
                "custody_verified": verification["custody_verified"],
                "master_records_installed": verification["master_records_installed"],
                "reconstructability_status": verification["status"],
                "custody_receipt_id": custody["custody_receipt"]["receipt_id"],
            }
        )
    return governed_return
