import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples" / "formal_testing_route_manifest.json"
VALIDATOR = ROOT / "scripts" / "validate_formal_testing_route.py"


def test_formal_testing_route_manifest_example_is_valid():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(MANIFEST)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "PASS: formal testing route manifest is valid" in result.stdout


def test_formal_testing_route_manifest_preserves_all_routes():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    route_ids = {route["route_id"] for route in manifest["declared_routes"]}

    assert route_ids == {
        "public_demo_validation",
        "formal_demo_runner",
        "rigorous_sandbox_testing",
        "standing_proof",
        "boundary_glm_case",
    }
