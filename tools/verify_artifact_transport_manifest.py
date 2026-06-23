#!/usr/bin/env python3
"""Verify the SDK artifact transport manifest fixture."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "universal_transition_table_intake"
MANIFEST = FIXTURE / "artifact_transport_manifest.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    candidate = json.loads((FIXTURE / "commitment_candidate.json").read_text(encoding="utf-8"))

    for artifact in manifest["required_artifacts"]:
        require((FIXTURE / artifact).exists(), f"missing transported artifact: {artifact}")

    invariant = manifest["required_invariants"]
    require(candidate["candidate_type"] == invariant["candidate_type"], "candidate type mismatch")
    require(candidate["authorizing"] is invariant["authorizing"], "authorizing invariant mismatch")
    require(candidate["inherits_review_authority"] is invariant["inherits_review_authority"], "review authority invariant mismatch")
    require(candidate["implies_standing"] is invariant["implies_standing"], "standing invariant mismatch")
    require(
        candidate["requires_fresh_standing_determination"] is invariant["requires_fresh_standing_determination"],
        "fresh standing invariant mismatch",
    )
    require(manifest["runtime_execution_enabled"] is False, "transport must not enable runtime execution")

    print("PASS artifact transport manifest required files present")
    print("PASS artifact transport preserves non-authorizing invariant")
    print("PASS artifact transport does not enable runtime execution")
    print("PASS SDK artifact transport manifest verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
