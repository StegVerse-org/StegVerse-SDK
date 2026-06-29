from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bundle_export_checker_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_bundle_export.py")],
        cwd=str(ROOT),
        check=True,
        capture_output=True,
        text=True,
    )

    assert "PASS bundle export files present" in result.stdout
    assert "PASS bundle export preserves candidate invariant" in result.stdout
    assert "PASS SDK bundle export checked" in result.stdout
