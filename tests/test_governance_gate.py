"""Governance gate: installable, stdlib-only, evidence-only check for any repository."""
import ast
import json
import subprocess
import sys
from pathlib import Path

from stegverse import governance_gate
from tests.test_portable_governance_verifier import _bundle

ROOT = Path(__file__).resolve().parents[1]
SIX_FIELDS = (
    "failure_code",
    "failed_predicate",
    "required_evidence_or_repair",
    "retry_entrypoint",
    "owning_existing_goal",
    "next_attempt",
)


def _repo(tmp_path, bundles=(), schemas=()):
    gov = tmp_path / ".stegverse" / "governance"
    gov.mkdir(parents=True)
    for name, document in bundles:
        (gov / name).write_text(json.dumps(document), encoding="utf-8")
    for name, document in schemas:
        (tmp_path / name).write_text(json.dumps(document), encoding="utf-8")
    return tmp_path


def _assert_fail_closed(report, reason):
    assert report["disposition"] == "FAIL_CLOSED"
    assert report["reason"] == reason
    for field in SIX_FIELDS:
        assert isinstance(report[field], str) and report[field].strip(), field
    assert report["failure_code"] == reason
    assert report["owning_existing_goal"] == governance_gate.OWNING_EXISTING_GOAL
    assert report["retry_entrypoint"] == governance_gate.RETRY_ENTRYPOINT


def test_valid_bundle_allows_and_report_claims_no_authority(tmp_path):
    root = _repo(tmp_path, bundles=[("ok.json", _bundle())],
                 schemas=[("a.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object"}),
                          ("b.schema.json", {"type": "object", "oneOf": [{}]})])
    report = governance_gate.run_gate(root)
    assert report["disposition"] == "ALLOW"
    assert report["reason"] == "ALL_BUNDLES_VERIFIED"
    assert [b["status"] for b in report["bundles"]] == ["ALLOW"]
    assert (report["schemas"]["compatible"], report["schemas"]["total"]) == (1, 2)
    assert report["usage"]["bundles_verified"] == 1
    assert report["tier"] == "FREE"
    assert not any(field in report for field in SIX_FIELDS)
    assert not any(v for k, v in report["authority"].items() if k != "verification_authority")
    assert report["authority"]["verification_authority"] == "NONE"


def test_tampered_or_malformed_bundle_fails_closed(tmp_path):
    tampered = _bundle()
    tampered["run_id"] = "different-run"
    root = _repo(tmp_path, bundles=[("tampered.json", tampered), ("list.json", [])])
    report = governance_gate.run_gate(root)
    _assert_fail_closed(report, "BUNDLE_VERIFICATION_FAILED")
    assert {b["status"] for b in report["bundles"]} == {"FAIL_CLOSED"}
    (tmp_path / ".stegverse" / "governance" / "broken.json").write_text("{", encoding="utf-8")
    _assert_fail_closed(governance_gate.run_gate(root), "BUNDLE_VERIFICATION_FAILED")


def test_empty_glob_fails_closed_with_six_fields(tmp_path):
    report = governance_gate.run_gate(_repo(tmp_path))
    _assert_fail_closed(report, "NO_GOVERNANCE_BUNDLES_FOUND")
    assert report["bundles"] == []
    assert report["failed_predicate"] == "AT_LEAST_ONE_PORTABLE_GOVERNANCE_BUNDLE"


def test_free_tier_limit_fails_closed(tmp_path):
    original = dict(governance_gate.FREE_TIER_LIMITS)
    governance_gate.FREE_TIER_LIMITS["bundles"] = 0
    try:
        root = _repo(tmp_path / "over", bundles=[("ok.json", _bundle())])
        report = governance_gate.run_gate(root)
    finally:
        governance_gate.FREE_TIER_LIMITS.clear()
        governance_gate.FREE_TIER_LIMITS.update(original)
    _assert_fail_closed(report, "FREE_TIER_LIMIT_EXCEEDED")


def test_missing_verifier_status_is_fail_closed(tmp_path):
    verifier = governance_gate._sdk_module("portable_governance_verifier")
    original = verifier.verify_portable_governance_bundle

    def no_status(document):
        return {"schema": "no-status"}

    verifier.verify_portable_governance_bundle = no_status
    try:
        root = _repo(tmp_path, bundles=[("ok.json", {"schema": "ignored"})])
        report = governance_gate.run_gate(root, check_schemas=False)
    finally:
        verifier.verify_portable_governance_bundle = original
    assert report["bundles"][0]["status"] == "FAIL_CLOSED"
    _assert_fail_closed(report, "BUNDLE_VERIFICATION_FAILED")


def test_cli_exit_codes_and_summary(tmp_path):
    root = _repo(tmp_path, bundles=[("ok.json", _bundle())])
    summary = tmp_path / "summary.md"
    output = tmp_path / "report.json"
    assert governance_gate.main([str(root), "--output", str(output), "--summary", str(summary)]) == 0
    assert json.loads(output.read_text())["disposition"] == "ALLOW"
    assert "StegVerse governance gate: ALLOW" in summary.read_text()
    bad = _repo(tmp_path / "bad", bundles=[("x.json", {"schema": "nope"})])
    assert governance_gate.main([str(bad), "--output", str(tmp_path / "bad.json")]) == 1
    empty = _repo(tmp_path / "empty")
    empty_report = tmp_path / "empty.json"
    assert governance_gate.main([str(empty), "--output", str(empty_report), "--no-schemas"]) == 1
    _assert_fail_closed(json.loads(empty_report.read_text()), "NO_GOVERNANCE_BUNDLES_FOUND")


def test_read_workflow_disposition_fail_closed_when_report_missing_or_unparsable(tmp_path):
    assert governance_gate.read_workflow_disposition(tmp_path / "absent.json") == "FAIL_CLOSED"
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    assert governance_gate.read_workflow_disposition(bad) == "FAIL_CLOSED"
    listed = tmp_path / "list.json"
    listed.write_text("[]", encoding="utf-8")
    assert governance_gate.read_workflow_disposition(listed) == "FAIL_CLOSED"
    unknown = tmp_path / "unknown.json"
    unknown.write_text(json.dumps({"disposition": "UNKNOWN"}), encoding="utf-8")
    assert governance_gate.read_workflow_disposition(unknown) == "FAIL_CLOSED"
    allowed = tmp_path / "allow.json"
    allowed.write_text(json.dumps({"disposition": "ALLOW"}), encoding="utf-8")
    assert governance_gate.read_workflow_disposition(allowed) == "ALLOW"


def test_workflow_snippet_prints_fail_closed_without_a_report(tmp_path):
    module_path = ROOT / "stegverse" / "governance_gate.py"
    missing = tmp_path / "stegverse-governance-report.json"
    script = (
        "import importlib.util\n"
        "disposition = 'FAIL_CLOSED'\n"
        "try:\n"
        f"    spec = importlib.util.spec_from_file_location('governance_gate', {str(module_path)!r})\n"
        "    module = importlib.util.module_from_spec(spec)\n"
        "    spec.loader.exec_module(module)\n"
        f"    disposition = module.read_workflow_disposition({str(missing)!r})\n"
        "except Exception:\n"
        "    disposition = 'FAIL_CLOSED'\n"
        "print('disposition=' + disposition)\n"
    )
    result = subprocess.run([sys.executable, "-I", "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "disposition=FAIL_CLOSED"
    workflow = (ROOT / ".github" / "workflows" / "governance-gate.yml").read_text(encoding="utf-8")
    assert "read_workflow_disposition" in workflow
    assert 'disposition = "FAIL_CLOSED"' in workflow
    assert "actions/checkout@11d5960a326750d5838078e36cf38b85af677262" in workflow
    assert "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02" in workflow
    assert "ba5bbf42eabec6a6ae3b0efdff7c683967a79083" in workflow
    assert "v1.3.0" not in workflow


def test_workflow_step_exits_nonzero_unless_disposition_is_allow(tmp_path):
    workflow = (ROOT / ".github" / "workflows" / "governance-gate.yml").read_text(encoding="utf-8")
    exit_line = 'if [ "$status" -eq 0 ] && [ "$disposition" = "ALLOW" ]; then exit 0; else exit 1; fi'
    assert exit_line in workflow
    assert 'echo "disposition=$disposition" >> "$GITHUB_OUTPUT"' in workflow
    assert "print(disposition)" in workflow
    assert "exit $status" not in workflow

    def exit_for(status, disposition):
        script = 'status="$1"\ndisposition="$2"\n' + exit_line + "\n"
        return subprocess.run(["bash", "-c", script, "bash", str(status), disposition]).returncode

    assert exit_for(0, "ALLOW") == 0
    for disposition in ("FAIL_CLOSED", "DENY", "PASS", "UNKNOWN", ""):
        assert exit_for(0, disposition) != 0, disposition
        assert exit_for(1, disposition) != 0, disposition
    assert exit_for(1, "ALLOW") != 0

    step = """
set +e
status=$1
disposition=$(python3 -I -c 'import importlib.util
disposition = "FAIL_CLOSED"
try:
    spec = importlib.util.spec_from_file_location("governance_gate", ".stegverse-sdk/stegverse/governance_gate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    disposition = module.read_workflow_disposition("stegverse-governance-report.json")
except Exception:
    disposition = "FAIL_CLOSED"
print(disposition)')
echo "disposition=$disposition" > github_output.txt
if [ "$status" -eq 0 ] && [ "$disposition" = "ALLOW" ]; then exit 0; else exit 1; fi
"""

    def run_step(directory, status):
        return subprocess.run(["bash", "-c", step, "bash", str(status)], cwd=directory,
                              capture_output=True, text=True)

    old = tmp_path / "old"
    sdk = old / ".stegverse-sdk" / "stegverse"
    sdk.mkdir(parents=True)
    (sdk / "governance_gate.py").write_text("VALUE = 'pre-534'\n", encoding="utf-8")
    (old / "stegverse-governance-report.json").write_text('{"disposition": "PASS"}\n', encoding="utf-8")
    missing_helper = run_step(old, 0)
    assert missing_helper.returncode != 0, missing_helper.stderr
    assert (old / "github_output.txt").read_text(encoding="utf-8").strip() == "disposition=FAIL_CLOSED"

    current = tmp_path / "current"
    current_sdk = current / ".stegverse-sdk" / "stegverse"
    current_sdk.mkdir(parents=True)
    (current_sdk / "governance_gate.py").write_text(
        (ROOT / "stegverse" / "governance_gate.py").read_text(encoding="utf-8"), encoding="utf-8")
    (current / "stegverse-governance-report.json").write_text('{"disposition": "FAIL_CLOSED"}\n', encoding="utf-8")
    closed = run_step(current, 0)
    assert closed.returncode != 0, closed.stderr
    assert (current / "github_output.txt").read_text(encoding="utf-8").strip() == "disposition=FAIL_CLOSED"
    (current / "stegverse-governance-report.json").write_text('{"disposition": "ALLOW"}\n', encoding="utf-8")
    allowed = run_step(current, 0)
    assert allowed.returncode == 0, allowed.stderr
    assert (current / "github_output.txt").read_text(encoding="utf-8").strip() == "disposition=ALLOW"
    checker_failed = run_step(current, 1)
    assert checker_failed.returncode != 0


def test_gate_imports_only_the_standard_library_and_runs_without_the_package_dependencies(tmp_path):
    for module in ("governance_gate", "portable_governance_verifier", "interlock_transition", "interlock_return",
                   "spe_steggate_bridge", "organization_record_names", "structural_validator_candidate"):
        tree = ast.parse((ROOT / "stegverse" / f"{module}.py").read_text(encoding="utf-8"))
        absolute = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        absolute |= {n.module.split(".")[0] for n in ast.walk(tree)
                     if isinstance(n, ast.ImportFrom) and n.module and n.level == 0}
        assert absolute <= set(sys.stdlib_module_names) | {"__future__"}, (module, absolute)
    root = _repo(tmp_path, bundles=[("ok.json", _bundle())])
    # -I: isolated mode, so neither the repository checkout nor site-packages supplies stegverse.
    result = subprocess.run([sys.executable, "-I", str(ROOT / "stegverse" / "governance_gate.py"), str(root)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["disposition"] == "ALLOW"
