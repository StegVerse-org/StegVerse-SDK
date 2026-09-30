"""Dispatch an Ecosystem Chat entry request to the operation it names.

The Chat entry contract has named operations since the parity work, but nothing
called it: the deployed surface accepted one payload shape and ran one fixed
pipeline, so a capability could be declared reachable at Chat while the surface
served none of it. This module is the missing dispatch.

It is deliberately explicit about the difference between an operation the entry
contract carries and one this surface actually serves. An operation that is
declared but not yet wired returns a stated reason rather than a stub answer,
because a surface that silently accepts an operation it cannot perform is the
same overclaim in a new place.

Non-authorizing. Dispatch validates and routes; it mints no receipt and grants
no admission.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from .ecosystem_chat_ask import answer_summary, ask_governed_question
from .ecosystem_chat_entry import (
    ASK,
    OPERATIONS,
    SCHEMA as ENTRY_SCHEMA,
    console_equivalent_request,
    validate_chat_entry,
)
from .governed_llm_fan import BranchExecutor

#: Operations performed by the node running Chat today. Everything else in
#: OPERATIONS is carried by the entry contract but not yet performed here, and
#: says so.
#:
#: "Served" is a property of the registered node, not of a host or a device: any
#: browser UI running Ecosystem Chat is itself a physical StegBrowser node, so
#: what conditions an operation is transportability, conferred by registration.
#: Nothing here may be gated on which device the node was established on.
SERVED_OPERATIONS: frozenset[str] = frozenset({ASK})

NOT_SERVED = "OPERATION_NOT_SERVED_BY_THIS_SURFACE"
NOT_SERVED_REPAIR = (
    "wire the operation's handler into stegverse.ecosystem_chat_operations, or "
    "reach it from a console entry, which serves it today"
)


class ChatOperationError(ValueError):
    """Raised when a request is not a dispatchable chat entry at all."""


def is_entry_request(body: Any) -> bool:
    """True when a request body is an entry-contract request rather than the
    historical pipeline payload, so the existing surface keeps its behaviour."""
    return isinstance(body, Mapping) and body.get("schema") == ENTRY_SCHEMA


def _not_served(entry: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "schema": "stegverse.ecosystem-chat-operation-result/v1",
        "operation": entry["operation"],
        "capability": entry["capability"],
        "served": False,
        "disposition": NOT_SERVED,
        "failed_predicate": "CHAT_SURFACE_SERVES_DECLARED_OPERATION",
        "required_evidence_or_repair": NOT_SERVED_REPAIR,
        "retry_entrypoint": "stegverse.ecosystem_chat_operations.handle_chat_entry",
        "served_operations": sorted(SERVED_OPERATIONS),
        "device_identity_gate": "NONE_PROHIBITED",
        "console_equivalent_request": console_equivalent_request(entry),
        "authority_effect": "NONE",
    }


def handle_chat_entry(
    payload: Mapping[str, Any] | None,
    *,
    executor: Optional[BranchExecutor] = None,
    joint_relation: Mapping[str, Any] | None = None,
) -> tuple[int, Dict[str, Any]]:
    """Validate an entry request and perform it when this surface serves it.

    Returns an HTTP-style status with the operation result. 200 for an answered
    question, 422 for one that could not be answered, and 501 for an operation
    the contract declares but this surface does not yet serve.
    """
    entry = validate_chat_entry(payload)
    operation = entry["operation"]

    if operation not in SERVED_OPERATIONS:
        return 501, _not_served(entry)

    request = entry["ask_request"]
    answer = ask_governed_question(
        request["question"],
        request["journey"],
        executor=executor,
        strategy=request["strategy"],
        joint_relation=joint_relation,
    )
    result = {
        "schema": "stegverse.ecosystem-chat-operation-result/v1",
        "operation": operation,
        "capability": OPERATIONS[operation],
        "served": True,
        "disposition": answer["disposition"],
        "answer": answer,
        "summary": answer_summary(answer),
        "verification": entry["verification"],
        "originating_entry_point": entry["entry_point"],
        "performed_by": "REGISTERED_NODE_RUNNING_CHAT",
        "device_identity_gate": "NONE_PROHIBITED",
        "authority_effect": "NONE",
    }
    return (200 if answer["governed_claim"] else 422), result


__all__ = [
    "ENTRY_SCHEMA", "NOT_SERVED", "NOT_SERVED_REPAIR", "SERVED_OPERATIONS",
    "ChatOperationError", "handle_chat_entry", "is_entry_request",
]
