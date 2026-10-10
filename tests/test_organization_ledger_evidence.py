import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path

import pytest

from stegverse.organization_ledger_evidence import (
    COMPLETION_SCHEMA,
    OWNING_EXISTING_GOAL,
    READBACK_SCHEMA,
    TRANSITION_REQUEST_ENTRYPOINT,
    main,
    verify_organization_ledger_readback,
)
from stegverse.post_return_evidence import complete_post_return_evidence
from tests.test_portable_governance_verifier import _bundle
from tests.organization_ledger_fixture import MANIFEST, OTHER_MANIFEST, _readback, _sha
from tests.test_post_return_evidence import _custody, _sovereign_result

SIX_FIELDS = (
    "failure_code",
    "failed_predicate",
    "required_evidence_or_repair",
    "retry_entrypoint",
    "owning_existing_goal",
    "next_attempt",
)
def _assert_fail_closed(result, predicate):
    assert result["schema"] == COMPLETION_SCHEMA
    assert result["disposition"] == "FAIL_CLOSED"
    assert result["sovereign_completion"] is False
    for field in SIX_FIELDS:
        assert result[field], field
    assert result["owning_existing_goal"] == OWNING_EXISTING_GOAL
    assert result["failed_predicate"] == predicate
    assert result["master_records_gating"] is False


def test_allow_for_admitted_receipt_in_chain_bound_to_manifest():
    readback = _readback()
    result = verify_organization_ledger_readback(
        readback,
        organization_receipt_sha256=readback["head_receipt_sha256"],
        canonical_manifest_sha256=MANIFEST,
    )
    assert result["disposition"] == "ALLOW"
    assert result["sovereign_completion"] is True
    assert result["organization_receipt_sha256"] == readback["head_receipt_sha256"]
    assert result["canonical_manifest_sha256"] == "sha256:" + MANIFEST
    assert result["chain_length"] == 2
    assert result["master_records_gating"] is False
    assert "failure_code" not in result


def test_missing_readback_fails_closed_with_six_fields():
    result = verify_organization_ledger_readback(None)
    _assert_fail_closed(result, "ORGANIZATION_LEDGER_READBACK_PRESENT")
    # No transition exists yet: the repair is a manifest-directed transition request.
    assert result["retry_entrypoint"] == TRANSITION_REQUEST_ENTRYPOINT
    assert ".stegverse/transition-requests/" in result["retry_entrypoint"]


def test_local_master_records_custody_is_not_a_readback():
    custody = {"schema": "stegverse.master-records.manifest-receipt-custody.v1", "custody_status": "RECORDED"}
    _assert_fail_closed(verify_organization_ledger_readback(custody), "ORGANIZATION_LEDGER_READBACK_SCHEMA")


def test_wrong_manifest_fails_closed():
    _assert_fail_closed(
        verify_organization_ledger_readback(_readback(), canonical_manifest_sha256=OTHER_MANIFEST),
        "RECEIPT_IS_BOUND_TO_THE_EXPECTED_MANIFEST",
    )
    unbound = _readback()
    unbound["chain"][1]["predecessor_org_state_sha256"] = "sha256:" + OTHER_MANIFEST
    _assert_fail_closed(verify_organization_ledger_readback(unbound), "RECEIPT_IS_BOUND_TO_THE_SUBMITTED_MANIFEST")


def test_refused_receipt_is_not_completion():
    _assert_fail_closed(verify_organization_ledger_readback(_readback(refused=True)), "INGRESS_RECEIPT_IS_NOT_A_REFUSAL")


@pytest.mark.parametrize(
    "mutate,predicate",
    [
        (lambda r: r.update(disposition="FAIL_CLOSED"), "ORGANIZATION_LEDGER_READBACK_ALLOWED"),
        (lambda r: r.update(ingress_organization_receipt_sha256=_sha("elsewhere")), "INGRESS_RECEIPT_IS_IN_THE_ORGANIZATION_LEDGER"),
        (lambda r: r.pop("ingress_organization_receipt_sha256"), "INGRESS_RECEIPT_IS_IN_THE_ORGANIZATION_LEDGER"),
        (lambda r: r["chain"][1].update(previous_receipt_sha256=_sha("fork")), "ORGANIZATION_LEDGER_CHAIN_IS_LINKED"),
        (lambda r: r.update(head_receipt_sha256=_sha("genesis")), "ORGANIZATION_LEDGER_HEAD_IS_CHAIN_TIP"),
        (lambda r: r.update(every_source_receipt_retained_and_verifies=False), "SOURCE_RECEIPT_RETAINED_AND_VERIFIES"),
        (lambda r: r.update(master_records_awaited=True), "MASTER_RECORDS_NOT_AWAITED"),
    ],
)
def test_readback_defects_fail_closed(mutate, predicate):
    readback = _readback()
    mutate(readback)
    _assert_fail_closed(verify_organization_ledger_readback(readback), predicate)


def test_wrong_expected_receipt_fails_closed():
    _assert_fail_closed(
        verify_organization_ledger_readback(_readback(), organization_receipt_sha256=_sha("genesis")),
        "INGRESS_RECEIPT_IS_THE_EXPECTED_RECEIPT",
    )


def test_cli_exit_codes(tmp_path: Path):
    path = tmp_path / "readback.json"
    path.write_text(json.dumps(_readback()), encoding="utf-8")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        assert main(["--readback", str(path), "--canonical-manifest-sha256", MANIFEST]) == 0
    assert json.loads(out.getvalue())["disposition"] == "ALLOW"
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        assert main(["--readback", str(tmp_path / "absent.json")]) == 1
    assert json.loads(out.getvalue())["failed_predicate"] == "ORGANIZATION_LEDGER_READBACK_PRESENT"


def _complete(tmp_path: Path, readback):
    result = _sovereign_result()

    def replay(receipt_id):
        return {"manifest_receipt_id": receipt_id, "deterministic_disposition_match": True,
                "consequence_reexecuted": False, "original_record_mutated": False,
                "operation_transition_custody_status": "RECORDED"}

    def reconstruct(receipt_id):
        return {"manifest_receipt_id": receipt_id, "transaction_id": result["transaction_id"],
                "consequence_reexecuted": False, "original_record_mutated": False,
                "operation_transition_custody_status": "RECORDED"}

    return complete_post_return_evidence(
        pre_steggate_bundle=_bundle(),
        sovereign_result=result,
        custody_record=_custody(),
        successor_state_id="external:s18",
        successor_state_hash="sha256:" + "7" * 64,
        exchange_path=tmp_path / "post-return.zip",
        replay=replay,
        reconstruct=reconstruct,
        organization_ledger_readback=readback,
        canonical_manifest_sha256=MANIFEST if readback else None,
    )


def test_post_return_local_custody_recorded_alone_is_not_sovereign_completion(tmp_path: Path):
    proof = _complete(tmp_path, None)
    assert proof["local_evidence_status"] == "NOT_EVALUATED"
    assert proof["local_run_record"]["status"] == "RECORDED"
    assert proof["local_run_record"]["completes_transition"] is False
    assert proof["status"] == "FAIL_CLOSED"
    assert proof["sovereign_completion"] is False
    for field in SIX_FIELDS:
        assert proof[field], field


def test_post_return_completes_on_organization_ledger_readback(tmp_path: Path):
    proof = _complete(tmp_path, copy.deepcopy(_readback()))
    assert proof["status"] == "PASS"
    assert proof["sovereign_completion"] is True
    assert proof["organization_ledger_completion"]["disposition"] == "ALLOW"
    assert "failure_code" not in proof
