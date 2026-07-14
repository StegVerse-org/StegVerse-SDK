"""Portable repo-standards gate records for SDK transport and inspection.

Validation confirms structure and preserves upstream authority boundaries. An SDK
record does not create release authority, admissibility, standing, or execution.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Dict, Mapping

SCHEMA_VERSION = "1.0.0"
ALLOWED_STATES = {"PENDING", "SATISFIED", "BLOCKED", "NOT_APPLICABLE"}


class RepoStandardsGateRecordError(ValueError):
    """Raised when a repo-standards gate record violates the SDK contract."""


def stable_gate_record_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def validate_repo_standards_gate_record(record: Mapping[str, Any]) -> None:
    required = {
        "schema_version",
        "record_id",
        "repository",
        "gate_state",
        "source_repository",
        "source_ref",
        "evidence_refs",
        "authority_boundaries",
        "continuation",
    }
    missing = required - set(record)
    if missing:
        raise RepoStandardsGateRecordError(f"missing gate-record fields: {sorted(missing)}")
    if record["schema_version"] != SCHEMA_VERSION:
        raise RepoStandardsGateRecordError("unsupported gate-record schema version")
    if record["gate_state"] not in ALLOWED_STATES:
        raise RepoStandardsGateRecordError("unsupported gate state")
    for field in ("record_id", "repository", "source_repository", "source_ref"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise RepoStandardsGateRecordError(f"{field} must be a non-empty string")
    evidence_refs = record["evidence_refs"]
    if not isinstance(evidence_refs, list) or len(evidence_refs) != len(set(evidence_refs)):
        raise RepoStandardsGateRecordError("evidence_refs must be a unique list")
    boundaries = record["authority_boundaries"]
    required_false = (
        "sdk_validation_is_release_authority",
        "sdk_transport_is_admissibility",
        "gate_record_is_execution_authority",
        "record_presence_is_gate_satisfaction",
    )
    if any(boundaries.get(name) is not False for name in required_false):
        raise RepoStandardsGateRecordError("SDK gate records may not elevate authority")
    continuation = record["continuation"]
    if not isinstance(continuation, Mapping):
        raise RepoStandardsGateRecordError("continuation must be an object")
    if continuation.get("owner") in (None, ""):
        raise RepoStandardsGateRecordError("continuation owner is required")
    if continuation.get("next_action") in (None, ""):
        raise RepoStandardsGateRecordError("continuation next_action is required")


def normalize_repo_standards_gate_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    normalized = deepcopy(dict(record))
    normalized["evidence_refs"] = sorted(normalized["evidence_refs"])
    validate_repo_standards_gate_record(normalized)
    normalized["record_sha256"] = stable_gate_record_hash(normalized)
    return normalized


def build_repo_standards_gate_record(
    *,
    record_id: str,
    repository: str,
    gate_state: str,
    source_repository: str,
    source_ref: str,
    evidence_refs: list[str],
    owner: str,
    next_action: str,
) -> Dict[str, Any]:
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_id": record_id,
        "repository": repository,
        "gate_state": gate_state,
        "source_repository": source_repository,
        "source_ref": source_ref,
        "evidence_refs": evidence_refs,
        "authority_boundaries": {
            "sdk_validation_is_release_authority": False,
            "sdk_transport_is_admissibility": False,
            "gate_record_is_execution_authority": False,
            "record_presence_is_gate_satisfaction": False,
        },
        "continuation": {
            "owner": owner,
            "next_action": next_action,
        },
    }
    return normalize_repo_standards_gate_record(record)
