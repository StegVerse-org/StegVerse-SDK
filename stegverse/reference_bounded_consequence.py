from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "stegverse.reference-bounded-consequence.v1"


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema": "stegverse.reference-sovereign-state.v1", "revision": 0, "values": {}}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("reference state root must be an object")
    if value.get("schema") != "stegverse.reference-sovereign-state.v1":
        raise ValueError("unsupported reference state schema")
    if not isinstance(value.get("revision"), int) or value["revision"] < 0:
        raise ValueError("reference state revision is invalid")
    if not isinstance(value.get("values"), dict):
        raise ValueError("reference state values must be an object")
    return value


def apply_reference_state_transition(
    path: str | Path,
    *,
    key: str,
    value: Any,
    idempotency_key: str,
) -> dict[str, Any]:
    """Perform one bounded local state transition with deterministic evidence.

    This function grants no authority by itself. It is intended to be supplied as
    the bounded consequence executor to the canonical StegCore transaction
    lifecycle, which decides whether it may be invoked.
    """
    target = Path(path)
    if not key.strip():
        raise ValueError("key is required")
    if not idempotency_key.strip():
        raise ValueError("idempotency_key is required")

    before = _load_state(target)
    before_bytes = _canonical_bytes(before)
    seen = dict(before.get("idempotency") or {})
    requested_hash = _sha256(_canonical_bytes({"key": key, "value": value}))
    prior = seen.get(idempotency_key)
    if prior is not None:
        if prior != requested_hash:
            raise ValueError("idempotency_key_conflict")
        return {
            "schema": SCHEMA_ID,
            "status": "IDEMPOTENT_REPLAY_SUPPRESSED",
            "state_transition_performed": False,
            "external_side_effect": False,
            "idempotency_key": idempotency_key,
            "request_hash": requested_hash,
            "before_state_hash": _sha256(before_bytes),
            "after_state_hash": _sha256(before_bytes),
            "revision": before["revision"],
            "authority_effect": "NONE",
        }

    values = dict(before["values"])
    values[key] = value
    seen[idempotency_key] = requested_hash
    after = {
        "schema": "stegverse.reference-sovereign-state.v1",
        "revision": before["revision"] + 1,
        "values": values,
        "idempotency": seen,
    }
    after_bytes = _canonical_bytes(after)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(after_bytes)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, target)

    return {
        "schema": SCHEMA_ID,
        "status": "STATE_TRANSITION_RECORDED",
        "state_transition_performed": True,
        "external_side_effect": False,
        "idempotency_key": idempotency_key,
        "request_hash": requested_hash,
        "key": key,
        "before_state_hash": _sha256(before_bytes),
        "after_state_hash": _sha256(after_bytes),
        "before_revision": before["revision"],
        "after_revision": after["revision"],
        "authority_effect": "NONE",
    }


def reference_state_executor(
    path: str | Path,
    *,
    key: str,
    value: Any,
    idempotency_key: str,
):
    """Return a zero-argument consequence callable for canonical StegCore."""
    def execute() -> Mapping[str, Any]:
        return apply_reference_state_transition(
            path,
            key=key,
            value=value,
            idempotency_key=idempotency_key,
        )

    return execute


__all__ = [
    "SCHEMA_ID",
    "apply_reference_state_transition",
    "reference_state_executor",
]
