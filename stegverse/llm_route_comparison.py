"""Transport-neutral governed-vs-recursive LLM comparison contracts.

This module prepares and validates comparison intent. It does not execute an
LLM provider, a micro-node runtime, or a core-node runtime, and it does not
grant execution authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_VERSION = "1.0.0"
EVIDENCE_CLASSES = {"MEASURED", "CONFIGURED", "DERIVED", "UNAVAILABLE"}
ROUTE_KINDS = {"STEGVERSE_GOVERNED", "EXTERNAL_RECURSIVE"}


class ComparisonValidationError(ValueError):
    """Raised when a comparison package violates a required invariant."""


@dataclass(frozen=True)
class MetricValue:
    value: Optional[str]
    unit: str
    evidence_class: str
    source_ref: Optional[str] = None

    def validate(self) -> None:
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise ComparisonValidationError(
                f"unsupported evidence_class: {self.evidence_class}"
            )
        if self.evidence_class == "UNAVAILABLE":
            if self.value is not None:
                raise ComparisonValidationError(
                    "UNAVAILABLE metrics must use value=None"
                )
            return
        if self.value is None:
            raise ComparisonValidationError(
                f"{self.evidence_class} metrics require a value"
            )
        try:
            Decimal(self.value)
        except (InvalidOperation, TypeError) as exc:
            raise ComparisonValidationError(
                f"metric value must be decimal-compatible: {self.value!r}"
            ) from exc


@dataclass(frozen=True)
class ComparisonRoute:
    route_id: str
    route_kind: str
    provider: str
    model: str
    execution_target: str
    governance_profile: str
    recursion_enabled: bool
    telemetry_required: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.route_id.strip():
            raise ComparisonValidationError("route_id is required")
        if self.route_kind not in ROUTE_KINDS:
            raise ComparisonValidationError(
                f"unsupported route_kind: {self.route_kind}"
            )
        if not self.execution_target.strip():
            raise ComparisonValidationError("execution_target is required")


@dataclass(frozen=True)
class ComparisonRequest:
    comparison_id: str
    normalized_input: Mapping[str, Any]
    task_identity: str
    output_requirements: Mapping[str, Any]
    routes: List[ComparisonRoute]
    metrics_requested: List[str]
    claim_boundary: str = (
        "SDK preparation is not runtime execution, authority, or proof of superiority."
    )

    def validate(self) -> None:
        if not self.comparison_id.strip():
            raise ComparisonValidationError("comparison_id is required")
        if not self.task_identity.strip():
            raise ComparisonValidationError("task_identity is required")
        if len(self.routes) < 2:
            raise ComparisonValidationError("at least two routes are required")
        for route in self.routes:
            route.validate()
        kinds = {route.route_kind for route in self.routes}
        if "STEGVERSE_GOVERNED" not in kinds:
            raise ComparisonValidationError("a STEGVERSE_GOVERNED route is required")
        if "EXTERNAL_RECURSIVE" not in kinds:
            raise ComparisonValidationError("an EXTERNAL_RECURSIVE route is required")
        route_ids = [route.route_id for route in self.routes]
        if len(route_ids) != len(set(route_ids)):
            raise ComparisonValidationError("route_id values must be unique")
        if not self.metrics_requested:
            raise ComparisonValidationError("metrics_requested cannot be empty")


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(value: Mapping[str, Any]) -> str:
    """Return a deterministic SHA-256 over canonical JSON."""

    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def build_comparison_package(request: ComparisonRequest) -> Dict[str, Any]:
    """Validate and serialize a transport-neutral comparison package."""

    request.validate()
    payload = {
        "schema_version": SCHEMA_VERSION,
        "comparison_id": request.comparison_id,
        "task_identity": request.task_identity,
        "normalized_input": dict(request.normalized_input),
        "output_requirements": dict(request.output_requirements),
        "routes": [asdict(route) for route in request.routes],
        "metrics_requested": list(request.metrics_requested),
        "claim_boundary": request.claim_boundary,
        "invariants": {
            "sdk_preparation_is_execution": False,
            "sdk_preparation_is_authority": False,
            "route_outputs_must_share_task_identity": True,
            "configured_values_must_not_be_reported_as_measured": True,
        },
    }
    payload["package_sha256"] = stable_hash(payload)
    return payload


def validate_metric_map(metrics: Mapping[str, Mapping[str, Any]]) -> None:
    """Validate a returned route metric map without trusting its producer."""

    for name, raw in metrics.items():
        if not name.strip():
            raise ComparisonValidationError("metric names cannot be empty")
        metric = MetricValue(
            value=raw.get("value"),
            unit=str(raw.get("unit", "")),
            evidence_class=str(raw.get("evidence_class", "")),
            source_ref=raw.get("source_ref"),
        )
        metric.validate()


def calculate_delta(
    baseline: MetricValue,
    candidate: MetricValue,
    *,
    unit: str,
) -> MetricValue:
    """Calculate baseline minus candidate from measured numeric values only."""

    baseline.validate()
    candidate.validate()
    if baseline.evidence_class != "MEASURED" or candidate.evidence_class != "MEASURED":
        return MetricValue(None, unit, "UNAVAILABLE", None)
    if baseline.unit != unit or candidate.unit != unit:
        raise ComparisonValidationError("delta metrics must share the requested unit")
    value = Decimal(baseline.value or "0") - Decimal(candidate.value or "0")
    return MetricValue(format(value, "f"), unit, "DERIVED", "baseline-minus-candidate")


def required_default_metrics() -> List[str]:
    """Return the initial common telemetry contract for both routes."""

    return [
        "total_cost_usd",
        "latency_ms",
        "model_calls",
        "input_tokens",
        "output_tokens",
        "tool_calls",
        "retries",
        "node_or_cell_activations",
        "receipt_count",
        "reconstructable",
    ]
