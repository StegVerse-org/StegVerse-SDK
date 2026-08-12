from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_github_fallback_boundary.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("github_fallback_boundary", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class GitHubFallbackBoundaryTests(unittest.TestCase):
    def test_canonical_workflows_satisfy_boundary(self) -> None:
        module = load_validator()
        workflows = ROOT / ".github" / "workflows"
        failures = {
            path.name: module.validate_workflow(path)
            for path in sorted(workflows.glob("*.yml"))
            if module.validate_workflow(path)
        }
        self.assertEqual(failures, {})

    def test_forbidden_authority_patterns_fail(self) -> None:
        module = load_validator()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.yml"
            path.write_text(
                """name: bad\non:\n  push:\npermissions:\n  contents: write\njobs:\n  bad:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: git push\n""",
                encoding="utf-8",
            )
            failures = module.validate_workflow(path)
        self.assertTrue(any(item.startswith("automatic_hosted_trigger") for item in failures))
        self.assertTrue(any(item.startswith("forbidden_fragment") for item in failures))

    def test_manual_permissions_empty_wrapper_passes(self) -> None:
        module = load_validator()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "good.yml"
            path.write_text(
                """name: good\non:\n  workflow_dispatch:\npermissions: {}\njobs:\n  validate:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo validation-only\n""",
                encoding="utf-8",
            )
            failures = module.validate_workflow(path)
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
