from stegverse.transition_usage import (
    TransitionUsageEvent,
    UsageMetric,
    UsageValidationError,
    aggregate_session_usage,
    build_usage_event,
)


def _event(measurement_id: str, owner: str, cost: str, entry_point: str):
    return build_usage_event(
        TransitionUsageEvent(
            measurement_id=measurement_id,
            session_id="session-001",
            transition_id=f"transition-{measurement_id}",
            entry_point=entry_point,
            entry_point_role="test-role",
            interaction_type="governed-test",
            metric_owner=owner,
            measurement_source=f"{owner}-runtime",
            evidence_class="MEASURED",
            metrics={
                "total_cost_usd": UsageMetric(cost, "USD", "MEASURED", measurement_id),
                "latency_ms": UsageMetric("10", "ms", "MEASURED", measurement_id),
            },
            occurred_at="2026-07-12T12:00:00Z",
        )
    )


def test_usage_event_is_deterministic_and_non_authorizing():
    first = _event("m-1", "sdk", "0.01", "sdk")
    second = _event("m-1", "sdk", "0.01", "sdk")
    assert first == second
    assert len(first["event_sha256"]) == 64
    assert first["invariants"]["usage_event_is_authority"] is False
    assert first["invariants"]["session_identity_preserved"] is True


def test_session_aggregation_spans_entry_points():
    result = aggregate_session_usage(
        [
            _event("m-1", "sdk", "0.01", "sdk"),
            _event("m-2", "llm_adapter", "0.04", "llm_adapter"),
            _event("m-3", "ecosystem_chat", "0.02", "ecosystem_chat"),
        ]
    )
    assert result["entry_points"] == ["ecosystem_chat", "llm_adapter", "sdk"]
    cost = next(item for item in result["totals"] if item["metric"] == "total_cost_usd")
    assert cost["value"] == "0.07"
    assert result["measurement_count_unique"] == 3


def test_duplicate_measurement_owner_pair_is_not_double_counted():
    event = _event("m-1", "sdk", "0.01", "sdk")
    result = aggregate_session_usage([event, event])
    assert result["measurement_count_received"] == 2
    assert result["measurement_count_unique"] == 1


def test_mixed_sessions_fail_closed():
    first = _event("m-1", "sdk", "0.01", "sdk")
    second = dict(_event("m-2", "sdk", "0.02", "sdk"))
    second["session_id"] = "session-002"
    try:
        aggregate_session_usage([first, second])
    except UsageValidationError as exc:
        assert "one session_id" in str(exc)
    else:
        raise AssertionError("mixed sessions must fail closed")
