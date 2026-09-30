"""Workflow files must load, and the whole-suite gate must stay universal.

An invalid workflow does not fail loudly: GitHub refuses to load it and the job
simply never appears among the pull request's check runs. That is worse than a
gate reporting a vacuous pass, because there is no output at all to read.

It happened here. A step condition referencing the `secrets` context -- not an
available context for `steps[*].if` -- made the test-suite ratchet invalid, and
the gate stopped running on two commits without anything going red on the PR
itself. These tests are the cheap check that would have caught it.

Non-authorizing: source validation only. Nothing is executed or dispatched.
"""

from __future__ import annotations

from pathlib import Path
import re

import pytest

yaml = pytest.importorskip("yaml")

WORKFLOWS = sorted((Path(__file__).resolve().parents[1] / ".github/workflows").glob("*.y*ml"))
RATCHET = "test-suite-ratchet.yml"

#: Contexts GitHub does not make available to a step-level `if`. Referencing one
#: there is not a runtime error, it makes the whole workflow fail to load.
FORBIDDEN_IN_STEP_IF = ("secrets.", "secrets[")


def _on(workflow: dict) -> dict:
    """PyYAML parses the `on:` key as the boolean True."""
    trigger = workflow.get("on", workflow.get(True))
    return trigger if isinstance(trigger, dict) else {}


def _steps(workflow: dict):
    for job_name, job in (workflow.get("jobs") or {}).items():
        for step in (job.get("steps") or []):
            if isinstance(step, dict):
                yield job_name, step


def test_there_are_workflows_to_check() -> None:
    """A passing sweep over an empty list would prove nothing."""
    assert WORKFLOWS, "no workflow files found to validate"


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_every_workflow_file_parses(path: Path) -> None:
    assert isinstance(yaml.safe_load(path.read_text(encoding="utf-8")), dict), path.name


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_no_step_condition_references_the_secrets_context(path: Path) -> None:
    """The exact mistake that silently disabled the ratchet.

    A secret needed by a condition goes into a job-level env, which a step `if`
    may read.
    """
    workflow = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    offenders = [
        f"{path.name}:{job}:{step.get('name') or step.get('uses')}"
        for job, step in _steps(workflow)
        if isinstance(step.get("if"), str)
        and any(token in step["if"] for token in FORBIDDEN_IN_STEP_IF)
    ]
    assert offenders == [], (
        "secrets is not an available context for steps[*].if; put it in a "
        f"job-level env and test env.NAME instead: {offenders}"
    )


def test_the_whole_suite_gate_has_no_path_filter() -> None:
    """The ratchet exists because path filters hid untested files.

    Narrowing it would recreate the hole it was built to close, quietly.
    """
    path = next((p for p in WORKFLOWS if p.name == RATCHET), None)
    assert path is not None, f"{RATCHET} is missing"
    trigger = _on(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    assert "pull_request" in trigger, "the ratchet must run on pull_request"
    on_pr = trigger["pull_request"] or {}
    for narrowing in ("paths", "paths-ignore"):
        assert narrowing not in on_pr, (
            f"{RATCHET} declares {narrowing}; the whole-suite gate must not be "
            "narrowed, or a test no workflow names goes unrun again"
        )


def test_a_tolerated_step_in_the_gate_is_followed_by_a_real_assertion() -> None:
    """continue-on-error must not become a silent reduction in coverage.

    The owner checkout is tolerated so a missing secret does not fail the gate
    for everyone. That same tolerance would swallow a genuine checkout failure,
    leaving the owner tests skipped and the job green. When the token is set, a
    later step has to prove the owner is actually present.
    """
    path = next(p for p in WORKFLOWS if p.name == RATCHET)
    workflow = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    steps = [step for _, step in _steps(workflow)]
    tolerated = [s for s in steps if s.get("continue-on-error")]
    if not tolerated:
        pytest.skip("the gate tolerates no step, so nothing can be swallowed")
    asserting = [
        s for s in steps
        if isinstance(s.get("run"), str) and "OWNER_PRESENT" in s["run"]
        and isinstance(s.get("if"), str) and "OWNER_TOKEN" in s["if"]
    ]
    assert asserting, (
        "the gate tolerates a step failure without any later step proving the "
        "owner arrived; a broken token would quietly shrink coverage"
    )
    # And it must come after the step whose failure it is covering for.
    assert steps.index(asserting[0]) > steps.index(tolerated[0])


def test_the_whole_suite_gate_installs_the_packages_dependencies() -> None:
    """Installing pytest alone collected 208 modules as import errors."""
    path = next(p for p in WORKFLOWS if p.name == RATCHET)
    body = path.read_text(encoding="utf-8")
    assert re.search(r"pip install[^\n]*-e\s*'\.\[dev", body), (
        "the ratchet must install the package's own dependencies, not just pytest"
    )
