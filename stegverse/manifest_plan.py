"""Immutable manifest-to-derived-plan construction for SDK 1.5 source qualification.

The plan is a source artifact only. It binds the original manifest digest, requested
requirements, resolved capability qualification, and bounded adaptation directives.
It does not grant authority, execute work, substitute routes, or claim runtime evidence.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from .capability_inventory import qualify_requirements


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def derive_execution_plan(
    manifest: Mapping[str, Any],
    requirements: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    qualification = qualify_requirements(manifest, requirements)

    steps = []
    for result in qualification["results"]:
        disposition = result["disposition"]
        step = {
            "requirement_id": result["requirement_id"],
            "capability_id": result["capability_id"],
            "requested_route_id": result["requested_route_id"],
            "qualification_disposition": disposition,
            "failed_predicate": result["failed_predicate"],
            "matched": result["matched"],
            "permitted_correction": result["permitted_correction"],
            "adaptation": None,
            "runtime_probe_required": disposition == "PROBE_REQUIRED",
        }
        if disposition == "SUPPORTED":
            step["adaptation"] = {
                "kind": "EXACT_DECLARED_CAPABILITY",
                "route_id": result["matched"]["route_id"] if result["matched"] else None,
                "bounded": True,
            }
        steps.append(step)

    plan_core = {
        "schema": "stegverse.sdk-derived-plan/v1",
        "source_manifest_sha256": qualification["manifest_sha256"],
        "requirements_sha256": _sha256(list(requirements)),
        "steps": tuple(steps),
        "execution_authorized": False,
        "runtime_execution_observed": False,
        "route_substitution_permitted": False,
        "source_evidence_ceiling": "SOURCE_DERIVED_PLAN_ONLY",
    }

    return {
        **plan_core,
        "derived_plan_sha256": _sha256(plan_core),
    }


def verify_plan_lineage(
    manifest: Mapping[str, Any],
    requirements: Sequence[Mapping[str, Any]],
    plan: Mapping[str, Any],
) -> bool:
    expected = derive_execution_plan(manifest, requirements)
    # Every field is covered; digest equality alone cannot authenticate siblings.
    return dict(plan) == expected
