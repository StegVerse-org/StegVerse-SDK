import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_sdk_core_node_unified_comparison_receipt.py"
RECEIPT = ROOT / "examples" / "sdk_core_node_unified_comparison_receipt.sample.json"


def test_sdk_core_node_unified_comparison_receipt_is_valid():
    result = subprocess.run([sys.executable, str(VALIDATOR), str(RECEIPT)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0
