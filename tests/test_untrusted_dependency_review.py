"""Inert security descriptors only; NO installation, shell, network or secret reads."""
from copy import deepcopy

import pytest

from stegverse.governance_navigation import canonical_sha256
from stegverse.manifest_builder import build_manifest
from stegverse.untrusted_dependency_review import SCHEMA, review_untrusted_executable_ingress


def fixture():
    candidate = {"actor_class": "external_framework", "action": "review_only",
                 "target": "synthetic-package", "scope": "inert-test",
                 "parameters": {"external_side_effect": False}}
    request = {
        "candidate": candidate, "judgment": {}, "signal": {}, "execution": {},
        "capability": {}, "continuity": {}, "approval": {}, "permission_present": False,
    }
    manifest = build_manifest(
        data={"synthetic": True}, source_framework="LOCAL_FIXTURE_ONLY",
        source_output_id="dependency-review-001", processor_request=request,
        created_at="2026-09-23T00:00:00Z",
    )
    d = {
        "schema": SCHEMA, "manifest_sha256": canonical_sha256(manifest),
        "source_revision_sha256": "a" * 64, "workspace_tree_sha256": "b" * 64,
        "dependencies": [
            {"name": "synthetic-lib", "version": "1.0", "expected_sha256": "c" * 64,
             "observed_sha256": "c" * 64, "declared_hooks": [], "transitive": False},
        ],
        "operations": [
            {"operation_id": "install-one", "kind": "DEPENDENCY_INSTALL",
             "trigger": "EXPLICIT_REQUEST", "dependency_name": "synthetic-lib",
             "requested_capabilities": ["PACKAGE_READ"],
             "declared_capabilities": ["PACKAGE_READ"]},
        ],
        "standing": {"policy_current": True, "warrant_current": True,
                     "intr_current_at_commit": True, "worker_fence_current": True},
        "evidence": {"independent_observer": True, "enforcement_observed": True,
                     "predecessor_reconstructed": True, "master_records_closure": True},
    }
    return manifest, d


def review(mutator=None):
    manifest, descriptor = fixture()
    if mutator:
        mutator(descriptor)
    return review_untrusted_executable_ingress(manifest, descriptor)


def test_bounded_pinned_package_still_never_grants_execution():
    result = review()
    assert result["decision"] == "NON_AUTHORIZING_LOCAL_REVIEW_ONLY"
    assert result["proposed_denial_reasons"] == ["AUTHENTIC_COMPONENT_011_AND_INTR_RECEIPTS_REQUIRED"]
    assert result["authentic_containment_proven"] is False
    assert result["authentic_intr_admission_proven"] is False
    assert result["authentic_master_records_custody_proven"] is False
    assert result["authority_effect"] == "NONE"


def test_substituted_transitive_dependency_detected_before_execution():
    def mutate(d):
        row = deepcopy(d["dependencies"][0])
        row.update(name="synthetic-transitive", transitive=True, observed_sha256="d" * 64)
        d["dependencies"].append(row)
    result = review(mutate)
    assert "DEPENDENCY_DIGEST_MISMATCH:synthetic-transitive" in result["proposed_denial_reasons"]


def test_install_hook_with_out_of_scope_write_and_secret_read():
    def mutate(d):
        d["dependencies"][0]["declared_hooks"] = ["postinstall"]
        d["operations"][0].update(
            kind="BUILD_HOOK", trigger="INSTALL_LIFECYCLE",
            requested_capabilities=["BOUNDED_FILE_WRITE", "ENVIRONMENT_READ"],
            declared_capabilities=["BOUNDED_FILE_WRITE"],
        )
    reasons = review(mutate)["proposed_denial_reasons"]
    assert "EXECUTABLE_INSTALL_HOOK_REQUIRES_DISTINCT_ADMISSION:synthetic-lib" in reasons
    assert "OPERATION_REQUESTS_UNDECLARED_CAPABILITY:install-one" in reasons
    assert "SENSITIVE_CAPABILITY_REQUIRES_INDEPENDENT_ENFORCEMENT:install-one" in reasons


def test_workspace_open_cannot_grant_automatic_shell():
    def mutate(d):
        d["operations"][0].update(
            kind="IDE_WORKSPACE_TASK", trigger="WORKSPACE_OPEN", dependency_name=None,
            requested_capabilities=["PROCESS_SPAWN"], declared_capabilities=["PROCESS_SPAWN"])
    reasons = review(mutate)["proposed_denial_reasons"]
    assert "AUTOMATIC_EXECUTION_REQUIRES_DISTINCT_ADMISSION:install-one" in reasons
    assert "SENSITIVE_CAPABILITY_REQUIRES_INDEPENDENT_ENFORCEMENT:install-one" in reasons


def test_ai_generated_command_network_and_tool_requests():
    def mutate(d):
        d["operations"][0].update(
            kind="AI_GENERATED_COMMAND", trigger="MODEL_SUGGESTION", dependency_name=None,
            requested_capabilities=["NETWORK_EGRESS", "CONSEQUENTIAL_TOOL"],
            declared_capabilities=[],
        )
    reasons = review(mutate)["proposed_denial_reasons"]
    assert "OPERATION_REQUESTS_UNDECLARED_CAPABILITY:install-one" in reasons
    assert "AUTOMATIC_EXECUTION_REQUIRES_DISTINCT_ADMISSION:install-one" in reasons


def test_stale_policy_and_fence_fail_closed():
    def mutate(d):
        d["standing"]["policy_current"] = False
        d["standing"]["worker_fence_current"] = False
    assert "CURRENT_STANDING_OR_CLAIM_NOT_ESTABLISHED" in review(mutate)["proposed_denial_reasons"]


def test_missing_predecessor_or_independent_enforcement_unproven():
    def mutate(d):
        d["evidence"]["independent_observer"] = False
        d["evidence"]["predecessor_reconstructed"] = False
    assert "CONTAINMENT_OR_CANONICAL_CUSTODY_NOT_ESTABLISHED" in review(mutate)["proposed_denial_reasons"]


def test_claimed_all_true_proof_still_not_authentic_runtime_proof():
    assert review()["authentic_master_records_custody_proven"] is False


@pytest.mark.parametrize("field", ["manifest_sha256", "source_revision_sha256", "workspace_tree_sha256"])
def test_identity_mismatch_or_invalid_digest_rejected(field):
    m, d = fixture()
    d[field] = "d" * 64 if field == "manifest_sha256" else "not-sha256"
    with pytest.raises(ValueError):
        review_untrusted_executable_ingress(m, d)


def test_duplicate_operation_and_dependency_rejected():
    m, d = fixture()
    d["operations"].append(deepcopy(d["operations"][0]))
    with pytest.raises(ValueError, match="operation_id"):
        review_untrusted_executable_ingress(m, d)
    d["operations"].pop()
    d["dependencies"].append(deepcopy(d["dependencies"][0]))
    with pytest.raises(ValueError, match="dependency name"):
        review_untrusted_executable_ingress(m, d)


def test_descriptor_rejects_executable_payload_instead_of_evaluating_it():
    m, d = fixture()
    d["operations"][0]["script"] = "NEVER_EXECUTE"
    with pytest.raises(ValueError, match="unsupported fields"):
        review_untrusted_executable_ingress(m, d)


def test_expired_fence_not_authorized_by_records_only_claim():
    def mutate(d):
        d["standing"]["worker_fence_current"] = False
        d["evidence"]["master_records_closure"] = True
    result = review(mutate)
    assert "CURRENT_STANDING_OR_CLAIM_NOT_ESTABLISHED" in result["proposed_denial_reasons"]
    assert result["decision"] != "ALLOW"
