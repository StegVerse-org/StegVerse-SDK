import copy

import pytest

from stegverse.interlock_return import canonical_hash, validate_interlock_return

H1 = "sha256:" + "1" * 64
H2 = "sha256:" + "2" * 64
H3 = "sha256:" + "3" * 64
H4 = "sha256:" + "4" * 64
H5 = "sha256:" + "5" * 64
H6 = "sha256:" + "6" * 64
H7 = "sha256:" + "7" * 64
H8 = "sha256:" + "8" * 64


def _record(*, state="ACKNOWLEDGED"):
    successor_receipts = []
    received = None
    binding = None
    relationships = []
    if state == "ACKNOWLEDGED":
        successor_receipts = [{"receipt_id": "framework-a:r18", "issuer": "framework-a", "receipt_hash": H7}]
        received = H5
        binding = H8
        relationships = [
            {"from_receipt_hash": H5, "to_receipt_hash": H7, "type": "ACKNOWLEDGES"},
            {"from_receipt_hash": H5, "to_receipt_hash": H7, "type": "BINDS_AS_PREDECESSOR"},
        ]
    elif state == "REJECTED":
        successor_receipts = [{"receipt_id": "framework-a:reject-18", "issuer": "framework-a", "receipt_hash": H7}]
        received = H5
        binding = H8
        relationships = [{"from_receipt_hash": H5, "to_receipt_hash": H7, "type": "REJECTS"}]

    return {
        "schema": "stegverse.interlock-return.v1",
        "package_id": "pkg-65-001",
        "transition_id": "tx-65-001",
        "run_id": "run-65-001",
        "participant_id": "framework-a",
        "binding": {
            "ingress_interlock_hash": H1,
            "governance_record_hash": H2,
            "material_causal_closure_hash": H3,
        },
        "egress": {
            "manifest_hash": H4,
            "governed_state_hash": H6,
            "receipts": [{"receipt_id": "stegverse:r900", "issuer": "StegVerse", "receipt_hash": H5}],
        },
        "acknowledgement": {
            "state": state,
            "received_egress_receipt_hash": received,
            "participant_binding_hash": binding,
            "participant_successor_receipts": successor_receipts,
        },
        "relationships": relationships,
        "reconstruction": {
            "required": True,
            "replay_scope": "MATERIAL_CAUSAL_CLOSURE",
            "egress_manifest_hash": H4,
        },
        "authority": {
            "sdk_authority": "NONE",
            "participant_truth_assumed": False,
            "return_transfers_authority": False,
            "master_records_custody_claimed": False,
            "execution_authorized": False,
        },
    }


def test_acknowledged_return_validates():
    record = _record()
    assert validate_interlock_return(record) == record


def test_pending_return_is_valid_without_fake_acknowledgement():
    record = _record(state="PENDING")
    assert validate_interlock_return(record) == record


def test_rejected_return_is_recorded_without_becoming_acknowledged():
    record = _record(state="REJECTED")
    assert validate_interlock_return(record) == record


def test_resolved_acknowledgement_binds_exact_egress_receipt():
    record = _record()
    record["acknowledgement"]["received_egress_receipt_hash"] = H6
    with pytest.raises(ValueError, match="exact egress receipt"):
        validate_interlock_return(record)


def test_resolved_acknowledgement_requires_participant_successor_receipt():
    record = _record()
    record["acknowledgement"]["participant_successor_receipts"] = []
    with pytest.raises(ValueError, match="successor receipt"):
        validate_interlock_return(record)


def test_pending_cannot_claim_binding_or_successor():
    record = _record(state="PENDING")
    record["acknowledgement"]["participant_binding_hash"] = H8
    with pytest.raises(ValueError, match="PENDING"):
        validate_interlock_return(record)


def test_relationship_must_connect_exact_receipt_sets():
    record = _record()
    record["relationships"][0]["to_receipt_hash"] = H6
    with pytest.raises(ValueError, match="connect egress"):
        validate_interlock_return(record)


def test_rejected_relationship_cannot_claim_acknowledgement():
    record = _record(state="REJECTED")
    record["relationships"][0]["type"] = "ACKNOWLEDGES"
    with pytest.raises(ValueError, match="REJECTED"):
        validate_interlock_return(record)


def test_reconstruction_binds_exact_egress_manifest():
    record = _record()
    record["reconstruction"]["egress_manifest_hash"] = H3
    with pytest.raises(ValueError, match="exact egress manifest"):
        validate_interlock_return(record)


def test_return_never_transfers_authority_or_truth():
    record = _record()
    record["authority"]["return_transfers_authority"] = True
    with pytest.raises(ValueError, match="return_transfers_authority"):
        validate_interlock_return(record)

    record = _record()
    record["authority"]["participant_truth_assumed"] = True
    with pytest.raises(ValueError, match="participant_truth_assumed"):
        validate_interlock_return(record)


def test_hash_is_deterministic_and_mutation_visible():
    record = _record()
    duplicate = copy.deepcopy(record)
    assert canonical_hash(record) == canonical_hash(duplicate)
    duplicate["binding"]["governance_record_hash"] = H8
    assert canonical_hash(record) != canonical_hash(duplicate)
