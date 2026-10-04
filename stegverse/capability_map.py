"""Reconcile the installed route table against what an evaluator can actually invoke.

Three maps describe SDK capability, and nothing kept them in agreement:

* ``route_resolution.PUBLISHED_ROUTES`` - which runtime is installed;
* ``manifest_builder.PROCESSOR_ROUTES`` - which capability ``manifest build
  --process`` can reach;
* ``inspection/examples`` - which capability an evaluator can invoke from an
  ordinary console, the only interface the Tests 1-3 run evidence admits.

An installed route that no builder binding reaches is not evaluator-invocable,
however complete its runtime is. ``capability_inventory`` reports such a route as
installed and stops there, so the drift is invisible from outside. This module
states it per route instead, and a route may sit outside the standard only
through a declared exemption that names its reason, repair and owner.

Non-authorizing. Source reconciliation only: it installs nothing, binds nothing,
substitutes no route and observes no runtime.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import re
from typing import Any

from .manifest_builder import (
    ECOSYSTEM_CONNECTED, LOCAL_CONFORMANCE, GOVERNANCE_PROFILE_ROUTES, PROCESSOR_ROUTES,
)
from .route_resolution import CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID, PUBLISHED_ROUTES

SCHEMA = "stegverse.sdk.capability-map-reconciliation/v1"

#: A canonical task id, as the registry writes them.
CANONICAL_TASK_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}$")

#: Every field an exemption must carry. An exemption is granted against an
#: existing canonical goal and expires; it is not a permanent self-declaration.
EXEMPTION_REQUIRED_FIELDS = (
    "failed_predicate",
    "required_evidence_or_repair",
    "retry_entrypoint",
    "owning_existing_goal",
    "registry_repository",
    "observed_registry_generation",
    "granted_by",
    "review_by",
)

#: The exemptions that exist. Adding a key here is the deliberate, reviewable
#: act of granting one - the gate fails when the declared set and the granted
#: set disagree, so an exemption cannot appear as a side effect of a new route.
EXEMPTION_BASELINE = frozenset({
    "native_source_math",
    "sovereign_inference",
})

OWNING_GOAL = "SDK-GENERIC-MANIFEST-ECOSYSTEM-INVARIANT-005"
REGISTRY_REPOSITORY = "StegVerse-Labs/.github"
OBSERVED_REGISTRY_GENERATION = 278
GRANTED_BY = "StegVerse-Labs/.github:SDK-GENERIC-MANIFEST-ECOSYSTEM-INVARIANT-005"
REVIEW_BY = "2026-12-31"
EXAMPLE_ROOT = Path(__file__).resolve().parent.parent / "inspection" / "examples"
SHARED_SOURCE = "sdk-tt-shared-source.json"

#: Evaluator-invocable fixture per builder-bound capability. Each entry is the
#: exact pair a console run takes: ``manifest build --input <source>
#: --processor-request <request> --process <capability>``.
EVALUATOR_EXAMPLES: dict[str, dict[str, str]] = {
    "governance": {
        "source": SHARED_SOURCE,
        "processor_request": "elan-governance-request.example.json",
    },
    "ecosystem_diagnostic": {
        "source": SHARED_SOURCE,
        "processor_request": "source-observation-synthetic-diagnostic-request.json",
    },
    "purpose_bound_worker": {
        "source": SHARED_SOURCE,
        "processor_request": "sdk-test1-purpose-worker.processor-request.json",
    },
    "atomic_task_worker": {
        "source": SHARED_SOURCE,
        "processor_request": "sdk-test2-atomic-task-worker.processor-request.json",
    },
    "svg_governance_cycle": {
        "source": SHARED_SOURCE,
        "processor_request": "sdk-svg-governance-cycle.processor-request.json",
    },
    "stegbrowser": {
        "source": SHARED_SOURCE,
        "processor_request": "sdk-test5-stegbrowser-llm-profile.processor-request.json",
    },
}

#: Published routes the Manifest Builder cannot select even though their
#: capability is bound, because ``--process <capability>`` resolves to exactly
#: one route id. Keyed by route id rather than capability.
ROUTE_SELECTION_EXEMPTIONS: dict[str, dict[str, str]] = {}


#: Routes published as installed that the Manifest Builder cannot reach. Each
#: exemption is explicit and carries the predicate that is unsatisfied, the
#: repair that would satisfy it and the owner who holds it. An exemption records
#: a known boundary; it never reports the capability as invocable.
BUILDER_BINDING_EXEMPTIONS: dict[str, dict[str, str]] = {
    "native_source_math": {
        "failed_predicate": "PROCESSING_CAPABILITY_PRESENT_IN_PROCESSOR_ROUTES",
        "required_evidence_or_repair": (
            "add a native_source_math processor-request validator and builder "
            "binding, then declare its evaluator example"
        ),
        "retry_entrypoint": "stegverse.manifest_builder.build_manifest",
        "owning_existing_goal": OWNING_GOAL,
        "registry_repository": REGISTRY_REPOSITORY,
        "observed_registry_generation": OBSERVED_REGISTRY_GENERATION,
        "granted_by": GRANTED_BY,
        "review_by": REVIEW_BY,
        "current_reachability": "RUNTIME_INSTALLED_TESTS_CONSTRUCT_THE_MANIFEST_DIRECTLY",
    },
    "sovereign_inference": {
        "failed_predicate": "PROCESSING_CAPABILITY_PRESENT_IN_PROCESSOR_ROUTES",
        "required_evidence_or_repair": (
            "add a sovereign_inference processor-request validator and builder "
            "binding, then declare its evaluator example"
        ),
        "retry_entrypoint": "stegverse.manifest_builder.build_manifest",
        "owning_existing_goal": OWNING_GOAL,
        "registry_repository": REGISTRY_REPOSITORY,
        "observed_registry_generation": OBSERVED_REGISTRY_GENERATION,
        "granted_by": GRANTED_BY,
        "review_by": REVIEW_BY,
        "current_reachability": "RUNTIME_INSTALLED_REACHED_THROUGH_EXISTING_UNIVERSAL_INTR_ONLY",
    },
}

EVALUATOR_INVOCABLE = "EVALUATOR_INVOCABLE"
DECLARED_EXEMPTION = "DECLARED_EXEMPTION"
STOP_DRIFT = "STOP_CAPABILITY_MAP_DRIFT"


def _expired(review_by: Any, *, today: date | None = None) -> bool:
    """True when an exemption's review date has passed.

    An exemption that never lapses is a permanent carve-out. This one goes red
    on its review date so the carve-out has to be re-granted or repaired.
    """
    try:
        deadline = date.fromisoformat(str(review_by))
    except (TypeError, ValueError):
        return True
    return (today or date.today()) > deadline


def _example_paths(capability: str) -> dict[str, str] | None:
    entry = EVALUATOR_EXAMPLES.get(capability)
    if entry is None:
        return None
    return {
        "source": str(EXAMPLE_ROOT / entry["source"]),
        "processor_request": str(EXAMPLE_ROOT / entry["processor_request"]),
    }


def reconcile_capability_map() -> dict[str, Any]:
    """Return one row per published route, saying whether it is invocable.

    A row is ``EVALUATOR_INVOCABLE`` only when the route is installed, the
    builder can reach its capability and a declared example pair exists on disk.
    A capability with a declared exemption is ``DECLARED_EXEMPTION``. Anything
    else is ``STOP_CAPABILITY_MAP_DRIFT`` and carries the predicate it failed.
    """
    rows: list[dict[str, Any]] = []
    for route_id, route in sorted(PUBLISHED_ROUTES.items()):
        capability = route["processor_capability"]
        installed = route.get("runtime_installed") is True
        selected_route = PROCESSOR_ROUTES.get(capability)
        bound = selected_route == route_id
        execution_profile = None
        if capability == "governance" and route_id in GOVERNANCE_PROFILE_ROUTES.values():
            execution_profile = next(
                profile for profile, selected in GOVERNANCE_PROFILE_ROUTES.items()
                if selected == route_id
            )
            bound = True
        exemption = BUILDER_BINDING_EXEMPTIONS.get(capability)
        if selected_route is not None and not bound:
            exemption = ROUTE_SELECTION_EXEMPTIONS.get(route_id)
        paths = _example_paths(capability)
        # The declared example belongs to the route the capability selects, not
        # to every route that happens to share the capability.
        example_present = (
            bound and bool(paths) and all(Path(p).is_file() for p in paths.values())
        )

        row: dict[str, Any] = {
            "capability_id": capability,
            "route_id": route_id,
            "runtime_installed": installed,
            "builder_binding": "BOUND" if bound else ("EXEMPT" if exemption else "ABSENT"),
            "evaluator_example": "PRESENT" if example_present else (
                "EXEMPT" if exemption else "ABSENT"
            ),
            "routing_surface": route.get("routing_surface"),
            "execution_profile": execution_profile,
            "execution_authorized": False,
            "evidence_ceiling": "SOURCE_RECONCILIATION_ONLY",
        }
        if paths and example_present:
            row["example"] = EVALUATOR_EXAMPLES[capability]
            if execution_profile:
                row["example"]["execution_profile"] = execution_profile

        if bound and example_present:
            row["disposition"] = EVALUATOR_INVOCABLE
        elif exemption and not bound:
            row["disposition"] = DECLARED_EXEMPTION
            row.update(exemption)
            row["exemption_expired"] = _expired(exemption.get("review_by"))
        else:
            row["disposition"] = STOP_DRIFT
            if not bound:
                row["failed_predicate"] = "PROCESSING_CAPABILITY_PRESENT_IN_PROCESSOR_ROUTES"
                row["required_evidence_or_repair"] = (
                    f"add {capability!r} to manifest_builder.PROCESSOR_ROUTES with a "
                    "processor-request validator, or declare an exemption naming its owner"
                )
            else:
                row["failed_predicate"] = "DECLARED_EVALUATOR_EXAMPLE_PRESENT"
                row["required_evidence_or_repair"] = (
                    f"add an inspection/examples fixture pair for {capability!r} and "
                    "declare it in capability_map.EVALUATOR_EXAMPLES"
                )
            row["retry_entrypoint"] = "python -m unittest tests.test_capability_map_conformance"
            row["owning_existing_goal"] = OWNING_GOAL
        rows.append(row)

    drift = [r for r in rows if r["disposition"] == STOP_DRIFT]
    granted = set(BUILDER_BINDING_EXEMPTIONS) | set(ROUTE_SELECTION_EXEMPTIONS)
    return {
        "exemption_baseline_matches": granted == set(EXEMPTION_BASELINE),
        "undeclared_exemptions": sorted(granted - set(EXEMPTION_BASELINE)),
        "stale_baseline_entries": sorted(set(EXEMPTION_BASELINE) - granted),
        "expired_exemption_count": sum(
            1 for r in rows if r.get("exemption_expired") is True
        ),
        "schema": SCHEMA,
        "published_route_count": len(rows),
        "evaluator_invocable_count": sum(
            1 for r in rows if r["disposition"] == EVALUATOR_INVOCABLE
        ),
        "declared_exemption_count": sum(
            1 for r in rows if r["disposition"] == DECLARED_EXEMPTION
        ),
        "drift_count": len(drift),
        "rows": tuple(rows),
        "grants_execution_authority": False,
        "authority_effect": "NONE_RECONCILIATION_ONLY",
    }


__all__ = [
    "BUILDER_BINDING_EXEMPTIONS", "CANONICAL_TASK_ID", "DECLARED_EXEMPTION",
    "EXEMPTION_BASELINE", "EXEMPTION_REQUIRED_FIELDS", "EVALUATOR_EXAMPLES",
    "EVALUATOR_INVOCABLE", "ROUTE_SELECTION_EXEMPTIONS", "SCHEMA", "STOP_DRIFT",
    "reconcile_capability_map",
]
