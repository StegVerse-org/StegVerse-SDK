#!/usr/bin/env python3
"""Validate SDK to Core-Node parallel fanout goal document."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOAL = ROOT / "docs" / "SDK_CORE_NODE_PARALLEL_FANOUT_GOAL.json"
EXPECTED_PATHS = ["PATH-1", "PATH-2", "PATH-3", "PATH-4", "PATH-5"]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    goal = read_json(GOAL)

    if goal["repo"] != "StegVerse-org/StegVerse-SDK":
        raise AssertionError("goal must belong to StegVerse-org/StegVerse-SDK")
    if goal["status"] not in {"started", "activated"}:
        raise AssertionError("goal status must be started or activated")

    fanout_paths = [item["path_id"] for item in goal["fanout_paths"]]
    if fanout_paths != EXPECTED_PATHS:
        raise AssertionError("goal must declare PATH-1 through PATH-5 in order")

    if "sdk_return_human_result" not in goal["user_loop"]:
        raise AssertionError("user loop must return a human result")
    if "comparison_receipt_observed" not in goal["witness_loop"]:
        raise AssertionError("witness loop must observe comparison receipt")

    required_next = {
        "schemas/sdk_core_node_fanout_request.schema.json",
        "examples/sdk_core_node_fanout_request.sample.json",
        "scripts/validate_sdk_core_node_fanout_goal.py",
        "scripts/validate_sdk_core_node_fanout_request.py",
        "tests/test_sdk_core_node_fanout_goal.py",
        "tests/test_sdk_core_node_fanout_request.py",
    }
    if not required_next.issubset(set(goal["next_artifacts"])):
        raise AssertionError("goal next_artifacts missing required build items")

    print("PASS: SDK core-node fanout goal is valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
