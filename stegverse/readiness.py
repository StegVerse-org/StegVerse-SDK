"""State-dependent readiness evaluation for StegVerse SDK integrations.

This module evaluates evidence readiness only. It does not perform governance or
change runtime authority. READY is a conclusion over all identified applicable
predicates, never a synonym for success of one narrower subsystem.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

PredicateState = Literal["SATISFIED", "UNSATISFIED", "UNKNOWN", "NOT_APPLICABLE"]
ReadinessState = Literal["READY", "PROBE_REQUIRED", "BLOCKED"]


@dataclass(frozen=True)
class ProbeEvidence:
    evidence_ref: str
    observed_at: str
    observation: str

    def __post_init__(self) -> None:
        if not self.evidence_ref.strip():
            raise ValueError("probe evidence_ref must be non-empty")
        if not self.observed_at.strip():
            raise ValueError("probe observed_at must be non-empty")
        if not self.observation.strip():
            raise ValueError("probe observation must be non-empty")


@dataclass(frozen=True)
class ReadinessPredicate:
    predicate_id: str
    state: PredicateState
    applicable: bool = True
    ambiguity_affects_readiness: bool = False
    probe_evidence: ProbeEvidence | None = None

    def __post_init__(self) -> None:
        if not self.predicate_id.strip():
            raise ValueError("predicate_id must be non-empty")
        if self.state not in {"SATISFIED", "UNSATISFIED", "UNKNOWN", "NOT_APPLICABLE"}:
            raise ValueError(f"unsupported predicate state: {self.state}")
        if not self.applicable and self.state != "NOT_APPLICABLE":
            raise ValueError("non-applicable predicates must use NOT_APPLICABLE")
        if self.applicable and self.state == "NOT_APPLICABLE":
            raise ValueError("applicable predicates cannot use NOT_APPLICABLE")
        if self.probe_evidence is not None and self.state == "UNKNOWN":
            raise ValueError("UNKNOWN predicates cannot claim resolving probe evidence")


@dataclass(frozen=True)
class ReadinessDecision:
    state: ReadinessState
    blockers: tuple[str, ...]
    probes_required: tuple[str, ...]
    considered_predicates: tuple[str, ...]


def evaluate_readiness(predicates: Iterable[ReadinessPredicate]) -> ReadinessDecision:
    """Evaluate cumulative readiness over all identified predicates.

    Precedence is BLOCKED > PROBE_REQUIRED > READY.  A SATISFIED predicate with
    readiness-affecting ambiguity remains probe-required until evidence removes
    that ambiguity.  Unknown unknowns cannot be evaluated before discovery; once
    discovered, callers must add them to this predicate set before reevaluation.
    """
    items = tuple(predicates)
    if not items:
        return ReadinessDecision(
            state="PROBE_REQUIRED",
            blockers=(),
            probes_required=("readiness_predicate_inventory",),
            considered_predicates=(),
        )

    seen: set[str] = set()
    blockers: list[str] = []
    probes: list[str] = []
    considered: list[str] = []

    for predicate in items:
        if predicate.predicate_id in seen:
            raise ValueError(f"duplicate readiness predicate: {predicate.predicate_id}")
        seen.add(predicate.predicate_id)
        considered.append(predicate.predicate_id)

        if not predicate.applicable:
            continue
        if predicate.state == "UNSATISFIED":
            blockers.append(predicate.predicate_id)
            continue
        if predicate.state == "UNKNOWN" or predicate.ambiguity_affects_readiness:
            probes.append(predicate.predicate_id)

    if blockers:
        state: ReadinessState = "BLOCKED"
    elif probes:
        state = "PROBE_REQUIRED"
    else:
        state = "READY"

    return ReadinessDecision(
        state=state,
        blockers=tuple(blockers),
        probes_required=tuple(probes),
        considered_predicates=tuple(considered),
    )


def resolve_with_probe(
    predicate: ReadinessPredicate,
    *,
    resolved_state: Literal["SATISFIED", "UNSATISFIED"],
    evidence: ProbeEvidence,
) -> ReadinessPredicate:
    """Resolve an UNKNOWN/ambiguous predicate using durable probe evidence."""
    if not predicate.applicable:
        raise ValueError("cannot probe a non-applicable predicate")
    if predicate.state != "UNKNOWN" and not predicate.ambiguity_affects_readiness:
        raise ValueError("predicate does not require a readiness probe")
    return ReadinessPredicate(
        predicate_id=predicate.predicate_id,
        state=resolved_state,
        applicable=True,
        ambiguity_affects_readiness=False,
        probe_evidence=evidence,
    )
