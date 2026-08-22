#!/usr/bin/env python3
"""Build and validate the shareable evaluation-boundary owner evidence packet.

This tool packages evidence only after the exact governed run exists. It grants
no release, runtime, governance, signing, custody, or credential authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

RELEASE_SET_ID = "EVALUATION-BOUNDARY-2026-08-19-R3"
RELEASE_SCHEMA = "stegverse.tvc.aggregate-release-receipt.v1"
VERIFIER_SCHEMA = "stegverse.evaluation-boundary-verification.v1"
EXPECTED_RELEASES = {
    ("StegVerse-org/StegVerse-SDK", "v1.1.0"): "922d6c5235229e854c36e1a194dc99ed15a31b51",
    ("Data-Continuation/core-lite", "v0.9.0"): "018e608018a793ee6dc62f4fdea59a3415e6e80e",
    ("StegVerse-Labs/StegCore", "v0.2.0"): "23b388ce23b08097593b5b5593eb4061e0ff5242",
    ("master-records/orchestration", "v0.1.0"): "4826f753641cc82bbb885f919494a6c1318fbae4",
}


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _release_binding_map(receipt: dict[str, Any]) -> dict[tuple[str, str], str]:
    rows = receipt.get("components")
    if not isinstance(rows, list):
        return {}
    result: dict[tuple[str, str], str] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        repo = str(row.get("repository") or "")
        tag = str(row.get("tag") or "")
        commit = str(row.get("commit") or row.get("commit_sha") or row.get("resolved_commit") or "")
        if repo and tag and commit:
            result[(repo, tag)] = commit
    return result


def validate_release_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("schema") != RELEASE_SCHEMA:
        errors.append("aggregate_release_schema_mismatch")
    if receipt.get("release_set_id") != RELEASE_SET_ID:
        errors.append("aggregate_release_set_mismatch")
    if receipt.get("credential_authority") != "TV/TVC":
        errors.append("aggregate_release_credential_authority_mismatch")
    if receipt.get("non_tv_tvc_credential_used") is not False:
        errors.append("aggregate_release_non_tvtvc_credential_boundary_failed")
    if receipt.get("all_components_release_tag_bound") is not True:
        errors.append("aggregate_release_tag_binding_incomplete")
    if receipt.get("all_declared_source_parents_verified") is not True:
        errors.append("aggregate_release_source_parent_verification_incomplete")
    source_validation = receipt.get("source_validation")
    if not isinstance(source_validation, dict) or source_validation.get("verified") is not True:
        errors.append("aggregate_release_source_validation_binding_missing")
    bindings = _release_binding_map(receipt)
    if bindings != EXPECTED_RELEASES:
        errors.append("aggregate_release_exact_binding_mismatch")
    return errors


def validate_pass_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("schema") != VERIFIER_SCHEMA:
        errors.append("independent_pass_schema_mismatch")
    if report.get("verification_complete") is not True or report.get("verified") is not True:
        errors.append("independent_pass_not_complete_verified")
    checks = report.get("checks")
    required = {"submitted_manifest_binding", "governance_request_binding", "result_binding"}
    if not isinstance(checks, dict) or set(checks) != required:
        errors.append("independent_pass_checks_incomplete")
    elif any((checks[name] or {}).get("status") != "PASS" for name in required):
        errors.append("independent_pass_contains_nonpass_check")
    if report.get("authority_granted") is not False:
        errors.append("independent_pass_authority_boundary_invalid")
    return errors


def validate_tamper_report(report: dict[str, Any], expected_failed_check: str, label: str) -> list[str]:
    errors: list[str] = []
    if report.get("schema") != VERIFIER_SCHEMA:
        errors.append(f"{label}_schema_mismatch")
        return errors
    checks = report.get("checks")
    if not isinstance(checks, dict) or (checks.get(expected_failed_check) or {}).get("status") != "FAIL":
        errors.append(f"{label}_expected_fail_not_observed")
    if report.get("verified") is not False:
        errors.append(f"{label}_unexpected_verified_true")
    if report.get("authority_granted") is not False:
        errors.append(f"{label}_authority_boundary_invalid")
    return errors


def build_owner_packet(paths: dict[str, Path], *, replay_required: bool) -> dict[str, Any]:
    errors: list[str] = []
    artifacts: list[dict[str, Any]] = []
    required_names = {
        "aggregate_release_receipt",
        "normalized_manifest",
        "governance_request",
        "sovereign_result",
        "manifest_receipt",
        "route_receipts",
        "master_records_custody",
        "reconstruction",
        "independent_pass",
        "tamper_manifest",
        "tamper_governance_request",
        "tamper_result",
    }
    if replay_required:
        required_names.add("replay")

    for name in sorted(required_names):
        path = paths.get(name)
        if path is None:
            errors.append(f"missing_argument:{name}")
            continue
        if not path.is_file():
            errors.append(f"missing_file:{name}:{path}")
            continue
        artifacts.append({
            "role": name,
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        })

    if errors:
        return _packet(errors, artifacts, replay_required)

    try:
        errors.extend(validate_release_receipt(_load_object(paths["aggregate_release_receipt"])))
        errors.extend(validate_pass_report(_load_object(paths["independent_pass"])))
        errors.extend(validate_tamper_report(
            _load_object(paths["tamper_manifest"]), "submitted_manifest_binding", "tamper_manifest"
        ))
        errors.extend(validate_tamper_report(
            _load_object(paths["tamper_governance_request"]), "governance_request_binding", "tamper_governance_request"
        ))
        errors.extend(validate_tamper_report(
            _load_object(paths["tamper_result"]), "result_binding", "tamper_result"
        ))
        # Exact run core evidence must be structured JSON objects. Their deeper
        # semantic validation remains with their canonical route/custody tools.
        for role in (
            "normalized_manifest", "governance_request", "sovereign_result",
            "manifest_receipt", "route_receipts", "master_records_custody", "reconstruction"
        ):
            _load_object(paths[role])
        if replay_required:
            _load_object(paths["replay"])
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"evidence_parse_failure:{type(exc).__name__}:{exc}")

    return _packet(errors, artifacts, replay_required)


def _packet(errors: list[str], artifacts: list[dict[str, Any]], replay_required: bool) -> dict[str, Any]:
    complete = not errors
    base = {
        "schema": "stegverse.evaluation-boundary-owner-packet.v1",
        "release_set_id": RELEASE_SET_ID,
        "sdk_version": "1.1.0",
        "sdk_commit": EXPECTED_RELEASES[("StegVerse-org/StegVerse-SDK", "v1.1.0")],
        "replay_required": replay_required,
        "complete": complete,
        "errors": errors,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "credential_authority": "TV/TVC",
        "non_tv_tvc_credential_required": False,
        "authority_granted": False,
    }
    digest_body = json.dumps(base, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    base["packet_manifest_sha256"] = "sha256:" + hashlib.sha256(digest_body).hexdigest()
    return base


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and hash the complete R3 owner evidence packet")
    parser.add_argument("--aggregate-release-receipt", required=True)
    parser.add_argument("--normalized-manifest", required=True)
    parser.add_argument("--governance-request", required=True)
    parser.add_argument("--sovereign-result", required=True)
    parser.add_argument("--manifest-receipt", required=True)
    parser.add_argument("--route-receipts", required=True)
    parser.add_argument("--master-records-custody", required=True)
    parser.add_argument("--reconstruction", required=True)
    parser.add_argument("--replay")
    parser.add_argument("--replay-required", action="store_true")
    parser.add_argument("--independent-pass", required=True)
    parser.add_argument("--tamper-manifest", required=True)
    parser.add_argument("--tamper-governance-request", required=True)
    parser.add_argument("--tamper-result", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    mapping = {
        key.replace("-", "_"): Path(value).resolve()
        for key, value in vars(args).items()
        if key not in {"output", "replay_required"} and value
    }
    packet = build_owner_packet(mapping, replay_required=bool(args.replay_required))
    rendered = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if packet["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
