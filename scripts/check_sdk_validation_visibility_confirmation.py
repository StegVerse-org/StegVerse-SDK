#!/usr/bin/env python3
"""Verify SDK validation visibility confirmation state."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIRMATION = ROOT / "data" / "sdk-validation-visibility-confirmation.json"


def stop(message: str) -> None:
    raise SystemExit(f"SDK_VALIDATION_VISIBILITY_CONFIRMATION_FAIL: {message}")


def main() -> int:
    data = json.loads(CONFIRMATION.read_text(encoding="utf-8"))
    if data.get("schema_version") != "stegverse.sdk.validation_visibility_confirmation.v0.1":
        stop("bad schema version")
    if data.get("state") != "workflow_run_not_connector_visible":
        stop("state mismatch")
    if not data.get("checked_commit"):
        stop("checked commit missing")
    if data.get("workflow_runs_visible") is not False:
        stop("workflow visibility must be false until run data is visible")
    if data.get("goal8_completion_checkpoint") != "data/goal8-completion-checkpoint.json":
        stop("Goal 8 completion checkpoint pointer mismatch")
    if data.get("manual_tasks_remaining") != []:
        stop("manual tasks must remain empty")
    if data.get("next_goal_candidate") != "SDK visibility refresh or cross-repo promotion record":
        stop("next goal candidate mismatch")
    print("SDK_VALIDATION_VISIBILITY_CONFIRMATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
