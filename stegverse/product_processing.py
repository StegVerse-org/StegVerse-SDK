"""Non-authorizing per-product provenance for composed SDK results.

This module projects already-observed SDK/runtime facts into a common product
processing envelope. It does not run products, decide admissibility, grant
authority, mint receipts, or infer unobserved transitions.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

PRODUCT_PROCESSING_SCHEMA = "stegverse.sdk.product-processing.v1"
ADMITTEDCODE_PROCESSING_SCHEMA = "stegverse.sdk.product-processing.admittedcode.v1"


def canonical_sha256(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest()


def _contribution(
    *,
    contribution_id: str,
    product_id: str,
    product_role: str,
    processing_status: str,
    processing_scope: list[str],
    input_bindings: Mapping[str, Any] | None = None,
    output_bindings: Mapping[str, Any] | None = None,
    evidence_refs: list[str] | None = None,
    authority_effect: str = "NONE",
    provenance_basis: str = "SDK_OBSERVED",
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "contribution_id": contribution_id,
        "product_id": product_id,
        "product_role": product_role,
        "processing_status": processing_status,
        "processing_scope": list(processing_scope),
        "input_bindings": dict(input_bindings or {}),
        "output_bindings": dict(output_bindings or {}),
        "evidence_refs": list(evidence_refs or []),
        "authority_effect": authority_effect,
        "provenance_basis": provenance_basis,
    }
    if details:
        value["details"] = dict(details)
    value["contribution_sha256"] = canonical_sha256(value)
    return value


def _source_product_contribution(normalized_request: Mapping[str, Any]) -> dict[str, Any] | None:
    input_block = normalized_request.get("input")
    if not isinstance(input_block, Mapping):
        return None
    identity = input_block.get("ingress_manifest_identity")
    if not isinstance(identity, Mapping):
        input_data = input_block.get("input_data")
        if isinstance(input_data, Mapping):
            identity = input_data.get("ingress_manifest_identity")
    if not isinstance(identity, Mapping):
        return None
    source_framework = identity.get("source_framework")
    if not isinstance(source_framework, str) or not source_framework.strip():
        return None
    product_id = source_framework.strip()
    product_key = product_id.lower().replace("_", "-")
    return _contribution(
        contribution_id=f"upstream-source:{product_key}",
        product_id=product_id,
        product_role="upstream_submission_product",
        processing_status="DECLARED_UPSTREAM_PROVENANCE",
        processing_scope=["source-native processing before SDK ingress"],
        input_bindings={},
        output_bindings={
            "canonical_manifest_sha256": identity.get("canonical_manifest_sha256"),
            "source_output_id": identity.get("source_output_id"),
        },
        authority_effect="NONE",
        provenance_basis="CALLER_MANIFEST_IDENTITY",
        details={
            "independently_verified_by_sdk": False,
            "sdk_infers_upstream_internal_processing": False,
        },
    )


def build_product_processing(
    *,
    normalized_request: Mapping[str, Any],
    runtime_result: Mapping[str, Any],
    evaluation: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build the generic envelope plus the typed AdmittedCode projection.

    Every assertion is derived from the already-produced SDK/runtime result.
    Unobserved Interlock/InTr and StegAgents processing is represented explicitly
    rather than inferred from route or execution labels.
    """
    evaluation = dict(evaluation or {})
    contributions: list[dict[str, Any]] = []

    source = _source_product_contribution(normalized_request)
    if source is not None:
        contributions.append(source)

    request_hash = runtime_result.get("submitted_manifest_hash")
    governance_hash = runtime_result.get("governance_request_hash")
    manifest_receipt_id = runtime_result.get("manifest_receipt_id")
    route_receipt_ids = list(runtime_result.get("route_receipt_ids") or [])
    disposition = runtime_result.get("governance_state")

    sdk = _contribution(
        contribution_id="sdk:return-composition",
        product_id="StegVerse-SDK",
        product_role="manifestation_route_binding_and_result_composition",
        processing_status="PROCESSED",
        processing_scope=[
            "request normalization",
            "declared route binding",
            "product provenance composition",
            "SDK return composition",
        ],
        input_bindings={
            "submitted_manifest_hash": request_hash,
            "governance_request_hash": governance_hash,
        },
        output_bindings={
            "transaction_id": runtime_result.get("transaction_id"),
            "route_manifest_id": runtime_result.get("route_manifest_id"),
        },
        evidence_refs=[str(x) for x in route_receipt_ids],
        authority_effect="NONE",
    )
    contributions.append(sdk)

    core_lite = _contribution(
        contribution_id="core-lite:manifested-route",
        product_id="Core-Lite",
        product_role="manifested_route_carrier",
        processing_status="PROCESSED" if runtime_result.get("route_manifest_id") else "NOT_OBSERVED",
        processing_scope=["manifested route carriage"],
        input_bindings={
            "declared_route_id": runtime_result.get("declared_route_id"),
            "route_declaration_hash": runtime_result.get("route_declaration_hash"),
        },
        output_bindings={
            "route_manifest_id": runtime_result.get("route_manifest_id"),
            "route_receipt_chain_head": runtime_result.get("route_receipt_chain_head"),
        },
        evidence_refs=[str(x) for x in route_receipt_ids],
        authority_effect="NONE",
    )
    contributions.append(core_lite)

    reason_codes = evaluation.get("reason_codes")
    if not isinstance(reason_codes, list):
        reason_codes = []
    admitted = _contribution(
        contribution_id="admittedcode:canonical-admission",
        product_id="AdmittedCode",
        product_role="admission_and_evidence",
        processing_status="PROCESSED" if disposition else "NOT_OBSERVED",
        processing_scope=["canonical governance/admissibility evaluation"],
        input_bindings={
            "governance_request_hash": governance_hash,
            "state_binding_hash": runtime_result.get("state_binding_hash"),
        },
        output_bindings={
            "disposition": disposition,
            "reason_codes": reason_codes,
            "reason": evaluation.get("reason"),
        },
        evidence_refs=[str(manifest_receipt_id)] if manifest_receipt_id else [],
        authority_effect="ADMISSION_DECISION_ONLY",
        details={
            "admission_is_execution": False,
            "canonical_runtime_identity": "stegverse:steggate:canonical:three-layer:v1",
            "canonical_evaluator": "stegcore.three_layer.evaluate_three_layer",
        },
    )
    contributions.append(admitted)

    stegcore = _contribution(
        contribution_id="stegcore:canonical-transaction",
        product_id="StegCore",
        product_role="canonical_governance_transaction_implementation",
        processing_status="PROCESSED" if manifest_receipt_id else "NOT_OBSERVED",
        processing_scope=[
            "canonical governance transaction lifecycle",
            "StegGate result binding",
            "commit-coherence bounded consequence gate",
        ],
        input_bindings={"governance_request_hash": governance_hash},
        output_bindings={
            "manifest_receipt_id": manifest_receipt_id,
            "chain_verified": bool(runtime_result.get("chain_verified")),
        },
        evidence_refs=[str(manifest_receipt_id)] if manifest_receipt_id else [],
        authority_effect="GOVERNANCE_IMPLEMENTATION_ONLY",
        details={"does_not_replace_transition_authority": True},
    )
    contributions.append(stegcore)

    intr = _contribution(
        contribution_id="intr:governed-transition",
        product_id="Interlock/InTr",
        product_role="governed_transition_authority",
        processing_status="NOT_OBSERVED",
        processing_scope=["governed state-transition admission/execution boundary"],
        input_bindings={},
        output_bindings={},
        evidence_refs=[],
        authority_effect="NONE",
        provenance_basis="EXPLICIT_ABSENCE_OF_AUTHENTIC_INTR_EVIDENCE",
        details={
            "route_traversal_does_not_prove_intr": True,
            "sdk_must_not_infer_transition_authority": True,
        },
    )
    contributions.append(intr)

    agents = _contribution(
        contribution_id="stegagents:bounded-runtime",
        product_id="StegAgents/runtime",
        product_role="purpose_bounded_execution",
        processing_status="NOT_OBSERVED",
        processing_scope=["bounded worker materialization/execution/retirement"],
        input_bindings={},
        output_bindings={},
        evidence_refs=[],
        authority_effect="NONE",
        provenance_basis="EXPLICIT_ABSENCE_OF_AUTHENTIC_WORKER_EVIDENCE",
        details={"generic_execution_result_does_not_prove_stegagents": True},
    )
    contributions.append(agents)

    custody_status = runtime_result.get("master_records_custody_status")
    master_records = _contribution(
        contribution_id="master-records:custody",
        product_id="Master Records",
        product_role="custody_and_reconstruction_evidence",
        processing_status="PROCESSED" if custody_status == "RECORDED" else "NOT_OBSERVED",
        processing_scope=["exact-run evidence custody"],
        input_bindings={
            "manifest_receipt_id": manifest_receipt_id,
            "transaction_id": runtime_result.get("transaction_id"),
        },
        output_bindings={"custody_status": custody_status},
        evidence_refs=[str(manifest_receipt_id)] if manifest_receipt_id else [],
        authority_effect="CUSTODY_ONLY",
        details={"custody_grants_execution_authority": False},
    )
    contributions.append(master_records)

    envelope: dict[str, Any] = {
        "schema": PRODUCT_PROCESSING_SCHEMA,
        "composition_authority_effect": "NONE",
        "product_attribution_rule": "ACTUAL_PROCESSING_EVIDENCE_ONLY",
        "unobserved_processing_is_explicit": True,
        "contributions": contributions,
    }
    envelope["product_processing_sha256"] = canonical_sha256(envelope)

    admitted_projection = dict(admitted)
    admitted_projection["schema"] = ADMITTEDCODE_PROCESSING_SCHEMA
    admitted_projection["generic_product_processing_schema"] = PRODUCT_PROCESSING_SCHEMA
    admitted_projection["generic_contribution_ref"] = admitted["contribution_id"]
    admitted_projection["projection_sha256"] = canonical_sha256(admitted_projection)
    return envelope, admitted_projection

def build_processor_product_processing(
    *,
    canonical_manifest: Mapping[str, Any],
    processor_product_id: str,
    processor_product_role: str,
    processor_result: Mapping[str, Any],
    processor_authority_effect: str,
    processor_evidence_refs: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compose product provenance for a non-governance SDK processor result.

    This is the generic sibling of build_product_processing. It records the
    selected processor as processed, keeps AdmittedCode explicitly NOT_PROCESSED
    when the route did not traverse the admission product, and refuses to infer
    downstream transition/execution/custody products from a processor result.
    """
    identity = {
        "source_framework": canonical_manifest.get("source_framework"),
        "source_output_id": canonical_manifest.get("source_output_id"),
        "canonical_manifest_sha256": canonical_manifest.get("canonical_manifest_sha256"),
    }
    normalized_request = {"input": {"ingress_manifest_identity": identity}}
    contributions: list[dict[str, Any]] = []
    source = _source_product_contribution(normalized_request)
    if source is not None:
        contributions.append(source)

    processing = canonical_manifest.get("processing")
    processing = processing if isinstance(processing, Mapping) else {}
    sdk = _contribution(
        contribution_id="sdk:return-composition",
        product_id="StegVerse-SDK",
        product_role="manifestation_route_binding_and_result_composition",
        processing_status="PROCESSED",
        processing_scope=["manifest validation", "processor selection", "SDK return composition"],
        input_bindings={
            "canonical_manifest_sha256": canonical_manifest.get("canonical_manifest_sha256"),
            "processing_capability": processing.get("capability"),
        },
        output_bindings={"processor_result_sha256": canonical_sha256(processor_result)},
        authority_effect="NONE",
    )
    contributions.append(sdk)

    processor = _contribution(
        contribution_id=f"processor:{processor_product_id.lower().replace(' ', '-').replace('/', '-')}",
        product_id=processor_product_id,
        product_role=processor_product_role,
        processing_status="PROCESSED",
        processing_scope=["selected SDK processor execution"],
        input_bindings={
            "canonical_manifest_sha256": canonical_manifest.get("canonical_manifest_sha256"),
            "route_id": processing.get("route_id"),
        },
        output_bindings={"processor_result_sha256": canonical_sha256(processor_result)},
        evidence_refs=list(processor_evidence_refs or []),
        authority_effect=processor_authority_effect,
    )
    contributions.append(processor)

    admitted = _contribution(
        contribution_id="admittedcode:canonical-admission",
        product_id="AdmittedCode",
        product_role="admission_and_evidence",
        processing_status="NOT_PROCESSED",
        processing_scope=[],
        input_bindings={},
        output_bindings={},
        evidence_refs=[],
        authority_effect="NONE",
        provenance_basis="ROUTE_DID_NOT_TRAVERSE_ADMITTEDCODE",
        details={
            "admission_is_execution": False,
            "canonical_runtime_identity": "stegverse:steggate:canonical:three-layer:v1",
            "canonical_evaluator": "stegcore.three_layer.evaluate_three_layer",
        },
    )
    contributions.append(admitted)

    for product_id, contribution_id, role, basis in (
        ("Interlock/InTr", "intr:governed-transition", "governed_transition_authority",
         "EXPLICIT_ABSENCE_OF_AUTHENTIC_INTR_EVIDENCE"),
        ("StegAgents/runtime", "stegagents:bounded-runtime", "purpose_bounded_execution",
         "EXPLICIT_ABSENCE_OF_AUTHENTIC_WORKER_EVIDENCE"),
        ("Master Records", "master-records:custody", "custody_and_reconstruction_evidence",
         "EXPLICIT_ABSENCE_OF_CUSTODY_EVIDENCE"),
    ):
        contributions.append(_contribution(
            contribution_id=contribution_id,
            product_id=product_id,
            product_role=role,
            processing_status="NOT_OBSERVED",
            processing_scope=[],
            input_bindings={},
            output_bindings={},
            evidence_refs=[],
            authority_effect="NONE",
            provenance_basis=basis,
        ))

    envelope: dict[str, Any] = {
        "schema": PRODUCT_PROCESSING_SCHEMA,
        "composition_authority_effect": "NONE",
        "product_attribution_rule": "ACTUAL_PROCESSING_EVIDENCE_ONLY",
        "unobserved_processing_is_explicit": True,
        "contributions": contributions,
    }
    envelope["product_processing_sha256"] = canonical_sha256(envelope)

    admitted_projection = dict(admitted)
    admitted_projection["schema"] = ADMITTEDCODE_PROCESSING_SCHEMA
    admitted_projection["generic_product_processing_schema"] = PRODUCT_PROCESSING_SCHEMA
    admitted_projection["generic_contribution_ref"] = admitted["contribution_id"]
    admitted_projection["projection_sha256"] = canonical_sha256(admitted_projection)
    return envelope, admitted_projection
