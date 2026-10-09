"""Universal manifest state-transition runtime.

Every installed processing capability derives only its request/state graph locally.
The consequential lifecycle is executed by the existing manifest-selected
StegVerse processing and governance path; InTr transports its payloads. This module
never invokes repository-local runners, WorkerCoordinator, Interlock/InTr, TV/TVC,
StegAgents, or Master Records directly.

The SDK's job is to *manifest*. Outbound organization routing is not selected by
``completion.egress``: that block describes requester-facing completion/return
semantics. The canonical Universal InTr connector registry declares
``sdk-manifest-ingress / SDK:ManifestIngress`` and its owning organization, but
the current registry does not yet supply a concrete organization ``.github``
ingress endpoint to this runtime. Until that canonical mapping is available,
run-manifest fails closed rather than treating LLM-adapter, Publisher, or any
caller-authored completion surface as the organization destination.

The return leg is ``admit_runtime_result``: results arrive after the receiving
Interlock runtime has transported and admitted them, exactly as
``evaluator_review_intr`` describes for its own lane.
"""
from __future__ import annotations

import hashlib
import importlib
import json
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .connector_capability_overlay import resolve_organization_ingress
from .route_resolution import canonical_sha256, route_from_manifest
from .organization_record_names import LEGACY_ORGANIZATION_RECORD_OBSERVED_FIELD, ORGANIZATION_RECORD_OBSERVED_FIELD, read_field

REQUEST_SCHEMA = "stegverse.sdk.manifest-state-transition-request/v1"
RESULT_SCHEMA = "stegverse.sdk.manifest-state-transition-result/v1"
UNIVERSAL_RUNTIME_BINDING = "stegverse.manifest_state_transition_runtime.execute_manifest"
HANDOFF_SCHEMA = "stegverse.sdk.manifest-transition-handoff/v1"
DESTINATION_RESOLUTION_SOURCE = "CANONICAL_CONNECTOR_CAPABILITY_OVERLAY"
# The protocol's own answer to a receiver that is not listening. The SDK never
# waits for one, and a receiver's availability is not a transition predicate.
RECEIVER_UNAVAILABLE_DISPOSITION = "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION"

# What an authentic Organization/Interlock transition closure must carry to be
# admitted. Master Records reconstruction is not part of admission: it is
# organization-records evidence only and never gates a result (owner directive,
# StegVerse-SDK#368 issuecomment-6089922594: "Master Records reconstruction is
# evidence-only and non-gating").
_REQUIRED_CLOSURE = {
    "state": "RECORDED",
    "required_evidence_validation_status": "PASS",
}
MASTER_RECORDS_EVIDENCE_SCHEMA = "stegverse.sdk.master-records-reconstruction-evidence/v1"



def _result_value(result: Mapping[str, Any], key: str) -> Any:
    """Read a result field; the organization-record flag also accepts its legacy name."""
    if key == ORGANIZATION_RECORD_OBSERVED_FIELD:
        return read_field(result, ORGANIZATION_RECORD_OBSERVED_FIELD, LEGACY_ORGANIZATION_RECORD_OBSERVED_FIELD)
    return result.get(key)

def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_adapter(binding: str):
    if not isinstance(binding, str) or "." not in binding:
        raise ValueError("installed route has no state-graph adapter binding")
    module_name, function_name = binding.rsplit(".", 1)
    if not module_name.startswith("stegverse."):
        raise ValueError("state-graph adapter must resolve inside the installed StegVerse SDK")
    function = getattr(importlib.import_module(module_name), function_name, None)
    if not callable(function):
        raise ValueError(f"state-graph adapter is not callable: {binding}")
    return function


def canonical_organization_destination(organization_boundary: Mapping[str, Any]) -> dict[str, Any]:
    return resolve_organization_ingress(organization_boundary, profile_id="sdk-manifest-ingress", profile_name="SDK:ManifestIngress", operation="SUBMIT_MANIFEST")


def manifest_declared_destination(canonical: Mapping[str, Any]) -> None:
    """Compatibility shim: completion.egress is not outbound organization routing.

    The canonical connector registry now declares sdk-manifest-ingress /
    SDK:ManifestIngress and its owner. A concrete organization .github ingress
    endpoint is not yet represented in the SDK-consumable canonical mapping, so
    no outbound destination may be synthesized from completion.egress.
    """
    return None


def derive_execution_request(manifest: Mapping[str, Any], organization_boundary: Mapping[str, Any] | None = None) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    if route.get("runtime_binding") != UNIVERSAL_RUNTIME_BINDING:
        raise ValueError("installed route does not use the universal manifest state-transition runtime")
    adapter_binding = route.get("state_graph_adapter_binding")
    adapter = _load_adapter(str(adapter_binding or ""))
    # The adapter receives the original wire manifest. validate_ingress_manifest()
    # returns a canonicalized view with derived evidence fields that are not legal
    # wire fields and therefore must never be re-fed through the public validator.
    graph = adapter(manifest)
    if not isinstance(graph, Mapping):
        raise ValueError("state-graph adapter returned a non-object result")
    graph = dict(graph)
    if graph.get("adapter_executes_lifecycle") is not False and route.get("processor_capability") in {
        "purpose_bound_worker", "atomic_task_worker"
    }:
        raise ValueError("worker state-graph adapter may not execute its lifecycle")
    graph_id = graph.get("graph_id")
    if not isinstance(graph_id, str) or not graph_id:
        raise ValueError("state-graph adapter did not provide graph_id")
    task_id = graph.get("canonical_task_id")
    requires_worker_claim = graph.get("requires_workercoordinator_claim_fence")
    if requires_worker_claim is None:
        requires_worker_claim = bool(task_id)
    if requires_worker_claim and (not isinstance(task_id, str) or not task_id):
        raise ValueError("worker-claim state graph did not provide canonical_task_id")
    if task_id is not None and (not isinstance(task_id, str) or not task_id):
        raise ValueError("canonical_task_id must be null or a non-empty string")
    destination = canonical_organization_destination(organization_boundary) if isinstance(organization_boundary, Mapping) else manifest_declared_destination(canonical)
    # Bind the unchanged wire manifest and normalized validated projection separately.
    manifest_hash = canonical["canonical_manifest_sha256"]
    projection = dict(canonical)
    projection.pop("canonical_manifest_sha256")
    request = {
        "schema": REQUEST_SCHEMA,
        "canonical_manifest": dict(manifest),
        "wire_manifest_sha256": _sha256(dict(manifest)),
        "canonical_manifest_projection": projection,
        "canonical_manifest_sha256": manifest_hash,
        "processing_capability": route["processor_capability"],
        "route_id": route["route_id"],
        "route_declaration_hash": route["route_declaration_hash"],
        "state_graph": graph,
        "graph_id": graph_id,
        "canonical_task_id": task_id,
        "requires_workercoordinator_claim_fence": bool(requires_worker_claim),
        "predecessor_closure_required": True,
        "credential_authority": "TV/TVC",
        "claim_fence_authority": "WORKERCOORDINATOR",
        "transition_authority": "INTERLOCK_INTR",
        "custody_replay_reconstruction_authority": "MASTER_RECORDS",
        "manifest_declared_destination": destination,
        "destination_resolution_source": DESTINATION_RESOLUTION_SOURCE,
        # Nothing outside the manifest may name a destination.
        "destination_resolution_environment_inputs": [],
        "request_grants_authority": False,
        "sdk_executes_lifecycle": False,
        "sdk_transports_request": False,
        "authority_effect": "NONE_MANIFEST_RUNTIME_REQUEST_ONLY",
    }
    request["request_sha256"] = _sha256(request)
    return request


def _closure_reconstruction_evidence(closure: Mapping[str, Any]) -> dict[str, Any]:
    """Report one closure's Master Records reconstruction as evidence, never as a gate."""
    status = closure.get("reconstruction_status")
    reconstructed = closure.get("reconstructed_receipt_sha256")
    if status is None and reconstructed is None:
        observed = "NOT_PROVIDED"
    elif status == "PASS" and reconstructed == closure.get("receipt_sha256"):
        observed = "PASS"
    else:
        observed = "FAIL"
    return {
        "transition_id": closure.get("transition_id"),
        "reconstruction_status": status,
        "reconstructed_receipt_matches": None if reconstructed is None else reconstructed == closure.get("receipt_sha256"),
        "evidence_status": observed,
    }


def _master_records_evidence(
    result: Mapping[str, Any], graph: Mapping[str, Any], closures: list[dict[str, Any]]
) -> dict[str, Any]:
    """Validate manifest-declared reconstruction evidence as evidence only.

    A route's state graph declares reconstruction-specific evidence through its
    ``terminal_requirements``. That declaration is checked and reported here; it
    does not decide admission of the Organization-records result.
    """
    terminal = graph.get("terminal_requirements")
    terminal = terminal if isinstance(terminal, Mapping) else {}
    declared = "reconstruction_status" in terminal or "exact_receipt_reconstruction_digest_equality" in terminal
    statuses = [row["evidence_status"] for row in closures]
    for key in ("replay_status", "reconstruction_status"):
        if key in result:
            statuses.append("PASS" if result.get(key) == "PASS" else "FAIL")
    if "FAIL" in statuses:
        overall = "FAIL"
    elif statuses and all(item == "PASS" for item in statuses):
        overall = "PASS"
    elif "PASS" in statuses:
        overall = "PARTIAL"
    else:
        overall = "NOT_PROVIDED"
    return {
        "schema": MASTER_RECORDS_EVIDENCE_SCHEMA,
        "declared_by_manifest": declared,
        "declared_requirements_satisfied": (overall == "PASS") if declared else None,
        "replay_status": result.get("replay_status"),
        "reconstruction_status": result.get("reconstruction_status"),
        "closures": closures,
        "evidence_status": overall,
        "gates_admission": False,
        "authority": "MASTER_RECORDS",
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }


def _validate_transition_closures(result: Mapping[str, Any], graph: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Admit the Organization/Interlock closure chain; return reconstruction evidence rows."""
    closures = result.get("transition_closures")
    ordered = graph.get("ordered_transitions")
    if not isinstance(ordered, list):
        raise ValueError("installed state graph ordered_transitions must be an array")
    if not ordered:
        ordered = result.get("resolved_ordered_transitions")
        if not isinstance(ordered, list) or not ordered or not all(isinstance(x, str) and x for x in ordered):
            raise ValueError("RUNTIME_CANONICAL_ORDERED_TRANSITIONS_REQUIRED")
    if not isinstance(closures, list) or len(closures) != len(ordered):
        raise ValueError("MASTER_RECORDS_ORGANIZATION_RECORD_COUNT_MISMATCH")
    previous_receipt = None
    evidence = []
    for index, (expected_transition, raw) in enumerate(zip(ordered, closures)):
        if not isinstance(raw, Mapping):
            raise ValueError(f"MASTER_RECORDS_ORGANIZATION_RECORD_OBJECT_REQUIRED:{index}")
        closure = dict(raw)
        if closure.get("transition_id") != expected_transition:
            raise ValueError(f"MASTER_RECORDS_TRANSITION_ORDER_MISMATCH:{index}")
        for key, expected in _REQUIRED_CLOSURE.items():
            if closure.get(key) != expected:
                raise ValueError(f"MASTER_RECORDS_ORGANIZATION_RECORD_REQUIRED:{expected_transition}:{key}")
        receipt = closure.get("receipt_sha256")
        if not isinstance(receipt, str) or not receipt:
            # The Organization transition receipt itself is required; only its
            # Master Records reconstruction is evidence.
            raise ValueError(f"MASTER_RECORDS_RECEIPT_RECONSTRUCTION_MISMATCH:{expected_transition}")
        if index:
            if closure.get("predecessor_receipt_sha256") != previous_receipt:
                raise ValueError(f"MASTER_RECORDS_IMMEDIATE_PREDECESSOR_MISMATCH:{expected_transition}")
        previous_receipt = receipt
        evidence.append(_closure_reconstruction_evidence(closure))
    return evidence


def _validate_profile_source_deny(result: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    """Preserve the existing consumer's exact DENY without laundering its provenance.

    An evaluating source/profile can return an actionable failure before actual
    Interlock/InTr adjudication. It is NOT an authenticated sovereign verdict.
    """
    if result.get("schema") != "stegverse.sdk.manifest-profile-disposition/v1":
        raise ValueError("UNIVERSAL_INTR_DISPOSITION_SCHEMA_MISMATCH")
    is_deny = result.get("disposition") == "DENY" and result.get("state") == "DENY"
    is_terminal = result.get("disposition") == "FAIL_CLOSED" and result.get("state") == "FAIL_CLOSED"
    if not (is_deny or is_terminal):
        raise ValueError("UNIVERSAL_INTR_PROFILE_DISPOSITION_NOT_DENY_OR_TERMINAL_FAIL_CLOSED")
    for key in ("request_sha256", "wire_manifest_sha256",
                "canonical_manifest_sha256", "graph_id", "processing_capability"):
        if result.get(key) != request.get(key):
            raise ValueError(f"UNIVERSAL_INTR_DISPOSITION_BINDING_MISMATCH:{key}")
    original = request.get("canonical_manifest") or {}
    payload = original.get("payload") if isinstance(original, Mapping) else None
    if isinstance(payload, Mapping):
        for field in ("goal_task_id", "cosv"):
            if payload.get(field) != result.get(field):
                raise ValueError(f"UNIVERSAL_INTR_DISPOSITION_ORIGINAL_LINEAGE_MISMATCH:{field}")
    expected_boundary = ("SDK_ADMITTED_DIAGNOSTIC_CONSUMER_LOCAL" if is_terminal
                         else "SDK_MANIFEST_PROFILE_SOURCE_ONLY")
    if result.get("evaluation_boundary") != expected_boundary:
        raise ValueError("UNIVERSAL_INTR_DISPOSITION_BOUNDARY_MISMATCH")
    if result.get("authentic_intr_disposition_observed") is not False:
        raise ValueError("UNIVERSAL_INTR_DISPOSITION_AUTHENTICITY_ESCALATION")
    if _result_value(result, ORGANIZATION_RECORD_OBSERVED_FIELD) is not False:
        raise ValueError("UNIVERSAL_INTR_DISPOSITION_CUSTODY_ESCALATION")
    if result.get("terminal") is not is_terminal or result.get("automatic_retry_permitted") is not False:
        raise ValueError("UNIVERSAL_INTR_DISPOSITION_RETRY_CONTRACT_MISMATCH")
    if is_terminal and result.get("retry_condition") != "SEPARATELY_GOVERNED_FUTURE_REENTRY_ONLY":
        raise ValueError("UNIVERSAL_INTR_TERMINAL_REENTRY_CONTRACT_MISMATCH")
    for key in ("reason_code", "failed_predicate", "transition_id", "repair_owner",
                "retry_condition", "source_disposition_ref"):
        if not isinstance(result.get(key), str) or not result[key]:
            raise ValueError(f"UNIVERSAL_INTR_DISPOSITION_FIELD_REQUIRED:{key}")
    if not isinstance(result.get("evidence_refs"), list):
        raise ValueError("UNIVERSAL_INTR_DISPOSITION_EVIDENCE_REQUIRED")
    # The returned path is the resident profile's source-diagnostic locator,
    # not an independently checked organization record or Master Records
    # organization-record receipt.
    return dict(result)


def _validate_nonterminal_diagnostic_progress(result: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    """Only validate lineage, not independently attest the resident receipts.

    The native consumer already performs actual organization-first Master Records
    custody. This SDK projection cannot convert its response to terminal egress.
    """
    expected = {
        "schema": "stegverse.sdk.manifest-state-transition-progress/v1",
        "state": "PROCESSING_RECORDED_PUBLISHER_REQUIRED",
        "disposition": "ALLOW",
        "terminal": False,
        "communication_terminal": False,
        "publisher_required": True,
        "publisher_executed": False,
        "far_side_transition_observed": False,
        "external_master_records_independently_read_back": False,
        "next_transition_id": "RTC-PUBLISHER-005",
        "publisher_package_profile": "stegverse.publisher.evidence-report-package/v1",
        "processing_capability": "ecosystem_diagnostic",
        "authority_effect": "NONE_PROCESSING_RESULT_ONLY",
    }
    for key, value in expected.items():
        if result.get(key) != value:
            raise ValueError(f"SDK_DIAGNOSTIC_PROGRESS_CONTRACT_MISMATCH:{key}")
    for key in ("request_sha256", "wire_manifest_sha256", "canonical_manifest_sha256",
                "graph_id", "processing_capability"):
        if result.get(key) != request.get(key):
            raise ValueError(f"SDK_DIAGNOSTIC_PROGRESS_LINEAGE_MISMATCH:{key}")
    original = request.get("canonical_manifest") or {}
    payload = original.get("payload") if isinstance(original, Mapping) else None
    if not isinstance(payload, Mapping):
        raise ValueError("SDK_DIAGNOSTIC_PROGRESS_SOURCE_PAYLOAD_REQUIRED")
    if result.get("goal_task_id") != payload.get("goal_task_id") or result.get("cosv") != payload.get("cosv"):
        raise ValueError("SDK_DIAGNOSTIC_PROGRESS_GOAL_COSV_MISMATCH")
    if ((original.get("completion") or {}).get("publisher") or {}).get("required") is not True:
        raise ValueError("SDK_DIAGNOSTIC_PROGRESS_ORIGINAL_PUBLISHER_REQUIRED")
    if result.get("source_manifest_file_sha256") != "e1b05a082ce19d3d254e3cde1dced03019174a94287724959672c9e65510c8f3":
        raise ValueError("SDK_DIAGNOSTIC_PROGRESS_FROZEN_FILE_MISMATCH")
    for key in ("diagnostic_result_sha256", "intr_admission_master_records_receipt_sha256",
                "runtime_binding_master_records_receipt_sha256", "diagnostic_master_records_receipt_sha256",
                "organization_receipt_sha256", "organization_previous_receipt_sha256"):
        value = result.get(key)
        if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise ValueError(f"SDK_DIAGNOSTIC_PROGRESS_RECEIPT_DIGEST_REQUIRED:{key}")
    for key in ("node_id", "interlock_id", "lease_id", "runtime_id", "diagnostic_result_ref"):
        if not isinstance(result.get(key), str) or not result[key]:
            raise ValueError(f"SDK_DIAGNOSTIC_PROGRESS_RUNTIME_BINDING_REQUIRED:{key}")
    output = result.get("diagnostic_result")
    graph = request.get("state_graph") or {}
    if not isinstance(output, Mapping) or output.get("schema") != "stegverse.ecosystem-diagnostic-result.v1":
        raise ValueError("SDK_DIAGNOSTIC_PROGRESS_RESULT_SCHEMA_MISMATCH")
    if output.get("diagnostic_request_id") != (graph.get("request") or {}).get("diagnostic_request_id"):
        raise ValueError("SDK_DIAGNOSTIC_PROGRESS_DIAGNOSTIC_REQUEST_MISMATCH")
    if output.get("authority_effect") != "NONE_DIAGNOSTIC_ONLY" or output.get("mutation_performed") is not False:
        raise ValueError("SDK_DIAGNOSTIC_PROGRESS_RESULT_AUTHORITY_DRIFT")
    exact = (json.dumps(output, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if result.get("diagnostic_result_file_encoding") != "utf8-json-indent2-sortkeys-newline" or hashlib.sha256(exact).hexdigest() != result["diagnostic_result_sha256"]:
        raise ValueError("SDK_DIAGNOSTIC_PROGRESS_RESULT_BYTES_MISMATCH")
    return dict(result)


def _validate_worker_result_attachment_fail_closed(
    result: Mapping[str, Any], request: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate the manifest profile's actionable non-ALLOW after a targeted worker cycle.

    This is explicitly not an authenticated downstream InTr verdict. It proves only
    that the manifest-selected task cycle was attempted and the request-bound purpose
    runtime receipt required for continuation was not returned.
    """
    required = {
        "schema": "stegverse.sdk.manifest-profile-disposition/v1",
        "state": "FAIL_CLOSED",
        "disposition": "FAIL_CLOSED",
        "evaluation_boundary": "SDK_MANIFEST_WORKER_RESULT_ATTACHMENT",
        "reason_code": "AUTHENTIC_PURPOSE_RUNTIME_RECEIPT_NOT_OBSERVED",
        "failed_predicate": "EXACT_REQUEST_BOUND_PURPOSE_RUNTIME_RECEIPT_PRESENT",
        "consequence_committed_by_this_profile": False,
        "authentic_intr_disposition_observed": False,
        ORGANIZATION_RECORD_OBSERVED_FIELD: False,
        "retry_entrypoint": "EXISTING_SDK_MANIFEST_UNIVERSAL_INTR_INGRESS",
        "automatic_retry_permitted": False,
        "authority_effect": "NONE_PROFILE_BOUNDARY_DISPOSITION_ONLY",
    }
    for key, value in required.items():
        if _result_value(result, key) != value:
            raise ValueError(f"WORKER_ATTACHMENT_FAIL_CLOSED_CONTRACT_MISMATCH:{key}")
    for key in (
        "request_sha256", "canonical_manifest_sha256", "graph_id",
        "processing_capability", "route_id", "canonical_task_id",
    ):
        if result.get(key) != request.get(key):
            raise ValueError(f"WORKER_ATTACHMENT_FAIL_CLOSED_BINDING_MISMATCH:{key}")
    evidence = result.get("required_evidence_refs")
    if not isinstance(evidence, list) or evidence != [
        "EXACT_REQUEST_BOUND_ORIGINAL_INTR_DISPOSITION",
        "ORGANIZATION_LEDGER_RECEIPT_AND_PREDECESSOR",
        "MATCHING_MASTER_RECORDS_RECONSTRUCTION",
    ]:
        raise ValueError("WORKER_ATTACHMENT_FAIL_CLOSED_EVIDENCE_CONTRACT_MISMATCH")
    if not isinstance(result.get("repair_owner"), str) or not result["repair_owner"]:
        raise ValueError("WORKER_ATTACHMENT_FAIL_CLOSED_REPAIR_OWNER_REQUIRED")
    if not isinstance(result.get("source_disposition_ref"), str) or not result["source_disposition_ref"]:
        raise ValueError("WORKER_ATTACHMENT_FAIL_CLOSED_SOURCE_REF_REQUIRED")
    return dict(result)


def _validate_manifest_binding_deny(result: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the existing profile's producer-level correctable DENY, not an InTr verdict."""
    from .manifest_builder import _CORRECTABLE_MANIFEST_BINDING_DENIALS
    required = {
        "schema": "stegverse.sdk.manifest-profile-disposition/v1",
        "state": "DENY",
        "disposition": "DENY",
        "terminal": False,
        "automatic_retry_permitted": False,
        "retry_condition": "CORRECT_ENVELOPE_IN_EXISTING_MANIFEST_BUILDER_THEN_NEW_GOVERNED_ATTEMPT",
        "evaluation_boundary": "SDK_MANIFEST_PROFILE",
        "transport_validated": True,
        "authentic_intr_admission_observed": False,
        ORGANIZATION_RECORD_OBSERVED_FIELD: False,
        "transition_id": "SDK_MANIFEST_BINDING",
        "repair_owner": "StegVerse-org/StegVerse-SDK:stegverse/manifest_builder.py",
        "authority_effect": "NONE_MANIFEST_PROFILE_DENY_ONLY",
    }
    for key, value in required.items():
        if _result_value(result, key) != value:
            raise ValueError(f"MANIFEST_BINDING_DENY_CONTRACT_MISMATCH:{key}")
    if result.get("reason_code") not in _CORRECTABLE_MANIFEST_BINDING_DENIALS:
        raise ValueError("MANIFEST_BINDING_DENY_REASON_UNAPPROVED")
    if result.get("failed_predicate") != result["reason_code"]:
        raise ValueError("MANIFEST_BINDING_DENY_PREDICATE_MISMATCH")
    if result.get("original_request_sha256") != _sha256(request):
        raise ValueError("MANIFEST_BINDING_DENY_ORIGINAL_REQUEST_MISMATCH")
    if result.get("original_wire_manifest_sha256") != _sha256(request["canonical_manifest"]):
        raise ValueError("MANIFEST_BINDING_DENY_ORIGINAL_WIRE_MISMATCH")
    if result.get("claimed_request_sha256") != request.get("request_sha256"):
        raise ValueError("MANIFEST_BINDING_DENY_CLAIMED_REQUEST_MISMATCH")
    if result.get("graph_id") != request.get("graph_id") or result.get("processing_capability") != request.get("processing_capability"):
        raise ValueError("MANIFEST_BINDING_DENY_GRAPH_MISMATCH")
    if not isinstance(result.get("source_disposition_ref"), str) or not result["source_disposition_ref"]:
        raise ValueError("MANIFEST_BINDING_DENY_SOURCE_REF_REQUIRED")
    return dict(result)


def _validate_shwp_parent_profile_result(result: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    """Bounded SDK-facing SHWP outcome; never substitute for organization custody."""
    if request.get("processing_capability") != "sovereign_inference":
        raise ValueError("SHWP_RESULT_WRONG_REQUEST_CAPABILITY")
    for key in ("request_sha256", "wire_manifest_sha256", "canonical_manifest_sha256",
                "graph_id", "processing_capability", "route_id", "canonical_task_id"):
        if result.get(key) != request.get(key):
            raise ValueError("SHWP_RESULT_MANIFEST_LINEAGE_MISMATCH:" + key)
    graph = request.get("state_graph") or {}
    expected_original = (graph.get("request") or {}).get("original_request_sha256")
    if result.get("original_request_sha256") != expected_original:
        raise ValueError("SHWP_RESULT_ORIGINAL_REQUEST_BINDING_MISMATCH")
    for key, expected in {
        "schema": "stegverse.sdk.shwp-manifest-transition-result/v1",
        "terminal": False,
        "evaluation_boundary": "SDK_SHWP_MANIFEST_BOUND_PARENT_CONSUMER",
        "authentic_intr_disposition_observed": False,
        ORGANIZATION_RECORD_OBSERVED_FIELD: False,
        "consequence_committed_by_this_adapter": False,
        "authority_effect": "NONE_PROFILE_RETURN_ONLY",
        "owning_existing_goal": "SHWP-ECOSYSTEM-CHAT-INFERENCE-001",
    }.items():
        if _result_value(result, key) != expected:
            raise ValueError("SHWP_RESULT_SOURCE_BOUNDARY_MISMATCH:" + key)
    if result.get("state") == "FAIL_CLOSED":
        if result.get("disposition") != "FAIL_CLOSED":
            raise ValueError("SHWP_NON_ALLOW_DISPOSITION_MISMATCH")
        if not isinstance(result.get("failed_predicate"), str) or not result["failed_predicate"]:
            raise ValueError("SHWP_NON_ALLOW_FAILED_PREDICATE_REQUIRED")
    elif result.get("state") == "PROCESSING_RECORDED_CUSTODY_READBACK_REQUIRED":
        if result.get("disposition") != "ALLOW" or result.get("failed_predicate") is not None:
            raise ValueError("SHWP_NONTERMINAL_PROCESSING_RESULT_INVALID")
        if result.get("consumer_disposition") != "ALLOW":
            raise ValueError("SHWP_NONTERMINAL_PARENT_CONSUMPTION_UNVERIFIED")
        # Even a verified original parent return is not original organization
        # HEAD/readback or independent predecessor-linked Master Records proof.
        if result.get("runtime_execution_attempted") is not True:
            raise ValueError("SHWP_NONTERMINAL_EXECUTION_ATTEMPT_REQUIRED")
    else:
        raise ValueError("SHWP_RESULT_UNSUPPORTED_STATE")
    claimed = result.get("diagnostic_sha256")
    body = dict(result)
    body.pop("diagnostic_sha256", None)
    if not isinstance(claimed, str) or _sha256(body) != claimed:
        raise ValueError("SHWP_RESULT_SOURCE_DIAGNOSTIC_DIGEST_MISMATCH")
    return dict(result)


def _validate_governance_runtime_result(
    result: Mapping[str, Any], request: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate one parent governance disposition without conflating downstream execution."""
    disposition = result.get("disposition")
    if disposition not in {"ALLOW", "DENY", "FAIL_CLOSED"}:
        raise ValueError("GOVERNANCE_RESULT_DISPOSITION_INVALID")
    expected_state = "COMPLETE" if disposition == "ALLOW" else disposition
    if result.get("state") != expected_state:
        raise ValueError("GOVERNANCE_RESULT_STATE_MISMATCH")
    if result.get("terminal") is not (disposition != "ALLOW"):
        raise ValueError("GOVERNANCE_RESULT_TERMINAL_MISMATCH")
    if result.get("communication_terminal") is not False:
        raise ValueError("GOVERNANCE_RESULT_COMMUNICATION_TERMINAL_ESCALATION")
    for key in (
        "request_sha256", "wire_manifest_sha256", "canonical_manifest_sha256",
        "graph_id", "canonical_task_id", "processing_capability", "route_id",
    ):
        if result.get(key) != request.get(key):
            raise ValueError(f"GOVERNANCE_RESULT_BINDING_MISMATCH:{key}")
    if result.get("processing_capability") != "governance":
        raise ValueError("GOVERNANCE_RESULT_CAPABILITY_MISMATCH")
    # A governance decision is recorded in organization records only. Master
    # Records is not part of the governance path, so a result claiming a Master
    # Records organization record is not a result this route produces.
    if result.get("records_authority") != "ORGANIZATION_RECORDS_ONLY":
        raise ValueError("GOVERNANCE_RESULT_ORGANIZATION_RECORDS_REQUIRED")
    if _result_value(result, ORGANIZATION_RECORD_OBSERVED_FIELD):
        raise ValueError("GOVERNANCE_RESULT_MASTER_RECORDS_NOT_IN_GOVERNANCE_PATH")
    if result.get("publisher_executed") is not False or result.get("site_propagation_executed") is not False:
        raise ValueError("GOVERNANCE_RESULT_EXTERNAL_MUTATION_ESCALATION")
    reconstruction = _validate_transition_closures(result, request["state_graph"])

    action = result.get("manifest_directed_action")
    task_id = request.get("canonical_task_id")
    if task_id == "ORGANIZATION-BATCH-CUSTODY-REPLAY-001":
        if disposition == "ALLOW":
            if not isinstance(action, Mapping):
                raise ValueError("ORGANIZATION_BATCH_ACTION_RESULT_REQUIRED_AFTER_ALLOW")
            required = {
                "schema": "stegverse.manifest-directed-action-execution/v1",
                "action_id": "ORGANIZATION_APPEND",
                "governance_disposition": None,
                "canonical_manifest_sha256": request["canonical_manifest_sha256"],
                "authority_effect": "NONE_EXECUTION_EVIDENCE_ONLY",
            }
            for key, expected in required.items():
                if action.get(key) != expected:
                    raise ValueError(f"ORGANIZATION_BATCH_ACTION_RESULT_MISMATCH:{key}")
            if action.get("execution_result") not in {"COMPLETED", "FAILED"}:
                raise ValueError("ORGANIZATION_BATCH_ACTION_EXECUTION_RESULT_INVALID")
            parent = action.get("parent_governance_receipt_sha256")
            if not isinstance(parent, str) or len(parent) != 64:
                raise ValueError("ORGANIZATION_BATCH_PARENT_GOVERNANCE_RECEIPT_INVALID")
            dispatch = action.get("dispatch_closure")
            if not isinstance(dispatch, Mapping):
                raise ValueError("ORGANIZATION_BATCH_DISPATCH_CLOSURE_REQUIRED")
            for key, expected in _REQUIRED_CLOSURE.items():
                if dispatch.get(key) != expected:
                    raise ValueError(f"ORGANIZATION_BATCH_DISPATCH_CLOSURE_INVALID:{key}")
            if action["execution_result"] == "COMPLETED":
                if not isinstance(action.get("organization_receipt_sha256"), str):
                    raise ValueError("ORGANIZATION_BATCH_ORGANIZATION_RECEIPT_REQUIRED")
                released = action.get("released_batch")
                if released is not None:
                    if not isinstance(released, Mapping):
                        raise ValueError("ORGANIZATION_BATCH_RELEASED_BATCH_RESULT_INVALID")
                    if released.get("execution_result") not in {"COMPLETED", "FAILED"}:
                        raise ValueError("ORGANIZATION_BATCH_CARRIAGE_RESULT_INVALID")
                    if released.get("governance_disposition") is not None:
                        raise ValueError("ORGANIZATION_BATCH_CARRIAGE_GOVERNANCE_ESCALATION")
            else:
                failure = action.get("failure_closure")
                if not isinstance(failure, Mapping):
                    raise ValueError("ORGANIZATION_BATCH_FAILURE_CLOSURE_REQUIRED")
                for key, expected in _REQUIRED_CLOSURE.items():
                    if failure.get(key) != expected:
                        raise ValueError(f"ORGANIZATION_BATCH_FAILURE_CLOSURE_INVALID:{key}")
                if not isinstance(action.get("failed_predicate"), str) or not action["failed_predicate"]:
                    raise ValueError("ORGANIZATION_BATCH_FAILED_PREDICATE_REQUIRED")
        elif action is not None:
            raise ValueError("ORGANIZATION_BATCH_NONALLOW_MUST_NOT_EXECUTE_ACTION")
    elif action is not None:
        raise ValueError("UNBOUND_MANIFEST_DIRECTED_ACTION_RESULT")
    checked = dict(result)
    checked["master_records_reconstruction_evidence"] = _master_records_evidence(
        result, request["state_graph"], reconstruction)
    return checked


def validate_runtime_result(result: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    if result.get("schema") == "stegverse.sdk.shwp-manifest-transition-result/v1":
        return _validate_shwp_parent_profile_result(result, request)
    if result.get("schema") == "stegverse.sdk.manifest-profile-disposition/v1" and result.get("evaluation_boundary") == "SDK_MANIFEST_PROFILE":
        return _validate_manifest_binding_deny(result, request)
    if result.get("schema") == "stegverse.sdk.manifest-profile-disposition/v1" and result.get("evaluation_boundary") == "SDK_MANIFEST_WORKER_RESULT_ATTACHMENT":
        return _validate_worker_result_attachment_fail_closed(result, request)
    if result.get("schema") == "stegverse.sdk.manifest-profile-disposition/v1":
        return _validate_profile_source_deny(result, request)
    if result.get("schema") == "stegverse.sdk.manifest-state-transition-progress/v1":
        return _validate_nonterminal_diagnostic_progress(result, request)
    if result.get("schema") == RESULT_SCHEMA and request.get("processing_capability") == "governance":
        return _validate_governance_runtime_result(result, request)
    if result.get("schema") != RESULT_SCHEMA:
        raise ValueError("UNIVERSAL_INTR_RESULT_SCHEMA_MISMATCH")
    if result.get("state") != "COMPLETE":
        reason = result.get("reason") or result.get("blocker") or "runtime_not_complete"
        raise ValueError(f"UNIVERSAL_INTR_RUNTIME_NOT_COMPLETE:{reason}")
    for key in ("canonical_manifest_sha256", "graph_id", "canonical_task_id", "processing_capability", "route_id"):
        if result.get(key) != request.get(key):
            raise ValueError(f"UNIVERSAL_INTR_RESULT_BINDING_MISMATCH:{key}")
    graph = request["state_graph"]
    reconstruction = _validate_transition_closures(result, graph)
    # Master Records replay and reconstruction are reported as evidence below;
    # a missing or failed status does not refuse an otherwise-valid result.
    terminal = result.get("terminal_state")
    if not isinstance(terminal, Mapping):
        raise ValueError("TERMINAL_STATE_REQUIRED")
    if terminal.get("records_only") is not True:
        raise ValueError("TERMINAL_RECORDS_ONLY_REQUIRED")
    if terminal.get("continued_authority") is not False:
        raise ValueError("TERMINAL_CONTINUED_AUTHORITY_FALSE_REQUIRED")
    receipt_id = result.get("manifest_receipt_id")
    if not isinstance(receipt_id, str) or not receipt_id:
        raise ValueError("MANIFEST_RECEIPT_ID_REQUIRED")
    checked = dict(result)
    checked["master_records_reconstruction_evidence"] = _master_records_evidence(result, graph, reconstruction)
    return checked


def _destination_not_declared(request: Mapping[str, Any]) -> dict[str, Any]:
    """Capability is known, but its canonical organization ingress endpoint is not."""
    result = {
        "schema": "stegverse.sdk.manifest-handoff-disposition/v1",
        "state": "FAIL_CLOSED",
        "disposition": "FAIL_CLOSED",
        "evaluation_boundary": "SDK_ORGANIZATION_DESTINATION_RESOLUTION",
        "failure_code": "CANONICAL_ORGANIZATION_INGRESS_ENDPOINT_NOT_RESOLVED",
        "failed_predicate": "REGISTERED_CAPABILITY_RESOLVES_TO_CANONICAL_ORGANIZATION_GITHUB_INGRESS_ENDPOINT",
        "required_evidence_or_repair": (
            "Consume the canonical capability/connector mapping that resolves "
            "sdk-manifest-ingress / SDK:ManifestIngress to the owning organization's "
            ".github ingress endpoint. Do not substitute completion.egress, "
            "LLM-adapter, Publisher, an environment URL, host, or device."),
        "retry_entrypoint": "stegverse.manifest_state_transition_runtime.execute_manifest",
        "next_attempt": "RETRY_AFTER_CANONICAL_ORGANIZATION_ENDPOINT_MAPPING_IS_AVAILABLE",
        "canonical_task_id": request.get("canonical_task_id"),
        "request_sha256": request["request_sha256"],
        "wire_manifest_sha256": request["wire_manifest_sha256"],
        "canonical_manifest_sha256": request["canonical_manifest_sha256"],
        "graph_id": request["graph_id"],
        "processing_capability": request["processing_capability"],
        "route_id": request["route_id"],
        "connector_profile_id": "sdk-manifest-ingress",
        "connector_destination_subsystem": "SDK:ManifestIngress",
        "connector_owner_ref": "StegVerse-org/StegVerse-SDK",
        "destination_resolution_source": DESTINATION_RESOLUTION_SOURCE,
        "completion_egress_controls_outbound_organization_routing": False,
        "llm_adapter_is_outbound_organization_destination": False,
        "publisher_is_outbound_organization_destination": False,
        "consequence_committed": False,
        "authentic_governance_disposition_observed": False,
        "organization_receipt_observed": False,
        "master_records_reconstruction_observed": False,
        "machine_dependency_introduced": False,
        "external_machine_required": False,
        "receiver_availability_consulted": False,
        "evidence_class": "SDK_LOCAL_CAPABILITY_DESTINATION_RESOLUTION",
        "authority_effect": "NONE",
    }
    result["diagnostic_sha256"] = _sha256(result)
    return result


def build_intr_handoff(request: Mapping[str, Any]) -> dict[str, Any]:
    """Hand the manifested request to the receiving Interlock runtime.

    This is the SDK's terminal act for the outbound leg. It binds the request to
    the organization-owned receiving operation and states what the Interlock now owns.
    It opens no connection, carries no transport credential, and does not wait:
    the handoff is complete whether or not a receiver is listening right now.
    """
    destination = request.get("manifest_declared_destination")
    if not isinstance(destination, Mapping):
        return _destination_not_declared(request)
    handoff = {
        "schema": HANDOFF_SCHEMA,
        "state": "MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF",
        "disposition": "ALLOW",
        "evaluation_boundary": "SDK_MANIFEST_HANDOFF",
        "terminal": False,
        "request_sha256": request["request_sha256"],
        "wire_manifest_sha256": request["wire_manifest_sha256"],
        "canonical_manifest_sha256": request["canonical_manifest_sha256"],
        "graph_id": request["graph_id"],
        "canonical_task_id": request.get("canonical_task_id"),
        "processing_capability": request["processing_capability"],
        "route_id": request["route_id"],
        "destination": dict(destination),
        "destination_resolution_source": DESTINATION_RESOLUTION_SOURCE,
        "destination_resolution_environment_inputs": [],
        # What the SDK did, and did not do.
        "transport_performed_by_sdk": False,
        "transport_credential_supplied_by_sdk": False,
        "receiver_contacted": False,
        "receiver_availability_required": False,
        "receiver_unavailable_disposition": RECEIVER_UNAVAILABLE_DISPOSITION,
        "awaits_external_machine": False,
        # What remains with the Interlock, unobserved from here.
        "transition_authority": "INTERLOCK_INTR",
        "intr_admission_observed": False,
        "far_side_transition_observed": False,
        "organization_receipt_observed": False,
        "master_records_reconstruction_observed": False,
        "consequence_committed": False,
        "next_transition_owner": "INTERLOCK_INTR",
        "return_entrypoint": "stegverse.manifest_state_transition_runtime.admit_runtime_result",
        "evidence_class": "SDK_LOCAL_MANIFEST_HANDOFF",
        "authority_effect": "NONE_MANIFEST_HANDOFF_ONLY",
    }
    handoff["handoff_sha256"] = _sha256(handoff)
    return handoff


def execute_manifest(manifest: Mapping[str, Any], organization_boundary: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Manifest one transition and hand it to the receiving Interlock runtime.

    Returns the handoff disposition. It does not return a runtime result, because
    the SDK does not perform the transition and does not wait for one: a result
    arrives separately, through ``admit_runtime_result``.
    """
    return build_intr_handoff(derive_execution_request(manifest, organization_boundary))


def admit_runtime_result(
    manifest: Mapping[str, Any],
    request: Mapping[str, Any],
    result: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate a result the receiving Interlock runtime has returned.

    The receiving runtime owns transport and admission before this is called. A
    correctable manifest-binding DENY is repaired and re-manifested once, which
    produces a new handoff with its own distinct hash - never a replay of the
    identical request, and never a second transport attempt from here.
    """
    checked = validate_runtime_result(result, request)
    if not (checked.get("disposition") == "DENY"
            and checked.get("evaluation_boundary") == "SDK_MANIFEST_PROFILE"):
        return checked
    from .manifest_builder import correct_manifest_binding_deny
    try:
        repaired = correct_manifest_binding_deny(manifest, request, checked)
    except ValueError as exc:
        if str(exc) == "manifest_binding_repair_produced_unchanged_request":
            return checked  # Retain precise DENY; never replay identical request.
        raise
    return {
        "schema": HANDOFF_SCHEMA,
        "state": "REMANIFESTED_AFTER_CORRECTABLE_BINDING_DENY",
        "disposition": "ALLOW",
        "evaluation_boundary": "SDK_MANIFEST_HANDOFF",
        "terminal": False,
        "corrected_from_request_sha256": request.get("request_sha256"),
        "corrected_from_disposition": dict(checked),
        "handoff": build_intr_handoff(repaired),
        "repaired_request": dict(repaired),
        "authority_effect": "NONE_MANIFEST_HANDOFF_ONLY",
    }


__all__ = [
    "DESTINATION_RESOLUTION_SOURCE",
    "HANDOFF_SCHEMA",
    "MASTER_RECORDS_EVIDENCE_SCHEMA",
    "RECEIVER_UNAVAILABLE_DISPOSITION",
    "REQUEST_SCHEMA",
    "RESULT_SCHEMA",
    "UNIVERSAL_RUNTIME_BINDING",
    "admit_runtime_result",
    "build_intr_handoff",
    "derive_execution_request",
    "execute_manifest",
    "manifest_declared_destination",
    "validate_runtime_result",
]
