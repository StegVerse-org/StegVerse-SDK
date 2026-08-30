from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from stegverse.sovereign_validation_runtime import (
    reconstruct_sovereign,
    replay_sovereign,
    run_sovereign_validation,
)

EXPECTED_MANIFEST_SHA256 = "07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f"
EXPECTED_MANIFEST_GIT_BLOB_SHA1 = "59d818a15fc7be732c97dae7d2174d8cfe9a7bab"
TEST_ID = "cross-framework-current-basis-001"
VECTOR_SCHEMA = "stegverse.cross-framework-current-basis-vector.v0.4"


class CrossFrameworkExecutionError(RuntimeError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _sha256_value(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _portable_replay_reference(manifest_receipt_id: str) -> str:
    return f"stegverse-replay:v1:{manifest_receipt_id}:{EXPECTED_MANIFEST_SHA256}"


def _replay_reference_text(
    *,
    manifest_receipt_id: str,
    transition_receipt: Mapping[str, Any],
    sovereign_result: Mapping[str, Any],
) -> str:
    portable = _portable_replay_reference(manifest_receipt_id)
    lines = (
        f"TEST_ID={TEST_ID}",
        f"MANIFEST_RECEIPT_ID={manifest_receipt_id}",
        f"MANIFEST_SHA256={EXPECTED_MANIFEST_SHA256}",
        f"MANIFEST_GIT_BLOB_SHA1={EXPECTED_MANIFEST_GIT_BLOB_SHA1}",
        f"TRANSITION_ID={transition_receipt.get('transition_id')}",
        f"TRANSITION_RECEIPT_HASH={transition_receipt.get('receipt_hash')}",
        f"STEGVERSE_RESULT_SHA256={_sha256_value(sovereign_result)}",
        f"PORTABLE_REPLAY_REFERENCE={portable}",
        f"REPLAY_REFERENCE={manifest_receipt_id}",
        f"RECONSTRUCTION_REFERENCE={manifest_receipt_id}",
    )
    return "\n".join(lines) + "\n"


def _load_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CrossFrameworkExecutionError(f"frozen manifest not found: {path}")
    observed = _sha256_file(path)
    if observed != EXPECTED_MANIFEST_SHA256:
        raise CrossFrameworkExecutionError(
            f"frozen manifest SHA-256 mismatch: expected {EXPECTED_MANIFEST_SHA256}, observed {observed}"
        )
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CrossFrameworkExecutionError("frozen manifest must be a JSON object")
    vector = ((value.get("input") or {}).get("comparison_input"))
    if not isinstance(vector, dict) or vector.get("vector_schema") != VECTOR_SCHEMA:
        raise CrossFrameworkExecutionError("frozen manifest does not contain the exact v0.4 comparison vector")
    return value


def _transition_receipt(
    *,
    vector: Mapping[str, Any],
    native_result: Mapping[str, Any],
    sovereign_result: Mapping[str, Any],
) -> dict[str, Any]:
    initial = vector["initial_state"]
    observed_at = datetime.now(timezone.utc).isoformat()
    body = {
        "schema": "stegverse.sdk.cross-framework-post-observation-transition-receipt.v1",
        "test_id": TEST_ID,
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "manifest_git_blob_sha1": EXPECTED_MANIFEST_GIT_BLOB_SHA1,
        "transition_id": vector["transition"]["transition_id"],
        "from_state_id": initial["state_id"],
        "to_state_id": vector["successor_state_observed_inputs"]["state_id"],
        "receipt_timing": "POST_OBSERVATION",
        "s0_declared_initial_test_state": True,
        "historical_s0_receipt_required": False,
        "material_change_is_invalidation_input": False,
        "s0_state_hash": _sha256_value(initial),
        "s1_observation_hash": _sha256_value(vector["successor_state_observed_inputs"]),
        "native_result_hash": _sha256_value(native_result),
        "sovereign_result_hash": _sha256_value(sovereign_result),
        "manifest_receipt_id": sovereign_result.get("manifest_receipt_id"),
        "observed_at": observed_at,
        "authority_effect": "EVIDENCE_ONLY_NO_RETROACTIVE_PERMISSION",
    }
    return {**body, "receipt_hash": _sha256_value(body)}


def execute(
    *,
    manifest_path: Path,
    custody_db: Path,
    output_dir: Path,
    host_identity: str,
) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    vector = manifest["input"]["comparison_input"]

    try:
        from stegcore.current_basis import (
            derive_admissibility_request,
            evaluate_current_basis_vector,
        )
    except ImportError as exc:
        raise CrossFrameworkExecutionError(
            "canonical merged StegCore current-basis capability is required"
        ) from exc

    native_request = derive_admissibility_request(vector)
    native_result = evaluate_current_basis_vector(vector)

    sovereign_result = run_sovereign_validation(
        manifest,
        custody_db=custody_db,
        host_identity=host_identity,
        derived_governance_request=native_request.model_dump(mode="json", exclude_none=False),
    )
    if sovereign_result.get("master_records_custody_status") != "RECORDED":
        raise CrossFrameworkExecutionError("canonical run did not establish Master Records custody")

    s1_observation = {
        "schema": "stegverse.sdk.cross-framework-s1-observation.v1",
        "test_id": TEST_ID,
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "manifest_git_blob_sha1": EXPECTED_MANIFEST_GIT_BLOB_SHA1,
        "s0_origin": "DECLARED_INITIAL_TEST_STATE",
        "s1_observed": bool(native_result.get("s1_observed") is True),
        "native_request": native_request.model_dump(mode="json", exclude_none=False),
        "native_evaluation": native_result,
        "sovereign_execution": sovereign_result,
        "counterpart_result_consumed_before_completion": False,
    }
    if not s1_observation["s1_observed"]:
        raise CrossFrameworkExecutionError("StegCore did not report S1 as observed")

    transition_receipt = _transition_receipt(
        vector=vector,
        native_result=native_result,
        sovereign_result=sovereign_result,
    )

    manifest_receipt_id = str(sovereign_result.get("manifest_receipt_id") or "").strip()
    if not manifest_receipt_id:
        raise CrossFrameworkExecutionError("canonical run returned no manifest_receipt_id")

    replay = replay_sovereign(manifest_receipt_id, custody_db=custody_db)
    reconstruction = reconstruct_sovereign(manifest_receipt_id, custody_db=custody_db)

    replay_recorded = replay.get("operation_transition_custody_status") == "RECORDED"
    reconstruction_recorded = reconstruction.get("operation_transition_custody_status") == "RECORDED"
    if not replay_recorded or not reconstruction_recorded:
        raise CrossFrameworkExecutionError("replay/reconstruction operation custody is incomplete")

    portable_replay_reference = _portable_replay_reference(manifest_receipt_id)
    replay_reference_text = _replay_reference_text(
        manifest_receipt_id=manifest_receipt_id,
        transition_receipt=transition_receipt,
        sovereign_result=sovereign_result,
    )

    _write(output_dir / "STEGVERSE_RESULT.json", sovereign_result)
    _write(output_dir / "S1_OBSERVATION.json", s1_observation)
    _write(output_dir / "S0_S1_TRANSITION_RECEIPT.json", transition_receipt)
    _write(output_dir / "REPLAY.json", replay)
    _write(output_dir / "RECONSTRUCTION.json", reconstruction)
    (output_dir / "REPLAY_REFERENCE.txt").write_text(replay_reference_text, encoding="utf-8")

    complete = {
        "schema": "stegverse.sdk.cross-framework-run-complete.v1",
        "status": "COMPLETE",
        "test_id": TEST_ID,
        "vector_schema": VECTOR_SCHEMA,
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "manifest_git_blob_sha1": EXPECTED_MANIFEST_GIT_BLOB_SHA1,
        "manifest_receipt_id": manifest_receipt_id,
        "portable_replay_reference": portable_replay_reference,
        "replay_reference_artifact": "REPLAY_REFERENCE.txt",
        "independent_execution_complete": True,
        "counterpart_result_consumed_before_completion": False,
        "s1_observed": True,
        "transition_receipt_bound": True,
        "transition_receipt_hash": transition_receipt["receipt_hash"],
        "custody_recorded": True,
        "replay_recorded": replay_recorded,
        "reconstruction_recorded": reconstruction_recorded,
        "external_side_effect": bool(sovereign_result.get("external_side_effect")),
        "github_actions_runtime_authority": False,
        "authority_effect": "EVIDENCE_ONLY",
    }
    _write(output_dir / "RUN_COMPLETE.json", complete)
    return complete


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute exact frozen current-basis v0.4 comparison through canonical StegVerse")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("inspection/examples/cross-framework-current-basis-request.draft.json"),
    )
    parser.add_argument(
        "--custody-db",
        type=Path,
        default=Path("./stegverse-master-records-validation.db"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("evidence/evaluator/cross-framework-current-basis-v0.4-result"),
    )
    parser.add_argument("--host-identity", default="stegverse-sovereign-local")
    args = parser.parse_args()
    result = execute(
        manifest_path=args.manifest,
        custody_db=args.custody_db,
        output_dir=args.output_dir,
        host_identity=args.host_identity,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
