#!/usr/bin/env python3
"""Verify Goal 3 activation for SDK artifact transport."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "universal_transition_table_intake"


def run_tool(tool_name: str) -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / tool_name)],
        cwd=ROOT,
        check=True,
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(name: str) -> dict:
    return json.loads((FIXTURE / name).read_text(encoding="utf-8"))


def main() -> int:
    run_tool("verify_artifact_transport_manifest.py")
    run_tool("generate_artifact_transport_receipt.py")
    run_tool("check_artifact_transport_receipt.py")

    manifest = read_json("artifact_transport_manifest.json")
    receipt = read_json("artifact_transport_receipt.json")
    candidate = read_json("commitment_candidate.json")

    require(manifest["runtime_execution_enabled"] is False, "manifest must not enable runtime execution")
    require(receipt["runtime_execution_enabled"] is False, "receipt must not enable runtime execution")
    require(receipt["non_authorizing_boundary_preserved"] is True, "transport must preserve the boundary")
    require(candidate["authorizing"] is False, "candidate must remain non-authorizing")
    require(candidate["inherits_review_authority"] is False, "candidate must not inherit review authority")
    require(candidate["implies_standing"] is False, "candidate must not imply standing")
    require(candidate["requires_fresh_standing_determination"] is True, "candidate must require fresh standing determination")

    print("PASS SDK Goal 3 manifest verifier passes")
    print("PASS SDK Goal 3 transport receipt verifier passes")
    print("PASS SDK Goal 3 non-authorizing boundary preserved")
    print("PASS SDK Goal 3 activation verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
