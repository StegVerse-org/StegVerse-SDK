"""Deltas must name the routes they were measured between.

A comparison across more than two routes has no privileged pair. Reporting one
anyway, chosen by whichever route was listed first, makes the published delta a
function of list order rather than of measurement.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from stegverse.llm_route_comparison import (
    DELTAS_OMITTED_MULTIPLE_BASELINES,
    DELTAS_OMITTED_MULTIPLE_CANDIDATES,
    ComparisonRequest,
    ComparisonRoute,
    RouteResult,
    build_comparison_receipt,
)

CLAIM_BEARING_FIELDS = (
    "deltas",
    "delta_scope",
    "deltas_omitted_reason",
    "route_deltas",
    "route_results",
)


def _route(route_id: str, kind: str) -> ComparisonRoute:
    return ComparisonRoute(
        route_id=route_id,
        route_kind=kind,
        provider="provider",
        model=route_id,
        execution_target="target",
        governance_profile="profile",
        recursion_enabled=kind == "EXTERNAL_RECURSIVE",
    )


def _result(route_id: str, latency_ms: str) -> RouteResult:
    return RouteResult(
        route_id=route_id,
        task_identity="TASK",
        output_sha256="a" * 64,
        metrics={
            "latency_ms": {
                "value": latency_ms,
                "unit": "ms",
                "evidence_class": "MEASURED",
            }
        },
        admissibility_result="ALLOW",
    )


def _receipt(
    routes: List[ComparisonRoute], results: List[RouteResult]
) -> Dict[str, Any]:
    request = ComparisonRequest(
        comparison_id="CMP-1",
        normalized_input={"query": "one question"},
        task_identity="TASK",
        output_requirements={},
        routes=routes,
        metrics_requested=["latency_ms"],
    )
    return build_comparison_receipt(request, results)


GOVERNED = _route("gov", "STEGVERSE_GOVERNED")
LLM_A = _route("llmA", "EXTERNAL_RECURSIVE")
LLM_B = _route("llmB", "EXTERNAL_RECURSIVE")
LLM_C = _route("llmC", "EXTERNAL_RECURSIVE")

FOUR_RESULTS = [
    _result("gov", "10"),
    _result("llmA", "100"),
    _result("llmB", "900"),
    _result("llmC", "5000"),
]


def test_two_route_comparison_reports_a_scoped_delta() -> None:
    receipt = _receipt([GOVERNED, LLM_A], [_result("gov", "10"), _result("llmA", "100")])
    assert receipt["deltas"]["latency_ms"]["value"] == "90"
    assert receipt["deltas_omitted_reason"] is None
    assert receipt["delta_scope"] == {
        "baseline_route_id": "gov",
        "candidate_route_id": "llmA",
    }


def test_multi_candidate_comparison_reports_one_delta_per_candidate() -> None:
    receipt = _receipt([GOVERNED, LLM_A, LLM_B, LLM_C], FOUR_RESULTS)
    measured = {
        (entry["baseline_route_id"], entry["candidate_route_id"]): entry["deltas"][
            "latency_ms"
        ]["value"]
        for entry in receipt["route_deltas"]
    }
    assert measured == {
        ("gov", "llmA"): "90",
        ("gov", "llmB"): "890",
        ("gov", "llmC"): "4990",
    }
    assert receipt["candidate_route_count"] == 3
    assert receipt["baseline_route_count"] == 1


def test_multi_candidate_comparison_omits_the_unscoped_delta_with_a_reason() -> None:
    receipt = _receipt([GOVERNED, LLM_A, LLM_B, LLM_C], FOUR_RESULTS)
    assert receipt["deltas"] == {}
    assert receipt["delta_scope"] is None
    assert receipt["deltas_omitted_reason"] == DELTAS_OMITTED_MULTIPLE_CANDIDATES


def test_route_list_order_cannot_change_what_the_receipt_claims() -> None:
    """The regression this module exists for.

    Before delta scoping, reordering `routes` alone moved the published
    latency_ms delta from 90 to 4990 -- same routes, same measurements, same
    comparison_id, a 55x difference in the reported number.
    """
    forward = _receipt([GOVERNED, LLM_A, LLM_B, LLM_C], FOUR_RESULTS)
    reversed_routes = _receipt([GOVERNED, LLM_C, LLM_B, LLM_A], FOUR_RESULTS)
    for field in CLAIM_BEARING_FIELDS:
        assert forward[field] == reversed_routes[field], field


def test_result_list_order_cannot_change_the_receipt_digest() -> None:
    forward = _receipt([GOVERNED, LLM_A, LLM_B, LLM_C], FOUR_RESULTS)
    shuffled = _receipt([GOVERNED, LLM_A, LLM_B, LLM_C], list(reversed(FOUR_RESULTS)))
    assert forward["receipt_sha256"] == shuffled["receipt_sha256"]


def test_multiple_baselines_omit_deltas_rather_than_pick_one() -> None:
    second_governed = _route("gov2", "STEGVERSE_GOVERNED")
    receipt = _receipt(
        [GOVERNED, second_governed, LLM_A],
        [_result("gov", "10"), _result("gov2", "20"), _result("llmA", "100")],
    )
    assert receipt["deltas"] == {}
    assert receipt["route_deltas"] == []
    assert receipt["deltas_omitted_reason"] == DELTAS_OMITTED_MULTIPLE_BASELINES
    assert receipt["baseline_route_count"] == 2


def test_every_reported_delta_names_both_of_its_routes() -> None:
    receipt = _receipt([GOVERNED, LLM_A, LLM_B, LLM_C], FOUR_RESULTS)
    declared = {route.route_id for route in (GOVERNED, LLM_A, LLM_B, LLM_C)}
    assert receipt["route_deltas"], "a multi-candidate comparison must report deltas"
    for entry in receipt["route_deltas"]:
        assert entry["baseline_route_id"] in declared
        assert entry["candidate_route_id"] in declared
        assert entry["baseline_route_id"] != entry["candidate_route_id"]
        assert entry["delta_semantics"] == receipt["delta_semantics"]


def test_all_route_results_are_carried_not_only_the_compared_pair() -> None:
    receipt = _receipt([GOVERNED, LLM_A, LLM_B, LLM_C], FOUR_RESULTS)
    carried = {entry["route_id"] for entry in receipt["route_results"]}
    assert carried == {"gov", "llmA", "llmB", "llmC"}


def test_a_missing_result_still_fails_closed_with_many_routes() -> None:
    with pytest.raises(Exception):
        _receipt([GOVERNED, LLM_A, LLM_B, LLM_C], FOUR_RESULTS[:3])
