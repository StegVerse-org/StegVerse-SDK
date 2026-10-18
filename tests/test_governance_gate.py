"""Governance gate: installable, stdlib-only, evidence-only check for any repository."""
import ast
import json
import subprocess
import sys
from pathlib import Path

from stegverse import governance_gate
from tests.test_portable_governance_verifier import _bundle

ROOT = Path(__file__).resolve().parents[1]


def _repo(tmp_path, bundles=(), schemas=()):
    gov = tmp_path / ".stegverse" / "governance"
    gov.mkdir(parents=True)
    for name, document in bundles:
        (gov / name).write_text(json.dumps(document), encoding="utf-8")
    for name, document in schemas:
        (tmp_path / name).write_text(json.dumps(document), encoding="utf-8")
    return tmp_path


def test_valid_bundle_passes_and_report_claims_no_authority(tmp_path):
    root = _repo(tmp_path, bundles=[("ok.json", _bundle())],
                 schemas=[("a.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object"}),
                          ("b.schema.json", {"type": "object", "patternProperties": {}})])
    report = governance_gate.run_gate(root)
    assert report["disposition"] == "PASS"
    assert report["reason"] == "ALL_BUNDLES_VERIFIED"
    assert [b["status"] for b in report["bundles"]] == ["PASS"]
    assert (report["schemas"]["compatible"], report["schemas"]["total"]) == (1, 2)
    assert report["usage"]["bundles_verified"] == 1
    assert report["tier"] == "FREE"
    assert not any(v for k, v in report["authority"].items() if k != "verification_authority")
    assert report["authority"]["verification_authority"] == "NONE"


def test_tampered_or_malformed_bundle_fails_closed(tmp_path):
    tampered = _bundle()
    tampered["run_id"] = "different-run"
    root = _repo(tmp_path, bundles=[("tampered.json", tampered), ("list.json", [])])
    report = governance_gate.run_gate(root)
    assert report["disposition"] == "FAIL_CLOSED"
    assert report["reason"] == "BUNDLE_VERIFICATION_FAILED"
    assert {b["status"] for b in report["bundles"]} == {"FAIL_CLOSED"}
    (tmp_path / ".stegverse" / "governance" / "broken.json").write_text("{", encoding="utf-8")
    assert governance_gate.run_gate(root)["disposition"] == "FAIL_CLOSED"


def test_no_bundles_passes_and_free_tier_limit_fails_closed(tmp_path, monkeypatch):
    root = _repo(tmp_path)
    assert governance_gate.run_gate(root)["reason"] == "NO_GOVERNANCE_BUNDLES_FOUND"
    monkeypatch.setitem(governance_gate.FREE_TIER_LIMITS, "bundles", 0)
    root = _repo(tmp_path / "over", bundles=[("ok.json", _bundle())])
    report = governance_gate.run_gate(root)
    assert (report["disposition"], report["reason"]) == ("FAIL_CLOSED", "FREE_TIER_LIMIT_EXCEEDED")


def test_cli_exit_codes_and_summary(tmp_path):
    root = _repo(tmp_path, bundles=[("ok.json", _bundle())])
    summary = tmp_path / "summary.md"
    output = tmp_path / "report.json"
    assert governance_gate.main([str(root), "--output", str(output), "--summary", str(summary)]) == 0
    assert json.loads(output.read_text())["disposition"] == "PASS"
    assert "StegVerse governance gate: PASS" in summary.read_text()
    bad = _repo(tmp_path / "bad", bundles=[("x.json", {"schema": "nope"})])
    assert governance_gate.main([str(bad), "--output", str(tmp_path / "bad.json")]) == 1


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
    assert json.loads(result.stdout)["disposition"] == "PASS"
