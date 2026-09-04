from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Any, Iterable


GRAPH_SCHEMA = "stegverse.mhia.capability_graph.v1"
MODULE_SCHEMA = "stegverse.mhia.module_manifest.v1"


class MHIACompositionError(ValueError):
    """Raised when module manifests cannot be composed safely."""


def _require_safe_authority_boundary(manifest: dict[str, Any]) -> None:
    boundary = manifest.get("authority_boundary") or {}
    if boundary.get("discovery_grants_authority") is not False:
        raise MHIACompositionError("discovery must not grant authority")
    if boundary.get("attachment_grants_authority") is not False:
        raise MHIACompositionError("attachment must not grant authority")
    if boundary.get("external_consequence_requires_admission") is not True:
        raise MHIACompositionError("external consequences must require admission")


def _normalize_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("schema") != MODULE_SCHEMA:
        raise MHIACompositionError("unsupported module manifest schema")
    module = manifest.get("module") or {}
    module_id = module.get("module_id")
    if not isinstance(module_id, str) or not module_id:
        raise MHIACompositionError("module_id is required")
    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise MHIACompositionError(f"{module_id}: capabilities are required")
    _require_safe_authority_boundary(manifest)
    return deepcopy(manifest)


def compose_capability_graph(manifests: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Compose deterministic, non-authorizing MHIA module discovery state.

    Composition discovers what is present. It never inherits, aggregates, or
    manufactures execution/governance authority from attachment or discovery.
    Exact duplicate capability declarations are represented as multiple
    providers. Incompatible declarations for the same capability id are
    retained as conflicts and are not exposed as usable capabilities.
    """

    normalized = [_normalize_manifest(m) for m in manifests]
    if not normalized:
        raise MHIACompositionError("at least one module manifest is required")

    normalized.sort(key=lambda m: m["module"]["module_id"])
    module_ids = [m["module"]["module_id"] for m in normalized]
    if len(module_ids) != len(set(module_ids)):
        raise MHIACompositionError("duplicate module_id")

    declarations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    modules: list[dict[str, Any]] = []

    for manifest in normalized:
        module = manifest["module"]
        module_id = module["module_id"]
        physical = manifest.get("physical_compatibility") or {}
        modules.append(
            {
                "module_id": module_id,
                "class": module.get("class"),
                "side": physical.get("side", "not_applicable"),
                "manufacturer": module.get("manufacturer"),
                "model": module.get("model"),
                "hardware_revision": module.get("hardware_revision"),
                "firmware_revision": module.get("firmware_revision"),
            }
        )
        for capability in manifest["capabilities"]:
            declarations[capability["id"]].append(
                {
                    "module_id": module_id,
                    "version": capability.get("version"),
                    "direction": capability.get("direction"),
                    "consequence_class": capability.get("consequence_class"),
                    "constraints": deepcopy(capability.get("constraints", {})),
                    "calibration_ref": capability.get("calibration_ref"),
                }
            )

    usable: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []

    for capability_id in sorted(declarations):
        providers = sorted(declarations[capability_id], key=lambda p: p["module_id"])
        signatures = {
            (
                p["version"],
                p["direction"],
                p["consequence_class"],
            )
            for p in providers
        }
        if len(signatures) > 1:
            conflicts.append(
                {
                    "capability_id": capability_id,
                    "reason": "INCOMPATIBLE_DECLARATIONS",
                    "providers": providers,
                    "usable": False,
                }
            )
            continue

        version, direction, consequence_class = next(iter(signatures))
        usable.append(
            {
                "capability_id": capability_id,
                "version": version,
                "direction": direction,
                "consequence_class": consequence_class,
                "providers": providers,
                "requires_admission": consequence_class == "external",
            }
        )

    return {
        "schema": GRAPH_SCHEMA,
        "modules": modules,
        "capabilities": usable,
        "conflicts": conflicts,
        "authority_boundary": {
            "discovery_grants_authority": False,
            "attachment_grants_authority": False,
            "composition_grants_authority": False,
            "authority_inherited_from_modules": False,
            "external_consequence_requires_admission": True,
        },
    }
