from stegverse.session_usage_receipt import build_session_usage_receipt
from stegverse.transition_usage import TransitionUsageEvent, UsageMetric, UsageValidationError, build_usage_event


def _event(measurement_id: str, owner: str):
    return build_usage_event(
        TransitionUsageEvent(
            measurement_id=measurement_id,
            session_id="session-001",
            transition_id=f"transition-{measurement_id}",
            entry_point=owner,
            entry_point_role="test-role",
            interaction_type="governed-test",
            metric_owner=owner,
            measurement_source=f"{owner}-runtime",
            evidence_class="MEASURED",
            metrics={"latency_ms": UsageMetric("10", "ms", "MEASURED", measurement_id)},
            occurred_at="2026-07-12T12:00:00Z",
        )
    )


def test_receipt_is_deterministic_and_non_custodial():
    events = [_event("m-1", "sdk"), _event("m-2", "runtime")]
    first = build_session_usage_receipt(events)
    second = build_session_usage_receipt(events)
    assert first == second
    assert len(first["receipt_sha256"]) == 64
    assert first["custody_posture"] == "HANDOFF_READY_NOT_CUSTODIED"
    assert first["authority_boundary"]["receipt_is_master_record_custody"] is False


def test_source_event_hash_drift_fails_closed():
    event = _event("m-1", "sdk")
    event["entry_point"] = "tampered"
    try:
        build_session_usage_receipt([event])
    except UsageValidationError as exc:
        assert "hash mismatch" in str(exc)
    else:
        raise AssertionError("tampered source event must fail closed")
