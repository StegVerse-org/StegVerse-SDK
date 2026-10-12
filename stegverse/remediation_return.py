"""Validate manifest-bound remediation lineage at the SDK return boundary.

This is a fail-closed evidence validator, not a governance decision or ledger
reader. Runtime authenticity must be established by the receiving Interlock.
"""
from __future__ import annotations

from typing import Any, Mapping

SCHEMA = "stegverse.sdk.remediation-return-validation/v1"


def validate_remediation_return(proposal: Mapping[str, Any], request: Mapping[str, Any],
                                result: Mapping[str, Any], evaluator: Mapping[str, Any]) -> dict[str, Any]:
    if proposal.get("schema") != "stegverse.remediation.manifest-transition-proposal/v1":
        raise ValueError("REMEDIATION_PROPOSAL_SCHEMA_REQUIRED")
    binding = proposal.get("manifest_transition")
    if not isinstance(binding, Mapping) or binding.get("authority_effect") != "NONE_BINDING_ONLY":
        raise ValueError("MANIFEST_SELECTED_BINDING_REQUIRED")
    if proposal.get("approval_result") != "NOT_EVALUATED":
        raise ValueError("PROPOSAL_MUST_NOT_PREAPPROVE")
    if request.get("canonical_manifest_sha256") != binding.get("canonical_manifest_sha256"):
        raise ValueError("REMEDIATION_MANIFEST_HASH_MISMATCH")
    for key in ("route_id", "processing_capability"):
        if request.get(key) != binding.get(key):
            raise ValueError(f"REMEDIATION_MANIFEST_ROUTE_MISMATCH:{key}")
    if result.get("canonical_manifest_sha256") != request.get("canonical_manifest_sha256"):
        raise ValueError("REMEDIATION_RESULT_MANIFEST_MISMATCH")
    if result.get("route_id") != request.get("route_id"):
        raise ValueError("REMEDIATION_RESULT_ROUTE_MISMATCH")
    if result.get("disposition") not in {"ALLOW", "DENY", "FAIL_CLOSED"}:
        raise ValueError("REMEDIATION_GOVERNANCE_DISPOSITION_REQUIRED")
    if not isinstance(evaluator, Mapping) or not evaluator.get("request_id"):
        raise ValueError("ORIGINATING_EVALUATOR_ID_REQUIRED")
    if result.get("originating_evaluator_request_id") != evaluator["request_id"]:
        raise ValueError("ORIGINATING_EVALUATOR_RETURN_BINDING_MISMATCH")
    chain = result.get("authoritative_receipt_chain")
    if not isinstance(chain, list) or not chain:
        raise ValueError("AUTHORITATIVE_RECEIPT_CHAIN_REQUIRED")
    previous = None
    for index, receipt in enumerate(chain):
        if not isinstance(receipt, Mapping) or not receipt.get("receipt_sha256"):
            raise ValueError("AUTHORITATIVE_RECEIPT_REQUIRED")
        if index and receipt.get("predecessor_receipt_sha256") != previous:
            raise ValueError("AUTHORITATIVE_RECEIPT_PREDECESSOR_MISMATCH")
        previous = receipt["receipt_sha256"]
    if result.get("independent_organization_ledger_readback_verified") is not True:
        raise ValueError("INDEPENDENT_ORGANIZATION_LEDGER_READBACK_REQUIRED")
    if result.get("originating_evaluator_return_acknowledged") is not True:
        raise ValueError("ORIGINATING_EVALUATOR_ACKNOWLEDGEMENT_REQUIRED")
    return {"schema": SCHEMA, "disposition": result["disposition"],
            "originating_evaluator_request_id": evaluator["request_id"],
            "receipt_chain_length": len(chain),
            "terminal_receipt_sha256": previous,
            "evidence_validated_structurally": True,
            "independent_attestation_performed_by_sdk": False,
            "authority_effect": "NONE_VALIDATION_ONLY"}
