from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

EXPECTED_MANIFEST_SHA256 = "07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f"
EXPECTED_MANIFEST_BLOB_SHA1 = "59d818a15fc7be732c97dae7d2174d8cfe9a7bab"

REQUIRED_COMPLETE_FLAGS = {
    "independent_execution_complete": True,
    "s1_observed": True,
    "transition_receipt_bound": True,
    "custody_recorded": True,
    "replay_recorded": True,
    "reconstruction_recorded": True,
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


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

    files = sorted(path for path in result_dir.rglob("*") if path.is_file())
    if len(files) < 2:
        raise RuntimeError("result directory contains no retained evidence beyond completion sentinel")

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
        "test_id": "cross-framework-current-basis-001",
        "vector_schema": "stegverse.cross-framework-current-basis-vector.v0.4",
        "frozen_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "frozen_manifest_git_blob_sha1": EXPECTED_MANIFEST_BLOB_SHA1,
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
