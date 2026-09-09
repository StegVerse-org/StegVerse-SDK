#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md"
TASK = ROOT / "tasks" / "SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003.json"
DEPENDENCIES = ROOT / "data" / "sdk-generic-manifest-downstream-dependencies.json"
OBSERVATION = ROOT / "data" / "sdk-generic-manifest-downstream-observation.json"

TASK_ID = "SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003"
COSV = "71000000100110"
STATE = "DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING"
PUBLIC_BASE = "https://stegverse.org/"
SITE_CONTAMINATION_BLOCKER = "SITE-CONECTRR-GOVERNANCE-CONTAMINATION-001"
SITE_CONTAMINATION_ISSUE = "StegVerse-Labs/Site:issue/1143"
SITE_CONTAMINATION_MERGE = "StegVerse-Labs/Site:commit/1260262ba6ab7198b20bf5a04a93264089e203da"
SITE_CONTAMINATION_CONTROLLER = "StegVerse-Labs/Site:commit/e6991ed197cdde8fc78b62b879ba35165241253b"
SITE_CLEAN_OBSERVATION = "StegVerse-Labs/Site:issue/1143#issuecomment-5598275109"

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
    observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))

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

    if deps.get("schema_version") != "1.4.0":
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
    if contamination.get("site_issue_ref") != SITE_CONTAMINATION_ISSUE:
        fail("Site contamination blocker must bind canonical Site issue #1143")
    if contamination.get("resolved") is not True or contamination.get("state") != "RESOLVED_VALIDATED_DEPLOYED":
        fail("Site contamination blocker must be resolved only after deployed clean-path evidence")

    live = contamination.get("deployed_contamination_observation")
    if not isinstance(live, dict) or live.get("state") != "REMEDIATED_AND_CLEAN_PATH_OBSERVED":
        fail("remediated deployed contamination observation missing")
    if live.get("site_issue_comment_ref") != "StegVerse-Labs/Site:issue/1143#issuecomment-5596432980":
        fail("Site original live-observation evidence ref mismatch")
    if live.get("sdk_issue_comment_ref") != "StegVerse-org/StegVerse-SDK:issue/129#issuecomment-5596433895":
        fail("SDK original live-observation evidence ref mismatch")
    if live.get("co_mingled_with_ordinary_session_events") is not True:
        fail("deployed observation must preserve original co-mingling evidence")
    if live.get("clean_default_path_observed") is not True:
        fail("clean default path must be observed after remediation")
    if live.get("clean_observation_ref") != SITE_CLEAN_OBSERVATION:
        fail("clean default-path public observation ref mismatch")
    if live.get("clean_observation_fixture_event_ids_present") is not False:
        fail("clean default-path observation cannot contain fixture event IDs")
    if live.get("clean_observation_conectrr_text_present") is not False:
        fail("clean default-path observation cannot contain Conectrr text")
    if live.get("fixture_event_ids") != ["event:conectrr:handoff:001", "event:stegverse:evaluation:001"]:
        fail("deployed observation fixture event IDs mismatch")

    queue = contamination.get("current_site_queue_blocker")
    if not isinstance(queue, dict):
        fail("Site contamination blocker missing current_site_queue_blocker")
    if queue.get("task_id") != "SITE-0001-COHERENT-TRANSITION-THRESHOLD-ACTIVATION":
        fail("unexpected current Site queue blocker")
    if queue.get("external_tasks_allowed") is not False or queue.get("external_session_ownership_allowed") is not False:
        fail("Site queue blocker must preserve closed external admission")

    patch = contamination.get("executable_patch_contract")
    if not isinstance(patch, dict):
        fail("Site contamination blocker missing executable_patch_contract")
    if patch.get("default_mode") != "NO_CONECTRR_FIXTURE":
        fail("Conectrr patch default mode must be NO_CONECTRR_FIXTURE")
    if "conectrr-fixture=1" not in str(patch.get("explicit_opt_in")):
        fail("Conectrr patch contract must include explicit opt-in semantics")
    patch_files = patch.get("files")
    required_patch_files = {
        "assets/ecosystem-node-views.js",
        "scripts/check_conectrr_browser_projection.py",
        "scripts/check_conectrr_runtime_projection.py",
        "scripts/check_conectrr_live_routes.py",
        "scripts/check_conectrr_remote_browser.py",
        "docs/CONECTRR_INTEROP_MIRROR_HANDOFF.md",
    }
    if not isinstance(patch_files, dict) or not required_patch_files.issubset(patch_files):
        fail("Conectrr executable patch contract missing required Site files")
    if patch.get("fixture_event_ids") != ["event:conectrr:handoff:001", "event:stegverse:evaluation:001"]:
        fail("Conectrr fixture event IDs mismatch")

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
    if not contamination_evidence_ready:
        fail("Site contamination blocker resolution evidence incomplete")
    if contamination.get("implementation_merge_ref") != SITE_CONTAMINATION_MERGE:
        fail("Site contamination merge evidence mismatch")
    if contamination.get("public_observation_ref") != SITE_CLEAN_OBSERVATION:
        fail("Site contamination public observation evidence mismatch")

    site_ready = evidence_complete(site)
    wiki_ready = evidence_complete(wiki, require_worker_record=True)
    for item, ready in ((site, site_ready), (wiki, wiki_ready)):
        if item.get("complete") is True and not ready:
            fail(f"{item.get('repository')} marked complete without satisfying completion evidence")
        if item.get("complete") is False and ready:
            fail(f"{item.get('repository')} has complete evidence but complete=false; reconcile state")

    if observation.get("schema_version") != "1.1.0" or observation.get("task_id") != TASK_ID or observation.get("cosv") != COSV:
        fail("downstream observation identity mismatch")
    if observation.get("observed_state") != "SITE_SUBBLOCKER_TRANSITION_OBSERVED":
        fail("observation must record Site sub-blocker transition")
    observed_site = observation.get("site") or {}
    if observed_site.get("repository_state") != "OBSERVED_BLOCKED":
        fail("observed Site repository state mismatch")
    if observed_site.get("external_tasks_allowed") is not False or observed_site.get("external_session_ownership_allowed") is not False:
        fail("observation must preserve current Site external-admission state")
    observed_contamination = observed_site.get("conectrr_governance_contamination") or {}
    if observed_contamination.get("task_id") != SITE_CONTAMINATION_BLOCKER:
        fail("observation contamination blocker identity mismatch")
    if observed_contamination.get("site_implementation_record_observed") is not True:
        fail("observation must record Site implementation evidence")
    if observed_contamination.get("implementation_merge_ref") != SITE_CONTAMINATION_MERGE:
        fail("observation Site implementation merge ref mismatch")
    if observed_contamination.get("repository_controller_completion_ref") != SITE_CONTAMINATION_CONTROLLER:
        fail("observation Site controller completion ref mismatch")
    if observed_contamination.get("default_fixture_injection_still_present_on_main") is not False:
        fail("observation must clear default fixture injection after merged remediation")
    if observed_contamination.get("clean_default_path_observed") is not True:
        fail("observation must record clean public default path")
    if observed_contamination.get("public_observation_ref") != SITE_CLEAN_OBSERVATION:
        fail("observation public clean-path ref mismatch")
    if observed_contamination.get("resolved") is not True:
        fail("observation must mark Site contamination resolved")

    observed_wiki = observation.get("admissibility") or {}
    if observed_wiki.get("worker_state") != "MACHINE_OWNED_DO_NOT_COMPETE":
        fail("observation admissibility worker state mismatch")
    if observed_wiki.get("new_worker_implementation_record_observed") is not False or observed_wiki.get("processor_generic_doctrine_transition_observed") is not False:
        fail("observation cannot claim admissibility transition without worker/coordinator evidence")
    observed_parent = observation.get("parent_effect") or {}
    if observed_parent.get("site_completion_predicate_satisfied") is not site_ready:
        fail("observation Site completion predicate mismatch")
    if observed_parent.get("admissibility_completion_predicate_satisfied") is not wiki_ready:
        fail("observation admissibility completion predicate mismatch")
    if observed_parent.get("site_conectrr_subblocker_resolved") is not True:
        fail("observation parent effect must record Site Conectrr sub-blocker resolution")
    if observed_parent.get("propagation_complete") is not False or observed_parent.get("authority_effect") != "NONE":
        fail("observation parent effect mismatch")

    expected_propagation = site_ready and wiki_ready
    if deps.get("propagation_complete") is not expected_propagation:
        fail("propagation_complete does not equal all required dependency completion predicates")
    if expected_propagation:
        fail("current parent task must not be complete until task/handoff/COSV are reconciled in same transition")

    remaining = "\n".join(str(item) for item in (task.get("remaining") or []))
    if "Site machine-owned admission" not in remaining or "Worker D" not in remaining:
        fail("task remaining dependencies not preserved")
    if "SITE-CONECTRR-GOVERNANCE-CONTAMINATION-001" in remaining:
        fail("resolved Site contamination blocker must not remain in task remaining list")

    print("PASS: processor-generic downstream propagation contract is internally consistent")
    print("canonical_public_domain=https://stegverse.org/")
    print("downstream_dependency_count=2")
    print("site_subblocker_transition_observed=true")
    print("site_conectrr_issue=StegVerse-Labs/Site#1143")
    print("site_conectrr_deployed_contamination_observed=true")
    print("site_conectrr_clean_default_path_observed=true")
    print("site_conectrr_contamination_resolved=true")
    print(f"site_completion_predicate_satisfied={str(site_ready).lower()}")
    print(f"admissibility_completion_predicate_satisfied={str(wiki_ready).lower()}")
    print("propagation_complete=false")
    print("authority_effect=NONE")


if __name__ == "__main__":
    main()
