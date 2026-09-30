"""Declared capability graph: manifest-declared capability sets and their closure.

``capability_resolution`` classifies one capability against the installed route
table. A submitting framework that needs several capabilities has no way to say
so: ``processing.capability`` is a scalar and ``manifest_builder`` binds it
through a fixed branch per capability. Expanding the reachable set therefore
means editing the SDK, not declaring anything.

This module lets the manifest declare the set instead. The declaration names a
root capability, the capabilities it needs, and the ``requires`` edges between
them. Resolution computes the closure from the root and classifies every member
against the installed routes, so the admitted set is exactly what was declared
and nothing wider.

Declaration is not creation. A declared capability the SDK does not install
resolves to the existing capability-development request, never to an admission,
and a requirement the declaration did not state is a fail-closed defect rather
than an implicit grant - declaring a capability does not declare what it needs.

Non-authorizing. Source resolution only: it installs nothing, binds no route,
substitutes no route, and observes no runtime.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .capability_resolution import (
    OFFLINE,
    ONLINE,
    UNKNOWN_CAPABILITY,
    capability_development_request,
    classify_capability,
)
from .governance_navigation import canonical_sha256

CAPABILITY_GRAPH_SCHEMA = "stegverse.capability-graph.v1"
RESOLUTION_SCHEMA = "stegverse.capability-graph-resolution.v1"
EXTENSION_KEY = "capability_graph"

# Resolution verdicts.
CLOSURE_RESOLVED = "DECLARED_CLOSURE_RESOLVED"
CLOSURE_MEMBER_UNKNOWN = "CLOSURE_MEMBER_UNKNOWN_CAPABILITY"
CLOSURE_MEMBER_OFFLINE = "CLOSURE_MEMBER_OFFLINE"

# Fail-closed declaration defects. These are graph semantics rather than shape,
# so they are reported as verdicts an external submitter can receipt, not raised.
UNDECLARED_REQUIREMENT = "UNDECLARED_REQUIREMENT_REACHED"
UNREACHED_DECLARATION = "DECLARED_CAPABILITY_NOT_REACHED_FROM_ROOT"
REQUIREMENT_CYCLE = "REQUIREMENT_CYCLE_DETECTED"

DEFECT_VERDICTS = (UNDECLARED_REQUIREMENT, UNREACHED_DECLARATION, REQUIREMENT_CYCLE)

# A declared closure can be wider than what ingress can currently carry. Where
# acting on the declaration would need ingress that does not exist yet, the
# behaviour sits behind a toggle that ships disabled: the declaration still
# resolves structurally and its members are still classified, but the verdict
# stops short of resolved and names what ingress must provide first.
#
# Every resolution records the toggles that were in force when it was evaluated,
# so a record never implies a capability the ingress of the day did not have.
CLOSURE_AWAITING_INGRESS = "MULTI_MEMBER_CLOSURE_AWAITING_INGRESS_CAPABILITY"

INGRESS_TOGGLES: Mapping[str, bool] = {
    # A closure with more than one member needs ingress that binds and executes
    # more than one processor for a single manifest, and a receipt chain that
    # distinguishes the members. `manifest_builder` binds exactly one processor
    # per manifest today, so a multi-member closure is declaration-only.
    "multi_member_closure_execution": False,
}

PENDING_INGRESS_DEVELOPMENT = {
    "multi_member_closure_execution": (
        "MANIFEST_BINDS_ONE_PROCESSOR_PER_SUBMISSION",
        "NO_PER_MEMBER_EXECUTION_BINDING",
        "NO_PER_MEMBER_RECEIPT_CHAIN",
    ),
}

AUTHORITY_BOUNDARY = {
    "declaration_creates_capability": False,
    "closure_membership_grants_execution": False,
    "resolution_grants_authority": False,
    "wider_closure_admits_undeclared_member": False,
    "sdk_substitutes_unresolved_member": False,
}

_ALLOWED_KEYS = {
    "schema",
    "graph_id",
    "root_capability",
    "declared_capabilities",
    "requires",
    "metadata",
}


class CapabilityGraphError(ValueError):
    """Raised when a capability-graph declaration is structurally invalid."""


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CapabilityGraphError(f"{field} is required")
    return value.strip()


def _normalize_capability(value: Any, field: str) -> str:
    return _require_text(value, field).lower()


def validate_capability_graph(value: Any) -> dict[str, Any]:
    """Validate the shape of a declared capability graph.

    Structural problems raise. Graph-semantic problems (an undeclared
    requirement, an unreached declaration, a cycle) are left for
    ``resolve_declared_capabilities`` to report as fail-closed verdicts.
    """
    if not isinstance(value, Mapping):
        raise CapabilityGraphError("capability graph must be an object")
    graph = dict(value)
    unknown = sorted(set(graph) - _ALLOWED_KEYS)
    if unknown:
        raise CapabilityGraphError(f"unsupported capability graph keys: {', '.join(unknown)}")
    if graph.get("schema") != CAPABILITY_GRAPH_SCHEMA:
        raise CapabilityGraphError("unsupported capability graph schema")

    graph_id = _require_text(graph.get("graph_id"), "graph_id")
    root = _normalize_capability(graph.get("root_capability"), "root_capability")

    declared_raw = graph.get("declared_capabilities")
    if not isinstance(declared_raw, list) or not declared_raw:
        raise CapabilityGraphError("declared_capabilities must be a non-empty array")
    declared: list[str] = []
    for item in declared_raw:
        name = _normalize_capability(item, "declared_capabilities entry")
        if name not in declared:
            declared.append(name)
    declared.sort()

    requires_raw = graph.get("requires", {})
    if not isinstance(requires_raw, Mapping):
        raise CapabilityGraphError("requires must be an object")
    requires: dict[str, list[str]] = {}
    for key, targets in requires_raw.items():
        source = _normalize_capability(key, "requires key")
        if source not in declared:
            raise CapabilityGraphError(
                f"requires names {source!r}, which is not a declared capability"
            )
        if not isinstance(targets, list):
            raise CapabilityGraphError(f"requires[{source!r}] must be an array")
        edges: list[str] = []
        for target in targets:
            name = _normalize_capability(target, f"requires[{source!r}] entry")
            if name == source:
                raise CapabilityGraphError(f"capability {source!r} cannot require itself")
            if name not in edges:
                edges.append(name)
        requires[source] = sorted(edges)

    metadata = graph.get("metadata")
    if metadata is not None and not isinstance(metadata, Mapping):
        raise CapabilityGraphError("metadata must be an object")

    normalized: dict[str, Any] = {
        "schema": CAPABILITY_GRAPH_SCHEMA,
        "graph_id": graph_id,
        "root_capability": root,
        "declared_capabilities": declared,
        "requires": requires,
    }
    if metadata is not None:
        normalized["metadata"] = deepcopy(dict(metadata))
    return normalized


def _walk_closure(graph: Mapping[str, Any]) -> tuple[list[str], str | None, str | None]:
    """Iterative depth-first closure from the root.

    Returns ``(closure, defect, detail)``, where ``defect`` is ``None`` when the
    declaration is closed and acyclic. The walk is iterative because the
    declaration is untrusted external input and its depth is not bounded by the
    SDK.
    """
    root = graph["root_capability"]
    declared = set(graph["declared_capabilities"])
    requires: Mapping[str, list[str]] = graph["requires"]

    if root not in declared:
        return [], UNDECLARED_REQUIREMENT, root

    closure: list[str] = []
    finished: set[str] = set()
    on_path: list[str] = []
    in_path: set[str] = set()
    # Each frame is (node, index of the next requirement to visit).
    stack: list[list[Any]] = [[root, 0]]
    on_path.append(root)
    in_path.add(root)

    while stack:
        node, index = stack[-1]
        edges = requires.get(node, ())
        if index >= len(edges):
            stack.pop()
            on_path.pop()
            in_path.discard(node)
            finished.add(node)
            closure.append(node)
            continue
        stack[-1][1] = index + 1
        target = edges[index]
        if target in in_path:
            cycle = " -> ".join(on_path[on_path.index(target):] + [target])
            return [], REQUIREMENT_CYCLE, cycle
        if target in finished:
            continue
        if target not in declared:
            return [], UNDECLARED_REQUIREMENT, target
        stack.append([target, 0])
        on_path.append(target)
        in_path.add(target)

    unreached = sorted(declared - set(closure))
    if unreached:
        return [], UNREACHED_DECLARATION, ", ".join(unreached)
    return sorted(closure), None, None


def closure_component_ids(graph: Mapping[str, Any], closure: list[str]) -> list[str]:
    """Component ids for a resolved closure, for composition coverage binding.

    A member ``c`` of graph ``G`` is component ``"G:c"``, matching how
    ``joint_relation`` derives a component set from a declared branch set.
    """
    graph_id = graph["graph_id"]
    return [f"{graph_id}:{name}" for name in closure]


def resolve_declared_capabilities(
    declaration: Any,
    *,
    processor_routes: Mapping[str, str],
    published_routes: Mapping[str, Mapping[str, Any]],
    source_framework: str = "",
    source_output_id: str = "",
    processor_request: Mapping[str, Any] | None = None,
    ingress_toggles: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Resolve a declared capability set against the installed route table.

    The admitted set is the closure of the declaration from its root, never
    wider. Any member the SDK does not install leaves the whole closure
    unresolved.
    """
    graph = validate_capability_graph(declaration)
    declaration_sha256 = canonical_sha256(graph)

    coverage = {
        "covers_graph_id": graph["graph_id"],
        "covers_root_capability": graph["root_capability"],
        "covers_declaration_sha256": declaration_sha256,
    }
    toggles = dict(INGRESS_TOGGLES)
    if ingress_toggles is not None:
        unknown_toggles = sorted(set(ingress_toggles) - set(INGRESS_TOGGLES))
        if unknown_toggles:
            raise CapabilityGraphError(
                f"unknown ingress toggles: {', '.join(unknown_toggles)}"
            )
        toggles.update({key: bool(value) for key, value in ingress_toggles.items()})

    base: dict[str, Any] = {
        "schema": RESOLUTION_SCHEMA,
        "graph_id": graph["graph_id"],
        "root_capability": graph["root_capability"],
        "declared_capabilities": list(graph["declared_capabilities"]),
        "coverage": deepcopy(coverage),
        "authority_boundary": deepcopy(AUTHORITY_BOUNDARY),
        "authority_effect": "NONE_RESOLUTION_ONLY",
        "ingress_toggles": dict(toggles),
    }

    closure, defect, detail = _walk_closure(graph)
    if defect is not None:
        return {
            **base,
            "verdict": defect,
            "defect_detail": detail,
            "closure": [],
            "member_resolutions": [],
            "resolved": False,
            "solution_required": True,
            "next_action": "REPAIR_CAPABILITY_GRAPH_DECLARATION",
        }

    members: list[dict[str, Any]] = []
    unknown: list[str] = []
    offline: list[str] = []
    for name in closure:
        resolution = classify_capability(name, processor_routes, published_routes)
        members.append(resolution)
        if resolution["status"] == UNKNOWN_CAPABILITY:
            unknown.append(name)
        elif resolution["status"] == OFFLINE:
            offline.append(name)

    result: dict[str, Any] = {
        **base,
        "closure": list(closure),
        "closure_component_ids": closure_component_ids(graph, closure),
        "member_resolutions": members,
    }

    if unknown:
        requests = [
            capability_development_request(
                capability=name,
                processor_request=processor_request if processor_request is not None else {},
                source_framework=source_framework,
                source_output_id=source_output_id,
            )
            for name in unknown
        ]
        return {
            **result,
            "verdict": CLOSURE_MEMBER_UNKNOWN,
            "unknown_members": list(unknown),
            "capability_development_requests": requests,
            "resolved": False,
            "solution_required": True,
            "next_action": "CREATE_CAPABILITY_DEVELOPMENT_DEPLOYMENT_REQUEST",
        }

    if offline:
        return {
            **result,
            "verdict": CLOSURE_MEMBER_OFFLINE,
            "offline_members": list(offline),
            "resolved": False,
            "solution_required": True,
            "next_action": "ATTEMPT_GOVERNED_WORKAROUND_SELECTION",
        }

    if len(closure) > 1 and not toggles["multi_member_closure_execution"]:
        return {
            **result,
            "verdict": CLOSURE_AWAITING_INGRESS,
            "gated_by_toggle": "multi_member_closure_execution",
            "pending_ingress_development": list(
                PENDING_INGRESS_DEVELOPMENT["multi_member_closure_execution"]
            ),
            "members_would_resolve": True,
            "resolved": False,
            "solution_required": True,
            "next_action": "DEVELOP_MULTI_MEMBER_INGRESS_BEFORE_ENABLING_TOGGLE",
        }

    return {
        **result,
        "verdict": CLOSURE_RESOLVED,
        "route_ids": [member["route_id"] for member in members],
        "resolved": True,
        "solution_required": False,
        "next_action": "BUILD_AND_SUBMIT_MANIFEST",
    }
