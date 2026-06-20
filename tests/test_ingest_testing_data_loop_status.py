import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "scripts" / "ingest_testing_data_loop_status.py"
VALIDATOR = ROOT / "scripts" / "validate_formal_testing_route.py"
STATUS = ROOT / "examples" / "testing_data_loop_status.json"
OBSERVATIONS = ROOT / "examples" / "testing_data_loop_workflow_observations.json"


def test_status_ingestion_outputs_valid_status(tmp_path):
    output = tmp_path / "status.json"
    result = subprocess.run([
        sys.executable,
        str(INGEST),
        "--status", str(STATUS),
        "--observations", str(OBSERVATIONS),
        "--output", str(output),
    ], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr

    status = json.loads(output.read_text(encoding="utf-8"))
    assert status["ci_status_visibility"] == "incomplete"

    checked = subprocess.run([
        sys.executable,
        str(VALIDATOR),
        "--kind", "status",
        str(output),
    ], cwd=ROOT, text=True, capture_output=True, check=False)
    assert checked.returncode == 0, checked.stderr
