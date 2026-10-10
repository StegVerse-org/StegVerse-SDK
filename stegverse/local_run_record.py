"""SDK-internal local run record for the sovereign validation lane (stdlib only).

This is a non-authoritative evidence file for one caller's local runs. It keeps
the route events, the run's evidence package and replay/reconstruct operation
events so a later replay or reconstruction can read them back. It is not a
ledger, not custody and not a gate:

- ``authority_effect`` is ``NONE`` and ``completes_transition`` is ``False`` on
  every row it returns;
- it never reports ``ALLOW`` or ``RECORDED`` as a completion; sovereign
  completion comes only from a verified organization-ledger readback
  (``stegverse.organization_ledger_evidence``);
- it is written only at the location the caller supplies. There is no default
  path and nothing derived from the host.

It replaces the earlier import of ``services.manifest_receipt_custody`` from the
master-records/orchestration package, which the SDK no longer depends on.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Mapping

SCHEMA = "stegverse.sdk.local-run-record.v1"
RECONSTRUCTION_SCHEMA = "stegverse.sdk.local-run-record-reconstruction.v1"
RECORD_STATUS = "LOCAL_EVIDENCE_ONLY"
NON_AUTHORITY = {
    "role": "DOWNSTREAM_NON_GATING_EVIDENCE",
    "authority_effect": "NONE",
    "completes_transition": False,
    "gates_transition": False,
}

_TABLES = (
    "CREATE TABLE IF NOT EXISTS route_events ("
    " route_manifest_id TEXT NOT NULL, sequence INTEGER NOT NULL, route_receipt_id TEXT NOT NULL UNIQUE,"
    " event_json TEXT NOT NULL, PRIMARY KEY (route_manifest_id, sequence))",
    "CREATE TABLE IF NOT EXISTS run_records ("
    " manifest_receipt_id TEXT PRIMARY KEY, package_json TEXT NOT NULL, record_sha256 TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS operation_events ("
    " event_receipt_id TEXT PRIMARY KEY, source_manifest_receipt_id TEXT NOT NULL, operation_id TEXT NOT NULL,"
    " sequence INTEGER NOT NULL, event_json TEXT NOT NULL)",
)


class LocalRunRecordError(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _location(location: Any) -> Path:
    if isinstance(location, os.PathLike):
        location = os.fspath(location)
    if not isinstance(location, str) or not location.strip():
        raise LocalRunRecordError(
            "local run record location must be supplied by the caller; there is no default location"
        )
    return Path(location)


class LocalRunRecordStore:
    """Append-only local run record at a caller-supplied file location."""

    def __init__(self, location: str | os.PathLike[str]):
        self.location = _location(location)
        with closing(self._connect()) as db, db:
            for statement in _TABLES:
                db.execute(statement)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.location))

    # Route events --------------------------------------------------------
    def record_route_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        body = dict(event)
        route_manifest_id = str(body.get("route_manifest_id") or "").strip()
        if not route_manifest_id:
            raise LocalRunRecordError("route event has no route_manifest_id")
        with closing(self._connect()) as db, db:
            last = db.execute(
                "SELECT sequence, event_json FROM route_events WHERE route_manifest_id=? ORDER BY sequence DESC LIMIT 1",
                (route_manifest_id,),
            ).fetchone()
            sequence = 0 if last is None else int(last[0]) + 1
            previous = None if last is None else json.loads(last[1])["event_sha256"]
            row = {
                "schema": SCHEMA,
                "route_manifest_id": route_manifest_id,
                "local_sequence": sequence,
                "previous_event_sha256": previous,
                "event": body,
                "record_status": RECORD_STATUS,
                **NON_AUTHORITY,
            }
            row["event_sha256"] = _sha256(row)
            row["route_receipt_id"] = "LRR-" + row["event_sha256"][:32].upper()
            db.execute(
                "INSERT INTO route_events VALUES(?,?,?,?)",
                (route_manifest_id, sequence, row["route_receipt_id"], _canonical(row)),
            )
        return row

    def route_events(self, route_manifest_id: str) -> list[dict[str, Any]]:
        with closing(self._connect()) as db:
            rows = db.execute(
                "SELECT event_json FROM route_events WHERE route_manifest_id=? ORDER BY sequence",
                (str(route_manifest_id),),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    # Run evidence package ------------------------------------------------
    def register(self, evidence_package: Mapping[str, Any]) -> dict[str, Any]:
        package = dict(evidence_package)
        rid = str(package.get("manifest_receipt_id") or "").strip().upper()
        if not rid:
            raise LocalRunRecordError("evidence package has no manifest_receipt_id")
        package_json = _canonical(package)
        record_sha256 = hashlib.sha256(package_json.encode("utf-8")).hexdigest()
        with closing(self._connect()) as db, db:
            existing = db.execute(
                "SELECT record_sha256 FROM run_records WHERE manifest_receipt_id=?", (rid,)
            ).fetchone()
            if existing is None:
                db.execute("INSERT INTO run_records VALUES(?,?,?)", (rid, package_json, record_sha256))
            elif existing[0] != record_sha256:
                raise LocalRunRecordError(f"local run record for {rid} already holds a different package")
        return self._record_view(rid, package, record_sha256)

    def evidence_package(self, manifest_receipt_id: str) -> dict[str, Any]:
        rid = str(manifest_receipt_id).strip().upper()
        with closing(self._connect()) as db:
            row = db.execute(
                "SELECT package_json, record_sha256 FROM run_records WHERE manifest_receipt_id=?", (rid,)
            ).fetchone()
        if row is None:
            raise LocalRunRecordError(f"no local run record for {rid}")
        package_json, record_sha256 = row
        if hashlib.sha256(package_json.encode("utf-8")).hexdigest() != record_sha256:
            raise LocalRunRecordError(f"local run record for {rid} does not match its digest")
        return self._record_view(rid, json.loads(package_json), record_sha256)

    @staticmethod
    def _record_view(rid: str, package: dict[str, Any], record_sha256: str) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "manifest_receipt_id": rid,
            "evidence_package": package,
            "record_sha256": record_sha256,
            # Field name kept for existing readers of the local run record digest.
            "master_record_sha256": record_sha256,
            "record_status": RECORD_STATUS,
            **NON_AUTHORITY,
        }

    # Replay / reconstruct operation events -------------------------------
    def record_operation_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        body = dict(event)
        rid = str(body.get("source_manifest_receipt_id") or "").strip().upper()
        operation_id = str(body.get("operation_id") or "").strip()
        if not rid or not operation_id:
            raise LocalRunRecordError("operation event needs source_manifest_receipt_id and operation_id")
        row = {"schema": SCHEMA, "event": body, "record_status": RECORD_STATUS, **NON_AUTHORITY}
        row["event_sha256"] = _sha256(row)
        row["event_receipt_id"] = "LOE-" + row["event_sha256"][:32].upper()
        with closing(self._connect()) as db, db:
            db.execute(
                "INSERT OR IGNORE INTO operation_events VALUES(?,?,?,?,?)",
                (row["event_receipt_id"], rid, operation_id, int(body.get("sequence") or 0), _canonical(row)),
            )
        return row

    def reconstruct(self, manifest_receipt_id: str) -> dict[str, Any]:
        """Derive the run's reconstruction from the stored package; nothing is re-executed."""
        record = self.evidence_package(manifest_receipt_id)
        package = record["evidence_package"]
        link = package.get("ecosystem_route_link") if isinstance(package.get("ecosystem_route_link"), Mapping) else {}
        observation = package.get("execution_observation") if isinstance(package.get("execution_observation"), Mapping) else {}
        evaluation = observation.get("evaluation") if isinstance(observation.get("evaluation"), Mapping) else {}
        route_manifest_id = link.get("route_manifest_id")
        events = self.route_events(route_manifest_id) if route_manifest_id else []
        previous = None
        chain_intact = bool(events)
        for row in events:
            check = {k: v for k, v in row.items() if k not in {"event_sha256", "route_receipt_id"}}
            if row.get("previous_event_sha256") != previous or _sha256(check) != row.get("event_sha256"):
                chain_intact = False
            previous = row.get("event_sha256")
        return {
            "schema": RECONSTRUCTION_SCHEMA,
            "manifest_receipt_id": record["manifest_receipt_id"],
            "transaction_id": package.get("transaction_id") or link.get("transaction_id"),
            "record_sha256": record["record_sha256"],
            "original_disposition": evaluation.get("disposition"),
            "route_manifest_id": route_manifest_id,
            "route_receipt_ids": [row["route_receipt_id"] for row in events],
            "local_route_chain_intact": chain_intact,
            "evidence_package": package,
            "consequence_reexecuted": False,
            "original_record_mutated": False,
            "record_status": RECORD_STATUS,
            **NON_AUTHORITY,
        }


__all__ = [
    "LocalRunRecordError",
    "LocalRunRecordStore",
    "NON_AUTHORITY",
    "RECONSTRUCTION_SCHEMA",
    "RECORD_STATUS",
    "SCHEMA",
]
