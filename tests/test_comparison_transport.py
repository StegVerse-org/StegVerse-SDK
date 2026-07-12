from pathlib import Path

import pytest

from stegverse.comparison_transport import (
    ComparisonTransportError,
    build_transport_envelope,
    export_json,
    import_json,
    validate_return_envelope,
)
from stegverse.llm_route_comparison import (
    ComparisonRequest,
    ComparisonRoute,
    required_default_metrics,
)


def _request() -> ComparisonRequest:
    metrics = required_default_metrics()
    return ComparisonRequest(
        comparison_id="cmp-transport-001",
        normalized_input={"prompt": "Assess transition."},
        task_identity="transition-assessment",
        output_requirements={"format": "json"},
        routes=[
            ComparisonRoute(
                route_id="governed",
                route_kind="STEGVERSE_GOVERNED",
                provider="stegverse",
                model="ecosystem-llm",
                execution_target="core-node-runtime-demo",
                governance_profile="transition-table-native",
                recursion_enabled=False,
                telemetry_required=metrics,
            ),
            ComparisonRoute(
                route_id="recursive",
                route_kind="EXTERNAL_RECURSIVE",
                provider="external",
                model="provider-model",
                execution_target="llm-adapter",
                governance_profile="comparison-observed",
                recursion_enabled=True,
                telemetry_required=metrics,
            ),
        ],
        metrics_requested=metrics,
    )


def _metric(value: str, unit: str) -> dict:
    return {
        "value": value,
        "unit": unit,
        "evidence_class": "MEASURED",
        "source_ref": "trace",
    }


def _result(route_id: str, task_identity: str, cost: str) -> dict:
    metrics = {
        "total_cost_usd": _metric(cost, "USD"),
        "latency_ms": _metric("10", "ms"),
        "model_calls": _metric("1", "count"),
        "input_tokens": _metric("10", "tokens"),
        "output_tokens": _metric("5", "tokens"),
        "tool_calls": _metric("0", "count"),
        "retries": _metric("0", "count"),
        "node_or_cell_activations": _metric("1", "count"),
        "receipt_count": _metric("1", "count"),
        "reconstructable": _metric("1", "boolean"),
    }
    return {
        "route_id": route_id,
        "task_identity": task_identity,
        "output_sha256": "a" * 64,
        "metrics": metrics,
        "admissibility_result": "ALLOW",
        "receipt_refs": [f"receipt:{route_id}"],
        "warnings": [],
    }


def test_build_transport_envelope_is_deterministic() -> None:
    first = build_transport_envelope(_request())
    second = build_transport_envelope(_request())
    assert first == second
    assert first["invariants"]["transport_is_execution_authority"] is False


def test_validate_return_envelope_builds_receipt() -> None:
    request = _request()
    envelope = {
        "message_type": "LLM_ROUTE_COMPARISON_RESULT",
        "comparison_id": request.comparison_id,
        "route_results": [
            _result("governed", request.task_identity, "0.01"),
            _result("recursive", request.task_identity, "0.04"),
        ],
    }
    receipt = validate_return_envelope(request, envelope)
    assert receipt["deltas"]["total_cost_usd"]["value"] == "0.03"
    assert len(receipt["receipt_sha256"]) == 64


def test_validate_return_envelope_rejects_id_change() -> None:
    with pytest.raises(ComparisonTransportError):
        validate_return_envelope(
            _request(),
            {"message_type": "LLM_ROUTE_COMPARISON_RESULT", "comparison_id": "other"},
        )


def test_json_round_trip(tmp_path: Path) -> None:
    destination = tmp_path / "nested" / "receipt.json"
    payload = {"b": 2, "a": 1}
    export_json(payload, destination)
    assert import_json(destination) == payload
