"""Unresolved citation proposals must never imply a completed repair."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from scripts.inspect_remaining_deepwiki_citations import propose, inspect

class TestRemainingCitationProposals(unittest.TestCase):
    def test_ast_symbol_and_root_slash(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root/"stegverse").mkdir()
            (root/"stegverse/demo.py").write_text("def process():\n    return True\n",encoding="utf-8")
            (root/".github/workflows").mkdir(parents=True)
            (root/".github/workflows/check.yml").write_text("name: check\non: workflow_dispatch\n",encoding="utf-8")
            sha = "a"*40
            found = propose("stegverse/demo.py:process",root,sha)
            self.assertEqual(len(found["proposals"]),1)
            self.assertFalse(found["semantic_verified"])
            self.assertTrue(found["proposals"][0].endswith("#L1-L2"))
            slash = propose("/.github/workflows/check.yml:1-2",root,sha)
            self.assertEqual(len(slash["proposals"]),1)
            self.assertIn("/.github/workflows/check.yml#L1-L2",slash["proposals"][0])
            bad = propose("stegverse/demo.py:1-3",root,sha)
            self.assertEqual(bad["disposition"],"LINE_RANGE_INCORRECT")
            self.assertFalse(bad["proposals"])

    def test_unreviewed_complex_occurrence_stays_outstanding(self):
        with TemporaryDirectory() as temp:
            md = "# Page: A\n[foo.py:process]() malformed]()"
            prev = {"source_revision":"a"*40,"entries":[{"page":"A","offset":10,
                    "label":"foo.py:process","candidate_url":None}]}
            report=inspect(md,prev,Path(temp))
            self.assertEqual(report["malformed_contextual_occurrences"],1)
            self.assertFalse(report["publication_allowed"])

if __name__=="__main__":
    unittest.main()
