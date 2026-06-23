from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_tool(tool_name: str) -> str:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / tool_name)],
        cwd=str(ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def test_artifact_transport_receipt_tools_pass() -> None:
    generated = run_tool("generate_artifact_transport_receipt.py")
    checked = run_tool("check_artifact_transport_receipt.py")

    assert "PASS generated artifact transport receipt" in generated
    assert "PASS artifact transport receipt matches manifest" in checked
    assert "PASS SDK artifact transport receipt checked" in checked
