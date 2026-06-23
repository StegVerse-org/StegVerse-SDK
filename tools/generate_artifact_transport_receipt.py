#!/usr/bin/env python3
"""Generate a non-executing artifact transport receipt for SDK Goal 3."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "universal_transition_table_intake"
MANIFEST = FIXTURE / "artifact_transport_manifest.json"
OUT = FIXTURE / "artifact_transport_receipt.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    manifest = read_json(MANIFEST)
    artifact_hashes = {}
    for artifact in manifest["required_artifacts"]:
        path = FIXTURE / artifact
        artifact_hashes[artifact] = hashlib.sha256(path.read_bytes()).hexdigest()

    receipt = {
        "schema": "stegverse.sdk.artifact_transport_receipt.v1",
        "receipt_id": f"artifact-transport-receipt-{manifest['package_id']}",
        "transport_id": manifest["transport_id"],
        "package_id": manifest["package_id"],
        "source_repo": manifest["source_repo"],
        "destination_repo": manifest["destination_repo"],
        "runtime_execution_enabled": False,
        "transport_manifest_hash": stable_hash(manifest),
        "artifact_hashes": artifact_hashes,
        "non_authorizing_boundary_preserved": True,
    }

    OUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"PASS generated artifact transport receipt: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
