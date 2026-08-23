import copy

import pytest

from stegverse.interlock_transition import canonical_hash, validate_interlock_transition

H1 = "sha256:" + "1" * 64
H2 = "sha256:" + "2" * 64
H3 = "sha256:" + "3" * 64
H4 = "sha256:" + "4" * 64
H5 = "sha256:" + "5" * 64
H6 = "sha256:" + "6" * 64
H7 = "sha256:" + "7" * 64


def _record():
    return {
        "schema": "stegverse.interlock-transition.v1",
        "package_id": "pkg-65-001",
        "transition_id": "tx-65-001",
        "run_id": "run-65-001",
        "connection": {
            "class": "INTERLOCK",
            "direction": "INGRESS",
            "participant_id": "framework-a",
            "participant_boundary_receipt_hash": H1,
            "participant_binding_hash": H2,
        },
        "manifest": {
            "manifest_hash": H3,
            "source_state_hash": H4,
            "canonicalization": "JCS_RFC8785_NFC",
            "predecessor_receipts": [
                {"receipt_id": "framework-a:r17", "issuer": "framework-a", "receipt_hash": H1}
            ],
        },
        "governance": {
            "mode": "DEFAULT_STEGVERSE",
            "profiles": [
                {
                    "profile_id": "stegverse.default.math.interpretation.v1",
                    "issuer": "StegVerse",
                    "profile_hash": H5,
                    "source": "STEGVERSE",
                }
            ],
        },
        "manifold": {
            "predecessors": [
                {"state_id": "framework-a:s17", "state_hash": H4},
                {"state_id": "evidence:e9", "state_hash": H6},
            ],
            "successors": [
                {"state_id": "stegverse:boundary:s18", "state_hash": H7}
            ],
            "relationships": [
                {
                    "from_state_id": "evidence:e9",
                    "to_state_id": "stegverse:boundary:s18",
                    "type": "EVIDENCE",
                },
                {
                    "from_state_id": "framework-a:s17",
                    "to_state_id": "stegverse:boundary:s18",
                    "type": "CAUSE",
                },
            ],
        },
        "boundary": {
            "state": "ACCEPT",
            "original_manifest_hash": H3,
            "repaired_manifest_hash": None,
        },
        "authority": {
            "sdk_authority": "NONE",
            "participant_truth_assumed": False,
            "interlock_transfers_authority": False,
            "master_records_custody_claimed": False,
            "execution_authorized": False,
        },
        "reconstruction": {
            "required": True,
            "replay_scope": "MATERIAL_CAUSAL_CLOSURE",
            "linear_chain_is_special_case": True,
        },
    }


def test_interlock_manifold_record_validates():
    record = _record()
    assert validate_interlock_transition(record) == record


def test_interlock_requires_participant_terminal_receipt():
    record = _record()
    record["manifest"]["predecessor_receipts"] = []
    with pytest.raises(ValueError, match="predecessor receipt"):
        validate_interlock_transition(record)


def test_boundary_receipt_must_be_one_of_manifest_predecessors():
    record = _record()
    record["connection"]["participant_boundary_receipt_hash"] = H2
    with pytest.raises(ValueError, match="present in predecessor"):
        validate_interlock_transition(record)


def test_default_stegverse_must_be_explicit_and_stegverse_sourced():
    record = _record()
    record["governance"]["profiles"][0]["source"] = "PARTICIPANT"
    with pytest.raises(ValueError, match="DEFAULT_STEGVERSE"):
        validate_interlock_transition(record)


def test_composed_requires_both_governance_sources():
    record = _record()
    record["governance"]["mode"] = "COMPOSED"
    with pytest.raises(ValueError, match="participant and StegVerse"):
        validate_interlock_transition(record)


def test_repair_preserves_original_and_creates_distinct_successor():
    record = _record()
    record["boundary"]["state"] = "REPAIR"
    record["boundary"]["repaired_manifest_hash"] = H6
    assert validate_interlock_transition(record) == record
    record["boundary"]["repaired_manifest_hash"] = H3
    with pytest.raises(ValueError, match="distinct successor"):
        validate_interlock_transition(record)


def test_interlock_never_transfers_truth_or_execution_authority():
    record = _record()
    record["authority"]["participant_truth_assumed"] = True
    with pytest.raises(ValueError, match="participant_truth_assumed"):
        validate_interlock_transition(record)

    record = _record()
    record["authority"]["execution_authorized"] = True
    with pytest.raises(ValueError, match="execution_authorized"):
        validate_interlock_transition(record)


def test_relationships_cannot_reference_unknown_states():
    record = _record()
    record["manifold"]["relationships"][0]["to_state_id"] = "missing"
    with pytest.raises(ValueError, match="unknown state"):
        validate_interlock_transition(record)


def test_linear_transition_is_supported_as_special_case():
    record = _record()
    record["manifold"] = {
        "predecessors": [{"state_id": "a", "state_hash": H4}],
        "successors": [{"state_id": "b", "state_hash": H7}],
        "relationships": [{"from_state_id": "a", "to_state_id": "b", "type": "CAUSE"}],
    }
    assert validate_interlock_transition(record) == record


def test_hash_is_deterministic_and_mutation_visible():
    record = _record()
    reordered = copy.deepcopy(record)
    assert canonical_hash(record) == canonical_hash(reordered)
    reordered["manifest"]["source_state_hash"] = H6
    assert canonical_hash(record) != canonical_hash(reordered)
