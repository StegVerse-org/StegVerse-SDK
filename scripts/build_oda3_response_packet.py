from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from stegverse.evaluation_boundary_verifier import canonical_sha256, verify_evaluation_boundary_result

ROOT = Path(__file__).resolve().parents[1]
RELEASE_SET_ID = "EVALUATION-BOUNDARY-2026-08-19-R3"
EXPECTED_COMPONENTS = {
    "StegVerse-org/StegVerse-SDK": ("v1.1.0", "922d6c5235229e854c36e1a194dc99ed15a31b51"),
    "Data-Continuation/core-lite": ("v0.9.0", "018e608018a793ee6dc62f4fdea59a3415e6e80e"),
    "StegVerse-Labs/StegCore": ("v0.2.0", "23b388ce23b08097593b5b5593eb4061e0ff5242"),
    "master-records/orchestration": ("v0.1.0", "4826f753641cc82bbb885f919494a6c1318fbae4"),
}

REQUIRED_RUN_FILES = {
    "normalized-manifest.json": "run/normalized-manifest.json",
    "governance-request.json": "run/governance-request.json",
    "governed-result.json": "run/governed-result.json",
}
REQUIRED_EVIDENCE_DIRS = ("route-receipts", "master-records", "reconstruction")
OPTIONAL_EVIDENCE_DIRS = ("replay",)
STATIC_PACKET_FILES = {
    ROOT / "docs" / "ODA3_PACKET_README_REPRODUCE.md": "README_REPRODUCE.md",
    ROOT / "docs" / "ODA3_LICENSE_ACCESS_NOTES.md": "LICENSE_ACCESS_NOTES.md",
}


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _component_rows(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    rows = receipt.get("components") or receipt.get("results") or []
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def verify_release_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if receipt.get("schema") != "stegverse.tvc.aggregate-release-receipt.v1":
        reasons.append("aggregate_receipt_schema_mismatch")
    if receipt.get("release_set_id") != RELEASE_SET_ID:
        reasons.append("aggregate_receipt_release_set_mismatch")
    if receipt.get("credential_authority") != "TV/TVC":
        reasons.append("aggregate_receipt_credential_authority_mismatch")
    if receipt.get("non_tv_tvc_credential_used") is not False:
        reasons.append("aggregate_receipt_non_tv_tvc_credential_used")
    if receipt.get("all_components_release_tag_bound") is not True:
        reasons.append("aggregate_receipt_components_not_tag_bound")

    source_validation = receipt.get("source_validation") or {}
    if not isinstance(source_validation, dict) or source_validation.get("verified") is not True:
        reasons.append("aggregate_receipt_source_validation_unverified")
    else:
        if source_validation.get("tests_passed") is not True:
            reasons.append("aggregate_receipt_source_tests_not_passed")
        if source_validation.get("guard_tests_passed") is not True:
            reasons.append("aggregate_receipt_guard_tests_not_passed")
        if source_validation.get("dispatcher_tests_passed") is not True:
            reasons.append("aggregate_receipt_dispatcher_tests_not_passed")
        if source_validation.get("non_tv_tvc_credential_used") is not False:
            reasons.append("aggregate_receipt_source_validation_non_tv_tvc_credential_used")
        if source_validation.get("release_authority") is not False:
            reasons.append("aggregate_receipt_source_validation_claimed_release_authority")
        if source_validation.get("runtime_authority") is not False:
            reasons.append("aggregate_receipt_source_validation_claimed_runtime_authority")

    observed: dict[str, tuple[str, str]] = {}
    for row in _component_rows(receipt):
        repo = str(row.get("repository") or "")
        tag = str(row.get("tag") or "")
        commit = str(row.get("commit") or row.get("commit_sha") or row.get("resolved_commit") or "")
        if repo:
            observed[repo] = (tag, commit)

    for repo, expected in EXPECTED_COMPONENTS.items():
        if observed.get(repo) != expected:
            reasons.append(f"aggregate_receipt_component_mismatch:{repo}")

    return {
        "verified": not reasons,
        "reasons": reasons or ["ok"],
        "release_set_id": RELEASE_SET_ID,
        "expected_components": EXPECTED_COMPONENTS,
    }


def _tamper_copy(value: dict[str, Any], marker: str) -> dict[str, Any]:
    copy = json.loads(json.dumps(value))
    copy["__oda3_deliberate_tamper__"] = marker
    return copy


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _nonempty_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return [path for path in directory.rglob("*") if path.is_file() and path.stat().st_size > 0]


def build_packet(*, release_receipt_path: Path, run_dir: Path, output_dir: Path) -> dict[str, Any]:
    release_receipt = _load_object(release_receipt_path)
    release_check = verify_release_receipt(release_receipt)
    if not release_check["verified"]:
        raise RuntimeError("release_receipt_not_verified:" + ",".join(release_check["reasons"]))

    missing_files = [name for name in REQUIRED_RUN_FILES if not (run_dir / name).is_file()]
    if missing_files:
        raise RuntimeError("runtime_evidence_missing:" + ",".join(sorted(missing_files)))

    missing_dirs = [name for name in REQUIRED_EVIDENCE_DIRS if not _nonempty_files(run_dir / name)]
    if missing_dirs:
        raise RuntimeError("custody_or_route_evidence_missing:" + ",".join(sorted(missing_dirs)))

    missing_static = [str(path.relative_to(ROOT)) for path in STATIC_PACKET_FILES if not path.is_file()]
    if missing_static:
        raise RuntimeError("reviewer_static_material_missing:" + ",".join(sorted(missing_static)))

    manifest = _load_object(run_dir / "normalized-manifest.json")
    governance_request = _load_object(run_dir / "governance-request.json")
    governed_result = _load_object(run_dir / "governed-result.json")

    independent = verify_evaluation_boundary_result(
        governed_result,
        normalized_manifest=manifest,
        governance_request=governance_request,
    )
    if independent.get("verification_complete") is not True or independent.get("verified") is not True:
        raise RuntimeError("independent_unmodified_verification_failed")

    manifest_tamper = _tamper_copy(manifest, "normalized-manifest")
    request_tamper = _tamper_copy(governance_request, "governance-request")
    result_tamper = _tamper_copy(governed_result, "governed-result")

    manifest_fail = verify_evaluation_boundary_result(
        governed_result,
        normalized_manifest=manifest_tamper,
        governance_request=governance_request,
    )
    request_fail = verify_evaluation_boundary_result(
        governed_result,
        normalized_manifest=manifest,
        governance_request=request_tamper,
    )
    result_fail = verify_evaluation_boundary_result(
        result_tamper,
        normalized_manifest=manifest,
        governance_request=governance_request,
    )

    expected_failures = {
        "manifest": manifest_fail["checks"]["submitted_manifest_binding"]["status"] == "FAIL",
        "governance_request": request_fail["checks"]["governance_request_binding"]["status"] == "FAIL",
        "result": result_fail["checks"]["result_binding"]["status"] == "FAIL",
    }
    if not all(expected_failures.values()):
        raise RuntimeError("deliberate_tamper_verification_did_not_fail_closed")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    shutil.copy2(release_receipt_path, output_dir / "RELEASE_SET.json")
    for source, destination in STATIC_PACKET_FILES.items():
        shutil.copy2(source, output_dir / destination)
    for source_name, destination in REQUIRED_RUN_FILES.items():
        destination_path = output_dir / destination
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(run_dir / source_name, destination_path)

    for directory in REQUIRED_EVIDENCE_DIRS + OPTIONAL_EVIDENCE_DIRS:
        source = run_dir / directory
        if source.is_dir():
            shutil.copytree(source, output_dir / "run" / directory)

    _write_json(output_dir / "verify" / "independent-pass.json", independent)
    _write_json(output_dir / "verify" / "manifest-tamper-fail.json", manifest_fail)
    _write_json(output_dir / "verify" / "governance-request-tamper-fail.json", request_fail)
    _write_json(output_dir / "verify" / "result-tamper-fail.json", result_fail)

    files = []
    for path in sorted(p for p in output_dir.rglob("*") if p.is_file()):
        if path.name == "FILE_MANIFEST.sha256.json":
            continue
        files.append({
            "path": str(path.relative_to(output_dir)),
            "sha256": _sha256_file(path),
            "bytes": path.stat().st_size,
        })
    file_manifest = {
        "schema": "stegverse.oda3-response-packet-file-manifest.v1",
        "release_set_id": RELEASE_SET_ID,
        "files": files,
        "packet_complete_for_binding_review": True,
        "required_route_custody_evidence_present": True,
        "authority_granted": False,
    }
    _write_json(output_dir / "FILE_MANIFEST.sha256.json", file_manifest)

    return {
        "status": "ok",
        "release_set_id": RELEASE_SET_ID,
        "release_receipt_verified": True,
        "route_custody_evidence_present": True,
        "independent_verification_pass": True,
        "tamper_failures": expected_failures,
        "output_dir": str(output_dir),
        "file_count": len(files) + 1,
        "authority_granted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the fail-closed ODA3 evaluation-boundary response packet")
    parser.add_argument("--release-receipt", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)
    try:
        result = build_packet(
            release_receipt_path=Path(args.release_receipt),
            run_dir=Path(args.run_dir),
            output_dir=Path(args.output_dir),
        )
    except Exception as exc:
        print(json.dumps({"status": "failed", "reason": str(exc), "authority_granted": False}, indent=2))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
