import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_sdk_core_node_unified_comparison_receipt.py"
RECEIPT = ROOT / "examples" / "sdk_core_node_unified_comparison_receipt.sample.json"


def test_sdk_core_node_unified_comparison_receipt_is_valid():
    result = subprocess.run([sys.executable, str(VALIDATOR), str(RECEIPT)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0


def test_comparison_receipt_does_not_require_master_records_witness(tmp_path):
    import json

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    receipt["witness_receipts"] = []
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    result = subprocess.run([sys.executable, str(VALIDATOR), str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr

    receipt["witness_receipts"] = ["not-a-master-records-ref"]
    path.write_text(json.dumps(receipt), encoding="utf-8")
    result = subprocess.run([sys.executable, str(VALIDATOR), str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode != 0
