from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import run_oda3_evaluation_boundary_r3 as harness
from stegverse.evaluation_boundary_verifier import canonical_sha256


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def test_run_harness_rejects_unverified_release_before_runtime(monkeypatch, tmp_path: Path):
    receipt = tmp_path / "receipt.json"
    manifest = tmp_path / "manifest.json"
    _write(receipt, {"schema": "wrong"})
    _write(manifest, {"schema_version": "1.0"})

    monkeypatch.setattr(
        harness,
        "run_sovereign_validation",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("runtime must not execute")),
    )

    with pytest.raises(RuntimeError, match="release_receipt_not_verified"):
        harness.run_exact_r3(
            release_receipt_path=receipt,
            manifest_path=manifest,
            custody_db=tmp_path / "custody.db",
            run_dir=tmp_path / "run",
        )


def test_run_harness_rejects_runtime_governance_binding_that_does_not_match_retained_exact_request(monkeypatch, tmp_path: Path):
    receipt_path = tmp_path / "receipt.json"
    manifest_path = tmp_path / "manifest.json"
    manifest = {
        "schema_version": "1.0",
        "request_id": "oda3-r3-binding-negative",
        "input": {"steggate_request": {"candidate": {"action": "bounded-test"}}},
    }
    canonical_request = {"candidate": {"action": "bounded-test"}, "resolved_default": None}
    result_body = {
        "submitted_manifest_hash": canonical_sha256(manifest),
        "governance_request_hash": canonical_sha256({"different": True}),
        "manifest_receipt_id": "MR-NEGATIVE",
    }
    governed = dict(result_body)
    governed["result_binding_hash"] = canonical_sha256(result_body)

    _write(receipt_path, {"schema": "stegverse.tvc.aggregate-release-receipt.v1"})
    _write(manifest_path, manifest)
    monkeypatch.setattr(harness, "verify_release_receipt", lambda value: {"verified": True, "release_set_id": "EVALUATION-BOUNDARY-2026-08-19-R3"})
    monkeypatch.setattr(harness, "load_public_inspection_request", lambda path: manifest)
    monkeypatch.setattr(harness, "validate_public_inspection_request", lambda value: manifest)
    monkeypatch.setattr(harness, "_canonical_governance_request", lambda raw: canonical_request)
    monkeypatch.setattr(harness, "run_sovereign_validation", lambda *args, **kwargs: governed)

    with pytest.raises(RuntimeError, match="runtime_governance_request_binding_mismatch"):
        harness.run_exact_r3(
            release_receipt_path=receipt_path,
            manifest_path=manifest_path,
            custody_db=tmp_path / "custody.db",
            run_dir=tmp_path / "run",
        )


def test_run_harness_retains_exact_tuple_custody_reconstruction_replay_and_packet(monkeypatch, tmp_path: Path):
    receipt_path = tmp_path / "receipt.json"
    manifest_path = tmp_path / "manifest.json"
    run_dir = tmp_path / "run"
    packet_dir = tmp_path / "packet"

    receipt = {
        "schema": "stegverse.tvc.aggregate-release-receipt.v1",
        "release_set_id": "EVALUATION-BOUNDARY-2026-08-19-R3",
    }
    manifest = {
        "schema_version": "1.0",
        "request_id": "oda3-r3-t1",
        "input": {"steggate_request": {"candidate": {"action": "bounded-test"}}},
    }
    normalized = {
        "schema_version": "1.0",
        "request_id": "oda3-r3-t1",
        "input": {"steggate_request": {"candidate": {"action": "bounded-test"}}},
    }
    canonical_request = {
        "candidate": {"action": "bounded-test"},
        "resolved_default": None,
    }
    governed_body = {
        "manifest_receipt_id": "MR-ODA3",
        "transaction_id": "TX-ODA3",
        "route_manifest_id": "RM-ODA3",
        "route_transition_count": 4,
        "master_records_custody_status": "RECORDED",
        "submitted_manifest_hash": canonical_sha256(normalized),
        "governance_request_hash": canonical_sha256(canonical_request),
    }
    governed = dict(governed_body)
    governed["result_binding_hash"] = canonical_sha256(governed_body)
    _write(receipt_path, receipt)
    _write(manifest_path, manifest)

    monkeypatch.setattr(
        harness,
        "verify_release_receipt",
        lambda value: {"verified": True, "reasons": ["ok"], "release_set_id": "EVALUATION-BOUNDARY-2026-08-19-R3"},
    )
    monkeypatch.setattr(harness, "load_public_inspection_request", lambda path: manifest)
    monkeypatch.setattr(harness, "validate_public_inspection_request", lambda value: normalized)
    monkeypatch.setattr(harness, "_canonical_governance_request", lambda raw: canonical_request)
    monkeypatch.setattr(harness, "run_sovereign_validation", lambda *args, **kwargs: governed)

    def export_custody(*, custody_db, governed_result, run_dir):
        _write(run_dir / "route-receipts" / "000.json", {"route_receipt_id": "RR-1"})
        _write(run_dir / "master-records" / "evidence-package.json", {"manifest_receipt_id": "MR-ODA3"})

    monkeypatch.setattr(harness, "_export_custody", export_custody)
    monkeypatch.setattr(
        harness,
        "reconstruct_sovereign",
        lambda rid, custody_db: {"schema": "stegverse.sovereign-reconstruction.v1", "manifest_receipt_id": rid},
    )
    monkeypatch.setattr(
        harness,
        "replay_sovereign",
        lambda rid, custody_db: {"schema": "stegverse.sovereign-replay.v1", "manifest_receipt_id": rid},
    )
    monkeypatch.setattr(
        harness,
        "build_packet",
        lambda **kwargs: {"status": "ok", "independent_verification_pass": True},
    )

    result = harness.run_exact_r3(
        release_receipt_path=receipt_path,
        manifest_path=manifest_path,
        custody_db=tmp_path / "custody.db",
        run_dir=run_dir,
        packet_dir=packet_dir,
    )

    assert result["status"] == "ok"
    assert result["manifest_receipt_id"] == "MR-ODA3"
    assert result["independent_binding_verification_pass"] is True
    assert result["reconstruction_retained"] is True
    assert result["replay_retained"] is True
    assert result["packet"]["independent_verification_pass"] is True
    assert json.loads((run_dir / "normalized-manifest.json").read_text())["request_id"] == "oda3-r3-t1"
    assert json.loads((run_dir / "governance-request.json").read_text()) == canonical_request
    assert (run_dir / "governed-result.json").is_file()
    assert (run_dir / "independent-binding-verification.json").is_file()
    assert (run_dir / "route-receipts" / "000.json").is_file()
    assert (run_dir / "master-records" / "evidence-package.json").is_file()
    assert (run_dir / "reconstruction" / "reconstruction.json").is_file()
    assert (run_dir / "replay" / "replay.json").is_file()
