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
