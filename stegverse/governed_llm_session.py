"""Governed LLM session packet validation.

This module validates the complete adapter session packet emitted by
StegVerse-org/LLM-adapter. It does not execute actions and does not grant
authority. It gives SDK intake a stable way to accept, reject, or quarantine
adapter packets before downstream routing.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping


SESSION_PACKET_SCHEMA_VERSION = "stegverse.sdk.governed_llm_session.v0.1"

REQUIRED_TOP_LEVEL_KEYS = (
    "provider_request",
    "provider_request_hash",
    "provider_response",
    "continuity",
    "adapter_result",
    "action_route",
    "commitment_request",
    "authority_decision",
    "execution_handoff",
)


class GovernedLLMSessionValidationError(ValueError):
    """Raised when a governed LLM session packet is malformed."""


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class GovernedLLMSessionDecision:
    """SDK intake decision for a governed LLM adapter session."""

    decision: str
    reason: str
    session_hash: str
    adapter_decision: str
    authority_decision: str
    execution_status: str
    schema_version: str = SESSION_PACKET_SCHEMA_VERSION

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def validate_governed_llm_session_packet(packet: Mapping[str, Any]) -> GovernedLLMSessionDecision:
    """Validate a governed LLM adapter session packet for SDK intake."""

    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in packet]
    if missing:
        raise GovernedLLMSessionValidationError("missing governed LLM session keys: {}".format(", ".join(missing)))

    provider_request_hash = str(packet.get("provider_request_hash", ""))
    provider_response = _as_mapping(packet["provider_response"], "provider_response")
    if str(provider_response.get("request_hash", "")) != provider_request_hash:
        raise GovernedLLMSessionValidationError("provider_response.request_hash does not match provider_request_hash")

    adapter_result = _as_mapping(packet["adapter_result"], "adapter_result")
    authority_decision = _as_mapping(packet["authority_decision"], "authority_decision")
    execution_handoff = _as_mapping(packet["execution_handoff"], "execution_handoff")

    adapter_decision = str(adapter_result.get("decision", "UNRESOLVED"))
    authority = str(authority_decision.get("decision", "UNRESOLVED"))
    execution_status = str(execution_handoff.get("status", "unresolved"))

    session_hash = stable_hash(packet)

    if execution_status not in {"not_executable", "ready_for_external_executor"}:
        return GovernedLLMSessionDecision(
            decision="FAIL_CLOSED",
            reason="execution handoff status is not recognized",
            session_hash=session_hash,
            adapter_decision=adapter_decision,
            authority_decision=authority,
            execution_status=execution_status,
        )

    if execution_status == "ready_for_external_executor" and authority != "ALLOW":
        return GovernedLLMSessionDecision(
            decision="FAIL_CLOSED",
            reason="execution handoff claims readiness without ALLOW authority decision",
            session_hash=session_hash,
            adapter_decision=adapter_decision,
            authority_decision=authority,
            execution_status=execution_status,
        )

    if adapter_decision == "DENY":
        return GovernedLLMSessionDecision(
            decision="DENY",
            reason="adapter denied the candidate output",
            session_hash=session_hash,
            adapter_decision=adapter_decision,
            authority_decision=authority,
            execution_status=execution_status,
        )

    if adapter_decision == "QUARANTINE":
        return GovernedLLMSessionDecision(
            decision="QUARANTINE",
            reason="adapter quarantined output before consequence",
            session_hash=session_hash,
            adapter_decision=adapter_decision,
            authority_decision=authority,
            execution_status=execution_status,
        )

    if adapter_decision == "ALLOW" and authority in {"NOT_REQUIRED", "ALLOW"}:
        return GovernedLLMSessionDecision(
            decision="ALLOW",
            reason="read-only or authority-satisfied adapter packet is structurally valid",
            session_hash=session_hash,
            adapter_decision=adapter_decision,
            authority_decision=authority,
            execution_status=execution_status,
        )

    return GovernedLLMSessionDecision(
        decision="FAIL_CLOSED",
        reason="adapter and authority decision combination is unresolved",
        session_hash=session_hash,
        adapter_decision=adapter_decision,
        authority_decision=authority,
        execution_status=execution_status,
    )


def _as_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise GovernedLLMSessionValidationError("{} must be an object".format(name))
    return value


__all__ = [
    "SESSION_PACKET_SCHEMA_VERSION",
    "GovernedLLMSessionDecision",
    "GovernedLLMSessionValidationError",
    "validate_governed_llm_session_packet",
]
