from __future__ import annotations

import copy
from pathlib import Path
from unittest.mock import patch

import pytest

from stegverse.post_return_production_runner import (
    _sha256,
    derive_three_layer_request,
    run_post_return_production_proof,
    verify_coherent_release_receipt,
    verify_manifest_standing_proposition_binding,
)
from stegverse.proof_release_gate import PROOF_CAPABILITY_SCHEMA
from tests.test_portable_governance_verifier import _bundle


def _release_receipt():
    components = [
        {"repository": "StegVerse-org/StegVerse-SDK", "tag": "v-successor-sdk", "commit_sha": "1" * 40},
        {"repository": "StegVerse-Labs/StegCore", "tag": "v-successor-core", "commit_sha": "2" * 40},
        {"repository": "master-records/orchestration", "tag": "v-successor-mr", "commit_sha": "3" * 40},
    ]
    coordinates = {item["repository"]: item["commit_sha"] for item in components}
    bindings = (
        ("SDK_POST_RETURN_EVIDENCE_V1", "StegVerse-org/StegVerse-SDK", "4" * 40),
        ("STEGCORE_SPE_STANDING_BINDING_V1", "StegVerse-Labs/StegCore", "5" * 40),
        ("MASTER_RECORDS_OPERATION_CUSTODY_V1", "master-records/orchestration", "6" * 40),
    )
    body = {
        "schema": "stegverse.tvc.aggregate-release-receipt.v1",
        "release_set_id": "POST-RETURN-SUCCESSOR-TEST",
        "credential_authority": "TV/TVC",
        "non_tv_tvc_credential_used": False,
        "components": components,
        "proof_capabilities": [
            {
                "schema": PROOF_CAPABILITY_SCHEMA,
                "capability_id": capability_id,
                "repository": repository,
                "release_commit_sha": coordinates[repository],
                "feature_commit_sha": feature_commit,
                "feature_in_release_commit": True,
                "containment_verification": "ANCESTOR_OR_EQUAL",
                "authority_effect": "NONE",
            }
            for capability_id, repository, feature_commit in bindings
        ],
        "all_declared_proof_capabilities_verified": True,
    }
    return {**body, "receipt_hash": _sha256(body)}


def _admissibility_request(bundle):
    three = bundle["steggate_bridge"]["admissibility_candidate"]["three_layer_request"]
    return {
        "candidate": {
            "actor_class": "reference",
            "action": three["action"],
            "target": three["target"],
            "scope": three["scope"],
            "parameters": {},
        },
        "judgment": dict(three["judgment_conditions"]),
        "signal": dict(three["signal_admission"]),
        "execution": dict(three["execution_boundary"]),
        "capability": {"allowed": True},
        "continuity": {"required": True, "previous_receipt_verified": True},
        "approval": {"required": False},
        "permission_present": True,
        "declared_context": {},
    }


def _manifest(bundle):
    return {
        "request_id": "post-return-successor-test",
        "input": {"steggate_request": _admissibility_request(bundle), "input_data": {}},
    }


def test_successor_release_receipt_with_exact_capabilities_verifies():
    result = verify_coherent_release_receipt(_release_receipt())
    assert result["verified"] is True
    assert result["release_set_id"] == "POST-RETURN-SUCCESSOR-TEST"
    assert result["proof_capabilities"]["verified"] is True
    assert result["authority_effect"] == "NONE"


def test_historical_or_capability_free_release_fails_closed():
    receipt = _release_receipt()
    body = dict(receipt)
    body.pop("receipt_hash")
    body.pop("proof_capabilities")
    body.pop("all_declared_proof_capabilities_verified")
    receipt = {**body, "receipt_hash": _sha256(body)}
    result = verify_coherent_release_receipt(receipt)
    assert result["verified"] is False
    assert "release_proof_capabilities_not_verified" in result["reasons"]


def test_manifest_is_exactly_bound_to_pre_steggate_three_layer_proposition():
    bundle = _bundle()
    manifest = _manifest(bundle)
    derived = derive_three_layer_request(manifest["input"]["steggate_request"])
    assert derived == bundle["steggate_bridge"]["admissibility_candidate"]["three_layer_request"]
    result = verify_manifest_standing_proposition_binding(manifest, bundle)
    assert result["verified"] is True
    assert result["three_layer_request_hash"] == bundle["steggate_bridge"]["admissibility_candidate"]["three_layer_request_hash"]


def test_cross_paired_manifest_and_standing_bundle_fails_before_runtime():
    bundle = _bundle()
    manifest = _manifest(bundle)
    manifest["input"]["steggate_request"]["candidate"]["target"] = "target:different"
    with pytest.raises(ValueError, match="does not match PRE_STEGGATE"):
        verify_manifest_standing_proposition_binding(manifest, bundle)


def test_incoherent_release_stops_before_sovereign_runtime(tmp_path: Path):
    release = _release_receipt()
    release["proof_capabilities"] = []
    body = dict(release)
    body.pop("receipt_hash")
    release["receipt_hash"] = _sha256(body)
    bundle = _bundle()
    release_path = tmp_path / "release.json"
    manifest_path = tmp_path / "manifest.json"
    bundle_path = tmp_path / "pre.json"
    import json
    release_path.write_text(json.dumps(release), encoding="utf-8")
    manifest_path.write_text(json.dumps(_manifest(bundle)), encoding="utf-8")
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    with patch(
        "stegverse.post_return_production_runner.run_sovereign_validation",
        side_effect=AssertionError("runtime must not execute"),
    ):
        with pytest.raises(RuntimeError, match="release_receipt_not_coherent"):
            run_post_return_production_proof(
                release_receipt_path=release_path,
                manifest_path=manifest_path,
                pre_steggate_bundle_path=bundle_path,
                custody_db=tmp_path / "custody.db",
                state_path=tmp_path / "state.json",
                exchange_path=tmp_path / "exchange.zip",
                proof_path=tmp_path / "proof.json",
            )


def test_success_path_passes_standing_to_canonical_runtime_and_uses_direct_custody(tmp_path: Path):
    import json

    release = _release_receipt()
    bundle = _bundle()
    manifest = _manifest(bundle)
    release_path = tmp_path / "release.json"
    manifest_path = tmp_path / "manifest.json"
    bundle_path = tmp_path / "pre.json"
    proof_path = tmp_path / "proof.json"
    release_path.write_text(json.dumps(release), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    sovereign = {
        "declared_execution_context_consumed_by_canonical_runtime": True,
        "governance_state": "ALLOW",
        "master_records_custody_status": "RECORDED",
        "manifest_receipt_id": "MR-" + "A" * 64,
        "transaction_id": "tx-production-proof",
        "execution_result": {
            "schema": "stegverse.reference-bounded-consequence.v1",
            "status": "STATE_TRANSITION_RECORDED",
            "state_transition_performed": True,
            "external_side_effect": False,
            "after_state_hash": "sha256:" + "B" * 64,
        },
    }
    custody = {
        "manifest_receipt_id": sovereign["manifest_receipt_id"],
        "master_record_sha256": "C" * 64,
        "evidence_package": {"transaction_id": sovereign["transaction_id"]},
    }
    post_proof = {
        "status": "PASS",
        "interlock_return_state": "ACKNOWLEDGED",
        "portable_verification": {"status": "PASS", "stage": "POST_RETURN"},
        "exchange_verification": {"status": "PASS"},
        "replay": {"operation_transition_custody_status": "RECORDED", "consequence_reexecuted": False},
        "reconstruction": {"operation_transition_custody_status": "RECORDED", "consequence_reexecuted": False},
    }
    captured = {}

    def sovereign_run(request, **kwargs):
        captured["standing_context"] = kwargs.get("declared_execution_context")
        captured["consequence_executor"] = kwargs.get("consequence_executor")
        captured["route_purpose"] = kwargs.get("route_purpose")
        return copy.deepcopy(sovereign)

    with (
        patch("stegverse.post_return_production_runner.load_public_inspection_request", return_value=manifest),
        patch("stegverse.post_return_production_runner.validate_public_inspection_request", return_value=manifest),
        patch("stegverse.post_return_production_runner.run_sovereign_validation", side_effect=sovereign_run),
        patch("stegverse.post_return_production_runner._custody_record", return_value=custody) as custody_lookup,
        patch("stegverse.post_return_production_runner.complete_post_return_evidence", return_value=post_proof) as complete,
    ):
        result = run_post_return_production_proof(
            release_receipt_path=release_path,
            manifest_path=manifest_path,
            pre_steggate_bundle_path=bundle_path,
            custody_db=tmp_path / "custody.db",
            state_path=tmp_path / "state.json",
            exchange_path=tmp_path / "exchange.zip",
            proof_path=proof_path,
        )

    assert result["status"] == "PASS"
    assert result["manifest_receipt_id"] == sovereign["manifest_receipt_id"]
    assert captured["standing_context"]["standing_required"] is True
    assert captured["standing_context"]["authority"]["execution_authorized"] is False
    assert callable(captured["consequence_executor"])
    assert captured["route_purpose"] == "post-return-production-proof"
    custody_lookup.assert_called_once_with(tmp_path / "custody.db", sovereign["manifest_receipt_id"])
    assert complete.call_args.kwargs["custody_record"] == custody
    assert complete.call_args.kwargs["sovereign_result"] == sovereign
    assert proof_path.is_file()
    retained = json.loads(proof_path.read_text(encoding="utf-8"))
    assert retained["post_return_proof"]["interlock_return_state"] == "ACKNOWLEDGED"
    assert retained["authority"]["copied_exchange_is_canonical_custody"] is False
