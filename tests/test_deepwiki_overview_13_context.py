"""Keep the 13 Overview source/context adjudications bounded and nonpublishing."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/deepwiki-review/OVERVIEW_13_CONTEXT_ADJUDICATION.md"
PIN = "175c1fa11967d14986682a72efb4171afe40aece"
LINK = re.compile(
    r"https://github.com/StegVerse-org/StegVerse-SDK/blob/([a-f0-9]{40})/"
    r"([\w./-]+)#L(\d+)(?:-L(\d+))?"
)


class OverviewContextAuditTests(unittest.TestCase):
    def test_every_13_pending_occurrence_is_scoped(self):
        text = DOC.read_text(encoding="utf-8")
        rows = text.split("## Separate first-party corrected description", 1)[0]
        expected_groups = (
            "0, 1", "2, 3", "4, 5", "6", "10", "11", "14, 15", "16, 17"
        )
        self.assertEqual(len(expected_groups), 8)
        for group in expected_groups:
            self.assertRegex(rows, r"(?m)^\\| " + re.escape(group) + r" \\|")
        self.assertIn("indices 12 and 13", text)
        self.assertEqual(text.count("`DENY:"), 8)

    def test_source_revisions_and_ranges_are_exact(self):
        text = DOC.read_text(encoding="utf-8")
        links = LINK.findall(text)
        self.assertGreaterEqual(len(links), 12)
        for revision, rel, start, end in links:
            with self.subTest(source=rel, first=start):
                self.assertEqual(revision, PIN)
                source = ROOT / rel
                self.assertTrue(source.is_file(), str(source))
                length = len(source.read_text(encoding="utf-8").splitlines())
                self.assertGreaterEqual(int(start), 1)
                self.assertLessEqual(int(end or start), length)
                self.assertLessEqual(int(start), int(end or start))

    def test_original_generated_copy_and_pages_builder_stay_outside_scope(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertNotIn("]()", text)
        self.assertNotIn("import generated", text.lower())
        self.assertIn("unchanged and unpublished", text)
        builder = (ROOT / "scripts/build_sdk_public_wiki.py").read_text(encoding="utf-8")
        self.assertNotIn("OVERVIEW_13_CONTEXT_ADJUDICATION.md", builder)
        self.assertNotIn("GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION.md", builder)


if __name__ == "__main__":
    unittest.main()
