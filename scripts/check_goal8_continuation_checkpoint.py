#!/usr/bin/env python3
"""Verify SDK Goal 8 continuation checkpoint after Goal 4 guard repair."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "data" / "goal8-continuation-checkpoint.json"
REQUIRED = (
    "docs/FREE_TIER_METADATA_INGESTION.md",
    "stegverse/free_tier_metadata.py",
    "tests/test_free_tier_metadata.py",
    "scripts/verify_free_tier_metadata_ingestion.py",
    "sdk.capabilities.json",
)


def stop(message: str) -> None:
    raise SystemExit(f"SDK_GOAL8_CONTINUATION_CHECKPOINT_FAIL: {message}")


def main() -> int:
    data = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    if data.get("schema_version") != "stegverse.sdk.goal8_continuation_checkpoint.v0.1":
        stop("bad schema version")
    if data.get("state") != "goal8_active_goal4_preserved":
        stop("state mismatch")
    if data.get("handoff_source") != "SDK_MIRROR_HANDOFF.md":
        stop("handoff source mismatch")
    if data.get("preserved_goal4_guard") != "data/goal4-demo-session-interface-stabilization.json":
        stop("Goal 4 guard pointer mismatch")
    installed = set(data.get("goal8_installed_surface", []))
    for path in REQUIRED:
        if path not in installed:
            stop(f"checkpoint missing {path}")
        if not (ROOT / path).exists():
            stop(f"repository missing {path}")
    if data.get("manual_tasks_remaining") != []:
        stop("manual tasks must remain empty")
    if data.get("next_goal_candidate") != "Goal 8 stabilization verifier":
        stop("next goal candidate mismatch")
    print("SDK_GOAL8_CONTINUATION_CHECKPOINT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
