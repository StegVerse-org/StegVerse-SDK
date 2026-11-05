"""Roadmap expected-capability conformance.

Binds the expectations in docs/SDK_EXPECTED_CAPABILITY_MATRIX.md to
repository state. These tests fail when the repository's claims and
the roadmap's expectations drift apart: a release candidate that
quietly gains a tag, a capabilities posture that overclaims, a
qualification grammar that loses a disposition, or a version row
(1.7.0) that acquires an undocumented capability allocation.

Fixture-free by design: they run under both the repository's
vendored stdlib runner and pytest.
"""
import json
from copy import deepcopy
from pathlib import Path

from stegverse.capability_inventory import qualify_requirements
from stegverse.manifest_plan import derive_execution_plan, verify_plan_lineage

ROOT = Path(__file__).resolve().parents[1]

SUPPORTED_REQ = {"requirement_id": "r-supported", "capability_id": "native_source_math"}


def _load_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_release_candidate_honesty_matches_version_json():
    version = _load_json("VERSION.json")
    assert version["component_version"] == "1.3.0"
    assert version["version_stage"] == "RELEASE_CANDIDATE"
    # The 1.3.0 gate is TV/TVC tag/release publication. Until that
    # evidence exists, the release block must stay empty.
    assert version["release"]["tag"] is None
    assert version["release"]["release_evidence"] == []
    candidate = version["release_candidate"]
    assert candidate["target_tag"] == "v1.3.0"
    assert candidate["tag_publication"] == "READY_PENDING_TV_TVC_EXECUTION"
    assert candidate["package_publication"] == "PENDING_TAG_AND_GITHUB_RELEASE"
    # The 1.4 line is development only and carries no release identity.
    assert version["development_line"]["version"] == "1.4.0.dev0"
    assert version["development_line"]["release_identity"] is False


def test_capabilities_posture_blocks_overclaim():
    posture = _load_json("sdk.capabilities.json")["validation_posture"]
    assert posture["implementation"] == "installed"
    assert posture["current_main_result"] == "not_observed"
    assert posture["release_ready"] is False
    assert posture["production_binding_enabled"] is False


def test_v15_five_dispositions_each_with_failure_evidence():
    manifest = {"payload": {"value": 7}}
    requirements = [
        dict(SUPPORTED_REQ),
        {
            "requirement_id": "r-missing",
            "capability_id": "native_source_math",
            "required_inputs": ["absent_field"],
        },
        {"requirement_id": "r-unsupported", "capability_id": "not-installed"},
        {
            "requirement_id": "r-version",
            "capability_id": "native_source_math",
            "version_compatible": False,
        },
        {
            "requirement_id": "r-probe",
            "capability_id": "native_source_math",
            "authentic_runtime_evidence_required": True,
        },
    ]
    qualification = qualify_requirements(manifest, requirements)
    by_id = {row["requirement_id"]: row for row in qualification["results"]}
    assert {row["disposition"] for row in by_id.values()} == {
        "SUPPORTED",
        "MISSING_INPUT",
        "UNSUPPORTED",
        "PROBE_REQUIRED",
        "VERSION_INCOMPATIBLE",
    }
    for row in by_id.values():
        if row["disposition"] == "SUPPORTED":
            assert row["failed_predicate"] is None
        else:
            # Limitations are explained precisely: the failed
            # requirement, its predicate, and the permitted
            # correction travel with the result.
            assert row["failed_predicate"]
            assert row["permitted_correction"]
    assert qualification["execution_authorized"] is False
    assert qualification["route_substitution_permitted"] is False


def test_v15_two_evaluators_same_interface_partial_runs_declared():
    evaluators = [
        {"evaluator": "framework-alpha", "payload": {"value": 1}},
        {"evaluator": "framework-beta", "payload": {"value": 2}},
    ]
    requirements = [
        dict(SUPPORTED_REQ),
        {"requirement_id": "r-unsupported", "capability_id": "not-installed"},
    ]
    plans = []
    for manifest in evaluators:
        original = deepcopy(manifest)
        plan = derive_execution_plan(manifest, requirements)
        # The original manifest is preserved; adaptation derives a
        # separate, lineage-bound plan.
        assert manifest == original
        assert verify_plan_lineage(manifest, requirements, plan) is True
        steps = {step["requirement_id"]: step for step in plan["steps"]}
        # A partial run is declared per requirement, never smoothed
        # into a silent success of the original manifest.
        assert steps["r-supported"]["qualification_disposition"] == "SUPPORTED"
        assert steps["r-unsupported"]["qualification_disposition"] == "UNSUPPORTED"
        assert steps["r-unsupported"]["adaptation"] is None
        assert plan["execution_authorized"] is False
        plans.append(plan)
    # The two evaluators' plans are bound to their own manifests:
    # neither plan verifies against the other's manifest.
    assert verify_plan_lineage(evaluators[0], requirements, plans[1]) is False
    assert verify_plan_lineage(evaluators[1], requirements, plans[0]) is False


def test_matrix_document_keeps_v17_undefined():
    matrix = (ROOT / "docs" / "SDK_EXPECTED_CAPABILITY_MATRIX.md").read_text(
        encoding="utf-8"
    )
    for version in ("1.3.0", "1.4.0", "1.5.0", "1.6.0"):
        assert version in matrix
    v17_section = matrix.split("### SDK 1.7.0", 1)[1]
    assert "UNDEFINED" in v17_section
    assert "No feature allocation for 1.7.0 exists" in v17_section
