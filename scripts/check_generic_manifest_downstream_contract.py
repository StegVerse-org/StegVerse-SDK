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

    surfaces = task.get("public_surface_candidates")
    expected = ["https://stegverse.org/", "https://stegverse.org/ecosystem-chat.html"]
    if surfaces != expected:
        fail(f"public_surface_candidates must equal {expected!r}; observed {surfaces!r}")

    remaining = task.get("remaining") or []
    joined = "\n".join(str(item) for item in remaining)
    if "Site machine-owned admission" not in joined:
        fail("Site machine-owned dependency is not preserved")
    if "Worker D" not in joined:
        fail("admissibility Worker D dependency is not preserved")

    print("PASS: processor-generic downstream propagation contract is internally consistent")
    print("canonical_public_domain=https://stegverse.org/")
    print("propagation_complete=false")
    print("authority_effect=NONE")


if __name__ == "__main__":
    main()
