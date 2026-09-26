"""Adapter from canonical InTr epistemic acknowledgements to SDK readiness predicates.

The universal protocol is owned by StegVerse-Labs/continuity-vault-kit. This module
only consumes its stable acknowledgement projection; it does not redefine that protocol.
"""
from __future__ import annotations

from typing import Any, Mapping

from .readiness import ReadinessPredicate

_ACK_ORDER = (
    "RECEIVED", "INTERPRETED", "APPLICABILITY_RESOLVED", "EVIDENCE_ACCEPTED", "AGREED", "INCORPORATED"
)


def readiness_predicate_from_epistemic_ack(
    acknowledgement: Mapping[str, Any], *, required_acknowledgement_level: str
) -> ReadinessPredicate:
    """Map receiver epistemic disposition into fail-closed local readiness state."""
    predicate_id = acknowledgement.get("incorporated_predicate_id") or acknowledgement.get("item_id")
    if not isinstance(predicate_id, str) or not predicate_id:
        raise ValueError("epistemic acknowledgement requires item/predicate identity")
    level = acknowledgement.get("level")
    if level not in _ACK_ORDER or required_acknowledgement_level not in _ACK_ORDER:
        raise ValueError("unsupported acknowledgement level")
    disposition = acknowledgement.get("incorporation_state")

    if disposition == "NOT_APPLICABLE":
        return ReadinessPredicate(predicate_id=predicate_id, state="NOT_APPLICABLE", applicable=False)
    if disposition in {"PROBE_REQUIRED", "DISPUTED", "REJECTED_AS_INVALID"}:
        return ReadinessPredicate(predicate_id=predicate_id, state="UNKNOWN", applicable=True, ambiguity_affects_readiness=True)
    if disposition != "INCORPORATED":
        raise ValueError("unsupported incorporation_state")

    if _ACK_ORDER.index(level) < _ACK_ORDER.index(required_acknowledgement_level):
        return ReadinessPredicate(predicate_id=predicate_id, state="UNKNOWN", applicable=True, ambiguity_affects_readiness=True)
    return ReadinessPredicate(predicate_id=predicate_id, state="SATISFIED", applicable=True)
