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

    if task.get("task_id") != TASK_ID:
        fail("unexpected task_id")
    if task.get("state") != STATE:
        fail("task state must remain dependency-execution-pending until downstream evidence lands")
    if task.get("manual_work_required") is not False:
        fail("manual_work_required must remain false")

    surface = task.get("public_surface")
    if not isinstance(surface, dict):
        fail("public_surface must be an object")
    if surface.get("canonical_base") != PUBLIC_BASE:
        fail("canonical public base must be https://stegverse.org/")
    if surface.get("ecosystem_chat") != "https://stegverse.org/ecosystem-chat.html":
        fail("Ecosystem Chat public route must use stegverse.org")
    if surface.get("dedicated_processor_generic_route") is not None:
        fail("dedicated processor-generic route must remain null until deployed evidence exists")
    if surface.get("raw_github_pages_is_canonical_public_surface") is not False:
        fail("raw GitHub Pages must not be canonical public surface")

    if deps.get("schema_version") != "1.0.0":
        fail("unexpected dependency manifest schema_version")
    if deps.get("task_id") != TASK_ID or deps.get("cosv") != COSV:
        fail("dependency manifest identity mismatch")
    if deps.get("state") != STATE:
        fail("dependency manifest state mismatch")
    if deps.get("canonical_public_base") != PUBLIC_BASE:
        fail("dependency manifest canonical public base mismatch")
    if deps.get("propagation_complete") is not False:
        fail("propagation_complete cannot be true while dependencies remain incomplete")
    if deps.get("authority_effect") != "NONE":
        fail("dependency manifest authority_effect must remain NONE")

    dependencies = deps.get("dependencies")
    if not isinstance(dependencies, list) or len(dependencies) != 2:
        fail("dependency manifest must contain exactly the two required downstream dependencies")
    by_repo = {item.get("repository"): item for item in dependencies if isinstance(item, dict)}

    site = by_repo.get("StegVerse-Labs/Site")
    if not site:
        fail("Site dependency missing")
    if site.get("owner") != "Site machine orchestration":
        fail("Site dependency owner mismatch")
    if site.get("admission") != "EXTERNAL_SESSION_MUTATION_DISALLOWED":
        fail("Site admission must remain externally disallowed until source state changes")
    if site.get("complete") is not False:
        fail("Site dependency cannot be complete before admitted implementation evidence")

    wiki = by_repo.get("StegVerse-Labs/admissibility-wiki")
    if not wiki:
        fail("admissibility-wiki dependency missing")
    if "Worker D / issue #65" not in str(wiki.get("owner")):
        fail("admissibility dependency owner mismatch")
    if wiki.get("admission") != "MACHINE_OWNED_DO_NOT_COMPETE":
        fail("admissibility dependency admission mismatch")
    if wiki.get("complete") is not False:
        fail("admissibility dependency cannot be complete before worker evidence")

    remaining = task.get("remaining") or []
    joined = "\n".join(str(item) for item in remaining)
    if "Site machine-owned admission" not in joined:
        fail("Site machine-owned dependency is not preserved")
    if "Worker D" not in joined:
        fail("admissibility Worker D dependency is not preserved")

    print("PASS: processor-generic downstream propagation contract is internally consistent")
    print("canonical_public_domain=https://stegverse.org/")
    print("downstream_dependency_count=2")
    print("dedicated_processor_generic_route=UNDEPLOYED")
    print("propagation_complete=false")
    print("authority_effect=NONE")


if __name__ == "__main__":
    main()
