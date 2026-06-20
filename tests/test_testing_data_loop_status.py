import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "examples" / "testing_data_loop_status.json"
VALIDATOR = ROOT / "scripts" / "validate_formal_testing_route.py"


def test_testing_data_loop_status_example_is_valid():
    result = subprocess.run([
        sys.executable,
        str(VALIDATOR),
        "--kind", "status",
        str(STATUS),
    ], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "PASS: testing data loop status is valid" in result.stdout
