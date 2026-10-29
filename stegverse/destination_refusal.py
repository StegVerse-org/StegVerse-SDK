"""Six-field record for a destination that did not answer one bounded request.

The task registry's runtime-observation invariants (external_machine_awaiting_allowed=false,
destination_liveness_is_transition_predicate=false) mean an unreachable destination is never
waited on or retried in a loop: the request is made once, and its failure is a six-field
DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION record that a later manifest-bound transition
can pick up. Errors raised for such failures carry it as ``.disposition``; records returned
instead of raised carry the six fields inline (SDK#484 V-P7).
"""
from __future__ import annotations

from typing import Any, Optional

OWNING_GOAL = "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001"
SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair",
              "retry_entrypoint", "owning_existing_goal", "next_attempt")


def destination_unavailable(destination: str, error: BaseException | str, retry_entrypoint: str,
                            failure_code: str = "DESTINATION_DID_NOT_ANSWER") -> dict[str, Any]:
    detail = error if isinstance(error, str) else f"{type(error).__name__}: {error}"
    return {
        "disposition": "FAIL_CLOSED",
        "failure_code": failure_code,
        "failed_predicate": "DESTINATION_ANSWERED_ONE_BOUNDED_REQUEST",
        "required_evidence_or_repair": (
            f"{destination} gave no usable answer ({detail}); the transition is held as "
            "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION and nothing waits on the destination"),
        "retry_entrypoint": retry_entrypoint,
        "owning_existing_goal": OWNING_GOAL,
        "next_attempt": "a new manifest-bound transition from retry_entrypoint; no retry loop, no liveness probe",
        "authority_effect": "NONE",
    }


def disposition_of(error: Optional[BaseException]) -> Optional[dict[str, Any]]:
    """The six-field record on an error or anywhere on its cause chain."""
    seen: set[int] = set()
    while error is not None and id(error) not in seen:
        seen.add(id(error))
        record = getattr(error, "disposition", None)
        if isinstance(record, dict):
            return record
        error = error.__cause__ or error.__context__
    return None


__all__ = ["OWNING_GOAL", "SIX_FIELDS", "destination_unavailable", "disposition_of"]
