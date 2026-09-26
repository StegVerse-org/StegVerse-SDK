"""Current-source guards for the original nineteen cross-framework citations."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/"docs/deepwiki-review/CROSS_FRAMEWORK_19_SOURCE_DECISIONS.json"
INDICES={410,411,412,413,414,416,418,421,422,423,424,425,426,428,433,434,436,437,438}

class CrossFrameworkSourceReviewTests(unittest.TestCase):
    def test_all_19_exact_source_predicates_are_current(self):
        data=json.loads(PACKET.read_text())
        self.assertEqual(data["original_capture_sha256"],
                         "a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087")
        rows=data["records"]
        self.assertEqual(len(rows),19)
        self.assertEqual({r["index"] for r in rows},INDICES)
        self.assertEqual(sum(r["full_atomic_source_fact_verified"] for r in rows),8)
        for row in rows:
            with self.subTest(index=row["index"]):
                path=(ROOT/row["witness_path"]).resolve()
                self.assertTrue(path.is_relative_to(ROOT.resolve()))
                self.assertTrue(path.is_file(),str(path))
                self.assertIn(row["exact_literal"],path.read_text(encoding="utf-8"))
                self.assertTrue(row["narrow_fact"])
                self.assertTrue(row["unsupported_extension"])
                self.assertFalse(row["complete_generated_claim_approved"])
                self.assertFalse(row["generated_text_republication_allowed"])
                self.assertFalse(row["authentic_governed_runtime_observed"])

    def test_existing_public_wiki_source_manifest_unchanged(self):
        public=(ROOT/"scripts/build_sdk_public_wiki.py").read_text()
        self.assertNotIn("CROSS_FRAMEWORK_19_SOURCE_DECISIONS",public)
        self.assertNotIn("GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION",public)

if __name__=="__main__":
    unittest.main()
