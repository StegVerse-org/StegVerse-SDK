#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md"
TASK = ROOT / "tasks" / "SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003.json"
DEPENDENCIES = ROOT / "data" / "sdk-generic-manifest-downstream-dependencies.json"

TASK_ID = "SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003"
COSV = "71000000100110"
STATE = "DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING"
PUBLIC_BASE = "https://stegverse.org/"
SITE_CONTAMINATION_BLOCKER = "SITE-CONECTRR-GOVERNANCE-CONTAMINATION-001"

REQUIRED_HANDOFF = [
    PUBLIC_BASE,
    "https://stegverse.org/ecosystem-chat.html",
    "payload class != processing capability",
    "processing capability != runtime route",
    "processing selection != authority",
    "route selection != authority",
    "caller projection != canonical custody",
    "unsupported or uninstalled processor/route execution fails closed",
    STATE,
]

FORBIDDEN_PUBLIC_HOSTS = (
    "https://stegverse-labs.github.io/Site/",
    "https://stegverse-labs.github.io/admissibility-wiki/",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def active_subblockers_resolved(item: dict) -> bool:
    blockers = item.get("active_subblockers") or []
    if not isinstance(blockers, list):
        fail(f"{item.get('repository')} active_subblockers must be a list")
    return all(isinstance(blocker, dict) and blocker.get("resolved") is True for blocker in blockers)


def evidence_complete(item: dict, require_worker_record: bool = False) -> bool:
    ev = item.get("completion_evidence")
    if not isinstance(ev, dict):
        fail(f"{item.get('repository')} completion_evidence missing")
    required = ["implementation_merge_ref", "exact_head_validation_ref", "handoff_reconciliation_ref"]
    if require_worker_record:
        required.insert(0, "worker_or_coordinator_record_ref")
    scalar_ok = all(isinstance(ev.get(k), str) and ev.get(k).strip() for k in required)
    route = ev.get("public_route")
    route_ok = isinstance(route, str) and route.startswith(PUBLIC_BASE) and ev.get("public_route_observed") is True
    return scalar_ok and route_ok and active_subblockers_resolved(item)


def main() -> None:
    handoff = HANDOFF.read_text(encoding="utf-8")
    task = json.loads(TASK.read_text(encoding="utf-8"))
    deps = json.loads(DEPENDENCIES.read_text(encoding="utf-8"))

    for token in REQUIRED_HANDOFF:
        if token not in handoff:
            fail(f"handoff missing required invariant: {token}")
    for host in FORBIDDEN_PUBLIC_HOSTS:
        if host in handoff:
            fail(f"handoff exposes provider URL as canonical public surface: {host}")

    if task.get("task_id") != TASK_ID or task.get("state") != STATE:
        fail("task identity/state mismatch")
    if task.get("manual_work_required") is not False:
        fail("manual_work_required must remain false")

    surface = task.get("public_surface")
    if not isinstance(surface, dict):
        fail("public_surface must be an object")
    if surface.get("canonical_base") != PUBLIC_BASE:
        fail("canonical public base mismatch")
    if surface.get("ecosystem_chat") != "https://stegverse.org/ecosystem-chat.html":
        fail("Ecosystem Chat public route must use stegverse.org")
    if surface.get("dedicated_processor_generic_route") is not None:
        fail("dedicated processor-generic route must remain null until deployed evidence exists")
    if surface.get("raw_github_pages_is_canonical_public_surface") is not False:
        fail("raw GitHub Pages must not be canonical public surface")

    if deps.get("schema_version") != "1.2.0":
        fail("unexpected dependency manifest schema_version")
    if deps.get("task_id") != TASK_ID or deps.get("cosv") != COSV or deps.get("state") != STATE:
        fail("dependency manifest identity/state mismatch")
    if deps.get("canonical_public_base") != PUBLIC_BASE or deps.get("authority_effect") != "NONE":
        fail("dependency manifest public-base/authority mismatch")

    dependencies = deps.get("dependencies")
    if not isinstance(dependencies, list) or len(dependencies) != 2:
        fail("dependency manifest must contain exactly two dependencies")
    by_repo = {item.get("repository"): item for item in dependencies if isinstance(item, dict)}

    site = by_repo.get("StegVerse-Labs/Site")
    wiki = by_repo.get("StegVerse-Labs/admissibility-wiki")
    if not site or not wiki:
        fail("required dependency missing")
    if site.get("owner") != "Site machine orchestration" or site.get("admission") != "EXTERNAL_SESSION_MUTATION_DISALLOWED":
        fail("Site ownership/admission mismatch")
    if "Worker D / issue #65" not in str(wiki.get("owner")) or wiki.get("admission") != "MACHINE_OWNED_DO_NOT_COMPETE":
        fail("admissibility ownership/admission mismatch")

    site_blockers = site.get("active_subblockers")
    if not isinstance(site_blockers, list):
        fail("Site active_subblockers missing")
    contamination = next((b for b in site_blockers if isinstance(b, dict) and b.get("id") == SITE_CONTAMINATION_BLOCKER), None)
    if not contamination:
        fail("Site Conectrr governance contamination blocker missing")
    if contamination.get("tracking_ref") != "StegVerse-org/StegVerse-SDK:issue/129#issuecomment-5595193431":
        fail("Site contamination blocker tracking_ref mismatch")
    required_resolution_evidence = [
        "implementation_merge_ref",
        "exact_head_validation_ref",
        "default_no_fixture_regression_ref",
        "opt_in_validation_ref",
        "public_observation_ref",
    ]
    contamination_evidence_ready = all(
        isinstance(contamination.get(key), str) and contamination.get(key).strip()
        for key in required_resolution_evidence
    )
    if contamination.get("resolved") is True and not contamination_evidence_ready:
        fail("Site contamination blocker resolved without complete evidence")
    if contamination.get("resolved") is False and contamination_evidence_ready:
        fail("Site contamination blocker has complete evidence but resolved=false; reconcile state")
    if contamination.get("resolved") is False and contamination.get("state") != "OPEN_MACHINE_OWNED":
        fail("unresolved Site contamination blocker must remain OPEN_MACHINE_OWNED")

    site_ready = evidence_complete(site)
    wiki_ready = evidence_complete(wiki, require_worker_record=True)
    for item, ready in ((site, site_ready), (wiki, wiki_ready)):
        if item.get("complete") is True and not ready:
            fail(f"{item.get('repository')} marked complete without satisfying completion evidence")
        if item.get("complete") is False and ready:
            fail(f"{item.get('repository')} has complete evidence but complete=false; reconcile state")

    expected_propagation = site_ready and wiki_ready
    if deps.get("propagation_complete") is not expected_propagation:
        fail("propagation_complete does not equal all required dependency completion predicates")
    if expected_propagation:
        fail("current parent task must not be complete until task/handoff/COSV are reconciled in same transition")

    remaining = "\n".join(str(item) for item in (task.get("remaining") or []))
    if "Site machine-owned admission" not in remaining or "Worker D" not in remaining:
        fail("task remaining dependencies not preserved")

    print("PASS: processor-generic downstream propagation contract is internally consistent")
    print("canonical_public_domain=https://stegverse.org/")
    print("downstream_dependency_count=2")
    print(f"site_conectrr_contamination_resolved={str(contamination.get('resolved') is True).lower()}")
    print(f"site_completion_predicate_satisfied={str(site_ready).lower()}")
    print(f"admissibility_completion_predicate_satisfied={str(wiki_ready).lower()}")
    print("propagation_complete=false")
    print("authority_effect=NONE")


if __name__ == "__main__":
    main()
