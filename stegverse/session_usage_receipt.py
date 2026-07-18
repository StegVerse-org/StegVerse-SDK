"""Build deterministic, non-custodial receipts from SDK session usage aggregation."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Iterable, Mapping

from .transition_usage import UsageValidationError, aggregate_session_usage


def _canonical(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Mapping[str, Any]) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def build_session_usage_receipt(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    records = list(events)
    if not records:
        raise UsageValidationError("at least one usage event is required")
    event_hashes: list[str] = []
    for event in records:
        event_hash = str(event.get("event_sha256", ""))
        if len(event_hash) != 64 or any(ch not in "0123456789abcdef" for ch in event_hash):
            raise UsageValidationError("every source event requires a valid event_sha256")
        body = dict(event)
        body.pop("event_sha256", None)
        if _hash(body) != event_hash:
            raise UsageValidationError("source event hash mismatch")
        event_hashes.append(event_hash)
    aggregation = aggregate_session_usage(records)
    receipt: dict[str, Any] = {
        "schema_version": "1.0.0",
        "receipt_type": "SDK_SESSION_USAGE_AGGREGATION",
        "session_id": aggregation["session_id"],
        "aggregation_sha256": aggregation["aggregation_sha256"],
        "measurement_count_received": aggregation["measurement_count_received"],
        "measurement_count_unique": aggregation["measurement_count_unique"],
        "entry_points": aggregation["entry_points"],
        "transition_ids": aggregation["transition_ids"],
        "totals": aggregation["totals"],
        "excluded": aggregation["excluded"],
        "dedupe_semantics": aggregation["dedupe_semantics"],
        "source_event_hashes": sorted(set(event_hashes)),
        "custody_posture": "HANDOFF_READY_NOT_CUSTODIED",
        "authority_boundary": {
            "receipt_is_execution_authority": False,
            "receipt_is_admissibility": False,
            "receipt_is_master_record_custody": False,
            "aggregation_is_universal_cost_claim": False,
        },
    }
    receipt["receipt_sha256"] = _hash(receipt)
    return receipt
