from pathlib import Path

import pytest

from stegverse.post_return_evidence import (
    build_pending_interlock_return,
    complete_post_return_evidence,
)
from tests.test_portable_governance_verifier import _bundle

H7 = "sha256:" + "7" * 64
H8 = "8" * 64
H9 = "9" * 64


def _sovereign_result():
    return {
        "manifest_receipt_id": "MR-" + "A" * 64,
        "transaction_id": "tx-canonical-001",
        "route_manifest_id": "MF-" + "B" * 64,
        "route_receipt_chain_head": H8,
        "governance_state": "ALLOW",
        "chain_verified": True,
        "transaction_identity_continuous": True,
        "master_records_custody_status": "RECORDED",
        "execution_result": {
            "schema": "stegverse.reference-bounded-consequence.v1",
            "status": "STATE_TRANSITION_RECORDED",
            "state_transition_performed": True,
            "external_side_effect": False,
            "before_state_hash": "sha256:" + "1" * 64,
            "after_state_hash": "sha256:" + "2" * 64,
        },
        "result_binding_hash": "sha256:" + "3" * 64,
    }


def _custody():
    result = _sovereign_result()
    return {
        "schema": "stegverse.master-records.manifest-receipt-custody.v1",
        "manifest_receipt_id": result["manifest_receipt_id"],
        "master_record_sha256": H9,
        "evidence_package": {
            "manifest_receipt_id": result["manifest_receipt_id"],
            "transaction_id": result["transaction_id"],
            "manifest_hash": "4" * 64,
            "receipt_chain_head": "5" * 64,
            "canonical_runtime_identity": "stegverse:steggate:canonical:three-layer:v1",
        },
        "locator_grants_authority": False,
    }


def test_pending_return_binds_exact_canonical_custody_and_consequence():
    pre = _bundle()
    pending = build_pending_interlock_return(
        pre["ingress_interlock"],
        _sovereign_result(),
        _custody(),
    )
    assert pending["acknowledgement"]["state"] == "PENDING"
    assert pending["binding"]["governance_record_hash"] == "sha256:" + H9
    assert pending["egress"]["receipts"][0]["receipt_id"].startswith("MR-")
    assert pending["authority"]["master_records_custody_claimed"] is False


def test_complete_post_return_evidence_verifies_exchange_replay_and_reconstruction(tmp_path: Path):
    pre = _bundle()
    result = _sovereign_result()

    def replay(receipt_id):
        assert receipt_id == result["manifest_receipt_id"]
        return {
            "manifest_receipt_id": receipt_id,
            "deterministic_disposition_match": True,
            "consequence_reexecuted": False,
            "original_record_mutated": False,
            "operation_transition_custody_status": "RECORDED",
        }

    def reconstruct(receipt_id):
        assert receipt_id == result["manifest_receipt_id"]
        return {
            "manifest_receipt_id": receipt_id,
            "transaction_id": result["transaction_id"],
            "consequence_reexecuted": False,
            "original_record_mutated": False,
            "operation_transition_custody_status": "RECORDED",
        }

    proof = complete_post_return_evidence(
        pre_steggate_bundle=pre,
        sovereign_result=result,
        custody_record=_custody(),
        successor_state_id="external:s18",
        successor_state_hash=H7,
        exchange_path=tmp_path / "post-return.zip",
        replay=replay,
        reconstruct=reconstruct,
    )
    assert proof["status"] == "PASS"
    assert proof["interlock_return_state"] == "ACKNOWLEDGED"
    assert proof["portable_verification"]["stage"] == "POST_RETURN"
    assert proof["portable_verification"]["status"] == "PASS"
    assert proof["exchange_verification"]["status"] == "PASS"
    assert proof["replay"]["consequence_reexecuted"] is False
    assert proof["reconstruction"]["consequence_reexecuted"] is False
    assert proof["authority"]["copied_evidence_is_canonical_custody"] is False


def test_return_fails_closed_without_real_bounded_transition():
    pre = _bundle()
    result = _sovereign_result()
    result["execution_result"]["state_transition_performed"] = False
    with pytest.raises(ValueError, match="did not perform"):
        build_pending_interlock_return(pre["ingress_interlock"], result, _custody())


def test_return_fails_closed_without_master_records_custody():
    pre = _bundle()
    result = _sovereign_result()
    result["master_records_custody_status"] = "PENDING"
    with pytest.raises(ValueError, match="not recorded"):
        build_pending_interlock_return(pre["ingress_interlock"], result, _custody())
