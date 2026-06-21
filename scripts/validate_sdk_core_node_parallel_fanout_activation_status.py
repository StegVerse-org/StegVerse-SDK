#!/usr/bin/env python3
"""Validate SDK Core-Node parallel fanout activation status."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "SDK_CORE_NODE_PARALLEL_FANOUT_ACTIVATION_STATUS.json"
REQUIRED_ARTIFACTS = [
    "docs/SDK_CORE_NODE_PARALLEL_FANOUT_GOAL.json",
    "schemas/sdk_core_node_fanout_request.schema.json",
    "examples/sdk_core_node_fanout_request.sample.json",
    "scripts/validate_sdk_core_node_fanout_goal.py",
    "scripts/validate_sdk_core_node_fanout_request.py",
    "tests/test_sdk_core_node_fanout_goal.py",
    "tests/test_sdk_core_node_fanout_request.py",
    "schemas/sdk_core_node_unified_comparison_receipt.schema.json",
    "examples/sdk_core_node_unified_comparison_receipt.sample.json",
    "scripts/validate_sdk_core_node_unified_comparison_receipt.py",
    "tests/test_sdk_core_node_unified_comparison_receipt.py",
    "examples/sdk_core_node_unified_comparison_result.sample.md",
    "scripts/generate_sdk_core_node_unified_comparison_result.py",
    "scripts/validate_sdk_core_node_unified_comparison_result.py",
    "tests/test_sdk_core_node_result.py",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    status = read_json(STATUS)

    if status["repo"] != "StegVerse-org/StegVerse-SDK":
        raise AssertionError("activation status must belong to StegVerse-org/StegVerse-SDK")
    if status["goal"] != "SDK intake to Core-Node parallel fanout with unified comparison receipt":
        raise AssertionError("unexpected activation goal")
    if status["status"] not in {"pre-activation", "activated"}:
        raise AssertionError("status must be pre-activation or activated")

    built = set(status["built_artifacts"])
    missing = [artifact for artifact in REQUIRED_ARTIFACTS if artifact not in built]
    if missing:
        raise AssertionError(f"activation status missing built artifacts: {missing}")

    for artifact in REQUIRED_ARTIFACTS:
        if not (ROOT / artifact).exists():
            raise AssertionError(f"declared artifact does not exist: {artifact}")

    if not status["required_activation_evidence"]:
        raise AssertionError("required activation evidence must not be empty")
    if status["status"] == "pre-activation" and not status["remaining"]:
        raise AssertionError("pre-activation status must declare remaining work")

    print("PASS: SDK core-node fanout activation status is valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
