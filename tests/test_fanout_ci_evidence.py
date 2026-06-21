import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_sdk_core_node_parallel_fanout_ci_evidence.py"


def test_fanout_ci_evidence():
    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0
