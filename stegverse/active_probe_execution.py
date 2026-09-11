"""Provider-neutral active probe execution for state-transition readiness.

Probe results are obtained from a runtime-supplied executor, never from caller
manifest assertions. Successful probe evidence may resolve represented predicate,
ambiguity, or discovered-unknown state, after which readiness is re-derived by the
canonical state-transition evidence normalizer. Probe evidence is non-authorizing.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping

from .state_transition_evidence import normalize_state_transition_evidence

ACTIVE_PROBE_RESULT_PROFILE = "stegverse.active-probe-result.v1"
ProbeExecutor = Callable[[str, Mapping[str, Any]], Mapping[str, Any]]


def _required_text(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise ValueError(f"active_probe_result.{key} is required")
    return item.strip()


def _validated_result(reason: str, raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ValueError("active probe executor must return an object")
    result = deepcopy(dict(raw))
    if result.get("profile") != ACTIVE_PROBE_RESULT_PROFILE:
        raise ValueError(f"active_probe_result.profile must be {ACTIVE_PROBE_RESULT_PROFILE}")
    if _required_text(result, "reason") != reason:
        raise ValueError("active probe result reason mismatch")
    outcome = result.get("outcome")
    if outcome not in {"SATISFIED", "UNRESOLVED"}:
        raise ValueError("active_probe_result.outcome must be SATISFIED or UNRESOLVED")
    _required_text(result, "observed_at")
    _required_text(result, "evidence_ref")
    _required_text(result, "source")
    if result.get("authority_effect") != "NONE":
        raise ValueError("active probe result must have authority_effect NONE")
    return result


def _apply_probe_result(transition: dict[str, Any], reason: str, result: Mapping[str, Any]) -> None:
    if result["outcome"] != "SATISFIED":
        return

    if reason.startswith("predicate:"):
        _, predicate_id, problem = reason.split(":", 2)
        predicate = next((p for p in transition["applicable_predicates"] if p["predicate_id"] == predicate_id), None)
        if predicate is None:
            raise ValueError(f"active probe predicate not found: {predicate_id}")
        if problem == "evidence_unresolved":
            predicate["evidence_status"] = "SATISFIED"
            return
        if problem == "applicability_unknown":
            applicability = result.get("applicability")
            if applicability not in {"APPLICABLE", "NOT_APPLICABLE"}:
                raise ValueError("applicability probe must resolve to APPLICABLE or NOT_APPLICABLE")
            predicate["applicability"] = applicability
            predicate["evidence_status"] = "SATISFIED" if applicability == "APPLICABLE" else "NOT_REQUIRED"
            return
        raise ValueError(f"unsupported predicate probe reason: {problem}")

    if reason.startswith("ambiguity:") and reason.endswith(":open"):
        ambiguity_id = reason[len("ambiguity:") : -len(":open")]
        item = next((a for a in transition["ambiguities"] if a["ambiguity_id"] == ambiguity_id), None)
        if item is None:
            raise ValueError(f"active probe ambiguity not found: {ambiguity_id}")
        item["status"] = "RESOLVED"
        return

    if reason.startswith("discovered_unknown:") and reason.endswith(":open"):
        unknown_id = reason[len("discovered_unknown:") : -len(":open")]
        item = next((u for u in transition["discovered_unknowns"] if u["unknown_id"] == unknown_id), None)
        if item is None:
            raise ValueError(f"active probe discovered unknown not found: {unknown_id}")
        item["status"] = "RESOLVED"
        return

    raise ValueError(f"unsupported active probe reason: {reason}")


def execute_active_probes(
    *,
    state_transition: Mapping[str, Any],
    ingress_manifest: Mapping[str, Any],
    executor: ProbeExecutor,
) -> dict[str, Any]:
    """Execute current probes for all unresolved represented transition reasons.

    The executor is supplied by the runtime integration layer and is not read from
    the ingress manifest. Each returned result is bound to one exact derived reason.
    The function then re-normalizes transition evidence so readiness is derived,
    never assigned by a probe or caller.
    """
    if not callable(executor):
        raise ValueError("active probe executor must be callable")
    transition = normalize_state_transition_evidence(state_transition)
    reasons = list(transition.get("probe_reasons") or [])
    if not reasons:
        return {
            "transition": transition,
            "probe_results": [],
            "readiness_before_probe": transition["readiness"],
            "readiness_after_probe": transition["readiness"],
            "authority_effect": "NONE",
        }

    results: list[dict[str, Any]] = []
    working = deepcopy(transition)
    for reason in reasons:
        raw = executor(reason, deepcopy(dict(ingress_manifest)))
        result = _validated_result(reason, raw)
        _apply_probe_result(working, reason, result)
        results.append(result)

    # Claimed/derived fields from the prior normalization must be removed before
    # deriving readiness again from the newly resolved represented evidence.
    working.pop("readiness", None)
    working.pop("probe_reasons", None)
    working.pop("evidence_grants_authority", None)
    working.pop("unknown_unknown_policy", None)
    resolved = normalize_state_transition_evidence(working)
    return {
        "transition": resolved,
        "probe_results": results,
        "readiness_before_probe": transition["readiness"],
        "readiness_after_probe": resolved["readiness"],
        "authority_effect": "NONE",
    }


__all__ = [
    "ACTIVE_PROBE_RESULT_PROFILE",
    "ProbeExecutor",
    "execute_active_probes",
]
