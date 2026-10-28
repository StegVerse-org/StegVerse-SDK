"""CM-GOV-1: old pin ba5bbf42 vs SDK#534 gate behavior, and install/rollback at a pinned SHA.

The recorded evidence is evidence/cm-gov-1-governance-gate-pin-reproduction.json. The working-tree
test runs everywhere (no git history needed) and checks this checkout against whichever recorded ref
has the same gate and workflow blobs. The full re-run needs both pinned commits in the local clone.
"""
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "cm-gov-1-governance-gate-pin-reproduction.json"
SPEC = importlib.util.spec_from_file_location("reproduce_governance_gate_pins",
                                              ROOT / "scripts" / "reproduce_governance_gate_pins.py")
repro = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repro)

RECORDED = json.loads(EVIDENCE.read_text(encoding="utf-8"))
OLD, NEW, SELF_DEFAULT = RECORDED["refs"]


def _without_digests(scenarios):
    return {name: {"checker": {k: v for k, v in s["checker"].items() if k != "report_sha256"},
                   "workflow_step": s["workflow_step"]} for name, s in scenarios.items()}


def test_old_pin_passes_an_empty_glob_and_emits_pass_without_six_fields():
    assert OLD["ref"] == repro.DEFAULT_REFS[0]
    empty = OLD["scenarios"]["empty"]
    assert (empty["checker"]["exit_status"], empty["checker"]["observed_disposition"]) == (0, "PASS")
    assert empty["checker"]["reason"] == "NO_GOVERNANCE_BUNDLES_FOUND"
    assert empty["workflow_step"] == {"disposition_output": "PASS", "job_exit_status": 0}
    assert OLD["dispositions_observed"] == ["FAIL_CLOSED", "PASS"]
    assert all(s["checker"]["six_fields_present"] == [] for s in OLD["scenarios"].values())
    assert OLD["workflow_sdk_ref_default"] == "main" and not OLD["actions_pinned_by_sha"]


def test_pr534_fails_closed_on_an_empty_glob_with_all_six_fields():
    assert NEW["ref"] == repro.DEFAULT_REFS[1]
    assert NEW["dispositions_observed"] == ["ALLOW", "FAIL_CLOSED"]
    for name in ("empty", "tampered", "not_object"):
        checker = NEW["scenarios"][name]["checker"]
        assert (checker["exit_status"], checker["observed_disposition"]) == (1, "FAIL_CLOSED")
        assert checker["six_fields_present"] == list(repro.SIX_FIELDS)
        assert NEW["scenarios"][name]["workflow_step"] == {"disposition_output": "FAIL_CLOSED", "job_exit_status": 1}
    valid = NEW["scenarios"]["valid"]
    assert (valid["checker"]["observed_disposition"], valid["workflow_step"]["job_exit_status"]) == ("ALLOW", 0)
    assert NEW["actions_pinned_by_sha"]


def test_pr534_workflow_with_its_default_sdk_ref_fails_closed_even_on_a_valid_bundle():
    # The default sdk_ref is the old checker, which has no read_workflow_disposition and emits PASS.
    # The new run step therefore maps every outcome to FAIL_CLOSED: safe, but unusable until the pin
    # follow-up retargets sdk_ref to the #534 merge commit.
    assert NEW["workflow_sdk_ref_default"] == OLD["ref"]
    assert set(NEW["workflow_with_default_sdk_ref"]) == {"empty", "valid", "tampered", "not_object"}
    assert all(step == {"disposition_output": "FAIL_CLOSED", "job_exit_status": 1}
               for step in NEW["workflow_with_default_sdk_ref"].values())


def test_pr534_job_workflow_sha_default_allows_a_valid_bundle_and_fails_closed_otherwise():
    # The repair for the finding above: an empty sdk_ref resolves to job.workflow_sha, so a caller that
    # keeps the default runs the checker of the very commit it pinned. Recorded at an ancestor commit.
    assert SELF_DEFAULT["ref"] == repro.DEFAULT_REFS[2]
    assert SELF_DEFAULT["workflow_sdk_ref_default"] == repro.SELF_REF_DEFAULT == "job.workflow_sha"
    assert SELF_DEFAULT["gate_blob"] == NEW["gate_blob"]
    assert SELF_DEFAULT["actions_pinned_by_sha"]
    defaulted = SELF_DEFAULT["workflow_with_default_sdk_ref"]
    assert defaulted["valid"] == {"disposition_output": "ALLOW", "job_exit_status": 0}
    for name in ("empty", "tampered", "not_object"):
        assert defaulted[name] == {"disposition_output": "FAIL_CLOSED", "job_exit_status": 1}
        assert SELF_DEFAULT["scenarios"][name]["checker"]["six_fields_present"] == list(repro.SIX_FIELDS)
    assert defaulted == {name: s["workflow_step"] for name, s in SELF_DEFAULT["scenarios"].items()}


def test_both_pins_install_and_roll_back_without_touching_the_caller():
    assert RECORDED["pin_rollback_reproduces_first_ref"] is True
    for ref in RECORDED["refs"]:
        assert all(r == {"caller_tree_unchanged": True, "rollback_restores_workspace": True}
                   for r in ref["install_rollback"].values())
        assert all(s["checker"]["authority_all_false"] for s in ref["scenarios"].values())


def test_working_tree_reproduces_the_recorded_ref_with_the_same_gate():
    tree = repro.reproduce_tree()
    matches = [r for r in RECORDED["refs"]
               if (r["gate_blob"], r["workflow_blob"]) == (tree["gate_blob"], tree["workflow_blob"])]
    if not matches:
        raise unittest.SkipTest("gate or workflow changed since CM-GOV-1 was recorded; "
                                "rerun scripts/reproduce_governance_gate_pins.py")
    assert _without_digests(tree["scenarios"]) == _without_digests(matches[0]["scenarios"])
    assert tree["install_rollback"] == matches[0]["install_rollback"]


def _has_commit(ref):
    return subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{ref}^{{commit}}"],
                          capture_output=True).returncode == 0


def test_full_reproduction_matches_the_recorded_evidence_byte_for_byte():
    if not all(_has_commit(ref) for ref in repro.DEFAULT_REFS):
        raise unittest.SkipTest("pinned commits are not in this clone (shallow checkout)")
    result = repro.reproduce(ROOT, repro.DEFAULT_REFS)
    assert json.dumps(result, indent=2, sort_keys=True) + "\n" == EVIDENCE.read_text(encoding="utf-8")


def test_run_step_extraction_reads_the_block_scalar():
    workflow = "steps:\n  - id: run\n    env:\n      A: b\n    run: |\n      set +e\n      echo hi\n\n      exit 0\n  - if: always()\n"
    assert repro.run_step_script(workflow) == "set +e\necho hi\n\nexit 0\n"
    with pytest.raises(ValueError):
        repro.run_step_script("steps: []\n")
