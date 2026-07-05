#!/usr/bin/env python3
"""Verify SDK scripts make the local package importable in CI."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMOKE = ROOT / "scripts" / "smoke_governed_llm_sdk.py"
PACKAGE = ROOT / "stegverse" / "__init__.py"


def fail(message: str) -> None:
    raise SystemExit(f"SDK_LOCAL_IMPORT_PATH_FAIL: {message}")


def main() -> int:
    if not PACKAGE.exists():
        fail("missing stegverse package")
    if not SMOKE.exists():
        fail("missing smoke script")
    text = SMOKE.read_text(encoding="utf-8")
    required = (
        "from pathlib import Path",
        "ROOT = Path(__file__).resolve().parents[1]",
        "sys.path.insert(0, str(ROOT))",
        "from stegverse import build_governed_llm_receipt_handoff",
    )
    for marker in required:
        if marker not in text:
            fail(f"smoke script missing import-path marker: {marker}")
    print("SDK_LOCAL_IMPORT_PATH_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
