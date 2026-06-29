#!/usr/bin/env python3
"""Check the declared bundle export fixture."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "universal_transition_table_intake"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(name: str) -> dict:
    return json.loads((FIXTURE / name).read_text(encoding="utf-8"))


def main() -> int:
    export = read_json("artifact_bundle_export.json")
    candidate = read_json("commitment_candidate.json")

    require(export.get("execution_enabled") is False, "bundle export must keep activation off")
    require(export["source_repo"] == "StegVerse-org/StegVerse-SDK", "unexpected source repo")
    require(export["intended_consumer_repo"] == "StegVerse-org/core-node-runtime-demo", "unexpected consumer repo")
    for artifact in export["artifacts"]:
        require((FIXTURE / artifact).exists(), f"missing exported artifact: {artifact}")

    invariant = export["required_invariant"]
    require(candidate["authorizing"] is invariant["commitment_candidate_authorizing"], "candidate invariant mismatch")
    require(candidate["inherits_review_authority"] is invariant["inherits_review_authority"], "review authority invariant mismatch")
    require(candidate["implies_standing"] is invariant["implies_standing"], "standing invariant mismatch")
    require(candidate["requires_fresh_standing_determination"] is invariant["requires_fresh_standing_determination"], "fresh standing invariant mismatch")

    print("PASS bundle export files present")
    print("PASS bundle export preserves candidate invariant")
    print("PASS bundle export keeps activation off")
    print("PASS SDK bundle export checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
