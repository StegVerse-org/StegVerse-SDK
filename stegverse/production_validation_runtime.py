"""Production-lane evaluator validation through manifested Core-Lite routing, StegCore, and Master Records."""
from __future__ import annotations

import argparse, hashlib, json, os, uuid
from typing import Any, Mapping
import requests
from .public_inspection import PublicInspectionRequestError, load_public_inspection_request, validate_public_inspection_request


class PublicInspectionRuntimeError(RuntimeError): pass


def _canonical_hash(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _load_stegcore():
    try:
        from stegcore.manifest_receipt_provider import build_master_records_submission
        from stegcore.manifest_receipts import ManifestReceiptRegistry
        from stegcore.steggate import AdmissibilityRequest, evaluate_admissibility
        from stegcore.transaction_lifecycle import TransactionLedger, run_manifested_transaction
    except ImportError as exc: raise PublicInspectionRuntimeError("StegCore is required for governed execution. Install the current governed-test dependency.") from exc
    return build_master_records_submission, ManifestReceiptRegistry, AdmissibilityRequest, evaluate_admissibility, TransactionLedger, run_manifested_transaction


def _load_route_carrier():
    try:
        from core_lite.transaction_route import ManifestRouteCarrier, RouteCarrierError, build_route_manifest, default_validation_route
    except ImportError as exc: raise PublicInspectionRuntimeError("Core-Lite manifested route carrier is required for production-lane validation.") from exc
    return ManifestRouteCarrier, RouteCarrierError, build_route_manifest, default_validation_route


def _runtime_input(request: Mapping[str, Any]) -> tuple[Mapping[str, Any], Any]:
    input_block = request.get("input")
    if not isinstance(input_block, Mapping): raise PublicInspectionRuntimeError("public inspection input must be an object")
    steggate_request = input_block.get("steggate_request")
    if not isinstance(steggate_request, Mapping): raise PublicInspectionRuntimeError("governed execution requires input.steggate_request containing a canonical StegCore AdmissibilityRequest")
    return steggate_request, input_block.get("input_data", {})


def _execution_provenance(request: Mapping[str, Any]) -> dict[str, Any]:
    provenance = request.get("execution_provenance")
    if not isinstance(provenance, Mapping): raise PublicInspectionRuntimeError("execution_provenance is required for governed validation")
    lane_class = str(provenance.get("lane_class") or "")
    if lane_class not in {"PRODUCTION_VALIDATION", "ENCLOSED_DEMO_TEST"}: raise PublicInspectionRuntimeError("execution_provenance.lane_class is invalid")
    return dict(provenance)


def _source_execution_provenance(package: Mapping[str, Any]) -> dict[str, Any]:
    metadata = ((package.get("manifest") or {}).get("metadata") or {})
    provenance = metadata.get("execution_provenance")
    if not isinstance(provenance, Mapping): raise PublicInspectionRuntimeError("retained run predates execution-provenance custody")
    return dict(provenance)


def _master_records_config(base_url: str | None = None, token: str | None = None) -> tuple[str, str]:
    url = (base_url or os.getenv("MASTER_RECORDS_URL") or "").rstrip("/"); auth = token or os.getenv("MASTER_RECORDS_AUTH_TOKEN") or ""
    if not url or not auth: raise PublicInspectionRuntimeError("Master Records custody is required. Configure MASTER_RECORDS_URL and MASTER_RECORDS_AUTH_TOKEN.")
    return url, auth


def _headers(token: str) -> dict[str, str]: return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _preflight_master_records(base_url: str, token: str) -> None:
    try:
        exact = requests.get(f"{base_url}/api/master-records/manifest-receipts/{'MR-' + '0'*64}", headers=_headers(token), timeout=10)
        route = requests.get(f"{base_url}/api/master-records/manifest-routes/{'MF-' + '0'*64}/events", headers=_headers(token), timeout=10)
    except requests.RequestException as exc: raise PublicInspectionRuntimeError(f"Master Records preflight failed: {exc}") from exc
    if exact.status_code not in (200, 404): raise PublicInspectionRuntimeError(f"Master Records exact-run custody route is not admitted: HTTP {exact.status_code}")
    if route.status_code != 200: raise PublicInspectionRuntimeError(f"Master Records manifested-route custody route is not admitted: HTTP {route.status_code}")


def _retain_in_master_records(base_url: str, token: str, record: Any, evidence: Mapping[str, Any], build_submission: Any) -> dict[str, Any]:
    payload = build_submission(record, evidence)
    try: response = requests.post(f"{base_url}/api/master-records/manifest-receipts", headers=_headers(token), json=payload, timeout=30)
    except requests.RequestException as exc: raise PublicInspectionRuntimeError(f"Master Records custody failed: {exc}") from exc
    if response.status_code not in (200, 201): raise PublicInspectionRuntimeError(f"Master Records custody failed: HTTP {response.status_code}: {response.text[:500]}")
    body = response.json()
    if body.get("custody_status") != "RECORDED": raise PublicInspectionRuntimeError("Master Records did not confirm RECORDED custody")
    return body


def _record_route_event(base_url: str, token: str, route_manifest_id: str, event: Mapping[str, Any]) -> dict[str, Any]:
    payload = {"schema": "stegverse.master-records.manifest-route-event-submission.v1", "event": dict(event), "custody_requested": True, "authority_requested": False}
    try: response = requests.post(f"{base_url}/api/master-records/manifest-routes/{route_manifest_id}/events", headers=_headers(token), json=payload, timeout=30)
    except requests.RequestException as exc: raise PublicInspectionRuntimeError(f"Master Records route custody failed: {exc}") from exc
    if response.status_code not in (200, 201): raise PublicInspectionRuntimeError(f"Master Records route custody failed: HTTP {response.status_code}: {response.text[:500]}")
    body = response.json()
    if body.get("custody_status") != "RECORDED": raise PublicInspectionRuntimeError("Master Records did not record manifested-route transition")
    return body


def _get_json(url: str, token: str) -> dict[str, Any]:
    try: response = requests.get(url, headers=_headers(token), timeout=30)
    except requests.RequestException as exc: raise PublicInspectionRuntimeError(f"Master Records lookup failed: {exc}") from exc
    if response.status_code != 200: raise PublicInspectionRuntimeError(f"Master Records lookup failed: HTTP {response.status_code}: {response.text[:500]}")
    body = response.json()
    if not isinstance(body, dict): raise PublicInspectionRuntimeError("Master Records returned a non-object response")
    return body


def _record_operation_event(base_url: str, token: str, manifest_receipt_id: str, operation_id: str, operation: str, sequence: int, event_type: str, *, details: Mapping[str, Any] | None = None, artifact: Mapping[str, Any] | None = None) -> dict[str, Any]:
    event = {"operation_id": operation_id, "operation": operation, "sequence": sequence, "event_type": event_type, "details": dict(details or {}), "artifact_sha256": _canonical_hash(artifact) if artifact is not None else None, "authority_granted": False}
    payload = {"schema": "stegverse.master-records.manifest-operation-event-submission.v1", "event": event, "custody_requested": True, "authority_requested": False}
    try: response = requests.post(f"{base_url}/api/master-records/manifest-receipts/{manifest_receipt_id}/operations", headers=_headers(token), json=payload, timeout=30)
    except requests.RequestException as exc: raise PublicInspectionRuntimeError(f"Master Records operation custody failed: {exc}") from exc
    if response.status_code not in (200, 201): raise PublicInspectionRuntimeError(f"Master Records operation custody failed: HTTP {response.status_code}: {response.text[:500]}")
    body = response.json()
    if body.get("custody_status") != "RECORDED": raise PublicInspectionRuntimeError("Master Records did not record operation transition")
    return body


def run_public_inspection_test(request: Mapping[str, Any], *, master_records_url: str | None = None, master_records_token: str | None = None) -> dict[str, Any]:
    normalized = validate_public_inspection_request(request); steggate_body, input_data = _runtime_input(normalized); provenance = _execution_provenance(normalized)
    if provenance.get("lane_class") != "PRODUCTION_VALIDATION": raise PublicInspectionRuntimeError("this runtime is the production-lane validation path; enclosed demo/test requests must remain on their declared demo/test surface")
    base_url, token = _master_records_config(master_records_url, master_records_token); _preflight_master_records(base_url, token)
    build_submission, ManifestReceiptRegistry, AdmissibilityRequest, _evaluate, TransactionLedger, run_manifested_transaction = _load_stegcore()
    ManifestRouteCarrier, RouteCarrierError, build_route_manifest, default_validation_route = _load_route_carrier()
    try: admissibility_request = AdmissibilityRequest.model_validate(steggate_body)
    except Exception as exc: raise PublicInspectionRuntimeError(f"invalid StegCore admissibility request: {exc}") from exc
    registry = ManifestReceiptRegistry(); ledger = TransactionLedger(); state: dict[str, Any] = {}
    route_manifest = build_route_manifest(execution_provenance=provenance, route=default_validation_route(), source="StegVerse-org/StegVerse-SDK:public-inspection", purpose="production-lane-evaluator-validation")
    def sink(event: dict[str, Any]) -> Mapping[str, Any]: return _record_route_event(base_url, token, route_manifest["route_manifest_id"], event)
    def simulated_executor() -> dict[str, Any]: return {"status": "SIMULATED_TEST_CONSEQUENCE", "external_side_effect": False, "request_id": normalized["request_id"]}
    def stegcore_handler(active_manifest: dict[str, Any], _payload: Any) -> dict[str, Any]:
        result = run_manifested_transaction(admissibility_request, simulated_executor, input_data=input_data, source="stegverse-sdk:production-validation", subject=f"public-inspection:{normalized['request_id']}", ledger=ledger, transaction_id=active_manifest["transaction_id"], metadata={"public_inspection_request_id": normalized["request_id"], "case_profile": normalized["case_profile"], "test_mode": True, "external_side_effects_enabled": False, "execution_provenance": provenance, "route_manifest_id": active_manifest["route_manifest_id"], "route_receipt_chain_head_at_stegcore_entry": active_manifest.get("receipt_chain_head"), "governance_request": admissibility_request.model_dump(mode="json", exclude_none=False)})
        record = registry.register(result); evidence = registry.evidence_package(record.manifest_receipt_id); evidence["ecosystem_route_link"] = {"route_manifest_id": active_manifest["route_manifest_id"], "transaction_id": active_manifest["transaction_id"], "execution_provenance": provenance, "route_receipt_chain_head_at_exact_run_custody": active_manifest.get("receipt_chain_head")}
        custody = _retain_in_master_records(base_url, token, record, evidence, build_submission); evaluation = result.execution_observation.get("evaluation") or {}
        state.update({"result": result, "record": record, "custody": custody, "evaluation": evaluation})
        return {"governance_state": evaluation.get("disposition"), "manifest_receipt_id": record.manifest_receipt_id, "transaction_id": record.transaction_id, "stegcore_chain_verified": bool(result.chain_verified), "exact_run_custody_status": custody.get("custody_status"), "external_side_effect": False}
    try: route_result = ManifestRouteCarrier(route_manifest, sink).run({"request_id": normalized["request_id"], "input_data": input_data}, {"stegcore": stegcore_handler})
    except RouteCarrierError as exc: raise PublicInspectionRuntimeError(str(exc)) from exc
    record, result, custody, evaluation = state["record"], state["result"], state["custody"], state["evaluation"]
    return {"schema": "stegverse.public-inspection-production-validation-result.v1", "request_id": normalized["request_id"], "case_profile": normalized["case_profile"], "runtime_mode": "PRODUCTION_LANE_VALIDATION_TEST", "execution_provenance": provenance, "route_manifest_id": route_result["route_manifest_id"], "route_transition_count": route_result["route_transition_count"], "route_receipt_chain_head": route_result["receipt_chain_head"], "route_manifest": route_result["route_manifest"], "governance_state": evaluation.get("disposition"), "manifest_receipt_id": record.manifest_receipt_id, "transaction_id": record.transaction_id, "transaction_identity_continuous": record.transaction_id == route_result["transaction_id"] == result.transaction_id, "chain_verified": bool(result.chain_verified), "consequence_executor_invoked": bool(result.execution_observation.get("executor_invoked")), "external_side_effect": False, "master_records_custody_status": custody.get("custody_status"), "master_records_custody_receipt": custody, "ecosystem_commit_status": "RECORDED", "locator_grants_authority": False, "github_grants_runtime_authority": False}


def replay_manifest_receipt(manifest_receipt_id: str, *, master_records_url: str | None = None, master_records_token: str | None = None) -> dict[str, Any]:
    base_url, token = _master_records_config(master_records_url, master_records_token); rid = manifest_receipt_id.strip().upper(); operation_id = "OP-REPLAY-" + uuid.uuid4().hex.upper()
    receipts = [_record_operation_event(base_url, token, rid, operation_id, "REPLAY", 0, "REQUESTED", details={"requested_artifact": "replay"})]
    body = _get_json(f"{base_url}/api/master-records/manifest-receipts/{rid}", token); receipts.append(_record_operation_event(base_url, token, rid, operation_id, "REPLAY", 1, "SOURCE_RESOLVED", details={"source_master_record_sha256": body.get("master_record_sha256")}))
    package = body.get("evidence_package")
    if not isinstance(package, Mapping): raise PublicInspectionRuntimeError("retained evidence package missing")
    provenance = _source_execution_provenance(package); request_body = ((package.get("manifest") or {}).get("metadata") or {}).get("governance_request")
    if not isinstance(request_body, Mapping): raise PublicInspectionRuntimeError("retained run predates replay-capable governance_request custody")
    _build, _Registry, AdmissibilityRequest, evaluate_admissibility, _Ledger, _run = _load_stegcore(); replay_eval = evaluate_admissibility(AdmissibilityRequest.model_validate(request_body)); original = ((package.get("execution_observation") or {}).get("evaluation") or {})
    artifact = {"schema": "stegverse.public-inspection-replay.v2", "operation_id": operation_id, "manifest_receipt_id": rid, "source_execution_provenance": provenance, "source_route_manifest_id": (package.get("ecosystem_route_link") or {}).get("route_manifest_id"), "original_disposition": str(original.get("disposition") or ""), "replay_disposition": replay_eval.disposition, "deterministic_disposition_match": replay_eval.disposition == str(original.get("disposition") or ""), "candidate_identity_match": replay_eval.candidate_hash == str(original.get("candidate_hash") or ""), "consequence_reexecuted": False, "original_record_mutated": False, "master_records_source": True, "replay_grants_authority": False}
    receipts.append(_record_operation_event(base_url, token, rid, operation_id, "REPLAY", 2, "EVALUATED", artifact=artifact)); receipts.append(_record_operation_event(base_url, token, rid, operation_id, "REPLAY", 3, "RETURNED", artifact=artifact, details={"return_target": "sdk_caller", "source_lane_class": provenance.get("lane_class")})); artifact["master_records_operation_receipts"] = receipts; artifact["operation_transition_custody_status"] = "RECORDED"; return artifact


def reconstruct_manifest_receipt(manifest_receipt_id: str, *, master_records_url: str | None = None, master_records_token: str | None = None) -> dict[str, Any]:
    base_url, token = _master_records_config(master_records_url, master_records_token); rid = manifest_receipt_id.strip().upper(); operation_id = "OP-RECONSTRUCT-" + uuid.uuid4().hex.upper()
    receipts = [_record_operation_event(base_url, token, rid, operation_id, "RECONSTRUCT", 0, "REQUESTED", details={"requested_artifact": "reconstruction"})]
    source = _get_json(f"{base_url}/api/master-records/manifest-receipts/{rid}", token); receipts.append(_record_operation_event(base_url, token, rid, operation_id, "RECONSTRUCT", 1, "SOURCE_RESOLVED", details={"source_master_record_sha256": source.get("master_record_sha256")}))
    source_package = source.get("evidence_package")
    if not isinstance(source_package, Mapping): raise PublicInspectionRuntimeError("retained evidence package missing")
    provenance = _source_execution_provenance(source_package); body = _get_json(f"{base_url}/api/master-records/manifest-receipts/{rid}/reconstruction", token)
    if body.get("consequence_reexecuted") is not False: raise PublicInspectionRuntimeError("reconstruction boundary invalid: consequence_reexecuted must be false")
    artifact = dict(body); artifact["operation_id"] = operation_id; artifact["source_execution_provenance"] = provenance; artifact["source_route_manifest_id"] = (source_package.get("ecosystem_route_link") or {}).get("route_manifest_id"); receipts.append(_record_operation_event(base_url, token, rid, operation_id, "RECONSTRUCT", 2, "ARTIFACT_DERIVED", artifact=artifact)); receipts.append(_record_operation_event(base_url, token, rid, operation_id, "RECONSTRUCT", 3, "RETURNED", artifact=artifact, details={"return_target": "sdk_caller", "source_lane_class": provenance.get("lane_class")})); artifact["master_records_operation_receipts"] = receipts; artifact["operation_transition_custody_status"] = "RECORDED"; return artifact


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run, replay, or reconstruct through manifested Core-Lite + StegCore + Master Records")
    parser.add_argument("operation", choices=("run", "replay", "reconstruct")); parser.add_argument("target"); parser.add_argument("--master-records-url"); parser.add_argument("--master-records-token"); args = parser.parse_args(argv)
    try:
        if args.operation == "run": result = run_public_inspection_test(load_public_inspection_request(args.target), master_records_url=args.master_records_url, master_records_token=args.master_records_token)
        elif args.operation == "replay": result = replay_manifest_receipt(args.target, master_records_url=args.master_records_url, master_records_token=args.master_records_token)
        else: result = reconstruct_manifest_receipt(args.target, master_records_url=args.master_records_url, master_records_token=args.master_records_token)
    except (PublicInspectionRequestError, PublicInspectionRuntimeError, ValueError) as exc: print(f"ERROR: {exc}"); return 2
    print(json.dumps(result, indent=2, sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
