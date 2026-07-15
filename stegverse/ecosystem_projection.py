"""Canonical projection production for packaged ecosystem catalogs."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping


class EcosystemProjectionError(ValueError):
    pass


_ALLOWED_TYPES = {"handoff", "manifest", "status", "receipt_projection"}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


def _validate_time(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def project_record(source: Mapping[str, Any]) -> dict[str, Any]:
    """Project an explicitly declared canonical source into catalog input form."""
    record_type = str(source.get("record_type", ""))
    if record_type not in _ALLOWED_TYPES:
        raise EcosystemProjectionError(f"unsupported record_type: {record_type}")
    if source.get("canonical") is not True:
        raise EcosystemProjectionError("source must explicitly declare canonical=true")
    if source.get("authoritative") is not True:
        raise EcosystemProjectionError("source must explicitly declare authoritative=true")
    required = ("repository", "source", "title", "text", "observed_at")
    missing = [name for name in required if not str(source.get(name, "")).strip()]
    if missing:
        raise EcosystemProjectionError(f"missing projection fields: {', '.join(missing)}")
    observed_at = _validate_time(str(source["observed_at"]))
    lifecycle = str(source.get("lifecycle_state", "CURRENT")).upper()
    if lifecycle not in {"CURRENT", "SUPERSEDED", "DEPRECATED", "QUARANTINED"}:
        raise EcosystemProjectionError(f"invalid lifecycle_state: {lifecycle}")
    identity_material = {
        "repository": str(source["repository"]),
        "source": str(source["source"]),
        "record_type": record_type,
        "observed_at": observed_at,
        "content_digest": _digest({"title": source["title"], "text": source["text"]}),
    }
    return {
        "record_id": str(source.get("record_id") or _digest(identity_material)),
        "repository": str(source["repository"]),
        "source": str(source["source"]),
        "record_type": record_type,
        "title": str(source["title"]),
        "text": str(source["text"]),
        "authoritative": True,
        "lifecycle_state": lifecycle,
        "observed_at": observed_at,
        "supersedes": [str(item) for item in source.get("supersedes", [])],
        "tags": [str(item) for item in source.get("tags", [])],
        "receipt_ref": str(source["receipt_ref"]) if source.get("receipt_ref") else None,
        "projection_source_digest": _digest(dict(source)),
        "canonical_source_declared": True,
    }


def project_records(sources: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    records = [project_record(source) for source in sources]
    ids = [record["record_id"] for record in records]
    if len(ids) != len(set(ids)):
        raise EcosystemProjectionError("duplicate projected record_id")
    records.sort(key=lambda item: (item["repository"], item["record_type"], item["record_id"]))
    return records
