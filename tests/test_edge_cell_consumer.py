from __future__ import annotations

import copy
import json
from pathlib import Path

from stegverse.edge_cell_consumer import (
    CANONICAL_ACTIVATION_RECEIPT_SHA256,
    CANONICAL_SOURCE_COMMIT,
    validate_edge_cell_source_binding,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "edge_cell_source_binding.json"


def source_binding() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_accepts_exact_canonical_source_binding():
    result = validate_edge_cell_source_binding(source_binding())

    assert result.accepted is True
    assert result.status == "accepted_for_non_authorizing_sdk_consumption"
    assert result.source_commit == CANONICAL_SOURCE_COMMIT
    assert result.activation_state == "ACTIVE"
    assert result.errors == ()
    assert result.non_claims["sdk_acceptance_is_execution_authority"] is False
    assert result.non_claims["sdk_acceptance_is_custody"] is False


def test_binding_result_is_deterministic():
    binding = source_binding()

    first = validate_edge_cell_source_binding(binding)
    second = validate_edge_cell_source_binding(copy.deepcopy(binding))

    assert first.to_dict() == second.to_dict()
    assert len(first.binding_sha256) == 64


def test_rejects_source_commit_drift():
    binding = source_binding()
    binding["source"]["commit"] = "0" * 40

    result = validate_edge_cell_source_binding(binding)

    assert result.accepted is False
    assert result.status == "rejected_fail_closed"
    assert "source.commit does not match the accepted runtime commit" in result.errors


def test_rejects_activation_receipt_hash_drift():
    binding = source_binding()
    assert binding["activation_receipt"]["receipt_hash"] == CANONICAL_ACTIVATION_RECEIPT_SHA256
    binding["activation_receipt"]["receipt_hash"] = "f" * 64

    result = validate_edge_cell_source_binding(binding)

    assert result.accepted is False
    assert "activation receipt hash does not match the accepted source" in result.errors


def test_rejects_authority_expansion():
    binding = source_binding()
    binding["profile"]["authority_effect"] = "EXPAND"
    binding["activation_receipt"]["authority_effect"] = "EXPAND"

    result = validate_edge_cell_source_binding(binding)

    assert result.accepted is False
    assert "profile authority expansion is prohibited" in result.errors
    assert "activation receipt authority expansion is prohibited" in result.errors


def test_rejects_conditional_capability_reclassification():
    binding = source_binding()
    binding["profile"]["base_capabilities"].append("PHYSICAL_ACTUATION")
    binding["profile"]["conditional_capabilities"].remove("PHYSICAL_ACTUATION")

    result = validate_edge_cell_source_binding(binding)

    assert result.accepted is False
    assert "profile base capabilities do not match the accepted source" in result.errors
    assert "profile conditional capabilities do not match the accepted source" in result.errors


def test_rejects_false_destination_custody_claim():
    binding = source_binding()
    binding["custody"]["status"] = "DESTINATION_ACCEPTED"
    binding["custody"]["destination_receipt_ref"] = "master-record://unverified"

    result = validate_edge_cell_source_binding(binding)

    assert result.accepted is False
    assert "custody status must remain source generated and unaccepted" in result.errors
    assert "SDK fixture cannot assert a destination custody receipt" in result.errors


def test_rejects_missing_fail_closed_control():
    binding = source_binding()
    binding["profile"]["governance_controls"]["missing_evidence_behavior"] = "ALLOW"

    result = validate_edge_cell_source_binding(binding)

    assert result.accepted is False
    assert "missing evidence behavior must remain fail closed" in result.errors
