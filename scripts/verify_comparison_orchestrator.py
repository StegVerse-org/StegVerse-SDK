#!/usr/bin/env python3
"""Verify the SDK paired comparison orchestrator with deterministic fixtures."""

from stegverse.comparison_orchestrator import ExecutorTarget, run_paired_comparison
from stegverse.llm_route_comparison import (
    ComparisonRequest,
    ComparisonRoute,
    required_default_metrics,
)


def metrics(cost: str, latency: str, calls: str) -> dict:
    values = {
        "total_cost_usd": (cost, "USD"),
        "latency_ms": (latency, "ms"),
        "model_calls": (calls, "count"),
        "input_tokens": ("100", "tokens"),
        "output_tokens": ("20", "tokens"),
        "tool_calls": ("1", "count"),
        "retries": ("0", "count"),
        "node_or_cell_activations": ("4", "count"),
        "receipt_count": ("3", "count"),
        "reconstructable": ("1", "boolean"),
    }
    return {
        name: {
            "value": value,
            "unit": unit,
            "evidence_class": "MEASURED",
            "source_ref": "deterministic-verifier-fixture",
        }
        for name, (value, unit) in values.items()
    }


def executor(route_id: str, cost: str, latency: str, calls: str):
    def run(envelope):
        return {
            "message_type": "LLM_ROUTE_COMPARISON_ROUTE_RESULT",
            "comparison_id": envelope["comparison_id"],
            "route_result": {
                "route_id": route_id,
                "task_identity": envelope["package"]["task_identity"],
                "output_sha256": ("a" if route_id == "stegverse-governed" else "b") * 64,
                "metrics": metrics(cost, latency, calls),
                "admissibility_result": "ALLOW" if route_id == "stegverse-governed" else "NOT_EVALUATED",
                "receipt_refs": [f"receipt:{route_id}"],
                "warnings": ["fixture-bound; not a live provider result"],
            },
        }
    return run


def main() -> int:
    requested = required_default_metrics()
    request = ComparisonRequest(
        comparison_id="cmp-orchestrator-verifier",
        normalized_input={"prompt": "Assess whether this transition may execute."},
        task_identity="transition-admissibility-assessment",
        output_requirements={"format": "json", "decision_required": True},
        routes=[
            ComparisonRoute(
                "stegverse-governed", "STEGVERSE_GOVERNED", "stegverse",
                "ecosystem-llm", "core-node-runtime-demo",
                "transition-table-native", False, requested,
            ),
            ComparisonRoute(
                "external-recursive", "EXTERNAL_RECURSIVE", "external",
                "provider-selected", "llm-adapter",
                "comparison-observed", True, requested,
            ),
        ],
        metrics_requested=requested,
    )
    result = run_paired_comparison(
        request,
        {
            "stegverse-governed": ExecutorTarget(
                "stegverse-governed",
                executor=executor("stegverse-governed", "0.0184", "2800", "2"),
            ),
            "external-recursive": ExecutorTarget(
                "external-recursive",
                executor=executor("external-recursive", "0.0927", "7400", "7"),
            ),
        },
    )
    deltas = result["comparison_receipt"]["deltas"]
    assert deltas["total_cost_usd"]["value"] == "0.0743"
    assert deltas["latency_ms"]["value"] == "4600"
    assert deltas["model_calls"]["value"] == "5"
    assert result["invariants"]["same_request_sent_to_all_routes"] is True
    print("Paired comparison orchestrator: PASS")
    print(f"Orchestration receipt: {result['orchestration_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
