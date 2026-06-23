#!/usr/bin/env python3
"""Check the SDK artifact transport receipt fixture."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "universal_transition_table_intake"


def read_json(name: str) -> dict:
    return json.loads((FIXTURE / name).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    manifest = read_json("artifact_transport_manifest.json")
    receipt = read_json("artifact_transport_receipt.json")

    require(receipt["transport_id"] == manifest["transport_id"], "transport id mismatch")
    require(receipt["package_id"] == manifest["package_id"], "package id mismatch")
    require(receipt["source_repo"] == manifest["source_repo"], "source repo mismatch")
    require(receipt["destination_repo"] == manifest["destination_repo"], "destination repo mismatch")
    require(receipt["runtime_execution_enabled"] is False, "transport receipt must not enable runtime execution")
    require(receipt["non_authorizing_boundary_preserved"] is True, "boundary must be preserved")

    for artifact in manifest["required_artifacts"]:
        require(artifact in receipt["artifact_hashes"], f"missing artifact hash: {artifact}")

    print("PASS artifact transport receipt matches manifest")
    print("PASS artifact transport receipt preserves boundary")
    print("PASS artifact transport receipt does not enable runtime execution")
    print("PASS SDK artifact transport receipt checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
