#!/usr/bin/env python3
"""Validate human-readable SDK Core-Node comparison result stability."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "examples" / "sdk_core_node_unified_comparison_result.sample.md"
REQUIRED_TEXT = [
    "# SDK Core-Node Unified Comparison Result",
    "PATH-1",
    "PATH-2",
    "PATH-3",
    "PATH-4",
    "PATH-5",
    "Cost USD",
    "master-records-package-observed-sample-001",
    "human_readable_summary",
]


def main() -> int:
    before = RESULT.read_text(encoding="utf-8")
    subprocess.run([sys.executable, "scripts/generate_sdk_core_node_unified_comparison_result.py"], cwd=ROOT, check=True)
    after = RESULT.read_text(encoding="utf-8")

    if before != after:
        raise AssertionError("human-readable comparison result is not stable after regeneration")
    missing = [item for item in REQUIRED_TEXT if item not in after]
    if missing:
        raise AssertionError(f"human-readable comparison result missing required text: {missing}")

    print("PASS: SDK core-node unified comparison result is valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
