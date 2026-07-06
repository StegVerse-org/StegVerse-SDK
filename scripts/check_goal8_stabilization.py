#!/usr/bin/env python3
"""Verify SDK Goal 8 stabilization record and installed surface."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "goal8-stabilization.json"


def stop(message: str) -> None:
    raise SystemExit(f"SDK_GOAL8_STABILIZATION_FAIL: {message}")


def main() -> int:
    data = json.loads(RECORD.read_text(encoding="utf-8"))
    if data.get("schema_version") != "stegverse.sdk.goal8_stabilization.v0.1":
        stop("bad schema version")
    if data.get("state") != "installed_surface_stabilized":
        stop("state mismatch")
    if data.get("handoff_source") != "SDK_MIRROR_HANDOFF.md":
        stop("handoff source mismatch")
    if data.get("continuation_checkpoint") != "data/goal8-continuation-checkpoint.json":
        stop("continuation checkpoint mismatch")
    required = data.get("required_validation", {})
    for label, rel_path in required.items():
        if not rel_path:
            stop(f"{label} path missing")
        if not (ROOT / rel_path).exists():
            stop(f"repository missing {rel_path}")
    if data.get("manual_tasks_remaining") != []:
        stop("manual tasks must remain empty")
    if data.get("next_goal_candidate") != "Goal 8 completion checkpoint":
        stop("next goal candidate mismatch")
    print("SDK_GOAL8_STABILIZATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
