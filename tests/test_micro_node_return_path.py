from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest

from stegverse.micro_node_return_path import (
    MicroNodeReturnPathValidationError,
    validate_micro_node_return_path,
)

FIXTURES = ROOT / "examples" / "micro_node_return_path"


def read_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_micro_node_return_path_allows_valid_fixture() -> None:
    decision = validate_micro_node_return_path(
        read_fixture("request.json"), read_fixture("governed_return.json")
    )
    assert decision.decision == "ALLOW"
    assert decision.transition_id == "llm-adapter-micro-node-demo-001"
    assert decision.request_hash
    assert decision.governed_return_hash


def test_micro_node_return_path_fails_closed_on_execution_authority() -> None:
    request = read_fixture("request.json")
    governed_return = read_fixture("governed_return.json")
    governed_return["execution_authority_granted"] = True

    decision = validate_micro_node_return_path(request, governed_return)

    assert decision.decision == "FAIL_CLOSED"
    assert "execution authority" in decision.reason


def test_micro_node_return_path_rejects_malformed_request() -> None:
    request = read_fixture("request.json")
    governed_return = read_fixture("governed_return.json")
    del request["return_path"]

    with pytest.raises(MicroNodeReturnPathValidationError):
        validate_micro_node_return_path(request, governed_return)
