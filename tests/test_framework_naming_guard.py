"""An artifact is named by its capability; history is declared, not erased."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

from stegverse.framework_naming_guard import (
    BASELINE_SCHEMA,
    CAPABILITY_NAMED,
    HISTORICAL,
    PENDING_RENAME,
    RECOGNIZED_EXTERNAL_SCHEMES,
    STALE_BASELINE,
    UNDECLARED,
    FrameworkNamingGuardError,
    evaluate_framework_naming,
    framework_named_paths,
    owned_schema_ids,
    segments,
    validate_baseline,
)


def _baseline(entries):
    return {"schema": BASELINE_SCHEMA, "entries": entries}


# --- detection -------------------------------------------------------------

def test_mirror_does_not_match_mir():
    """Eighty-five mirror-handoff documents must not be swept up by a MIR search."""
    assert "mirror" in segments("docs/SDK_MIRROR_HANDOFF.md")
    assert framework_named_paths(["docs/SDK_MIRROR_HANDOFF.md"]) == []
    assert framework_named_paths(["docs/ECOSYSTEM_MIRROR_HANDOFF.md"]) == []


def test_a_framework_segment_is_detected_in_any_position():
    for path in (
        "stegverse/mir_leaf_v3.py",
        "inspection/examples/elan-relational-state-test1.json",
        "inspection/examples/hgai-governance-reference-graph.json",
        "inspection/examples/sdk-test3-richard-seam.processor-request.json",
    ):
        assert framework_named_paths([path]) == [path], path


def test_a_doc_that_is_both_mir_named_and_a_mirror_handoff_is_detected():
    """Matching on the MIR segment, not on the word mirror."""
    path = "docs/MIR_SDK_RETURN_MATERIALIZATION_MIRROR_HANDOFF.md"
    assert framework_named_paths([path]) == [path]


def test_capability_named_paths_are_clean():
    assert framework_named_paths([
        "stegverse/capability_graph.py",
        "inspection/examples/sdk-test1-purpose-worker.processor-request.json",
        "stegverse/transparency_log_leaf.py",
    ]) == []


# --- ours versus theirs ----------------------------------------------------

def test_sdk_owned_identifier_carrying_a_framework_name_is_reported():
    assert owned_schema_ids('"stegverse.sdk.mir-run2-replay/v1"') == [
        "stegverse.sdk.mir-run2-replay/v1"
    ]


def test_scheme_the_counterpart_owns_is_recognized_not_violated():
    """Recognizing an external format is data, exactly as source_framework is."""
    for scheme in RECOGNIZED_EXTERNAL_SCHEMES:
        assert owned_schema_ids(f'"{scheme}"') == [], scheme


def test_a_quoted_source_path_is_not_counted_as_an_identifier():
    """Paths are reported by the path scan; counting them twice double-declares."""
    assert owned_schema_ids('"stegverse/mir_leaf_v3.py"') == []


# --- the rule --------------------------------------------------------------

def test_clean_repository_conforms():
    result = evaluate_framework_naming(
        paths=["stegverse/capability_graph.py"], baseline=_baseline([])
    )
    assert result["verdict"] == CAPABILITY_NAMED
    assert result["conforming"] is True


def test_a_new_framework_named_artifact_fails():
    result = evaluate_framework_naming(
        paths=["stegverse/elan_new_thing.py"], baseline=_baseline([])
    )
    assert result["verdict"] == UNDECLARED
    assert result["conforming"] is False
    assert result["undeclared"] == ["stegverse/elan_new_thing.py"]


def test_declaring_history_does_not_excuse_a_new_artifact():
    """The property that makes the set shrink rather than grow."""
    result = evaluate_framework_naming(
        paths=["stegverse/mir_leaf_v3.py", "stegverse/mir_brand_new.py"],
        baseline=_baseline([
            {"artifact": "stegverse/mir_leaf_v3.py", "disposition": HISTORICAL,
             "reason": "pre-org-receipt provenance"},
        ]),
    )
    assert result["verdict"] == UNDECLARED
    assert result["undeclared"] == ["stegverse/mir_brand_new.py"]
    assert result["historical"] == ["stegverse/mir_leaf_v3.py"]


def test_a_baseline_entry_whose_artifact_is_gone_fails():
    """The baseline cannot rot into a list of things nobody checks."""
    result = evaluate_framework_naming(
        paths=["stegverse/capability_graph.py"],
        baseline=_baseline([
            {"artifact": "stegverse/mir_deleted.py", "disposition": HISTORICAL,
             "reason": "pre-org-receipt provenance"},
        ]),
    )
    assert result["verdict"] == STALE_BASELINE
    assert result["conforming"] is False
    assert result["stale_baseline_entries"] == ["stegverse/mir_deleted.py"]


def test_renaming_an_artifact_away_shrinks_the_declared_set():
    after = evaluate_framework_naming(
        paths=["stegverse/transparency_log_leaf.py"], baseline=_baseline([])
    )
    assert after["conforming"] is True
    assert after["observed_count"] == 0


# --- baseline integrity ----------------------------------------------------

def test_pending_rename_must_name_its_capability():
    with pytest.raises(FrameworkNamingGuardError, match="requires capability_name"):
        validate_baseline(_baseline([
            {"artifact": "stegverse/mir_leaf_v3.py", "disposition": PENDING_RENAME,
             "reason": "to be renamed"},
        ]))


def test_a_capability_name_may_not_itself_carry_a_framework_token():
    with pytest.raises(FrameworkNamingGuardError, match="still carries a framework token"):
        validate_baseline(_baseline([
            {"artifact": "stegverse/mir_leaf_v3.py", "disposition": PENDING_RENAME,
             "capability_name": "stegverse/mir_transparency_log.py", "reason": "x"},
        ]))


@pytest.mark.parametrize("entries,match", [
    ([{"artifact": "a", "disposition": HISTORICAL, "reason": "r"},
      {"artifact": "a", "disposition": HISTORICAL, "reason": "r"}], "duplicate"),
    ([{"artifact": "a", "disposition": "INVENTED", "reason": "r"}], "disposition must be"),
    ([{"artifact": "a", "disposition": HISTORICAL}], "reason is required"),
    ([{"artifact": "", "disposition": HISTORICAL, "reason": "r"}], "requires artifact"),
])
def test_baseline_defects_raise(entries, match):
    with pytest.raises(FrameworkNamingGuardError, match=match):
        validate_baseline(_baseline(entries))


def test_guard_grants_nothing():
    result = evaluate_framework_naming(paths=[], baseline=_baseline([]))
    assert result["authority_effect"] == "NONE_SOURCE_NAMING_ONLY"
    assert all(v is False for v in result["authority_boundary"].values())


# --- the live repository ----------------------------------------------------

def test_committed_baseline_conforms_on_this_checkout():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_framework_naming.py"), "--strict", "--json"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    result = json.loads(proc.stdout)
    assert result["verdict"] == CAPABILITY_NAMED
    assert result["observed_count"] == result["declared_count"]
    assert result["pending_capability_rename"], "the rename backlog should be visible"
