from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.build_evaluation_boundary_response_packet import build_packet
from stegverse.evaluation_boundary_verifier import canonical_sha256


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _release_receipt() -> dict:
    components = [
        {"repository": "StegVerse-org/StegVerse-SDK", "tag": "v1.1.0", "commit": "922d6c5235229e854c36e1a194dc99ed15a31b51"},
        {"repository": "Data-Continuation/core-lite", "tag": "v0.9.0", "commit": "018e608018a793ee6dc62f4fdea59a3415e6e80e"},
        {"repository": "StegVerse-Labs/StegCore", "tag": "v0.2.0", "commit": "23b388ce23b08097593b5b5593eb4061e0ff5242"},
        {"repository": "master-records/orchestration", "tag": "v0.1.0", "commit": "4826f753641cc82bbb885f919494a6c1318fbae4"},
    ]
    return {
        "schema": "stegverse.tvc.aggregate-release-receipt.v1",
        "release_set_id": "EVALUATION-BOUNDARY-2026-08-19-R3",
        "credential_authority": "TV/TVC",
        "non_tv_tvc_credential_used": False,
        "all_components_release_tag_bound": True,
        "components": components,
        "source_validation": {
            "verified": True,
            "tests_passed": True,
            "guard_tests_passed": True,
            "dispatcher_tests_passed": True,
            "non_tv_tvc_credential_used": False,
            "release_authority": False,
            "runtime_authority": False,
        },
    }


def _runtime_tuple(run_dir: Path, *, with_custody: bool = True) -> None:
    manifest = {"schema_version": "1.0", "request_id": "evaluation_boundary-r3-t1", "authority_claim": False}
    governance_request = {"candidate": {"action": "bounded-test"}, "permission_present": False}
    result_body = {
        "submitted_manifest_hash": canonical_sha256(manifest),
        "governance_request_hash": canonical_sha256(governance_request),
        "disposition": "ALLOW",
        "authority_effect": "NONE",
    }
    result = dict(result_body)
    result["result_binding_hash"] = canonical_sha256(result_body)
    _write(run_dir / "normalized-manifest.json", manifest)
    _write(run_dir / "governance-request.json", governance_request)
    _write(run_dir / "governed-result.json", result)
    if with_custody:
        _write(run_dir / "route-receipts" / "route.json", {"schema": "test.route-receipt", "recorded": True})
        _write(run_dir / "master-records" / "custody.json", {"schema": "test.master-record", "recorded": True})
        _write(run_dir / "reconstruction" / "reconstruction.json", {"schema": "test.reconstruction", "verified": True})


def test_packet_builder_fails_when_runtime_evidence_is_missing(tmp_path: Path):
    receipt_path = tmp_path / "receipt.json"
    _write(receipt_path, _release_receipt())
    with pytest.raises(RuntimeError, match="runtime_evidence_missing"):
        build_packet(release_receipt_path=receipt_path, run_dir=tmp_path / "run", output_dir=tmp_path / "packet")


def test_packet_builder_rejects_release_receipt_without_guard_suite_pass(tmp_path: Path):
    receipt = _release_receipt()
    receipt["source_validation"].pop("guard_tests_passed")
    receipt_path = tmp_path / "receipt.json"
    _write(receipt_path, receipt)
    _runtime_tuple(tmp_path / "run")
    with pytest.raises(RuntimeError, match="aggregate_receipt_guard_tests_not_passed"):
        build_packet(release_receipt_path=receipt_path, run_dir=tmp_path / "run", output_dir=tmp_path / "packet")


def test_packet_builder_rejects_release_receipt_without_dispatcher_suite_pass(tmp_path: Path):
    receipt = _release_receipt()
    receipt["source_validation"].pop("dispatcher_tests_passed")
    receipt_path = tmp_path / "receipt.json"
    _write(receipt_path, receipt)
    _runtime_tuple(tmp_path / "run")
    with pytest.raises(RuntimeError, match="aggregate_receipt_dispatcher_tests_not_passed"):
        build_packet(release_receipt_path=receipt_path, run_dir=tmp_path / "run", output_dir=tmp_path / "packet")


def test_packet_builder_fails_without_route_custody_and_reconstruction_evidence(tmp_path: Path):
    receipt_path = tmp_path / "receipt.json"
    run_dir = tmp_path / "run"
    _write(receipt_path, _release_receipt())
    _runtime_tuple(run_dir, with_custody=False)
    with pytest.raises(RuntimeError, match="custody_or_route_evidence_missing"):
        build_packet(release_receipt_path=receipt_path, run_dir=run_dir, output_dir=tmp_path / "packet")


def test_packet_builder_emits_independent_pass_tamper_fails_and_file_manifest(tmp_path: Path):
    receipt_path = tmp_path / "receipt.json"
    run_dir = tmp_path / "run"
    packet_dir = tmp_path / "packet"
    _write(receipt_path, _release_receipt())
    _runtime_tuple(run_dir)

    result = build_packet(release_receipt_path=receipt_path, run_dir=run_dir, output_dir=packet_dir)

    assert result["status"] == "ok"
    assert result["release_receipt_verified"] is True
    assert result["route_custody_evidence_present"] is True
    assert result["independent_verification_pass"] is True
    assert result["tamper_failures"] == {"manifest": True, "governance_request": True, "result": True}
    assert (packet_dir / "README_REPRODUCE.md").is_file()
    assert (packet_dir / "LICENSE_ACCESS_NOTES.md").is_file()
    assert (packet_dir / "run" / "route-receipts" / "route.json").is_file()
    assert (packet_dir / "run" / "master-records" / "custody.json").is_file()
    assert (packet_dir / "run" / "reconstruction" / "reconstruction.json").is_file()
    assert (packet_dir / "verify" / "independent-pass.json").is_file()
    assert (packet_dir / "verify" / "manifest-tamper-fail.json").is_file()
    assert (packet_dir / "verify" / "governance-request-tamper-fail.json").is_file()
    assert (packet_dir / "verify" / "result-tamper-fail.json").is_file()
    file_manifest = json.loads((packet_dir / "FILE_MANIFEST.sha256.json").read_text(encoding="utf-8"))
    assert file_manifest["packet_complete_for_binding_review"] is True
    assert file_manifest["required_route_custody_evidence_present"] is True
    assert file_manifest["authority_granted"] is False
