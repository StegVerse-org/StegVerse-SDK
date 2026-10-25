"""Every pip install the SDK's workflows run is held to constraints/sdk-install.txt (SDK#484 V-P5).

The constraints file pins the exact transitive install set: one exact version per package per
Python line (3.9 below the marker, 3.10+ above it). Each workflow that runs pip sets
PIP_CONSTRAINT to that file at the path its source tree is materialized to, so nothing a
workflow installs floats, including the setuptools/wheel build backend pip installs in
isolation. A floating line, an uncovered top-level install or a workflow without the
constraint fails closed with the six fields. The surfaces the G17 registry freezes byte for byte
(control/workflow-surface-registry.json, SDK#560) cannot take the PIP_CONSTRAINT line until the
registry owner (StegVerse-org/.github#163) re-pins them; their installs are still checked.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSTRAINTS = ROOT / "constraints" / "sdk-install.txt"
WORKFLOWS = ROOT / ".github" / "workflows"
MARKERS = {None, 'python_version < "3.10"', 'python_version >= "3.10"'}
LINE = re.compile(r"^([a-z0-9][a-z0-9._-]*)==([0-9][0-9A-Za-z.+!-]*)(?:\s*;\s*(.+))?$")
# What the workflows install by name, beside the SDK itself (".", ".[dev]", dist/*.whl).
TOP_LEVEL = {"pytest", "build", "twine", "wheel", "pip", "setuptools"}
# Frozen by verbatim_sha256 (or carried verbatim from folded records) in the G17 registry.
G17_FROZEN = {"release.yml", "validation-dispatcher.yml"}
SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair",
              "retry_entrypoint", "owning_existing_goal", "next_attempt")


def refusal(failure_code: str, failed_predicate: str, detail: str) -> dict:
    return {
        "disposition": "FAIL_CLOSED",
        "failure_code": failure_code,
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": f"{detail}; re-resolve with the command in {CONSTRAINTS.name}'s header",
        "retry_entrypoint": "tests/test_install_constraints_guard.py",
        "owning_existing_goal": "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001",
        "next_attempt": "rerun the guard after the constraints file and the workflows agree",
    }


def parse(text: str) -> tuple[dict, list]:
    """{(name, marker): version} and the six-field refusals for every malformed line."""
    pins, refusals = {}, []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = LINE.match(line)
        if not match or match.group(3) not in MARKERS:
            refusals.append(refusal("CONSTRAINT_NOT_EXACT", "EVERY_CONSTRAINT_IS_NAME_EQUALS_VERSION", repr(line)))
            continue
        name, version, marker = match.groups()
        if (name, marker) in pins:
            refusals.append(refusal("CONSTRAINT_DUPLICATED", "ONE_VERSION_PER_PACKAGE_PER_PYTHON_LINE", repr(line)))
        pins[(name, marker)] = version
    for name in {n for n, _ in pins}:
        markers = {m for n, m in pins if n == name}
        if markers not in ({None}, MARKERS - {None}):
            refusals.append(refusal("CONSTRAINT_PYTHON_LINE_UNCOVERED", "EVERY_PACKAGE_PINNED_ON_BOTH_PYTHON_LINES",
                                    f"{name} has markers {sorted(map(str, markers))}"))
    return pins, refusals


def _versions(pins: dict, name: str) -> list[tuple[int, ...]]:
    return [tuple(int(p) for p in re.findall(r"\d+", v)[:3]) for (n, _), v in pins.items() if n == name]


def workflow_refusals() -> list:
    refusals = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if "pip install" not in text:
            continue
        tar = "archive/" in text and "/tmp/source" in text
        expected = ("/tmp/source/constraints/sdk-install.txt" if tar
                    else "${{ github.workspace }}/constraints/sdk-install.txt")
        if f"PIP_CONSTRAINT: {expected}" not in text and path.name not in G17_FROZEN:
            refusals.append(refusal("WORKFLOW_INSTALL_UNCONSTRAINED", "EVERY_WORKFLOW_PIP_INSTALL_USES_SDK_CONSTRAINTS",
                                    f"{path.name} lacks PIP_CONSTRAINT: {expected}"))
        for command in re.findall(r"pip install([^\n|&;]*)", text):
            for token in command.split():
                if token.startswith("-") or token.startswith(("'.", '".', ".", "dist/", "/")):
                    continue
                if re.split(r"[<>=\[]", token.strip("'\""))[0].lower() not in TOP_LEVEL:
                    refusals.append(refusal("WORKFLOW_INSTALLS_UNDECLARED_PACKAGE", "WORKFLOW_INSTALLS_ARE_CONSTRAINED_TOP_LEVEL",
                                            f"{path.name} installs {token}"))
    return refusals


def test_constraints_are_exact_and_cover_both_python_lines():
    pins, refusals = parse(CONSTRAINTS.read_text(encoding="utf-8"))
    assert refusals == [], refusals
    assert TOP_LEVEL <= {n for n, _ in pins}


def test_pins_satisfy_the_declared_ranges():
    pins, _ = parse(CONSTRAINTS.read_text(encoding="utf-8"))
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"pytest>=7.0"' in pyproject and 'requires = ["setuptools>=61.0", "wheel"]' in pyproject
    assert all(v >= (7, 0) for v in _versions(pins, "pytest"))
    assert all(v >= (61, 0) for v in _versions(pins, "setuptools"))


def test_every_workflow_pip_install_is_constrained():
    refusals = workflow_refusals()
    assert refusals == [], refusals


def test_the_guard_refuses_drift_with_six_fields():
    _, refusals = parse('pytest>=8\nwheel==1 ; sys_platform == "linux"\nbuild==1.0 ; python_version < "3.10"\n'
                        "pip==1\npip==2\n")
    codes = sorted(r["failure_code"] for r in refusals)
    assert codes == ["CONSTRAINT_DUPLICATED", "CONSTRAINT_NOT_EXACT", "CONSTRAINT_NOT_EXACT",
                     "CONSTRAINT_PYTHON_LINE_UNCOVERED"]
    assert all(r[f] for r in refusals for f in SIX_FIELDS)
