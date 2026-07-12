from stegverse.comparison_orchestrator import (
    ComparisonOrchestrationError,
    ExecutorTarget,
    run_paired_comparison,
)
from stegverse.llm_route_comparison import (
    ComparisonRequest,
    ComparisonRoute,
    required_default_metrics,
)


def _request() -> ComparisonRequest:
    metrics = required_default_metrics()
    return ComparisonRequest(
        comparison_id="cmp-paired-001",
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


def _metrics(cost: str, latency: str, calls: str) -> dict:
    return {
        "total_cost_usd": {"value": cost, "unit": "USD", "evidence_class": "MEASURED", "source_ref": "trace"},
        "latency_ms": {"value": latency, "unit": "ms", "evidence_class": "MEASURED", "source_ref": "trace"},
        "model_calls": {"value": calls, "unit": "count", "evidence_class": "MEASURED", "source_ref": "trace"},
        "input_tokens": {"value": "100", "unit": "tokens", "evidence_class": "MEASURED", "source_ref": "trace"},
        "output_tokens": {"value": "20", "unit": "tokens", "evidence_class": "MEASURED", "source_ref": "trace"},
        "tool_calls": {"value": "1", "unit": "count", "evidence_class": "MEASURED", "source_ref": "trace"},
        "retries": {"value": "0", "unit": "count", "evidence_class": "MEASURED", "source_ref": "trace"},
        "node_or_cell_activations": {"value": "4", "unit": "count", "evidence_class": "MEASURED", "source_ref": "trace"},
        "receipt_count": {"value": "3", "unit": "count", "evidence_class": "MEASURED", "source_ref": "trace"},
        "reconstructable": {"value": "1", "unit": "boolean", "evidence_class": "MEASURED", "source_ref": "trace"},
    }


def _executor(route_id: str, cost: str, latency: str, calls: str):
    def execute(envelope):
        return {
            "message_type": "LLM_ROUTE_COMPARISON_ROUTE_RESULT",
            "comparison_id": envelope["comparison_id"],
            "route_result": {
                "route_id": route_id,
                "task_identity": envelope["package"]["task_identity"],
                "output_sha256": "a" * 64 if route_id == "stegverse-governed" else "b" * 64,
                "metrics": _metrics(cost, latency, calls),
                "admissibility_result": "ALLOW" if route_id == "stegverse-governed" else "NOT_EVALUATED",
                "receipt_refs": [f"receipt:{route_id}"],
                "warnings": [],
            },
        }
    return execute


def test_paired_orchestrator_builds_delta_receipt() -> None:
    request = _request()
    result = run_paired_comparison(
        request,
        {
            "stegverse-governed": ExecutorTarget(
                "stegverse-governed",
                executor=_executor("stegverse-governed", "0.0184", "2800", "2"),
            ),
            "external-recursive": ExecutorTarget(
                "external-recursive",
                executor=_executor("external-recursive", "0.0927", "7400", "7"),
            ),
        },
    )
    receipt = result["comparison_receipt"]
    assert receipt["deltas"]["total_cost_usd"]["value"] == "0.0743"
    assert receipt["deltas"]["latency_ms"]["value"] == "4600"
    assert receipt["deltas"]["model_calls"]["value"] == "5"
    assert result["route_result_count"] == 2
    assert len(result["orchestration_sha256"]) == 64


def test_paired_orchestrator_rejects_missing_target() -> None:
    request = _request()
    try:
        run_paired_comparison(
            request,
            {
                "stegverse-governed": ExecutorTarget(
                    "stegverse-governed",
                    executor=_executor("stegverse-governed", "0.01", "100", "1"),
                )
            },
        )
    except ComparisonOrchestrationError as exc:
        assert "match" in str(exc)
    else:
        raise AssertionError("missing route target should fail closed")


def test_paired_orchestrator_rejects_route_identity_drift() -> None:
    request = _request()

    def wrong_route(envelope):
        payload = _executor("stegverse-governed", "0.01", "100", "1")(envelope)
        payload["route_result"]["route_id"] = "external-recursive"
        return payload

    try:
        run_paired_comparison(
            request,
            {
                "stegverse-governed": ExecutorTarget("stegverse-governed", executor=wrong_route),
                "external-recursive": ExecutorTarget(
                    "external-recursive",
                    executor=_executor("external-recursive", "0.02", "200", "2"),
                ),
            },
            parallel=False,
        )
    except ComparisonOrchestrationError as exc:
        assert "identity mismatch" in str(exc)
    else:
        raise AssertionError("route identity drift should fail closed")
