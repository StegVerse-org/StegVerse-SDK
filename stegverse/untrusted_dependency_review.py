"""Inert SDK-side source review of executable dependency/IDE/AI ingress.

This module accepts only declarative metadata. It never resolves packages, opens a
workspace, reads credentials, invokes subprocesses, tests OS isolation, issues an
ALLOW, or constructs authoritative receipts. The checked-out component-011
defensive envelope remains the runtime containment owner.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from .governance_navigation import canonical_sha256
from .manifest_contract import validate_ingress_manifest

SCHEMA = "stegverse.sdk.untrusted-executable-ingress-review.v1"
HEX = re.compile(r"^[0-9a-f]{64}$")
KINDS = {"DEPENDENCY_INSTALL", "BUILD_HOOK", "IDE_WORKSPACE_TASK", "AI_GENERATED_COMMAND"}
TRIGGERS = {"EXPLICIT_REQUEST", "INSTALL_LIFECYCLE", "WORKSPACE_OPEN", "MODEL_SUGGESTION"}
CAPABILITIES = {"PACKAGE_READ", "BOUNDED_FILE_WRITE", "NETWORK_EGRESS", "PROCESS_SPAWN",
                "ENVIRONMENT_READ", "CREDENTIAL_ACCESS", "CONSEQUENTIAL_TOOL"}
DEPENDENCY_FIELDS = {"name", "version", "expected_sha256", "observed_sha256",
                     "declared_hooks", "transitive"}
OPERATION_FIELDS = {"operation_id", "kind", "trigger", "dependency_name",
                    "requested_capabilities", "declared_capabilities"}
TOP_FIELDS = {"schema", "manifest_sha256", "source_revision_sha256",
              "workspace_tree_sha256", "dependencies", "operations", "standing",
              "evidence"}
STANDING_FIELDS = {"policy_current", "warrant_current", "intr_current_at_commit",
                   "worker_fence_current"}
EVIDENCE_FIELDS = {"independent_observer", "enforcement_observed",
                   "predecessor_reconstructed", "master_records_closure"}


def _object(value: Any, fields: set[str], name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(name + " must be an object")
    unknown = set(value) - fields
    if unknown:
        raise ValueError(name + " contains unsupported fields: " + ", ".join(sorted(unknown)))
    return value


def _digest(value: Any, name: str) -> str:
    if not isinstance(value, str) or not HEX.fullmatch(value):
        raise ValueError(name + " must be lowercase sha256")
    return value


def _caps(value: Any, name: str) -> set[str]:
    if not isinstance(value, list) or any(not isinstance(v, str) or v not in CAPABILITIES for v in value):
        raise ValueError(name + " must list known capability names")
    if len(set(value)) != len(value):
        raise ValueError(name + " contains duplicate capability")
    return set(value)


def review_untrusted_executable_ingress(
    manifest: Mapping[str, Any], descriptor: Mapping[str, Any]
) -> dict[str, Any]:
    """Return source-only proposed denials, never executable permission."""
    validate_ingress_manifest(manifest)
    d = _object(descriptor, TOP_FIELDS, "descriptor")
    if d.get("schema") != SCHEMA:
        raise ValueError("descriptor schema mismatch")
    manifest_hash = canonical_sha256(manifest)
    if _digest(d.get("manifest_sha256"), "manifest_sha256") != manifest_hash:
        raise ValueError("exact source manifest mismatch")
    _digest(d.get("source_revision_sha256"), "source_revision_sha256")
    _digest(d.get("workspace_tree_sha256"), "workspace_tree_sha256")

    deps = d.get("dependencies")
    operations = d.get("operations")
    if not isinstance(deps, list) or not isinstance(operations, list) or not operations:
        raise ValueError("dependencies and nonempty operations lists required")
    reasons: list[str] = []
    names: set[str] = set()
    for raw in deps:
        dep = _object(raw, DEPENDENCY_FIELDS, "dependency")
        name = dep.get("name")
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("dependency name must be unique and nonempty")
        names.add(name)
        if not isinstance(dep.get("version"), str) or not dep["version"].strip():
            raise ValueError("dependency version required")
        expected = _digest(dep.get("expected_sha256"), name + ".expected_sha256")
        observed = _digest(dep.get("observed_sha256"), name + ".observed_sha256")
        if expected != observed:
            reasons.append("DEPENDENCY_DIGEST_MISMATCH:" + name)
        hooks = dep.get("declared_hooks")
        if not isinstance(hooks, list) or any(not isinstance(h, str) or not h for h in hooks):
            raise ValueError("declared_hooks must list hook names, never code")
        if hooks:
            reasons.append("EXECUTABLE_INSTALL_HOOK_REQUIRES_DISTINCT_ADMISSION:" + name)
        if not isinstance(dep.get("transitive"), bool):
            raise ValueError("transitive must be boolean")

    seen: set[str] = set()
    for raw in operations:
        op = _object(raw, OPERATION_FIELDS, "operation")
        oid = op.get("operation_id")
        if not isinstance(oid, str) or not oid.strip() or oid in seen:
            raise ValueError("operation_id must be unique and nonempty")
        seen.add(oid)
        kind, trigger = op.get("kind"), op.get("trigger")
        if kind not in KINDS or trigger not in TRIGGERS:
            raise ValueError("unsupported operation kind or trigger")
        dependency = op.get("dependency_name")
        if dependency is not None and dependency not in names:
            raise ValueError("operation references undeclared dependency")
        requested = _caps(op.get("requested_capabilities"), oid + ".requested_capabilities")
        declared = _caps(op.get("declared_capabilities"), oid + ".declared_capabilities")
        if requested - declared:
            reasons.append("OPERATION_REQUESTS_UNDECLARED_CAPABILITY:" + oid)
        if trigger in {"INSTALL_LIFECYCLE", "WORKSPACE_OPEN", "MODEL_SUGGESTION"}:
            reasons.append("AUTOMATIC_EXECUTION_REQUIRES_DISTINCT_ADMISSION:" + oid)
        if kind == "DEPENDENCY_INSTALL" and dependency is None:
            reasons.append("INSTALL_WITHOUT_DECLARED_DEPENDENCY:" + oid)
        if requested & {"CREDENTIAL_ACCESS", "ENVIRONMENT_READ", "NETWORK_EGRESS",
                        "PROCESS_SPAWN", "CONSEQUENTIAL_TOOL"}:
            reasons.append("SENSITIVE_CAPABILITY_REQUIRES_INDEPENDENT_ENFORCEMENT:" + oid)

    standing = _object(d.get("standing"), STANDING_FIELDS, "standing")
    if any(standing.get(key) is not True for key in STANDING_FIELDS):
        reasons.append("CURRENT_STANDING_OR_CLAIM_NOT_ESTABLISHED")
    evidence = _object(d.get("evidence"), EVIDENCE_FIELDS, "evidence")
    if any(evidence.get(key) is not True for key in EVIDENCE_FIELDS):
        reasons.append("CONTAINMENT_OR_CANONICAL_CUSTODY_NOT_ESTABLISHED")

    # Even all-true self-reported descriptor claims are not independent
    # runtime/authority observations. No executable or terminal authorization.
    reasons.append("AUTHENTIC_COMPONENT_011_AND_INTR_RECEIPTS_REQUIRED")
    return {
        "schema": SCHEMA,
        "decision": "NON_AUTHORIZING_LOCAL_REVIEW_ONLY",
        "proposed_denial_reasons": sorted(set(reasons)),
        "candidate_operation_ids": sorted(seen),
        "authentic_containment_proven": False,
        "authentic_intr_admission_proven": False,
        "authentic_master_records_custody_proven": False,
        "authority_effect": "NONE",
    }


__all__ = ["SCHEMA", "review_untrusted_executable_ingress"]
