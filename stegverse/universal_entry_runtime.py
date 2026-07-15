"""Canonical universal-entry execution wrapper with continuation events."""
from __future__ import annotations

from typing import Any, Mapping

from .universal_entry import CapabilityRegistry
from .universal_entry_dispatch import HandlerRegistry, LaneHandler, dispatch_universal_entry
from .universal_entry_events import build_dispatch_event_chain, validate_event_chain


def run_universal_entry(
    envelope: Mapping[str, Any],
    capability_registry: CapabilityRegistry | Mapping[str, Any],
    handler_registry: HandlerRegistry | Mapping[str, LaneHandler],
    *,
    initial_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Dispatch an entry and attach a validated, non-custodial event chain."""
    governed_return = dispatch_universal_entry(
        envelope,
        capability_registry,
        handler_registry,
        initial_context=initial_context,
    )
    events = build_dispatch_event_chain(envelope, governed_return)
    governed_return["continuation_events"] = validate_event_chain(events)
    governed_return["continuation"] = {
        "event_count": len(events),
        "first_event_id": events[0]["event_id"] if events else None,
        "last_event_id": events[-1]["event_id"] if events else None,
        "custody_submitted": False,
        "master_records_installed": False,
    }
    return governed_return
