#!/usr/bin/env python3
"""Validate the durable session-consolidation task registry.

The validator is side-effect free. It prevents archive-ready state from being
asserted while tasks are unassigned, claims are indefinite, release conditions
are absent, or session-owned claims remain active.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_TASK_FIELDS = {
    "task_id",
    "originating_goal",
    "repository",
    "branch",
    "location",
    "owner",
    "claim_state",
    "completion_state",
    "validation_state",
    "integration_state",
    "evidence_location",
    "next_action",
    "release_condition",
    "archival_dependency",
}

ALLOWED_CLAIM_STATES = {
    "UNCLAIMED",
    "CLAIMED_FOR_IMPLEMENTATION",
    "CLAIMED_FOR_VALIDATION",
    "CLAIMED_FOR_INTEGRATION",
    "MACHINE_OWNED",
    "BLOCKED",
    "COMPLETE",
    "SUPERSEDED",
    "MERGED_INTO_CANONICAL_WORKSTREAM",
}

ACTIVE_SESSION_CLAIMS = {
    "CLAIMED_FOR_IMPLEMENTATION",
    "CLAIMED_FOR_VALIDATION",
    "CLAIMED_FOR_INTEGRATION",
}


def _nonempty_text(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if registry.get("schema_version") != "stegverse.session_consolidation_registry.v1":
        errors.append("unsupported schema_version")

    for field in (
        "registry_id",
        "originating_goal",
        "canonical_repository",
        "canonical_branch",
        "canonical_handoff",
        "consolidation_record",
        "created_at",
        "terminal_session_state",
    ):
        _nonempty_text(registry.get(field), field, errors)

    declared_states = registry.get("allowed_states")
    if not isinstance(declared_states, list) or set(declared_states) != ALLOWED_CLAIM_STATES:
        errors.append("allowed_states must exactly match the canonical claim-state registry")

    claims = registry.get("session_claims")
    if not isinstance(claims, dict):
        errors.append("session_claims must be an object")
    else:
        for role in ("implementation", "validation", "integration", "observation"):
            if claims.get(role) != "RELEASED":
                errors.append(f"session claim {role} must be RELEASED for archive-ready state")

    tasks = registry.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty array")
        tasks = []

    seen_ids: set[str] = set()
    for index, task in enumerate(tasks):
        prefix = f"tasks[{index}]"
        if not isinstance(task, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(REQUIRED_TASK_FIELDS - set(task))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue

        task_id = task.get("task_id")
        _nonempty_text(task_id, f"{prefix}.task_id", errors)
        if isinstance(task_id, str):
            if task_id in seen_ids:
                errors.append(f"duplicate task_id: {task_id}")
            seen_ids.add(task_id)

        for field in (
            "originating_goal",
            "repository",
            "branch",
            "location",
            "owner",
            "completion_state",
            "validation_state",
            "integration_state",
            "evidence_location",
            "next_action",
            "release_condition",
        ):
            _nonempty_text(task.get(field), f"{prefix}.{field}", errors)

        state = task.get("claim_state")
        if state not in ALLOWED_CLAIM_STATES:
            errors.append(f"{prefix}.claim_state is invalid")
        if state == "UNCLAIMED":
            errors.append(f"{prefix} cannot remain UNCLAIMED in an archive-ready registry")
        if state in ACTIVE_SESSION_CLAIMS:
            errors.append(f"{prefix} retains an active human/session claim")
        if task.get("archival_dependency") is not False:
            errors.append(f"{prefix}.archival_dependency must be false after durable transfer")

    archive_test = registry.get("archive_test")
    if not isinstance(archive_test, dict):
        errors.append("archive_test must be an object")
    else:
        expected = {
            "unique_session_information_remaining_only_in_chat": False,
            "session_owned_active_claims": False,
            "unassigned_tasks": False,
            "tasks_without_release_conditions": False,
            "canonical_continuation_recorded": True,
            "archive_ready": True,
        }
        for key, value in expected.items():
            if archive_test.get(key) is not value:
                errors.append(f"archive_test.{key} must be {value!r}")

    if registry.get("terminal_session_state") != "MERGED_INTO_CANONICAL_WORKSTREAM":
        errors.append("terminal_session_state must be MERGED_INTO_CANONICAL_WORKSTREAM")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "registry",
        nargs="?",
        default="task-registry/orli-judgment-system-boundary-2026-08-02.json",
    )
    args = parser.parse_args()

    path = Path(args.registry)
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"SESSION CONSOLIDATION REGISTRY: FAIL - {type(exc).__name__}: {exc}")
        return 1

    if not isinstance(registry, dict):
        print("SESSION CONSOLIDATION REGISTRY: FAIL - root must be an object")
        return 1

    errors = validate_registry(registry)
    if errors:
        print("SESSION CONSOLIDATION REGISTRY: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("SESSION CONSOLIDATION REGISTRY: PASS")
    print(f"registry_id={registry['registry_id']}")
    print(f"tasks={len(registry['tasks'])}")
    print("session_claims=released")
    print("archive_ready=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
