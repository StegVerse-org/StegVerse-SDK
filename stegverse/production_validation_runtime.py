"""Production-lane evaluator validation through manifested Core-Lite routing and deployed StegCore.

Every route transition is appended through the caller-bound Organization ledger sink:
runtime reality and custody stay with the Organization, and the transition closes on
the organization-ledger receipt. Master Records only records the released exact-run
batch receipt downstream, after closure. That recording is optional and non-gating:
a missing configuration or a recording failure is reported in ``master_records_recording``
(six-field non-ALLOW on failure) and never changes the run result
(LLMA-DECLARED-PATH-CONFORMANCE-368). Replay and reconstruction read the released
record back from Master Records, which is its downstream reconstruction role.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import uuid
from typing import Any, Callable, Mapping

import requests

from .public_inspection import PublicInspectionRequestError, load_public_inspection_request, validate_public_inspection_request
from .organization_record_names import (
    LEGACY_RECORD_STATUS_FIELD,
    ORGANIZATION_RECORD_RECEIPT_FIELD,
    ORGANIZATION_RECORD_STATUS_FIELD,
    RECORD_REQUESTED_FIELD,
    RECORD_STATUS_FIELD,
    read_field,
)


class PublicInspectionRuntimeError(RuntimeError):
    pass


OWNING_EXISTING_GOAL = "LLMA-DECLARED-PATH-CONFORMANCE-368"
OrganizationLedgerSink = Callable[[str, Mapping[str, Any]], Mapping[str, Any]]


def _non_allow(failure_code: str, failed_predicate: str, repair: str, retry: str, next_attempt: str, **extra: Any) -> dict[str, Any]:
    body = {
        "failure_code": failure_code,
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": repair,
        "retry_entrypoint": retry,
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "next_attempt": next_attempt,
    }
    body.update(extra)
    return body


def _canonical_hash(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _load_stegcore():
    try:
        from stegcore.manifest_receipt_provider import build_master_records_submission
        from stegcore.manifest_receipts import ManifestReceiptRegistry
        from stegcore.steggate import AdmissibilityRequest, evaluate_admissibility
        from stegcore.transaction_lifecycle import ManifestedTransactionResult
    except ImportError as exc:
        raise PublicInspectionRuntimeError("StegCore schemas are required. Install the current governed-test dependency.") from exc
    return build_master_records_submission, ManifestReceiptRegistry, AdmissibilityRequest, evaluate_admissibility, ManifestedTransactionResult


def _load_route_carrier():
    try:
        from core_lite.transaction_route import ManifestRouteCarrier, RouteCarrierError, build_route_manifest, default_validation_route
    except ImportError as exc:
        raise PublicInspectionRuntimeError("Core-Lite manifested route carrier is required for production-lane validation.") from exc
    return ManifestRouteCarrier, RouteCarrierError, build_route_manifest, default_validation_route


def _runtime_input(request: Mapping[str, Any]) -> tuple[Mapping[str, Any], Any]:
    input_block = request.get("input")
    if not isinstance(input_block, Mapping):
        raise PublicInspectionRuntimeError("public inspection input must be an object")
    steggate_request = input_block.get("steggate_request")
    if not isinstance(steggate_request, Mapping):
        raise PublicInspectionRuntimeError("governed execution requires input.steggate_request containing a canonical StegCore AdmissibilityRequest")
    return steggate_request, input_block.get("input_data", {})


def _execution_provenance(request: Mapping[str, Any]) -> dict[str, Any]:
    provenance = request.get("execution_provenance")
    if not isinstance(provenance, Mapping):
        raise PublicInspectionRuntimeError("execution_provenance is required for governed validation")
    lane_class = str(provenance.get("lane_class") or "")
    if lane_class not in {"PRODUCTION_VALIDATION", "ENCLOSED_DEMO_TEST"}:
        raise PublicInspectionRuntimeError("execution_provenance.lane_class is invalid")
    return dict(provenance)


def _source_execution_provenance(package: Mapping[str, Any]) -> dict[str, Any]:
    metadata = ((package.get("manifest") or {}).get("metadata") or {})
    provenance = metadata.get("execution_provenance")
    if not isinstance(provenance, Mapping):
        raise PublicInspectionRuntimeError("retained run predates execution-provenance custody")
    return dict(provenance)


def _optional_master_records_config(base_url: str | None = None, token: str | None = None) -> tuple[str, str] | None:
    url = (base_url or os.getenv("MASTER_RECORDS_URL") or "").rstrip("/")
    auth = token or os.getenv("MASTER_RECORDS_AUTH_TOKEN") or ""
    if not url or not auth:
        return None
    return url, auth


def _master_records_config(base_url: str | None = None, token: str | None = None) -> tuple[str, str]:
    """Configuration for reading a released record back from Master Records (replay/reconstruction)."""
    config = _optional_master_records_config(base_url, token)
    if config is None:
        raise PublicInspectionRuntimeError("Replay and reconstruction read the released record from Master Records. Configure MASTER_RECORDS_URL and MASTER_RECORDS_AUTH_TOKEN.")
    return config


def _stegcore_config(base_url: str | None = None) -> str:
    url = (base_url or os.getenv("STEGCORE_URL") or "").rstrip("/")
    if not url:
        raise PublicInspectionRuntimeError("STEGCORE_URL is required for production validation; no hosted-provider default is permitted")
    return url


def _record_status(body: Mapping[str, Any]) -> Any:
    """Record status from a Master Records response; pre-migration services use the legacy name."""
    return read_field(body, RECORD_STATUS_FIELD, LEGACY_RECORD_STATUS_FIELD)


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _preflight_stegcore(base_url: str) -> dict[str, Any]:
    try:
        response = requests.get(f"{base_url}/v1/runtime-identity", timeout=15)
    except requests.RequestException as exc:
        raise PublicInspectionRuntimeError(f"StegCore production service preflight failed: {exc}") from exc
    if response.status_code != 200:
        raise PublicInspectionRuntimeError(f"StegCore production service preflight failed: HTTP {response.status_code}")
    body = response.json()
    if body.get("runtime_identity") != "stegverse:steggate:canonical:three-layer:v1":
        raise PublicInspectionRuntimeError("StegCore production runtime identity mismatch")
    if body.get("manifested_validation_endpoint") != "/v1/manifested-validation":
        raise PublicInspectionRuntimeError("StegCore production service does not expose manifested validation")
    return body


def _retain_in_master_records(base_url: str, token: str, record: Any, evidence: Mapping[str, Any], build_submission: Any) -> dict[str, Any]:
    """Submit the released exact-run batch receipt to Master Records (downstream recording)."""
    payload = build_submission(record, evidence)
    try:
        response = requests.post(f"{base_url}/api/master-records/manifest-receipts", headers=_headers(token), json=payload, timeout=30)
    except requests.RequestException as exc:
        raise PublicInspectionRuntimeError(f"Master Records organization record failed: {exc}") from exc
    if response.status_code not in (200, 201):
        raise PublicInspectionRuntimeError(f"Master Records organization record failed: HTTP {response.status_code}: {response.text[:500]}")
    body = response.json()
    if _record_status(body) != "RECORDED":
        raise PublicInspectionRuntimeError("Master Records did not confirm a RECORDED organization record")
    return body


def _record_downstream(base_url: str, token: str, record: Any, evidence: Mapping[str, Any], build_submission: Any) -> dict[str, Any]:
    """Record the released batch receipt in Master Records; never raise, never gate."""
    base = {
        "recorder_role": "DOWNSTREAM_RELEASED_BATCH_RECEIPT_RECORDING",
        "gates_completion": False,
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
    try:
        receipt = _retain_in_master_records(base_url, token, record, evidence, build_submission)
    except (PublicInspectionRuntimeError, requests.RequestException, ValueError) as exc:
        return {
            **base,
            "status": "NOT_RECORDED",
            "disposition": "NON_ALLOW_RECORDING_ONLY",
            **_non_allow(
                "MASTER_RECORDS_RECORDING_NOT_COMPLETED",
                "MASTER_RECORDS_RECORDED_RELEASED_EXACT_RUN_RECEIPT",
                "Optional: re-submit the released exact-run receipt to Master Records. The run already closed on its organization-ledger receipt.",
                "stegverse.production_validation_runtime._retain_in_master_records",
                "OPTIONAL_DOWNSTREAM_RECORDING_RETRY_NON_BLOCKING",
                failure_detail=str(exc),
            ),
        }
    return {**base, "status": "RECORDED", "receipt": receipt}


def _get_json(url: str, token: str) -> dict[str, Any]:
    try:
        response = requests.get(url, headers=_headers(token), timeout=30)
    except requests.RequestException as exc:
        raise PublicInspectionRuntimeError(f"Master Records lookup failed: {exc}") from exc
    if response.status_code != 200:
        raise PublicInspectionRuntimeError(f"Master Records lookup failed: HTTP {response.status_code}: {response.text[:500]}")
    body = response.json()
    if not isinstance(body, dict):
        raise PublicInspectionRuntimeError("Master Records returned a non-object response")
    return body


def _record_operation_event(base_url: str, token: str, manifest_receipt_id: str, operation_id: str, operation: str, sequence: int, event_type: str, *, details: Mapping[str, Any] | None = None, artifact: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Record one replay/reconstruction operation event in Master Records.

    Downstream and non-gating: a failure is returned as a six-field non-ALLOW entry and
    the operation continues.
    """
    try:
        return _record_operation_event_strict(base_url, token, manifest_receipt_id, operation_id, operation, sequence, event_type, details=details, artifact=artifact)
    except (PublicInspectionRuntimeError, requests.RequestException, ValueError) as exc:
        return {
            "status": "NOT_RECORDED",
            "disposition": "NON_ALLOW_RECORDING_ONLY",
            "gates_operation": False,
            "operation_id": operation_id,
            "sequence": sequence,
            "event_type": event_type,
            **_non_allow(
                "MASTER_RECORDS_OPERATION_EVENT_NOT_RECORDED",
                "MASTER_RECORDS_RECORDED_OPERATION_EVENT",
                "Optional: re-submit the operation event to Master Records. The operation result stands without it.",
                "stegverse.production_validation_runtime._record_operation_event",
                "OPTIONAL_DOWNSTREAM_RECORDING_RETRY_NON_BLOCKING",
                failure_detail=str(exc),
            ),
        }


def _record_operation_event_strict(base_url: str, token: str, manifest_receipt_id: str, operation_id: str, operation: str, sequence: int, event_type: str, *, details: Mapping[str, Any] | None = None, artifact: Mapping[str, Any] | None = None) -> dict[str, Any]:
    event = {"operation_id": operation_id, "operation": operation, "sequence": sequence, "event_type": event_type, "details": dict(details or {}), "artifact_sha256": _canonical_hash(artifact) if artifact is not None else None, "authority_granted": False}
    payload = {"schema": "stegverse.master-records.manifest-operation-event-submission.v1", "event": event, RECORD_REQUESTED_FIELD: True, "authority_requested": False}
    try:
        response = requests.post(f"{base_url}/api/master-records/manifest-receipts/{manifest_receipt_id}/operations", headers=_headers(token), json=payload, timeout=30)
    except requests.RequestException as exc:
        raise PublicInspectionRuntimeError(f"Master Records operation organization record failed: {exc}") from exc
    if response.status_code not in (200, 201):
        raise PublicInspectionRuntimeError(f"Master Records operation organization record failed: HTTP {response.status_code}: {response.text[:500]}")
    body = response.json()
    if _record_status(body) != "RECORDED":
        raise PublicInspectionRuntimeError("Master Records did not record operation transition")
    return body


def _run_deployed_stegcore(base_url: str, active_manifest: Mapping[str, Any], admissibility_request: Any, input_data: Any, normalized: Mapping[str, Any], provenance: Mapping[str, Any], ManifestedTransactionResult: Any) -> Any:
    payload = {
        "transaction_id": active_manifest["transaction_id"],
        "request": admissibility_request.model_dump(mode="json", exclude_none=False),
        "input_data": input_data,
        "source": "stegverse-sdk:production-validation",
        "subject": f"public-inspection:{normalized['request_id']}",
        "metadata": {
            "public_inspection_request_id": normalized["request_id"],
            "case_profile": normalized["case_profile"],
            "test_mode": True,
            "external_side_effects_enabled": False,
            "execution_provenance": dict(provenance),
            "route_manifest_id": active_manifest["route_manifest_id"],
            "route_receipt_chain_head_at_stegcore_entry": active_manifest.get("receipt_chain_head"),
            "governance_request": admissibility_request.model_dump(mode="json", exclude_none=False),
        },
        "external_side_effects_enabled": False,
    }
    try:
        response = requests.post(f"{base_url}/v1/manifested-validation", json=payload, timeout=45)
    except requests.RequestException as exc:
        raise PublicInspectionRuntimeError(f"deployed StegCore manifested validation failed: {exc}") from exc
    if response.status_code != 200:
        raise PublicInspectionRuntimeError(f"deployed StegCore manifested validation failed: HTTP {response.status_code}: {response.text[:500]}")
    body = response.json()
    if body.get("transaction_id") != active_manifest["transaction_id"]:
        raise PublicInspectionRuntimeError("deployed StegCore changed the manifested transaction identity")
    if body.get("service_runtime_identity") != "stegverse:steggate:canonical:three-layer:v1":
        raise PublicInspectionRuntimeError("deployed StegCore response runtime identity mismatch")
    if body.get("service_external_side_effect") is not False:
        raise PublicInspectionRuntimeError("deployed StegCore validation consequence boundary invalid")
    return ManifestedTransactionResult.model_validate(body)


def organization_ledger_not_bound(request_id: Any) -> dict[str, Any]:
    """Six-field non-ALLOW when no Organization ledger sink is bound for the route."""
    return {
        "schema": "stegverse.public-inspection-production-validation-refusal.v1",
        "request_id": request_id,
        "disposition": "FAIL_CLOSED",
        **_non_allow(
            "ORGANIZATION_LEDGER_SINK_NOT_BOUND",
            "ROUTE_TRANSITIONS_APPEND_TO_ORGANIZATION_LEDGER",
            "Bind organization_ledger_sink to the owning Organization's ledger append (manifest-directed, under the organization ledger lock). Master Records is not a substitute: it only records released batch receipts downstream.",
            "stegverse.production_validation_runtime.run_public_inspection_test",
            "RETRY_WITH_ORGANIZATION_LEDGER_SINK_BOUND",
        ),
        "consequence_committed": False,
        "external_side_effect": False,
        "authority_effect": "NONE",
    }


def run_public_inspection_test(request: Mapping[str, Any], *, organization_ledger_sink: OrganizationLedgerSink | None = None, master_records_url: str | None = None, master_records_token: str | None = None, stegcore_url: str | None = None) -> dict[str, Any]:
    """Run one production-lane validation; route transitions append to the Organization ledger.

    ``organization_ledger_sink(route_manifest_id, event)`` must return the Organization's
    ledger receipt (``custody_status`` RECORDED plus the event's ``route_receipt_id`` and
    ``event_hash``). Master Records configuration is optional: when present, the released
    exact-run receipt is recorded there downstream after closure, without gating.
    """
    normalized = validate_public_inspection_request(request)
    steggate_body, input_data = _runtime_input(normalized)
    provenance = _execution_provenance(normalized)
    if provenance.get("lane_class") != "PRODUCTION_VALIDATION":
        raise PublicInspectionRuntimeError("this runtime is the production-lane validation path; enclosed demo/test requests must remain on their declared demo/test surface")
    if organization_ledger_sink is None:
        return organization_ledger_not_bound(normalized["request_id"])

    master_records = _optional_master_records_config(master_records_url, master_records_token)
    core_url = _stegcore_config(stegcore_url)
    core_identity = _preflight_stegcore(core_url)

    build_submission, ManifestReceiptRegistry, AdmissibilityRequest, _evaluate, ManifestedTransactionResult = _load_stegcore()
    ManifestRouteCarrier, RouteCarrierError, build_route_manifest, default_validation_route = _load_route_carrier()
    try:
        admissibility_request = AdmissibilityRequest.model_validate(steggate_body)
    except Exception as exc:
        raise PublicInspectionRuntimeError(f"invalid StegCore admissibility request: {exc}") from exc

    registry = ManifestReceiptRegistry()
    state: dict[str, Any] = {}
    route_manifest = build_route_manifest(
        execution_provenance=provenance,
        route=default_validation_route(),
        source="StegVerse-org/StegVerse-SDK:public-inspection",
        purpose="production-lane-evaluator-validation",
    )

    def sink(event: dict[str, Any]) -> Mapping[str, Any]:
        return organization_ledger_sink(route_manifest["route_manifest_id"], event)

    def stegcore_handler(active_manifest: dict[str, Any], _payload: Any) -> dict[str, Any]:
        result = _run_deployed_stegcore(core_url, active_manifest, admissibility_request, input_data, normalized, provenance, ManifestedTransactionResult)
        record = registry.register(result)
        evidence = registry.evidence_package(record.manifest_receipt_id)
        evidence["ecosystem_route_link"] = {
            "route_manifest_id": active_manifest["route_manifest_id"],
            "transaction_id": active_manifest["transaction_id"],
            "execution_provenance": dict(provenance),
            "route_receipt_chain_head_at_exact_run_custody": active_manifest.get("receipt_chain_head"),
            "stegcore_service_url": core_url,
            "stegcore_runtime_identity": core_identity.get("runtime_identity"),
        }
        evaluation = result.execution_observation.get("evaluation") or {}
        state.update({"result": result, "record": record, "evidence": evidence, "evaluation": evaluation})
        return {
            "governance_state": evaluation.get("disposition"),
            "manifest_receipt_id": record.manifest_receipt_id,
            "transaction_id": record.transaction_id,
            "stegcore_chain_verified": bool(result.chain_verified),
            "exact_run_receipt_closure": "ORGANIZATION_LEDGER_ROUTE_EVENT",
            "external_side_effect": False,
            "service_execution_surface": core_url,
        }

    try:
        route_result = ManifestRouteCarrier(route_manifest, sink).run(
            {"request_id": normalized["request_id"], "input_data": input_data},
            {"stegcore": stegcore_handler},
        )
    except RouteCarrierError as exc:
        raise PublicInspectionRuntimeError(str(exc)) from exc

    record, result, evaluation = state["record"], state["result"], state["evaluation"]
    # Released after closure: optional downstream Master Records recording.
    if master_records is None:
        recording = {
            "status": "NOT_CONFIGURED",
            "recorder_role": "DOWNSTREAM_RELEASED_BATCH_RECEIPT_RECORDING",
            "gates_completion": False,
            "authority_effect": "NONE_EVIDENCE_ONLY",
        }
    else:
        recording = _record_downstream(master_records[0], master_records[1], record, state["evidence"], build_submission)
    return {
        "schema": "stegverse.public-inspection-production-validation-result.v2",
        "request_id": normalized["request_id"],
        "case_profile": normalized["case_profile"],
        "runtime_mode": "PRODUCTION_LANE_VALIDATION_TEST",
        "execution_provenance": provenance,
        "stegcore_service_url": core_url,
        "stegcore_runtime_identity": core_identity.get("runtime_identity"),
        "route_manifest_id": route_result["route_manifest_id"],
        "route_transition_count": route_result["route_transition_count"],
        "route_receipt_chain_head": route_result["receipt_chain_head"],
        "route_manifest": route_result["route_manifest"],
        "governance_state": evaluation.get("disposition"),
        "manifest_receipt_id": record.manifest_receipt_id,
        "transaction_id": record.transaction_id,
        "transaction_identity_continuous": record.transaction_id == route_result["transaction_id"] == result.transaction_id,
        "chain_verified": bool(result.chain_verified),
        "consequence_executor_invoked": bool(result.execution_observation.get("executor_invoked")),
        "external_side_effect": False,
        "organization_ledger_closure": {
            "status": "RECORDED",
            "route_receipt_chain_head": route_result["receipt_chain_head"],
            "closes_transition": True,
        },
        "master_records_recording": recording,
        ORGANIZATION_RECORD_STATUS_FIELD: recording["status"],
        ORGANIZATION_RECORD_RECEIPT_FIELD: recording.get("receipt"),
        "ecosystem_commit_status": "RECORDED",
        "locator_grants_authority": False,
        "github_grants_runtime_authority": False,
    }


def replay_manifest_receipt(manifest_receipt_id: str, *, master_records_url: str | None = None, master_records_token: str | None = None) -> dict[str, Any]:
    base_url, token = _master_records_config(master_records_url, master_records_token)
    rid = manifest_receipt_id.strip().upper()
    operation_id = "OP-REPLAY-" + uuid.uuid4().hex.upper()
    receipts = [_record_operation_event(base_url, token, rid, operation_id, "REPLAY", 0, "REQUESTED", details={"requested_artifact": "replay"})]
    body = _get_json(f"{base_url}/api/master-records/manifest-receipts/{rid}", token)
    receipts.append(_record_operation_event(base_url, token, rid, operation_id, "REPLAY", 1, "SOURCE_RESOLVED", details={"source_master_record_sha256": body.get("master_record_sha256")}))
    package = body.get("evidence_package")
    if not isinstance(package, Mapping):
        raise PublicInspectionRuntimeError("retained evidence package missing")
    provenance = _source_execution_provenance(package)
    request_body = ((package.get("manifest") or {}).get("metadata") or {}).get("governance_request")
    if not isinstance(request_body, Mapping):
        raise PublicInspectionRuntimeError("retained run predates replay-capable governance_request custody")
    _build, _Registry, AdmissibilityRequest, evaluate_admissibility, _Manifested = _load_stegcore()
    replay_eval = evaluate_admissibility(AdmissibilityRequest.model_validate(request_body))
    original = ((package.get("execution_observation") or {}).get("evaluation") or {})
    artifact = {
        "schema": "stegverse.public-inspection-replay.v2",
        "operation_id": operation_id,
        "manifest_receipt_id": rid,
        "source_execution_provenance": provenance,
        "source_route_manifest_id": (package.get("ecosystem_route_link") or {}).get("route_manifest_id"),
        "original_disposition": str(original.get("disposition") or ""),
        "replay_disposition": replay_eval.disposition,
        "deterministic_disposition_match": replay_eval.disposition == str(original.get("disposition") or ""),
        "candidate_identity_match": replay_eval.candidate_hash == str(original.get("candidate_hash") or ""),
        "consequence_reexecuted": False,
        "original_record_mutated": False,
        "master_records_source": True,
        "replay_grants_authority": False,
    }
    receipts.append(_record_operation_event(base_url, token, rid, operation_id, "REPLAY", 2, "EVALUATED", artifact=artifact))
    receipts.append(_record_operation_event(base_url, token, rid, operation_id, "REPLAY", 3, "RETURNED", artifact=artifact, details={"return_target": "sdk_caller", "source_lane_class": provenance.get("lane_class")}))
    artifact["master_records_operation_receipts"] = receipts
    artifact["operation_events_recorded_downstream"] = all(r.get("status") != "NOT_RECORDED" for r in receipts)
    artifact["operation_event_recording_gates_operation"] = False
    return artifact


def reconstruct_manifest_receipt(manifest_receipt_id: str, *, master_records_url: str | None = None, master_records_token: str | None = None) -> dict[str, Any]:
    base_url, token = _master_records_config(master_records_url, master_records_token)
    rid = manifest_receipt_id.strip().upper()
    operation_id = "OP-RECONSTRUCT-" + uuid.uuid4().hex.upper()
    receipts = [_record_operation_event(base_url, token, rid, operation_id, "RECONSTRUCT", 0, "REQUESTED", details={"requested_artifact": "reconstruction"})]
    source = _get_json(f"{base_url}/api/master-records/manifest-receipts/{rid}", token)
    receipts.append(_record_operation_event(base_url, token, rid, operation_id, "RECONSTRUCT", 1, "SOURCE_RESOLVED", details={"source_master_record_sha256": source.get("master_record_sha256")}))
    source_package = source.get("evidence_package")
    if not isinstance(source_package, Mapping):
        raise PublicInspectionRuntimeError("retained evidence package missing")
    provenance = _source_execution_provenance(source_package)
    body = _get_json(f"{base_url}/api/master-records/manifest-receipts/{rid}/reconstruction", token)
    if body.get("consequence_reexecuted") is not False:
        raise PublicInspectionRuntimeError("reconstruction boundary invalid: consequence_reexecuted must be false")
    artifact = dict(body)
    artifact["operation_id"] = operation_id
    artifact["source_execution_provenance"] = provenance
    artifact["source_route_manifest_id"] = (source_package.get("ecosystem_route_link") or {}).get("route_manifest_id")
    receipts.append(_record_operation_event(base_url, token, rid, operation_id, "RECONSTRUCT", 2, "ARTIFACT_DERIVED", artifact=artifact))
    receipts.append(_record_operation_event(base_url, token, rid, operation_id, "RECONSTRUCT", 3, "RETURNED", artifact=artifact, details={"return_target": "sdk_caller", "source_lane_class": provenance.get("lane_class")}))
    artifact["master_records_operation_receipts"] = receipts
    artifact["operation_events_recorded_downstream"] = all(r.get("status") != "NOT_RECORDED" for r in receipts)
    artifact["operation_event_recording_gates_operation"] = False
    return artifact


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run through manifested Core-Lite + deployed StegCore (Organization ledger sink required); replay or reconstruct from the released record in Master Records")
    parser.add_argument("operation", choices=("run", "replay", "reconstruct"))
    parser.add_argument("target")
    parser.add_argument("--master-records-url")
    parser.add_argument("--master-records-token")
    parser.add_argument("--stegcore-url")
    args = parser.parse_args(argv)
    try:
        if args.operation == "run":
            # The CLI binds no Organization ledger sink, so it returns the six-field refusal;
            # deployments call run_public_inspection_test with their ledger append.
            result = run_public_inspection_test(load_public_inspection_request(args.target), master_records_url=args.master_records_url, master_records_token=args.master_records_token, stegcore_url=args.stegcore_url)
            if result.get("failure_code"):
                print(json.dumps(result, indent=2, sort_keys=True))
                return 2
        elif args.operation == "replay":
            result = replay_manifest_receipt(args.target, master_records_url=args.master_records_url, master_records_token=args.master_records_token)
        else:
            result = reconstruct_manifest_receipt(args.target, master_records_url=args.master_records_url, master_records_token=args.master_records_token)
    except (PublicInspectionRequestError, PublicInspectionRuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
