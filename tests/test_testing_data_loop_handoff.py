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
