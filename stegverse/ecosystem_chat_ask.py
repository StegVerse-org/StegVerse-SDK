"""Answer a question in Ecosystem Chat with a governed multi-LLM response.

Ecosystem Chat is an LLM-style interface for anything about the ecosystem. This
is the path that makes it one: a question fans to N branches, each calling a
different LLM through the StegBrowser owner, and the answers compose into one
governed response the asker can verify from a phone.

That is Test 6 wired as a product rather than a demonstration. The same shape
serves any domain-scoped assistant built on it -- veterans claims, then
benefits, then VA-wide -- because nothing here knows what the question is about.
The domain is the routes and the question, never this module.

No worker is in the path. The fan runs in the SDK and the LLM interaction stays
with the StegBrowser owner behind an injected executor.

Non-authorizing. A governed answer is a composed, attributed, replayable
answer; it is not admission, not authority, and not a claim that the answer is
correct. Agreement among models is agreement, and the response says so.
"""

from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, List, Mapping, Optional, Sequence

from .governed_composite_response import (
    STRATEGIES,
    STRATEGY_UNANIMOUS,
    compose_governed_response,
    reconstruct_governed_response,
)
from .governed_llm_fan import BranchExecutor, run_governed_llm_fan
from .manifest_builder import build_manifest
from .stegbrowser_processor import JOURNEY_SCHEMA_V2

ANSWER_SCHEMA = "stegverse.ecosystem-chat-governed-answer/v1"

#: An ASK is the manifested data packet with its return already stated, which is
#: the Interlock/InTr shape: a transition declares its own return up front, so
#: the return is fully determined rather than observed afterwards. That makes
#: both digests derivable from the question and its routes -- the outbound
#: manifest states the return descriptor, the return manifest is that descriptor
#: plus the outbound's own digest, and each is hashed as a real document.
JOURNEY_PLANNING = "STATED_RETURN_INTERLOCK_INTR"
JOURNEY_PLANNING_BASIS = (
    "the outbound manifest states its return, so return_manifest_sha256 is "
    "computed from a fully determined document and predecessor-links to the "
    "outbound digest; nothing is observed to plan the journey"
)

OUTBOUND_MANIFEST_SCHEMA = "stegverse.ecosystem-chat-ask-outbound/v1"
RETURN_MANIFEST_SCHEMA = "stegverse.ecosystem-chat-ask-return/v1"

DISPOSITION_ANSWERED = "GOVERNED_ANSWER"
DISPOSITION_FAN_INCOMPLETE = "FAN_INCOMPLETE"
DISPOSITION_NOT_COMPOSED = "NOT_COMPOSED"

#: What the asker compares to check the answer without a console.
ANSWER_VERIFICATION_FIELDS: tuple[str, ...] = (
    "composite_sha256",
    "reconstructed_composite_sha256",
    "reconstruction_status",
    "selected_answer_sha256",
    "distinct_answer_count",
    "unanimous",
    "disposition",
    "governed_claim",
)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


class EcosystemChatAskError(ValueError):
    """Raised when a question cannot be turned into a fan at all."""


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EcosystemChatAskError(f"{name} must be a non-empty string")
    return value.strip()


def _outbound_manifest(
    *, question: str, branch_id: str, fan_journey_id: str, origin_endpoint: str,
    route: Mapping[str, Any], response_marker: str,
) -> Dict[str, Any]:
    """One branch's outbound manifest, which states its own return.

    Stating the return here is what makes the journey plannable: the return
    manifest is not something observed after the LLM answers, it is a document
    this manifest fully determines.
    """
    prompt = str(route.get("prompt") or question)
    return {
        "schema": OUTBOUND_MANIFEST_SCHEMA,
        "fan_journey_id": fan_journey_id,
        "branch_id": branch_id,
        "origin_endpoint": origin_endpoint,
        "ephemeral_endpoint": f"stegbrowser:ephemeral:{branch_id}",
        "question": question,
        "prompt": prompt,
        "provider": _text(route.get("provider"), "route provider"),
        "model": _text(route.get("model"), "route model"),
        "secure_url": _text(route.get("secure_url"), "route secure_url"),
        "response_marker": response_marker,
        # The return, stated in advance. A return that does not match this is
        # not this branch's return.
        "stated_return": {
            "schema": RETURN_MANIFEST_SCHEMA,
            "fan_journey_id": fan_journey_id,
            "branch_id": branch_id,
            "origin_endpoint": origin_endpoint,
            "response_marker": response_marker,
            "carries": ["response_commitment", "provider", "model", "journey_id"],
            "response_must_contain_marker": True,
            "consequence_reexecuted": False,
        },
    }


def _return_manifest(outbound: Mapping[str, Any], outbound_sha256: str) -> Dict[str, Any]:
    """The stated return, predecessor-linked to the outbound that stated it."""
    return {
        **dict(outbound["stated_return"]),
        "predecessor_manifest_sha256": outbound_sha256,
    }


def plan_ask_journey(
    question: str,
    routes: Sequence[Mapping[str, Any]],
    *,
    fan_journey_id: str,
    origin_endpoint: str = "stegverse:ecosystem-chat",
    marker_prefix: str = "ECOSYSTEM_CHAT",
) -> Dict[str, Any]:
    """Plan a v2 fan journey from a question and its routes.

    Each branch gets a real outbound manifest and the return that manifest
    states, and each digest is a hash of one of those documents rather than a
    placeholder. Because the return is stated rather than observed, planning
    needs nothing from the interaction it will later authorize.
    """
    asked = _text(question, "question")
    if len(routes) < 2:
        raise EcosystemChatAskError("a governed answer requires at least two routes")
    fan = _text(fan_journey_id, "fan_journey_id")

    branches: List[Dict[str, Any]] = []
    plans: List[Dict[str, Any]] = []
    for index, route in enumerate(routes):
        if not isinstance(route, Mapping):
            raise EcosystemChatAskError(f"route {index} must be an object")
        branch_id = _text(route.get("branch_id", f"b{index}"), f"route {index} branch_id")
        marker = f"{marker_prefix}-{fan}-{branch_id}"
        outbound = _outbound_manifest(
            question=asked, branch_id=branch_id, fan_journey_id=fan,
            origin_endpoint=origin_endpoint, route=route, response_marker=marker,
        )
        outbound_sha = _sha256(outbound)
        returned = _return_manifest(outbound, outbound_sha)
        return_sha = _sha256(returned)
        if return_sha == outbound_sha:
            raise EcosystemChatAskError("a stated return must differ from its outbound")

        branch: Dict[str, Any] = {
            "branch_id": branch_id,
            "ephemeral_endpoint": outbound["ephemeral_endpoint"],
            "outbound_manifest_sha256": outbound_sha,
            "return_manifest_sha256": return_sha,
            "return_predecessor_manifest_sha256": outbound_sha,
            "prompt": outbound["prompt"],
            "response_marker": marker,
            "provider": outbound["provider"],
            "model": outbound["model"],
            "secure_url": outbound["secure_url"],
        }
        actions = route.get("browser_actions")
        if actions is not None:
            branch["browser_actions"] = [dict(a) for a in actions]
        branches.append(branch)
        plans.append({
            "branch_id": branch_id,
            "outbound_manifest": outbound,
            "return_manifest": returned,
            "outbound_manifest_sha256": outbound_sha,
            "return_manifest_sha256": return_sha,
        })

    return {
        "schema": JOURNEY_SCHEMA_V2,
        "journey_id": fan,
        "origin_endpoint": origin_endpoint,
        "branches": branches,
        # The documents the digests are hashes of, so a reader can recompute
        # them rather than take the journey's word for it.
        "planned_manifests": plans,
        "planning_basis": JOURNEY_PLANNING,
    }


def verify_planned_journey(journey: Mapping[str, Any]) -> Dict[str, Any]:
    """Recompute every planned digest from its own document.

    A stated return is only a commitment if it can be checked, so this hashes
    the carried manifests again and reports whether the journey's digests match.
    """
    plans = journey.get("planned_manifests")
    if not isinstance(plans, list) or not plans:
        raise EcosystemChatAskError("journey carries no planned manifests to verify")
    rows: List[Dict[str, Any]] = []
    for plan in plans:
        outbound_sha = _sha256(plan["outbound_manifest"])
        returned = _return_manifest(plan["outbound_manifest"], outbound_sha)
        rows.append({
            "branch_id": plan["branch_id"],
            "outbound_matches": outbound_sha == plan["outbound_manifest_sha256"],
            "return_matches": _sha256(returned) == plan["return_manifest_sha256"],
            "return_predecessor_links": (
                plan["return_manifest"].get("predecessor_manifest_sha256") == outbound_sha
            ),
        })
    return {
        "branches": rows,
        "verified": all(
            row["outbound_matches"] and row["return_matches"]
            and row["return_predecessor_links"] for row in rows
        ),
        "basis": JOURNEY_PLANNING,
        "authority_effect": "NONE",
    }


def build_ask_manifest(
    question: str,
    journey: Mapping[str, Any],
    *,
    source_framework: str = "EcosystemChat",
    source_output_id: str = "governed-ask",
    data_class: str = "stegverse.ecosystem-chat-question.v1",
    default_response_marker: str = "ECOSYSTEM_CHAT_ANSWER",
    default_provider: str = "credential-free",
) -> Dict[str, Any]:
    """Build the ingress manifest whose fan answers one question.

    Chat interfaces with the builder; it does not build. This calls the same
    manifest builder a console entry calls, so both entry points hand the same
    manifest to the same processor.
    """
    asked = _text(question, "question")
    if not isinstance(journey, Mapping) or journey.get("schema") != JOURNEY_SCHEMA_V2:
        raise EcosystemChatAskError(f"ask journey schema must be {JOURNEY_SCHEMA_V2}")
    branches = journey.get("branches")
    if not isinstance(branches, list) or len(branches) < 2:
        raise EcosystemChatAskError("a governed answer requires at least two branches")

    return build_manifest(
        data={"question": asked},
        data_class=data_class,
        source_framework=source_framework,
        source_output_id=source_output_id,
        processor_request={
            "schema": "stegbrowser.llm-profile-request.v1",
            "profile": "llm.v1",
            # The question is the prompt; a branch may override it, and the
            # journey's own branch data decides provider, model and endpoint.
            "prompt": asked,
            "response_marker": default_response_marker,
            "provider": default_provider,
            "journey": dict(journey),
        },
        process="stegbrowser",
        return_depth="full-trace",
        publisher_required=False,
    )


def ask_governed_question(
    question: str,
    journey: Mapping[str, Any],
    *,
    executor: Optional[BranchExecutor] = None,
    strategy: str = STRATEGY_UNANIMOUS,
    joint_relation: Mapping[str, Any] | None = None,
    composition_id: Optional[str] = None,
    requester: str = "SDK:EcosystemChat",
) -> Dict[str, Any]:
    """Fan a question to N LLMs, compose one governed answer, and replay it.

    Returns the answer together with the fan's branch outcomes and the
    reconstruction result, so the asker verifies rather than trusts. A fan that
    did not complete never composes: an answer built from some of the workers
    would misrepresent how it was reached.
    """
    if strategy not in STRATEGIES:
        raise EcosystemChatAskError(f"unsupported strategy: {strategy}")

    manifest = build_ask_manifest(question, journey)
    fan = run_governed_llm_fan(manifest, executor=executor, requester=requester)

    answer: Dict[str, Any] = {
        "schema": ANSWER_SCHEMA,
        "question": _text(question, "question"),
        "fan_journey_id": fan["fan_journey_id"],
        "branch_count": fan["branch_count"],
        "branches": fan["branches"],
        "required_endpoint_receipts": fan["required_endpoint_receipts"],
        "observed_endpoint_receipts": fan["observed_endpoint_receipts"],
        "fan_complete": fan["complete"],
        "fan_sha256": fan["fan_sha256"],
        "strategy": strategy,
        "worker_in_path": False,
        "chat_builds_manifest": False,
        "chat_selects_answer": False,
        # A device is interchangeable. Any browser UI running Ecosystem Chat is
        # itself a physical StegBrowser node, so the fan is performed by the
        # registered node, and what conditions it is transportability -- never
        # which device the node was established on.
        "node": {
            "executed_by": "REGISTERED_NODE_RUNNING_CHAT",
            "any_browser_running_chat_is_a_stegbrowser_node": True,
            "device_identity_gate": "NONE_PROHIBITED",
            "transportability_conferred_by": "NODE_REGISTRATION",
            "transportability_conferred_by_device": False,
            "node_confers_user_verifier_authority": False,
            "user_verification_authority": "KV/SKAP Vault",
        },
        "journey_planning": {
            "basis": JOURNEY_PLANNING,
            "detail": JOURNEY_PLANNING_BASIS,
        },
        "boundary": {
            "answer_is_certified_correct": False,
            "agreement_is_evidence_of_correctness": False,
            "answer_grants_execution_authority": False,
            "composed_from_a_partial_fan": False,
        },
    }

    if not fan["complete"]:
        answer.update({
            "disposition": DISPOSITION_FAN_INCOMPLETE,
            "governed_claim": False,
            "answer": None,
            "composite": None,
            "replay": None,
            "failure": fan["failure"],
        })
        return answer

    composite = compose_governed_response(
        fan["components"],
        composition_id=composition_id or f"CHAT-{fan['fan_journey_id']}",
        fan_journey_id=fan["fan_journey_id"],
        strategy=strategy,
        joint_relation=joint_relation,
    )
    replay = reconstruct_governed_response(composite, fan["components"])

    answer.update({
        "disposition": (
            DISPOSITION_ANSWERED if composite["composite_answer"] is not None
            else DISPOSITION_NOT_COMPOSED
        ),
        "governed_claim": composite["governed_claim"],
        "answer": composite["composite_answer"],
        "composite": composite,
        "replay": replay,
        "failure": None,
        "verification": {
            "compare_fields": list(ANSWER_VERIFICATION_FIELDS),
            "verified_when": (
                "composite_sha256 equals reconstructed_composite_sha256 and "
                "reconstruction_status is RECONSTRUCTED"
            ),
            "legible_without_a_console": True,
        },
    })
    return answer


def answer_summary(answer: Mapping[str, Any]) -> Dict[str, Any]:
    """The few fields a chat surface shows, including how to check the answer."""
    composite = answer.get("composite") if isinstance(answer.get("composite"), Mapping) else {}
    replay = answer.get("replay") if isinstance(answer.get("replay"), Mapping) else {}
    return {
        "disposition": answer.get("disposition"),
        "answer": answer.get("answer"),
        "governed_claim": answer.get("governed_claim"),
        "models_asked": [
            f"{row.get('provider')}/{row.get('model')}"
            for row in answer.get("branches") or []
            if row.get("provider")
        ],
        "unanimous": composite.get("unanimous"),
        "distinct_answer_count": composite.get("distinct_answer_count"),
        "composite_sha256": composite.get("composite_sha256"),
        "reconstructed_composite_sha256": replay.get("reconstructed_composite_sha256"),
        "reconstruction_status": replay.get("reconstruction_status"),
        "agreement_is_evidence_of_correctness": False,
    }


__all__ = [
    "ANSWER_SCHEMA", "ANSWER_VERIFICATION_FIELDS", "DISPOSITION_ANSWERED",
    "DISPOSITION_FAN_INCOMPLETE", "DISPOSITION_NOT_COMPOSED",
    "EcosystemChatAskError", "JOURNEY_PLANNING", "JOURNEY_PLANNING_BASIS",
    "OUTBOUND_MANIFEST_SCHEMA", "RETURN_MANIFEST_SCHEMA", "answer_summary",
    "ask_governed_question", "build_ask_manifest", "plan_ask_journey",
    "verify_planned_journey",
]
