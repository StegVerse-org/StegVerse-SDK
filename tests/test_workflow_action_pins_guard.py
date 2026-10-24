"""Every action a workflow runs is pinned to a commit (SDK#484 V-P6).

A tag or branch (`@v4`, `@main`, `@release/v1`) lets an external repository change what runs
here without a change in this repository. Every `uses:` must name a 40-hex commit or a local
`./` path. There are no exceptions: governance-gate.yml was the one exception until SDK#534
merged and pinned it. A floating reference fails closed with the six fields.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
USES = re.compile(r"^\s*(?:-\s*)?uses:\s*(\S+)")
PINNED = re.compile(r"^[\w.-]+/[\w.-]+(?:/[\w./-]+)?@[0-9a-f]{40}$")
# file -> (floating references allowed, why)
EXCEPTIONS = {}
SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair",
              "retry_entrypoint", "owning_existing_goal", "next_attempt")


def floating(text: str) -> list[str]:
    refs = []
    for line in text.splitlines():
        match = USES.match(line)
        if match and not match.group(1).startswith("./") and not PINNED.match(match.group(1)):
            refs.append(match.group(1))
    return refs


def refusals() -> list[dict]:
    found = []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        refs = floating(path.read_text(encoding="utf-8"))
        allowed = EXCEPTIONS.get(path.name, (0, ""))[0]
        if len(refs) != allowed:
            found.append({
                "disposition": "FAIL_CLOSED",
                "failure_code": "WORKFLOW_ACTION_NOT_PINNED",
                "failed_predicate": "EVERY_USES_IS_A_COMMIT_OR_LOCAL_PATH",
                "required_evidence_or_repair": f"{path.name}: pin {refs} to the commit the tag resolves to "
                                               f"(git ls-remote), keeping the tag as a trailing comment",
                "retry_entrypoint": "tests/test_workflow_action_pins_guard.py",
                "owning_existing_goal": "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001",
                "next_attempt": "rerun the guard after the references are pinned",
            })
    return found


def test_every_workflow_action_is_pinned_to_a_commit():
    assert refusals() == [], refusals()


def test_exceptions_are_justified_and_not_stale():
    for name, (count, why) in EXCEPTIONS.items():
        assert (WORKFLOWS / name).is_file() and len(why) > 20
        assert len(floating((WORKFLOWS / name).read_text(encoding="utf-8"))) == count, name


def test_the_guard_flags_tags_and_branches():
    text = ("steps:\n  - uses: actions/checkout@v4\n  - uses: org/repo/.github/workflows/x.yml@main\n"
            "  - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5\n"
            "  - uses: ./.github/workflows/local.yml\n# uses: commented/out@v1\n")
    assert floating(text) == ["actions/checkout@v4", "org/repo/.github/workflows/x.yml@main"]
