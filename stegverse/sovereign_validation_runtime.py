"""Sovereign production-validation path using canonical merged implementations only."""
from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from pathlib import Path
from typing import Any, Callable, Mapping

from .public_inspection import load_public_inspection_request, validate_public_inspection_request
from .route_resolution import (
    CANONICAL_PRODUCTION_ROUTE_ID,
    governance_state_hash,
    validate_runtime_provenance,
)


class SovereignValidationError(RuntimeError):
    pass


TESTING_CONTRACT_VERSION = "stegverse.sdk-testing-noninterference.v1"


def _canonical_sha256(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest()


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


def _prov(
    request: Mapping[str, Any], host_identity: str, governance_request: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = request.get("execution_provenance")
    try:
        resolved = validate_runtime_provenance(raw)
    except ValueError as exc:
        raise SovereignValidationError(f"declared route rejected: {exc}") from exc
    if resolved["route_id"] != CANONICAL_PRODUCTION_ROUTE_ID:
        raise SovereignValidationError(
            f"declared route has no sovereign runtime binding here: {resolved['route_id']}"
        )
    actual_state_hash = governance_state_hash(governance_request)
    supplied_state_hash = raw.get("state_binding_hash") if isinstance(raw, Mapping) else None
    if supplied_state_hash is not None and supplied_state_hash != actual_state_hash:
        raise SovereignValidationError(
            "declared route state_binding_hash does not match the governance state supplied for execution"
        )
    value = dict(raw)
    value.update({
        "route_id": resolved["route_id"],
        "route_declaration_hash": resolved["route_declaration_hash"],
        "state_binding_hash": actual_state_hash,
        "execution_host_class": "SOVEREIGN_LOCAL",
        "execution_host_identity": host_identity,
        "third_party_host_required": False,
    })
    return value, resolved


def run_sovereign_validation(
    request: Mapping[str, Any],
    *,
    custody_db: str | Path,
    host_identity: str = "stegverse-sovereign-local",
    consequence_executor: Callable[[], Mapping[str, Any]] | None = None,
    consequence_metadata: Mapping[str, Any] | None = None,
    declared_execution_context: Mapping[str, Any] | None = None,
    route_source: str = "StegVerse-SDK:sovereign-validation",
    route_purpose: str = "production-lane-evaluator-validation",
) -> dict[str, Any]:
    """Run the exact published route established by the submitted manifest.

    ``consequence_executor`` is an optional bounded operation supplied by an SDK
    integration test. It is invoked only by the canonical StegCore transaction
    lifecycle when the governance disposition permits execution. The SDK does not
    introduce a second evaluator, receipt authority, or custody path.

    ``declared_execution_context`` is carried unchanged into the canonical
    StegCore transaction lifecycle. The SDK does not decide standing from that
    context. A StegCore runtime that requires standing must independently verify
    the bound evidence and fail closed before invoking the consequence.

    Evaluator WHAT/HOW/WHY declarations are retained as evidence metadata but are
    never inputs to the StegGate decision model. The runtime resolves the route
    declared by the manifest/request, verifies the governance-relevant state is
    bound to that route, and rejects unsupported routes rather than substituting
    another route.
    """
    normalized = validate_public_inspection_request(request)
    input_block = normalized.get("input")
    if not isinstance(input_block, Mapping) or not isinstance(input_block.get("steggate_request"), Mapping):
        raise SovereignValidationError("input.steggate_request is required")
    raw_governance_request = input_block["steggate_request"]
    (Carrier, build_route, default_route, Custody, build_submission, Registry,
     Request, _evaluate, Ledger, run_tx) = _components()
    provenance, resolved_route = _prov(normalized, host_identity, raw_governance_request)
    if resolved_route["runtime_binding"] != "core_lite.default_validation_route":
        raise SovereignValidationError(
            f"resolved route runtime binding is unavailable: {resolved_route['runtime_binding']}"
        )
    selected_route = default_route()
    custody = Custody(custody_db)
    registry, ledger = Registry(), Ledger()
    request_model = Request.model_validate(raw_governance_request)
    input_data = input_block.get("input_data", {})
    evaluation_declaration = normalized.get("evaluation_declaration")
    manifest_binding_hash = _canonical_sha256(normalized)
    governance_request_hash = _canonical_sha256(request_model.model_dump(mode="json", exclude_none=False))
    route_manifest = build_route(execution_provenance=provenance, route=selected_route,
                                 source=route_source, purpose=route_purpose)
    state: dict[str, Any] = {}
    consequence_enabled = consequence_executor is not None

    def sink(event: dict[str, Any]) -> Mapping[str, Any]:
        body = dict(event)
        body["route_manifest_id"] = route_manifest["route_manifest_id"]
        body["declared_route_id"] = resolved_route["route_id"]
        body["route_declaration_hash"] = resolved_route["route_declaration_hash"]
        body["state_binding_hash"] = provenance["state_binding_hash"]
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
            "evaluation_declaration": evaluation_declaration,
            "evaluation_declaration_is_decision_input": False,
            "requester_label_is_decision_input": False,
            "testing_contract_version": TESTING_CONTRACT_VERSION,
            "configuration_not_augmentation": True,
            "route_augmentation_permitted": False,
            "route_substitution_permitted": False,
            "route_substitution_occurred": False,
            "unsupported_capability_behavior": "REJECT_BEFORE_EXECUTION",
            "submitted_manifest_hash": manifest_binding_hash,
            "governance_request_hash": governance_request_hash,
            "declared_route_id": resolved_route["route_id"],
            "route_declaration_hash": resolved_route["route_declaration_hash"],
            "state_binding_hash": provenance["state_binding_hash"],
            "execution_provenance": provenance,
            "route_manifest_id": active_manifest["route_manifest_id"],
            "route_receipt_chain_head_at_stegcore_entry": active_manifest.get("receipt_chain_head"),
            "governance_request": request_model.model_dump(mode="json", exclude_none=False),
            "test_mode": True,
            "external_side_effects_enabled": consequence_enabled,
            "declared_execution_context_supplied": declared_execution_context is not None,
        }
        if consequence_metadata:
            metadata["bounded_consequence"] = dict(consequence_metadata)
        result = run_tx(
            request_model, executor, input_data=input_data,
            source="stegverse-sdk:sovereign-production-validation",
            subject=f"public-inspection:{normalized['request_id']}", ledger=ledger,
            transaction_id=active_manifest["transaction_id"],
            metadata=metadata,
            declared_execution_context=declared_execution_context,
            capability_surface={"actions_exposed": [request_model.candidate.action],
                                "execution_mode": "governed" if consequence_enabled else "manual",
                                "requires_governed_commit": True},
            authority_resolution={"status": "approved", "basis_invalidated_by_action": False},
        )
        record = registry.register(result)
        evidence = registry.evidence_package(record.manifest_receipt_id)
        evidence["ecosystem_route_link"] = {
            "declared_route_id": resolved_route["route_id"],
            "route_declaration_hash": resolved_route["route_declaration_hash"],
            "state_binding_hash": provenance["state_binding_hash"],
            "route_substitution_occurred": False,
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
        {
            "request_id": normalized["request_id"],
            "input_data": input_data,
            "declared_route_id": resolved_route["route_id"],
            "route_declaration_hash": resolved_route["route_declaration_hash"],
            "state_binding_hash": provenance["state_binding_hash"],
        },
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
        "evaluation_declaration": evaluation_declaration,
        "testing_contract_version": TESTING_CONTRACT_VERSION,
        "configuration_not_augmentation": True,
        "route_augmentation_permitted": False,
        "route_substitution_permitted": False,
        "route_substitution_occurred": False,
        "evaluator_identity_is_decision_input": False,
        "declared_expected_observation_is_decision_input": False,
        "unsupported_capability_behavior": "REJECT_BEFORE_EXECUTION",
        "submitted_manifest_hash": manifest_binding_hash,
        "governance_request_hash": governance_request_hash,
        "declared_route_id": resolved_route["route_id"],
        "route_declaration_hash": resolved_route["route_declaration_hash"],
        "state_binding_hash": provenance["state_binding_hash"],
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
        "declared_execution_context_consumed_by_canonical_runtime": declared_execution_context is not None,
    }
    if isinstance(execution_result, Mapping):
        output["execution_result"] = dict(execution_result)
    output["result_binding_hash"] = _canonical_sha256(output)
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