import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOOP = ROOT / "examples" / "testing_data_loop.json"
VALIDATOR = ROOT / "scripts" / "validate_formal_testing_route.py"


def test_testing_data_loop_example_is_valid():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--kind", "loop", str(LOOP)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "PASS: testing data loop is valid" in result.stdout


def test_testing_data_loop_requires_master_records_receipts():
    loop = json.loads(LOOP.read_text(encoding="utf-8"))

    assert loop["master_records_required"] is True
    assert all(step["master_records_receipt_required"] is True for step in loop["loop_steps"])
