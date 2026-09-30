"""The published examples must work for an evaluator the repository has never seen."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "inspection" / "examples"

SOURCE = EXAMPLES / "external-framework-submission-source.example.json"
REQUEST = EXAMPLES / "external-framework-governance-request.example.json"
DECLARATION = EXAMPLES / "external-framework-evaluation-declaration.example.json"

# A framework name that appears nowhere in this repository.
UNSEEN_FRAMEWORK = "ACME_GOVERNANCE_LABS"

FRAMEWORK_TOKENS = ("elan", "mir", "hgai", "flint", "richard", "stcm", "chf")


def test_the_three_examples_exist():
    for path in (SOURCE, REQUEST, DECLARATION):
        assert path.is_file(), path


def test_no_example_carries_a_framework_name():
    """A generic example that names one framework is not generic."""
    for path in (SOURCE, REQUEST, DECLARATION):
        text = path.read_text(encoding="utf-8").lower()
        for token in FRAMEWORK_TOKENS:
            assert token not in text, f"{path.name} mentions {token!r}"


def test_governance_request_carries_every_required_field():
    from stegverse.manifest_builder import GOVERNANCE_REQUEST_FIELDS

    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    missing = [f for f in GOVERNANCE_REQUEST_FIELDS if f not in request]
    assert missing == [], missing


def test_an_unseen_framework_can_prepare_a_submission(tmp_path):
    """The whole point: self-serve, with identity supplied on the command line."""
    output = tmp_path / "submission.json"
    proc = subprocess.run(
        [
            sys.executable, "-m", "stegverse", "external-run", "--prepare-only",
            "--input", str(SOURCE),
            "--governance-request", str(REQUEST),
            "--evaluation-declaration", str(DECLARATION),
            "--source-framework", UNSEEN_FRAMEWORK,
            "--source-output-id", "acme-first-submission-001",
            "--data-class", "acme.submission-state.v1",
            "--return-depth", "full-trace",
            "--output", str(output),
        ],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr

    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["schema"] == "stegverse.sdk.external-framework-submission.v1"
    assert result["status"] == "SUBMISSION_READY"

    # Nothing about execution may be claimed by a prepare-only run.
    assert result["execution_performed"] is False
    assert result["manifest_receipt_id"] is None

    manifest = result["manifest"]
    assert manifest["source_framework"] == UNSEEN_FRAMEWORK
    assert manifest["extensions"]["source_data_class"] == "acme.submission-state.v1"
    assert manifest["processing"]["capability"] == "governance"
    assert manifest["hashes"]["payload_sha256"]
    assert manifest["hashes"]["candidate_sha256"]
    # The declaration is retained apart from the governance request.
    assert manifest["extensions"]["evaluation_declaration"]
    assert "evaluation_declaration" not in manifest["extensions"]["stegverse_governance_request"]
