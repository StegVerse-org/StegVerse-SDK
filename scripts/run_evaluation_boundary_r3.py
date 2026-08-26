from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Mapping

from scripts.build_evaluation_boundary_response_packet import build_packet, verify_release_receipt
from stegverse.evaluation_boundary_verifier import canonical_sha256, verify_evaluation_boundary_result
from stegverse.public_inspection import load_public_inspection_request, validate_public_inspection_request
from stegverse.sovereign_validation_runtime import (
    _components,
    reconstruct_sovereign,
    replay_sovereign,
    run_sovereign_validation,
)


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _canonical_governance_request(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Return the exact StegGate request representation hashed by the frozen runtime.

    The sovereign runtime validates the submitted request through StegCore's
    ``AdmissibilityRequest`` model and hashes ``model_dump(mode='json',
    exclude_none=False)``. Retaining the pre-model input here would create an
    apparently plausible evidence file whose hash can differ from the runtime's
    actual governance-request binding because defaults/null fields are resolved by
    the model. This helper intentionally uses the same canonical model boundary.
    """
    (_Carrier, _build, _route, _Custody, _submit, _Registry, Request, _eval, _Ledger, _run) = _components()
    return Request.model_validate(raw).model_dump(mode="json", exclude_none=False)


def _export_custody(*, custody_db: Path, governed_result: dict[str, Any], run_dir: Path) -> None:
    (_Carrier, _build, _route, Custody, _submit, _Registry, _Request, _eval, _Ledger, _run) = _components()
    custody = Custody(custody_db)

    route_manifest_id = str(governed_result.get("route_manifest_id") or "")
    manifest_receipt_id = str(governed_result.get("manifest_receipt_id") or "")
    if not route_manifest_id:
        raise RuntimeError("governed_result_missing_route_manifest_id")
    if not manifest_receipt_id:
        raise RuntimeError("governed_result_missing_manifest_receipt_id")

    route_events = custody.route_events(route_manifest_id)
    if not route_events:
        raise RuntimeError("route_receipt_chain_missing")
    for index, event in enumerate(route_events):
        _write_json(run_dir / "route-receipts" / f"{index:03d}.json", event)

    evidence = custody.evidence_package(manifest_receipt_id)
    if not isinstance(evidence, dict) or not evidence:
        raise RuntimeError("master_records_evidence_package_missing")
    _write_json(run_dir / "master-records" / "evidence-package.json", evidence)


def run_exact_r3(
    *,
    release_receipt_path: Path,
    manifest_path: Path,
    custody_db: Path,
    run_dir: Path,
    packet_dir: Path | None = None,
    host_identity: str = "stegverse-sovereign-local",
    include_replay: bool = True,
) -> dict[str, Any]:
    """Execute the frozen evaluation-boundary R3 proposition only after verified release proof exists.

    This harness adds no evaluator, route, decision semantics, credential authority,
    or custody path. It calls the canonical SDK sovereign runtime, exports evidence
    already retained by Master Records custody, records reconstruction/replay as
    separately custodied operations, and optionally invokes the fail-closed packet
    builder.
    """
    release_receipt = _load_object(release_receipt_path)
    release_check = verify_release_receipt(release_receipt)
    if not release_check.get("verified"):
        raise RuntimeError("release_receipt_not_verified:" + ",".join(release_check.get("reasons") or []))

    request = load_public_inspection_request(manifest_path)
    normalized = validate_public_inspection_request(request)
    input_block = normalized.get("input") or {}
    raw_governance_request = input_block.get("steggate_request")
    if not isinstance(raw_governance_request, Mapping):
        raise RuntimeError("normalized_manifest_missing_governance_request")
    governance_request = _canonical_governance_request(raw_governance_request)

    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    custody_db.parent.mkdir(parents=True, exist_ok=True)

    _write_json(run_dir / "normalized-manifest.json", normalized)
    _write_json(run_dir / "governance-request.json", governance_request)

    governed_result = run_sovereign_validation(
        normalized,
        custody_db=custody_db,
        host_identity=host_identity,
    )

    expected_manifest_hash = canonical_sha256(normalized)
    expected_governance_hash = canonical_sha256(governance_request)
    if governed_result.get("submitted_manifest_hash") != expected_manifest_hash:
        raise RuntimeError("runtime_submitted_manifest_binding_mismatch")
    if governed_result.get("governance_request_hash") != expected_governance_hash:
        raise RuntimeError("runtime_governance_request_binding_mismatch")

    independent = verify_evaluation_boundary_result(
        governed_result,
        normalized_manifest=normalized,
        governance_request=governance_request,
    )
    if independent.get("verification_complete") is not True or independent.get("verified") is not True:
        raise RuntimeError("runtime_binding_tuple_independent_verification_failed")

    _write_json(run_dir / "governed-result.json", governed_result)
    _write_json(run_dir / "independent-binding-verification.json", independent)
    _export_custody(custody_db=custody_db, governed_result=governed_result, run_dir=run_dir)

    manifest_receipt_id = str(governed_result["manifest_receipt_id"])
    reconstruction = reconstruct_sovereign(manifest_receipt_id, custody_db=custody_db)
    _write_json(run_dir / "reconstruction" / "reconstruction.json", reconstruction)

    replay = None
    if include_replay:
        replay = replay_sovereign(manifest_receipt_id, custody_db=custody_db)
        _write_json(run_dir / "replay" / "replay.json", replay)

    packet_result = None
    if packet_dir is not None:
        packet_result = build_packet(
            release_receipt_path=release_receipt_path,
            run_dir=run_dir,
            output_dir=packet_dir,
        )

    return {
        "status": "ok",
        "release_set_id": release_check["release_set_id"],
        "manifest_receipt_id": manifest_receipt_id,
        "transaction_id": governed_result.get("transaction_id"),
        "route_manifest_id": governed_result.get("route_manifest_id"),
        "route_transition_count": governed_result.get("route_transition_count"),
        "master_records_custody_status": governed_result.get("master_records_custody_status"),
        "independent_binding_verification_pass": True,
        "reconstruction_retained": True,
        "replay_retained": replay is not None,
        "packet": packet_result,
        "authority_granted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run and retain the exact evaluation-boundary R3 governed evaluation-boundary evidence")
    parser.add_argument("--release-receipt", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--custody-db", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--packet-dir")
    parser.add_argument("--host-identity", default="stegverse-sovereign-local")
    parser.add_argument("--no-replay", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_exact_r3(
            release_receipt_path=Path(args.release_receipt),
            manifest_path=Path(args.manifest),
            custody_db=Path(args.custody_db),
            run_dir=Path(args.run_dir),
            packet_dir=Path(args.packet_dir) if args.packet_dir else None,
            host_identity=args.host_identity,
            include_replay=not args.no_replay,
        )
    except Exception as exc:
        print(json.dumps({"status": "failed", "reason": str(exc), "authority_granted": False}, indent=2))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
