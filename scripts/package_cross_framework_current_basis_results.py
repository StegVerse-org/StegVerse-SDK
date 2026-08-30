from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

EXPECTED_MANIFEST_SHA256 = "07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f"
EXPECTED_MANIFEST_BLOB_SHA1 = "59d818a15fc7be732c97dae7d2174d8cfe9a7bab"
TEST_ID = "cross-framework-current-basis-001"

REQUIRED_COMPLETE_FLAGS = {
    "independent_execution_complete": True,
    "s1_observed": True,
    "transition_receipt_bound": True,
    "custody_recorded": True,
    "replay_recorded": True,
    "reconstruction_recorded": True,
    "counterpart_result_consumed_before_completion": False,
    "external_side_effect": False,
    "github_actions_runtime_authority": False,
}
REQUIRED_EVIDENCE_FILES = (
    "STEGVERSE_RESULT.json",
    "S1_OBSERVATION.json",
    "S0_S1_TRANSITION_RECEIPT.json",
    "REPLAY.json",
    "RECONSTRUCTION.json",
    "REPLAY_REFERENCE.txt",
    "RUN_COMPLETE.json",
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical_value_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _parse_reference_text(path: Path) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "=" not in line:
            raise RuntimeError("REPLAY_REFERENCE.txt contains a non-copyable line")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            raise RuntimeError("REPLAY_REFERENCE.txt contains an empty key or value")
        parsed[key] = value
    return parsed


def package_results(*, result_dir: Path, manifest_path: Path, output_dir: Path) -> dict[str, Any]:
    sentinel = result_dir / "RUN_COMPLETE.json"
    if not sentinel.exists():
        raise RuntimeError("RUN_COMPLETE.json missing; authentic run is not publication-ready")

    complete = _load_json(sentinel)
    if complete.get("status") != "COMPLETE":
        raise RuntimeError("RUN_COMPLETE.json status must be COMPLETE")
    if complete.get("manifest_sha256") != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("completed run is not bound to the frozen v0.4 SHA-256")
    if complete.get("manifest_git_blob_sha1") != EXPECTED_MANIFEST_BLOB_SHA1:
        raise RuntimeError("completed run is not bound to the frozen v0.4 Git blob")
    for field, expected in REQUIRED_COMPLETE_FLAGS.items():
        if complete.get(field) is not expected:
            raise RuntimeError(f"RUN_COMPLETE.json missing completion proof: {field}")

    if not manifest_path.exists():
        raise RuntimeError("frozen manifest path missing")
    if _sha256(manifest_path) != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("working manifest bytes do not match frozen v0.4 identity")

    missing = [name for name in REQUIRED_EVIDENCE_FILES if not (result_dir / name).is_file()]
    if missing:
        raise RuntimeError("result directory missing required authentic evidence: " + ",".join(missing))

    stegverse_result = _load_json(result_dir / "STEGVERSE_RESULT.json")
    s1 = _load_json(result_dir / "S1_OBSERVATION.json")
    transition = _load_json(result_dir / "S0_S1_TRANSITION_RECEIPT.json")
    replay = _load_json(result_dir / "REPLAY.json")
    reconstruction = _load_json(result_dir / "RECONSTRUCTION.json")
    replay_reference = _parse_reference_text(result_dir / "REPLAY_REFERENCE.txt")

    if s1.get("manifest_sha256") != EXPECTED_MANIFEST_SHA256 or s1.get("s1_observed") is not True:
        raise RuntimeError("S1 observation is not bound to the frozen v0.4 run")
    if s1.get("counterpart_result_consumed_before_completion") is not False:
        raise RuntimeError("S1 observation violates independent execution isolation")
    if transition.get("manifest_sha256") != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("transition receipt is not bound to the frozen v0.4 run")
    if transition.get("receipt_timing") != "POST_OBSERVATION":
        raise RuntimeError("transition receipt is not post-observation evidence")
    if transition.get("receipt_hash") != complete.get("transition_receipt_hash"):
        raise RuntimeError("RUN_COMPLETE transition receipt hash mismatch")

    manifest_receipt_id = str(complete.get("manifest_receipt_id") or "").strip()
    if not manifest_receipt_id:
        raise RuntimeError("RUN_COMPLETE missing manifest_receipt_id")
    if stegverse_result.get("manifest_receipt_id") != manifest_receipt_id:
        raise RuntimeError("STEGVERSE_RESULT manifest_receipt_id mismatch")
    portable_reference = f"stegverse-replay:v1:{manifest_receipt_id}:{EXPECTED_MANIFEST_SHA256}"
    if complete.get("portable_replay_reference") != portable_reference:
        raise RuntimeError("RUN_COMPLETE portable replay reference mismatch")
    if complete.get("replay_reference_artifact") != "REPLAY_REFERENCE.txt":
        raise RuntimeError("RUN_COMPLETE replay reference artifact mismatch")

    expected_reference_values = {
        "TEST_ID": TEST_ID,
        "MANIFEST_RECEIPT_ID": manifest_receipt_id,
        "MANIFEST_SHA256": EXPECTED_MANIFEST_SHA256,
        "MANIFEST_GIT_BLOB_SHA1": EXPECTED_MANIFEST_BLOB_SHA1,
        "TRANSITION_ID": str(transition.get("transition_id") or "").strip(),
        "TRANSITION_RECEIPT_HASH": str(transition.get("receipt_hash") or "").strip(),
        "STEGVERSE_RESULT_SHA256": _canonical_value_sha256(stegverse_result),
        "PORTABLE_REPLAY_REFERENCE": portable_reference,
        "REPLAY_REFERENCE": manifest_receipt_id,
        "RECONSTRUCTION_REFERENCE": manifest_receipt_id,
    }
    for key, expected in expected_reference_values.items():
        if not expected or replay_reference.get(key) != expected:
            raise RuntimeError(f"REPLAY_REFERENCE.txt mismatch: {key}")

    if replay.get("operation_transition_custody_status") != "RECORDED":
        raise RuntimeError("replay custody evidence is not recorded")
    if reconstruction.get("operation_transition_custody_status") != "RECORDED":
        raise RuntimeError("reconstruction custody evidence is not recorded")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    evidence_out = output_dir / "run-evidence"
    shutil.copytree(result_dir, evidence_out)
    shutil.copy2(manifest_path, output_dir / "frozen-manifest-v0.4.json")

    indexed: list[dict[str, Any]] = []
    for path in sorted(p for p in output_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(output_dir).as_posix()
        indexed.append({"path": rel, "sha256": _sha256(path), "bytes": path.stat().st_size})

    index = {
        "schema": "stegverse.sdk.cross-framework-result-publication.v1",
        "test_id": TEST_ID,
        "vector_schema": "stegverse.cross-framework-current-basis-vector.v0.4",
        "frozen_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "frozen_manifest_git_blob_sha1": EXPECTED_MANIFEST_BLOB_SHA1,
        "manifest_receipt_id": manifest_receipt_id,
        "portable_replay_reference": portable_reference,
        "copy_paste_reference_artifact": "run-evidence/REPLAY_REFERENCE.txt",
        "publication_role": "VERIFICATION_AND_DISTRIBUTION_ONLY",
        "github_actions_runtime_authority": False,
        "files": indexed,
    }
    (output_dir / "RESULT_PACKET_INDEX.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return index


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default="evidence/evaluator/cross-framework-current-basis-v0.4-result")
    parser.add_argument("--manifest", default="inspection/examples/cross-framework-current-basis-request.draft.json")
    parser.add_argument("--output-dir", default="/tmp/cross-framework-current-basis-v0.4-packet")
    args = parser.parse_args()
    result = package_results(
        result_dir=Path(args.result_dir),
        manifest_path=Path(args.manifest),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
