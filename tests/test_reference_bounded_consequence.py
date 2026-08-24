import json
from pathlib import Path

import pytest

from stegverse.reference_bounded_consequence import (
    apply_reference_state_transition,
    reference_state_executor,
)


def test_reference_state_transition_records_real_before_after_state(tmp_path: Path):
    path = tmp_path / "state.json"
    result = apply_reference_state_transition(
        path,
        key="bounded_value",
        value=42,
        idempotency_key="tx:reference:001",
    )
    assert result["status"] == "STATE_TRANSITION_RECORDED"
    assert result["state_transition_performed"] is True
    assert result["external_side_effect"] is False
    assert result["before_state_hash"] != result["after_state_hash"]
    assert result["before_revision"] == 0
    assert result["after_revision"] == 1
    state = json.loads(path.read_text(encoding="utf-8"))
    assert state["values"]["bounded_value"] == 42
    assert state["revision"] == 1


def test_reference_state_transition_suppresses_exact_idempotent_replay(tmp_path: Path):
    path = tmp_path / "state.json"
    first = apply_reference_state_transition(
        path,
        key="bounded_value",
        value=42,
        idempotency_key="tx:reference:001",
    )
    second = apply_reference_state_transition(
        path,
        key="bounded_value",
        value=42,
        idempotency_key="tx:reference:001",
    )
    assert first["state_transition_performed"] is True
    assert second["status"] == "IDEMPOTENT_REPLAY_SUPPRESSED"
    assert second["state_transition_performed"] is False
    assert second["before_state_hash"] == second["after_state_hash"]
    assert second["revision"] == 1


def test_reference_state_transition_rejects_idempotency_conflict(tmp_path: Path):
    path = tmp_path / "state.json"
    apply_reference_state_transition(
        path,
        key="bounded_value",
        value=42,
        idempotency_key="tx:reference:001",
    )
    with pytest.raises(ValueError, match="idempotency_key_conflict"):
        apply_reference_state_transition(
            path,
            key="bounded_value",
            value=43,
            idempotency_key="tx:reference:001",
        )


def test_executor_is_zero_argument_and_non_authorizing(tmp_path: Path):
    path = tmp_path / "state.json"
    executor = reference_state_executor(
        path,
        key="bounded_value",
        value={"accepted": True},
        idempotency_key="tx:reference:002",
    )
    result = executor()
    assert result["state_transition_performed"] is True
    assert result["authority_effect"] == "NONE"
