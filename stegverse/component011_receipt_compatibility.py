"""Source-only compatibility inspection of existing component-011 receipt snapshots.

Never issues execution authority, performs runtime I/O, mutates custody, or
converts caller-supplied objects into independently verified observations.
Actual WorkerCoordinator, TV/TVC, InTr and Master Records readback must be
obtained through their existing authorized production surfaces.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

SCHEMA = "stegverse.sdk.component011-custody-compatibility/v1"
SOURCE_TASK = "ECOSYSTEM-INGRESS-AI-BOUNDARIES-001"
COMPONENT = "RTC-NONCHATGPT-AI-DECISION-SANDBOX-011"
BOUNDARY_SCHEMA = "stegverse.ungoverned-ai-defensive-envelope-resident-boundary/v1"
CONSUMPTION_SCHEMA = "stegverse.ungoverned-ai-defensive-envelope-request-consumption/v1"
CANONICAL_SCHEMA = "stegverse.canonical-state-transition-receipt/v1"
ORG_SCHEMA = "stegverse.organization-transition-receipt/v1"
REQUIRED_PROBES = frozenset({"FILESYSTEM_OPEN", "NETWORK_IMPORT", "ENVIRONMENT_IMPORT"})
UNTESTED_EFFECTS = ("PACKAGE_INSTALL_HOOK_OS_CONTAINMENT", "IDE_WORKSPACE_SHELL_CONTAINMENT",
                    "TRANSITIVE_PACKAGE_FETCH_CONTROL", "UNTRUSTED_NATIVE_CODE_CONTAINMENT")


def _hash(value: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def _object(raw: Any, label: str) -> Mapping[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, Mapping):
        raise ValueError(label + " must be an object if present")
    return raw


def reconcile_component011_snapshots(
    *,
    consumption: Mapping[str, Any] | None = None,
    boundary: Mapping[str, Any] | None = None,
    canonical_transition: Mapping[str, Any] | None = None,
    organization: Mapping[str, Any] | None = None,
    master_records: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Inspect copies; result can only describe claimed/structural evidence."""
    consumption = _object(consumption, "consumption")
    boundary = _object(boundary, "boundary")
    canonical_transition = _object(canonical_transition, "canonical_transition")
    organization = _object(organization, "organization")
    master_records = _object(master_records, "master_records")
    findings: list[str] = []
    structural: dict[str, bool] = {}

    if consumption is None:
        findings.append("AUTHENTIC_REQUEST_CONSUMPTION_RECEIPT_MISSING")
    else:
        structural["consumption_shape"] = (
            consumption.get("schema") == CONSUMPTION_SCHEMA
            and consumption.get("task_id") == SOURCE_TASK
            and consumption.get("terminal") is True
            and consumption.get("bridge_contract_valid") is True
            and consumption.get("runtime_execution_attempted") is True
        )
        if not structural["consumption_shape"]:
            findings.append("REQUEST_CONSUMPTION_NOT_TERMINALLY_BOUND")

    if boundary is None:
        findings.append("AUTHENTIC_COMPONENT011_BOUNDARY_RECEIPT_MISSING")
    else:
        claim = boundary.get("claim") if isinstance(boundary.get("claim"), Mapping) else {}
        probe = boundary.get("probe") if isinstance(boundary.get("probe"), Mapping) else {}
        declared = boundary.get("checks") if isinstance(boundary.get("checks"), Mapping) else {}
        denied = probe.get("denied_interactions")
        denial_valid = (
            isinstance(denied, list)
            and REQUIRED_PROBES.issubset({
                row.get("probe_id") for row in denied if isinstance(row, Mapping)
            })
            and all(
                isinstance(row, Mapping)
                and row.get("decision") == "DENY"
                and row.get("consumed") is False
                and row.get("consequence_reachable") is False
                for row in denied
            )
        )
        structural["boundary_shape"] = (
            boundary.get("schema") == BOUNDARY_SCHEMA
            and boundary.get("task_id") == SOURCE_TASK
            and boundary.get("component_id") == COMPONENT
            and boundary.get("state") == "REPRESENTATIVE_BOUNDARY_PROBE_OBSERVED"
            and isinstance(claim.get("claim_id"), str)
            and bool(claim.get("claim_id"))
            and isinstance(claim.get("fencing_token"), int)
            and not isinstance(claim.get("fencing_token"), bool)
            and claim.get("fencing_token") >= 1
            and isinstance(boundary.get("tvc_source_head"), str)
            and bool(boundary.get("tvc_source_head"))
            and boundary.get("external_provider_observed") is False
            and denial_valid
            and all(declared.get(name) is True for name in (
                "allow_consumed", "allow_result", "filesystem_not_exposed",
                "network_not_exposed", "temporary_state_destroyed",
                "deny_not_consumed", "deny_consequence_unreachable",
                "ambient_credentials_not_exposed", "egress_evidence_only",
            ))
        )
        if not structural["boundary_shape"]:
            findings.append("BOUNDARY_DENIAL_OR_CLAIM_NOT_STRUCTURALLY_PROVEN")
        # Existing consumption record embeds the worker return, not the
        # boundary receipt/hash. Never infer binding from matching task IDs.
        if consumption is not None:
            findings.append("CONSUMPTION_TO_BOUNDARY_RECEIPT_EXACT_BINDING_NOT_PROVEN")

    transition_hash = None
    if canonical_transition is None:
        findings.append("CANONICAL_TRANSITION_RECEIPT_MISSING")
    else:
        structural["canonical_transition_shape"] = (
            canonical_transition.get("schema") == CANONICAL_SCHEMA
            and canonical_transition.get("subject_or_correlation_id") == SOURCE_TASK
            and isinstance(canonical_transition.get("transition_id"), str)
            and bool(canonical_transition.get("transition_id"))
        )
        transition_hash = _hash(canonical_transition)
        if not structural["canonical_transition_shape"]:
            findings.append("CANONICAL_TRANSITION_RECEIPT_MISMATCH")
        if boundary is not None:
            # The authoritative transition must independently refer to the
            # exact boundary receipt digest, not merely the same task ID.
            ev = canonical_transition.get("transition_evidence")
            expected = "sha256:" + hashlib.sha256(
                json.dumps(boundary, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
            ).hexdigest()
            structural["transition_to_boundary"] = (
                isinstance(ev, Mapping)
                and ev.get("component011_boundary_receipt_sha256") == expected
            )
            if not structural["transition_to_boundary"]:
                findings.append("BOUNDARY_TO_CANONICAL_TRANSITION_EXACT_LINK_MISSING")

    if organization is None:
        findings.append("AUTHENTIC_ORGANIZATION_LEDGER_RECEIPT_MISSING")
    else:
        structural["organization_shape"] = (
            organization.get("schema") == ORG_SCHEMA
            and organization.get("organization") == "StegVerse-Labs"
            and canonical_transition is not None
            and organization.get("source_receipt_schema") == CANONICAL_SCHEMA
            and organization.get("source_transition_sha256") == transition_hash
            and organization.get("canonical_state_transition_receipt_sha256") == transition_hash
            and isinstance(organization.get("receipt_sha256"), str)
            and bool(organization.get("receipt_sha256"))
        )
        if not structural["organization_shape"]:
            findings.append("ORGANIZATION_SOURCE_TRANSITION_EXACT_LINK_MISSING")

    if master_records is None:
        findings.append("CANONICAL_MASTER_RECORDS_READBACK_MISSING")
    else:
        org_hash = organization.get("receipt_sha256") if organization else None
        structural["master_records_claim_shape"] = (
            master_records.get("state") == "RECORDED"
            and master_records.get("reconstruction_status") == "PASS"
            and master_records.get("required_evidence_validation_status") == "PASS"
            and isinstance(master_records.get("receipt_sha256"), str)
            and master_records.get("receipt_sha256") == master_records.get("reconstructed_receipt_sha256")
            and org_hash is not None
            and master_records.get("organization_receipt_sha256") == org_hash
        )
        if not structural["master_records_claim_shape"]:
            findings.append("MASTER_RECORDS_CLOSURE_OR_ORG_BINDING_MISSING")

    findings.append("AUTHENTIC_AUTHORITY_AND_CUSTODY_INDEPENDENT_READBACK_REQUIRED")
    return {
        "schema": SCHEMA,
        "decision": "NON_AUTHORIZING_SOURCE_RECONCILIATION_ONLY",
        "structural_checks": structural,
        "missing_or_unproven": sorted(set(findings)),
        "boundary_probe_scope": sorted(REQUIRED_PROBES),
        "not_proven_effects": list(UNTESTED_EFFECTS),
        "authentic_runtime_proven": False,
        "organization_custody_proven": False,
        "master_records_reconstructed": False,
        "authority_effect": "NONE",
    }


__all__ = ["SCHEMA", "reconcile_component011_snapshots"]
