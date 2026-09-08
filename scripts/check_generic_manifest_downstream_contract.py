#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md"
TASK = ROOT / "tasks" / "SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003.json"

REQUIRED_HANDOFF = [
    "https://stegverse.org/",
    "https://stegverse.org/ecosystem-chat.html",
    "payload class != processing capability",
    "processing capability != runtime route",
    "processing selection != authority",
    "route selection != authority",
    "caller projection != canonical custody",
    "unsupported or uninstalled processor/route execution fails closed",
    "DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING",
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

    for token in REQUIRED_HANDOFF:
        if token not in handoff:
            fail(f"handoff missing required invariant: {token}")

    for host in FORBIDDEN_PUBLIC_HOSTS:
        if host in handoff:
            fail(f"handoff exposes provider URL as canonical public surface: {host}")

    if task.get("task_id") != "SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003":
        fail("unexpected task_id")
    if task.get("state") != "DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING":
        fail("task state must remain dependency-execution-pending until downstream evidence lands")
    if task.get("manual_work_required") is not False:
        fail("manual_work_required must remain false")

    surface = task.get("public_surface")
    if not isinstance(surface, dict):
        fail("public_surface must be an object")
    if surface.get("canonical_base") != "https://stegverse.org/":
        fail("canonical public base must be https://stegverse.org/")
    if surface.get("ecosystem_chat") != "https://stegverse.org/ecosystem-chat.html":
        fail("Ecosystem Chat public route must use stegverse.org")
    if surface.get("dedicated_processor_generic_route") is not None:
        fail("dedicated processor-generic route must remain null until deployed evidence exists")
    if surface.get("raw_github_pages_is_canonical_public_surface") is not False:
        fail("raw GitHub Pages must not be canonical public surface")

    remaining = task.get("remaining") or []
    joined = "\n".join(str(item) for item in remaining)
    if "Site machine-owned admission" not in joined:
        fail("Site machine-owned dependency is not preserved")
    if "Worker D" not in joined:
        fail("admissibility Worker D dependency is not preserved")

    print("PASS: processor-generic downstream propagation contract is internally consistent")
    print("canonical_public_domain=https://stegverse.org/")
    print("dedicated_processor_generic_route=UNDEPLOYED")
    print("propagation_complete=false")
    print("authority_effect=NONE")


if __name__ == "__main__":
    main()
