import copy

import pytest

from stegverse.governed_application_spine import (
    CANONICAL_STEGGATE_RUNTIME,
    canonical_hash,
    validate_governed_application_spine,
)


HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64
HASH_C = "sha256:" + "c" * 64
HASH_D = "sha256:" + "d" * 64
HASH_E = "sha256:" + "e" * 64


def _record(*, execute=False):
    return {
        "schema": "stegverse.governed-application-spine.v1",
        "package_id": "pkg-001",
        "transition_id": "transition-001",
        "run_id": "run-001",
        "source": {
            "origin_class": "SDK_INPUT",
            "source_hash": HASH_A,
            "artifact_refs": ["attachment:example"],
        },
        "candidate": {
            "candidate_hash": HASH_B,
            "authorizing": False,
            "model_output_authority": "NONE",
        },
        "standing": {
            "state": "ALLOW" if execute else "PENDING",
            "receipt_hash": HASH_C if execute else None,
            "execution_authorized": False,
            "standing_current": True if execute else None,
            "validity_window": None,
        },
        "admissibility": {
            "runtime_identity": CANONICAL_STEGGATE_RUNTIME,
            "request_hash": HASH_D if execute else None,
            "state": "ALLOW" if execute else "PENDING",
            "commit_time_validity": "CURRENT" if execute else "PENDING",
            "commit_coherence": "ALLOW" if execute else "PENDING",
        },
        "execution": {
            "performed": execute,
            "executor_ref": "executor:test" if execute else None,
            "result_hash": HASH_E if execute else None,
        },
        "continuity": {
            "return_ingested": execute,
            "receipt_chain_head": HASH_E if execute else None,
            "reconstruction_state": "PASS" if execute else "PENDING",
            "discovery_ref": None,
            "custody_ref": None,
        },
        "authority": {
            "sdk_authority": "NONE",
            "spe_execution_authority": "NONE",
            "model_output_authority": "NONE",
            "custody_authority": "NONE",
        },
    }


def test_pending_record_is_valid_and_non_authorizing():
    record = _record(execute=False)
    assert validate_governed_application_spine(record) == record


def test_complete_allowed_execution_is_valid():
    record = _record(execute=True)
    assert validate_governed_application_spine(record) == record


def test_spe_allow_alone_cannot_authorize_execution():
    record = _record(execute=True)
    record["admissibility"]["state"] = "PENDING"
    record["admissibility"]["commit_time_validity"] = "PENDING"
    record["admissibility"]["commit_coherence"] = "PENDING"
    with pytest.raises(ValueError, match="StegGate ALLOW"):
        validate_governed_application_spine(record)


def test_stale_standing_cannot_cross_execution_boundary():
    record = _record(execute=True)
    record["standing"]["standing_current"] = False
    with pytest.raises(ValueError, match="current SPE ALLOW standing"):
        validate_governed_application_spine(record)


def test_model_output_cannot_gain_authority():
    record = _record(execute=False)
    record["candidate"]["model_output_authority"] = "EXECUTE"
    with pytest.raises(ValueError, match="model output cannot carry authority"):
        validate_governed_application_spine(record)


def test_sdk_candidate_cannot_be_authorizing():
    record = _record(execute=False)
    record["candidate"]["authorizing"] = True
    with pytest.raises(ValueError, match="non-authorizing"):
        validate_governed_application_spine(record)


def test_canonical_hash_is_deterministic_and_key_order_independent():
    left = {"a": 1, "b": {"x": 2, "y": 3}}
    right = {"b": {"y": 3, "x": 2}, "a": 1}
    assert canonical_hash(left) == canonical_hash(right)


def test_mutating_source_hash_changes_record_hash():
    record = _record(execute=False)
    altered = copy.deepcopy(record)
    altered["source"]["source_hash"] = HASH_E
    assert canonical_hash(record) != canonical_hash(altered)
