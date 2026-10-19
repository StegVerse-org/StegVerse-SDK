"""The StegCore pin rebind is one manifest-bound command (SDK#484 V-P4(a), V-P7)."""
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = ROOT / ".github" / "release-requests" / "stegcore-pin-rebind-9939739.json"
SPEC = importlib.util.spec_from_file_location("apply_release_pin_rebind", ROOT / "scripts" / "apply_release_pin_rebind.py")
rebind = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rebind)

REQUEST = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
OLD, NEW = REQUEST["old_pin"], REQUEST["new_pin"]
CORE_LITE = "72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8"
# After the owner runs the command the request is consumed: every target carries NEW.
CONSUMED = all(OLD not in (ROOT / item["path"]).read_text(encoding="utf-8") for item in REQUEST["rewrites"])
SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair",
              "retry_entrypoint", "owning_existing_goal", "next_attempt")


def _receipt(stegcore=NEW, core_lite=CORE_LITE):
    return {"components": [
        {"repository": "StegVerse-Labs/StegCore", "commit_sha": "1" * 40, "source_parent_commit": stegcore},
        {"repository": "Data-Continuation/core-lite", "commit_sha": "2" * 40, "source_parent_commit": core_lite},
    ]}


def _refusal(request, receipt, root=ROOT, repo=None):
    try:
        rebind.plan(request, receipt, root, repo)
    except rebind.RebindRefused as refused:
        assert all(refused.disposition[field] for field in SIX_FIELDS), refused.disposition
        return refused.disposition
    raise AssertionError("the rebind did not refuse")


def _unapplied():
    if CONSUMED:
        raise unittest.SkipTest("rebind already applied; see test_a_consumed_request_left_every_target_on_the_new_pin")


def test_a_consumed_request_left_every_target_on_the_new_pin():
    if not CONSUMED:
        raise unittest.SkipTest("rebind not applied yet")
    assert all(NEW in (ROOT / item["path"]).read_text(encoding="utf-8") for item in REQUEST["rewrites"])


def test_request_names_the_declared_pins():
    _unapplied()
    import tests.test_dependency_inventory_guard as guard
    assert (OLD, NEW) == (guard.STEGCORE_RELEASE_PIN, guard.STEGCORE_SINGLE_PIN)
    assert REQUEST["current_receipt"]["stegcore_component"]["source_parent_commit_sha"] == OLD
    assert REQUEST["required_successor_receipt"]["components"]["StegVerse-Labs/StegCore"]["source_parent_commit"] == NEW
    assert REQUEST["authority"]["this_request_authorizes_nothing"] is True


def test_without_a_receipt_it_is_the_unbound_six_field_hold():
    record = _refusal(REQUEST, None)
    assert record["failure_code"] == "STEGCORE_SINGLE_PIN_REQUIRES_RELEASE_REBIND"


def test_the_current_receipt_does_not_rebind():
    assert _refusal(REQUEST, _receipt(stegcore=OLD))["failure_code"] == "SUCCESSOR_RECEIPT_DOES_NOT_BIND_PIN"
    assert _refusal(REQUEST, _receipt(core_lite="3" * 40))["failure_code"] == "SUCCESSOR_RECEIPT_DOES_NOT_BIND_PIN"


def test_a_successor_receipt_rewrites_every_target_and_aligns():
    _unapplied()
    rewritten = rebind.plan(REQUEST, _receipt())
    assert sorted(rewritten) == sorted(item["path"] for item in REQUEST["rewrites"])
    assert all(OLD not in text and NEW in text for text in rewritten.values())
    requirements = rebind.governed_test_requirements(rewritten["pyproject.toml"])
    assert any(NEW in line and line.startswith("stegcore @") for line in requirements)
    assert f'STEGCORE_RELEASE_PIN = "{NEW}"' in rewritten["tests/test_dependency_inventory_guard.py"]


def test_check_mode_writes_nothing(tmp_path):
    _unapplied()
    for item in REQUEST["rewrites"]:
        (tmp_path / item["path"]).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / item["path"], tmp_path / item["path"])
    before = {item["path"]: (tmp_path / item["path"]).read_text() for item in REQUEST["rewrites"]}
    rewritten = rebind.plan(REQUEST, _receipt(), tmp_path)
    assert rewritten and before == {p: (tmp_path / p).read_text() for p in before}


def test_a_drifted_target_refuses_and_nothing_is_planned(tmp_path):
    _unapplied()
    for item in REQUEST["rewrites"]:
        (tmp_path / item["path"]).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / item["path"], tmp_path / item["path"])
    target = tmp_path / "pyproject.toml"
    target.write_text(target.read_text() + f"\n# {OLD}\n")
    assert _refusal(REQUEST, _receipt(), tmp_path)["failure_code"] == "REBIND_TARGET_DRIFTED"


def test_ancestry_is_verified_when_a_clone_is_given(tmp_path):
    def git(*args):
        return subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True,
                              text=True).stdout.strip()
    git("init", "-q")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "old")
    old = git("rev-parse", "HEAD")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "new")
    new = git("rev-parse", "HEAD")
    forward = copy.deepcopy(REQUEST)
    forward["old_pin"], forward["new_pin"] = new, old  # reversed: old is not an ancestor of new
    forward["rewrites"] = []
    forward["required_successor_receipt"]["components"]["StegVerse-Labs/StegCore"]["source_parent_commit"] = old
    record = _refusal(forward, _receipt(stegcore=old), ROOT, tmp_path)
    assert record["failure_code"] == "NEW_PIN_DOES_NOT_DESCEND_FROM_OLD"
