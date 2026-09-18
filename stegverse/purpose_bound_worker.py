"""Local SDK demonstration of a purpose-bound worker derived from one TT cell."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "stegverse.sdk.tt-purpose-bound-worker.v1"
PACKET_SCHEMA = "stegverse.sdk.tt-purpose-bound-worker.records-only.v1"
SUPPORTED_CAPABILITY = "text.integrity_summary"


class PurposeBoundWorkerError(ValueError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _receipt(sequence: int, phase: str, body: Mapping[str, Any], previous_hash: str | None) -> dict[str, Any]:
    receipt = {
        "sequence": sequence,
        "phase": phase,
        "previous_receipt_hash": previous_hash,
        **dict(body),
    }
    receipt["receipt_hash"] = _sha256(receipt)
    return receipt


def _validate_request(request: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if request.get("schema") != SCHEMA:
        raise PurposeBoundWorkerError(f"schema must be {SCHEMA}")
    cell = request.get("transition_cell")
    if not isinstance(cell, Mapping):
        raise PurposeBoundWorkerError("transition_cell must be an object")
    candidate = cell.get("candidate")
    if not isinstance(candidate, Mapping):
        raise PurposeBoundWorkerError("transition_cell.candidate must be an object")

    purpose = candidate.get("purpose")
    capability = candidate.get("required_capability")
    payload = candidate.get("payload")
    lifetime = candidate.get("max_lifetime_seconds")

    if not isinstance(purpose, str) or not purpose.strip():
        raise PurposeBoundWorkerError("candidate.purpose must be a non-empty string")
    if capability != SUPPORTED_CAPABILITY:
        raise PurposeBoundWorkerError(f"unsupported capability: {capability!r}")
    if not isinstance(payload, Mapping) or not isinstance(payload.get("text"), str):
        raise PurposeBoundWorkerError("candidate.payload.text must be a string")
    if not isinstance(lifetime, int) or isinstance(lifetime, bool) or lifetime <= 0:
        raise PurposeBoundWorkerError("candidate.max_lifetime_seconds must be a positive integer")

    return dict(cell), dict(candidate)


def run_purpose_bound_worker(request: Mapping[str, Any]) -> dict[str, Any]:
    """Materialize one bounded local worker, invoke it, retire it, and return records only."""
    cell, candidate = _validate_request(request)
    cell_hash = _sha256(cell)
    purpose = candidate["purpose"]
    capability = candidate["required_capability"]
    payload = candidate["payload"]
    payload_hash = _sha256(payload)
    worker_id = "worker:" + hashlib.sha256(
        f"{cell_hash}|{purpose}|{capability}".encode("utf-8")
    ).hexdigest()[:24]

    worker_spec = {
        "worker_id": worker_id,
        "actor_class": "ai_worker",
        "purpose": purpose,
        "required_capability": capability,
        "max_lifetime_seconds": candidate["max_lifetime_seconds"],
        "retirement_condition": "PURPOSE_COMPLETED_OR_FAILED",
        "authority_effect": "NONE_LOCAL_SEMANTIC_DEMONSTRATION",
        "persistence": "NONE_AFTER_CLOSE",
    }

    receipts: list[dict[str, Any]] = []
    r1 = _receipt(1, "MATERIALIZED", {
        "worker_id": worker_id,
        "worker_spec_hash": _sha256(worker_spec),
        "transition_cell_hash": cell_hash,
    }, None)
    receipts.append(r1)

    r2 = _receipt(2, "INVOCATION_STARTED", {
        "worker_id": worker_id,
        "capability": capability,
        "payload_hash": payload_hash,
    }, r1["receipt_hash"])
    receipts.append(r2)

    text = payload["text"]
    result = {
        "capability": capability,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "utf8_bytes": len(text.encode("utf-8")),
        "word_count": len(text.split()),
    }
    result_hash = _sha256(result)

    r3 = _receipt(3, "TASK_COMPLETED", {
        "worker_id": worker_id,
        "task_result_hash": result_hash,
    }, r2["receipt_hash"])
    receipts.append(r3)

    r4 = _receipt(4, "RETIRED", {
        "worker_id": worker_id,
        "retirement_reason": "PURPOSE_COMPLETED",
        "worker_live_after_close": False,
    }, r3["receipt_hash"])
    receipts.append(r4)

    packet = {
        "schema": PACKET_SCHEMA,
        "source_schema": SCHEMA,
        "transition_cell_hash": cell_hash,
        "purpose": purpose,
        "worker_spec": worker_spec,
        "lifecycle_receipts": receipts,
        "task_result": result,
        "task_result_hash": result_hash,
        "records_only": True,
        "worker_live_after_close": False,
        "runtime_binding_state": "LOCAL_SEMANTIC_DEMONSTRATION_ONLY",
        "live_runtime_receipt_refs": [],
        "authority_effect": "NONE",
    }
    packet["records_packet_hash"] = _sha256(packet)
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stegverse worker-lifecycle",
        description="Run one TT-cell purpose-bound local worker and return a records-only packet.",
    )
    parser.add_argument("--input", required=True, help="Path to a stegverse.sdk.tt-purpose-bound-worker.v1 JSON request")
    args = parser.parse_args(argv)
    request = json.loads(Path(args.input).read_text(encoding="utf-8"))
    packet = run_purpose_bound_worker(request)
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
