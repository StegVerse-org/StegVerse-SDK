"""The external-framework path manifests by default and executes only on request.

Before this, the SDK's complete manifesting function sat behind --prepare-only --
a name that reads as a partial step -- while the default path executed locally,
replayed and reconstructed, with replay and reconstruct defaulted on. Those are
Interlock's and the Organization's roles, not the SDK's.

Source validation only. Nothing here claims runtime observation or canonical closure.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stegverse.external_framework_runner import (  # noqa: E402
    main,
    manifest_external_framework_submission,
    prepare_external_framework_submission,
    run_external_framework,
)
from tests.test_manifest_builder import governance_request  # noqa: E402

COMMON = dict(
    data={"relational_state": "ambiguous"},
    source_framework="probe_framework",
    source_output_id="probe-output-1",
    processor_request=governance_request(),
    created_at="2026-10-02T00:00:00Z",
)


def manifested() -> dict:
    return manifest_external_framework_submission(**COMMON)


def test_manifesting_stops_at_canonical_organization_endpoint_resolution():
    result = manifested()
    assert result["status"] == "SUBMISSION_READY"
    assert result["evidence_class"] == "SDK_LOCAL_MANIFEST_HANDOFF"
    handoff = result["handoff"]
    assert handoff["state"] == "FAIL_CLOSED"
    assert handoff["disposition"] == "FAIL_CLOSED"
    assert handoff["evaluation_boundary"] == "SDK_ORGANIZATION_DESTINATION_RESOLUTION"
    assert handoff["destination_resolution_source"] == "CANONICAL_CONNECTOR_CAPABILITY_OVERLAY"
    assert handoff["connector_profile_id"] == "sdk-manifest-ingress"
    assert result["manifest_declared_destination"] is None


def test_manifesting_executes_transports_and_awaits_nothing():
    result = manifested()
    handoff = result["handoff"]
    assert result["execution_performed"] is False
    assert result["manifest_receipt_id"] is None
    assert result["posture_resolution_performed"] is False
    assert handoff["receiver_availability_consulted"] is False
    assert handoff["external_machine_required"] is False


def test_manifesting_observes_nothing_on_the_far_side():
    result = manifested()
    assert result["intr_admission_observed"] is False
    assert result["far_side_transition_observed"] is False
    assert result["organization_receipt_observed"] is False
    assert result["handoff"]["consequence_committed"] is False


def test_the_former_name_still_resolves_to_the_same_function():
    """Existing callers of prepare_external_framework_submission keep working."""
    assert prepare_external_framework_submission is manifest_external_framework_submission
    assert prepare_external_framework_submission(**COMMON) == manifested()


def enclosed_run(**overrides) -> dict:
    fake = {"manifest_receipt_id": "mr-test-1", "intr_security_posture_binding": None,
            "posture_bound_execution": False}
    with patch("stegverse.evaluator_governance_runtime.run_evaluator_governance_manifest",
               return_value=fake), \
         patch("stegverse.sovereign_validation_runtime.replay_sovereign",
               return_value={"ok": True}), \
         patch("stegverse.sovereign_validation_runtime.reconstruct_sovereign",
               return_value={"ok": True}):
        return run_external_framework(**{**COMMON, **overrides})


def test_the_execution_lane_declares_itself_enclosed_and_local():
    result = enclosed_run()
    assert result["lane"] == "SDK_LOCAL_ENCLOSED_VALIDATION"
    assert result["evidence_class"] == "SANDBOX_RUNTIME_OBSERVED"
    assert result["custody_store_is_local"] is True
    assert result["authority_effect"] == "NONE_ENCLOSED_VALIDATION_ONLY"
    assert result["execution_performed"] is True


def test_the_execution_lane_claims_no_canonical_closure():
    """A local replay is evidence about this lane and nothing else."""
    result = enclosed_run()
    assert result["canonical_lifecycle_performed"] is False
    assert result["intr_admission_observed"] is False
    assert result["far_side_transition_observed"] is False
    assert result["organization_receipt_observed"] is False
    assert result["master_records_reconstruction_observed"] is False
    assert result["may_be_promoted_to_canonical_closure"] is False


def test_local_replay_and_reconstruction_are_marked_local_to_this_store():
    both = enclosed_run()
    assert both["replay_is_local_to_this_custody_store"] is True
    assert both["reconstruction_is_local_to_this_custody_store"] is True
    neither = enclosed_run(replay=False, reconstruct=False)
    assert neither["replay_is_local_to_this_custody_store"] is False
    assert neither["reconstruction_is_local_to_this_custody_store"] is False
    assert "replay" not in neither and "reconstruction" not in neither


def test_the_two_lanes_never_report_the_same_evidence_class():
    assert manifested()["evidence_class"] != enclosed_run()["evidence_class"]


def cli(tmp_path: Path, *flags: str) -> dict:
    tmp_path.mkdir(parents=True, exist_ok=True)
    output = tmp_path / "out.json"
    argv = [
        "--input", str(tmp_path / "data.json"),
        "--governance-request", str(tmp_path / "request.json"),
        "--source-framework", "probe_framework",
        "--source-output-id", "probe-output-1",
        "--created-at", "2026-10-02T00:00:00Z",
        "--output", str(output),
        *flags,
    ]
    (tmp_path / "data.json").write_text(json.dumps(COMMON["data"]), encoding="utf-8")
    (tmp_path / "request.json").write_text(json.dumps(governance_request()), encoding="utf-8")
    assert main(argv) == 0
    return json.loads(output.read_text(encoding="utf-8"))


def test_the_cli_default_is_manifesting_with_no_flag_at_all(tmp_path):
    result = cli(tmp_path)
    assert result["status"] == "SUBMISSION_READY"
    assert result["execution_performed"] is False
    assert result["handoff"]["state"] == "FAIL_CLOSED"
    assert result["handoff"]["evaluation_boundary"] == "SDK_ORGANIZATION_DESTINATION_RESOLUTION"


def test_prepare_only_still_produces_exactly_the_default(tmp_path):
    """The flag now selects what already happens; pipelines passing it keep working."""
    default = cli(tmp_path / "a")
    legacy = cli(tmp_path / "b", "--prepare-only")
    assert default == legacy


def test_executing_locally_requires_an_explicit_flag(tmp_path):
    fake = {"manifest_receipt_id": "mr-cli-1", "intr_security_posture_binding": None,
            "posture_bound_execution": False}
    with patch("stegverse.evaluator_governance_runtime.run_evaluator_governance_manifest",
               return_value=fake), \
         patch("stegverse.sovereign_validation_runtime.replay_sovereign", return_value={"ok": True}), \
         patch("stegverse.sovereign_validation_runtime.reconstruct_sovereign", return_value={"ok": True}):
        result = cli(tmp_path, "--execute-enclosed")
    assert result["execution_performed"] is True
    assert result["lane"] == "SDK_LOCAL_ENCLOSED_VALIDATION"


def test_no_custody_store_is_touched_on_the_default_path(tmp_path):
    """Manifesting must not create or read a local custody database."""
    before = set(p.name for p in tmp_path.iterdir()) if tmp_path.exists() else set()
    cli(tmp_path)
    created = set(p.name for p in tmp_path.iterdir()) - before
    assert not any(name.endswith(".db") for name in created), created


def test_the_module_states_which_lane_is_the_sdk_job():
    source = (ROOT / "stegverse" / "external_framework_runner.py").read_text(encoding="utf-8")
    assert "is the SDK's job" in source
    assert "enclosed validation lane" in source
    # The old docstring claimed the SDK executed, replayed and reconstructed.
    assert '"""Build, posture-bind through InTr when requested, execute, replay, reconstruct."""' not in source
