import json
from pathlib import Path

from scripts.build_evaluation_boundary_owner_packet import (
    EXPECTED_RELEASES,
    RELEASE_SET_ID,
    build_owner_packet,
)


def _write(path: Path, value: dict) -> Path:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


def _verification(*, failed_check: str | None = None) -> dict:
    checks = {
        "submitted_manifest_binding": {"status": "PASS"},
        "governance_request_binding": {"status": "PASS"},
        "result_binding": {"status": "PASS"},
    }
    if failed_check:
        checks[failed_check] = {"status": "FAIL"}
    return {
        "schema": "stegverse.evaluation-boundary-verification.v1",
        "verification_complete": True,
        "verified": failed_check is None,
        "checks": checks,
        "authority_granted": False,
    }


def _release_receipt() -> dict:
    components = [
        {"repository": repo, "tag": tag, "commit": commit}
        for (repo, tag), commit in EXPECTED_RELEASES.items()
    ]
    return {
        "schema": "stegverse.tvc.aggregate-release-receipt.v1",
        "release_set_id": RELEASE_SET_ID,
        "credential_authority": "TV/TVC",
        "non_tv_tvc_credential_used": False,
        "all_components_release_tag_bound": True,
        "all_declared_source_parents_verified": True,
        "source_validation": {"verified": True},
        "components": components,
    }


def _paths(tmp_path: Path) -> dict[str, Path]:
    values = {
        "aggregate_release_receipt": _release_receipt(),
        "normalized_manifest": {"schema": "manifest"},
        "governance_request": {"schema": "request"},
        "sovereign_result": {"schema": "result"},
        "manifest_receipt": {"schema": "manifest-receipt"},
        "route_receipts": {"schema": "route-receipts"},
        "master_records_custody": {"schema": "custody"},
        "reconstruction": {"schema": "reconstruction"},
        "replay": {"schema": "replay"},
        "independent_pass": _verification(),
        "tamper_manifest": _verification(failed_check="submitted_manifest_binding"),
        "tamper_governance_request": _verification(failed_check="governance_request_binding"),
        "tamper_result": _verification(failed_check="result_binding"),
    }
    return {name: _write(tmp_path / f"{name}.json", value) for name, value in values.items()}


def test_complete_owner_packet_requires_exact_release_and_falsification_evidence(tmp_path):
    packet = build_owner_packet(_paths(tmp_path), replay_required=True)
    assert packet["complete"] is True
    assert packet["errors"] == []
    assert packet["release_set_id"] == RELEASE_SET_ID
    assert packet["sdk_version"] == "1.1.0"
    assert packet["artifact_count"] == 13
    assert packet["authority_granted"] is False
    assert packet["non_tv_tvc_credential_required"] is False
    assert packet["packet_manifest_sha256"].startswith("sha256:")


def test_packet_fails_closed_when_release_binding_is_wrong(tmp_path):
    paths = _paths(tmp_path)
    receipt = json.loads(paths["aggregate_release_receipt"].read_text())
    receipt["components"][0]["commit"] = "0" * 40
    _write(paths["aggregate_release_receipt"], receipt)
    packet = build_owner_packet(paths, replay_required=False)
    assert packet["complete"] is False
    assert "aggregate_release_exact_binding_mismatch" in packet["errors"]


def test_packet_fails_closed_when_expected_tamper_is_not_detected(tmp_path):
    paths = _paths(tmp_path)
    _write(paths["tamper_result"], _verification())
    packet = build_owner_packet(paths, replay_required=False)
    assert packet["complete"] is False
    assert "tamper_result_expected_fail_not_observed" in packet["errors"]
    assert "tamper_result_unexpected_verified_true" in packet["errors"]


def test_packet_requires_replay_only_when_requested(tmp_path):
    paths = _paths(tmp_path)
    paths.pop("replay")
    optional = build_owner_packet(paths, replay_required=False)
    assert optional["complete"] is True
    required = build_owner_packet(paths, replay_required=True)
    assert required["complete"] is False
    assert "missing_argument:replay" in required["errors"]
