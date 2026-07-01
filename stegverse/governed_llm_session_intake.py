"""SDK intake routing for governed LLM session packets.

This module wraps governed LLM session validation with route guidance. It does
not execute actions, grant authority, or mutate external state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .governed_llm_session import (
    GovernedLLMSessionValidationError,
    stable_hash,
    validate_governed_llm_session_packet,
)


SESSION_INTAKE_SCHEMA_VERSION = "stegverse.sdk.governed_llm_session_intake.v0.1"


@dataclass(frozen=True)
class GovernedLLMSessionIntakeResult:
    """Route-ready SDK intake result for a governed LLM session packet."""

    intake_decision: str
    route: str
    reason: str
    session_hash: str
    retain_record: bool
    validation_decision: str
    schema_version: str = SESSION_INTAKE_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def intake_governed_llm_session_packet(packet: Mapping[str, Any]) -> GovernedLLMSessionIntakeResult:
    """Validate and route a governed LLM session packet for SDK intake."""

    try:
        validation = validate_governed_llm_session_packet(packet)
    except GovernedLLMSessionValidationError as exc:
        return GovernedLLMSessionIntakeResult(
            intake_decision="REJECT",
            route="reject_malformed_packet",
            reason=str(exc),
            session_hash=stable_hash(packet),
            retain_record=True,
            validation_decision="ERROR",
        )

    if validation.decision == "ALLOW":
        route = "route_read_only_or_external_executor_handoff"
        if validation.execution_status == "ready_for_external_executor":
            route = "route_external_executor_handoff"
        return GovernedLLMSessionIntakeResult(
            intake_decision="ROUTE",
            route=route,
            reason=validation.reason,
            session_hash=validation.session_hash,
            retain_record=True,
            validation_decision=validation.decision,
        )

    if validation.decision == "QUARANTINE":
        return GovernedLLMSessionIntakeResult(
            intake_decision="QUARANTINE",
            route="quarantine_before_consequence",
            reason=validation.reason,
            session_hash=validation.session_hash,
            retain_record=True,
            validation_decision=validation.decision,
        )

    if validation.decision == "DENY":
        return GovernedLLMSessionIntakeResult(
            intake_decision="REJECT",
            route="reject_denied_adapter_output",
            reason=validation.reason,
            session_hash=validation.session_hash,
            retain_record=True,
            validation_decision=validation.decision,
        )

    return GovernedLLMSessionIntakeResult(
        intake_decision="FAIL_CLOSED",
        route="fail_closed_unresolved_session",
        reason=validation.reason,
        session_hash=validation.session_hash,
        retain_record=True,
        validation_decision=validation.decision,
    )


__all__ = [
    "SESSION_INTAKE_SCHEMA_VERSION",
    "GovernedLLMSessionIntakeResult",
    "intake_governed_llm_session_packet",
]
