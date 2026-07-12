"""Paired orchestration for governed-vs-recursive comparison execution.

The orchestrator submits one immutable comparison package to two explicitly
configured route executors, validates both returned route results, and emits a
single canonical comparison receipt. Orchestration is not execution authority,
admissibility, provider standing, or proof of universal superiority.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional

import requests

from .comparison_transport import ComparisonTransportError, build_transport_envelope
from .llm_route_comparison import (
    ComparisonRequest,
    RouteResult,
    build_comparison_receipt,
    stable_hash,
)

ORCHESTRATION_SCHEMA_VERSION = "1.0.0"
RouteExecutor = Callable[[Mapping[str, Any]], Mapping[str, Any]]


class ComparisonOrchestrationError(RuntimeError):
    """Raised when paired execution cannot produce two valid route results."""


@dataclass(frozen=True)
class ExecutorTarget:
    route_id: str
    endpoint: Optional[str] = None
    executor: Optional[RouteExecutor] = None
    timeout_seconds: float = 60.0
    headers: Optional[Mapping[str, str]] = None

    def validate(self) -> None:
        configured = int(self.endpoint is not None) + int(self.executor is not None)
        if configured != 1:
            raise ComparisonOrchestrationError(
                "each target must configure exactly one of endpoint or executor"
            )
        if self.endpoint is not None and not self.endpoint.startswith(("http://", "https://")):
            raise ComparisonOrchestrationError("executor endpoint must use http:// or https://")
        if self.timeout_seconds <= 0:
            raise ComparisonOrchestrationError("timeout_seconds must be positive")


def _as_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ComparisonOrchestrationError(f"{label} must be a JSON object")
    return value


def _execute_target(target: ExecutorTarget, envelope: Mapping[str, Any]) -> Mapping[str, Any]:
    target.validate()
    if target.executor is not None:
        try:
            return _as_mapping(target.executor(envelope), "executor response")
        except ComparisonOrchestrationError:
            raise
        except Exception as exc:  # executor boundary must fail closed
            raise ComparisonOrchestrationError(
                f"executor failed for route {target.route_id}: {exc}"
            ) from exc

    assert target.endpoint is not None
    try:
        response = requests.post(
            target.endpoint,
            json=envelope,
            headers=dict(target.headers or {}),
            timeout=target.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise ComparisonOrchestrationError(
            f"transport failed for route {target.route_id}: {exc}"
        ) from exc
    except ValueError as exc:
        raise ComparisonOrchestrationError(
            f"executor returned invalid JSON for route {target.route_id}"
        ) from exc
    return _as_mapping(payload, "executor response")


def _parse_single_route_result(
    request: ComparisonRequest,
    target: ExecutorTarget,
    payload: Mapping[str, Any],
) -> RouteResult:
    if payload.get("message_type") != "LLM_ROUTE_COMPARISON_ROUTE_RESULT":
        raise ComparisonOrchestrationError(
            f"unexpected message_type for route {target.route_id}"
        )
    if payload.get("comparison_id") != request.comparison_id:
        raise ComparisonOrchestrationError(
            f"comparison_id changed for route {target.route_id}"
        )
    raw = _as_mapping(payload.get("route_result"), "route_result")
    if raw.get("route_id") != target.route_id:
        raise ComparisonOrchestrationError(
            f"route result identity mismatch for {target.route_id}"
        )
    result = RouteResult(
        route_id=str(raw.get("route_id", "")),
        task_identity=str(raw.get("task_identity", "")),
        output_sha256=str(raw.get("output_sha256", "")),
        metrics=_as_mapping(raw.get("metrics", {}), "metrics"),
        admissibility_result=str(raw.get("admissibility_result", "")),
        receipt_refs=list(raw.get("receipt_refs", [])),
        warnings=list(raw.get("warnings", [])),
    )
    result.validate(request)
    return result


def run_paired_comparison(
    request: ComparisonRequest,
    targets: Mapping[str, ExecutorTarget],
    *,
    parallel: bool = True,
) -> Dict[str, Any]:
    """Execute both declared routes and emit one canonical comparison receipt."""

    request.validate()
    declared = {route.route_id for route in request.routes}
    if set(targets) != declared:
        raise ComparisonOrchestrationError(
            "targets must match the comparison request route_ids exactly"
        )
    for route_id, target in targets.items():
        if target.route_id != route_id:
            raise ComparisonOrchestrationError("target mapping key must match target.route_id")
        target.validate()

    envelope = build_transport_envelope(request)
    results: Dict[str, RouteResult] = {}

    if parallel:
        with ThreadPoolExecutor(max_workers=len(targets)) as pool:
            futures = {
                pool.submit(_execute_target, target, envelope): route_id
                for route_id, target in targets.items()
            }
            for future in as_completed(futures):
                route_id = futures[future]
                payload = future.result()
                results[route_id] = _parse_single_route_result(
                    request, targets[route_id], payload
                )
    else:
        for route_id, target in targets.items():
            payload = _execute_target(target, envelope)
            results[route_id] = _parse_single_route_result(request, target, payload)

    ordered_results = [results[route.route_id] for route in request.routes]
    receipt = build_comparison_receipt(request, ordered_results)
    orchestration = {
        "orchestration_schema_version": ORCHESTRATION_SCHEMA_VERSION,
        "message_type": "LLM_ROUTE_COMPARISON_COMPLETE",
        "comparison_id": request.comparison_id,
        "request_envelope_sha256": envelope["envelope_sha256"],
        "route_result_count": len(ordered_results),
        "parallel_execution_requested": parallel,
        "comparison_receipt": receipt,
        "invariants": {
            "orchestration_is_execution_authority": False,
            "orchestration_is_admissibility": False,
            "same_request_sent_to_all_routes": True,
            "all_route_results_validated_before_delta": True,
        },
    }
    orchestration["orchestration_sha256"] = stable_hash(orchestration)
    return orchestration
