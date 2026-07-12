from stegverse.llm_route_comparison import (
    ComparisonRequest,
    ComparisonRoute,
    MetricValue,
    build_comparison_package,
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
