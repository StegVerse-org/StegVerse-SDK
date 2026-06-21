#!/usr/bin/env python3
"""Validate SDK Core-Node parallel fanout CI evidence tracker."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "docs" / "SDK_CORE_NODE_PARALLEL_FANOUT_CI_EVIDENCE.md"
REQUIRED_TEXT = [
    "Track activation evidence for SDK intake to Core-Node parallel fanout with unified comparison receipt.",
    "status: pre-activation",
    "python -m pytest exits 0.",
    "SDK fanout goal validator passes.",
    "SDK fanout request validator passes.",
    "SDK unified comparison receipt validator passes.",
    "SDK human-readable comparison result validator passes.",
    "SDK activation status validator passes.",
    "SDK fanout handoff validator passes.",
    "commit: PENDING",
    "fanout activation evidence: PENDING",
]


def main() -> int:
    text = TRACKER.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED_TEXT if item not in text]
    if missing:
        raise AssertionError(f"CI evidence tracker missing required text: {missing}")

    print("PASS: SDK core-node fanout CI evidence tracker is valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
