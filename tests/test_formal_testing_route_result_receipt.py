import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_RECEIPT = ROOT / "examples" / "formal_testing_route_result_receipt.json"
VALIDATOR = ROOT / "scripts" / "validate_formal_testing_route.py"


def test_formal_testing_route_result_receipt_example_is_valid():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--kind", "result", str(RESULT_RECEIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "PASS: formal testing route result receipt is valid" in result.stdout


def test_formal_testing_route_result_receipt_preserves_sdk_intake():
    receipt = json.loads(RESULT_RECEIPT.read_text(encoding="utf-8"))
    intake = receipt["sdk_intake"]

    assert intake["ingestion_point"] == "StegVerse-org/StegVerse-SDK"
    assert intake["dataset_manifest_hash"].startswith("sha256:")
    assert intake["intake_receipt_id"]
