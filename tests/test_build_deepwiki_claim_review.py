"""Evidence-only claim-packet generation never declares semantic verification."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from scripts.build_deepwiki_claim_review import build, source_span

class DeepWikiClaimPacketTests(unittest.TestCase):
    def test_source_excerpt_is_not_semantic_verification(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "unit.py").write_text("def example():\n    return 1\n", encoding="utf-8")
            md = "# Page: Example\nThe example returns one [unit.py:1-2]()."
            p = {"source_revision": "a" * 40, "entries": [
                {"page": "Example", "label": "unit.py:1-2",
                 "offset": md.index("[unit.py:1-2]()"),
                 "disposition": "VALID_SOURCE_LINE_CANDIDATE_SEMANTICS_UNREVIEWED",
                 "candidate_url": "https://github.com/example#L1-L2",
                 "candidate_path": "unit.py"}]}
            result = build(md, p, root)
            self.assertEqual(result["candidate_total"], 1)
            self.assertEqual(result["candidate_unique_urls"], 1)
            self.assertEqual(result["rows"][0]["source_status"], "EXACT_DECLARED_SOURCE_SPAN")
            self.assertEqual(result["semantic_verified_count"], 0)
            self.assertFalse(result["publication_allowed"])

    def test_missing_source_is_explicit(self):
        with TemporaryDirectory() as tmp:
            snippet, verdict = source_span(Path(tmp), {
                "candidate_path": "not-found.py", "label": "not-found.py:1"})
            self.assertIsNone(snippet)
            self.assertEqual(verdict, "SOURCE_NOT_FOUND")

if __name__ == "__main__":
    unittest.main()
