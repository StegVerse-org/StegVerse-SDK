"""Source-only installed-capability discovery and requirement qualification.

This module derives capability inventory from the canonical published SDK route table.
It never grants execution authority, substitutes a route, or treats source installation
as proof of an observed runtime transition.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from .route_resolution import PUBLISHED_ROUTES

DISPOSITIONS = {
    "SUPPORTED",
    "MISSING_INPUT",
    "UNSUPPORTED",
    "PROBE_REQUIRED",
    "VERSION_INCOMPATIBLE",
}

def _sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def installed_capability_inventory() -> tuple[dict[str, Any], ...]:
    rows = []
    for route_id, route in sorted(PUBLISHED_ROUTES.items()):
        rows.append({
            "capability_id": route["processor_capability"],
            "route_id": route_id,
            "runtime_binding": route.get("runtime_binding"),
            "runtime_installed": route.get("runtime_installed") is True,
            "lane_class": route.get("lane_class"),
            "routing_surface": route.get("routing_surface"),
            "containment": route.get("containment"),
            "external_consequence_enabled": route.get("external_consequence_enabled") is True,
            "execution_authorized": False,
            "route_substitution_permitted": False,
            "evidence_ceiling": "SOURCE_DECLARATION_ONLY",
        })
    return tuple(rows)

def qualify_requirements(
    manifest: Mapping[str, Any],
    requirements: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    inventory = installed_capability_inventory()
    by_capability: dict[str, list[dict[str, Any]]] = {}
    for row in inventory:
        by_capability.setdefault(row["capability_id"], []).append(row)

    results = []
    for req in requirements:
        req_id = req.get("requirement_id")
        capability = req.get("capability_id")
        route_id = req.get("route_id")
        required_inputs = tuple(req.get("required_inputs") or ())
        missing = [name for name in required_inputs if name not in manifest]
        disposition = "SUPPORTED"
        predicate = "INSTALLED_CAPABILITY_AND_ROUTE_MATCH"
        correction = None
        matched = None

        if missing:
            disposition = "MISSING_INPUT"
            predicate = "REQUIRED_INPUT_PRESENT"
            correction = {"supply_inputs": missing}
        elif capability not in by_capability:
            disposition = "UNSUPPORTED"
            predicate = "CAPABILITY_INSTALLED"
            correction = {"request_supported_capability": sorted(by_capability)}
        else:
            candidates = by_capability[capability]
            if route_id is not None:
                matched = next((row for row in candidates if row["route_id"] == route_id), None)
                if matched is None:
                    disposition = "UNSUPPORTED"
                    predicate = "EXACT_ROUTE_INSTALLED"
                    correction = {"supported_routes": sorted(row["route_id"] for row in candidates)}
            else:
                matched = candidates[0]

        if disposition == "SUPPORTED" and matched is not None and not matched["runtime_installed"]:
            disposition = "UNSUPPORTED"
            predicate = "RUNTIME_BINDING_INSTALLED"
            correction = {"install_declared_runtime_binding": matched["route_id"]}

        if disposition == "SUPPORTED" and req.get("version_compatible") is False:
            disposition = "VERSION_INCOMPATIBLE"
            predicate = "REQUESTED_VERSION_COMPATIBLE"
            correction = {"use_compatible_version": True}
        elif disposition == "SUPPORTED" and req.get("authentic_runtime_evidence_required") is True:
            disposition = "PROBE_REQUIRED"
            predicate = "AUTHENTIC_RUNTIME_EVIDENCE_OBSERVED"
            correction = {"invoke_existing_manifest_directed_transition": True}

        results.append({
            "requirement_id": req_id,
            "capability_id": capability,
            "requested_route_id": route_id,
            "disposition": disposition,
            "failed_predicate": None if disposition == "SUPPORTED" else predicate,
            "matched": matched,
            "permitted_correction": correction,
        })

    return {
        "schema": "stegverse.sdk-capability-qualification/v1",
        "manifest_sha256": _sha256(manifest),
        "inventory": inventory,
        "results": tuple(results),
        "execution_authorized": False,
        "route_substitution_permitted": False,
    }
