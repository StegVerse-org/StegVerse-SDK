"""Canonical Master Records custody/replay/reconstruction for every SDK run-manifest event.

This module does not create a custody plane. It binds generic SDK manifest execution
to the existing Master Records ManifestReceiptCustody implementation already used by
the sovereign SDK path.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from typing import Any, Mapping


DEFAULT_CUSTODY_DB = "./stegverse-master-records-validation.db"
RUNTIME_IDENTITY = "StegVerse-SDK:run-manifest"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _custody():
    try:
        from services.manifest_receipt_custody import ManifestReceiptCustody
    except ImportError as exc:
        raise RuntimeError(
            "run-manifest requires the canonical Master Records custody package; "
            "install the SDK governed-test dependencies"
        ) from exc
    return ManifestReceiptCustody


def _lifecycle_receipts(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    direct = result.get("lifecycle_receipts")
    if isinstance(direct, list):
        return [dict(row) for row in direct if isinstance(row, Mapping)]
    worker = result.get("worker_result")
    if isinstance(worker, Mapping) and isinstance(worker.get("lifecycle_receipts"), list):
        return [dict(row) for row in worker["lifecycle_receipts"] if isinstance(row, Mapping)]
    packet = result.get("records_packet")
    if isinstance(packet, Mapping) and isinstance(packet.get("lifecycle_receipts"), list):
        return [dict(row) for row in packet["lifecycle_receipts"] if isinstance(row, Mapping)]
    return []


def _verify_embedded_receipt_chain(receipts: list[dict[str, Any]]) -> tuple[bool, str | None]:
    if not receipts:
        return True, None
    previous = None
    for index, receipt in enumerate(receipts):
        supplied = receipt.get("receipt_hash")
        if not isinstance(supplied, str) or not supplied:
            return False, None
        body = dict(receipt)
        body.pop("receipt_hash", None)
        computed = _sha256(body)
        if supplied.lower() != computed.lower():
            return False, None
        declared_previous = receipt.get("previous_receipt_hash")
        if index == 0:
            if declared_previous is not None:
                return False, None
        elif declared_previous != previous:
            return False, None
        previous = supplied
    return True, previous


def _required_evidence_status(result: Mapping[str, Any]) -> str:
    explicit = result.get("evidence_expectations_satisfied")
    if explicit is False:
        return "FAIL"
    missing = result.get("missing_expected_evidence_fields")
    if isinstance(missing, list) and missing:
        return "FAIL"
    return "PASS"


def retain_replay_reconstruct(
    manifest: Mapping[str, Any],
    processor_result: Mapping[str, Any],
    *,
    custody_db: str | Path = DEFAULT_CUSTODY_DB,
) -> dict[str, Any]:
    """Retain one completed SDK event and prove replay/reconstruction before return."""
    Custody = _custody()
    custody = Custody(custody_db)

    manifest_copy = json.loads(_canonical_json(dict(manifest)))
    result_copy = json.loads(_canonical_json(dict(processor_result)))
    manifest_hash = _sha256(manifest_copy)
    result_hash = _sha256(result_copy)
    receipts = _lifecycle_receipts(result_copy)
    chain_verified, embedded_head = _verify_embedded_receipt_chain(receipts)
    if not chain_verified:
        raise RuntimeError("SDK event lifecycle receipt chain failed deterministic verification")

    receipt_chain_head = embedded_head or result_hash
    tx = "SDKTX-" + uuid.uuid4().hex.upper()
    rid_seed = {
        "transaction_id": tx,
        "manifest_hash": manifest_hash,
        "receipt_chain_head": receipt_chain_head,
        "canonical_runtime_identity": RUNTIME_IDENTITY,
    }
    rid = "MR-" + _sha256(rid_seed).upper()

    evidence_package = {
        "schema": "stegverse.sdk-event-evidence-package.v1",
        "manifest_receipt_id": rid,
        "transaction_id": tx,
        "manifest_hash": manifest_hash,
        "receipt_chain_head": receipt_chain_head,
        "canonical_runtime_identity": RUNTIME_IDENTITY,
        "manifest": manifest_copy,
        "processor_result": result_copy,
        "processor_result_sha256": result_hash,
        "lifecycle_receipts": receipts,
        "lifecycle_receipt_chain_verified": chain_verified,
        "required_evidence_validation_status": _required_evidence_status(result_copy),
        "locator_grants_authority": False,
    }
    if evidence_package["required_evidence_validation_status"] != "PASS":
        raise RuntimeError("SDK event required evidence validation failed")

    retained = custody.register(evidence_package)
    retained_view = custody.evidence_package(rid)
    persisted = retained_view["evidence_package"]
    receipt_sha256 = _sha256(persisted)

    replay_id = "OP-REPLAY-" + uuid.uuid4().hex.upper()
    replay_events = []
    for seq, typ in ((0, "REQUESTED"), (1, "SOURCE_RESOLVED")):
        replay_events.append(custody.record_operation_event({
            "source_manifest_receipt_id": rid,
            "operation_id": replay_id,
            "operation": "REPLAY",
            "sequence": seq,
            "event_type": typ,
            "authority_granted": False,
        }))

    replay_receipts = _lifecycle_receipts(persisted.get("processor_result") or {})
    replay_chain_verified, replay_head = _verify_embedded_receipt_chain(replay_receipts)
    replay_result_hash = _sha256((persisted.get("processor_result") or {}))
    replay_artifact = {
        "schema": "stegverse.sdk-event-replay.v1",
        "manifest_receipt_id": rid,
        "manifest_hash_match": _sha256(persisted.get("manifest") or {}) == manifest_hash,
        "processor_result_hash_match": replay_result_hash == result_hash,
        "lifecycle_chain_verified": replay_chain_verified,
        "receipt_chain_head_match": (replay_head or replay_result_hash) == receipt_chain_head,
        "consequence_reexecuted": False,
        "original_record_mutated": False,
    }
    replay_artifact["deterministic_match"] = all([
        replay_artifact["manifest_hash_match"],
        replay_artifact["processor_result_hash_match"],
        replay_artifact["lifecycle_chain_verified"],
        replay_artifact["receipt_chain_head_match"],
    ])
    for seq, typ in ((2, "EVALUATED"), (3, "RETURNED")):
        replay_events.append(custody.record_operation_event({
            "source_manifest_receipt_id": rid,
            "operation_id": replay_id,
            "operation": "REPLAY",
            "sequence": seq,
            "event_type": typ,
            "artifact_sha256": _sha256(replay_artifact),
            "details": {"artifact": replay_artifact},
            "authority_granted": False,
        }))
    replay_artifact["operation_receipt_ids"] = [e["event_receipt_id"] for e in replay_events]
    replay_artifact["operation_transition_custody_status"] = "RECORDED"
    replay_artifact["status"] = "PASS" if replay_artifact["deterministic_match"] else "FAIL"
    if replay_artifact["status"] != "PASS":
        raise RuntimeError("SDK event deterministic replay failed")

    reconstruct_id = "OP-RECONSTRUCT-" + uuid.uuid4().hex.upper()
    reconstruction_events = []
    for seq, typ in ((0, "REQUESTED"), (1, "SOURCE_RESOLVED")):
        reconstruction_events.append(custody.record_operation_event({
            "source_manifest_receipt_id": rid,
            "operation_id": reconstruct_id,
            "operation": "RECONSTRUCT",
            "sequence": seq,
            "event_type": typ,
            "authority_granted": False,
        }))
    reconstructed = custody.reconstruct(rid)
    reconstructed_receipt_sha256 = reconstructed["reconstructed_evidence"]["evidence_package_sha256"]
    digest_equal = receipt_sha256 == reconstructed_receipt_sha256
    for seq, typ in ((2, "ARTIFACT_DERIVED"), (3, "RETURNED")):
        reconstruction_events.append(custody.record_operation_event({
            "source_manifest_receipt_id": rid,
            "operation_id": reconstruct_id,
            "operation": "RECONSTRUCT",
            "sequence": seq,
            "event_type": typ,
            "artifact_sha256": reconstructed_receipt_sha256,
            "authority_granted": False,
        }))

    reconstruction_status = "PASS" if digest_equal else "FAIL"
    if reconstruction_status != "PASS":
        raise RuntimeError("SDK event reconstruction digest mismatch")

    return {
        "manifest_receipt_id": rid,
        "transaction_id": tx,
        "master_records_custody_status": "RECORDED",
        "required_evidence_validation_status": "PASS",
        "receipt_sha256": receipt_sha256,
        "replay": {
            **replay_artifact,
        },
        "reconstruction": {
            "schema": reconstructed.get("schema"),
            "status": reconstruction_status,
            "operation_id": reconstruct_id,
            "operation_receipt_ids": [e["event_receipt_id"] for e in reconstruction_events],
            "operation_transition_custody_status": "RECORDED",
            "reconstructed_receipt_sha256": reconstructed_receipt_sha256,
            "receipt_reconstruction_digest_equal": digest_equal,
            "original_record_mutated": reconstructed.get("original_record_mutated"),
            "consequence_reexecuted": reconstructed.get("consequence_reexecuted"),
        },
    }
