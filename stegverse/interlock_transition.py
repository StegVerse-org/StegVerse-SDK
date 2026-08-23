from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

SCHEMA_ID = "stegverse.interlock-transition.v1"
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
CONNECTION_CLASSES = {"ADAPTER", "INTERLOCK"}
DIRECTIONS = {"INGRESS", "EGRESS"}
GOVERNANCE_MODES = {"PROVIDED", "DEFAULT_STEGVERSE", "COMPOSED"}
BOUNDARY_STATES = {"PRESENTED", "ACCEPT", "REPAIR", "DENY", "REVIEW"}
RELATIONSHIP_TYPES = {
    "CAUSE",
    "DEPENDENCY",
    "EVIDENCE",
    "AUTHORITY",
    "CORROBORATION",
    "CONFLICT",
    "SUPERSEDES",
    "OBSERVED_WITHOUT_DEPENDENCY",
}


def canonical_hash(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _required_string(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def _require_hash(value: Any, name: str) -> str:
    text = _required_string(value, name)
    if not SHA256_RE.fullmatch(text):
        raise ValueError(f"{name} must be sha256:<64 lowercase hex>")
    return text


def _validate_receipt_ref(item: Mapping[str, Any], name: str) -> None:
    _required_string(item.get("receipt_id"), f"{name}.receipt_id")
    _required_string(item.get("issuer"), f"{name}.issuer")
    _require_hash(item.get("receipt_hash"), f"{name}.receipt_hash")


def validate_interlock_transition(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate portable interlock/manifold structure without granting authority."""
    value = dict(record)
    if value.get("schema") != SCHEMA_ID:
        raise ValueError("unsupported interlock transition schema")
    for field in ("package_id", "transition_id", "run_id"):
        _required_string(value.get(field), field)

    connection = dict(value.get("connection") or {})
    connection_class = connection.get("class")
    if connection_class not in CONNECTION_CLASSES:
        raise ValueError("connection.class is invalid")
    if connection.get("direction") not in DIRECTIONS:
        raise ValueError("connection.direction is invalid")
    _required_string(connection.get("participant_id"), "connection.participant_id")

    manifest = dict(value.get("manifest") or {})
    _require_hash(manifest.get("manifest_hash"), "manifest.manifest_hash")
    _require_hash(manifest.get("source_state_hash"), "manifest.source_state_hash")
    if manifest.get("canonicalization") != "JCS_RFC8785_NFC":
        raise ValueError("manifest canonicalization must be JCS_RFC8785_NFC")

    predecessor_receipts = list(manifest.get("predecessor_receipts") or [])
    for index, receipt in enumerate(predecessor_receipts):
        if not isinstance(receipt, Mapping):
            raise ValueError("predecessor receipt must be an object")
        _validate_receipt_ref(receipt, f"manifest.predecessor_receipts[{index}]")

    if connection_class == "INTERLOCK":
        if not predecessor_receipts:
            raise ValueError("INTERLOCK requires at least one predecessor receipt")
        _require_hash(connection.get("participant_boundary_receipt_hash"), "connection.participant_boundary_receipt_hash")
        _require_hash(connection.get("participant_binding_hash"), "connection.participant_binding_hash")
        predecessor_hashes = {str(item.get("receipt_hash")) for item in predecessor_receipts}
        if connection["participant_boundary_receipt_hash"] not in predecessor_hashes:
            raise ValueError("interlock boundary receipt must be present in predecessor receipts")

    governance = dict(value.get("governance") or {})
    mode = governance.get("mode")
    if mode not in GOVERNANCE_MODES:
        raise ValueError("governance.mode is invalid")
    profiles = list(governance.get("profiles") or [])
    if not profiles:
        raise ValueError("governance profiles must be explicit")
    has_stegverse = False
    has_participant = False
    for index, profile in enumerate(profiles):
        if not isinstance(profile, Mapping):
            raise ValueError("governance profile must be an object")
        _required_string(profile.get("profile_id"), f"governance.profiles[{index}].profile_id")
        _required_string(profile.get("issuer"), f"governance.profiles[{index}].issuer")
        _require_hash(profile.get("profile_hash"), f"governance.profiles[{index}].profile_hash")
        source = profile.get("source")
        if source not in {"PARTICIPANT", "STEGVERSE"}:
            raise ValueError("governance profile source is invalid")
        has_stegverse = has_stegverse or source == "STEGVERSE"
        has_participant = has_participant or source == "PARTICIPANT"

    if mode == "PROVIDED" and (not has_participant or has_stegverse):
        raise ValueError("PROVIDED governance requires participant-only profiles")
    if mode == "DEFAULT_STEGVERSE" and (not has_stegverse or has_participant):
        raise ValueError("DEFAULT_STEGVERSE requires StegVerse-only profiles")
    if mode == "COMPOSED" and not (has_stegverse and has_participant):
        raise ValueError("COMPOSED governance requires participant and StegVerse profiles")

    manifold = dict(value.get("manifold") or {})
    predecessors = list(manifold.get("predecessors") or [])
    successors = list(manifold.get("successors") or [])
    if not predecessors:
        raise ValueError("manifold requires at least one predecessor state")

    known_state_ids = set()
    for group_name, group in (("predecessors", predecessors), ("successors", successors)):
        seen = set()
        for index, state in enumerate(group):
            if not isinstance(state, Mapping):
                raise ValueError(f"manifold.{group_name} state must be an object")
            state_id = _required_string(state.get("state_id"), f"manifold.{group_name}[{index}].state_id")
            _require_hash(state.get("state_hash"), f"manifold.{group_name}[{index}].state_hash")
            if state_id in seen:
                raise ValueError(f"duplicate manifold {group_name} state_id")
            seen.add(state_id)
            known_state_ids.add(state_id)

    relationships = list(manifold.get("relationships") or [])
    for index, edge in enumerate(relationships):
        if not isinstance(edge, Mapping):
            raise ValueError("manifold relationship must be an object")
        source_state = _required_string(edge.get("from_state_id"), f"manifold.relationships[{index}].from_state_id")
        target_state = _required_string(edge.get("to_state_id"), f"manifold.relationships[{index}].to_state_id")
        if edge.get("type") not in RELATIONSHIP_TYPES:
            raise ValueError("manifold relationship type is invalid")
        if source_state not in known_state_ids or target_state not in known_state_ids:
            raise ValueError("manifold relationship references unknown state")

    boundary = dict(value.get("boundary") or {})
    if boundary.get("state") not in BOUNDARY_STATES:
        raise ValueError("boundary.state is invalid")
    original_manifest_hash = _require_hash(boundary.get("original_manifest_hash"), "boundary.original_manifest_hash")
    if original_manifest_hash != manifest.get("manifest_hash"):
        raise ValueError("boundary original manifest must bind exact incoming manifest")
    repaired_hash = boundary.get("repaired_manifest_hash")
    if boundary.get("state") == "REPAIR":
        _require_hash(repaired_hash, "boundary.repaired_manifest_hash")
        if repaired_hash == original_manifest_hash:
            raise ValueError("REPAIR must create a distinct successor manifest")
    elif repaired_hash is not None:
        raise ValueError("repaired_manifest_hash is only valid for REPAIR")

    authority = dict(value.get("authority") or {})
    required_authority = {
        "sdk_authority": "NONE",
        "participant_truth_assumed": False,
        "interlock_transfers_authority": False,
        "master_records_custody_claimed": False,
        "execution_authorized": False,
    }
    for field, expected in required_authority.items():
        if authority.get(field) != expected:
            raise ValueError(f"authority.{field} must be {expected!r}")

    reconstruction = dict(value.get("reconstruction") or {})
    if reconstruction.get("required") is not True:
        raise ValueError("reconstruction.required must be true")
    if reconstruction.get("replay_scope") != "MATERIAL_CAUSAL_CLOSURE":
        raise ValueError("reconstruction.replay_scope must be MATERIAL_CAUSAL_CLOSURE")
    if reconstruction.get("linear_chain_is_special_case") is not True:
        raise ValueError("linear chain must be declared a special case")

    return value


__all__ = [
    "SCHEMA_ID",
    "CONNECTION_CLASSES",
    "DIRECTIONS",
    "GOVERNANCE_MODES",
    "BOUNDARY_STATES",
    "RELATIONSHIP_TYPES",
    "canonical_hash",
    "validate_interlock_transition",
]
