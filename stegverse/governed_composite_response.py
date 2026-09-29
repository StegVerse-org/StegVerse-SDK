"""Deterministic composition of N worker LLM answers into one governed response.

Test 6's shape: several workers each call a different LLM through StegBrowser to
answer one query, and one governed response comes back out. This module performs
that composition over ``stegbrowser.llm-profile-result.v1`` components.

Composition here is deterministic and non-generative. The composite answer is
always verbatim one of the component answers, selected by a declared strategy
over component agreement. Nothing is synthesized, so the composite is
recomputable from the components alone -- which is what makes it replayable.

What this module does not do: it does not execute a worker, call an LLM, grant
execution authority, or treat agreement among components as evidence of
correctness. Component admissibility is not lifted into composite
admissibility; a validated joint relation is a separate prerequisite, and
without one the composite is carried as RELATION_UNRESOLVED rather than as a
governed claim.
"""

from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence

COMPOSITE_SCHEMA = "stegverse.governed-composite-response.v1"
COMPONENT_SCHEMA = "stegbrowser.llm-profile-result.v1"
JOINT_RELATION_SCHEMA = "stegverse.governed_admissibility.joint_relation.v1"

STRATEGY_UNANIMOUS = "UNANIMOUS"
STRATEGY_MAJORITY = "MAJORITY"
STRATEGY_ATTRIBUTED_SET = "ATTRIBUTED_SET"
STRATEGIES = (STRATEGY_UNANIMOUS, STRATEGY_MAJORITY, STRATEGY_ATTRIBUTED_SET)

ANSWER_NORMALIZATION = "strip_own_response_marker_then_collapse_whitespace"

DISPOSITION_GOVERNED = "GOVERNED_COMPOSITE_RESPONSE"
DISPOSITION_RELATION_UNRESOLVED = "RELATION_UNRESOLVED"
DISPOSITION_FAIL_CLOSED = "FAIL_CLOSED"

FAILURE_COMPONENT_COMMITMENT = "COMPONENT_RESPONSE_COMMITMENT_MISMATCH"
FAILURE_COMPONENT_MARKER = "COMPONENT_RESPONSE_MISSING_ITS_MARKER"
FAILURE_COMPONENT_SCHEMA = "COMPONENT_SCHEMA_UNRECOGNIZED"
FAILURE_FOREIGN_FAN = "COMPONENT_JOURNEY_ID_OUTSIDE_DECLARED_FAN"
FAILURE_DUPLICATE_JOURNEY = "DUPLICATE_COMPONENT_JOURNEY_ID"
FAILURE_NO_UNANIMITY = "COMPONENTS_DIVERGE_UNDER_UNANIMOUS_STRATEGY"
FAILURE_NO_MAJORITY = "NO_STRICT_MAJORITY_ANSWER"

QUERY_BINDING_BASIS = "SHARED_FAN_JOURNEY_ID_PREFIX"
QUERY_BINDING_LIMIT = (
    "stegbrowser.llm-profile-result.v1 does not carry the prompt, and each "
    "branch's request_commitment covers its own provider, model, marker and "
    "journey_id, so it necessarily differs for every worker in a fan. Shared "
    "authorship of one query is therefore established by the fan journey_id "
    "the branches were issued under, not by a commitment over the query text."
)

_WHITESPACE = re.compile(r"\s+")


class CompositeResponseError(ValueError):
    """Raised when composition inputs cannot be composed at all."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    """Digest matching the component producer's own commitment form."""

    return "sha256:" + sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _normalized_answer(result: Mapping[str, Any]) -> str:
    """Return the answer with this component's own marker removed.

    Each branch of a fan carries its own response_marker, so two workers that
    returned substantively identical answers still differ byte for byte. Without
    removing each component's own marker, agreement could never be observed.
    """

    text = str(result.get("response_text") or "")
    marker = str(result.get("response_marker") or "")
    if marker:
        text = text.replace(marker, " ")
    return _WHITESPACE.sub(" ", text).strip()


def _component_failures(result: Mapping[str, Any]) -> List[str]:
    """Verify one component against its own commitment rather than its label."""

    failures: List[str] = []
    if result.get("schema") != COMPONENT_SCHEMA:
        failures.append(FAILURE_COMPONENT_SCHEMA)
        return failures

    marker = str(result.get("response_marker") or "")
    text = str(result.get("response_text") or "")
    if not marker or marker not in text:
        failures.append(FAILURE_COMPONENT_MARKER)

    supplied = result.get("response_commitment")
    recomputed = dict(result)
    recomputed.pop("response_commitment", None)
    if not isinstance(supplied, str) or supplied != _sha256(recomputed):
        failures.append(FAILURE_COMPONENT_COMMITMENT)
    return failures


def _validated_joint_relation(relation: Mapping[str, Any] | None) -> bool:
    if not isinstance(relation, Mapping):
        return False
    if relation.get("schema") != JOINT_RELATION_SCHEMA:
        return False
    if str(relation.get("relation_status") or "") != "validated":
        return False
    for key in ("relation_id", "authority_source"):
        value = relation.get(key)
        if not isinstance(value, str) or not value.strip():
            return False
    return (
        relation.get("evidence_posture") == "receipt_backed"
        and relation.get("replay_posture") == "receipt_backed"
    )


def _select(
    strategy: str, groups: Sequence[Mapping[str, Any]], component_count: int
) -> tuple[Optional[str], Optional[str]]:
    """Return (selected answer digest, failure code) for a declared strategy."""

    if strategy == STRATEGY_ATTRIBUTED_SET:
        return None, None
    if strategy == STRATEGY_UNANIMOUS:
        if len(groups) == 1:
            return str(groups[0]["answer_sha256"]), None
        return None, FAILURE_NO_UNANIMITY
    leaders = [g for g in groups if len(g["worker_journey_ids"]) * 2 > component_count]
    if len(leaders) == 1:
        return str(leaders[0]["answer_sha256"]), None
    return None, FAILURE_NO_MAJORITY


def compose_governed_response(
    components: Sequence[Mapping[str, Any]],
    *,
    composition_id: str,
    fan_journey_id: str,
    strategy: str = STRATEGY_UNANIMOUS,
    joint_relation: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Compose N verified worker answers into one reconstructable composite.

    Every component is verified against its own response_commitment and its own
    response marker, and must carry a distinct journey_id under the declared
    fan, so one worker's answer cannot be counted twice and a component from
    another fan cannot be folded in.

    ``fan_journey_id`` names the fan the branches were issued under. It is the
    only shared-query binding the component schema supports; see
    QUERY_BINDING_LIMIT for what that does and does not establish.
    """

    cid = str(composition_id or "").strip()
    if not cid:
        raise CompositeResponseError("composition_id_required")
    fan = str(fan_journey_id or "").strip()
    if not fan:
        raise CompositeResponseError("fan_journey_id_required")
    if strategy not in STRATEGIES:
        raise CompositeResponseError(f"unsupported strategy: {strategy}")
    if len(components) < 2:
        raise CompositeResponseError("composition_requires_at_least_two_components")

    failures: List[str] = []
    summaries: List[Dict[str, Any]] = []
    for index, component in enumerate(components):
        if not isinstance(component, Mapping):
            raise CompositeResponseError(f"component {index} must be a JSON object")
        component_failures = _component_failures(component)
        failures.extend(component_failures)
        summaries.append(
            {
                "journey_id": component.get("journey_id"),
                "provider": component.get("provider"),
                "model": component.get("model"),
                "request_commitment": component.get("request_commitment"),
                "response_commitment": component.get("response_commitment"),
                "answer_sha256": _sha256(_normalized_answer(component)),
                "integrity_valid": not component_failures,
                "integrity_failures": component_failures,
            }
        )

    summaries.sort(key=lambda item: str(item["journey_id"]))

    journey_ids = [str(item["journey_id"]) for item in summaries]
    if len(set(journey_ids)) != len(journey_ids):
        failures.append(FAILURE_DUPLICATE_JOURNEY)

    # A branch of this fan is journey_id "<fan>:<branch>". Anything else is a
    # component from somewhere other than the query being composed.
    if any(not jid.startswith(f"{fan}:") for jid in journey_ids):
        failures.append(FAILURE_FOREIGN_FAN)

    # Distinct answers, each naming every worker that returned it. Sorted so the
    # composite never depends on the order components arrived in.
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in summaries:
        grouped.setdefault(str(item["answer_sha256"]), []).append(item)
    groups = [
        {
            "answer_sha256": digest,
            "worker_journey_ids": sorted(str(m["journey_id"]) for m in members),
            "models": sorted({f"{m['provider']}/{m['model']}" for m in members}),
            "support_count": len(members),
        }
        for digest, members in grouped.items()
    ]
    groups.sort(key=lambda group: str(group["answer_sha256"]))

    selected_digest: Optional[str] = None
    if failures:
        disposition = DISPOSITION_FAIL_CLOSED
    else:
        selected_digest, selection_failure = _select(strategy, groups, len(summaries))
        if selection_failure:
            failures.append(selection_failure)
            disposition = DISPOSITION_FAIL_CLOSED
        elif _validated_joint_relation(joint_relation):
            disposition = DISPOSITION_GOVERNED
        else:
            disposition = DISPOSITION_RELATION_UNRESOLVED

    composite_answer: Optional[str] = None
    if selected_digest is not None and disposition != DISPOSITION_FAIL_CLOSED:
        for component in components:
            if _sha256(_normalized_answer(component)) == selected_digest:
                composite_answer = _normalized_answer(component)
                break

    composite: Dict[str, Any] = {
        "schema": COMPOSITE_SCHEMA,
        "composition_id": cid,
        "strategy": strategy,
        "disposition": disposition,
        "governed_claim": disposition == DISPOSITION_GOVERNED,
        "component_count": len(summaries),
        "components": summaries,
        "fan_journey_id": fan,
        "query_binding": {
            "basis": QUERY_BINDING_BASIS,
            "fan_journey_id": fan,
            "same_prompt_verified_from_components": False,
            "limit": QUERY_BINDING_LIMIT,
        },
        "distinct_answer_count": len(groups),
        "distinct_model_count": len(
            {f"{item['provider']}/{item['model']}" for item in summaries}
        ),
        "answer_groups": groups,
        "unanimous": len(groups) == 1,
        "selected_answer_sha256": selected_digest,
        "composite_answer": composite_answer,
        "failure_codes": sorted(set(failures)),
        "joint_relation_supplied": isinstance(joint_relation, Mapping),
        "joint_relation_valid": _validated_joint_relation(joint_relation),
        "reconstruction": {
            "answer_normalization": ANSWER_NORMALIZATION,
            "component_answer_digests": sorted(
                str(item["answer_sha256"]) for item in summaries
            ),
            "recomputable_from_components_alone": True,
        },
        "separability": {
            "component_admissibility_implies_composite_admissibility": False,
            "joint_relation_required_for_governed_claim": True,
        },
        "boundary": {
            "agreement_is_evidence_of_correctness": False,
            "composition_synthesizes_new_text": False,
            "composition_is_execution_authority": False,
            "composition_executes_components": False,
            "composition_calls_an_llm": False,
        },
    }
    composite["composite_sha256"] = _sha256(composite)
    return composite


def reconstruct_governed_response(
    composite: Mapping[str, Any],
    components: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Recompute a composite from its components and report whether it matches.

    This is the replay check. It re-derives the composite under the strategy the
    receipt declares and compares digests, so "reconstructable" is measured
    rather than asserted.
    """

    if composite.get("schema") != COMPOSITE_SCHEMA:
        raise CompositeResponseError(f"composite schema must be {COMPOSITE_SCHEMA}")

    relation = None
    if composite.get("joint_relation_valid"):
        relation = {
            "schema": JOINT_RELATION_SCHEMA,
            "relation_status": "validated",
            "relation_id": "reconstruction-placeholder",
            "authority_source": "reconstruction-placeholder",
            "evidence_posture": "receipt_backed",
            "replay_posture": "receipt_backed",
        }

    try:
        recomputed = compose_governed_response(
            components,
            composition_id=str(composite.get("composition_id") or ""),
            fan_journey_id=str(composite.get("fan_journey_id") or ""),
            strategy=str(composite.get("strategy") or ""),
            joint_relation=relation,
        )
    except CompositeResponseError as exc:
        return {
            "reconstruction_status": "FAILED",
            "reconstructed": False,
            "reason": str(exc),
            "claimed_composite_sha256": composite.get("composite_sha256"),
            "reconstructed_composite_sha256": None,
        }

    # The joint relation identity is not recoverable from the composite, so it
    # is excluded from the compared digest rather than guessed at.
    def _comparable(value: Mapping[str, Any]) -> Dict[str, Any]:
        stripped = dict(value)
        stripped.pop("composite_sha256", None)
        return stripped

    matches = _comparable(recomputed) == _comparable(composite)
    return {
        "reconstruction_status": "RECONSTRUCTED" if matches else "DIVERGED",
        "reconstructed": matches,
        "claimed_composite_sha256": composite.get("composite_sha256"),
        "reconstructed_composite_sha256": recomputed["composite_sha256"],
        "claimed_answer_sha256": composite.get("selected_answer_sha256"),
        "reconstructed_answer_sha256": recomputed["selected_answer_sha256"],
    }
