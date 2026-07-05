#!/usr/bin/env python3
"""Verify SDK AI Entry validation is wired so no manual verification task is required."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / ".github" / "workflows" / "validate.yml"
MIRROR = ROOT / "iosnoperiod" / "github" / "workflows" / "validate.yml"
AGGREGATE = ROOT / "scripts" / "verify_goal4.py"
STATUS = ROOT / "docs" / "AI_ENTRY_RECEIPT_CAPTURE_STATUS.md"
DOC = ROOT / "docs" / "AI_ENTRY_SDK_RECEIPT_CAPTURE.md"
IOS_DOC = ROOT / "iosnoperiod.md"

REQUIRED = "python scripts/verify_goal4.py"


def fail(message: str) -> None:
    raise SystemExit(f"SDK_AI_ENTRY_NO_MANUAL_TASKS_FAIL: {message}")


def require_text(path: Path, markers: tuple[str, ...]) -> None:
    if not path.exists():
        fail(f"missing {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            fail(f"{path.relative_to(ROOT)} missing {marker}")


def main() -> int:
    require_text(AGGREGATE, ("verify_ai_entry_receipt_capture.py", "tests/test_ai_entry_receipt_capture.py"))
    require_text(CANONICAL, (REQUIRED, "workflow_dispatch"))
    require_text(MIRROR, (REQUIRED, "workflow_dispatch"))
    require_text(STATUS, ("preview_only == true", "receipt_capture_enabled == false"))
    require_text(DOC, ("AI Entry SDK Receipt Capture Boundary", "preview"))
    require_text(IOS_DOC, ("Canonical: .github/workflows/validate.yml", "Mirror: iosnoperiod/github/workflows/validate.yml"))
    print("SDK_AI_ENTRY_NO_MANUAL_TASKS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
