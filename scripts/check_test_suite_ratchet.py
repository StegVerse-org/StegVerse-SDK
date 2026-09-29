#!/usr/bin/env python3
"""Fail when a change adds a test failure the baseline does not already hold.

Every workflow in this repository is path-filtered to an explicit file list, so
a test that no workflow names is never run by CI. At the time this was written
that was 146 of 279 test files, and no workflow ran `tests/` as a directory.

The tests that went unrun included the ones guarding the capability map and
entry-point parity -- gates whose entire purpose is catching drift. Their CLI
reports ran in CI; the tests that exercise their claims did not. A parity report
reads `drift_count: 0` even when the map claims a capability the Chat contract
has dropped, because the report compares the map against a declared constant.
Only the test catches that, so only running the suite closes it.

This runs the whole suite and compares the *set* of failing tests against a
committed baseline. A set, not a count: a change that breaks one test while
another is fixed leaves the count unchanged, and that is exactly the regression
a count would miss.

The baseline is a ceiling, not an endorsement. Nothing here requires the
failures already on main to be fixed, and nothing stops the ceiling being
lowered as they are. Newly passing tests are reported so it can be tightened
deliberately rather than drifting.

Non-authorizing. This validates supplied source only: it mints no receipt,
confers no admission and observes no runtime.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sysconfig
import sys

GATE = "TEST_SUITE_RATCHET"
BASELINE = Path("data/test-suite-baseline.json")
REPO_ROOT = Path(__file__).resolve().parent.parent

# pytest prints one of these per failing or erroring test in -q output.
OUTCOME = re.compile(r"^(?:FAILED|ERROR)\s+(\S+)")
# The tail summary, e.g. "36 failed, 1388 passed, 7 skipped, 2 errors in 4.36s".
PASSED = re.compile(r"\b(\d+) passed\b")

REPAIR = ("fix the newly failing test, or - when the failure is genuinely "
          "pre-existing and newly surfaced - add it to the baseline in the same "
          "change, where a reviewer sees it")
COLLAPSE_REPAIR = ("the suite did not run to completion, so this gate proved "
                   "nothing; repair collection before reading the failure set")


class SuiteDidNotRun(RuntimeError):
    """Raised when the run cannot be trusted to have exercised the suite."""


def _pytest_command() -> list[str]:
    """Return a command that reaches the pytest belonging to this interpreter.

    Two problems make this worth being explicit about, and both were observed
    here rather than imagined.

    `python -m pytest` from the repository root imports the vendored `pytest/`
    package instead of the installed distribution, and that shim supports
    neither the flags this gate needs nor the whole suite.

    And PATH order is not a safe way to choose: this container has two pytest
    installations, and the one PATH resolves first produced 209 collection
    errors where the other ran the suite. A gate that silently picks the wrong
    runner reports a failure set for something other than the suite. So prefer
    the console script belonging to sys.executable, which is the pytest that
    shares the interpreter the tests import their dependencies from.
    """
    candidates = [Path(sysconfig.get_path("scripts")) / "pytest"]
    on_path = shutil.which("pytest")
    if on_path:
        candidates.append(Path(on_path))
    for candidate in candidates:
        if candidate.is_file() and REPO_ROOT not in candidate.resolve().parents:
            return [str(candidate)]
    return [sys.executable, "-m", "pytest"]


def run_suite(target: str) -> tuple[set[str], int, str]:
    """Return (failing test ids, passing test count) from one full suite run.

    --continue-on-collection-errors is required, not cosmetic: a module that
    cannot be imported otherwise aborts the session before any test body runs,
    and the gate would then pass having exercised nothing.
    """
    command = [*_pytest_command(), target, "-q", "--tb=no", "-p", "no:cacheprovider",
               "--continue-on-collection-errors"]
    completed = subprocess.run(command, capture_output=True, text=True, cwd=REPO_ROOT)
    failing = {
        match.group(1)
        for line in completed.stdout.splitlines()
        if (match := OUTCOME.match(line))
    }
    passed = [int(m.group(1)) for m in (PASSED.search(line)
                                        for line in completed.stdout.splitlines()) if m]
    if not passed:
        raise SuiteDidNotRun(
            "no pytest summary reporting passing tests was produced; "
            f"exit={completed.returncode} stderr={completed.stderr.strip()[:400]}"
        )
    return failing, max(passed), " ".join(command)


def load_baseline(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"{GATE}: baseline {path} is missing; generate it with --write-baseline")
    return json.loads(path.read_text(encoding="utf-8"))


def excluded_tests(baseline: dict) -> set[str]:
    """Tests the gate ignores in both directions, each naming why.

    An exclusion is not a silent retry. It is recorded in the baseline with a
    reason, so what the gate is not watching stays visible to a reviewer.
    """
    return {row["test"] for row in (baseline.get("excluded") or [])}


def compare(observed: set[str], passed: int, baseline: dict) -> dict:
    """Classify the run against the baseline.

    An excluded test can neither fail the gate nor be reported as fixed.
    """
    known = set(baseline.get("known_failing") or [])
    excluded = excluded_tests(baseline)
    floor = int(baseline.get("minimum_passing") or 0)
    return {
        "observed_failing_count": len(observed),
        "baseline_failing_count": len(known),
        "observed_passing_count": passed,
        "minimum_passing": floor,
        # A suite that collapses to a fraction of its tests reports few
        # failures, which would otherwise read as an improvement.
        "suite_collapsed": passed < floor,
        "newly_failing": sorted(observed - known - excluded),
        "newly_passing": sorted(known - observed - excluded),
        "excluded": sorted(excluded),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="tests")
    parser.add_argument("--baseline", default=str(BASELINE))
    parser.add_argument("--write-baseline", action="store_true",
                        help="record the current failing set as the baseline")
    parser.add_argument("--findings", action="store_true",
                        help="emit structured findings instead of prose")
    args = parser.parse_args()
    path = REPO_ROOT / args.baseline

    try:
        observed, passed, runner = run_suite(args.target)
    except SuiteDidNotRun as exc:
        print(f"{GATE}: SUITE_DID_NOT_RUN {exc}")
        return 1

    if args.write_baseline:
        existing = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        excluded = existing.get("excluded") or []
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "schema": "stegverse.test-suite-baseline/v1",
            "target": args.target,
            "known_failing": sorted(x for x in observed
                                    if x not in {r["test"] for r in excluded}),
            # Preserved across regeneration: an exclusion and its reason survive.
            "excluded": excluded,
            # A floor, not the observed count: adding tests must not need a
            # baseline rewrite, but losing most of them must fail.
            "minimum_passing": int(passed * 0.95),
            "observed_passing_at_baseline": passed,
            "baseline_is_a_ceiling_not_an_endorsement": True,
            "authority_effect": "NONE",
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"{GATE}: wrote baseline of {len(observed)} failing tests "
              f"({passed} passing) to {path}")
        print(f"{GATE}: runner {runner}")
        return 0

    report = compare(observed, passed, load_baseline(path))

    if args.findings:
        rows = [
            {
                "gate": GATE, "task_id": test_id,
                "predicate_id": "NO_NEW_TEST_FAILURE",
                "detail": f"{test_id} fails on this head and is not in the baseline",
                "evidence": [str(args.baseline)], "repair": REPAIR,
                "retry_entrypoint": f"{Path(__file__).name} --findings",
                "severity": "HIGH", "remediation_class": "DISPATCHABLE",
                "authority_effect": "NONE_FINDING_ONLY",
            }
            for test_id in report["newly_failing"]
        ]
        if report["suite_collapsed"]:
            rows.append({
                "gate": GATE, "task_id": "SUITE_COLLAPSED",
                "predicate_id": "SUITE_RAN_TO_COMPLETION",
                "detail": (f"{report['observed_passing_count']} tests passed, below the "
                           f"declared floor of {report['minimum_passing']}"),
                "evidence": [str(args.baseline)], "repair": COLLAPSE_REPAIR,
                "retry_entrypoint": f"{Path(__file__).name} --findings",
                "severity": "HIGH", "remediation_class": "DISPATCHABLE",
                "authority_effect": "NONE_FINDING_ONLY",
            })
        print(json.dumps({
            "gate": GATE, "finding_count": len(rows), "findings": rows,
            "authority_effect": "NONE_FINDING_ONLY",
        }, indent=2, sort_keys=True))
        return 1 if rows else 0

    for test_id in report["newly_failing"]:
        print(f"{GATE}: NEW_FAILURE {test_id}")
    for test_id in report["newly_passing"]:
        print(f"{GATE}: NEWLY_PASSING {test_id} - tighten the baseline")
    if report["suite_collapsed"]:
        print(f"{GATE}: SUITE_COLLAPSED passing={report['observed_passing_count']} "
              f"floor={report['minimum_passing']}")
    print(
        f"{GATE}_AUDIT observed={report['observed_failing_count']} "
        f"baseline={report['baseline_failing_count']} "
        f"passing={report['observed_passing_count']} "
        f"new={len(report['newly_failing'])} "
        f"newly_passing={len(report['newly_passing'])} "
        f"excluded={len(report['excluded'])}"
    )
    print(f"{GATE}_RUNNER {runner}")
    return 1 if (report["newly_failing"] or report["suite_collapsed"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
