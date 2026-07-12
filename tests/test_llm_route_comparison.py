import pytest

from stegverse.llm_route_comparison import (
    ComparisonRequest,
    ComparisonRoute,
    ComparisonValidationError,
    MetricValue,
    RouteResult,
    build_comparison_package,
    build_comparison_receipt,
    calculate_delta,
    required_default_metrics,
)


def _request() -> ComparisonRequest:
    metrics = required_default_metrics()
    return ComparisonRequest(
        comparison_id="cmp-001",
        normalized_input={"prompt": "Assess whether this transition may execute."},
        task_identity="transition-admissibility-assessment",
        output_requirements={"format": "json", "decision_required": True},
        routes=[
            ComparisonRoute(
                route_id="stegverse-governed",
                route_kind="STEGVERSE_GOVERNED",
                provider="stegverse",
                model="ecosystem-llm",
                execution_target="core-node-runtime-demo",
                governance_profile="transition-table-native",
                recursion_enabled=False,
                telemetry_required=metrics,
            ),
            ComparisonRoute(
                route_id="external-recursive",
                route_kind="EXTERNAL_RECURSIVE",
                provider="external",
                model="provider-selected",
                execution_target="llm-adapter",
                governance_profile="comparison-observed",
                recursion_enabled=True,
                telemetry_required=metrics,
            ),
        ],
        metrics_requested=metrics,
    )


def _metrics(cost: str, latency: str, source: str) -> dict:
    values = {
        "total_cost_usd": (cost, "USD"),
        "latency_ms": (latency, "ms"),
        "model_calls": ("2", "count"),
        "input_tokens": ("1000", "tokens"),
        "output_tokens": ("250", "tokens"),
        "tool_calls": ("1", "count"),
        "retries": ("0", "count"),
        "node_or_cell_activations": ("8", "count"),
        "receipt_count": ("4", "count"),
        "reconstructable": ("1", "boolean"),
    }
    return {
        name: {
            "value": value,
            "unit": unit,
            "evidence_class": "MEASURED",
            "source_ref": source,
        }
        for name, (value, unit) in values.items()
    }


def test_build_comparison_package_is_deterministic() -> None:
    first = build_comparison_package(_request())
    second = build_comparison_package(_request())
    assert first == second
    assert len(first["package_sha256"]) == 64
    assert first["invariants"]["sdk_preparation_is_execution"] is False


def test_calculate_delta_from_measured_values() -> None:
    recursive = MetricValue("0.0927", "USD", "MEASURED", "trace-a")
    governed = MetricValue("0.0184", "USD", "MEASURED", "trace-b")
    delta = calculate_delta(recursive, governed, unit="USD")
    assert delta.value == "0.0743"
    assert delta.evidence_class == "DERIVED"


def test_calculate_delta_rejects_configured_as_measured() -> None:
    configured = MetricValue("4817.00", "USD", "CONFIGURED", "scenario")
    measured = MetricValue("0.004812", "USD", "MEASURED", "trace")
    delta = calculate_delta(configured, measured, unit="USD")
    assert delta.value is None
    assert delta.evidence_class == "UNAVAILABLE"


def test_build_comparison_receipt_calculates_measured_deltas() -> None:
    request = _request()
    results = [
        RouteResult(
            route_id="stegverse-governed",
            task_identity=request.task_identity,
            output_sha256="a" * 64,
            metrics=_metrics("0.0184", "2800", "governed-trace"),
            admissibility_result="ALLOW",
            receipt_refs=["receipt-governed"],
        ),
        RouteResult(
            route_id="external-recursive",
            task_identity=request.task_identity,
            output_sha256="b" * 64,
            metrics=_metrics("0.0927", "7400", "recursive-trace"),
            admissibility_result="OBSERVED_OUTPUT",
        ),
    ]
    receipt = build_comparison_receipt(request, results)
    assert receipt["deltas"]["total_cost_usd"]["value"] == "0.0743"
    assert receipt["deltas"]["latency_ms"]["value"] == "4600"
    assert receipt["delta_semantics"] == "external_recursive_minus_stegverse_governed"
    assert len(receipt["receipt_sha256"]) == 64


def test_route_result_cannot_change_task_identity() -> None:
    request = _request()
    bad = RouteResult(
        route_id="stegverse-governed",
        task_identity="different-task",
        output_sha256="a" * 64,
        metrics=_metrics("0.01", "100", "trace"),
        admissibility_result="ALLOW",
    )
    with pytest.raises(ComparisonValidationError, match="changed task identity"):
        bad.validate(request)
