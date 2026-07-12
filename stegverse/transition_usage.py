"""Cross-entry transition usage events and session aggregation contracts.

Usage reporting is descriptive evidence. It does not grant execution authority,
admissibility, standing, or publication rights.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional

USAGE_SCHEMA_VERSION = "1.0.0"
EVIDENCE_CLASSES = {"MEASURED", "CONFIGURED", "DERIVED", "UNAVAILABLE"}


class UsageValidationError(ValueError):
    """Raised when a usage event or aggregation violates continuity rules."""


@dataclass(frozen=True)
class UsageMetric:
    value: Optional[str]
    unit: str
    evidence_class: str
    source_ref: Optional[str] = None

    def validate(self) -> None:
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise UsageValidationError(f"unsupported evidence_class: {self.evidence_class}")
        if self.evidence_class == "UNAVAILABLE":
            if self.value is not None:
                raise UsageValidationError("UNAVAILABLE metrics require value=None")
            return
        if self.value is None:
            raise UsageValidationError(f"{self.evidence_class} metrics require a value")
        try:
            Decimal(self.value)
        except (InvalidOperation, TypeError) as exc:
            raise UsageValidationError(
                f"usage metric must be decimal-compatible: {self.value!r}"
            ) from exc


@dataclass(frozen=True)
class TransitionUsageEvent:
    measurement_id: str
    session_id: str
    transition_id: str
    entry_point: str
    entry_point_role: str
    interaction_type: str
    metric_owner: str
    measurement_source: str
    evidence_class: str
    metrics: Mapping[str, UsageMetric]
    occurred_at: str
    origin_entry_point: Optional[str] = None
    parent_transition_id: Optional[str] = None
    route_kind: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    receipt_refs: List[str] = field(default_factory=list)

    def validate(self) -> None:
        required = {
            "measurement_id": self.measurement_id,
            "session_id": self.session_id,
            "transition_id": self.transition_id,
            "entry_point": self.entry_point,
            "entry_point_role": self.entry_point_role,
            "interaction_type": self.interaction_type,
            "metric_owner": self.metric_owner,
            "measurement_source": self.measurement_source,
            "occurred_at": self.occurred_at,
        }
        for label, value in required.items():
            if not value.strip():
                raise UsageValidationError(f"{label} is required")
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise UsageValidationError(f"unsupported evidence_class: {self.evidence_class}")
        if not self.metrics:
            raise UsageValidationError("metrics cannot be empty")
        for name, metric in self.metrics.items():
            if not name.strip():
                raise UsageValidationError("metric names cannot be empty")
            metric.validate()
        try:
            datetime.fromisoformat(self.occurred_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise UsageValidationError("occurred_at must be ISO-8601") from exc
        if len(self.receipt_refs) != len(set(self.receipt_refs)):
            raise UsageValidationError("receipt_refs must be unique")


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_usage_hash(value: Mapping[str, Any]) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def build_usage_event(event: TransitionUsageEvent) -> Dict[str, Any]:
    """Validate and serialize one cross-entry transition usage event."""

    event.validate()
    payload: Dict[str, Any] = {
        "schema_version": USAGE_SCHEMA_VERSION,
        "event_type": "TRANSITION_USAGE_RECORDED",
        "measurement_id": event.measurement_id,
        "session_id": event.session_id,
        "transition_id": event.transition_id,
        "parent_transition_id": event.parent_transition_id,
        "origin_entry_point": event.origin_entry_point or event.entry_point,
        "entry_point": event.entry_point,
        "entry_point_role": event.entry_point_role,
        "interaction_type": event.interaction_type,
        "metric_owner": event.metric_owner,
        "measurement_source": event.measurement_source,
        "route_kind": event.route_kind,
        "provider": event.provider,
        "model": event.model,
        "evidence_class": event.evidence_class,
        "metrics": {name: asdict(metric) for name, metric in event.metrics.items()},
        "receipt_refs": list(event.receipt_refs),
        "occurred_at": event.occurred_at,
        "invariants": {
            "usage_event_is_authority": False,
            "usage_event_is_admissibility": False,
            "entry_point_display_is_execution": False,
            "session_identity_preserved": True,
            "transition_lineage_preserved": True,
            "measurement_owner_is_unique": True,
        },
    }
    payload["event_sha256"] = stable_usage_hash(payload)
    return payload


def aggregate_session_usage(events: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Deduplicate usage events and aggregate numeric metrics for one session.

    Aggregation groups only metrics with matching names, units, and evidence classes.
    Mixed or unavailable evidence remains visible but is not silently summed.
    """

    records = list(events)
    if not records:
        raise UsageValidationError("at least one usage event is required")

    session_ids = {str(item.get("session_id", "")) for item in records}
    if len(session_ids) != 1 or "" in session_ids:
        raise UsageValidationError("all usage events must share one session_id")

    seen_measurements = set()
    unique_records = []
    for item in records:
        measurement_id = str(item.get("measurement_id", ""))
        metric_owner = str(item.get("metric_owner", ""))
        dedupe_key = (measurement_id, metric_owner)
        if not measurement_id or not metric_owner:
            raise UsageValidationError("measurement_id and metric_owner are required")
        if dedupe_key in seen_measurements:
            continue
        seen_measurements.add(dedupe_key)
        unique_records.append(item)

    grouped: Dict[tuple[str, str, str], Decimal] = {}
    excluded: List[Dict[str, str]] = []
    for item in unique_records:
        metrics = item.get("metrics", {})
        if not isinstance(metrics, Mapping):
            raise UsageValidationError("metrics must be a mapping")
        for name, raw in metrics.items():
            if not isinstance(raw, Mapping):
                raise UsageValidationError("metric values must be mappings")
            evidence_class = str(raw.get("evidence_class", ""))
            unit = str(raw.get("unit", ""))
            value = raw.get("value")
            if evidence_class == "UNAVAILABLE" or value is None:
                excluded.append({"metric": str(name), "reason": "UNAVAILABLE"})
                continue
            try:
                amount = Decimal(str(value))
            except InvalidOperation as exc:
                raise UsageValidationError(f"metric {name} is not numeric") from exc
            key = (str(name), unit, evidence_class)
            grouped[key] = grouped.get(key, Decimal("0")) + amount

    totals = [
        {
            "metric": metric,
            "unit": unit,
            "evidence_class": evidence_class,
            "value": format(value, "f"),
        }
        for (metric, unit, evidence_class), value in sorted(grouped.items())
    ]

    result: Dict[str, Any] = {
        "schema_version": USAGE_SCHEMA_VERSION,
        "session_id": next(iter(session_ids)),
        "measurement_count_received": len(records),
        "measurement_count_unique": len(unique_records),
        "entry_points": sorted({str(item.get("entry_point", "")) for item in unique_records}),
        "transition_ids": sorted({str(item.get("transition_id", "")) for item in unique_records}),
        "totals": totals,
        "excluded": excluded,
        "dedupe_semantics": "measurement_id_plus_metric_owner",
        "claim_boundary": (
            "Aggregated usage is descriptive evidence and does not establish authority, "
            "admissibility, standing, or universal cost superiority."
        ),
    }
    result["aggregation_sha256"] = stable_usage_hash(result)
    return result


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
