"""The independent HOLD experiment must keep running, and keep claiming nothing.

The experiment lived only as a script behind a workflow whose path filter named
the script and its own yml. Nothing else. So when the manifest-first change
removed env-based destination binding from the runtime -- deliberately, with
``NoTransportRemainsTest`` asserting the names stay gone -- the experiment kept
importing them and broke at import, and no workflow could see it. Its own
workflow only runs when the script changes, and the change that broke it was in
a module the filter does not name.

The test-suite ratchet runs this directory on every pull request with no path
filter, so exercising the experiment from a test is what makes a module change
that breaks it fail visibly, rather than leaving a script no gate runs.

These assertions are the workflow's own, plus the destination reading that
replaced the environment variables.
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "experiment_sv_hold_independent.py"

_spec = importlib.util.spec_from_file_location("experiment_sv_hold_independent", SCRIPT)
experiment = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(experiment)

def _run() -> dict:
    with tempfile.TemporaryDirectory() as output:
        return experiment.run(output_dir=Path(output), attempt_runtime=False)


def test_the_experiment_imports() -> None:
    """The break this test exists for was an ImportError, not a failed assertion."""
    assert hasattr(experiment, "run")
    assert experiment.EXPERIMENT_ID
    assert len(experiment.CONDITIONS) == 5


def test_the_runtime_exposes_no_environment_destination_binding() -> None:
    """Destination comes from the manifest. If these names ever return, the
    experiment must not reach for them again."""
    from stegverse import manifest_state_transition_runtime as runtime

    assert not hasattr(runtime, "INGRESS_URL_ENV")
    assert not hasattr(runtime, "TRANSPORT_AUTHORIZATION_ENV")
    source = SCRIPT.read_text(encoding="utf-8")
    assert "INGRESS_URL_ENV" not in source
    assert "TRANSPORT_AUTHORIZATION_ENV" not in source


def test_every_condition_source_validates_and_claims_nothing() -> None:
    summary = _run()
    assert len(summary["conditions"]) == 5
    assert summary["other_framework_evidence_consumed"] is False
    assert summary["live_execution_claim"] is False
    assert summary["master_records_closure_claim"] is False
    for row in summary["conditions"]:
        assert row["source_validation"] == "PASS", row
        assert row["runtime_disposition"] == "NOT_ATTEMPTED", row
        assert row["actual_effect_observed"] is False, row
        assert row["master_records_reconstruction_observed"] is False, row


def test_source_qualification_does_not_invent_an_organization_destination() -> None:
    """Requester completion metadata is not canonical organization routing.
    Source qualification therefore records no outbound destination and performs
    no runtime attempt while the connector capability lacks a concrete .github
    ingress endpoint."""
    summary = _run()
    for row in summary["conditions"]:
        assert "declared_destination" not in row
        assert row["runtime_disposition"] == "NOT_ATTEMPTED"


def test_a_prepared_handoff_carries_no_authority() -> None:
    summary = _run()
    for row in summary["conditions"]:
        if "handoff_authority_effect" in row:
            assert row["handoff_authority_effect"].startswith("NONE"), row


def test_each_condition_binds_its_own_manifest_and_request() -> None:
    summary = _run()
    manifests = [row["canonical_manifest_sha256"] for row in summary["conditions"]]
    requests = [row["derived_request_sha256"] for row in summary["conditions"]]
    assert len(set(manifests)) == len(manifests), "two conditions share a manifest digest"
    assert len(set(requests)) == len(requests), "two conditions share a request digest"


def test_skipping_the_runtime_attempt_leaves_every_condition_unattempted() -> None:
    with tempfile.TemporaryDirectory() as output:
        summary = experiment.run(output_dir=Path(output), attempt_runtime=False)
    for row in summary["conditions"]:
        assert row["runtime_disposition"] == "NOT_ATTEMPTED", row
        assert row["source_validation"] == "PASS", row


def test_the_experiment_writes_its_evidence() -> None:
    with tempfile.TemporaryDirectory() as output:
        experiment.run(output_dir=Path(output), attempt_runtime=False)
        written = {p.name for p in Path(output).glob("*.json")}
    assert "summary.json" in written
    for step, *_ in experiment.CONDITIONS:
        assert f"{step}-input.json" in written
        assert f"{step}-manifest.json" in written
        assert f"{step}-derived-request.json" in written
