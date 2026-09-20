# Vendored exact canonical Master Records custody source.
# Upstream: master-records/orchestration@03312236c115bc814024d700810391340648601f
# Path: services/manifest_receipt_custody.py
# Do not edit here; replace only from the canonical upstream source.

"""Provider-neutral custody for manifested transactions and exact-run receipts.

Every manifested ecosystem state transition is append-only Master Records history.
Exact-run records remain immutable; later replay/reconstruction and ordinary route
transitions are linked without granting execution or routing authority themselves.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Mapping

SCHEMA = "stegverse.master-records.manifest-receipt-custody.v1"
RECONSTRUCTION_SCHEMA = "stegverse.master-records.manifest-receipt-reconstruction.v1"
OPERATION_EVENT_SCHEMA = "stegverse.master-records.manifest-operation-event.v1"
ROUTE_EVENT_SCHEMA = "stegverse.master-records.manifest-route-event.v1"
_LOCK = RLock()

ROUTE_EVENT_TYPES = {
    "MANIFEST_ESTABLISHED",
    "ENTRY_RECEIVED",
    "SDK_ENTERED",
    "INGESTION_ENTERED",
    "CGE_ADMITTED",
    "CGE_ROUTED",
    "MODULE_ENTERED",
    "MODULE_RESULT",
    "CGE_RETURN_INGESTED",
    "ROUTE_CLEARED",
    "RETURNED",
    "FAIL_CLOSED",
}


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _normalize_sha_locator(value: str, prefix: str, error: str) -> str:
    if not isinstance(value, str):
        raise ValueError(error)
    normalized = value.strip().upper()
    if not normalized.startswith(prefix):
        raise ValueError(error)
    digest = normalized[len(prefix):]
    if len(digest) != 64 or any(ch not in "0123456789ABCDEF" for ch in digest):
        raise ValueError(error)
    return normalized


def normalize_manifest_receipt_id(value: str) -> str:
    return _normalize_sha_locator(value, "MR-", "manifest_receipt_id_invalid")


def normalize_route_manifest_id(value: str) -> str:
    return _normalize_sha_locator(value, "MF-", "route_manifest_id_invalid")


@dataclass(frozen=True)
class ManifestReceiptCustodyRecord:
    manifest_receipt_id: str
    transaction_id: str
    manifest_hash: str
    receipt_chain_head: str
    canonical_runtime_identity: str
    evidence_package: dict[str, Any]
    record_sha256: str

    def as_dict(self) -> dict[str, Any]:
        return {"schema": SCHEMA, "manifest_receipt_id": self.manifest_receipt_id, "transaction_id": self.transaction_id, "manifest_hash": self.manifest_hash, "receipt_chain_head": self.receipt_chain_head, "canonical_runtime_identity": self.canonical_runtime_identity, "evidence_package": self.evidence_package, "record_sha256": self.record_sha256, "locator_grants_authority": False, "custody_grants_execution_authority": False, "custody_grants_admissibility": False}


class ManifestReceiptCustody:
    """Append-only manifested-route, exact-run, and operation-transition custody."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        with _LOCK, self._connection:
            self._connection.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS manifest_receipt_records (
                    manifest_receipt_id TEXT PRIMARY KEY, transaction_id TEXT UNIQUE NOT NULL,
                    manifest_hash TEXT NOT NULL, receipt_chain_head TEXT NOT NULL,
                    canonical_runtime_identity TEXT NOT NULL, evidence_package_json TEXT NOT NULL,
                    record_sha256 TEXT NOT NULL);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_manifest_receipt_exact_run
                    ON manifest_receipt_records(transaction_id, manifest_hash, receipt_chain_head, canonical_runtime_identity);
                CREATE TABLE IF NOT EXISTS manifest_operation_events (
                    event_receipt_id TEXT PRIMARY KEY,
                    operation_id TEXT NOT NULL,
                    source_manifest_receipt_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    UNIQUE(operation_id, sequence));
                CREATE INDEX IF NOT EXISTS idx_manifest_operation_source ON manifest_operation_events(source_manifest_receipt_id, operation_id, sequence);
                CREATE TABLE IF NOT EXISTS manifest_route_events (
                    route_receipt_id TEXT PRIMARY KEY,
                    route_manifest_id TEXT NOT NULL,
                    transaction_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    checkpoint_id TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    UNIQUE(route_manifest_id, sequence));
                CREATE INDEX IF NOT EXISTS idx_manifest_route_transaction ON manifest_route_events(transaction_id, route_manifest_id, sequence);
            """)

    @staticmethod
    def _validate_package(package: Mapping[str, Any]) -> tuple[str, str, str, str, str]:
        rid = normalize_manifest_receipt_id(str(package.get("manifest_receipt_id") or ""))
        tx = str(package.get("transaction_id") or "").strip(); mh = str(package.get("manifest_hash") or "").strip().lower(); ch = str(package.get("receipt_chain_head") or "").strip().lower(); rt = str(package.get("canonical_runtime_identity") or "").strip()
        if not tx or not rt: raise ValueError("manifest_receipt_identity_incomplete")
        for name, digest in (("manifest_hash", mh), ("receipt_chain_head", ch)):
            if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest): raise ValueError(f"{name}_invalid")
        if package.get("locator_grants_authority") is True: raise ValueError("manifest_receipt_authority_escalation")
        return rid, tx, mh, ch, rt

    def register(self, package: Mapping[str, Any]) -> ManifestReceiptCustodyRecord:
        rid, tx, mh, ch, rt = self._validate_package(package)
        canonical_package = json.loads(canonical_json(dict(package)))
        body = {"manifest_receipt_id": rid, "transaction_id": tx, "manifest_hash": mh, "receipt_chain_head": ch, "canonical_runtime_identity": rt, "evidence_package": canonical_package}
        rh = canonical_sha256(body); serialized = canonical_json(canonical_package)
        with _LOCK, self._connection:
            existing = self._connection.execute("SELECT * FROM manifest_receipt_records WHERE manifest_receipt_id = ?", (rid,)).fetchone()
            if existing is not None:
                if existing["record_sha256"] != rh: raise ValueError("manifest_receipt_id_conflict")
                return self._row_to_record(existing)
            if self._connection.execute("SELECT 1 FROM manifest_receipt_records WHERE transaction_id = ?", (tx,)).fetchone() is not None: raise ValueError("transaction_id_already_bound")
            self._connection.execute("INSERT INTO manifest_receipt_records VALUES(?,?,?,?,?,?,?)", (rid, tx, mh, ch, rt, serialized, rh))
        return self.resolve(rid)

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> ManifestReceiptCustodyRecord:
        return ManifestReceiptCustodyRecord(row["manifest_receipt_id"], row["transaction_id"], row["manifest_hash"], row["receipt_chain_head"], row["canonical_runtime_identity"], json.loads(row["evidence_package_json"]), row["record_sha256"])

    def resolve(self, manifest_receipt_id: str) -> ManifestReceiptCustodyRecord:
        rid = normalize_manifest_receipt_id(manifest_receipt_id)
        rows = self._connection.execute("SELECT * FROM manifest_receipt_records WHERE manifest_receipt_id = ?", (rid,)).fetchall()
        if len(rows) != 1: raise KeyError("manifest_receipt_not_found_or_ambiguous")
        return self._row_to_record(rows[0])

    def evidence_package(self, manifest_receipt_id: str) -> dict[str, Any]:
        r = self.resolve(manifest_receipt_id)
        return {"schema": SCHEMA, "manifest_receipt_id": r.manifest_receipt_id, "master_record_sha256": r.record_sha256, "evidence_package": dict(r.evidence_package), "locator_grants_authority": False}

    def reconstruct(self, manifest_receipt_id: str) -> dict[str, Any]:
        r = self.resolve(manifest_receipt_id); ph = canonical_sha256(r.evidence_package)
        return {"schema": RECONSTRUCTION_SCHEMA, "manifest_receipt_id": r.manifest_receipt_id, "transaction_id": r.transaction_id, "manifest_hash": r.manifest_hash, "receipt_chain_head": r.receipt_chain_head, "canonical_runtime_identity": r.canonical_runtime_identity, "persisted_evidence": dict(r.evidence_package), "reconstructed_evidence": {"evidence_package_sha256": ph, "master_record_sha256": r.record_sha256}, "original_record_mutated": False, "consequence_reexecuted": False, "reconstruction_grants_authority": False}

    def record_route_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        manifest_id = normalize_route_manifest_id(str(event.get("route_manifest_id") or ""))
        transaction_id = str(event.get("transaction_id") or "").strip()
        event_type = str(event.get("event_type") or "").upper()
        checkpoint_id = str(event.get("checkpoint_id") or "").strip()
        sequence = event.get("sequence")
        if not transaction_id or not checkpoint_id or event_type not in ROUTE_EVENT_TYPES or not isinstance(sequence, int) or sequence < 0:
            raise ValueError("manifest_route_event_invalid")
        if event.get("authority_granted") is True:
            raise ValueError("manifest_route_authority_escalation")
        with _LOCK, self._connection:
            previous_row = self._connection.execute("SELECT event_hash, transaction_id FROM manifest_route_events WHERE route_manifest_id = ? ORDER BY sequence DESC LIMIT 1", (manifest_id,)).fetchone()
            expected_sequence = 0 if previous_row is None else self._connection.execute("SELECT MAX(sequence) AS n FROM manifest_route_events WHERE route_manifest_id = ?", (manifest_id,)).fetchone()["n"] + 1
            if sequence != expected_sequence:
                raise ValueError("manifest_route_sequence_invalid")
            if previous_row is not None and previous_row["transaction_id"] != transaction_id:
                raise ValueError("manifest_route_transaction_conflict")
            previous_hash = None if previous_row is None else previous_row["event_hash"]
            body = {
                "schema": ROUTE_EVENT_SCHEMA,
                "route_manifest_id": manifest_id,
                "transaction_id": transaction_id,
                "sequence": sequence,
                "event_type": event_type,
                "checkpoint_id": checkpoint_id,
                "module": str(event.get("module") or ""),
                "route_index": event.get("route_index"),
                "input_sha256": event.get("input_sha256"),
                "output_sha256": event.get("output_sha256"),
                "execution_provenance": dict(event.get("execution_provenance") or {}),
                "details": dict(event.get("details") or {}),
                "previous_event_hash": previous_hash,
                "authority_granted": False,
            }
            event_hash = canonical_sha256(body)
            route_receipt_id = "MRR-" + event_hash.upper()
            recorded_at = datetime.now(timezone.utc).isoformat()
            body.update({"event_hash": event_hash, "route_receipt_id": route_receipt_id, "recorded_at": recorded_at})
            self._connection.execute("INSERT INTO manifest_route_events VALUES(?,?,?,?,?,?,?,?,?,?)", (route_receipt_id, manifest_id, transaction_id, sequence, event_type, checkpoint_id, canonical_json(body), previous_hash, event_hash, recorded_at))
        return body

    def route_events(self, route_manifest_id: str) -> list[dict[str, Any]]:
        manifest_id = normalize_route_manifest_id(route_manifest_id)
        rows = self._connection.execute("SELECT event_json FROM manifest_route_events WHERE route_manifest_id = ? ORDER BY sequence", (manifest_id,)).fetchall()
        return [json.loads(row["event_json"]) for row in rows]

    def record_operation_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        rid = normalize_manifest_receipt_id(str(event.get("source_manifest_receipt_id") or "")); self.resolve(rid)
        operation = str(event.get("operation") or "").upper(); event_type = str(event.get("event_type") or "").upper(); operation_id = str(event.get("operation_id") or "").strip(); sequence = event.get("sequence")
        allowed = {"REPLAY": {"REQUESTED", "SOURCE_RESOLVED", "EVALUATED", "RETURNED"}, "RECONSTRUCT": {"REQUESTED", "SOURCE_RESOLVED", "ARTIFACT_DERIVED", "RETURNED"}}
        if operation not in allowed or event_type not in allowed[operation] or not operation_id or not isinstance(sequence, int) or sequence < 0: raise ValueError("manifest_operation_event_invalid")
        if event.get("authority_granted") is True: raise ValueError("manifest_operation_authority_escalation")
        with _LOCK, self._connection:
            previous = self._connection.execute("SELECT event_hash FROM manifest_operation_events WHERE operation_id = ? ORDER BY sequence DESC LIMIT 1", (operation_id,)).fetchone()
            expected_sequence = 0 if previous is None else self._connection.execute("SELECT MAX(sequence) AS n FROM manifest_operation_events WHERE operation_id = ?", (operation_id,)).fetchone()["n"] + 1
            if sequence != expected_sequence: raise ValueError("manifest_operation_sequence_invalid")
            previous_hash = None if previous is None else previous["event_hash"]
            body = {"schema": OPERATION_EVENT_SCHEMA, "operation_id": operation_id, "source_manifest_receipt_id": rid, "operation": operation, "sequence": sequence, "event_type": event_type, "artifact_sha256": event.get("artifact_sha256"), "details": dict(event.get("details") or {}), "previous_event_hash": previous_hash, "authority_granted": False}
            event_hash = canonical_sha256(body); event_receipt_id = "MRO-" + event_hash.upper(); recorded_at = datetime.now(timezone.utc).isoformat(); body["event_hash"] = event_hash; body["event_receipt_id"] = event_receipt_id; body["recorded_at"] = recorded_at
            self._connection.execute("INSERT INTO manifest_operation_events VALUES(?,?,?,?,?,?,?,?,?,?)", (event_receipt_id, operation_id, rid, operation, sequence, event_type, canonical_json(body), previous_hash, event_hash, recorded_at))
        return body

    def operation_events(self, manifest_receipt_id: str, operation_id: str) -> list[dict[str, Any]]:
        rid = normalize_manifest_receipt_id(manifest_receipt_id)
        rows = self._connection.execute("SELECT event_json FROM manifest_operation_events WHERE source_manifest_receipt_id = ? AND operation_id = ? ORDER BY sequence", (rid, operation_id)).fetchall()
        return [json.loads(row["event_json"]) for row in rows]

    def close(self) -> None:
        self._connection.close()
