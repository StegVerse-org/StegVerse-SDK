"""Consume canonical coordinate registry and navigation envelopes without expanding authority."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping


class CoordinateNavigationError(ValueError):
    """Raised when canonical coordinate or navigation evidence fails closed."""


def _canonical(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Mapping[str, Any]) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def consume_navigation_envelope(
    envelope: Mapping[str, Any],
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    required = {
        "envelope_version", "navigation_id", "actor", "source_coordinate",
        "destination_coordinate", "context_refs", "authority_transfer",
        "standing_transfer", "delegation_transfer", "data_transfer",
        "receipt_required", "commit_time_revalidation_required", "return_path",
    }
    missing = required - set(envelope)
    if missing:
        raise CoordinateNavigationError(f"missing navigation fields: {sorted(missing)}")
    if envelope["authority_transfer"] != "NONE":
        raise CoordinateNavigationError("navigation cannot transfer authority")
    if envelope["standing_transfer"] != "NONE":
        raise CoordinateNavigationError("navigation cannot transfer standing")
    if envelope["delegation_transfer"] != "NONE":
        raise CoordinateNavigationError("navigation cannot transfer delegation")
    if envelope["data_transfer"] != "DECLARED_REFS_ONLY":
        raise CoordinateNavigationError("navigation may carry declared references only")
    if envelope["receipt_required"] is not True:
        raise CoordinateNavigationError("navigation receipt is required")
    if envelope["commit_time_revalidation_required"] is not True:
        raise CoordinateNavigationError("commit-time revalidation is required")
    refs = list(envelope["context_refs"])
    if any(not isinstance(ref, str) or not ref for ref in refs) or len(refs) != len(set(refs)):
        raise CoordinateNavigationError("context_refs must be unique non-empty strings")

    coordinates = registry.get("coordinates")
    if not isinstance(coordinates, list):
        raise CoordinateNavigationError("registry coordinates must be a list")
    source = str(envelope["source_coordinate"])
    destination = str(envelope["destination_coordinate"])
    source_records = [item for item in coordinates if item.get("coordinate_id") == source]
    if len(source_records) != 1:
        raise CoordinateNavigationError("source coordinate must resolve exactly once")
    source_record = source_records[0]
    edges = registry.get("edges")
    if not isinstance(edges, list):
        raise CoordinateNavigationError("registry edges must be a list")
    matching_edges = [
        edge for edge in edges
        if edge.get("source") == source and edge.get("destination") == destination
    ]
    if len(matching_edges) != 1:
        raise CoordinateNavigationError("destination is not one declared registry edge")
    edge = matching_edges[0]
    if edge.get("authority_transfer") != "NONE" or edge.get("receipt_required") is not True:
        raise CoordinateNavigationError("registry edge violates navigation boundary")

    result: dict[str, Any] = {
        "schema_version": "1.0.0",
        "navigation_id": str(envelope["navigation_id"]),
        "actor": str(envelope["actor"]),
        "source_coordinate": source,
        "destination_coordinate": destination,
        "context_refs": refs,
        "authority_transfer": "NONE",
        "standing_transfer": "NONE",
        "delegation_transfer": "NONE",
        "data_transfer": "DECLARED_REFS_ONLY",
        "receipt_required": True,
        "commit_time_revalidation_required": True,
        "return_path": str(envelope["return_path"]),
        "registry_version": str(registry.get("registry_version", "")),
        "coordinate_version": str(source_record.get("version", "")),
        "contract_ref": str(source_record.get("contract_ref", "")),
        "coordinate_content_sha256": str(source_record.get("content_sha256", "")),
        "sdk_boundary": {
            "sdk_consumption_is_navigation_authority": False,
            "sdk_consumption_transfers_authority": False,
            "sdk_consumption_is_commit_time_validation": False,
            "registry_is_execution_authority": False,
        },
    }
    if not result["registry_version"] or not result["coordinate_version"] or not result["contract_ref"]:
        raise CoordinateNavigationError("registry version binding is incomplete")
    digest = result["coordinate_content_sha256"]
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise CoordinateNavigationError("coordinate content hash is invalid")
    result["consumer_sha256"] = _hash(result)
    return result
