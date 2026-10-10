import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "examples" / "testing_data_loop_handoff.json"
VALIDATOR = ROOT / "scripts" / "validate_formal_testing_route.py"


def test_testing_data_loop_handoff_example_is_valid():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--kind", "handoff", str(HANDOFF)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "PASS: testing data loop handoff is valid" in result.stdout


def test_handoff_does_not_require_master_records_receipts(tmp_path):
    import json

    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    handoff.pop("master_records_receipts")
    path = tmp_path / "handoff.json"
    path.write_text(json.dumps(handoff), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--kind", "handoff", str(path)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
