"""Sovereign production-validation path using canonical merged implementations only."""
from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from typing import Any, Callable, Mapping

from .public_inspection import load_public_inspection_request, validate_public_inspection_request


class SovereignValidationError(RuntimeError):
    pass


def _components():
    try:
        from core_lite.transaction_route import ManifestRouteCarrier, build_route_manifest, default_validation_route
        from services.manifest_receipt_custody import ManifestReceiptCustody
        from stegcore.manifest_receipt_provider import build_master_records_submission
        from stegcore.manifest_receipts import ManifestReceiptRegistry
        from stegcore.steggate import AdmissibilityRequest, evaluate_admissibility
        from stegcore.transaction_lifecycle import TransactionLedger, run_manifested_transaction
    except ImportError as exc:
        raise SovereignValidationError(
            "Canonical StegCore, Core-Lite and Master Records packages are required; no parallel evaluator is provided."
        ) from exc
    return (ManifestRouteCarrier, build_route_manifest, default_validation_route,
            ManifestReceiptCustody, build_master_records_submission, ManifestReceiptRegistry,
            AdmissibilityRequest, evaluate_admissibility, TransactionLedger, run_manifested_transaction)


def _prov(request: Mapping[str, Any], host_identity: str) -> dict[str, Any]:
    raw = request.get("execution_provenance")
    if not isinstance(raw, Mapping) or raw.get("lane_class") != "PRODUCTION_VALIDATION":
        raise SovereignValidationError("sovereign runtime accepts only PRODUCTION_VALIDATION manifests")
    value = dict(raw)
    value.update({
        "routing_surface": "CANONICAL_PRODUCTION",
        "execution_host_class": "SOVEREIGN_LOCAL",
        "execution_host_identity": host_identity,
        "third_party_host_required": False,
    })
    return value


def run_sovereign_validation(
    request: Mapping[str, Any],
    *,
    custody_db: str | Path,
    host_identity: str = "stegverse-sovereign-local",
    consequence_executor: Callable[[], Mapping[str, Any]] | None = None,
    consequence_metadata: Mapping[str, Any] | None = None,
    route_source: str = "StegVerse-SDK:sovereign-validation",
    route_purpose: str = "production-lane-evaluator-validation",
) -> dict[str, Any]:
    """Run the canonical manifested transaction and custody path.

    ``consequence_executor`` is an optional bounded operation supplied by an SDK
    integration test. It is invoked only by the canonical StegCore transaction
    lifecycle when the governance disposition permits execution. The SDK does not
    introduce a second evaluator, receipt authority, or custody path.
    """
    normalized = validate_public_inspection_request(request)
    input_block = normalized.get("input")
    if not isinstance(input_block, Mapping) or not isinstance(input_block.get("steggate_request"), Mapping):
        raise SovereignValidationError("input.steggate_request is required")
    (Carrier, build_route, default_route, Custody, build_submission, Registry,
     Request, _evaluate, Ledger, run_tx) = _components()
    provenance = _prov(normalized, host_identity)
    custody = Custody(custody_db)
    registry, ledger = Registry(), Ledger()
    request_model = Request.model_validate(input_block["steggate_request"])
    input_data = input_block.get("input_data", {})
    route_manifest = build_route(execution_provenance=provenance, route=default_route(),
                                 source=route_source, purpose=route_purpose)
    state: dict[str, Any] = {}
    consequence_enabled = consequence_executor is not None

    def sink(event: dict[str, Any]) -> Mapping[str, Any]:
        body = dict(event)
        body["route_manifest_id"] = route_manifest["route_manifest_id"]
        recorded = custody.record_route_event(body)
        return {"custody_status": "RECORDED", "event": recorded}

    def executor() -> dict[str, Any]:
        if consequence_executor is None:
            return {"status": "SIMULATED_TEST_CONSEQUENCE", "external_side_effect": False,
                    "request_id": normalized["request_id"]}
        produced = consequence_executor()
        if not isinstance(produced, Mapping):
            raise SovereignValidationError("bounded consequence executor must return a mapping")
        result = dict(produced)
        result.setdefault("external_side_effect", True)
        result.setdefault("request_id", normalized["request_id"])
        return result

    def steggate_handler(active_manifest: dict[str, Any], _payload: Any) -> dict[str, Any]:
        metadata = {
            "public_inspection_request_id": normalized["request_id"],
            "case_profile": normalized["case_profile"],
            "execution_provenance": provenance,
            "route_manifest_id": active_manifest["route_manifest_id"],
            "route_receipt_chain_head_at_stegcore_entry": active_manifest.get("receipt_chain_head"),
            "governance_request": request_model.model_dump(mode="json", exclude_none=False),
            "test_mode": True,
            "external_side_effects_enabled": consequence_enabled,
        }
        if consequence_metadata:
            metadata["bounded_consequence"] = dict(consequence_metadata)
        result = run_tx(
            request_model, executor, input_data=input_data,
            source="stegverse-sdk:sovereign-production-validation",
            subject=f"public-inspection:{normalized['request_id']}", ledger=ledger,
            transaction_id=active_manifest["transaction_id"],
            metadata=metadata,
            capability_surface={"actions_exposed": [request_model.candidate.action],
                                "execution_mode": "governed" if consequence_enabled else "manual",
                                "requires_governed_commit": True},
            authority_resolution={"status": "approved", "basis_invalidated_by_action": False},
        )
        record = registry.register(result)
        evidence = registry.evidence_package(record.manifest_receipt_id)
        evidence["ecosystem_route_link"] = {
            "route_manifest_id": active_manifest["route_manifest_id"],
            "transaction_id": active_manifest["transaction_id"],
            "execution_provenance": provenance,
            "route_receipt_chain_head_at_exact_run_custody": active_manifest.get("receipt_chain_head"),
        }
        submission = build_submission(record, evidence)
        retained = custody.register(submission["evidence_package"])
        state.update(result=result, record=record, retained=retained)
        observation = result.execution_observation or {}
        execution_result = observation.get("result") if isinstance(observation, Mapping) else None
        external_effect = bool(execution_result.get("external_side_effect")) if isinstance(execution_result, Mapping) else False
        return {"governance_state": observation["evaluation"]["disposition"],
                "manifest_receipt_id": record.manifest_receipt_id,
                "transaction_id": record.transaction_id,
                "stegcore_chain_verified": result.chain_verified,
                "exact_run_custody_status": "RECORDED", "external_side_effect": external_effect}

    route_result = Carrier(route_manifest, sink).run(
        {"request_id": normalized["request_id"], "input_data": input_data},
        {"stegcore": steggate_handler},
    )
    result, record = state["result"], state["record"]
    trace = custody.route_events(route_result["route_manifest_id"])
    observation = result.execution_observation or {}
    execution_result = observation.get("result") if isinstance(observation, Mapping) else None
    external_effect = bool(execution_result.get("external_side_effect")) if isinstance(execution_result, Mapping) else False
    output = {
        "schema": "stegverse.sovereign-production-validation-result.v1",
        "request_id": normalized["request_id"], "case_profile": normalized["case_profile"],
        "execution_provenance": provenance,
        "transaction_id": record.transaction_id,
        "route_manifest_id": route_result["route_manifest_id"],
        "route_receipt_ids": [e["route_receipt_id"] for e in trace],
        "route_transition_count": len(trace),
        "route_receipt_chain_head": route_result["receipt_chain_head"],
        "manifest_receipt_id": record.manifest_receipt_id,
        "governance_state": observation["evaluation"]["disposition"],
        "chain_verified": bool(result.chain_verified),
        "transaction_identity_continuous": record.transaction_id == route_result["transaction_id"] == result.transaction_id,
        "master_records_custody_status": "RECORDED",
        "external_side_effect": external_effect,
        "third_party_host_required": False,
    }
    if isinstance(execution_result, Mapping):
        output["execution_result"] = dict(execution_result)
    return output


def replay_sovereign(manifest_receipt_id: str, *, custody_db: str | Path) -> dict[str, Any]:
    (_Carrier, _build, _route, Custody, _submit, _Registry, Request, evaluate, _Ledger, _run) = _components()
    custody = Custody(custody_db)
    rid = manifest_receipt_id.strip().upper()
    package = custody.evidence_package(rid)["evidence_package"]
    request_body = ((package.get("manifest") or {}).get("metadata") or {}).get("governance_request")
    if not isinstance(request_body, Mapping):
        raise SovereignValidationError("retained run has no governance_request")
    op_id = "OP-REPLAY-" + uuid.uuid4().hex.upper()
    receipts = []
    for seq, typ in ((0, "REQUESTED"), (1, "SOURCE_RESOLVED")):
        receipts.append(custody.record_operation_event({"source_manifest_receipt_id": rid,
            "operation_id": op_id, "operation": "REPLAY", "sequence": seq,
            "event_type": typ, "authority_granted": False}))
    replay_eval = evaluate(Request.model_validate(request_body))
    original = ((package.get("execution_observation") or {}).get("evaluation") or {})
    artifact = {"schema": "stegverse.sovereign-replay.v1", "operation_id": op_id,
        "manifest_receipt_id": rid, "original_disposition": original.get("disposition"),
        "replay_disposition": replay_eval.disposition,
        "deterministic_disposition_match": replay_eval.disposition == original.get("disposition"),
        "consequence_reexecuted": False, "original_record_mutated": False}
    for seq, typ in ((2, "EVALUATED"), (3, "RETURNED")):
        receipts.append(custody.record_operation_event({"source_manifest_receipt_id": rid,
            "operation_id": op_id, "operation": "REPLAY", "sequence": seq,
            "event_type": typ, "details": {"artifact": artifact}, "authority_granted": False}))
    artifact["operation_receipt_ids"] = [r["event_receipt_id"] for r in receipts]
    artifact["operation_transition_custody_status"] = "RECORDED"
    return artifact


def reconstruct_sovereign(manifest_receipt_id: str, *, custody_db: str | Path) -> dict[str, Any]:
    (_Carrier, _build, _route, Custody, _submit, _Registry, _Request, _eval, _Ledger, _run) = _components()
    custody = Custody(custody_db)
    rid = manifest_receipt_id.strip().upper()
    op_id = "OP-RECONSTRUCT-" + uuid.uuid4().hex.upper()
    receipts = []
    for seq, typ in ((0, "REQUESTED"), (1, "SOURCE_RESOLVED")):
        receipts.append(custody.record_operation_event({"source_manifest_receipt_id": rid,
            "operation_id": op_id, "operation": "RECONSTRUCT", "sequence": seq,
            "event_type": typ, "authority_granted": False}))
    artifact = custody.reconstruct(rid)
    for seq, typ in ((2, "ARTIFACT_DERIVED"), (3, "RETURNED")):
        receipts.append(custody.record_operation_event({"source_manifest_receipt_id": rid,
            "operation_id": op_id, "operation": "RECONSTRUCT", "sequence": seq,
            "event_type": typ, "authority_granted": False}))
    artifact["operation_id"] = op_id
    artifact["operation_receipt_ids"] = [r["event_receipt_id"] for r in receipts]
    artifact["operation_transition_custody_status"] = "RECORDED"
    return artifact


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Canonical StegVerse production validation without a third-party host")
    parser.add_argument("operation", choices=("run", "replay", "reconstruct"))
    parser.add_argument("target")
    parser.add_argument("--custody-db", default="./stegverse-master-records-validation.db")
    parser.add_argument("--host-identity", default="stegverse-sovereign-local")
    args = parser.parse_args(argv)
    if args.operation == "run":
        result = run_sovereign_validation(load_public_inspection_request(args.target), custody_db=args.custody_db, host_identity=args.host_identity)
    elif args.operation == "replay":
        result = replay_sovereign(args.target, custody_db=args.custody_db)
    else:
        result = reconstruct_sovereign(args.target, custody_db=args.custody_db)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
