from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from stegverse.provider_usage_ingest import (
    ProviderUsageIngestError,
    ingest_provider_usage_event,
    validate_provider_usage_event,
)
from stegverse.transition_usage import aggregate_session_usage

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/provider_usage_event.json"


def load_event():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_validates_and_projects():
    event = load_event()
    validate_provider_usage_event(event)
    result = ingest_provider_usage_event(
        event,
        session_id="session-001",
        transition_id="transition-001",
        occurred_at="2026-07-25T23:30:00Z",
    ).to_dict()
    assert result["authority_transferred"] is False
    assert result["receipt_required"] is True
    projected = result["transition_usage_event"]
    assert projected["metric_owner"] == "fixture-provider"
    assert projected["metrics"]["total_tokens"]["value"] == "20"
    assert projected["metrics"]["compute_units"]["evidence_class"] == "UNAVAILABLE"
    assert projected["invariants"]["usage_event_is_authority"] is False


def test_projected_event_aggregates_without_authority_transfer():
    event = load_event()
    projected = ingest_provider_usage_event(
        event,
        session_id="session-001",
        transition_id="transition-001",
        occurred_at="2026-07-25T23:30:00Z",
    ).transition_usage_event
    aggregate = aggregate_session_usage([projected])
    assert aggregate["measurement_count_unique"] == 1
    assert "does not establish authority" in aggregate["claim_boundary"]


@pytest.mark.parametrize(
    "mutator",
    [
        lambda e: e["authority_boundary"].__setitem__("adapter_is_execution_authority", True),
        lambda e: e["reasoning_provenance"].__setitem__("full_chain_of_thought_included", True),
        lambda e: e["measurements"].__setitem__("total_tokens", 21),
        lambda e: e["return_to_origin"].__setitem__("receipt_required", False),
        lambda e: e["provider"].__setitem__("model", "tampered-model"),
        lambda e: e.__setitem__("manual_user_action_required", True),
    ],
)
def test_mutations_fail_closed(mutator):
    event = copy.deepcopy(load_event())
    mutator(event)
    with pytest.raises(ProviderUsageIngestError):
        validate_provider_usage_event(event)


def test_hash_drift_fails_closed():
    event = load_event()
    event["event_sha256"] = "0" * 64
    with pytest.raises(ProviderUsageIngestError, match="hash mismatch"):
        validate_provider_usage_event(event)
