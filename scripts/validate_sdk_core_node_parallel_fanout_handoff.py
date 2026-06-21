#!/usr/bin/env python3
"""Validate SDK Core-Node parallel fanout handoff."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "SDK_CORE_NODE_PARALLEL_FANOUT_HANDOFF.md"
REQUIRED_TEXT = [
    "SDK intake to Core-Node parallel fanout with unified comparison receipt.",
    "status: pre-activation",
    "python -m pytest",
    "SDK fanout goal validator passes.",
    "SDK fanout request validator passes.",
    "SDK unified comparison receipt validator passes.",
    "SDK human-readable comparison result validator passes.",
    "SDK activation status validator passes.",
    "Update docs/SDK_CORE_NODE_PARALLEL_FANOUT_ACTIVATION_STATUS.json status from pre-activation to activated.",
    "Update docs/SDK_CORE_NODE_PARALLEL_FANOUT_GOAL.json status from started to activated.",
    "Close issue #1 as completed.",
]


def main() -> int:
    text = HANDOFF.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED_TEXT if item not in text]
    if missing:
        raise AssertionError(f"handoff missing required text: {missing}")

    print("PASS: SDK core-node fanout handoff is valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
