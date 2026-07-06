#!/usr/bin/env python3
"""Verify SDK Goal 8 completion checkpoint."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "data" / "goal8-completion-checkpoint.json"


def stop(message: str) -> None:
    raise SystemExit(f"SDK_GOAL8_COMPLETION_CHECKPOINT_FAIL: {message}")


def main() -> int:
    data = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    if data.get("schema_version") != "stegverse.sdk.goal8_completion_checkpoint.v0.1":
        stop("bad schema version")
    if data.get("state") != "completion_checkpoint_recorded":
        stop("state mismatch")
    completed = data.get("completed_components", {})
    if not completed or any(value is not True for value in completed.values()):
        stop("completed components must all be true")
    surface = data.get("active_surface", {})
    for label, rel_path in surface.items():
        if not rel_path:
            stop(f"{label} path missing")
        if not (ROOT / rel_path).exists():
            stop(f"repository missing {rel_path}")
    if data.get("manual_tasks_remaining") != []:
        stop("manual tasks must remain empty")
    if data.get("next_goal_candidate") != "SDK validation visibility confirmation":
        stop("next goal candidate mismatch")
    print("SDK_GOAL8_COMPLETION_CHECKPOINT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
