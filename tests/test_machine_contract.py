"""Source discovery and handoff regressions; no authentic receiver is invoked."""
import json
import io
from contextlib import redirect_stdout
import pytest

from datetime import datetime, timedelta, timezone

from stegverse.capability_inventory import hmac_evidence_verifier
from stegverse.machine_contract import sdk_machine_contract, SUBMISSION_TERMINAL_STEPS
from stegverse.manifest_builder import GOVERNANCE_PROFILE_ROUTES, build_manifest
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.external_framework_runner import (
    manifest_external_framework_submission,
    prepare_external_framework_manifest,
)
from stegverse.manifest_execution import execute_manifest
from stegverse.evaluator_console import main
from tests.test_manifest_builder import governance_request
from tests.test_manifest_destination_binding import ORGANIZATION_BOUNDARY
from tests.test_manifest_readiness_gate import ATTEMPT, KEY, KEY_ID, _all_ready


def fixture_fetch(binding):
    assert binding.repository == "StegVerse-Labs/.github"
    assert binding.path == "org-runtime/interlock-intr.json"
    return {"text": json.dumps(ORGANIZATION_BOUNDARY),
            "repository": binding.repository, "path": binding.path,
            "ref": binding.ref, "sha": "source-fixture"}


def readiness(**kwargs):
    """Signed fixture readiness evidence for the framework draft (SDK#368 gate on this path)."""
    draft = prepare_external_framework_manifest(**kwargs)
    return dict(attempt_id=ATTEMPT, evidence_verifier=hmac_evidence_verifier({KEY_ID: KEY}),
                readiness_evidence=_all_ready(draft, at=datetime.now(timezone.utc) - timedelta(seconds=5)))


def test_discovery_preserves_both_routes_and_submission_boundary():
    contract = sdk_machine_contract()
    assert contract["governance_execution_profiles"] == GOVERNANCE_PROFILE_ROUTES
    for profile in contract["machine_readable_instructions"].values():
        assert profile["steps"][-2:] == SUBMISSION_TERMINAL_STEPS
        assert profile["interlock_intr"] == "INTERNAL_POST_SUBMISSION"
    native = contract["machine_readable_instructions"]["EXTERNAL_FRAMEWORK_MANIFEST_CONTINUATION"]
    assert native["native_sdk_requires_llm_adapter"] is False


def test_console_help_and_json_projection():
    output = io.StringIO()
    with redirect_stdout(output), pytest.raises(SystemExit) as stop:
        main(["--help"])
    assert stop.value.code == 0
    for command in sdk_machine_contract()["cli"]:
        assert command in output.getvalue()
    output = io.StringIO()
    with redirect_stdout(output):
        assert main(["machine-contract"]) == 0
    assert json.loads(output.getvalue()) == sdk_machine_contract()


@pytest.mark.parametrize("framework", [False, True])
def test_both_sdk_preparation_paths_preserve_manifest_and_handoff_evidence(framework):
    kwargs = dict(data={"arbitrary": [1, 2]}, source_framework="source-fixture",
                  source_output_id="arbitrary-output", processor_request=governance_request(),
                  created_at="2026-10-05T00:00:00Z")
    manifest = build_manifest(**kwargs)
    if framework:
        prepared = manifest_external_framework_submission(
            **kwargs, **readiness(**kwargs), canonical_source_fetcher=fixture_fetch)
        manifest = prepared["manifest"]
        result = prepared["handoff"]
        assert prepared["execution_performed"] is False
    else:
        result = execute_manifest(manifest, canonical_source_fetcher=fixture_fetch)
    canonical = validate_ingress_manifest(manifest)
    assert result["canonical_manifest_sha256"] == canonical["canonical_manifest_sha256"]
    assert result["route_id"] == manifest["processing"]["route_id"]
    assert result["receiver_contacted"] is False
    assert result["organization_receipt_observed"] is False
    assert result["evidence_class"] == "SDK_LOCAL_MANIFEST_HANDOFF"


def test_framework_does_not_fallback_when_canonical_source_is_unavailable():
    def unavailable(_):
        raise ValueError("source-fixture-unavailable")
    kwargs = dict(data={}, source_framework="fixture", source_output_id="fixture",
                  processor_request=governance_request(), created_at="2026-10-05T00:00:00Z")
    with pytest.raises(ValueError, match="source-fixture-unavailable"):
        manifest_external_framework_submission(
            **kwargs, **readiness(**kwargs), canonical_source_fetcher=unavailable)
