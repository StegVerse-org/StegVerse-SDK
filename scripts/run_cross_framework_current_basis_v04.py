from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Mapping

from stegverse.evaluation_boundary_verifier import canonical_sha256, verify_evaluation_boundary_result
from stegverse.public_inspection import load_public_inspection_request, validate_public_inspection_request
from stegverse.sovereign_validation_runtime import (
    _components,
    reconstruct_sovereign,
    replay_sovereign,
    run_sovereign_validation,
)

FROZEN_MANIFEST_SHA256 = "07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f"
FROZEN_MANIFEST_GIT_BLOB_SHA1 = "59d818a15fc7be732c97dae7d2174d8cfe9a7bab"
VECTOR_SCHEMA = "stegverse.cross-framework-current-basis-vector.v0.4"
TEST_ID = "cross-framework-current-basis-001"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _exact_file_identity(path: Path) -> tuple[str, str]:
    body = path.read_bytes()
    sha256 = hashlib.sha256(body).hexdigest()
    blob_header = f"blob {len(body)}\0".encode("utf-8")
    blob_sha1 = hashlib.sha1(blob_header + body).hexdigest()
    return sha256, blob_sha1


def _canonical_request(value: Mapping[str, Any]) -> dict[str, Any]:
    (_Carrier, _build, _route, _Custody, _submit, _Registry, Request, _eval, _Ledger, _run) = _components()
    return Request.model_validate(dict(value)).model_dump(mode="json", exclude_none=False)


def _derive_governance_request(vector: Mapping[str, Any]) -> dict[str, Any]:
    try:
        from stegcore.current_basis import derive_admissibility_request
    except ImportError as exc:
        raise RuntimeError("canonical_stegcore_current_basis_capability_unavailable") from exc
    request = derive_admissibility_request(dict(vector))
    return _canonical_request(request.model_dump(mode="json", exclude_none=False))


def _export_custody(*, custody_db: Path, governed_result: dict[str, Any], run_dir: Path) -> dict[str, Any]:
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
    return evidence


def _build_transition_receipt(
    *,
    vector: Mapping[str, Any],
    governed_result: Mapping[str, Any],
) -> dict[str, Any]:
    initial = vector["initial_state"]
    successor = vector["successor_state_observed_inputs"]
    transition = vector["transition"]
    body = {
        "schema": "stegverse.cross-framework.s0-s1-transition-receipt.v1",
        "test_id": TEST_ID,
        "vector_schema": VECTOR_SCHEMA,
        "frozen_manifest_sha256": FROZEN_MANIFEST_SHA256,
        "frozen_manifest_git_blob_sha1": FROZEN_MANIFEST_GIT_BLOB_SHA1,
        "source_state_id": initial["state_id"],
        "source_state_hash": canonical_sha256(initial),
        "transition_id": transition["transition_id"],
        "transition_definition_hash": canonical_sha256(transition),
        "successor_state_id": successor["state_id"],
        "successor_observed_input_hash": canonical_sha256(successor),
        "observation_complete": True,
        "governance_state": governed_result.get("governance_state"),
        "governance_result_binding_hash": governed_result.get("result_binding_hash"),
        "governance_request_hash": governed_result.get("governance_request_hash"),
        "manifest_receipt_id": governed_result.get("manifest_receipt_id"),
        "transaction_id": governed_result.get("transaction_id"),
        "route_manifest_id": governed_result.get("route_manifest_id"),
        "receipt_temporality": "POST_S1_OBSERVATION",
        "pre_execution_receipt": False,
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
    return {**body, "receipt_hash": canonical_sha256(body)}


def run_exact_current_basis(
    *,
    manifest_path: Path,
    custody_db: Path,
    run_dir: Path,
    host_identity: str = "stegverse-sovereign-local",
) -> dict[str, Any]:
    exact_sha256, exact_blob = _exact_file_identity(manifest_path)
    if exact_sha256 != FROZEN_MANIFEST_SHA256:
        raise RuntimeError("frozen_manifest_sha256_mismatch")
    if exact_blob != FROZEN_MANIFEST_GIT_BLOB_SHA1:
        raise RuntimeError("frozen_manifest_git_blob_mismatch")

    request = load_public_inspection_request(manifest_path)
    normalized = validate_public_inspection_request(request)
    if normalized.get("request_id") != TEST_ID:
        raise RuntimeError("unexpected_test_id")
    input_block = normalized.get("input")
    if not isinstance(input_block, Mapping):
        raise RuntimeError("normalized_manifest_missing_input")
    vector = input_block.get("comparison_input")
    if not isinstance(vector, Mapping) or vector.get("vector_schema") != VECTOR_SCHEMA:
        raise RuntimeError("normalized_manifest_missing_exact_v04_vector")

    governance_request = _derive_governance_request(vector)

    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    custody_db.parent.mkdir(parents=True, exist_ok=True)

    # Preserve the exact approved bytes, not a re-serialized substitute.
    shutil.copyfile(manifest_path, run_dir / "frozen-manifest-v0.4.json")
    _write_json(run_dir / "normalized-manifest.json", normalized)
    _write_json(run_dir / "stegcore-native-governance-request.json", governance_request)

    execution_context = {
        "test_id": TEST_ID,
        "vector_schema": VECTOR_SCHEMA,
        "frozen_manifest_sha256": FROZEN_MANIFEST_SHA256,
        "frozen_manifest_git_blob_sha1": FROZEN_MANIFEST_GIT_BLOB_SHA1,
        "s0_origin": "DECLARED_INITIAL_TEST_STATE",
        "prior_state_supplied": False,
        "transition_receipt_pre_execution_input": False,
    }

    governed_result = run_sovereign_validation(
        normalized,
        custody_db=custody_db,
        host_identity=host_identity,
        derived_governance_request=governance_request,
        declared_execution_context=execution_context,
        route_source="StegVerse-SDK:cross-framework-current-basis-v0.4",
        route_purpose="independent-cross-framework-current-basis-evaluation",
    )
    if governed_result.get("governance_request_source") != "DERIVED_NATIVE_REQUEST":
        raise RuntimeError("runtime_did_not_consume_derived_native_request")
    if governed_result.get("master_records_custody_status") != "RECORDED":
        raise RuntimeError("master_records_custody_not_recorded")
    if governed_result.get("chain_verified") is not True:
        raise RuntimeError("stegcore_chain_not_verified")
    if governed_result.get("transaction_identity_continuous") is not True:
        raise RuntimeError("transaction_identity_not_continuous")

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

    transition_receipt = _build_transition_receipt(vector=vector, governed_result=governed_result)
    _write_json(run_dir / "s0-s1-transition-receipt.json", transition_receipt)

    manifest_receipt_id = str(governed_result["manifest_receipt_id"])
    reconstruction = reconstruct_sovereign(manifest_receipt_id, custody_db=custody_db)
    if reconstruction.get("operation_transition_custody_status") != "RECORDED":
        raise RuntimeError("reconstruction_operation_custody_not_recorded")
    _write_json(run_dir / "reconstruction" / "reconstruction.json", reconstruction)

    replay = replay_sovereign(manifest_receipt_id, custody_db=custody_db)
    if replay.get("operation_transition_custody_status") != "RECORDED":
        raise RuntimeError("replay_operation_custody_not_recorded")
    if replay.get("consequence_reexecuted") is not False:
        raise RuntimeError("replay_reexecuted_consequence")
    _write_json(run_dir / "replay" / "replay.json", replay)

    complete = {
        "schema": "stegverse.cross-framework.current-basis-run-complete.v1",
        "status": "COMPLETE",
        "test_id": TEST_ID,
        "vector_schema": VECTOR_SCHEMA,
        "manifest_sha256": FROZEN_MANIFEST_SHA256,
        "manifest_git_blob_sha1": FROZEN_MANIFEST_GIT_BLOB_SHA1,
        "independent_execution_complete": True,
        "s1_observed": True,
        "transition_receipt_bound": True,
        "custody_recorded": True,
        "replay_recorded": True,
        "reconstruction_recorded": True,
        "manifest_receipt_id": manifest_receipt_id,
        "transaction_id": governed_result.get("transaction_id"),
        "route_manifest_id": governed_result.get("route_manifest_id"),
        "governance_state": governed_result.get("governance_state"),
        "governance_result_binding_hash": governed_result.get("result_binding_hash"),
        "transition_receipt_hash": transition_receipt["receipt_hash"],
        "authority_granted": False,
        "external_side_effect": governed_result.get("external_side_effect"),
    }
    _write_json(run_dir / "RUN_COMPLETE.json", complete)
    return complete


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Execute the exact frozen cross-framework current-basis v0.4 test through canonical StegVerse governance."
    )
    parser.add_argument(
        "--manifest",
        default="inspection/examples/cross-framework-current-basis-request.draft.json",
    )
    parser.add_argument("--custody-db", required=True)
    parser.add_argument(
        "--run-dir",
        default="evidence/evaluator/cross-framework-current-basis-v0.4-result",
    )
    parser.add_argument("--host-identity", default="stegverse-sovereign-local")
    args = parser.parse_args(argv)
    try:
        result = run_exact_current_basis(
            manifest_path=Path(args.manifest),
            custody_db=Path(args.custody_db),
            run_dir=Path(args.run_dir),
            host_identity=args.host_identity,
        )
    except Exception as exc:
        print(json.dumps({"status": "FAILED", "reason": str(exc), "authority_granted": False}, indent=2))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
