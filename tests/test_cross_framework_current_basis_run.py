from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts import run_cross_framework_current_basis_v04 as harness
from stegverse.evaluation_boundary_verifier import canonical_sha256


def _write_exact_manifest(path: Path) -> dict:
    manifest = {
        "schema_version": "1.0",
        "request_id": harness.TEST_ID,
        "input": {
            "comparison_input": {
                "vector_schema": harness.VECTOR_SCHEMA,
                "initial_state": {"state_id": "S0", "standing": "DECLARED_VALID_FOR_TEST"},
                "transition": {"transition_id": "DELTA-S0-S1"},
                "successor_state_observed_inputs": {"state_id": "S1"},
            }
        },
    }
    path.write_bytes(json.dumps(manifest, sort_keys=True).encode("utf-8"))
    return manifest


def test_exact_identity_rejected_before_runtime():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        path = root / "manifest.json"
        _write_exact_manifest(path)
        with (
            patch.object(harness, "FROZEN_MANIFEST_SHA256", "0" * 64),
            patch.object(harness, "run_sovereign_validation", side_effect=AssertionError("must not run")),
        ):
            with pytest.raises(RuntimeError, match="sha256_mismatch"):
                harness.run_exact_current_basis(
                    manifest_path=path,
                    custody_db=root / "custody.db",
                    run_dir=root / "run",
                )


def test_transition_receipt_is_post_observation_and_bound_to_exact_run():
    vector = {
        "initial_state": {"state_id": "S0", "standing": "DECLARED_VALID_FOR_TEST"},
        "transition": {"transition_id": "DELTA-S0-S1", "materiality": "MATERIAL"},
        "successor_state_observed_inputs": {"state_id": "S1", "observation": "facts"},
    }
    governed = {
        "governance_state": "FAIL_CLOSED",
        "result_binding_hash": "sha256:result",
        "governance_request_hash": "sha256:request",
        "manifest_receipt_id": "MR-1",
        "transaction_id": "TX-1",
        "route_manifest_id": "RM-1",
    }
    receipt = harness._build_transition_receipt(vector=vector, governed_result=governed)
    assert receipt["source_state_id"] == "S0"
    assert receipt["successor_state_id"] == "S1"
    assert receipt["receipt_temporality"] == "POST_S1_OBSERVATION"
    assert receipt["pre_execution_receipt"] is False
    assert receipt["manifest_receipt_id"] == "MR-1"
    body = dict(receipt)
    declared = body.pop("receipt_hash")
    assert declared == canonical_sha256(body)


def test_full_harness_writes_run_complete_only_after_custody_replay_reconstruction():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        manifest_path = root / "manifest.json"
        manifest = _write_exact_manifest(manifest_path)
        raw = manifest_path.read_bytes()
        exact_sha = hashlib.sha256(raw).hexdigest()
        exact_blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        normalized = dict(manifest)
        governance_request = {
            "candidate": {
                "actor_class": "ai",
                "action": "publish_candidate",
                "target": "t",
                "scope": "evaluation",
            }
        }
        governed_body = {
            "schema": "stegverse.sovereign-production-validation-result.v1",
            "manifest_receipt_id": "MR-CURRENT-BASIS",
            "transaction_id": "TX-CURRENT-BASIS",
            "route_manifest_id": "RM-CURRENT-BASIS",
            "route_transition_count": 4,
            "master_records_custody_status": "RECORDED",
            "submitted_manifest_hash": canonical_sha256(normalized),
            "governance_request_hash": canonical_sha256(governance_request),
            "governance_request_source": "DERIVED_NATIVE_REQUEST",
            "governance_state": "FAIL_CLOSED",
            "chain_verified": True,
            "transaction_identity_continuous": True,
            "external_side_effect": False,
        }
        governed = dict(governed_body)
        governed["result_binding_hash"] = canonical_sha256(governed_body)

        def export_custody(*, custody_db, governed_result, run_dir):
            (run_dir / "route-receipts").mkdir(parents=True)
            (run_dir / "route-receipts" / "000.json").write_text("{}\n")
            (run_dir / "master-records").mkdir(parents=True)
            (run_dir / "master-records" / "evidence-package.json").write_text("{}\n")
            return {"manifest_receipt_id": "MR-CURRENT-BASIS"}

        with (
            patch.object(harness, "FROZEN_MANIFEST_SHA256", exact_sha),
            patch.object(harness, "FROZEN_MANIFEST_GIT_BLOB_SHA1", exact_blob),
            patch.object(harness, "load_public_inspection_request", return_value=manifest),
            patch.object(harness, "validate_public_inspection_request", return_value=normalized),
            patch.object(harness, "_derive_governance_request", return_value=governance_request),
            patch.object(harness, "run_sovereign_validation", return_value=governed),
            patch.object(harness, "_export_custody", side_effect=export_custody),
            patch.object(harness, "reconstruct_sovereign", return_value={"operation_transition_custody_status": "RECORDED"}),
            patch.object(harness, "replay_sovereign", return_value={"operation_transition_custody_status": "RECORDED", "consequence_reexecuted": False}),
        ):
            complete = harness.run_exact_current_basis(
                manifest_path=manifest_path,
                custody_db=root / "custody.db",
                run_dir=root / "run",
            )

        assert complete["status"] == "COMPLETE"
        assert complete["independent_execution_complete"] is True
        assert complete["s1_observed"] is True
        assert complete["transition_receipt_bound"] is True
        assert complete["custody_recorded"] is True
        assert complete["replay_recorded"] is True
        assert complete["reconstruction_recorded"] is True
        run_dir = root / "run"
        assert (run_dir / "RUN_COMPLETE.json").is_file()
        assert (run_dir / "s0-s1-transition-receipt.json").is_file()
        assert (run_dir / "master-records" / "evidence-package.json").is_file()
