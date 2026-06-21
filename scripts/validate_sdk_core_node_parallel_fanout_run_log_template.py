#!/usr/bin/env python3
"""Validate SDK Core-Node parallel fanout run-log template."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "docs" / "SDK_CORE_NODE_PARALLEL_FANOUT_RUN_LOG_TEMPLATE.md"
REQUIRED_TEXT = [
    "python -m pytest",
    "repo: StegVerse-org/StegVerse-SDK",
    "exit_code: 0",
    "fanout_goal_validator: PASS",
    "fanout_request_validator: PASS",
    "unified_comparison_receipt_validator: PASS",
    "human_readable_comparison_result_validator: PASS",
    "activation_status_validator: PASS",
    "handoff_validator: PASS",
    "ci_evidence_tracker_validator: PASS",
    "test_sdk_core_node_fanout_goal.py",
    "test_sdk_core_node_fanout_request.py",
    "test_sdk_core_node_unified_comparison_receipt.py",
    "test_sdk_core_node_result.py",
    "test_fanout_status.py",
    "test_fanout_handoff.py",
    "test_fanout_ci_evidence.py",
    "sdk_core_node_parallel_fanout_activation_result: <PASS | FAIL>",
    "Update docs/SDK_CORE_NODE_PARALLEL_FANOUT_ACTIVATION_STATUS.json status from pre-activation to activated.",
    "Close issue #1 as completed.",
]


def main() -> int:
    text = TEMPLATE.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED_TEXT if item not in text]
    if missing:
        raise AssertionError(f"run-log template missing required text: {missing}")

    print("PASS: SDK core-node fanout run-log template is valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
