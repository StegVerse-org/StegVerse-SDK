"""Read-only Stage-1 reconciliation of supplied existing organization transition receipts.

The authoritative organization ledger and Master Records must be queried by their
existing resident owner. This function has no network, local ledger, credential,
execution, or custody access and NEVER authenticates caller-supplied snapshots.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .micro_node_commit_time_experiment import _hash
from .stage1_capability_discovery import review_stage1_capabilities

CANONICAL = "stegverse.canonical-state-transition-receipt/v1"
ORGANIZATION = "stegverse.organization-transition-receipt/v1"
RICHARD = "SDK-TT-RICHARD-SEAM-AUTHENTIC-RUNTIME-001"
EXPECTED = (
    "WORKERCOORDINATOR_CLAIM_FENCE_BOUND",
    "TV_TVC_WARRANT_POLICY_VERIFIED",
    "ACTIVATE_TASK_AND_CREATE_BIND_WORKER",
    "TASK_BOUND_WORKER_TASK_COMPLETED",
    "CLOSE_TASK_AND_RETIRE_WORKER",
)
SCHEMA = "stegverse.sdk.stage1-org-receipt-review.v1"


def _uri(value: Any) -> str:
    return "sha256:" + _hash(value)


def review_stage1_org_receipt_snapshots(
    manifest: Mapping[str, Any],
    group_result: Mapping[str, Any],
    evidence: Mapping[str, Any],
    descriptor: Mapping[str, Any],
    *,
    receipt_pairs: Sequence[Mapping[str, Any]],
    previous_org_receipt_sha256: str | None = None,
) -> dict[str, Any]:
    """Inspect a supplied bounded window; no snapshot is authoritative proof."""
    stage = review_stage1_capabilities(manifest, group_result, evidence, descriptor)
    if not isinstance(receipt_pairs, (list, tuple)):
        raise ValueError("receipt_pairs must be an ordered list")
    if previous_org_receipt_sha256 is not None and (
        not isinstance(previous_org_receipt_sha256, str)
        or len(previous_org_receipt_sha256) != 71
        or not previous_org_receipt_sha256.startswith("sha256:")
    ):
        raise ValueError("invalid previous organization receipt pointer")
    # No synthetic stand-in for the authoritative resident organization stream.
    if not receipt_pairs:
        return {
            "schema": SCHEMA, "task_id": RICHARD,
            "stage1_descriptor_sha256": stage["descriptor_sha256"],
            "first_structurally_retained_failure": None,
            "first_unresolved_transition": EXPECTED[0],
            "observed_structural_transitions": [],
            "findings": ["NO_AUTHENTIC_ORGANIZATION_RECEIPTS_SUPPLIED"],
            "decision": "UNKNOWN_NOT_AUTHENTICALLY_OBSERVED",
            "authentic_runtime_proven": False,
            "records_only_reconstruction_proven": False,
            "external_participation_proven": False,
            "authority_effect": "NONE",
        }
    findings: list[str] = []
    transitions: list[str] = []
    first_failure: dict[str, str] | None = None
    prev = previous_org_receipt_sha256
    expected_index = 0
    unrelated_org_receipts = 0
    for index, pair in enumerate(receipt_pairs):
        if not isinstance(pair, Mapping):
            raise ValueError("receipt pair must be an object")
        # The organization ledger is GLOBAL. A task-filtered sequence is
        # not enough to prove immediate predecessor continuity if other
        # tasks interleave. Accept and verify the intervening source+org
        # receipt pairs rather than inventing a contiguous per-task ledger.
        source = pair.get("source_receipt", pair.get("canonical"))
        org = pair.get("organization")
        if not isinstance(source, Mapping) or not isinstance(org, Mapping):
            findings.append("RECEIPT_PAIR_MISSING")
            break
        kind = source.get("schema")
        transition = source.get("transition_id")
        task = source.get("subject_or_correlation_id")
        if kind == CANONICAL:
            source_digest = _uri(source)
            repo_digest = None
        elif kind == "stegverse.repo-transition-receipt/v1":
            # The existing organization aggregator uses a body hash for
            # repository receipt sources, not the canonical receipt hash.
            body = dict(source)
            declared = body.pop("receipt_sha256", None)
            source_digest = _uri(body)
            if (declared != source_digest or
                    not str(source.get("repository", "")).startswith("StegVerse-Labs/")):
                findings.append("INTERVENING_REPO_SOURCE_INVALID")
                break
            repo_digest = declared
            task = None
        else:
            findings.append("SOURCE_RECEIPT_SCHEMA_MISMATCH")
            break
        if (not isinstance(transition, str) or not transition
                or org.get("schema") != ORGANIZATION
                or org.get("organization") != "StegVerse-Labs"
                or org.get("source_receipt_schema") != kind
                or org.get("source_transition_sha256") != source_digest
                or org.get("source_transition_id") != transition
                or org.get("canonical_state_transition_receipt_sha256") != (
                    source_digest if kind == CANONICAL else None
                )
                or org.get("repo_receipt_sha256") != repo_digest
                or org.get("subject_or_correlation_id") != task):
            findings.append("CANONICAL_TO_ORGANIZATION_BINDING_INVALID")
            break
        org_body = dict(org)
        claimed_hash = org_body.pop("receipt_sha256", None)
        if claimed_hash != _uri(org_body):
            findings.append("ORGANIZATION_RECEIPT_DIGEST_MISMATCH")
            break
        if org.get("previous_receipt_sha256") != prev:
            findings.append("ORGANIZATION_IMMEDIATE_PREDECESSOR_MISMATCH")
            break
        prev = claimed_hash
        if kind != CANONICAL or task != RICHARD:
            unrelated_org_receipts += 1
            continue
        if expected_index >= len(EXPECTED) or transition != EXPECTED[expected_index]:
            findings.append("TRANSITION_ORDER_OR_ID_MISMATCH")
            break
        transitions.append(transition)
        expected_index += 1
        outcome = source.get("transition_outcome")
        if outcome in {"FAILED", "FAIL_CLOSED"}:
            first_failure = {
                "transition_id": transition,
                "transition_outcome": outcome,
                "canonical_receipt_sha256": source_digest,
                "organization_receipt_sha256": claimed_hash,
            }
            findings.append("STRUCTURALLY_RETAINED_FAILURE_REQUIRES_AUTHENTIC_SOURCE_READBACK")
            break
        if outcome not in {"ALLOW", "EXECUTED", "COMPLETED", "OBSERVED", "NO_CHANGE"}:
            findings.append("UNRECOGNIZED_OR_NONADVANCING_TRANSITION_OUTCOME")
            break
        # Source pairs alone do not verify warrant, admission, independent
        # origin, authentic Master Records closure or worker-absent replay.
    if not first_failure and expected_index < len(EXPECTED):
        findings.append("NEXT_TRANSITION_NOT_EVIDENCED")
    if expected_index == len(EXPECTED) and first_failure is None:
        findings.append("SOURCE_RECEIPTS_DO_NOT_PROVE_MASTER_RECORDS_OR_EXTERNAL_REALITY")
    return {
        "schema": SCHEMA, "task_id": RICHARD,
        "stage1_descriptor_sha256": stage["descriptor_sha256"],
        "first_structurally_retained_failure": first_failure,
        "first_unresolved_transition": EXPECTED[expected_index] if expected_index < len(EXPECTED) else None,
        "observed_structural_transitions": transitions,
        "verified_intervening_org_receipt_copies": unrelated_org_receipts,
        "findings": sorted(set(findings)),
        "decision": "NON_AUTHORIZING_SNAPSHOT_REVIEW_ONLY",
        "authentic_runtime_proven": False,
        "records_only_reconstruction_proven": False,
        "external_participation_proven": False,
        "authority_effect": "NONE",
    }
