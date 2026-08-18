"""Evaluator-neutral manifest route resolution for governed SDK execution.

A manifest establishes the intended route. This module recognizes only published
route declarations and never substitutes a different route. A recognized route
must also have an installed runtime binding before execution may proceed.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

ROUTE_DECLARATION_EXTENSION = "stegverse_route"
CANONICAL_PRODUCTION_ROUTE_ID = "stegverse.route.canonical-governed.v1"

_ROUTE_FIELDS = (
    "route_id",
    "lane_class",
    "routing_surface",
    "containment",
    "sandbox_required",
    "external_consequence_enabled",
)
_ROUTE_MATCH_FIELDS = tuple(field for field in _ROUTE_FIELDS if field != "route_id")

PUBLISHED_ROUTES: dict[str, dict[str, Any]] = {
    CANONICAL_PRODUCTION_ROUTE_ID: {
        "route_id": CANONICAL_PRODUCTION_ROUTE_ID,
        "lane_class": "PRODUCTION_VALIDATION",
        "routing_surface": "CANONICAL_PRODUCTION",
        "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
        "sandbox_required": False,
        "external_consequence_enabled": False,
        "runtime_binding": "core_lite.default_validation_route",
        "runtime_installed": True,
    },
}

STATE_BINDING_FIELDS = (
    "candidate",
    "judgment",
    "signal",
    "execution",
    "capability",
    "continuity",
    "approval",
    "permission_present",
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def governance_state_projection(request: Mapping[str, Any]) -> dict[str, Any]:
    """Return the exact governance-relevant state bound to a declared route."""
    return {field: request.get(field) for field in STATE_BINDING_FIELDS}


def governance_state_hash(request: Mapping[str, Any]) -> str:
    return canonical_sha256(governance_state_projection(request))


def resolve_route_declaration(declaration: Any) -> dict[str, Any]:
    """Resolve one explicit manifest route declaration without inventing semantics."""
    if not isinstance(declaration, Mapping):
        raise ValueError(
            f"manifest requires extensions.{ROUTE_DECLARATION_EXTENSION} declaring a published route"
        )
    unknown = sorted(set(declaration) - set(_ROUTE_FIELDS))
    if unknown:
        raise ValueError("unknown route declaration fields: " + ", ".join(unknown))
    missing = [field for field in _ROUTE_FIELDS if field not in declaration]
    if missing:
        raise ValueError("missing route declaration fields: " + ", ".join(missing))

    route_id = declaration.get("route_id")
    if not isinstance(route_id, str) or route_id not in PUBLISHED_ROUTES:
        raise ValueError(f"unsupported manifest route: {route_id!r}")
    published = PUBLISHED_ROUTES[route_id]
    for field in _ROUTE_FIELDS:
        if declaration.get(field) != published[field]:
            raise ValueError(
                f"manifest route {route_id} conflicts with published {field}: "
                f"expected {published[field]!r}, got {declaration.get(field)!r}"
            )
    if not published.get("runtime_installed"):
        raise ValueError(f"manifest route is published but runtime binding is not installed: {route_id}")

    resolved = {field: published[field] for field in _ROUTE_FIELDS}
    resolved["route_declaration_hash"] = canonical_sha256(resolved)
    resolved["runtime_binding"] = published["runtime_binding"]
    resolved["route_recognized"] = True
    resolved["route_substitution_permitted"] = False
    return resolved


def route_from_manifest(canonical_manifest: Mapping[str, Any]) -> dict[str, Any]:
    extensions = canonical_manifest.get("extensions")
    if not isinstance(extensions, Mapping):
        raise ValueError("manifest extensions must be an object")
    return resolve_route_declaration(extensions.get(ROUTE_DECLARATION_EXTENSION))


def _route_id_from_legacy_tuple(provenance: Mapping[str, Any]) -> str:
    matches = []
    for route_id, published in PUBLISHED_ROUTES.items():
        if all(provenance.get(field) == published[field] for field in _ROUTE_MATCH_FIELDS):
            matches.append(route_id)
    if len(matches) != 1:
        raise ValueError("execution_provenance does not identify exactly one published route")
    return matches[0]


def validate_runtime_provenance(provenance: Any) -> dict[str, Any]:
    """Re-resolve runtime provenance and prove it identifies one installed route.

    Older 0A requests may omit ``route_id`` but already declare the full route
    tuple. They are accepted only when that tuple maps uniquely to one published
    route. 0B manifests are required to carry an explicit route_id.
    """
    if not isinstance(provenance, Mapping):
        raise ValueError("execution_provenance must be an object")
    route_id = provenance.get("route_id")
    if route_id is None:
        route_id = _route_id_from_legacy_tuple(provenance)
    declaration = {"route_id": route_id}
    declaration.update({field: provenance.get(field) for field in _ROUTE_MATCH_FIELDS})
    resolved = resolve_route_declaration(declaration)
    supplied_hash = provenance.get("route_declaration_hash")
    if supplied_hash is not None and supplied_hash != resolved["route_declaration_hash"]:
        raise ValueError("execution_provenance route_declaration_hash does not match resolved route")
    return resolved
