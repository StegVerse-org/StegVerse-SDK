from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sdk_goal3_activation_verifier_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "verify_goal3_activation.py")],
        cwd=str(ROOT),
        check=True,
        capture_output=True,
        text=True,
    )

    assert "PASS SDK Goal 3 manifest verifier passes" in result.stdout
    assert "PASS SDK Goal 3 transport receipt verifier passes" in result.stdout
    assert "PASS SDK Goal 3 non-authorizing boundary preserved" in result.stdout
    assert "PASS SDK Goal 3 activation verified" in result.stdout
