#!/usr/bin/env python3
"""Verify the SDK governed-vs-recursive comparison contract end to end."""

from __future__ import annotations

from stegverse import (
    ComparisonRequest,
    ComparisonRoute,
    RouteResult,
    build_comparison_package,
    build_comparison_receipt,
    required_default_metrics,
)


def metrics(cost: str, latency: str, calls: str, source: str) -> dict:
    values = {
        "total_cost_usd": (cost, "USD"),
        "latency_ms": (latency, "ms"),
        "model_calls": (calls, "count"),
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


def main() -> int:
    requested = required_default_metrics()
    request = ComparisonRequest(
        comparison_id="comparison-demo-001",
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
                telemetry_required=requested,
            ),
            ComparisonRoute(
                route_id="external-recursive",
                route_kind="EXTERNAL_RECURSIVE",
                provider="external",
                model="provider-selected",
                execution_target="llm-adapter",
                governance_profile="comparison-observed",
                recursion_enabled=True,
                telemetry_required=requested,
            ),
        ],
        metrics_requested=requested,
    )
    package = build_comparison_package(request)
    results = [
        RouteResult(
            route_id="stegverse-governed",
            task_identity=request.task_identity,
            output_sha256="a" * 64,
            metrics=metrics("0.0184", "2800", "2", "fixture-governed"),
            admissibility_result="ALLOW",
            receipt_refs=["fixture-receipt-governed"],
        ),
        RouteResult(
            route_id="external-recursive",
            task_identity=request.task_identity,
            output_sha256="b" * 64,
            metrics=metrics("0.0927", "7400", "7", "fixture-recursive"),
            admissibility_result="OBSERVED_OUTPUT",
        ),
    ]
    receipt = build_comparison_receipt(request, results)

    assert len(package["package_sha256"]) == 64
    assert receipt["deltas"]["total_cost_usd"]["value"] == "0.0743"
    assert receipt["deltas"]["latency_ms"]["value"] == "4600"
    assert receipt["deltas"]["model_calls"]["value"] == "5"
    assert receipt["reconstructable"] is True
    print("LLM route comparison verification passed.")
    print(f"package_sha256={package['package_sha256']}")
    print(f"receipt_sha256={receipt['receipt_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
