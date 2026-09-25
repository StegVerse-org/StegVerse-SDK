"""First-party guide must cite real source spans and retain nonpublication boundary."""
from pathlib import Path
import re
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs/deepwiki-review/FIRST_PARTY_SOURCE_GUIDE.md"
PIN = "9cf1d69c770ea92048a0883adf6ff0dfa09797db"
SOURCE_LINK = re.compile(
    r"https://github.com/StegVerse-org/StegVerse-SDK/blob/([0-9a-f]{40})/"
    r"([^\s)]+?)#L(\d+)(?:-L(\d+))?"
)
EXACT_LINES = (
    ("pyproject.toml", 29, "requests>=2.28.0"),
    ("pyproject.toml", 30, "pyyaml>=6.0"),
    ("stegverse/manifest_builder.py", 211, "def build_manifest"),
    ("stegverse/manifest_contract.py", 165, "def validate_ingress_manifest"),
    ("stegverse/route_resolution.py", 152, "def route_from_manifest"),
    ("stegverse/purpose_bound_worker_processor.py", 63, "partition reconstruction mismatch"),
    ("stegverse/atomic_task_worker_processor.py", 23, "TEST2_SCENARIO"),
    ("stegverse/atomic_task_worker_processor.py", 24, "TEST3_SCENARIO"),
    ("stegverse/atomic_task_worker_processor.py", 25, "TEST3_LEGACY_SCENARIO"),
    ("stegverse/governance_reference_graph.py", 23, "AUTHORITY_BOUNDARY"),
    ("stegverse/ecosystem_chat_pipeline.py", 27, "build_persistence_plan"),
    ("stegverse/ecosystem_chat_pipeline.py", 28, "build_destination_binding"),
    ("stegverse/ecosystem_chat_pipeline.py", 36, "write_with_adapter"),
)

class FirstPartyGuideTests(unittest.TestCase):
    def test_literal_source_facts_remain_current(self):
        for name, lineno, literal in EXACT_LINES:
            with self.subTest(file=name, line=lineno):
                lines = (ROOT / name).read_text(encoding="utf-8").splitlines()
                self.assertIn(literal, lines[lineno - 1])

    def test_every_pinned_source_link_exists_within_bounds(self):
        guide = GUIDE.read_text(encoding="utf-8")
        matches = SOURCE_LINK.findall(guide)
        self.assertGreaterEqual(len(matches), 10)
        for revision, encoded, a, b in matches:
            self.assertEqual(revision, PIN)
            file = (ROOT / unquote(encoded)).resolve()
            self.assertTrue(file.is_relative_to(ROOT.resolve()))
            self.assertTrue(file.is_file(), file)
            length = len(file.read_text(encoding="utf-8").splitlines())
            self.assertLessEqual(int(b or a), length)
            self.assertLessEqual(int(a), int(b or a))

    def test_no_generated_page_import_or_misleading_runtime_claim(self):
        guide = GUIDE.read_text(encoding="utf-8")
        self.assertNotIn("]()", guide)
        self.assertIn("not an import of external generated DeepWiki text", guide)
        self.assertIn("not live runtime proof", guide)
        self.assertIn("separate decisions", guide)

if __name__ == "__main__":
    unittest.main()
