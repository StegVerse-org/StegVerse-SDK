"""Build a deterministic read-only ecosystem catalog from canonical projections."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping

from .ecosystem_records import EcosystemRecord

_ALLOWED_TYPES = {"handoff", "manifest", "status", "receipt_projection"}
_TERMINAL_EXCLUDED = {"SUPERSEDED", "DEPRECATED", "QUARANTINED"}


class EcosystemCatalogError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


def _iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_catalog(
    projections: Iterable[Mapping[str, Any]],
    *,
    built_at: str,
    source_set_id: str,
) -> dict[str, Any]:
    """Validate, filter, sort, and hash a packaged read-only record catalog."""
    _iso(built_at)
    if not source_set_id.strip():
        raise EcosystemCatalogError("source_set_id is required")

    records: list[dict[str, Any]] = []
    identities: set[str] = set()
    for raw in projections:
        record_type = str(raw.get("record_type", ""))
        if record_type not in _ALLOWED_TYPES:
            raise EcosystemCatalogError(f"unsupported record_type: {record_type}")
        if raw.get("authoritative") is not True:
            continue
        lifecycle = str(raw.get("lifecycle_state", "CURRENT")).upper()
        if lifecycle in _TERMINAL_EXCLUDED:
            continue
        record = EcosystemRecord.from_mapping(raw)
        if record.record_id in identities:
            raise EcosystemCatalogError(f"duplicate record_id: {record.record_id}")
        identities.add(record.record_id)
        item = record.to_mapping()
        item["record_type"] = record_type
        item["catalog_source_digest"] = _digest(dict(raw))
        records.append(item)

    records.sort(key=lambda item: (item["repository"], item["record_type"], item["record_id"]))
    body = {
        "schema": "stegverse.ecosystem_catalog.v0.1",
        "source_set_id": source_set_id,
        "built_at": built_at,
        "read_only": True,
        "authorizing": False,
        "custody_transferred": False,
        "record_count": len(records),
        "records": records,
    }
    body["catalog_id"] = _digest(body)
    return body


def validate_catalog(catalog: Mapping[str, Any]) -> dict[str, Any]:
    if catalog.get("schema") != "stegverse.ecosystem_catalog.v0.1":
        raise EcosystemCatalogError("unsupported catalog schema")
    if catalog.get("read_only") is not True:
        raise EcosystemCatalogError("catalog must be read-only")
    if catalog.get("authorizing") is not False or catalog.get("custody_transferred") is not False:
        raise EcosystemCatalogError("catalog attempted authority or custody escalation")
    records = catalog.get("records")
    if not isinstance(records, list) or catalog.get("record_count") != len(records):
        raise EcosystemCatalogError("catalog record count mismatch")
    expected = dict(catalog)
    catalog_id = expected.pop("catalog_id", None)
    if catalog_id != _digest(expected):
        raise EcosystemCatalogError("catalog digest mismatch")
    seen: set[str] = set()
    for raw in records:
        record = EcosystemRecord.from_mapping(raw)
        if record.record_id in seen:
            raise EcosystemCatalogError(f"duplicate record_id: {record.record_id}")
        seen.add(record.record_id)
    return dict(catalog)
