#!/usr/bin/env python3
"""Verify SDK tests avoid fragile pytest helper assumptions."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MICRO_NODE_TEST = ROOT / "tests" / "test_micro_node_return_path.py"


def fail(message: str) -> None:
    raise SystemExit(f"PYTEST_COMPATIBILITY_SURFACE_FAIL: {message}")


def main() -> int:
    if not MICRO_NODE_TEST.exists():
        fail("missing micro-node return-path test")
    text = MICRO_NODE_TEST.read_text(encoding="utf-8")
    blocked = ("import pytest", "pytest.raises")
    for marker in blocked:
        if marker in text:
            fail(f"test must not depend on {marker}")
    required = ("try:", "except MicroNodeReturnPathValidationError", "raise AssertionError")
    for marker in required:
        if marker not in text:
            fail(f"test missing explicit exception assertion marker: {marker}")
    print("PYTEST_COMPATIBILITY_SURFACE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
