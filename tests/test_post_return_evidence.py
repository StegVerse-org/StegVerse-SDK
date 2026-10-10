from pathlib import Path

import pytest

from stegverse.organization_ledger_evidence import TRANSITION_REQUEST_ENTRYPOINT, verify_organization_ledger_readback
from stegverse.post_return_evidence import (
    ORGANIZATION_LEDGER_ISSUER,
    build_pending_interlock_return,
    complete_post_return_evidence,
)
from tests.organization_ledger_fixture import MANIFEST, _readback
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
    """The local run store's record: optional downstream evidence, never a return input."""
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


def _completion():
    return verify_organization_ledger_readback(_readback(), canonical_manifest_sha256=MANIFEST)


def test_pending_return_binds_the_organization_ledger_receipt():
    pre = _bundle()
    completion = _completion()
    pending = build_pending_interlock_return(pre["ingress_interlock"], _sovereign_result(), completion)
    assert pending["acknowledgement"]["state"] == "PENDING"
    assert pending["binding"]["governance_record_hash"] == completion["organization_receipt_sha256"]
    receipt = pending["egress"]["receipts"][0]
    assert receipt["issuer"] == ORGANIZATION_LEDGER_ISSUER
    assert receipt["receipt_hash"] == completion["organization_receipt_sha256"]
    assert pending["egress"]["manifest_hash"] == "sha256:" + MANIFEST
    assert pending["authority"]["master_records_organization_record_claimed"] is False


def _replay_and_reconstruct(result):
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

    return replay, reconstruct


def test_complete_post_return_evidence_verifies_exchange_replay_and_reconstruction(tmp_path: Path):
    pre = _bundle()
    result = _sovereign_result()
    replay, reconstruct = _replay_and_reconstruct(result)
    proof = complete_post_return_evidence(
        pre_steggate_bundle=pre,
        sovereign_result=result,
        custody_record=_custody(),
        successor_state_id="external:s18",
        successor_state_hash=H7,
        exchange_path=tmp_path / "post-return.zip",
        replay=replay,
        reconstruct=reconstruct,
        organization_ledger_readback=_readback(),
        canonical_manifest_sha256=MANIFEST,
    )
    assert proof["status"] == "PASS"
    assert proof["sovereign_completion"] is True
    assert proof["interlock_return_state"] == "ACKNOWLEDGED"
    assert proof["portable_verification"]["stage"] == "POST_RETURN"
    assert proof["portable_verification"]["status"] == "PASS"
    assert proof["exchange_verification"]["status"] == "PASS"
    assert proof["replay"]["consequence_reexecuted"] is False
    assert proof["reconstruction"]["consequence_reexecuted"] is False
    assert proof["local_run_record"]["completes_transition"] is False
    assert proof["authority"]["copied_evidence_is_canonical_custody"] is False


def test_complete_post_return_evidence_does_not_need_the_local_run_store(tmp_path: Path):
    result = _sovereign_result()
    replay, reconstruct = _replay_and_reconstruct(result)
    proof = complete_post_return_evidence(
        pre_steggate_bundle=_bundle(),
        sovereign_result=result,
        successor_state_id="external:s18",
        successor_state_hash=H7,
        exchange_path=tmp_path / "post-return.zip",
        replay=replay,
        reconstruct=reconstruct,
        organization_ledger_readback=_readback(),
    )
    assert proof["status"] == "PASS"
    assert proof["local_run_record"]["status"] == "NOT_PROVIDED"


def test_local_run_store_alone_fails_closed_before_any_return_is_built(tmp_path: Path):
    def never(_receipt_id):
        raise AssertionError("no return work without an organization-ledger receipt")

    proof = complete_post_return_evidence(
        pre_steggate_bundle=_bundle(),
        sovereign_result=_sovereign_result(),
        custody_record=_custody(),
        successor_state_id="external:s18",
        successor_state_hash=H7,
        exchange_path=tmp_path / "post-return.zip",
        replay=never,
        reconstruct=never,
    )
    assert proof["status"] == "FAIL_CLOSED"
    assert proof["sovereign_completion"] is False
    assert proof["failed_predicate"] == "ORGANIZATION_LEDGER_READBACK_PRESENT"
    assert proof["retry_entrypoint"] == TRANSITION_REQUEST_ENTRYPOINT
    assert proof["local_run_record"]["status"] == "RECORDED"
    assert not (tmp_path / "post-return.zip").exists()


def test_return_fails_closed_without_real_bounded_transition():
    pre = _bundle()
    result = _sovereign_result()
    result["execution_result"]["state_transition_performed"] = False
    with pytest.raises(ValueError, match="did not perform"):
        build_pending_interlock_return(pre["ingress_interlock"], result, _completion())


def test_return_fails_closed_without_organization_ledger_receipt():
    pre = _bundle()
    refused = verify_organization_ledger_readback(_readback(refused=True))
    with pytest.raises(ValueError, match="INGRESS_RECEIPT_IS_NOT_A_REFUSAL"):
        build_pending_interlock_return(pre["ingress_interlock"], _sovereign_result(), refused)
    with pytest.raises(ValueError, match="ORGANIZATION_LEDGER_READBACK_PRESENT"):
        build_pending_interlock_return(
            pre["ingress_interlock"], _sovereign_result(), verify_organization_ledger_readback(None))
