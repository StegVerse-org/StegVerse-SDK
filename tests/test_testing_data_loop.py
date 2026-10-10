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


def test_testing_data_loop_requires_organization_ledger_receipts_not_master_records():
    loop = json.loads(LOOP.read_text(encoding="utf-8"))

    assert loop["organization_ledger_receipt_required"] is True
    assert loop["master_records_required"] is False
    assert all(step["organization_ledger_receipt_required"] is True for step in loop["loop_steps"])
    assert all(step["master_records_receipt_required"] is False for step in loop["loop_steps"])


def _validate(tmp_path, loop):
    path = tmp_path / "loop.json"
    path.write_text(json.dumps(loop), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--kind", "loop", str(path)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def test_master_records_can_never_be_made_a_loop_requirement(tmp_path):
    loop = json.loads(LOOP.read_text(encoding="utf-8"))
    for step in loop["loop_steps"]:
        step.pop("master_records_receipt_required")
    loop.pop("master_records_required")
    assert _validate(tmp_path, loop).returncode == 0

    gated = json.loads(LOOP.read_text(encoding="utf-8"))
    gated["master_records_required"] = True
    assert _validate(tmp_path, gated).returncode != 0

    unledgered = json.loads(LOOP.read_text(encoding="utf-8"))
    unledgered["loop_steps"][0]["organization_ledger_receipt_required"] = False
    assert _validate(tmp_path, unledgered).returncode != 0
