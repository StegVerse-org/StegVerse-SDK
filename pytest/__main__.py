#!/usr/bin/env python3
"""Minimal `python -m pytest` runner for repository route-artifact tests.

Supported surface:
- positional Python test files
- functions named test_*
- plain assert statements
- tmp_path fixture

This is intentionally small and exists so CI can run route-artifact tests even
when the workflow runner has not installed external pytest.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
import tempfile
import traceback
from pathlib import Path
from types import ModuleType


ROOT = Path.cwd()


def load_module(path: Path) -> ModuleType:
    module_name = path.with_suffix("").as_posix().replace("/", "_").replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load test module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def call_test(function) -> None:
    signature = inspect.signature(function)
    kwargs = {}
    temp_dirs: list[tempfile.TemporaryDirectory[str]] = []
    try:
        for name in signature.parameters:
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


def main(argv: list[str]) -> int:
    files = [Path(arg) for arg in argv if arg.endswith(".py")]
    if not files:
        files = sorted((ROOT / "tests").glob("test_*.py"))

    total = 0
    failed = 0
    for path in files:
        module = load_module(path)
        for name, function in iter_tests(module):
            total += 1
            label = f"{path}::{name}"
            try:
                call_test(function)
                print(f"PASS {label}")
            except BaseException:
                failed += 1
                print(f"FAIL {label}", file=sys.stderr)
                traceback.print_exc()

    if failed:
        print(f"{failed} failed, {total - failed} passed")
        return 1
    print(f"{total} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
