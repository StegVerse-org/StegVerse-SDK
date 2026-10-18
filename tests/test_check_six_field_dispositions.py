"""Tests for scripts/check_six_field_dispositions.py (stdlib-only six-field check)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_six_field_dispositions.py"
_spec = importlib.util.spec_from_file_location("check_six_field_dispositions", SCRIPT)
chk = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(chk)

SIX = {
    "failure_code": "X_FAILED",
    "failed_predicate": "X_HOLDS",
    "required_evidence_or_repair": "supply X",
    "retry_entrypoint": "scripts/x.py",
    "owning_existing_goal": "GOAL-001",
    "next_attempt": "re-run after X",
}


def _write(path: Path, content) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        path.write_text(content, encoding="utf-8")
    else:
        path.write_text(json.dumps(content), encoding="utf-8")
    return path


def _run(*paths, legacy=None):
    return chk.run([str(p) for p in paths], str(legacy) if legacy else None)


# ----------------------------------------------------------------- JSON


def test_compliant_json_allows(tmp_path):
    _write(tmp_path / "r.json", {"disposition": "FAIL_CLOSED", **SIX})
    _write(tmp_path / "ok.json", {"disposition": "ALLOW"})
    report = _run(tmp_path)
    assert report["disposition"] == "ALLOW"
    assert report["findings"] == []
    assert report["scanned"]["json"] == 2
    for field in chk.SIX_FIELDS:
        assert field not in report


def test_fail_closed_missing_fields_is_finding(tmp_path):
    _write(tmp_path / "r.json", {"disposition": "FAIL_CLOSED", "failure_code": "ONLY_CODE", "next_attempt": ""})
    report = _run(tmp_path)
    assert report["disposition"] == "FAIL_CLOSED"
    assert report["failure_code"] == "SIX_FIELD_DISPOSITION_INCOMPLETE"
    [finding] = report["findings"]
    assert finding["pointer"] == ""
    assert finding["value"] == "FAIL_CLOSED"
    assert "failure_code" not in finding["missing_fields"]
    assert "next_attempt" in finding["missing_fields"]  # empty value counts as missing
    assert len(finding["missing_fields"]) == 5


def test_fields_nested_under_child_object_still_finding(tmp_path):
    _write(tmp_path / "r.json", {"status": "DENY", "actionable_disposition": dict(SIX)})
    report = _run(tmp_path)
    [finding] = report["findings"]
    assert finding["key"] == "status"
    assert finding["missing_fields"] == list(chk.SIX_FIELDS)


def test_deny_in_deep_list_found_with_pointer(tmp_path):
    doc = {"runs": [{"cases": [{"decision": "ALLOW"}, {"decision": "DENY", "failure_code": "C"}]}],
           "a/b": {"result": "REFUSED", **SIX}}
    _write(tmp_path / "r.json", doc)
    report = _run(tmp_path)
    [finding] = report["findings"]
    assert finding["pointer"] == "/runs/0/cases/1"
    assert finding["value"] == "DENY"


def test_non_allow_match_is_case_sensitive_and_string_only(tmp_path):
    _write(tmp_path / "r.json", {"items": [{"status": "blocked"}, {"status": ["DENY"]}, {"result": {"x": 1}}]})
    assert _run(tmp_path)["disposition"] == "ALLOW"


def test_schema_files_ignored(tmp_path):
    _write(tmp_path / "a.json", {"$schema": "https://json-schema.org/draft/2020-12/schema",
                                 "properties": {"status": {"enum": ["DENY"]}}, "default": {"status": "DENY"}})
    _write(tmp_path / "b.schema.json", {"status": "BLOCKED"})
    _write(tmp_path / "c.json", {"disposition": "ALLOW"})
    report = _run(tmp_path)
    assert report["disposition"] == "ALLOW"
    reasons = {Path(s["path"]).name: s["reason"] for s in report["scanned"]["skipped"]}
    assert reasons == {"a.json": "json_schema", "b.schema.json": "json_schema"}


def test_unparsable_json_skipped_and_recorded(tmp_path):
    _write(tmp_path / "bad.json", "{not json")
    _write(tmp_path / "good.json", {"disposition": "ALLOW"})
    report = _run(tmp_path)
    assert report["disposition"] == "ALLOW"
    assert [s["reason"] for s in report["scanned"]["skipped"]] == ["unparsable_json"]


def test_skips_excluded_directories(tmp_path):
    _write(tmp_path / "node_modules" / "r.json", {"status": "DENY"})
    _write(tmp_path / ".git" / "r.json", {"status": "DENY"})
    _write(tmp_path / "ok.json", {"status": "ALLOW"})
    report = _run(tmp_path)
    assert report["disposition"] == "ALLOW"
    assert report["scanned"]["json"] == 1


# ----------------------------------------------------------------- workflows

ECHO_ONLY = """\
name: x
on: push
jobs:
  j:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: gate
        run: |
          if [ "$X" != ok ]; then
            echo "disposition=FAIL_CLOSED" >> "$GITHUB_OUTPUT"
            exit 1
          fi
      - name: after
        run: echo done
"""

ALL_SIX = """\
jobs:
  j:
    steps:
      - run: |
          {
            echo "disposition=FAIL_CLOSED"
            echo "failure_code=X"
            echo "failed_predicate=Y"
            echo "required_evidence_or_repair=Z"
            echo "retry_entrypoint=.github/workflows/x.yml"
            echo "owning_existing_goal=G"
            echo "next_attempt=rerun"
          } >> "$GITHUB_OUTPUT"
"""


def test_workflow_echo_without_fields_is_finding(tmp_path):
    wf = _write(tmp_path / ".github" / "workflows" / "x.yml", ECHO_ONLY)
    report = _run(wf)
    [finding] = report["findings"]
    assert finding["kind"] == "workflow"
    assert finding["line"] == 9
    assert finding["tokens"] == ["FAIL_CLOSED"]
    assert finding["missing_fields"] == list(chk.SIX_FIELDS)


def test_workflow_block_with_all_six_ok(tmp_path):
    _write(tmp_path / "w.yaml", ALL_SIX)
    report = _run(tmp_path)
    assert report["disposition"] == "ALLOW"
    assert report["scanned"]["workflows"] == 1


def test_single_line_run(tmp_path):
    _write(tmp_path / "w.yml", "jobs:\n  j:\n    steps:\n      - run: echo \"::error::DENY failure_code=X\"\n")
    report = _run(tmp_path)
    [finding] = report["findings"]
    assert finding["line"] == 4
    assert "failure_code" not in finding["missing_fields"]


def test_allow_only_and_non_output_tokens_not_findings(tmp_path):
    text = (
        "jobs:\n  j:\n    steps:\n"
        "      - run: |\n"
        "          echo \"disposition=ALLOW\" >> \"$GITHUB_OUTPUT\"\n"
        "          if [ \"$D\" = FAIL_CLOSED ]; then exit 1; fi\n"
        "          # echo FAIL_CLOSED in a comment\n"
        "          echo BLOCK_SIZE=4\n"
    )
    _write(tmp_path / "w.yml", text)
    assert _run(tmp_path)["findings"] == []


def test_heredoc_body_counts_as_output(tmp_path):
    text = (
        "jobs:\n  j:\n    steps:\n"
        "      - run: |\n"
        "          cat <<'EOF' > out.json\n"
        "          {\"status\": \"BLOCKED\"}\n"
        "          EOF\n"
    )
    _write(tmp_path / "w.yml", text)
    assert len(_run(tmp_path)["findings"]) == 1


def test_run_block_extent_ends_at_dedent(tmp_path):
    text = (
        "jobs:\n  j:\n    steps:\n"
        "      - run: |\n"
        "          echo \"DENY\"\n"
        "      - run: |\n"
        "          echo failure_code failed_predicate required_evidence_or_repair\n"
        "          echo retry_entrypoint owning_existing_goal next_attempt\n"
    )
    _write(tmp_path / "w.yml", text)
    [finding] = _run(tmp_path)["findings"]
    assert finding["line"] == 4


# ----------------------------------------------------------------- report-level


def test_empty_directory_is_fail_closed(tmp_path):
    report = _run(tmp_path)
    assert report["disposition"] == "FAIL_CLOSED"
    assert report["failure_code"] == "NO_INPUTS_SCANNED"
    for field in chk.SIX_FIELDS:
        assert report[field]


def test_only_unparsable_inputs_is_no_inputs(tmp_path):
    _write(tmp_path / "bad.json", "nope")
    assert _run(tmp_path)["failure_code"] == "NO_INPUTS_SCANNED"


def test_report_fail_closed_carries_six_fields(tmp_path):
    _write(tmp_path / "r.json", {"status": "BLOCK"})
    report = _run(tmp_path)
    assert report["schema"] == "stegverse.six-field-disposition-check.v1"
    assert report["failure_code"] == "SIX_FIELD_DISPOSITION_INCOMPLETE"
    assert report["failed_predicate"] == "EVERY_NON_ALLOW_RESULT_CARRIES_SIX_FIELDS"
    assert report["retry_entrypoint"] == "scripts/check_six_field_dispositions.py"
    assert report["owning_existing_goal"] == "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001"
    # The report is itself a compliant result under its own rule.
    assert chk.scan_json_value(report, "report") == []


def test_exemption_honoured(tmp_path):
    _write(tmp_path / "legacy" / "old.json", {"status": "DENY"})
    _write(tmp_path / "new.json", {"status": "ALLOW"})
    legacy = _write(tmp_path / "exempt.json", {"entries": [
        {"path": "legacy/old.json", "reason": "frozen historical receipt", "owning_existing_goal": "G-1"}]})
    report = _run(tmp_path / "legacy", tmp_path / "new.json", legacy=legacy)
    assert report["disposition"] == "ALLOW"
    assert report["findings"] == []
    [ex] = report["exempted"]
    assert ex["exemption"]["owning_existing_goal"] == "G-1"


def test_exemption_glob(tmp_path):
    _write(tmp_path / "legacy" / "old.json", {"status": "DENY"})
    legacy = _write(tmp_path / "exempt.json", {"entries": [
        {"path": "*/legacy/*.json", "reason": "r", "owning_existing_goal": "G"}]})
    assert _run(tmp_path / "legacy", legacy=legacy)["disposition"] == "ALLOW"


@pytest.mark.parametrize("content", [
    {"entries": [{"path": "x.json", "reason": "r"}]},
    {"entries": [{"path": "x.json", "reason": "", "owning_existing_goal": "G"}]},
    {"entries": "x"},
    {"nope": []},
    "not json",
])
def test_malformed_exemption_fail_closed(tmp_path, content):
    _write(tmp_path / "ok.json", {"status": "ALLOW"})
    legacy = _write(tmp_path / "exempt" / "e.txt", content)
    report = _run(tmp_path / "ok.json", legacy=legacy)
    assert report["disposition"] == "FAIL_CLOSED"
    assert report["failure_code"] == "EXEMPTION_DECLARATION_INCOMPLETE"
    assert report["exemption_errors"]
    for field in chk.SIX_FIELDS:
        assert report[field]


def test_output_is_deterministic(tmp_path):
    for name in ("b.json", "a.json", "c/z.json"):
        _write(tmp_path / name, {"status": "DENY"})
    r1 = json.dumps(_run(tmp_path), sort_keys=True)
    r2 = json.dumps(_run(tmp_path), sort_keys=True)
    assert r1 == r2
    paths = [Path(f["path"]).name for f in json.loads(r1)["findings"]]
    assert paths == ["a.json", "b.json", "z.json"]


# ----------------------------------------------------------------- CLI


def _cli(*args, cwd):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          cwd=cwd, capture_output=True, text=True)


def test_cli_exit_codes_and_output(tmp_path):
    _write(tmp_path / "ok" / "r.json", {"disposition": "ALLOW"})
    _write(tmp_path / "bad" / "r.json", {"disposition": "REFUSED"})
    (tmp_path / "empty").mkdir()

    ok = _cli("ok", cwd=tmp_path)
    assert ok.returncode == 0, ok.stderr
    assert json.loads(ok.stdout)["disposition"] == "ALLOW"

    bad = _cli("bad", "--output", "report.json", cwd=tmp_path)
    assert bad.returncode == 1
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["findings"][0]["path"] == "bad/r.json"

    empty = _cli("empty", cwd=tmp_path)
    assert empty.returncode == 1
    assert json.loads(empty.stdout)["failure_code"] == "NO_INPUTS_SCANNED"


def test_cli_default_path_is_cwd(tmp_path):
    _write(tmp_path / "r.json", {"disposition": "ALLOW"})
    assert _cli(cwd=tmp_path).returncode == 0
