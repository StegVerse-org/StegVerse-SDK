"""Manifest bindings for collaborative ingress: Ecosystem Chat, VA-scoped chat, HIL intake.

Existing owner: SDK-MANIFEST-COLLAB-INGRESS-CONFORMANCE-001 (SDK#368 plan step 2).

Each surface is a manifest-selected processing capability on the existing
universal Interlock/InTr path, reached only through
``stegverse.manifest_execution.execute_manifest``. VA-scoped chat is the same
path as general Ecosystem Chat with a manifest-declared scope policy; a request
outside that policy is refused (DENY) before any handoff. The request rides
its extension beside ``extensions.stegverse_route`` and is never a top-level
manifest field.

Nothing here answers a chat message, records a human decision, transports a
request or grants authority. Math-solver and wiki-request ingress have no owner
task and are deliberately not published (see ``DEFERRED_INGRESS``).
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import (
    ECOSYSTEM_CHAT_ROUTE_ID,
    HIL_INTAKE_ROUTE_ID,
    VA_SCOPED_CHAT_ROUTE_ID,
    route_from_manifest,
)

OWNER_TASK_ID = "SDK-MANIFEST-COLLAB-INGRESS-CONFORMANCE-001"
ECOSYSTEM_CHAT_CAPABILITY = "ecosystem_chat"
VA_SCOPED_CHAT_CAPABILITY = "va_scoped_chat"
HIL_INTAKE_CAPABILITY = "hil_intake"

ECOSYSTEM_CHAT_REQUEST_EXTENSION = "stegverse_ecosystem_chat_request"
VA_SCOPED_CHAT_REQUEST_EXTENSION = "stegverse_va_scoped_chat_request"
HIL_INTAKE_REQUEST_EXTENSION = "stegverse_hil_intake_request"
ECOSYSTEM_CHAT_REQUEST_SCHEMA = "stegverse.ecosystem-chat-request/v1"
VA_SCOPED_CHAT_REQUEST_SCHEMA = "stegverse.va-scoped-chat-request/v1"
HIL_INTAKE_REQUEST_SCHEMA = "stegverse.hil-intake-request/v1"

#: Ingress surfaces named in the per-surface census that have no owner task.
#: They are recorded, not published: no route id, capability id or builder binding.
DEFERRED_INGRESS = {
    "math_solver": "NO_OWNER_TASK_FOR_MATH_SOLVER_ENTRY_BINDING",
    "admissibility_wiki_requests": "NO_OWNER_TASK_FOR_WIKI_REQUEST_INGRESS",
}

_CHAT_FIELDS = frozenset({"schema", "session_ref", "message", "requested_topic"})
_VA_FIELDS = _CHAT_FIELDS | {"va_scope"}
_VA_SCOPE_FIELDS = frozenset({"policy_id", "va_ref", "allowed_topics"})
_HIL_FIELDS = frozenset({"schema", "session_ref", "subject_ref", "requested_decision", "context_refs"})


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value


def _closed(value: Any, *, schema: str, fields: frozenset[str], capability: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{capability} processor_request must be an object")
    if value.get("schema") != schema:
        raise ValueError(f"{capability} request schema must be {schema}")
    unknown = sorted(set(value) - fields)
    if unknown:
        raise ValueError(f"unknown {capability} request fields: " + ", ".join(unknown))
    return value


def validate_ecosystem_chat_request(value: Any) -> dict[str, Any]:
    request = _closed(value, schema=ECOSYSTEM_CHAT_REQUEST_SCHEMA, fields=_CHAT_FIELDS,
                      capability=ECOSYSTEM_CHAT_CAPABILITY)
    for field in ("session_ref", "message", "requested_topic"):
        _text(request.get(field), field)
    return deepcopy(dict(request))


def validate_va_scoped_chat_request(value: Any) -> dict[str, Any]:
    """Structural admission only; the scope decision is made on the execution path."""
    request = _closed(value, schema=VA_SCOPED_CHAT_REQUEST_SCHEMA, fields=_VA_FIELDS,
                      capability=VA_SCOPED_CHAT_CAPABILITY)
    for field in ("session_ref", "message", "requested_topic"):
        _text(request.get(field), field)
    scope = request.get("va_scope")
    if not isinstance(scope, Mapping):
        raise ValueError("va_scope must be an object declaring the VA scope policy")
    unknown = sorted(set(scope) - _VA_SCOPE_FIELDS)
    if unknown:
        raise ValueError("unknown va_scope fields: " + ", ".join(unknown))
    _text(scope.get("policy_id"), "va_scope.policy_id")
    _text(scope.get("va_ref"), "va_scope.va_ref")
    topics = scope.get("allowed_topics")
    if not isinstance(topics, list) or not topics or not all(isinstance(t, str) and t.strip() for t in topics):
        raise ValueError("va_scope.allowed_topics must be a non-empty array of topics")
    return deepcopy(dict(request))


def validate_hil_intake_request(value: Any) -> dict[str, Any]:
    request = _closed(value, schema=HIL_INTAKE_REQUEST_SCHEMA, fields=_HIL_FIELDS, capability=HIL_INTAKE_CAPABILITY)
    for field in ("session_ref", "subject_ref", "requested_decision"):
        _text(request.get(field), field)
    refs = request.get("context_refs", [])
    if not isinstance(refs, list) or not all(isinstance(ref, str) and ref for ref in refs):
        raise ValueError("context_refs must be an array of references")
    return deepcopy(dict(request))


def va_scope_disposition(request: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate the manifest-declared VA scope policy. ALLOW or a governed DENY."""
    scope = request["va_scope"]
    topic = request["requested_topic"].strip()
    in_scope = topic in {t.strip() for t in scope["allowed_topics"]}
    return {
        "disposition": "ALLOW" if in_scope else "DENY",
        "failed_predicate": None if in_scope else "REQUESTED_TOPIC_WITHIN_MANIFEST_DECLARED_VA_SCOPE",
        "policy_id": scope["policy_id"],
        "va_ref": scope["va_ref"],
        "requested_topic": topic,
        "allowed_topics": list(scope["allowed_topics"]),
        "policy_source": "MANIFEST_DECLARED",
    }


_BINDINGS = {
    ECOSYSTEM_CHAT_CAPABILITY: (ECOSYSTEM_CHAT_ROUTE_ID, ECOSYSTEM_CHAT_REQUEST_EXTENSION, validate_ecosystem_chat_request),
    VA_SCOPED_CHAT_CAPABILITY: (VA_SCOPED_CHAT_ROUTE_ID, VA_SCOPED_CHAT_REQUEST_EXTENSION, validate_va_scoped_chat_request),
    HIL_INTAKE_CAPABILITY: (HIL_INTAKE_ROUTE_ID, HIL_INTAKE_REQUEST_EXTENSION, validate_hil_intake_request),
}


def derive_state_graph(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Request graph for one collaborative-ingress capability on the universal path."""
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    capability = route.get("processor_capability")
    if capability not in _BINDINGS:
        raise ValueError("COLLAB_INGRESS_ROUTE_NOT_PUBLISHED_FOR_CAPABILITY")
    route_id, extension, validate = _BINDINGS[capability]
    if route.get("route_id") != route_id:
        raise ValueError("COLLAB_INGRESS_MANIFEST_ROUTE_CAPABILITY_MISMATCH")
    if (canonical.get("processing") or {}).get("capability") != capability:
        raise ValueError(f"manifest processing capability does not select {capability}")
    request = validate((canonical.get("extensions") or {}).get(extension))
    graph = {
        "schema": "stegverse.sdk.installed-state-transition-graph/v1",
        "graph_id": f"{OWNER_TASK_ID}:{capability.upper()}:{request['session_ref']}",
        "canonical_task_id": None,
        "owner_task_id": OWNER_TASK_ID,
        "processing_capability": capability,
        "route_id": route_id,
        "request": request,
        "ordered_transitions": [],
        "ordered_transitions_source": "RECEIVING_ORGANIZATION_MANIFEST_INGRESS",
        "requires_workercoordinator_claim_fence": False,
        "predecessor_closure_required": True,
        "adapter_executes_lifecycle": False,
        "authority_effect": "NONE_GRAPH_DERIVATION_ONLY",
    }
    if capability == VA_SCOPED_CHAT_CAPABILITY:
        scope = va_scope_disposition(request)
        graph["va_scope_disposition"] = scope
        if scope["disposition"] == "DENY":
            graph["manifest_policy_refusal"] = {
                "evaluation_boundary": "SDK_MANIFEST_DECLARED_SCOPE_POLICY",
                "failed_predicate": scope["failed_predicate"],
                "evidence": scope,
            }
    if capability == HIL_INTAKE_CAPABILITY:
        # The human decision belongs to the receiving organization; nothing here decides.
        graph["human_decision_required"] = True
        graph["automated_consequence_permitted"] = False
    return graph


__all__ = [
    "DEFERRED_INGRESS", "OWNER_TASK_ID",
    "ECOSYSTEM_CHAT_CAPABILITY", "VA_SCOPED_CHAT_CAPABILITY", "HIL_INTAKE_CAPABILITY",
    "ECOSYSTEM_CHAT_REQUEST_EXTENSION", "VA_SCOPED_CHAT_REQUEST_EXTENSION", "HIL_INTAKE_REQUEST_EXTENSION",
    "ECOSYSTEM_CHAT_REQUEST_SCHEMA", "VA_SCOPED_CHAT_REQUEST_SCHEMA", "HIL_INTAKE_REQUEST_SCHEMA",
    "validate_ecosystem_chat_request", "validate_va_scoped_chat_request", "validate_hil_intake_request",
    "va_scope_disposition", "derive_state_graph",
]
