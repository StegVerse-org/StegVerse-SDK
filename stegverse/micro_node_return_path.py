"""SDK validation for LLM-adapter micro-node governed return-path fixtures.

This module validates a micro-node-compatible transition request and governed
return payload without calling a live micro-node runtime and without granting
execution authority.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping

MICRO_NODE_RETURN_PATH_SCHEMA_VERSION = "stegverse.sdk.micro_node_return_path.v0.1"

REQUIRED_REQUEST_FIELDS = (
    "transition_id",
    "origin_system",
    "return_path",
    "action",
    "actor",
    "target",
    "scope",
    "policy_ref",
    "delegation_ref",
    "payload",
)

REQUIRED_RETURN_FIELDS = (
    "transition_id",
    "return_path",
    "decision",
    "receipt_hash",
    "returned_to_origin",
    "execution_authority_granted",
    "provider_output_is_authority",
)

TERMINAL_DECISIONS = frozenset({"ALLOW", "DENY", "FAIL_CLOSED"})


class MicroNodeReturnPathValidationError(ValueError):
    """Raised when a micro-node return-path fixture is malformed."""


@dataclass(frozen=True)
class MicroNodeReturnPathDecision:
    """SDK decision for a micro-node governed return-path fixture pair."""

    decision: str
    reason: str
    transition_id: str
    request_hash: str
    governed_return_hash: str
    schema_version: str = MICRO_NODE_RETURN_PATH_SCHEMA_VERSION

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def validate_micro_node_return_path(
    request: Mapping[str, Any], governed_return: Mapping[str, Any]
) -> MicroNodeReturnPathDecision:
    """Validate fixture-bound micro-node return-path compatibility.

    The validator is intentionally non-executing. It validates that an adapter
    request can preserve return-path continuity and receive a terminal governed
    return without turning provider output or the commitment request into
    execution authority.
    """

    if not isinstance(request, Mapping):
        raise MicroNodeReturnPathValidationError("request must be an object")
    if not isinstance(governed_return, Mapping):
        raise MicroNodeReturnPathValidationError("governed_return must be an object")

    missing_request = [key for key in REQUIRED_REQUEST_FIELDS if key not in request]
    if missing_request:
        raise MicroNodeReturnPathValidationError(
            "request missing fields: {}".format(", ".join(missing_request))
        )

    missing_return = [key for key in REQUIRED_RETURN_FIELDS if key not in governed_return]
    if missing_return:
        raise MicroNodeReturnPathValidationError(
            "governed_return missing fields: {}".format(", ".join(missing_return))
        )

    transition_id = str(request.get("transition_id", ""))
    request_hash = stable_hash(request)
    governed_return_hash = stable_hash(governed_return)

    failures: list[str] = []
    if transition_id != str(governed_return.get("transition_id", "")):
        failures.append("transition_id mismatch")
    if str(request.get("return_path", "")) != str(governed_return.get("return_path", "")):
        failures.append("return_path mismatch")
    if str(governed_return.get("decision", "")) not in TERMINAL_DECISIONS:
        failures.append("bad terminal decision")
    if governed_return.get("returned_to_origin") is not True:
        failures.append("return path was not preserved")
    if governed_return.get("execution_authority_granted") is not False:
        failures.append("execution authority must remain false")
    if governed_return.get("provider_output_is_authority") is not False:
        failures.append("provider output must not become authority")
    payload = request.get("payload")
    if not isinstance(payload, Mapping):
        failures.append("request payload must be an object")
    elif payload.get("execution_authority_requested") is not False:
        failures.append("request must not ask for execution authority")
    if governed_return.get("commitment_request_is_authority", False) is not False:
        failures.append("commitment request must not become authority")

    if failures:
        return MicroNodeReturnPathDecision(
            decision="FAIL_CLOSED",
            reason="; ".join(failures),
            transition_id=transition_id,
            request_hash=request_hash,
            governed_return_hash=governed_return_hash,
        )

    return MicroNodeReturnPathDecision(
        decision="ALLOW",
        reason="micro-node return-path fixture preserves return path without execution authority",
        transition_id=transition_id,
        request_hash=request_hash,
        governed_return_hash=governed_return_hash,
    )


__all__ = [
    "MICRO_NODE_RETURN_PATH_SCHEMA_VERSION",
    "MicroNodeReturnPathDecision",
    "MicroNodeReturnPathValidationError",
    "validate_micro_node_return_path",
]
