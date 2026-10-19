"""The SDK adds no third-party dependency by accident (owner directive: reduce, never add).

Runtime code under stegverse/ and every .py file at the repository root may import a
third-party module only lazily and inside try/except ImportError, so the package installs and
imports with the standard library alone. pyproject.toml declares no runtime dependency, and
the [dev] extra holds pytest only. scripts/capture_sdk_validation_diagnostic.py checks for
exactly the declared dev modules. (SDK#484 V-P3 dependency inventory.)
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL = {"stegverse", "stegverse_sdk", "scripts", "tests", "tools", "examples", "experiments", "pytest"}


def _third_party_imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    guarded: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and any(
                isinstance(h.type, ast.Name) and h.type.id in ("ImportError", "ModuleNotFoundError")
                or isinstance(h.type, ast.Tuple) and any(getattr(e, "id", "") in ("ImportError", "ModuleNotFoundError")
                                                         for e in h.type.elts)
                for h in node.handlers):
            for inner in ast.walk(ast.Module(body=node.body, type_ignores=[])):
                guarded.add(id(inner))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module.split(".")[0]]
        else:
            continue
        for name in names:
            if name not in sys.stdlib_module_names and name not in LOCAL and name != "__future__":
                yield name, node.lineno, id(node) in guarded


def test_runtime_and_root_modules_import_third_party_code_only_guarded():
    files = sorted((ROOT / "stegverse").rglob("*.py")) + sorted(ROOT.glob("*.py"))
    unguarded = [f"{p.relative_to(ROOT)}:{line}:{name}" for p in files if "__pycache__" not in p.parts
                 for name, line, ok in _third_party_imports(p) if not ok and p.name != "setup.py"]
    assert unguarded == [], f"FAIL_CLOSED UNDECLARED_RUNTIME_DEPENDENCY: {unguarded}"


def test_declared_dependencies_stay_minimal():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    runtime = re.search(r"^dependencies\s*=\s*\[(.*?)\]", text, re.S | re.M)
    assert runtime and not re.findall(r'"([^"]+)"', runtime.group(1)), "runtime dependencies must stay empty"
    dev = re.search(r"^dev\s*=\s*\[(.*?)\]", text, re.S | re.M)
    assert dev and re.findall(r'"([^"]+)"', dev.group(1)) == ["pytest>=7.0"]


def test_diagnostic_checks_exactly_the_declared_dev_modules():
    text = (ROOT / "scripts" / "capture_sdk_validation_diagnostic.py").read_text(encoding="utf-8")
    assert 'REQUIRED_MODULES = ["pytest"]' in text


def test_guard_flags_an_unguarded_third_party_import(tmp_path):
    probe = tmp_path / "probe.py"
    probe.write_text("import requests\ntry:\n    import yaml\nexcept ImportError:\n    yaml = None\n", encoding="utf-8")
    found = {(name, ok) for name, _, ok in _third_party_imports(probe)}
    assert found == {("requests", False), ("yaml", True)}


# SDK#484 V-P4. Every git pin in an extra, by (extra, package). StegCore carries two values and
# cannot carry one yet: governed-test is bound to the SDK 1.2.0 final TVC release receipt
# (tests/test_release_dependency_alignment.py, release-dependency-alignment-validation.yml), and
# manifold-test needs stegcore.manifold_governance, added six commits later. The manifold pin
# descends from the release pin (git merge-base --is-ancestor, StegCore clone, 2026-10-19), so
# the single pin is 9939739 once a successor release receipt names it; that rebind is the
# owner's. Until then any other value, or a third one, fails closed.
STEGCORE_RELEASE_PIN = "ef38410505b0ef3e84148892b1d6e3cdef20f300"
STEGCORE_SINGLE_PIN = "99397392462b8e39a510ec6d9e543551270bd402"
DECLARED_GIT_PINS = {
    ("governed-test", "stegcore"): ("StegVerse-Labs/StegCore", STEGCORE_RELEASE_PIN),
    ("governed-test", "stegverse-core-lite"): ("Data-Continuation/core-lite", "72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8"),
    ("manifold-test", "stegcore"): ("StegVerse-Labs/StegCore", STEGCORE_SINGLE_PIN),
}
GIT_PIN = re.compile(r'"([A-Za-z0-9_.-]+)\s*@\s*git\+https://github\.com/([^/@\s]+/[^/@\s]+?)\.git@([^"\s;]+)')


def _extra_git_pins(text: str) -> dict:
    extras = re.search(r"^\[project\.optional-dependencies\]\s*$(.*?)(?=^\[)", text, re.S | re.M).group(1)
    pins = {}
    for name, body in re.findall(r"^([A-Za-z0-9_-]+)\s*=\s*\[(.*?)\]", extras, re.S | re.M):
        for package, repository, ref in GIT_PIN.findall(body):
            pins[(name, package.lower())] = (repository, ref)
    return pins


def pin_refusal(pins: dict) -> dict | None:
    """Six-field FAIL_CLOSED when the extras' git pins differ from DECLARED_GIT_PINS, else None."""
    if pins == DECLARED_GIT_PINS:
        return None
    return {
        "disposition": "FAIL_CLOSED",
        "failure_code": "UNDECLARED_GIT_PIN",
        "failed_predicate": "EXTRA_GIT_PINS_EQUAL_DECLARED_GIT_PINS",
        "required_evidence_or_repair": (
            f"found {sorted(pins.items())}, declared {sorted(DECLARED_GIT_PINS.items())}; a StegCore value other "
            f"than {STEGCORE_RELEASE_PIN} (release receipt) and {STEGCORE_SINGLE_PIN} needs the owner's release rebind"),
        "retry_entrypoint": "tests/test_dependency_inventory_guard.py",
        "owning_existing_goal": "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001",
        "next_attempt": "rerun the guard after DECLARED_GIT_PINS and the release alignment evidence agree",
    }


def test_extra_git_pins_are_exactly_the_declared_pins():
    refusal = pin_refusal(_extra_git_pins((ROOT / "pyproject.toml").read_text(encoding="utf-8")))
    assert refusal is None, refusal


def test_stegcore_has_at_most_the_release_pin_and_its_descendant():
    values = {ref for (_, package), (_, ref) in DECLARED_GIT_PINS.items() if package == "stegcore"}
    assert values <= {STEGCORE_RELEASE_PIN, STEGCORE_SINGLE_PIN}
    release = (ROOT / "tests" / "test_release_dependency_alignment.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "release-dependency-alignment-validation.yml").read_text(encoding="utf-8")
    assert f'STEGCORE_TVC_SOURCE_PARENT = "{STEGCORE_RELEASE_PIN}"' in release
    assert f"'source_parent_commit': '{STEGCORE_RELEASE_PIN}'" in workflow


def test_a_second_stegcore_value_fails_closed_with_six_fields():
    pins = dict(DECLARED_GIT_PINS)
    pins[("governed-test", "stegcore")] = ("StegVerse-Labs/StegCore", "0" * 40)
    refusal = pin_refusal(pins)
    assert refusal["failure_code"] == "UNDECLARED_GIT_PIN"
    assert all(refusal[f] for f in ("failure_code", "failed_predicate", "required_evidence_or_repair",
                                    "retry_entrypoint", "owning_existing_goal", "next_attempt"))
    text = '[project.optional-dependencies]\nx = [\n    "stegcore @ git+https://github.com/StegVerse-Labs/StegCore.git@main",\n]\n\n[t]\n'
    assert _extra_git_pins(text) == {("x", "stegcore"): ("StegVerse-Labs/StegCore", "main")}


def _optional_owner_imports():
    found = set()
    for path in sorted((ROOT / "stegverse").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                modules = [node.module]
            elif isinstance(node, ast.Import):
                modules = [a.name for a in node.names]
            else:
                continue
            found |= {(m.split(".")[0], m, rel) for m in modules if m.split(".")[0] in ("stegos", "stegbrowser")}
    return found


def test_undeclared_owner_packages_are_exactly_the_listed_ones():
    from stegverse.optional_package_refusal import UNDECLARED_OPTIONAL_PACKAGES
    assert _optional_owner_imports() == {(p, m, site) for p, (m, site) in UNDECLARED_OPTIONAL_PACKAGES.items()}


def test_each_undeclared_owner_package_refuses_with_six_fields():
    import stegverse.evaluator_governance_runtime as runtime
    import stegverse.governed_llm_fan as fan
    blocked = ("stegos", "stegos.intr_security_posture_resolution", "stegbrowser", "stegbrowser.llm_browser_execution")
    saved = {name: sys.modules.get(name, ...) for name in blocked}
    sys.modules.update({name: None for name in blocked})
    try:
        records = []
        for call, error in ((runtime._load_intr_resolver, runtime.IntrResolverUnavailable),
                            (lambda: fan._resolve_executor(None), fan.GovernedLlmFanError)):
            try:
                call()
            except error as exc:
                records.append(exc.disposition)
            else:
                raise AssertionError(f"{call} did not refuse")
    finally:
        for name, module in saved.items():
            if module is ...:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
    for record in records:
        assert record["disposition"] == "FAIL_CLOSED"
        assert all(record[f] for f in ("failure_code", "failed_predicate", "required_evidence_or_repair",
                                       "retry_entrypoint", "owning_existing_goal", "next_attempt"))
