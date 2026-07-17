#!/usr/bin/env python3
"""Minimal ``python -m pytest`` runner for repository tests.

Supported surface:
- positional Python test files or automatic ``tests/test_*.py`` discovery
- functions named ``test_*``
- plain assert statements
- ``tmp_path`` fixture
- ``pytest.raises``
- ``pytest.mark.parametrize``
- ``--maxfail=N``

The runner is intentionally bounded and does not claim full pytest
compatibility.
"""
from __future__ import annotations

import importlib.util
import inspect
import itertools
import sys
import tempfile
import traceback
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable

ROOT = Path.cwd()


def load_module(path: Path) -> ModuleType:
    module_name = path.with_suffix("").as_posix().replace("/", "_").replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load test module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parameter_cases(function) -> list[dict[str, Any]]:
    declarations: Iterable[tuple[tuple[str, ...], list[Any]]] = getattr(
        function, "_pytest_parametrize", []
    )
    cases: list[dict[str, Any]] = [{}]
    for names, values in declarations:
        expanded: list[dict[str, Any]] = []
        for base, value in itertools.product(cases, values):
            if len(names) == 1:
                row = (value,)
            else:
                if not isinstance(value, (tuple, list)) or len(value) != len(names):
                    raise ValueError(
                        f"parametrize value {value!r} does not match names {names!r}"
                    )
                row = tuple(value)
            merged = dict(base)
            merged.update(dict(zip(names, row)))
            expanded.append(merged)
        cases = expanded
    return cases


def call_test(function, parameters: dict[str, Any]) -> None:
    signature = inspect.signature(function)
    kwargs = dict(parameters)
    temp_dirs: list[tempfile.TemporaryDirectory[str]] = []
    try:
        for name in signature.parameters:
            if name in kwargs:
                continue
            if name == "tmp_path":
                temp_dir = tempfile.TemporaryDirectory()
                temp_dirs.append(temp_dir)
                kwargs[name] = Path(temp_dir.name)
            else:
                raise RuntimeError(f"unsupported test fixture: {name}")
        function(**kwargs)
    finally:
        for temp_dir in temp_dirs:
            temp_dir.cleanup()


def iter_tests(module: ModuleType):
    for name in sorted(dir(module)):
        if not name.startswith("test_"):
            continue
        value = getattr(module, name)
        if callable(value):
            yield name, value


def selected_files(argv: list[str]) -> list[Path]:
    files = [Path(arg.split("::", 1)[0]) for arg in argv if ".py" in arg]
    if files:
        return list(dict.fromkeys(files))
    return sorted((ROOT / "tests").glob("test_*.py"))


def max_failures(argv: list[str]) -> int | None:
    for index, arg in enumerate(argv):
        if arg.startswith("--maxfail="):
            return max(1, int(arg.split("=", 1)[1]))
        if arg == "--maxfail" and index + 1 < len(argv):
            return max(1, int(argv[index + 1]))
    return None


def main(argv: list[str]) -> int:
    files = selected_files(argv)
    maxfail = max_failures(argv)
    total = 0
    failed = 0
    stop = False
    for path in files:
        if stop:
            break
        module = load_module(path)
        for name, function in iter_tests(module):
            if stop:
                break
            for index, parameters in enumerate(parameter_cases(function)):
                total += 1
                suffix = f"[{index}]" if parameters else ""
                label = f"{path}::{name}{suffix}"
                try:
                    call_test(function, parameters)
                    print(f"PASS {label}")
                except BaseException:
                    failed += 1
                    print(f"FAIL {label}", file=sys.stderr)
                    traceback.print_exc()
                    if maxfail is not None and failed >= maxfail:
                        stop = True
                        break

    if failed:
        print(f"{failed} failed, {total - failed} passed")
        return 1
    print(f"{total} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
