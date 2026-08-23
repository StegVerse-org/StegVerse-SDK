from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

SCHEMA_ID = "stegverse.governed-application-spine.v1"
CANONICAL_STEGGATE_RUNTIME = "stegverse:steggate:canonical:three-layer:v1"
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def canonical_hash(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _required_string(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def _hash_or_none(value: Any, name: str) -> None:
    if value is not None and not SHA256_RE.fullmatch(str(value)):
        raise ValueError(f"{name} must be sha256:<64 lowercase hex>")


def validate_governed_application_spine(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the SDK-visible composition boundary without granting authority.

    This validator intentionally does not evaluate SPE standing, StegGate
    admissibility, execute actions, or install custody. It verifies that a
    composed lifecycle record cannot represent those boundaries inconsistently.
    """

    value = dict(record)
    if value.get("schema") != SCHEMA_ID:
        raise ValueError("unsupported governed application spine schema")
    for field in ("package_id", "transition_id", "run_id"):
        _required_string(value.get(field), field)

    source = dict(value.get("source") or {})
    _required_string(source.get("origin_class"), "source.origin_class")
    _hash_or_none(source.get("source_hash"), "source.source_hash")
    if source.get("source_hash") is None:
        raise ValueError("source.source_hash is required")

    candidate = dict(value.get("candidate") or {})
    _hash_or_none(candidate.get("candidate_hash"), "candidate.candidate_hash")
    if candidate.get("candidate_hash") is None:
        raise ValueError("candidate.candidate_hash is required")
    if candidate.get("authorizing") is not False:
        raise ValueError("SDK candidate must remain non-authorizing")
    if candidate.get("model_output_authority", "NONE") != "NONE":
        raise ValueError("model output cannot carry authority")

    standing = dict(value.get("standing") or {})
    if standing.get("state") not in {"PENDING", "ALLOW", "DENY", "FAIL_CLOSED"}:
        raise ValueError("standing.state is invalid")
    _hash_or_none(standing.get("receipt_hash"), "standing.receipt_hash")
    if standing.get("state") != "PENDING" and standing.get("receipt_hash") is None:
        raise ValueError("resolved standing requires a receipt hash")
    if standing.get("execution_authorized") is not False:
        raise ValueError("SPE standing never authorizes execution")

    admissibility = dict(value.get("admissibility") or {})
    if admissibility.get("runtime_identity") != CANONICAL_STEGGATE_RUNTIME:
        raise ValueError("canonical StegGate runtime identity required")
    if admissibility.get("state") not in {"PENDING", "ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"}:
        raise ValueError("admissibility.state is invalid")
    if admissibility.get("commit_time_validity") not in {"PENDING", "CURRENT", "STALE", "INVALID", "NOT_APPLICABLE"}:
        raise ValueError("commit_time_validity is invalid")
    if admissibility.get("commit_coherence") not in {"PENDING", "ALLOW", "DENY", "FAIL_CLOSED"}:
        raise ValueError("commit_coherence is invalid")
    _hash_or_none(admissibility.get("request_hash"), "admissibility.request_hash")

    execution = dict(value.get("execution") or {})
    if not isinstance(execution.get("performed"), bool):
        raise ValueError("execution.performed must be boolean")
    _hash_or_none(execution.get("result_hash"), "execution.result_hash")

    continuity = dict(value.get("continuity") or {})
    if not isinstance(continuity.get("return_ingested"), bool):
        raise ValueError("continuity.return_ingested must be boolean")
    if continuity.get("reconstruction_state") not in {"PENDING", "PASS", "FAIL"}:
        raise ValueError("continuity.reconstruction_state is invalid")
    _hash_or_none(continuity.get("receipt_chain_head"), "continuity.receipt_chain_head")

    authority = dict(value.get("authority") or {})
    if authority.get("sdk_authority") != "NONE":
        raise ValueError("SDK authority must remain NONE")
    if authority.get("spe_execution_authority") != "NONE":
        raise ValueError("SPE execution authority must remain NONE")
    if authority.get("model_output_authority") != "NONE":
        raise ValueError("model output authority must remain NONE")
    if authority.get("custody_authority", "NONE") not in {"NONE", "SEPARATELY_ADMITTED"}:
        raise ValueError("custody authority is invalid")

    if execution["performed"]:
        if standing.get("state") != "ALLOW" or standing.get("standing_current") is not True:
            raise ValueError("execution requires current SPE ALLOW standing")
        if admissibility.get("state") != "ALLOW":
            raise ValueError("execution requires canonical StegGate ALLOW")
        if admissibility.get("commit_time_validity") != "CURRENT":
            raise ValueError("execution requires current commit-time validity")
        if admissibility.get("commit_coherence") != "ALLOW":
            raise ValueError("execution requires commit coherence ALLOW")
        _required_string(execution.get("executor_ref"), "execution.executor_ref")
        if execution.get("result_hash") is None:
            raise ValueError("performed execution requires result_hash")

    return value


__all__ = [
    "SCHEMA_ID",
    "CANONICAL_STEGGATE_RUNTIME",
    "canonical_hash",
    "validate_governed_application_spine",
]
