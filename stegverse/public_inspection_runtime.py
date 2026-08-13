"""Trusted local TEST runtime for bounded public inspection requests.

This module accepts the same bounded public-inspection schema and executes an
embedded canonical StegCore AdmissibilityRequest through the canonical
manifested-transaction path. TEST mode uses a side-effect-free executor.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from .public_inspection import PublicInspectionRequestError, load_public_inspection_request, validate_public_inspection_request


class PublicInspectionRuntimeError(RuntimeError):
    pass


def _load_stegcore():
    try:
        from stegcore.manifest_receipts import ManifestReceiptRegistry
        from stegcore.steggate import AdmissibilityRequest
        from stegcore.transaction_lifecycle import TransactionLedger, run_manifested_transaction
    except ImportError as exc:
        raise PublicInspectionRuntimeError(
            "StegCore is required for governed TEST execution. Install the current StegVerse-Labs/StegCore checkout in this Python environment."
        ) from exc
    return ManifestReceiptRegistry, AdmissibilityRequest, TransactionLedger, run_manifested_transaction


def _runtime_input(request: Mapping[str, Any]) -> tuple[Mapping[str, Any], Any]:
    input_block = request.get("input")
    if not isinstance(input_block, Mapping):
        raise PublicInspectionRuntimeError("public inspection input must be an object")
    steggate_request = input_block.get("steggate_request")
    if not isinstance(steggate_request, Mapping):
        raise PublicInspectionRuntimeError(
            "governed TEST execution requires input.steggate_request containing a canonical StegCore AdmissibilityRequest"
        )
    return steggate_request, input_block.get("input_data", {})


def run_public_inspection_test(request: Mapping[str, Any], *, registry_path: str | Path | None = None, ledger_path: str | Path | None = None) -> dict[str, Any]:
    normalized = validate_public_inspection_request(request)
    steggate_body, input_data = _runtime_input(normalized)
    ManifestReceiptRegistry, AdmissibilityRequest, TransactionLedger, run_manifested_transaction = _load_stegcore()
    try:
        admissibility_request = AdmissibilityRequest.model_validate(steggate_body)
    except Exception as exc:
        raise PublicInspectionRuntimeError(f"invalid StegCore admissibility request: {exc}") from exc

    registry = ManifestReceiptRegistry(registry_path)
    ledger = TransactionLedger(ledger_path)

    def simulated_executor() -> dict[str, Any]:
        return {
            "status": "SIMULATED_TEST_CONSEQUENCE",
            "external_side_effect": False,
            "request_id": normalized["request_id"],
        }

    result = run_manifested_transaction(
        admissibility_request,
        simulated_executor,
        input_data=input_data,
        source="stegverse-sdk:public-inspection-test",
        subject=f"public-inspection:{normalized['request_id']}",
        ledger=ledger,
        metadata={
            "public_inspection_request_id": normalized["request_id"],
            "case_profile": normalized["case_profile"],
            "test_mode": True,
            "external_side_effects_enabled": False,
        },
    )
    record = registry.register(result)
    evidence = registry.evidence_package(record.manifest_receipt_id)
    reconstruction = registry.reconstruct(record.manifest_receipt_id).model_dump(mode="json")
    evaluation = result.execution_observation.get("evaluation") or {}
    return {
        "schema": "stegverse.public-inspection-governed-test-result.v1",
        "request_id": normalized["request_id"],
        "case_profile": normalized["case_profile"],
        "runtime_mode": "TEST",
        "governance_state": evaluation.get("disposition"),
        "manifest_receipt_id": record.manifest_receipt_id,
        "transaction_id": record.transaction_id,
        "chain_verified": bool(result.chain_verified),
        "consequence_executor_invoked": bool(result.execution_observation.get("executor_invoked")),
        "external_side_effect": False,
        "evidence_package": evidence,
        "reconstruction": reconstruction,
        "local_exact_run_retained": registry_path is not None,
        "production_master_records_custody": False,
        "locator_grants_authority": False,
        "github_grants_runtime_authority": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a bounded public inspection request through canonical StegCore TEST governance")
    parser.add_argument("request")
    parser.add_argument("--registry", default=".stegverse/public-inspection/manifest-receipts.jsonl")
    parser.add_argument("--ledger", default=".stegverse/public-inspection/transaction-receipts.jsonl")
    args = parser.parse_args(argv)
    try:
        request = load_public_inspection_request(args.request)
        result = run_public_inspection_test(request, registry_path=args.registry, ledger_path=args.ledger)
    except (PublicInspectionRequestError, PublicInspectionRuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
