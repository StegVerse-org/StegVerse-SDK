"""Guard for fixtures/protocol_v1_conformance_profile_v1.json (StegVerse-Labs/.github#3369).

The profile maps each Protocol v1.0 acceptance item to existing tests. These
checks keep it honest: every SDK reference must name a test that exists here,
every Labs reference must be pinned to an exact commit, and nothing in the
profile may claim authority or runtime evidence. Standard library only.
"""
from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "fixtures" / "protocol_v1_conformance_profile_v1.json"

REQUIRED_ITEMS = {
    "NON_ALLOW_PRODUCES_NO_EFFECT",
    "AUTHENTIC_ALLOW_WITH_BOUNDED_EFFECT",
    "PAYLOAD_TAMPER",
    "REPLAY",
    "FORGED_IDENTITY",
    "STALE_HEAD_OR_FENCE",
    "WRONG_ROUTE",
    "MISSING_AUTHORITY",
    "MISSING_OR_INVALID_RECEIPTS",
    "RECONSTRUCTION_FAILURE_NON_GATING",
}
NODE = re.compile(r"^tests/test_[a-z0-9_]+\.py::(?:[A-Za-z_][A-Za-z0-9_]*::)?test_[a-z0-9_]+$")
SHA = re.compile(r"^[0-9a-f]{40}$")


def _defined_tests(path: Path) -> set[str]:
    """Node ids (path::[Class::]test) defined in one test module."""
    rel = path.relative_to(ROOT).as_posix()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            found.add(f"{rel}::{node.name}")
        if isinstance(node, ast.ClassDef):
            for member in node.body:
                if isinstance(member, ast.FunctionDef) and member.name.startswith("test_"):
                    found.add(f"{rel}::{node.name}::{member.name}")
    return found


class ProtocolV1ConformanceProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = json.loads(PROFILE.read_text(encoding="utf-8"))

    def test_profile_is_non_authorizing(self) -> None:
        self.assertEqual(self.profile["schema"], "stegverse.protocol-v1-conformance-profile/v1")
        self.assertEqual(self.profile["authority_effect"], "NONE")
        self.assertNotEqual(self.profile["bounded_effect"]["status"], "ADOPTED_WITHOUT_CONSENSUS")

    def test_every_acceptance_item_is_mapped_once(self) -> None:
        items = [entry["item"] for entry in self.profile["acceptance"]]
        self.assertEqual(len(items), len(set(items)))
        self.assertEqual(set(items), REQUIRED_ITEMS)
        for entry in self.profile["acceptance"]:
            self.assertTrue(entry["refs"], entry["item"])

    def test_sdk_references_name_existing_tests(self) -> None:
        cache: dict[str, set[str]] = {}
        for entry in self.profile["acceptance"]:
            for ref in entry["refs"]:
                self.assertRegex(ref["node"], NODE)
                if ref["source"] != "sdk":
                    continue
                path = ref["node"].split("::", 1)[0]
                if path not in cache:
                    module = ROOT / path
                    self.assertTrue(module.is_file(), f"missing test module {path}")
                    cache[path] = _defined_tests(module)
                self.assertIn(ref["node"], cache[path], f"{entry['item']}: test not found")

    def test_external_references_are_pinned_to_exact_commits(self) -> None:
        sources = self.profile["external_sources"]
        for name, source in sources.items():
            self.assertRegex(source["commit"], SHA, name)
        for entry in self.profile["acceptance"]:
            for ref in entry["refs"]:
                if ref["source"] == "sdk":
                    self.assertNotIn("line", ref)
                    continue
                self.assertIn(ref["source"], sources)
                self.assertIsInstance(ref.get("line"), int)
                self.assertGreater(ref["line"], 0)

    def test_no_reference_claims_runtime_or_completion_evidence(self) -> None:
        text = PROFILE.read_text(encoding="utf-8")
        for claim in ("SANDBOX_RUNTIME_OBSERVED", "EXTERNAL_PROVIDER_OBSERVED", "END_TO_END", "MASTER_RECORDS_RECONSTRUCTED"):
            self.assertNotIn(claim, text)
        self.assertTrue(self.profile["not_covered_by_tests"])


if __name__ == "__main__":
    unittest.main()
