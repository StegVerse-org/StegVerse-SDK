from copy import deepcopy
from hashlib import sha256
import json

import pytest

from stegverse.spe_allow_consumer import (
    SPEAllowConsumerError,
    build_progression_packet,
    validate_progression_packet,
    validate_spe_receipt,
)


def digest(value):
    material = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + sha256(material.encode("utf-8")).hexdigest()


def receipt(decision="ALLOW"):
    body = {
        "schema": "stegverse.spe.standing_receipt.v0.1",
        "receipt_id": "spe-receipt-001",
        "transition_id": "transition-001",
        "run_id": "run-001",
        "candidate_hash": "candidate-hash-001",
        "decision": decision,
        "policy_ref": "policy://spe/default",
        "standing_evidence_ref": "evidence://spe/standing/001",
        "authorizing": False,
        "execution_authority_granted": False,
        "delegation_granted": False,
        "mutation_authorized": False,
        "publication_authorized": False,
        "custody_transferred": False,
        "admissibility_determined": False,
    }
    return {**body, "receipt_hash": digest(body)}


def validate(value):
    return validate_spe_receipt(
        value,
        expected_transition_id="transition-001",
        expected_run_id="run-001",
        expected_candidate_hash="candidate-hash-001",
    )


def test_allow_permits_progression_but_never_execution():
    packet = build_progression_packet(
        receipt(),
        expected_transition_id="transition-001",
        expected_run_id="run-001",
        expected_candidate_hash="candidate-hash-001",
        next_boundary="StegVerse-Labs/Ecosystem-Delegation",
    )
    assert packet["progression_permitted"] is True
    assert packet["progression_status"] == "READY_FOR_NEXT_GOVERNED_BOUNDARY"
    assert packet["execution_permitted"] is False
    assert packet["execution_authority_granted"] is False
    assert packet["fresh_authority_determination_required"] is True
    assert validate_progression_packet(packet) == packet


@pytest.mark.parametrize("decision", ["DENY", "FAIL_CLOSED"])
def test_non_allow_decisions_block_progression(decision):
    packet = build_progression_packet(
        receipt(decision),
        expected_transition_id="transition-001",
        expected_run_id="run-001",
        expected_candidate_hash="candidate-hash-001",
        next_boundary="StegVerse-Labs/Ecosystem-Delegation",
    )
    assert packet["progression_permitted"] is False
    assert packet["progression_status"] == "PROGRESSION_BLOCKED"
    assert packet["execution_permitted"] is False


def test_rejects_transition_identity_mismatch():
    with pytest.raises(SPEAllowConsumerError, match="transition_id mismatch"):
        validate_spe_receipt(
            receipt(),
            expected_transition_id="different-transition",
            expected_run_id="run-001",
            expected_candidate_hash="candidate-hash-001",
        )


def test_rejects_receipt_authority_escalation():
    bad = receipt()
    bad["execution_authority_granted"] = True
    body = dict(bad)
    body.pop("receipt_hash")
    bad["receipt_hash"] = digest(body)
    with pytest.raises(SPEAllowConsumerError, match="execution_authority_granted"):
        validate(bad)


def test_rejects_receipt_digest_tamper():
    bad = deepcopy(receipt())
    bad["standing_evidence_ref"] = "evidence://tampered"
    with pytest.raises(SPEAllowConsumerError, match="digest mismatch"):
        validate(bad)


def test_rejects_progression_packet_execution_escalation():
    packet = build_progression_packet(
        receipt(),
        expected_transition_id="transition-001",
        expected_run_id="run-001",
        expected_candidate_hash="candidate-hash-001",
        next_boundary="StegVerse-Labs/Ecosystem-Delegation",
    )
    packet["execution_permitted"] = True
    with pytest.raises(SPEAllowConsumerError, match="execution_permitted"):
        validate_progression_packet(packet)
