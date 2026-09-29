"""Transport-neutral governed-vs-recursive LLM comparison contracts.

This module prepares and validates comparison intent and returned telemetry. It
does not execute an LLM provider, a micro-node runtime, or a core-node runtime,
and it does not grant execution authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Any, Dict, List, Mapping, Optional

SCHEMA_VERSION = "1.2.0"
EVIDENCE_CLASSES = {"MEASURED", "CONFIGURED", "DERIVED", "UNAVAILABLE"}
ROUTE_KINDS = {"STEGVERSE_GOVERNED", "EXTERNAL_RECURSIVE"}

DELTA_BASELINE_KIND = "STEGVERSE_GOVERNED"
DELTA_CANDIDATE_KIND = "EXTERNAL_RECURSIVE"
DELTA_SEMANTICS = "external_recursive_minus_stegverse_governed"
DELTAS_OMITTED_MULTIPLE_BASELINES = "MULTIPLE_BASELINE_ROUTES_NO_SINGLE_PAIRWISE_DELTA"
DELTAS_OMITTED_MULTIPLE_CANDIDATES = "MULTIPLE_CANDIDATE_ROUTES_NO_SINGLE_PAIRWISE_DELTA"


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


@dataclass(frozen=True)
class RouteResult:
    route_id: str
    task_identity: str
    output_sha256: str
    metrics: Mapping[str, Mapping[str, Any]]
    admissibility_result: str
    receipt_refs: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def validate(self, request: ComparisonRequest) -> None:
        route_ids = {route.route_id for route in request.routes}
        if self.route_id not in route_ids:
            raise ComparisonValidationError(f"unknown route_id: {self.route_id}")
        if self.task_identity != request.task_identity:
            raise ComparisonValidationError("route result changed task identity")
        if len(self.output_sha256) != 64:
            raise ComparisonValidationError("output_sha256 must be a SHA-256 hex digest")
        validate_metric_map(self.metrics)
        missing = set(request.metrics_requested) - set(self.metrics)
        if missing:
            raise ComparisonValidationError(
                f"route result missing requested metrics: {sorted(missing)}"
            )


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


def _metric_value(raw: Mapping[str, Any]) -> MetricValue:
    return MetricValue(
        raw.get("value"),
        str(raw.get("unit", "")),
        str(raw.get("evidence_class", "")),
        raw.get("source_ref"),
    )


def _pairwise_deltas(
    request: ComparisonRequest,
    baseline_result: RouteResult,
    candidate_result: RouteResult,
) -> Dict[str, Dict[str, Any]]:
    """Return candidate-minus-baseline deltas for one explicitly named pair."""

    deltas: Dict[str, Dict[str, Any]] = {}
    for metric_name in request.metrics_requested:
        left = _metric_value(candidate_result.metrics[metric_name])
        right = _metric_value(baseline_result.metrics[metric_name])
        unit = left.unit if left.unit == right.unit else ""
        if not unit:
            delta = MetricValue(None, "", "UNAVAILABLE", None)
        else:
            delta = calculate_delta(left, right, unit=unit)
        deltas[metric_name] = asdict(delta)
    return deltas


def build_comparison_receipt(
    request: ComparisonRequest,
    results: List[RouteResult],
) -> Dict[str, Any]:
    """Validate route results and create a reconstructable comparison receipt."""

    request.validate()
    if len(results) != len(request.routes):
        raise ComparisonValidationError("one result is required for every route")
    seen = set()
    for result in results:
        result.validate(request)
        if result.route_id in seen:
            raise ComparisonValidationError("duplicate route result")
        seen.add(result.route_id)

    by_id = {result.route_id: result for result in results}
    baselines = [r for r in request.routes if r.route_kind == DELTA_BASELINE_KIND]
    candidates = [r for r in request.routes if r.route_kind == DELTA_CANDIDATE_KIND]

    # Every candidate route gets its own scoped delta against the single
    # baseline. Sorted by route_id so a cosmetic reordering of request.routes
    # cannot change what this receipt says.
    route_deltas: List[Dict[str, Any]] = []
    if len(baselines) == 1:
        baseline_result = by_id[baselines[0].route_id]
        for candidate in sorted(candidates, key=lambda route: route.route_id):
            route_deltas.append(
                {
                    "baseline_route_id": baselines[0].route_id,
                    "candidate_route_id": candidate.route_id,
                    "delta_semantics": DELTA_SEMANTICS,
                    "deltas": _pairwise_deltas(
                        request, baseline_result, by_id[candidate.route_id]
                    ),
                }
            )

    # A single top-level `deltas` map can only mean one thing when exactly one
    # baseline and one candidate exist. With more of either there is no
    # privileged pair, so it is omitted with a reason rather than filled from
    # whichever route happened to be listed first.
    deltas: Dict[str, Dict[str, Any]] = {}
    delta_scope: Optional[Dict[str, str]] = None
    deltas_omitted_reason: Optional[str] = None
    if len(baselines) != 1:
        deltas_omitted_reason = DELTAS_OMITTED_MULTIPLE_BASELINES
    elif len(candidates) != 1:
        deltas_omitted_reason = DELTAS_OMITTED_MULTIPLE_CANDIDATES
    else:
        deltas = route_deltas[0]["deltas"]
        delta_scope = {
            "baseline_route_id": route_deltas[0]["baseline_route_id"],
            "candidate_route_id": route_deltas[0]["candidate_route_id"],
        }

    request_package = build_comparison_package(request)
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "comparison_id": request.comparison_id,
        "request_package_sha256": request_package["package_sha256"],
        "task_identity": request.task_identity,
        "route_results": [
            asdict(result)
            for result in sorted(results, key=lambda item: item.route_id)
        ],
        "delta_semantics": DELTA_SEMANTICS,
        "deltas": deltas,
        "delta_scope": delta_scope,
        "deltas_omitted_reason": deltas_omitted_reason,
        "route_deltas": route_deltas,
        "baseline_route_count": len(baselines),
        "candidate_route_count": len(candidates),
        "claim_boundary": (
            "Measured deltas compare only like-for-like task results. "
            "No delta establishes universal superiority or avoided-consequence cost."
        ),
        "delta_boundary": (
            "Every delta names the two routes it was measured between. "
            "An unscoped delta across more than two routes is not reported."
        ),
        "reconstructable": True,
    }
    receipt["receipt_sha256"] = stable_hash(receipt)
    return receipt


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
